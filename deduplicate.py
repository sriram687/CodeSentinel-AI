"""
deduplicate.py (Multi-Core Parallel Version - Fixed for Datasketch 2.x)
MinHash LSH Deduplication for VulBERTa / CodeSentinel-AI

Uses multi-processing across CPU cores to compute MinHash signatures at ultra-high speed,
applying Jaccard Similarity >= 0.80 deduplication across all 1.1M merged code samples.

Source Priority Order for Resolving Duplicates:
1. primevul
2. diversevul
3. devign
4. d2a
5. reveal
6. vuldeepecker
7. mvd
8. draper
"""

import os
import json
import time
from multiprocessing import Pool, cpu_count
from typing import List, Dict, Any, Tuple
import numpy as np
from datasketch import MinHash, MinHashLSH

INPUT_FILE = os.path.join(os.path.dirname(__file__), "data", "merged", "merged_raw.jsonl")
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "data", "merged", "merged_deduped.jsonl")
STATS_FILE = os.path.join(os.path.dirname(__file__), "data", "merged", "dedup_stats.json")

SOURCE_PRIORITY = {
    "primevul": 1,
    "diversevul": 2,
    "devign": 3,
    "d2a": 4,
    "reveal": 5,
    "vuldeepecker": 6,
    "mvd": 7,
    "draper": 8
}

JACCARD_THRESHOLD = 0.80
NUM_PERM = 128
SHINGLE_SIZE = 3

def process_record_minhash(record_tuple: Tuple[int, Dict[str, Any]]) -> Tuple[int, np.ndarray, str]:
    """Worker function: Extract 3-gram shingles and compute MinHash signature."""
    idx, rec = record_tuple
    code = rec["code"]
    text = "".join(code.split())
    if len(text) < SHINGLE_SIZE:
        shingles = {text}
    else:
        shingles = {text[i:i+SHINGLE_SIZE] for i in range(len(text) - SHINGLE_SIZE + 1)}

    m = MinHash(num_perm=NUM_PERM)
    for shingle in shingles:
        m.update(shingle.encode('utf-8'))
    return (idx, m.hashvalues, m.scheme)

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} does not exist. Run merge_datasets.py first.")
        return

    print("Loading raw merged dataset...")
    t0 = time.time()
    
    records = []
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    total_raw = len(records)
    print(f"Loaded {total_raw} records in {time.time() - t0:.2f}s")

    # Sort records by source priority (highest priority first)
    records.sort(key=lambda x: SOURCE_PRIORITY.get(x.get("source_dataset", "draper"), 99))

    num_workers = min(16, max(1, cpu_count() - 2))
    print(f"\nComputing MinHash signatures using {num_workers} parallel CPU workers...")
    t1 = time.time()

    record_tuples = [(i, r) for i, r in enumerate(records)]

    minhash_hashvalues = {}
    default_scheme = "affine32"

    with Pool(processes=num_workers) as pool:
        for idx, h_values, scheme in pool.imap_unordered(process_record_minhash, record_tuples, chunksize=1000):
            minhash_hashvalues[idx] = h_values
            default_scheme = scheme
            if len(minhash_hashvalues) % 100000 == 0 or len(minhash_hashvalues) == total_raw:
                print(f"  Signatures computed: {len(minhash_hashvalues)}/{total_raw} [{time.time() - t1:.1f}s]")

    print(f"MinHash signature computation complete in {time.time() - t1:.2f}s!")

    print(f"\nBuilding MinHash LSH Index (Threshold={JACCARD_THRESHOLD}, Perms={NUM_PERM})...")
    lsh = MinHashLSH(threshold=JACCARD_THRESHOLD, num_perm=NUM_PERM)

    t2 = time.time()
    kept_records = []
    removed_count = 0
    duplicates_by_source = {s: 0 for s in SOURCE_PRIORITY}

    for idx in range(total_raw):
        rec = records[idx]
        h_vals = minhash_hashvalues[idx]
        
        # Correctly reconstruct MinHash object in datasketch 2.x
        m = MinHash(num_perm=NUM_PERM, hashvalues=h_vals, scheme=default_scheme)

        result = lsh.query(m)
        if result:
            removed_count += 1
            src = rec.get("source_dataset", "unknown")
            duplicates_by_source[src] = duplicates_by_source.get(src, 0) + 1
        else:
            key = f"r_{idx}"
            lsh.insert(key, m)
            kept_records.append(rec)

        if (idx + 1) % 100000 == 0 or idx == total_raw - 1:
            print(f"  LSH processed {idx + 1}/{total_raw} ({len(kept_records)} kept, {removed_count} duplicates) [{time.time() - t2:.1f}s]")

    total_kept = len(kept_records)
    print(f"\nDeduplication Complete in {time.time() - t0:.2f}s total!")
    print(f"Total Raw    : {total_raw}")
    print(f"Total Kept   : {total_kept} ({total_kept/total_raw:.2%})")
    print(f"Total Removed: {removed_count}")

    print(f"\nWriting deduplicated records to {OUTPUT_FILE}...")
    split_counts = {}
    label_counts = {0: 0, 1: 0}
    source_counts = {}

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for r in kept_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            s = r["split"]
            split_counts[s] = split_counts.get(s, 0) + 1
            lbl = r["label"]
            label_counts[lbl] += 1
            src = r["source_dataset"]
            source_counts[src] = source_counts.get(src, 0) + 1

    stats = {
        "total_raw": total_raw,
        "total_kept": total_kept,
        "removed_count": removed_count,
        "dedup_ratio": total_kept / total_raw if total_raw > 0 else 0.0,
        "splits": split_counts,
        "labels": label_counts,
        "vulnerable_ratio": label_counts[1] / total_kept if total_kept > 0 else 0.0,
        "sources": source_counts,
        "duplicates_removed_by_source": duplicates_by_source
    }

    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    print(f"Saved deduplicated data to {OUTPUT_FILE}")
    print(f"Saved stats to {STATS_FILE}")

if __name__ == "__main__":
    main()
