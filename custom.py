import torch

class CustomDataCollatorForLanguageModeling:
    def __init__(self, tokenizer, mlm=True, mlm_probability=0.15):
        self.tokenizer = tokenizer
        self.mlm = mlm
        self.mlm_probability = mlm_probability

    def __call__(self, examples):
        batch = torch.tensor(examples, dtype=torch.long)
        return {"input_ids": batch, "attention_mask": (batch != 1).long()}
