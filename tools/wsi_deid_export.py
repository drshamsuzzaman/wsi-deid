#!/usr/bin/env python
"""Backward-compatible wrapper for the package CLI."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from wsi_deid.cli import main


if __name__ == "__main__":
    main(["export", *sys.argv[1:]])
