# WSI DeID

Whole Slide Image De-identification and Pseudonymisation Toolkit.

WSI DeID is an early-stage Python tool for preparing digital pathology slides for research sharing. It is designed around practical pathology risks: identifiers in filenames, vendor metadata, macro/label images, barcodes, paper labels, and handwritten or scratch-written markings on the glass slide.

The current prototype has been tested first on Hamamatsu `.ndpi` input and exports a clean, lossless tiled pyramidal TIFF derivative.

Developed by **Dr. Shamsuz Zaman**, Pathologist-Scientist, ICMR-Centre for Cancer Pathology, Government of India.

This repository should be treated as an open-source research software project by the author and not as an official Government of India or ICMR software release.

## Important Scope

This tool supports **de-identification and pseudonymisation workflows**. It does not guarantee legal anonymisation.

If a re-identification key is retained, the output should be described as pseudonymised/de-identified, not anonymised.

Human QC and local ethics/institutional review remain necessary before sharing slides.

## Simplest CLI Example

```bash
wsi-deid export --input "path/to/slide.ndpi" --output-dir "path/to/clean_output"
```

The default export is lossless (`deflate`) and writes a clean `.ome.tif`, a pseudonym key CSV, QC images, and a JSON report.

## Quick Start for Pathologists

Use this route if you want to process a folder of WSI files without writing code.

### Option A: Download Without Git

1. Open the repository page.
2. Click **Code**.
3. Click **Download ZIP**.
4. Extract the ZIP file.
5. Open a terminal/command prompt in the extracted folder.
6. Install the tool:

```bash
python -m pip install --editable .
```

7. Open the batch notebook:

```text
tools/wsi_deid_batch_export.ipynb
```

8. Change `INPUT_DIR` to the folder containing your WSI files.
9. Run the notebook cells from top to bottom.
10. Review the QC images before sharing the clean WSI outputs.

### Option B: Clone With Git

```bash
git clone https://github.com/drshamsuzzaman/wsi-deid.git
cd wsi-deid
python -m pip install --editable .
jupyter notebook tools/wsi_deid_batch_export.ipynb
```

In the notebook, change:

```python
INPUT_DIR = Path(r"C:\Users\YourName\Desktop\slides")
```

to the folder containing your slides.

The notebook creates:

```text
wsi_deid_clean_YYYYMMDD_HHMMSS/
  WSI_000001.ome.tif
  WSI_000002.ome.tif
  pseudonym_key.csv
  qc/
```

Keep `pseudonym_key.csv` secure and separate from shared outputs.

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

## What Is Removed or Changed

The clean derivative is designed to remove or avoid the most common WSI identifier locations:

- Original filename is replaced by a pseudonymous study ID.
- Original vendor metadata is not copied into the clean derivative.
- Only minimal clean metadata is written.
- Original associated macro/label images are not embedded in the clean derivative.
- Separate QC images are generated so the user can check whether label/barcode and handwritten/scratch-number regions were blocked.
- Label associated images, when present, are blanked in QC.
- Macro/overview associated images, when present, are redacted in QC by masking the barcode/label end and the opposite handwritten/scratch end.

## What Is Not Guaranteed

This tool does not guarantee legal anonymisation or complete removal of all re-identification risk.

Current limitations:

- The source WSI file is not modified.
- A re-identification key CSV is created; if retained, the workflow is pseudonymisation/de-identification, not anonymisation.
- Clean output is currently `.ome.tif` / tiled pyramidal TIFF, not rewritten `.ndpi`.
- Proprietary vendor formats may contain private metadata fields that are not fully interpretable by open-source readers.
- Rare diagnoses, dates, linked clinical data, or unusual tissue patterns may still create re-identification risk outside the WSI file itself.
- Automatic macro masking must be reviewed by a human before sharing outputs.
- Viewer compatibility may vary across platforms and WSI viewers.

Use local ethics, institutional, and data-sharing review before external release.

## QC Example

The tool writes QC images for each processed slide:

```text
qc/
  WSI_000001_macro_before.png
  WSI_000001_macro_mask.png
  WSI_000001_macro_after.png
  WSI_000001_report.json
```

Before sharing clean WSI files, review the QC images and confirm:

- barcode/label regions are fully blocked
- handwritten/scratch-number regions are fully blocked
- diagnostic tissue is not blocked
- no patient or institution identifiers remain visible in QC outputs intended for sharing

Screenshots in this repository should use only synthetic examples or fully de-identified images. Do not upload real patient labels, accession numbers, barcodes, or identifiable institutional labels into the public repository.



## Platform Setup

Install Python 3.10 or newer, install native OpenSlide where needed, then install WSI DeID from the repository folder.

### 1. Install Python and OpenSlide

Windows:

- Install Python 3.10 or newer from [python.org](https://www.python.org/downloads/windows/) or the Microsoft Store.
- No separate OpenSlide install is usually needed because `openslide-bin` is installed automatically on Windows.

macOS:

- Install Python and OpenSlide with Homebrew:

```bash
brew install python openslide
```

Linux:

- On Ubuntu/Debian:

```bash
sudo apt-get update
sudo apt-get install python3 python3-pip openslide-tools libopenslide0
```

### 2. Install WSI DeID

From the repository folder:

```bash
python -m pip install --editable .
```

On some Linux systems, use:

```bash
python3 -m pip install --editable .
```

### 3. Install and Open Jupyter

```bash
python -m pip install notebook
python -m notebook tools/wsi_deid_batch_export.ipynb
```

On Windows, this path style also works:

```powershell
python -m notebook tools\wsi_deid_batch_export.ipynb
```

On some Linux systems, use:

```bash
python3 -m pip install notebook
python3 -m notebook tools/wsi_deid_batch_export.ipynb
```

## Command-Line Use

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

On macOS/Linux, use backslashes for line continuation and normal Unix-style paths:

```bash
wsi-deid export \
  --input "/path/to/B-300-26.ndpi" \
  --output-dir "/path/to/wsi_deid_clean" \
  --study-id WSI_000001
```

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

## Development

Install development dependencies:

```bash
python -m pip install --editable ".[dev]"
```

Run tests:

```bash
pytest
```

The current test suite uses synthetic images and does not require patient WSI data.


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
