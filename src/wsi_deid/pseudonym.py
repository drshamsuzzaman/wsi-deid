from __future__ import annotations

import csv
import hashlib
import secrets
from datetime import datetime
from pathlib import Path


def make_study_id(prefix: str = "WSI") -> str:
    return f"{prefix}_{secrets.token_hex(4).upper()}"


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def append_key_row(key_csv: Path, source_path: Path, output_path: Path, study_id: str) -> None:
    key_csv.parent.mkdir(parents=True, exist_ok=True)
    is_new = not key_csv.exists()
    with key_csv.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "study_id",
                "original_filename",
                "original_path",
                "output_filename",
                "output_path",
                "source_sha256",
                "created_at",
                "notes",
            ],
        )
        if is_new:
            writer.writeheader()
        writer.writerow(
            {
                "study_id": study_id,
                "original_filename": source_path.name,
                "original_path": str(source_path.resolve()),
                "output_filename": output_path.name,
                "output_path": str(output_path.resolve()),
                "source_sha256": sha256_file(source_path),
                "created_at": datetime.now().isoformat(timespec="seconds"),
                "notes": "Pseudonymisation key. Store separately from shared WSI outputs.",
            }
        )
