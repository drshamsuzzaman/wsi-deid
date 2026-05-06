from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import numpy as np
import openslide
import tifffile
from PIL import Image

from .pseudonym import append_key_row, make_study_id
from .redaction import redact_slide_ends


def tiff_resolution_from_mpp(slide: openslide.OpenSlide) -> tuple[tuple[float, float] | None, str | None]:
    """Return TIFF resolution as pixels per centimeter from OpenSlide MPP metadata."""
    mpp_x = slide.properties.get("openslide.mpp-x")
    mpp_y = slide.properties.get("openslide.mpp-y")
    if not mpp_x or not mpp_y:
        return None, None

    try:
        x_pixels_per_cm = 10000.0 / float(mpp_x)
        y_pixels_per_cm = 10000.0 / float(mpp_y)
    except ValueError:
        return None, None

    return (x_pixels_per_cm, y_pixels_per_cm), "CENTIMETER"


def save_macro_qc(
    slide: openslide.OpenSlide,
    qc_dir: Path,
    study_id: str,
    barcode_end_mm: float,
    handwritten_end_mm: float,
) -> dict:
    qc_dir.mkdir(parents=True, exist_ok=True)
    info: dict = {"associated_images": list(slide.associated_images.keys())}
    for name, assoc in slide.associated_images.items():
        safe_name = name.lower().replace(" ", "_")
        assoc_rgb = assoc.convert("RGB")
        assoc_rgb.save(qc_dir / f"{study_id}_{safe_name}_before.png")

        if safe_name == "label":
            after = Image.new("RGB", assoc_rgb.size, (255, 255, 255))
            mask = Image.new("L", assoc_rgb.size, 255)
            redact_info = {"mode": "blanked_full_label"}
        elif safe_name in {"macro", "overview"}:
            after, mask, redact_info = redact_slide_ends(
                assoc_rgb,
                barcode_side="auto",
                barcode_end_mm=barcode_end_mm,
                handwritten_end_mm=handwritten_end_mm,
            )
        else:
            after = assoc_rgb
            mask = Image.new("L", assoc_rgb.size, 0)
            redact_info = {"mode": "unchanged_unrecognized_associated_image"}

        after.save(qc_dir / f"{study_id}_{safe_name}_after.png")
        mask.save(qc_dir / f"{study_id}_{safe_name}_mask.png")
        info[safe_name] = redact_info
    return info


def tile_generator(slide: openslide.OpenSlide, level: int, tile_size: int):
    width, height = slide.level_dimensions[level]
    downsample = slide.level_downsamples[level]
    for y in range(0, height, tile_size):
        for x in range(0, width, tile_size):
            read_w = min(tile_size, width - x)
            read_h = min(tile_size, height - y)
            base_x = int(round(x * downsample))
            base_y = int(round(y * downsample))
            tile = slide.read_region((base_x, base_y), level, (read_w, read_h)).convert("RGB")
            arr = np.asarray(tile)
            if read_w != tile_size or read_h != tile_size:
                padded = np.full((tile_size, tile_size, 3), 255, dtype=np.uint8)
                padded[:read_h, :read_w] = arr
                arr = padded
            yield arr


def write_pyramidal_tiff(
    slide: openslide.OpenSlide,
    output_path: Path,
    study_id: str,
    tile_size: int = 512,
    max_sublevels: int = 6,
    compression: str | None = "deflate",
    jpeg_quality: int = 90,
) -> list[int]:
    level_count = min(slide.level_count, max_sublevels + 1)
    levels = list(range(level_count))
    output_path.parent.mkdir(parents=True, exist_ok=True)

    clean_description = {
        "study_id": study_id,
        "deidentified": True,
        "associated_images": "omitted",
        "source_vendor": slide.properties.get("openslide.vendor", ""),
        "objective_power": slide.properties.get("openslide.objective-power", ""),
        "mpp_x": slide.properties.get("openslide.mpp-x", ""),
        "mpp_y": slide.properties.get("openslide.mpp-y", ""),
        "created_by": "wsi-deid",
    }

    with tifffile.TiffWriter(output_path, bigtiff=True) as tif:
        resolution, resolutionunit = tiff_resolution_from_mpp(slide)
        for i, level in enumerate(levels):
            width, height = slide.level_dimensions[level]
            options = {
                "shape": (height, width, 3),
                "dtype": np.uint8,
                "photometric": "rgb",
                "tile": (tile_size, tile_size),
                "compression": compression,
                "metadata": None,
                "description": json.dumps(clean_description) if i == 0 else None,
            }
            if resolution is not None and resolutionunit is not None:
                downsample = slide.level_downsamples[level]
                options["resolution"] = (
                    resolution[0] / downsample,
                    resolution[1] / downsample,
                )
                options["resolutionunit"] = resolutionunit
            if i == 0 and len(levels) > 1:
                options["subifds"] = len(levels) - 1
            if i > 0:
                options["subfiletype"] = 1
            if compression == "jpeg":
                options["compressionargs"] = {"level": jpeg_quality}
            tif.write(tile_generator(slide, level, tile_size), **options)
            print(f"Wrote level {level}: {width} x {height}")
    return levels


def write_report(report_path: Path, data: dict) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def inspect_tiff_pyramid(tiff_path: Path) -> dict:
    """Inspect pyramid levels using tifffile, which understands TIFF SubIFDs."""
    levels = []
    with tifffile.TiffFile(tiff_path) as tif:
        if not tif.series:
            return {"level_count": 0, "levels": []}
        series = tif.series[0]
        for index, level in enumerate(series.levels):
            page = level.pages[0]
            levels.append(
                {
                    "index": index,
                    "shape": list(level.shape),
                    "is_tiled": bool(page.is_tiled),
                    "compression": page.compression.name,
                }
            )
    return {"level_count": len(levels), "levels": levels}


def export_clean_wsi(
    source: Path,
    output_dir: Path,
    qc_dir: Path | None = None,
    key_csv: Path | None = None,
    study_id: str | None = None,
    barcode_end_mm: float = 22.0,
    handwritten_end_mm: float = 12.0,
    tile_size: int = 512,
    max_sublevels: int = 6,
    compression: str | None = "deflate",
    jpeg_quality: int = 90,
) -> dict:
    source = Path(source)
    if not source.exists():
        raise FileNotFoundError(source)

    study_id = study_id or make_study_id()
    output_dir = Path(output_dir)
    qc_dir = Path(qc_dir) if qc_dir else output_dir / "qc"
    key_csv = Path(key_csv) if key_csv else output_dir / "pseudonym_key.csv"
    output_path = output_dir / f"{study_id}.ome.tif"

    slide = openslide.OpenSlide(str(source))
    macro_info = save_macro_qc(
        slide,
        qc_dir=qc_dir,
        study_id=study_id,
        barcode_end_mm=barcode_end_mm,
        handwritten_end_mm=handwritten_end_mm,
    )
    written_levels = write_pyramidal_tiff(
        slide,
        output_path=output_path,
        study_id=study_id,
        tile_size=tile_size,
        max_sublevels=max_sublevels,
        compression=compression,
        jpeg_quality=jpeg_quality,
    )
    pyramid_info = inspect_tiff_pyramid(output_path)
    report = {
        "study_id": study_id,
        "source_path": str(source.resolve()),
        "output_path": str(output_path.resolve()),
        "source_format": slide.properties.get("openslide.vendor", ""),
        "level_dimensions": list(slide.level_dimensions),
        "written_levels": written_levels,
        "output_pyramid": pyramid_info,
        "macro_redaction": macro_info,
        "metadata_policy": "Only minimal clean derivative metadata written. Vendor metadata and associated images omitted.",
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    slide.close()

    append_key_row(key_csv, source, output_path, study_id)
    write_report(qc_dir / f"{study_id}_report.json", report)
    print("Verified TIFF pyramid levels:", pyramid_info["level_count"])
    return {
        "study_id": study_id,
        "output_path": output_path,
        "qc_dir": qc_dir,
        "key_csv": key_csv,
        "report": report,
    }
