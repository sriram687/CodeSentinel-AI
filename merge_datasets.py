"""
merge_datasets.py
Unified dataset creation for VulBERTa Encoder Phase 1 (CodeSentinel-AI)

Combines 8 C/C++ vulnerability datasets into a unified schema:
  - PrimeVul
  - DiverseVul
  - Devign
  - D2A
  - ReVeal
  - VulDeePecker
  - MVD
  - Draper (capped at 150k stratified sample)

Standard Schema:
  {
    "code": str,
    "label": int (0 or 1),
    "cwe_id": str,
    "source_dataset": str,
    "split": str ("train", "validation", "test")
  }
"""

import os
import json
import random
import pandas as pd
from typing import List, Dict, Any

DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "finetune")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "data", "merged")
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "merged_raw.jsonl")

RANDOM_SEED = 42
random.seed(RANDOM_SEED)

def process_primevul() -> List[Dict[str, Any]]:
    print("[1/8] Processing PrimeVul...")
    path = os.path.join(DATA_DIR, "primevul", "PrimeVul.json")
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            code = obj.get("func", "").strip()
            if not code:
                continue
            target = int(obj.get("target", 0))
            cwe = str(obj.get("cwe", "Unknown")).strip()
            if not cwe or cwe.lower() == "none":
                cwe = "Unknown"
            split = obj.get("hf_split", "train")
            if split == "valid" or split == "validation":
                split = "validation"
            elif split == "test":
                split = "test"
            else:
                split = "train"
            
            records.append({
                "code": code,
                "label": target,
                "cwe_id": cwe,
                "source_dataset": "primevul",
                "split": split
            })
    print(f"  PrimeVul loaded: {len(records)} samples")
    return records

def process_diversevul() -> List[Dict[str, Any]]:
    print("[2/8] Processing DiverseVul...")
    path = os.path.join(DATA_DIR, "diversevul", "DiverseVul.json")
    raw = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            code = obj.get("func", "").strip()
            if not code:
                continue
            target = int(obj.get("target", 0))
            cwe = obj.get("cwe")
            if isinstance(cwe, list):
                cwe_str = ", ".join(str(c) for c in cwe) if cwe else "Unknown"
            else:
                cwe_str = str(cwe).strip() if cwe else "Unknown"
            if not cwe_str or cwe_str.lower() == "none":
                cwe_str = "Unknown"
            raw.append({"code": code, "target": target, "cwe": cwe_str})

    # Stratified split 80 / 10 / 10
    positives = [r for r in raw if r["target"] == 1]
    negatives = [r for r in raw if r["target"] == 0]
    random.shuffle(positives)
    random.shuffle(negatives)

    def assign_splits(items):
        n = len(items)
        n_train = int(n * 0.8)
        n_val = int(n * 0.1)
        for i, item in enumerate(items):
            if i < n_train:
                item["split"] = "train"
            elif i < n_train + n_val:
                item["split"] = "validation"
            else:
                item["split"] = "test"

    assign_splits(positives)
    assign_splits(negatives)

    records = []
    for r in positives + negatives:
        records.append({
            "code": r["code"],
            "label": r["target"],
            "cwe_id": r["cwe"],
            "source_dataset": "diversevul",
            "split": r["split"]
        })
    print(f"  DiverseVul loaded: {len(records)} samples")
    return records

def process_devign() -> List[Dict[str, Any]]:
    print("[3/8] Processing Devign...")
    json_path = os.path.join(DATA_DIR, "devign", "Devign.json")
    with open(json_path, "r", encoding="utf-8") as f:
        devign_data = json.load(f)

    splits_map = {}
    for s_name, filename in [("train", "train.txt"), ("validation", "valid.txt"), ("test", "test.txt")]:
        fpath = os.path.join(DATA_DIR, "devign", filename)
        if os.path.exists(fpath):
            with open(fpath, "r") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        splits_map[int(line)] = s_name

    records = []
    for idx, item in enumerate(devign_data):
        code = item.get("func", "").strip()
        if not code:
            continue
        split = splits_map.get(idx, "train")
        records.append({
            "code": code,
            "label": int(item.get("target", 0)),
            "cwe_id": "Unknown",
            "source_dataset": "devign",
            "split": split
        })
    print(f"  Devign loaded: {len(records)} samples")
    return records

def process_d2a() -> List[Dict[str, Any]]:
    print("[4/8] Processing D2A...")
    file_map = {
        "train": "d2a_lbv1_function_train.csv",
        "validation": "d2a_lbv1_function_dev.csv",
        "test": "d2a_lbv1_function_test.csv"
    }
    records = []
    for split, fname in file_map.items():
        fpath = os.path.join(DATA_DIR, "d2a", "function", fname)
        if not os.path.exists(fpath):
            continue
        df = pd.read_csv(fpath)
        for _, row in df.iterrows():
            code = str(row.get("code", "")).strip()
            if not code or code.lower() == "nan":
                continue
            records.append({
                "code": code,
                "label": int(row.get("label", 0)),
                "cwe_id": "Unknown",
                "source_dataset": "d2a",
                "split": split
            })
    print(f"  D2A loaded: {len(records)} samples")
    return records

def process_reveal() -> List[Dict[str, Any]]:
    print("[5/8] Processing ReVeal...")
    file_map = {
        "train": "reveal_train.pkl",
        "validation": "reveal_val.pkl",
        "test": "reveal_test.pkl"
    }
    records = []
    for split, fname in file_map.items():
        fpath = os.path.join(DATA_DIR, "reveal", fname)
        if not os.path.exists(fpath):
            continue
        df = pd.read_pickle(fpath)
        for _, row in df.iterrows():
            code = str(row.get("functionSource", "")).strip()
            if not code or code.lower() == "nan":
                continue
            records.append({
                "code": code,
                "label": int(row.get("label", 0)),
                "cwe_id": "Unknown",
                "source_dataset": "reveal",
                "split": split
            })
    print(f"  ReVeal loaded: {len(records)} samples")
    return records

def process_vuldeepecker() -> List[Dict[str, Any]]:
    print("[6/8] Processing VulDeePecker...")
    file_map = {
        "train": "vuldeepecker_train.pkl",
        "validation": "vuldeepecker_val.pkl",
        "test": "vuldeepecker_test.pkl"
    }
    records = []
    for split, fname in file_map.items():
        fpath = os.path.join(DATA_DIR, "vuldeepecker", fname)
        if not os.path.exists(fpath):
            continue
        df = pd.read_pickle(fpath)
        for _, row in df.iterrows():
            code = str(row.get("functionSource", "")).strip()
            if not code or code.lower() == "nan":
                continue
            cwe = str(row.get("cwe", "Unknown")).strip()
            if not cwe or cwe.lower() == "nan" or cwe.lower() == "none":
                cwe = "Unknown"
            records.append({
                "code": code,
                "label": int(row.get("label", 0)),
                "cwe_id": cwe,
                "source_dataset": "vuldeepecker",
                "split": split
            })
    print(f"  VulDeePecker loaded: {len(records)} samples")
    return records

def process_mvd() -> List[Dict[str, Any]]:
    print("[7/8] Processing MVD...")
    cwe_map = {0: "None", 1: "CWE-119", 2: "CWE-120", 3: "CWE-476", 4: "CWE-787"}
    file_map = {
        "train": "mvd_train.pkl",
        "validation": "mvd_val.pkl",
        "test": "mvd_test.pkl"
    }
    records = []
    for split, fname in file_map.items():
        fpath = os.path.join(DATA_DIR, "mvd", fname)
        if not os.path.exists(fpath):
            continue
        df = pd.read_pickle(fpath)
        for _, row in df.iterrows():
            code = str(row.get("func", "")).strip()
            if not code or code.lower() == "nan":
                continue
            lbl = int(row.get("label", 0))
            binary_label = 0 if lbl == 0 else 1
            cwe_str = cwe_map.get(lbl, "Unknown")
            records.append({
                "code": code,
                "label": binary_label,
                "cwe_id": cwe_str,
                "source_dataset": "mvd",
                "split": split
            })
    print(f"  MVD loaded: {len(records)} samples")
    return records

def process_draper(max_total_samples: int = 150000) -> List[Dict[str, Any]]:
    print(f"[8/8] Processing Draper (capped at {max_total_samples} samples)...")
    file_map = {
        "train": "draper_train.pkl",
        "validation": "draper_val.pkl",
        "test": "draper_test.pkl"
    }

    raw_by_split = {}
    for split, fname in file_map.items():
        fpath = os.path.join(DATA_DIR, "draper", fname)
        if not os.path.exists(fpath):
            continue
        df = pd.read_pickle(fpath)
        
        # Sample proportionally from each split
        raw_by_split[split] = df

    total_draper_count = sum(len(df) for df in raw_by_split.values())
    if total_draper_count == 0:
        return []

    records = []
    cwe_cols = ["CWE-119", "CWE-120", "CWE-469", "CWE-476", "CWE-other"]

    for split, df in raw_by_split.items():
        split_ratio = len(df) / total_draper_count
        n_samples_split = int(max_total_samples * split_ratio)
        
        # Stratified sampling by combine
        pos_df = df[df["combine"] == True]
        neg_df = df[df["combine"] == False]

        pos_ratio = len(pos_df) / len(df)
        n_pos = int(n_samples_split * pos_ratio)
        n_neg = n_samples_split - n_pos

        pos_sampled = pos_df.sample(n=min(n_pos, len(pos_df)), random_state=RANDOM_SEED)
        neg_sampled = neg_df.sample(n=min(n_neg, len(neg_df)), random_state=RANDOM_SEED)
        
        sampled_df = pd.concat([pos_sampled, neg_sampled]).sample(frac=1.0, random_state=RANDOM_SEED)

        for _, row in sampled_df.iterrows():
            code = str(row.get("functionSource", "")).strip()
            if not code or code.lower() == "nan":
                continue
            is_vuln = bool(row.get("combine", False))
            
            # Find CWE
            found_cwes = [c for c in cwe_cols if bool(row.get(c, False))]
            cwe_str = ", ".join(found_cwes) if found_cwes else ("Unknown" if is_vuln else "None")

            records.append({
                "code": code,
                "label": 1 if is_vuln else 0,
                "cwe_id": cwe_str,
                "source_dataset": "draper",
                "split": split
            })

    print(f"  Draper loaded: {len(records)} samples")
    return records

def main():
    all_records = []
    all_records.extend(process_primevul())
    all_records.extend(process_diversevul())
    all_records.extend(process_devign())
    all_records.extend(process_d2a())
    all_records.extend(process_reveal())
    all_records.extend(process_vuldeepecker())
    all_records.extend(process_mvd())
    all_records.extend(process_draper(max_total_samples=150000))

    print(f"\nWriting {len(all_records)} total records to {OUTPUT_FILE}...")
    
    split_counts = {}
    source_counts = {}
    label_counts = {0: 0, 1: 0}

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for r in all_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            
            s = r["split"]
            split_counts[s] = split_counts.get(s, 0) + 1
            
            src = r["source_dataset"]
            source_counts[src] = source_counts.get(src, 0) + 1
            
            lbl = r["label"]
            label_counts[lbl] += 1

    print("\n=== Dataset Merge Summary ===")
    print(f"Total merged records: {len(all_records)}")
    print(f"Splits: {split_counts}")
    print(f"Class imbalance: Safe (0) = {label_counts[0]}, Vulnerable (1) = {label_counts[1]} (Vulnerable ratio: {label_counts[1]/len(all_records):.2%})")
    print("Sources breakdown:")
    for src, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {src}: {count} samples")

if __name__ == "__main__":
    main()
