import os
import sys
import logging
import torch
from utils.cleaner import clean_code
from utils.tokenizer_utils import load_custom_tokenizer
from utils.model_loader import load_sequence_model

logging.getLogger("transformers").setLevel(logging.ERROR)
os.environ["TRANSFORMERS_VERBOSITY"] = "error"

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def scan_code(code_snippet: str):
    tokenizer = load_custom_tokenizer("./tokenizer/drapgh-vocab.json", "./tokenizer/drapgh-merges.txt")
    cleaned = clean_code(code_snippet)
    encoded = tokenizer.encode(cleaned)
    input_ids = torch.tensor([encoded.ids])
    attention_mask = torch.tensor([encoded.attention_mask])

    models_to_scan = [
        ("VB-MLP_draper", "General C/C++ GitHub Benchmark"),
        ("VB-MLP_devign", "OS Kernel & Production Systems (Linux/QEMU)"),
        ("VB-MLP_reveal", "Imbalanced Chromium/Debian Codebase"),
        ("VB-MLP_vuldeepecker", "API Misuse & Buffer Violations"),
        ("VB-MLP_d2a", "IBM Static Analysis False Positive Filter"),
    ]

    print("
" + "="*82)
    print(" 🛡️  CODESENTINEL-AI MAX-RISK SECURITY SCANNER")
    print("="*82)
    print("Input Code Snippet:
")
    print(code_snippet.strip())
    print("-" * 82)
    print(f"{'Model Name':<22} | {'Target Focus Domain':<44} | {'Risk Conf':<9} | {'Verdict'}")
    print("-" * 82)

    results = []
    for model_folder, description in models_to_scan:
        path = os.path.join("./models", model_folder)
        if not os.path.exists(path):
            continue
        try:
            model = load_sequence_model(path)
            with torch.no_grad():
                outputs = model(input_ids=input_ids, attention_mask=attention_mask)
                probs = torch.nn.functional.softmax(outputs.logits, dim=1)
                vuln_prob = probs[0][1].item() * 100
                pred = torch.argmax(probs, dim=1).item()
                status = "[VULNERABLE]" if pred == 1 else "[SAFE]"
                results.append((vuln_prob, model_folder, description, status))
                print(f"{model_folder:<22} | {description:<44} | {vuln_prob:>7.2f}% | {status}")
        except Exception:
            pass

    print("="*82)
    if results:
        max_prob, top_model, top_desc, _ = max(results, key=lambda x: x[0])
        print(f"HIGHEST VULNERABILITY SCORE : {max_prob:.2f}% (Flagged by {top_model})")
        if max_prob >= 50.0:
            print(f"FINAL VERDICT: ⚠️ VULNERABLE CODE DETECTED!")
            print(f"               Detected by specialized domain model: {top_model} ({top_desc})")
        else:
            print(f"FINAL VERDICT: ✅ SAFE CODE")
            print(f"               All models confirmed risk remains below threshold.")
    print("="*82)

if __name__ == "__main__":
    test_code = "void demo(char *src) { char b[32]; strcpy(b, src); }"
    scan_code(test_code)
