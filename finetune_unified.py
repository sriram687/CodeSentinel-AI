"""
finetune_unified.py
Unified Fine-Tuning Script for VulBERTa_Extend (CodeSentinel-AI)

Trains a single, unified VulBERTa_Extend model on all 8 vulnerability datasets
using the B200 GPU cluster (or high-memory GPU environment).

Optimized Config for Single B200 GPU:
  - CUDA_VISIBLE_DEVICES=4 (or CLI arg --cuda_device)
  - Batch Size: 1024
  - Precision: BF16 (bfloat16)
  - Backbone LR: 3.2e-4 | Head LR: 1.6e-3 (5x ratio)
  - Loss: Class-Weighted CrossEntropyLoss
  - Evaluates MCC per epoch & saves best checkpoint
"""

import os
import sys
import json
import time
import math
import argparse
from typing import List, Dict, Any

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import numpy as np
from sklearn.metrics import matthews_corrcoef, f1_score, precision_score, recall_score, accuracy_score, roc_auc_score

from transformers import RobertaModel, RobertaConfig, get_linear_schedule_with_warmup
from models import VulBERTa_Extend
from utils.cleaner import clean_code
from utils.tokenizer_utils import load_custom_tokenizer

class CodeVulnerabilityDataset(Dataset):
    def __init__(self, data_records: List[Dict[str, Any]], tokenizer, max_length: int = 512):
        self.records = data_records
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.records)

    def __getitem__(self, idx):
        rec = self.records[idx]
        code = clean_code(rec["code"])
        label = int(rec["label"])
        
        encoded = self.tokenizer.encode(code)
        input_ids = encoded.ids
        attention_mask = encoded.attention_mask

        # Truncate / pad to max_length if needed
        if len(input_ids) > self.max_length:
            input_ids = input_ids[:self.max_length]
            attention_mask = attention_mask[:self.max_length]

        return {
            "input_ids": torch.tensor(input_ids, dtype=torch.long),
            "attention_mask": torch.tensor(attention_mask, dtype=torch.long),
            "labels": torch.tensor(label, dtype=torch.long),
            "source": rec.get("source_dataset", "unknown")
        }

def collate_fn(batch):
    max_len = max(len(item["input_ids"]) for item in batch)
    
    input_ids_padded = []
    attention_mask_padded = []
    labels = []
    sources = []

    for item in batch:
        pad_len = max_len - len(item["input_ids"])
        # pad token id = 1 for RoBERTa
        input_ids_padded.append(torch.cat([item["input_ids"], torch.ones(pad_len, dtype=torch.long)]))
        attention_mask_padded.append(torch.cat([item["attention_mask"], torch.zeros(pad_len, dtype=torch.long)]))
        labels.append(item["labels"])
        sources.append(item["source"])

    return {
        "input_ids": torch.stack(input_ids_padded),
        "attention_mask": torch.stack(attention_mask_padded),
        "labels": torch.stack(labels),
        "sources": sources
    }

def evaluate(model, dataloader, device, loss_fct=None, mixed_precision_type=torch.bfloat16):
    model.eval()
    total_loss = 0.0
    all_preds = []
    all_probs = []
    all_targets = []
    primevul_preds = []
    primevul_probs = []
    primevul_targets = []

    use_amp = device.type == "cuda" and mixed_precision_type is not None

    with torch.no_grad():
        for batch in dataloader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)
            sources = batch["sources"]

            with torch.amp.autocast(device_type=device.type, dtype=mixed_precision_type, enabled=use_amp):
                outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
                logits = outputs.logits
                if loss_fct is not None:
                    loss = loss_fct(logits, labels)
                    total_loss += loss.item() * len(labels)

            probs = torch.softmax(logits, dim=1)[:, 1].cpu().numpy()
            preds = np.argmax(logits.cpu().numpy(), axis=1)
            targets = labels.cpu().numpy()

            all_probs.extend(probs)
            all_preds.extend(preds)
            all_targets.extend(targets)

            # Filter PrimeVul subset for targeted gate evaluation
            for p, pr, t, s in zip(preds, probs, targets, sources):
                if s == "primevul":
                    primevul_preds.append(p)
                    primevul_probs.append(pr)
                    primevul_targets.append(t)

    all_targets = np.array(all_targets)
    all_preds = np.array(all_preds)
    all_probs = np.array(all_probs)

    avg_loss = total_loss / len(all_targets) if loss_fct is not None else 0.0
    mcc = matthews_corrcoef(all_targets, all_preds)
    acc = accuracy_score(all_targets, all_preds)
    prec = precision_score(all_targets, all_preds, zero_division=0)
    rec = recall_score(all_targets, all_preds, zero_division=0)
    f1 = f1_score(all_targets, all_preds, zero_division=0)
    try:
        auc = roc_auc_score(all_targets, all_probs)
    except Exception:
        auc = 0.5

    pv_mcc = 0.0
    if len(primevul_targets) > 0:
        pv_mcc = matthews_corrcoef(np.array(primevul_targets), np.array(primevul_preds))

    return {
        "loss": avg_loss,
        "mcc": float(mcc),
        "accuracy": float(acc),
        "precision": float(prec),
        "recall": float(rec),
        "f1": float(f1),
        "auc": float(auc),
        "primevul_mcc": float(pv_mcc)
    }

def parse_args():
    parser = argparse.ArgumentParser(description="Fine-tune VulBERTa_Extend on Unified Dataset")
    parser.add_argument("--data_file", type=str, default="data/merged/merged_deduped.jsonl")
    parser.add_argument("--output_dir", type=str, default="models/VulBERTa_Unified")
    parser.add_argument("--batch_size", type=int, default=1024)
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--backbone_lr", type=float, default=3.2e-4)
    parser.add_argument("--head_lr", type=float, default=1.6e-3)
    parser.add_argument("--max_length", type=int, default=512)
    parser.add_argument("--warmup_ratio", type=float, default=0.1)
    parser.add_argument("--mixed_precision", type=str, default="bf16", choices=["bf16", "fp16", "fp32"])
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--num_workers", type=int, default=4)
    return parser.parse_args()

def main():
    args = parse_args()
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)

    print("="*80)
    print(" 🚀 VULBERTA_EXTEND UNIFIED TRAINING PIPELINE (CodeSentinel-AI)")
    print("="*80)
    print(f"Data File        : {args.data_file}")
    print(f"Output Directory : {args.output_dir}")
    print(f"Batch Size       : {args.batch_size}")
    print(f"Epochs           : {args.epochs}")
    print(f"Backbone LR      : {args.backbone_lr}")
    print(f"Classification LR: {args.head_lr}")
    print(f"Precision Mode   : {args.mixed_precision}")
    print("="*80)

    os.makedirs(args.output_dir, exist_ok=True)

    # Set up Device & AMP Dtype
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    if device.type == "cuda":
        gpu_name = torch.cuda.get_device_name(0)
        vram_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
        print(f"GPU Model: {gpu_name} ({vram_gb:.2f} GB VRAM)")

    amp_dtype = None
    if args.mixed_precision == "bf16":
        amp_dtype = torch.bfloat16
    elif args.mixed_precision == "fp16":
        amp_dtype = torch.float16

    # Load Tokenizer
    vocab_path = os.path.join(os.path.dirname(__file__), "tokenizer", "drapgh-vocab.json")
    merges_path = os.path.join(os.path.dirname(__file__), "tokenizer", "drapgh-merges.txt")
    print("\nLoading VulBERTa Tokenizer...")
    tokenizer = load_custom_tokenizer(vocab_path, merges_path, max_length=args.max_length)

    # Load Data Records
    print(f"\nLoading data records from {args.data_file}...")
    train_records, val_records, test_records = [], [], []

    with open(args.data_file, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            s = r.get("split", "train")
            if s == "train":
                train_records.append(r)
            elif s == "validation" or s == "valid":
                val_records.append(r)
            elif s == "test":
                test_records.append(r)

    print(f"Split counts -> Train: {len(train_records)}, Validation: {len(val_records)}, Test: {len(test_records)}")

    # Compute Class Weights for Imbalanced Loss
    n_safe = sum(1 for r in train_records if int(r["label"]) == 0)
    n_vuln = sum(1 for r in train_records if int(r["label"]) == 1)
    pos_weight = n_safe / float(max(1, n_vuln))
    print(f"Class imbalance ratio: {n_safe} Safe vs {n_vuln} Vulnerable (pos_weight = {pos_weight:.2f})")

    class_weights = torch.tensor([1.0, float(pos_weight)], dtype=torch.float).to(device)
    loss_fct = nn.CrossEntropyLoss(weight=class_weights)

    # Create Datasets & DataLoaders
    train_dataset = CodeVulnerabilityDataset(train_records, tokenizer, max_length=args.max_length)
    val_dataset = CodeVulnerabilityDataset(val_records, tokenizer, max_length=args.max_length)
    test_dataset = CodeVulnerabilityDataset(test_records, tokenizer, max_length=args.max_length)

    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True, collate_fn=collate_fn, num_workers=args.num_workers)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False, collate_fn=collate_fn, num_workers=args.num_workers)
    test_loader = DataLoader(test_dataset, batch_size=args.batch_size, shuffle=False, collate_fn=collate_fn, num_workers=args.num_workers)

    # Initialize VulBERTa_Extend Model
    print("\nInitializing VulBERTa_Extend Model with roberta-base backbone...")
    base_model = RobertaModel.from_pretrained("roberta-base")
    model = VulBERTa_Extend(base_model=base_model, n_classes=2, dropout=0.1)
    model.to(device)

    # Differential Learning Rates Setup
    optimizer_grouped_parameters = [
        {
            "params": [p for n, p in model.base_model.named_parameters() if p.requires_grad],
            "lr": args.backbone_lr,
            "weight_decay": 0.01
        },
        {
            "params": [p for n, p in model.named_parameters() if "base_model" not in n and p.requires_grad],
            "lr": args.head_lr,
            "weight_decay": 0.01
        }
    ]

    optimizer = torch.optim.AdamW(optimizer_grouped_parameters)
    
    total_steps = len(train_loader) * args.epochs
    warmup_steps = int(total_steps * args.warmup_ratio)
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=warmup_steps, num_training_steps=total_steps)

    scaler = torch.amp.GradScaler('cuda', enabled=(device.type == "cuda" and amp_dtype == torch.float16))

    best_val_mcc = -1.0
    best_checkpoint_dir = os.path.join(args.output_dir, "best_model")

    print(f"\nStarting Training for {args.epochs} Epochs ({total_steps} total steps)...")
    start_train_time = time.time()

    for epoch in range(1, args.epochs + 1):
        model.train()
        epoch_loss = 0.0
        epoch_start = time.time()

        for step, batch in enumerate(train_loader, 1):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            optimizer.zero_grad()

            with torch.amp.autocast(device_type=device.type, dtype=amp_dtype, enabled=(amp_dtype is not None)):
                outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
                logits = outputs.logits
                loss = loss_fct(logits, labels)

            if scaler.is_enabled():
                scaler.scale(loss).backward()
                scaler.step(optimizer)
                scaler.update()
            else:
                loss.backward()
                optimizer.step()

            scheduler.step()
            epoch_loss += loss.item()

            if step % 20 == 0 or step == len(train_loader):
                print(f"  Epoch [{epoch}/{args.epochs}] Step [{step}/{len(train_loader)}] Loss: {loss.item():.4f} | Elapsed: {time.time() - epoch_start:.1f}s")

        avg_train_loss = epoch_loss / len(train_loader)
        
        # Validation Evaluation
        print(f"\n  Evaluating Epoch {epoch} Validation Performance...")
        val_metrics = evaluate(model, val_loader, device, loss_fct, mixed_precision_type=amp_dtype)
        
        print(f"  Validation -> Loss: {val_metrics['loss']:.4f} | MCC: {val_metrics['mcc']:.4f} | PrimeVul MCC: {val_metrics['primevul_mcc']:.4f} | F1: {val_metrics['f1']:.4f} | Acc: {val_metrics['accuracy']:.4f}")

        # Checkpoint Saving based on Best Validation MCC
        if val_metrics["mcc"] > best_val_mcc:
            best_val_mcc = val_metrics["mcc"]
            print(f"  🔥 New Best Validation MCC: {best_val_mcc:.4f}! Saving checkpoint to {best_checkpoint_dir}...")
            os.makedirs(best_checkpoint_dir, exist_ok=True)
            torch.save(model.state_dict(), os.path.join(best_checkpoint_dir, "pytorch_model.bin"))
            with open(os.path.join(best_checkpoint_dir, "val_metrics.json"), "w") as f:
                json.dump(val_metrics, f, indent=2)

    total_training_time = time.time() - start_train_time
    print(f"\nTraining Complete in {total_training_time / 60:.2f} minutes!")

    # Final Test Set Evaluation
    print("\n" + "="*80)
    print(" 🏆 FINAL EVALUATION ON HELD-OUT TEST SPLITS")
    print("="*80)

    print("Loading Best Checkpoint Model...")
    model.load_state_dict(torch.load(os.path.join(best_checkpoint_dir, "pytorch_model.bin")))
    test_metrics = evaluate(model, test_loader, device, loss_fct, mixed_precision_type=amp_dtype)

    print(f"Full Test Set Metrics:")
    print(f"  MCC           : {test_metrics['mcc']:.4f}")
    print(f"  PrimeVul MCC  : {test_metrics['primevul_mcc']:.4f}")
    print(f"  Accuracy      : {test_metrics['accuracy']:.4f}")
    print(f"  F1-Score      : {test_metrics['f1']:.4f}")
    print(f"  Precision     : {test_metrics['precision']:.4f}")
    print(f"  Recall        : {test_metrics['recall']:.4f}")
    print(f"  ROC-AUC       : {test_metrics['auc']:.4f}")

    summary = {
        "best_val_mcc": float(best_val_mcc),
        "total_training_time_seconds": float(total_training_time),
        "test_metrics": test_metrics,
        "config": vars(args)
    }

    with open(os.path.join(args.output_dir, "training_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nAll training results saved to {os.path.join(args.output_dir, 'training_summary.json')}")

if __name__ == "__main__":
    main()
