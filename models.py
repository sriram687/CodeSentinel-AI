import torch
import torch.nn as nn
from transformers.modeling_outputs import SequenceClassifierOutput

class VulBERTa_Vanilla(nn.Module):
    def __init__(self, base_model, n_classes=2, dropout=0.1):
        super().__init__()
        self.num_labels = n_classes
        self.base_model = base_model
        self.dropout = nn.Dropout(dropout)
        self.fc1 = nn.Linear(768, 768)
        self.fc2 = nn.Linear(768, n_classes)
        
    def forward(self, input_ids=None, attention_mask=None, labels=None, **kwargs):
        outputs = self.base_model(input_ids, attention_mask=attention_mask, **kwargs)
        x = outputs[0][:, 0, :]
        x = self.dropout(x)
        x = torch.tanh(self.fc1(x))
        x = self.dropout(x)
        logits = self.fc2(x)
        
        loss = None
        if labels is not None:
            loss_fct = nn.CrossEntropyLoss()
            loss = loss_fct(logits.view(-1, self.num_labels), labels.view(-1))
            
        return SequenceClassifierOutput(loss=loss, logits=logits)

class VulBERTa_Extend(nn.Module):
    def __init__(self, base_model, n_classes=2, dropout=0.1):
        super().__init__()
        self.num_labels = n_classes
        self.base_model = base_model
        self.dropout1 = nn.Dropout(dropout)
        self.dropout2 = nn.Dropout(dropout)
        self.fc1 = nn.Linear(768, 512)
        self.fc2 = nn.Linear(512, 256)
        self.fc3 = nn.Linear(256, n_classes)
        
    def forward(self, input_ids=None, attention_mask=None, labels=None, **kwargs):
        outputs = self.base_model(input_ids, attention_mask=attention_mask, **kwargs)
        x = outputs[0][:, 0, :]
        x = self.dropout1(x)
        x = torch.relu(self.fc1(x))
        x = self.dropout2(x)
        x = torch.relu(self.fc2(x))
        logits = self.fc3(x)
        
        loss = None
        if labels is not None:
            loss_fct = nn.CrossEntropyLoss()
            loss = loss_fct(logits.view(-1, self.num_labels), labels.view(-1))
            
        return SequenceClassifierOutput(loss=loss, logits=logits)
