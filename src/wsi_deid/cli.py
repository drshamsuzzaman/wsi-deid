from __future__ import annotations

import argparse
from pathlib import Path

from .export import export_clean_wsi


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wsi-deid",
        description="Whole-slide image de-identification and pseudonymisation toolkit.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    export_parser = subparsers.add_parser(
        "export",
        help="Export a clean de-identified WSI derivative.",
    )
    export_parser.add_argument("--input", required=True, type=Path, help="Source WSI path, e.g. .ndpi")
    export_parser.add_argument("--output-dir", required=True, type=Path, help="Clean WSI output folder")
    export_parser.add_argument("--qc-dir", type=Path, help="QC images and report folder")
    export_parser.add_argument("--key-csv", type=Path, help="Pseudonym key CSV path")
    export_parser.add_argument("--study-id", help="Optional study ID; generated if omitted")
    export_parser.add_argument("--barcode-end-mm", type=float, default=22.0)
    export_parser.add_argument("--handwritten-end-mm", type=float, default=12.0)
    export_parser.add_argument("--tile-size", type=int, default=512)
    export_parser.add_argument("--max-sublevels", type=int, default=6)
    export_parser.add_argument(
        "--compression",
        choices=["deflate", "none", "jpeg"],
        default="deflate",
        help="Use deflate for lossless output. JPEG is lossy and should be opt-in only.",
    )
    export_parser.add_argument("--jpeg-quality", type=int, default=90)
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "export":
        result = export_clean_wsi(
            source=args.input,
            output_dir=args.output_dir,
            qc_dir=args.qc_dir,
            key_csv=args.key_csv,
            study_id=args.study_id,
            barcode_end_mm=args.barcode_end_mm,
            handwritten_end_mm=args.handwritten_end_mm,
            tile_size=args.tile_size,
            max_sublevels=args.max_sublevels,
            compression=None if args.compression == "none" else args.compression,
            jpeg_quality=args.jpeg_quality,
        )
        print("Clean WSI:", result["output_path"])
        print("QC folder:", result["qc_dir"])
        print("Key CSV:", result["key_csv"])
