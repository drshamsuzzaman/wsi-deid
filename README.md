# WSI DeID

Whole Slide Image De-identification and Pseudonymisation Toolkit.

WSI DeID is an early-stage Python tool for preparing digital pathology slides for research sharing. It is designed around practical pathology risks: identifiers in filenames, vendor metadata, macro/label images, barcodes, paper labels, and handwritten or scratch-written markings on the glass slide.

The current prototype has been tested first on Hamamatsu `.ndpi` input and exports a clean, lossless tiled pyramidal TIFF derivative.

Developed by **Dr. Shamsuz Zaman**, Pathologist-Scientist, Indian Council of Medical Research (ICMR), Government of India.

Unless separately approved by the institution, this repository should be treated as an open-source research software project by the author and not as an official Government of India or ICMR software release.

## Important Scope

This tool supports **de-identification and pseudonymisation workflows**. It does not guarantee legal anonymisation.

If a re-identification key is retained, the output should be described as pseudonymised/de-identified, not anonymised.

Human QC and local ethics/institutional review remain necessary before sharing slides.

## What It Does

- Reads WSI files supported by OpenSlide, including many `.ndpi`, `.svs`, `.scn`, `.mrxs`, `.tif`, and `.tiff` files.
- Assigns a pseudonymous study ID.
- Creates a pseudonymisation key CSV.
- Extracts macro/label associated images for QC.
- Blanks label images.
- Detects the barcode/label side in the macro image.
- Masks the barcode/label end and the opposite handwritten/scratch-number end.
- Exports a clean lossless tiled pyramidal `.ome.tif` derivative.
- Omits original associated macro/label images from the clean WSI.
- Writes minimal clean metadata.
- Saves before/mask/after QC images and a JSON processing report.

## Why Not Clean `.ndpi` Output?

`.ndpi` is a proprietary Hamamatsu format. Open-source tools can usually read NDPI, but safely writing a new valid NDPI after removing metadata and replacing embedded macro/label images is not currently reliable.

For de-identified sharing, this project currently recommends:

```text
NDPI input -> clean lossless OME-TIFF / pyramidal TIFF output
```

The original NDPI should be kept restricted.

## Install

From the repository folder:

```bash
python -m pip install -e .
```

On Windows, the project depends on `openslide-bin` to provide the native OpenSlide library.

## Basic Use

```bash
wsi-deid export ^
  --input "C:\path\to\B-300-26.ndpi" ^
  --output-dir "C:\path\to\wsi_deid_clean" ^
  --study-id WSI_000001
```

The default export is lossless:

```text
compression = deflate
```

JPEG export is available only as an explicit opt-in and is not recommended when pathology information must be preserved without compression loss.

## Outputs

```text
wsi_deid_clean/
  WSI_000001.ome.tif
  pseudonym_key.csv
  qc/
    WSI_000001_macro_before.png
    WSI_000001_macro_mask.png
    WSI_000001_macro_after.png
    WSI_000001_report.json
```

Store `pseudonym_key.csv` separately from shared WSI outputs, ideally encrypted and access-controlled.

## Viewers

The clean output is a tiled pyramidal TIFF/OME-style derivative. Try opening it with:

- QuPath
- Fiji/ImageJ with Bio-Formats
- napari with suitable TIFF/OME plugins
- other OME-TIFF or pyramidal TIFF-aware viewers

Hamamatsu NDP.view is primarily for `.ndpi` and may not open the clean `.ome.tif`.

## Development Status

This is an early prototype. The masking strategy has worked on an example NDPI macro image where both the paper label side and scratch-written non-barcode end needed redaction. More scanner/vendor validation is needed before routine use.

Planned next steps:

- batch-folder CLI
- DICOM-WSI export
- richer metadata rules by vendor
- encrypted key storage
- formal QC report
- viewer compatibility testing
- JOSS/SoftwareX-ready documentation and tests
