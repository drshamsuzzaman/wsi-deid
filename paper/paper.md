---
title: 'WSI DeID: A Python toolkit for whole-slide image de-identification and pseudonymisation'
tags:
  - Python
  - digital pathology
  - whole-slide imaging
  - de-identification
  - pseudonymisation
  - medical imaging
authors:
  - name: Dr. Shamsuz Zaman
    corresponding: true
    affiliation: 1
affiliations:
 - name: ICMR-Centre for Cancer Pathology, Indian Council of Medical Research, Government of India, India
   index: 1
date: 06 May 2026
bibliography: paper.bib
---

# Summary

Whole-slide images (WSIs) are high-resolution digital scans of glass pathology slides. They are increasingly used for teaching, research, quality assurance, and artificial intelligence development in pathology. Before WSIs can be shared for research, visible and embedded identifiers must be handled carefully. Identifiers may appear not only in filenames or metadata, but also in scanner macro images, paper labels, barcodes, and handwritten or scratch-written markings on the glass slide.

WSI DeID is an early-stage Python toolkit for de-identification and pseudonymisation workflows in digital pathology. The software reads vendor WSI formats supported by OpenSlide, including Hamamatsu NDPI in tested workflows, generates pseudonymous slide identifiers, creates a key CSV, produces quality-control (QC) images, and exports a clean lossless tiled pyramidal TIFF derivative. The tool does not modify the source WSI. Instead, it creates a separate clean derivative with minimal clean metadata and omits the original associated macro/label images from the output. The current implementation also writes physical calibration information, such as microns-per-pixel, into TIFF resolution fields when such metadata are exposed by the source slide.

# Statement of need

Digital pathology research groups often need to share WSIs across institutions or with computational collaborators. In practice, a pathology slide can contain identifiers in several locations. A conventional file rename is not sufficient because patient or institutional information may be present in scanner metadata, label images, macro images, barcodes, or physical slide-end markings. Conversely, manual redaction is slow, inconsistent, and difficult to audit for large WSI collections.

WSI DeID addresses this workflow gap by combining pseudonymous naming, key generation, associated-image handling, macro-image QC, slide-end redaction, and clean derivative export in one reproducible workflow. The tool is designed for pathologists and pathology research teams who may prefer a Jupyter notebook workflow, while also exposing a command-line interface for technical users. The software is intentionally conservative in its language: when a re-identification key is retained, the workflow is described as pseudonymisation/de-identification rather than legal anonymisation.

# State of the field

Several mature open-source tools support digital pathology image reading, visualization, and analysis. OpenSlide provides a vendor-neutral library for reading many WSI formats [@goode2013openslide]. Bio-Formats supports microscopy image metadata and format conversion across many proprietary formats [@linkert2010metadata]. QuPath provides a widely used open-source platform for digital pathology image analysis and visualization [@bankhead2017qupath]. The Python ecosystem also includes libraries such as tifffile for reading and writing TIFF files [@gohlke2026tifffile].

These tools provide essential infrastructure, but they do not by themselves define a pathology-facing de-identification workflow that combines pseudonym key generation, macro/label QC, slide-end masking, and clean lossless derivative export. WSI DeID builds on these libraries and focuses specifically on the practical pre-sharing step for WSI datasets.

# Software design

WSI DeID currently uses OpenSlide to read source WSI files and associated images. The export workflow assigns a study identifier, records a pseudonymisation key CSV, extracts associated macro/label images for QC, and writes a clean tiled pyramidal TIFF derivative using tifffile. The default compression is lossless DEFLATE to avoid JPEG recompression loss of pathology information. Pyramid structure is verified using tifffile because some OpenSlide builds report generic TIFF derivatives as a single level even when TIFF SubIFD pyramid levels are present.

The macro-image QC workflow targets two common visual identifier locations: the barcode/label end of the slide and the opposite end where handwritten or scratch-written identifiers may appear. The current redaction approach detects the slide region in the macro image, infers the barcode side, and masks configurable physical slide-end widths. QC outputs include before, mask, and after images so a human reviewer can confirm that identifiers are blocked and diagnostic tissue is not obscured. The clean WSI derivative omits the original macro/label associated images rather than embedding redacted copies.

The repository includes a pathologist-oriented batch Jupyter notebook, a command-line interface, and tests using synthetic images. Generated outputs include the clean WSI derivative, a pseudonym key CSV, QC images, and a JSON report containing metadata policy and TIFF pyramid verification.

# Research impact statement

WSI DeID is intended to support research dataset preparation in digital pathology, especially for laboratories beginning to share WSI data for computational pathology and AI work. The tool helps make a common pre-analytic data-governance step reproducible and inspectable. It may be useful for internal dataset curation, multi-institutional research preparation, teaching datasets, and development of pathology AI workflows where slide identifiers must be removed or separated from shared image derivatives.

The software does not replace institutional governance, ethics review, data use agreements, or human QC. Rather, it provides a transparent technical workflow that can be incorporated into local standard operating procedures. Future development priorities include broader scanner/vendor validation, optional DICOM-WSI export, additional export backends, encrypted key storage, formal QC reports, and compatibility testing across common WSI viewers.

# AI usage disclosure

Generative AI assistance was used during early software drafting, documentation development, and preparation of this paper. The author reviewed, edited, and tested the generated code and documentation. Functional behavior was checked using synthetic tests and real-world NDPI workflow trials, including verification of tiled pyramid output and lossless compression. The author remains responsible for the software design, validation decisions, documentation, and scientific claims.

# Acknowledgements

The author acknowledges the Indian Council of Medical Research (ICMR) and the ICMR-Centre for Cancer Pathology for the professional context in which this need was identified. This repository is presented as open-source research software by the author and not as an official Government of India or ICMR software release unless separately approved.

# References
