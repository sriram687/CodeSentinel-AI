# VulBERTa / CodeSentinel-AI: Deep Learning Model Architecture & Fine-Tuning Pipeline

## 📌 Executive Technical Summary
**CodeSentinel-AI** (built on the **VulBERTa** framework) is a deep learning machine learning platform designed for automated vulnerability detection in C/C++ source code. The system uses pre-trained **RoBERTa (Robustly Optimized BERT Approach)** transformer language models, fine-tuned with specialized **Multi-Layer Perceptron (MLP)** and **1D-Convolutional Neural Network (CNN)** classification heads across 6 domain-specific security datasets.

This document details the complete machine learning architecture, pre-training methodology, fine-tuning procedures, dataset curations, loss functions, tokenization pipelines, framework dependencies, and backend inference engines.

---

## 🛠️ Frameworks & Technical Dependencies Stack

The backend machine learning pipeline is built on the following core frameworks and Python libraries:

| Library / Framework | Version Requirement | Technical Purpose & Usage in Codebase |
|---|---|---|
| **PyTorch (`torch`, `torch.nn`)** | `>=1.10.0` | Deep learning computation framework, neural network layers (`nn.Linear`, `nn.Dropout`, `nn.Tanh`, `nn.ReLU`), loss functions (`CrossEntropyLoss`), softmax activation, and CUDA GPU tensor execution. |
| **Hugging Face Transformers (`transformers`)** | `>=4.15.0` | RoBERTa transformer encoder model backbone (`RobertaModel`, `RobertaForSequenceClassification`, `RobertaConfig`), `SequenceClassifierOutput` data structures, and checkpoint state loading. |
| **Hugging Face Tokenizers (`tokenizers`)** | `>=0.11.0` | Custom Byte-Pair Encoding (`BPE`) model, normalizers (`StripAccents`, `Replace`), custom pre-tokenizer (`PreTokenizer.custom`), and template processors (`TemplateProcessing`). |
| **libclang / Clang AST (`clang.cindex`)** | `libclang.dll` | Clang C-API binding used for syntactical AST pre-tokenization (`clang_split`) to parse C source code constructs prior to subword BPE tokenization. |
| **Flask & Flask-CORS (`flask`, `flask_cors`)** | `>=2.0.0` | Python REST API backend server serving live multi-model inference endpoints (`/api/scan`, `/api/models`, `/api/health`). |
| **Scikit-Learn (`sklearn.metrics`)** | `>=0.24.0` | Classification performance metrics calculation (`accuracy_score`, `precision_score`, `recall_score`, `f1_score`, `confusion_matrix`). |
| **NumPy (`numpy`)** | `>=1.20.0` | Numerical array processing and tensor conversion. |

---

## 🏗️ End-to-End Machine Learning Pipeline

```
[ Raw C/C++ Code Snippet ]
          │
          ▼
[ Code Cleaner & Preprocessor ] ───────> Strips block/inline comments, flattens whitespace
          │
          ▼
[ Clang AST Pre-Tokenizer ] ───────────> Parses C syntax tree (tmp.c) via libclang C-Index
          │
          ▼
[ Byte-Pair Encoding (BPE) ] ──────────> Subword tokenization (50,000 vocab size)
          │
          ▼
[ Special Token Processor ] ───────────> Inserts <s> (BOS), </s> (EOS), <pad>, <unk>, <mask>
          │
          ▼
[ RoBERTa Encoder Backbone ] ──────────> 12 Transformer Layers, 768-dim embeddings
          │
  ┌───────┴─────────────────────────────────┐
  ▼                                         ▼
[ VulBERTa_Vanilla MLP Head ]     [ VulBERTa_Extend MLP Head ]
- Tanh Activation                 - Double ReLU Activation
- Dense(768 -> 768 -> 2)          - Dense(768 -> 512 -> 256 -> 2)
  │                                         │
  └───────────────────┬─────────────────────┘
                      ▼
        [ Multi-Model Domain Ensemble ]
  - VB-MLP_draper       - VB-MLP_devign       - VB-CNN_devign
  - VB-MLP_reveal       - VB-CNN_reveal       - VB-MLP_vuldeepecker
  - VB-CNN_vuldeepecker - VB-MLP_mvd          - VB-CNN_mvd
  - VB-MLP_d2a
                      │
                      ▼
     [ Softmax Logits & Risk Score ] ─────> Calculates P(vulnerable) % & max risk
                      │
                      ▼
     [ Line Attention Risk Engine ] ──────> Computes line-level risk scores
```

---

## 🔤 C/C++ Tokenization & AST Preprocessing (`utils/cleaner.py` & `utils/tokenizer_utils.py`)

Standard natural language tokenizers fail on source code because programming languages rely on strict syntactic syntax, pointer operators, and custom identifiers. VulBERTa solves this using a two-stage hybrid tokenization pipeline:

### 1. Code Cleaning & Normalization (`utils/cleaner.py`)
Before tokenization, raw C/C++ source code passes through regex cleaning to remove non-executable artifacts:
* Strips C multi-line comments (`/* ... */`) and single-line comments (`// ...`).
* Flattens tabs (`\t`) and newlines (`\n`) into standardized single spaces.

### 2. Clang AST-Guided Pre-Tokenization (`utils/tokenizer_utils.py`)
* Leverages `libclang` (`clang.cindex`) to parse the cleaned code string into a temporary translation unit (`tmp.c`).
* The custom pre-tokenizer (`MyTokenizer.clang_split`) traverses the Clang AST cursor extents, splitting code strictly along C lexical syntax boundaries (keywords, variable names, operators, delimiters) before subword encoding.

### 3. Custom Byte-Pair Encoding (BPE) Vocabulary
* **Vocabulary Size**: 50,000 tokens trained specifically on C/C++ source code datasets (`tokenizer/drapgh-vocab.json`, `tokenizer/drapgh-merges.txt`).
* **Normalizer**: Applies `StripAccents()` and replaces spaces with symbol `Ä`.
* **Special Tokens Template**:
  * `<s>` (ID: 0) — Beginning of Sequence (BOS)
  * `<pad>` (ID: 1) — Padding token
  * `</s>` (ID: 2) — End of Sequence (EOS)
  * `<unk>` (ID: 3) — Unknown token
  * `<mask >` (ID: 4) — Masked language modeling token
* **Sequence Control**: Enforces truncation to a maximum sequence length of **1024 tokens** (`MAX_SEQ_LENGTH = 1024`).

---

## 🧠 Base Model Pre-Training Architecture & MLM Objective

### 1. Transformer Architecture Parameters
* **Model Type**: RoBERTa Transformer Encoder (`RobertaModel`)
* **Hidden Layers**: 12 Transformer Encoder layers
* **Hidden Dimension ($d_{model}$)**: 768
* **Attention Heads**: 12
* **Feed-Forward Network Dimension ($d_{ff}$)**: 3072
* **Total Parameters**: ~110 Million parameters

### 2. Unsupervised Pre-Training Objective
* **Pre-Training Corpus**: **1,200,000+ C/C++ functions** collected from open-source GitHub repositories.
* **Pre-Training Task**: **Masked Language Modeling (MLM)**.
* **Masking Probability**: 15% of tokens in each sequence are randomly selected:
  * 80% replaced with the special `<mask >` token.
  * 10% replaced with a random token from the 50,000 BPE vocabulary.
  * 10% kept unchanged.
* **Objective**: Minimizes Cross-Entropy Loss over masked token predictions to learn deep syntax representation of C/C++ code, variable lifetimes, pointer references, and memory allocation structures.

---

## 📐 Fine-Tuning Classifier Heads & Loss Functions (`models.py`)

During fine-tuning, the pre-trained RoBERTa backbone pooler representation ($\mathbf{h}_{[CLS]} \in \mathbb{R}^{768}$) is connected to task-specific classification heads.

### 1. `VulBERTa_Vanilla` Head Architecture
Standard sequence classification head using a single non-linear projection with Tanh activation:

$$\mathbf{x}_1 = \text{Dropout}(\mathbf{h}_{[CLS]}, p=0.1)$$
$$\mathbf{x}_2 = \text{Tanh}(\mathbf{W}_1 \mathbf{x}_1 + \mathbf{b}_1) \quad \text{where } \mathbf{W}_1 \in \mathbb{R}^{768 \times 768}$$
$$\mathbf{x}_3 = \text{Dropout}(\mathbf{x}_2, p=0.1)$$
$$\mathbf{z} = \mathbf{W}_2 \mathbf{x}_3 + \mathbf{b}_2 \quad \text{where } \mathbf{W}_2 \in \mathbb{R}^{768 \times 2}$$

### 2. `VulBERTa_Extend` Head Architecture
Extended multi-stage deep classifier head using double ReLU activations:

$$\mathbf{x}_1 = \text{Dropout1}(\mathbf{h}_{[CLS]}, p=0.1)$$
$$\mathbf{x}_2 = \text{ReLU}(\mathbf{W}_1 \mathbf{x}_1 + \mathbf{b}_1) \quad \text{where } \mathbf{W}_1 \in \mathbb{R}^{768 \times 512}$$
$$\mathbf{x}_3 = \text{Dropout2}(\mathbf{x}_2, p=0.1)$$
$$\mathbf{x}_4 = \text{ReLU}(\mathbf{W}_2 \mathbf{x}_3 + \mathbf{b}_2) \quad \text{where } \mathbf{W}_2 \in \mathbb{R}^{512 \times 256}$$
$$\mathbf{z} = \mathbf{W}_3 \mathbf{x}_4 + \mathbf{b}_3 \quad \text{where } \mathbf{W}_3 \in \mathbb{R}^{256 \times 2}$$

### 3. VulBERTa-CNN Head Architecture (1D-Convolutional Scanner)
Passes the sequence of token hidden states $\mathbf{H} \in \mathbb{R}^{L \times 768}$ output by RoBERTa through 1D convolutional layers with sliding window kernel sizes ($k \in \{3, 5, 7\}$):

$$\mathbf{C}_k = \text{ReLU}(\text{Conv1D}_k(\mathbf{H}))$$
$$\mathbf{y}_k = \text{MaxOverTimePooling}(\mathbf{C}_k)$$
$$\mathbf{z} = \mathbf{W}_{concat} [\mathbf{y}_3 \parallel \mathbf{y}_5 \parallel \mathbf{y}_7] + \mathbf{b}$$

### 4. Loss Function & Probability Output
Both MLP and CNN heads compute loss during training using binary Cross-Entropy Loss:

$$\mathcal{L} = -\frac{1}{N} \sum_{i=1}^{N} \left[ y_i \log(\hat{p}_i) + (1 - y_i) \log(1 - \hat{p}_i) \right]$$

During inference, logits $\mathbf{z} = [z_0, z_1]$ are normalized via Softmax to obtain the vulnerability probability score:

$$P(\text{vulnerable}) = \frac{e^{z_1}}{e^{z_0} + e^{z_1}} \times 100\%$$

---

## ⚙️ Fine-Tuning Training Hyperparameters

| Hyperparameter | Value | Description |
|---|---|---|
| **Optimizer** | `AdamW` | Adam with decoupled weight decay regularization. |
| **Learning Rate ($\alpha$)** | $2 \times 10^{-5}$ | Fine-tuning learning rate for RoBERTa encoder backbone. |
| **Classifier Head LR** | $1 \times 10^{-4}$ | Learning rate for newly initialized dense layers. |
| **LR Scheduler** | Linear Warmup | Linear warmup for first 10% of training steps, followed by linear decay. |
| **Adam $\beta_1, \beta_2$** | $0.9, 0.999$ | Exponential decay rates for momentum vector estimates. |
| **Adam $\epsilon$** | $1 \times 10^{-8}$ | Numerical stability constant. |
| **Batch Size** | 32 / 64 | Per-device batch size (leveraging gradient accumulation). |
| **Weight Decay** | $0.01$ | Regularization to prevent overfitting on small datasets. |
| **Dropout Rate** | $0.1$ | Dropout probability applied across dense hidden layers. |
| **Max Epochs** | $5 - 10$ | Fine-tuning epochs with early stopping monitored on validation F1 score. |

---

## 📊 Fine-Tuned Model Checkpoints & Dataset Matrix

CodeSentinel-AI features **10 specialized fine-tuned model checkpoints** across **6 security benchmark datasets**:

```
models/
├── VB-MLP_draper/           # Draper VDIS General C/C++ Benchmark (MLP)
├── VB-MLP_devign/           # Linux Kernel & QEMU Security Commits (MLP)
├── VB-CNN_devign/           # Linux Kernel 1D-CNN Scanner
├── VB-MLP_reveal/           # ReVeal Imbalanced Chromium/Debian Code (MLP)
├── VB-CNN_reveal/           # ReVeal Imbalanced 1D-CNN Scanner
├── VB-MLP_vuldeepecker/     # VulDeePecker C API Misuse & Buffer Violations (MLP)
├── VB-CNN_vuldeepecker/     # VulDeePecker 1D-CNN Scanner
├── VB-MLP_mvd/              # Multi-Class Vulnerability Dataset (MLP)
├── VB-CNN_mvd/              # Multi-Class 1D-CNN Scanner
└── VB-MLP_d2a/              # IBM Static Analysis False Positive Filter (MLP)
```

### Detailed Dataset Breakdown & Target Specifications

#### 1. **Draper VDIS Benchmark (`VB-MLP_draper`)**
* **Dataset Size**: **1,274,104 C/C++ functions** collected by Draper Laboratory.
* **CWE Coverage**: CWE-119 (Buffer Error), CWE-120 (Buffer Copy), CWE-476 (NULL Pointer), CWE-401 (Memory Leak).
* **Fine-Tuned Model**: `VB-MLP_draper` (MLP Dense Head, 499.4 MB).
* **Target Domain**: General-purpose GitHub open-source C/C++ code scanning.

#### 2. **Devign Benchmark (`VB-MLP_devign` & `VB-CNN_devign`)**
* **Dataset Source**: Manually verified security commits from 4 major C projects: **Linux Kernel, QEMU, Wireshark, FFmpeg**.
* **Dataset Size**: 21,854 C functions.
* **Fine-Tuned Models**: `VB-MLP_devign` (499.4 MB) & `VB-CNN_devign` (178.0 MB).
* **Target Domain**: Operating system kernels, virtualization layers, device drivers, and low-level C infrastructure code.

#### 3. **ReVeal Imbalanced Benchmark (`VB-MLP_reveal` & `VB-CNN_reveal`)**
* **Dataset Source**: Extracted from **Chromium browser engine** and **Debian Linux** repositories.
* **Dataset Characteristics**: Reflects realistic enterprise class imbalance where vulnerable functions make up **<10%** of total code functions.
* **Fine-Tuned Models**: `VB-MLP_reveal` (499.4 MB) & `VB-CNN_reveal` (178.0 MB).
* **Target Domain**: High-precision enterprise scanning with ultra-low false positive rates.

#### 4. **VulDeePecker Benchmark (`VB-MLP_vuldeepecker` & `VB-CNN_vuldeepecker`)**
* **Dataset Focus**: Code slices centered around dangerous C standard library API calls (`strcpy`, `strcat`, `sprintf`, `gets`, `memcpy`, `malloc`/`free`).
* **CWE Coverage**: CWE-119 (Buffer Overflow) and CWE-399 (Resource Management).
* **Fine-Tuned Models**: `VB-MLP_vuldeepecker` (499.4 MB) & `VB-CNN_vuldeepecker` (178.0 MB).
* **Target Domain**: Library parameter boundary checking and API misuse detection.

#### 5. **MVD (Multi-Class Vulnerability Dataset) (`VB-MLP_mvd` & `VB-CNN_mvd`)**
* **Dataset Focus**: Categorized code samples across **40 distinct CWE classes** (Format String, Double Free, Use-After-Free, Integer Overflow, Out-of-bounds Read/Write).
* **Fine-Tuned Models**: `VB-MLP_mvd` (499.5 MB) & `VB-CNN_mvd` (178.0 MB).
* **Target Domain**: Granular multi-class vulnerability identification.

#### 6. **IBM D2A False Positive Benchmark (`VB-MLP_d2a`)**
* **Dataset Source**: Curated by **IBM Research** by pairing static analysis warnings (e.g., Infer) with GitHub fix commits across OpenSSL, FFmpeg, and HTTPd.
* **Fine-Tuned Model**: `VB-MLP_d2a` (499.4 MB).
* **Target Domain**: Filtering false positive security alerts produced by traditional static code analyzers in CI/CD build pipelines.

---

## 🎯 Line-Level Attention & Risk Scoring Mechanics (`api_server.py`)

While sequence classification output determines whether an overall C function is vulnerable, security engineers require exact line location attribution. `api_server.py` implements a hybrid line-level risk engine:

1. **Global Max-Risk Score Calculation**:
   $$\text{MaxRisk} = \max_{m \in \text{LoadedModels}} P_m(\text{vulnerable})$$
   $$\text{TopModel} = \arg\max_{m \in \text{LoadedModels}} P_m(\text{vulnerable})$$

2. **Per-Line Risk Attribution Logic**:
   Each line $i$ in the input source code is analyzed for dangerous C memory/string manipulation keywords ($\mathcal{K} = \{\text{strcpy}, \text{gets}, \text{strcat}, \text{free}, \text{malloc}, \text{sprintf}, \text{memcpy}\}$):

   $$\text{LineScore}(i) = \begin{cases} 
   \min\left(98.5, \; \text{MaxRisk} \times 1.05\right) & \text{if } \text{MaxRisk} \ge 50.0\% \text{ and } \text{Line}(i) \cap \mathcal{K} \neq \emptyset \\
   45.0\% & \text{if } \text{MaxRisk} < 50.0\% \text{ and } \text{Line}(i) \cap \mathcal{K} \neq \emptyset \\
   \max\left(2.0, \; \text{MaxRisk} \times 0.08\right) & \text{otherwise}
   \end{cases}$$

---

## 📁 Backend Machine Learning Codebase Structure

```
VulBERTa/
├── api_server.py             # Flask REST API backend server (port 5000)
├── config.py                 # Paths, CUDA device, and dataset configurations
├── custom.py                 # Custom DataCollator for language modeling
├── models.py                 # PyTorch model definitions (VulBERTa_Vanilla & VulBERTa_Extend)
├── predict.py                # Standalone single-model inference script
├── scan_all_models.py        # CLI tool auditing code across all domain models
├── requirements.txt          # Python ML dependencies (torch, transformers, flask, etc.)
├── PROJECT_CONTEXT.md        # Deep learning model & fine-tuning specification
├── data/                     # Dataset storage directory
├── models/                   # Fine-tuned model checkpoints (VB-MLP_*, VB-CNN_*)
├── tokenizer/                # Pre-trained BPE tokenizer files
│   ├── drapgh-vocab.json     # 50k token BPE vocabulary JSON
│   └── drapgh-merges.txt     # BPE subword merges text file
└── utils/                    # Core Python utilities
    ├── cleaner.py            # C/C++ regex code normalization
    ├── metrics.py            # Classification metrics (Accuracy, Precision, Recall, F1)
    ├── model_loader.py       # Model deserialization & safe loader patch
    └── tokenizer_utils.py    # Clang AST pre-tokenizer & Hugging Face BPE wrapper
```

---

## 🚀 Execution & Inference Guide

### 1. Launch Flask REST API Server
```bash
python api_server.py
```
* Pre-loads domain MLP models into RAM memory.
* Serves REST API on `http://localhost:5000/api/scan`.

### 2. Run CLI Multi-Model Security Scan
```bash
python scan_all_models.py
```
* Audits input C code across all domain models and prints ASCII table results directly in terminal.

### 3. Run Single-Model Inference
```bash
python predict.py
```
* Runs targeted vulnerability prediction using a specific checkpoint (`VB-MLP_draper`).
