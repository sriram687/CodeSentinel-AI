import os
import sys
import torch
from utils.cleaner import clean_code
from utils.tokenizer_utils import load_custom_tokenizer
from utils.model_loader import load_sequence_model

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def predict_vulnerability(code_snippet: str, model_path: str = "./models/VB-MLP_draper"):
    tokenizer = load_custom_tokenizer("./tokenizer/drapgh-vocab.json", "./tokenizer/drapgh-merges.txt")
    model = load_sequence_model(model_path)
    
    cleaned = clean_code(code_snippet)
    encoded = tokenizer.encode(cleaned)
    input_ids = torch.tensor([encoded.ids])
    attention_mask = torch.tensor([encoded.attention_mask])

    with torch.no_grad():
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        probs = torch.nn.functional.softmax(outputs.logits, dim=1)
        vuln_prob = probs[0][1].item() * 100
        prediction = torch.argmax(probs, dim=1).item()

    print(f"Risk Score: {vuln_prob:.2f}% | Status: {'[VULNERABLE]' if prediction==1 else '[SAFE]'}")
    return vuln_prob, prediction

if __name__ == "__main__":
    code = "void test(char *input) { char buf[16]; strcpy(buf, input); }"
    predict_vulnerability(code)
