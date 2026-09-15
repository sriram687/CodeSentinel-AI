"""
eval_baseline.py
Baseline Evaluation of 10-Model MaxRisk Ensemble on PrimeVul Test Split

Loads all 10 specialized VulBERTa models (5x VB-MLP, 4x VB-CNN, 1x D2A)
and evaluates them on PrimeVul test set to compute baseline MCC benchmark.
"""

import os
import json
import torch
import numpy as np
from sklearn.metrics import matthews_corrcoef, f1_score, precision_score, recall_score, accuracy_score
from utils.cleaner import clean_code
from utils.tokenizer_utils import load_custom_tokenizer
from utils.model_loader import load_sequence_model

PRIMEVUL_TEST_FILE = os.path.join(os.path.dirname(__file__), "data", "finetune", "primevul", "PrimeVul.json")
MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
VOCAB_PATH = os.path.join(os.path.dirname(__file__), "tokenizer", "drapgh-vocab.json")
MERGES_PATH = os.path.join(os.path.dirname(__file__), "tokenizer", "drapgh-merges.txt")
OUTPUT_METRICS_FILE = os.path.join(os.path.dirname(__file__), "data", "eval_baseline_results.json")

def load_primevul_test_set():
    print(f"Loading PrimeVul test set from {PRIMEVUL_TEST_FILE}...")
    samples = []
    with open(PRIMEVUL_TEST_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            obj = json.loads(line)
            if obj.get("hf_split") == "test":
                code = obj.get("func", "").strip()
                if code:
                    samples.append({
                        "code": code,
                        "label": int(obj.get("target", 0))
                    })
    print(f"Loaded {len(samples)} PrimeVul test samples.")
    return samples

def main():
    test_samples = load_primevul_test_set()
    labels = np.array([s["label"] for s in test_samples])

    print("Loading VulBERTa Tokenizer...")
    tokenizer = load_custom_tokenizer(VOCAB_PATH, MERGES_PATH, max_length=512)

    model_names = [
        "VB-MLP_draper",
        "VB-MLP_devign",
        "VB-MLP_reveal",
        "VB-MLP_vuldeepecker",
        "VB-MLP_d2a",
        "VB-MLP_mvd",
        "VB-CNN_devign",
        "VB-CNN_reveal",
        "VB-CNN_vuldeepecker",
        "VB-CNN_mvd"
    ]

    available_models = []
    for name in model_names:
        path = os.path.join(MODELS_DIR, name)
        if os.path.exists(path):
            available_models.append(name)
        else:
            print(f"Warning: Model directory {name} not found, skipping.")

    print(f"\nEvaluating {len(available_models)} available models on {len(test_samples)} samples...")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    all_model_probs = {}

    for m_name in available_models:
        print(f"\nEvaluating model: {m_name}...")
        m_path = os.path.join(MODELS_DIR, m_name)
        model = load_sequence_model(m_path)
        model.to(device)
        model.eval()

        probs_list = []
        batch_size = 64
        
        for i in range(0, len(test_samples), batch_size):
            batch = test_samples[i : i + batch_size]
            cleaned_codes = [clean_code(b["code"]) for b in batch]
            
            # Tokenize batch
            encodings = [tokenizer.encode(c) for c in cleaned_codes]
            input_ids = torch.tensor([e.ids for e in encodings], dtype=torch.long).to(device)
            attention_mask = torch.tensor([e.attention_mask for e in encodings], dtype=torch.long).to(device)

            with torch.no_grad():
                outputs = model(input_ids=input_ids, attention_mask=attention_mask)
                probs = torch.nn.functional.softmax(outputs.logits, dim=1)[:, 1].cpu().numpy()
                probs_list.extend(probs)

        probs_arr = np.array(probs_list)
        all_model_probs[m_name] = probs_arr
        preds = (probs_arr >= 0.5).astype(int)

        mcc = matthews_corrcoef(labels, preds)
        acc = accuracy_score(labels, preds)
        prec = precision_score(labels, preds, zero_division=0)
        rec = recall_score(labels, preds, zero_division=0)
        f1 = f1_score(labels, preds, zero_division=0)

        print(f"  {m_name:<22} -> MCC: {mcc:.4f} | Acc: {acc:.4f} | F1: {f1:.4f} | Prec: {prec:.4f} | Rec: {rec:.4f}")

    # Compute MaxRisk Ensemble (Maximum Vuln Probability across all models)
    if all_model_probs:
        max_risk_probs = np.maximum.reduce(list(all_model_probs.values()))
        max_risk_preds = (max_risk_probs >= 0.5).astype(int)

        ens_mcc = matthews_corrcoef(labels, max_risk_preds)
        ens_acc = accuracy_score(labels, max_risk_preds)
        ens_prec = precision_score(labels, max_risk_preds, zero_division=0)
        ens_rec = recall_score(labels, max_risk_preds, zero_division=0)
        ens_f1 = f1_score(labels, max_risk_preds, zero_division=0)

        print("\n" + "="*80)
        print(" 🔥 10-MODEL MAX-RISK ENSEMBLE BASELINE METRICS (PrimeVul Test Split)")
        print("="*80)
        print(f"  MCC       : {ens_mcc:.4f}")
        print(f"  Accuracy  : {ens_acc:.4f}")
        print(f"  F1-Score  : {ens_f1:.4f}")
        print(f"  Precision : {ens_prec:.4f}")
        print(f"  Recall    : {ens_rec:.4f}")
        print("="*80)

        results = {
            "max_risk_ensemble": {
                "mcc": float(ens_mcc),
                "accuracy": float(ens_acc),
                "f1": float(ens_f1),
                "precision": float(ens_prec),
                "recall": float(ens_rec)
            },
            "individual_models": {
                name: {
                    "mcc": float(matthews_corrcoef(labels, (probs >= 0.5).astype(int))),
                    "f1": float(f1_score(labels, (probs >= 0.5).astype(int), zero_division=0))
                } for name, probs in all_model_probs.items()
            }
        }

        with open(OUTPUT_METRICS_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        print(f"\nResults saved to {OUTPUT_METRICS_FILE}")

if __name__ == "__main__":
    main()
