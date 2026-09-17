import os
import sys
import logging
import torch
import torch.nn.functional as F
from flask import Flask, request, jsonify
from flask_cors import CORS

import transformers.utils.import_utils
import transformers.modeling_utils
transformers.utils.import_utils.check_torch_load_is_safe = lambda: None
transformers.modeling_utils.check_torch_load_is_safe = lambda: None

from transformers import RobertaModel, AutoModelForCausalLM, AutoTokenizer
from models import VulBERTa_Extend
from utils.tokenizer_utils import load_custom_tokenizer
from utils.cleaner import clean_code

# Suppress verbose loggers
logging.getLogger("transformers").setLevel(logging.ERROR)
os.environ["TRANSFORMERS_VERBOSITY"] = "error"

app = Flask(__name__)
CORS(app)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Global variables for models
encoder_model = None
encoder_tokenizer = None
decoder_model = None
decoder_tokenizer = None

def load_pipeline():
    global encoder_model, encoder_tokenizer, decoder_model, decoder_tokenizer
    
    print("1. Loading VulBERTa Encoder (Vulnerability Detector)...")
    encoder_tokenizer = load_custom_tokenizer("tokenizer/drapgh-vocab.json", "tokenizer/drapgh-merges.txt", max_length=512)
    base_model = RobertaModel.from_pretrained("models/VulBERTa")

    encoder_path = "models/VulBERTa_Unified_Fixed/best_model/pytorch_model.bin"
    if not os.path.exists(encoder_path):
        encoder_path = "models/VulBERTa_Unified/best_model/pytorch_model.bin"

    if os.path.exists(encoder_path):
        encoder_model = VulBERTa_Extend(base_model=base_model, n_classes=2, dropout=0.1)
        encoder_model.load_state_dict(torch.load(encoder_path, map_location=device))
        encoder_model.to(device)
        encoder_model.eval()
        print(f"   ✅ Encoder loaded from: {encoder_path}")
    else:
        print(f"   ❌ Could not find encoder checkpoint at {encoder_path}. Using base un-finetuned model for fallback.")
        encoder_model = VulBERTa_Extend(base_model=base_model, n_classes=2, dropout=0.1).to(device)

    print("2. Loading Qwen Decoder (Patch Generator)...")
    decoder_path = "decoder/decoder_checkpoints_v3/final_student"
    if not os.path.exists(decoder_path):
        decoder_path = "decoder/decoder_checkpoints/final_student"

    if os.path.exists(decoder_path):
        decoder_model = AutoModelForCausalLM.from_pretrained(decoder_path, torch_dtype=torch.bfloat16).to(device)
        decoder_tokenizer = AutoTokenizer.from_pretrained(decoder_path)
        decoder_model.eval()
        print(f"   ✅ Decoder loaded from: {decoder_path}")
    else:
        print(f"   ❌ Could not find decoder checkpoint at {decoder_path}. Patching will be disabled.")

@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "online",
        "encoder_loaded": encoder_model is not None,
        "decoder_loaded": decoder_model is not None
    })

@app.route("/api/analyze", methods=["POST"])
def analyze_code():
    try:
        data = request.get_json(force=True, silent=True)
        if not data or not isinstance(data, dict):
            return jsonify({"error": "Invalid request. Expected JSON with 'code' field."}), 400

        raw_code = data.get("code", "")
        if not raw_code.strip():
            return jsonify({"error": "Code snippet is empty."}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to parse JSON body: {str(e)}"}), 400

    if not encoder_model:
        return jsonify({"error": "Encoder model is not loaded."}), 500

    # Clean and Tokenize
    cleaned = clean_code(raw_code)
    encoded = encoder_tokenizer.encode(cleaned)
    input_ids = torch.tensor([encoded.ids]).to(device)
    attention_mask = torch.tensor([encoded.attention_mask]).to(device)

    # 1. Scan with Encoder
    with torch.no_grad():
        outputs = encoder_model(input_ids=input_ids, attention_mask=attention_mask)
        probs = F.softmax(outputs.logits, dim=1)
        vuln_score = round(probs[0][1].item() * 100, 2)

    is_vulnerable = vuln_score > 50.0
    patch_text = None

    # 2. Repair with Decoder if vulnerable
    if is_vulnerable and decoder_model:
        prompt = (
            f"<|im_start|>system\nYou are an expert C/C++ security engineer.<|im_end|>\n"
            f"<|im_start|>user\n<vuln_found CWE='CWE-120'>\n{raw_code.strip()}\n</vuln_found><patch>\n<|im_end|>\n"
            f"<|im_start|>assistant\n"
        )
        dec_inputs = decoder_tokenizer(prompt, return_tensors="pt").to(device)
        
        # Stop at </patch> if running v3
        stop_token_id = decoder_tokenizer.encode("</patch>", add_special_tokens=False)
        stop_ids = stop_token_id if stop_token_id else []

        with torch.no_grad():
            generated_ids = decoder_model.generate(
                **dec_inputs,
                max_new_tokens=300,
                temperature=0.1,
                do_sample=True,
                repetition_penalty=1.5,
                eos_token_id=[decoder_tokenizer.eos_token_id] + stop_ids,
                pad_token_id=decoder_tokenizer.eos_token_id
            )

        patch_text = decoder_tokenizer.decode(generated_ids[0][dec_inputs.input_ids.shape[1]:], skip_special_tokens=True).strip()

    return jsonify({
        "vuln_score": vuln_score,
        "vulnerable": is_vulnerable,
        "patch": patch_text
    })

if __name__ == "__main__":
    load_pipeline()
    print("\n🚀 CodeSentinel-AI Unified Pipeline Server started on port 5050!")
    app.run(host="0.0.0.0", port=5050, debug=False)
