"""
download_datasets.py
====================
Downloads PrimeVul and DiverseVul from HuggingFace Hub and saves them
as newline-delimited JSON files suitable for the merge pipeline.

Usage:
    python download_datasets.py
"""

import json
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
FINETUNE_DIR = BASE_DIR / "data" / "finetune"

TARGETS = [
    {
        "hf_name":    "colin/PrimeVul",
        "out_dir":    FINETUNE_DIR / "primevul",
        "out_file":   "PrimeVul.json",
    },
    {
        "hf_name":   "claudios/DiverseVul",
        "out_dir":   FINETUNE_DIR / "diversevul",
        "out_file":  "DiverseVul.json",
    },
]


def download_and_save(target: dict) -> None:
    from datasets import load_dataset

    hf_name   = target["hf_name"]
    out_dir   = target["out_dir"]
    out_file  = target["out_file"]
    out_path  = out_dir / out_file

    out_dir.mkdir(parents=True, exist_ok=True)

    if out_path.exists():
        size_mb = out_path.stat().st_size / 1_048_576
        print(f"[SKIP] {out_path.name} already exists ({size_mb:.1f} MB). Delete to re-download.")
        return

    print(f"\n[INFO] Downloading {hf_name} ...")
    ds = load_dataset(hf_name)

    total = 0
    with open(out_path, "w", encoding="utf-8") as f:
        for split_name, split_ds in ds.items():
            for record in split_ds:
                record = dict(record)
                record["hf_split"] = split_name
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
                total += 1
                if total % 50_000 == 0:
                    print(f"  ... {total:,} records written", flush=True)

    size_mb = out_path.stat().st_size / 1_048_576
    print(f"[OK]  {out_path.name}  -- {total:,} records  ({size_mb:.1f} MB)")


def main():
    for target in TARGETS:
        try:
            download_and_save(target)
        except Exception as exc:
            print(f"[ERROR] Failed to download {target['hf_name']}: {exc}", file=sys.stderr)
            raise


if __name__ == "__main__":
    main()
