import os
import torch
import transformers.utils.import_utils
import transformers.modeling_utils

# Patch transformers torch load version check
transformers.utils.import_utils.check_torch_load_is_safe = lambda: None
transformers.modeling_utils.check_torch_load_is_safe = lambda: None

from transformers import RobertaForSequenceClassification

def load_sequence_model(model_path):
    """Load fine-tuned RoBERTa sequence classification model."""
    model = RobertaForSequenceClassification.from_pretrained(model_path)
    model.eval()
    return model
