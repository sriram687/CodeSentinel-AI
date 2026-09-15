# CodeSentinel-AI: Deep Learning Vulnerability Scanner & Fumadocs Studio

## 📌 Executive Summary
**CodeSentinel-AI** (built on the VulBERTa framework) is a deep learning security platform for detecting source code vulnerabilities in C/C++ applications. It leverages pre-trained RoBERTa transformer representations fine-tuned with custom Multi-Layer Perceptron (MLP) and 1D-Convolutional Neural Network (CNN) classification heads across 6 domain-specific security datasets.

The system includes:
1. **Flask REST API Backend (`api_server.py`)** with live multi-model inference and line-level risk highlighted focus score computation.
2. **Fumadocs Frontend Studio (`frontend/`)** built with React, Vite, and custom CSS featuring a dark velvet / alabaster theme system, code editor, line heatmaps, multi-model comparison matrix, 10-model catalog explorer, and developer documentation.
3. **CLI Security Scanner (`scan_all_models.py`)** for running terminal-based max-risk vulnerability audits.

---

## 🏗️ Architectural Overview & Component Pipeline

```
[ C/C++ Code Input ]
        │
        ▼
[ Cleaner & Preprocessor (utils/cleaner.py) ]
        │
        ▼
[ Custom C/C++ BPE Tokenizer (tokenizer/drapgh-*) ]
        │
        ▼
[ Pre-trained RoBERTa Model Backbone ]
        │
┌───────┴────────────────────────┐
▼                                ▼
[ VulBERTa_Vanilla Head ]   [ VulBERTa_Extend Head ]
(Tanh + Dense 768->768->2)   (ReLU + Dense 768->512->256->2)
        │                                │
        └────────────────┬───────────────┘
                         ▼
        [ Multi-Model Domain Ensemble ]
   - VB-MLP_draper (General GitHub C/C++)
   - VB-MLP_devign (Linux Kernel / QEMU)
   - VB-MLP_reveal (Chromium / Debian)
   - VB-MLP_vuldeepecker (C API Misuse)
   - VB-MLP_d2a (IBM Static Analysis Filter)
                         │
                         ▼
        [ Line-Level Risk Attention Engine ]
                         │
                         ▼
   [ Flask REST API / Fumadocs Studio UI ]
```

---

## 🧠 Machine Learning Models, Training Methodology & Datasets

### 1. Base Pre-training Methodology (VulBERTa Pre-training)
* **Pre-training Corpus**: Trained on a dataset of **1,200,000+ C/C++ functions** collected from open-source GitHub repositories and real-world security benchmarks.
* **Tokenizer Customization**: Uses a custom **Byte-Level BPE (Byte-Pair Encoding)** tokenizer (`tokenizer/drapgh-vocab.json`, `tokenizer/drapgh-merges.txt`) with a 50,000 vocabulary size designed specifically for C/C++ source code grammar, reserved keywords (`if`, `while`, `struct`, `sizeof`), memory management primitives (`malloc`, `free`, `realloc`), pointer declarations (`*`, `&`, `->`), and standard library calls.
* **Pre-training Task**: **Masked Language Modeling (MLM)** with 15% token masking probability. The model learns syntax rules, control flow dependencies, variable scope, pointer arithmetic, and contextual relationships between functions.

---

### 2. Fine-Tuning Architectures & Classifier Heads
CodeSentinel-AI supports two primary fine-tuning classifier head architectures attached to the RoBERTa encoder backbone:

#### A. **VulBERTa-MLP (Multi-Layer Perceptron Sequence Classifier)**
* **Architecture**: Extract pooler sequence embedding (`[CLS]` representation of length 768) from the RoBERTa transformer and feed it into multi-stage non-linear dense layers.
  * **`VulBERTa_Vanilla`**: `[CLS]` -> Dropout(0.1) -> Linear(768, 768) -> Tanh -> Dropout(0.1) -> Linear(768, 2)
  * **`VulBERTa_Extend`**: `[CLS]` -> Dropout(0.1) -> Linear(768, 512) -> ReLU -> Dropout(0.1) -> Linear(512, 256) -> ReLU -> Linear(256, 2)
* **Target & Usage**: Global function-level semantic understanding. Best for deep evaluation of full C functions.
* **Disk Model Checkpoint Size**: ~499.4 MB per checkpoint.

#### B. **VulBERTa-CNN (1D-Convolutional Neural Network Scanner)**
* **Architecture**: Passes full token embedding sequence representations output by RoBERTa through 1D convolutional filter maps with multiple kernel sizes to capture local sliding n-gram code patterns.
* **Target & Usage**: Fast local pattern extraction focused on dangerous API call sequences, boundary checks, and pointer offset operations.
* **Disk Model Checkpoint Size**: ~178.0 MB per checkpoint.

---

### 3. Detailed Dataset Breakdown & Model Training Matrix

| Model Checkpoint | Classifier Arch | Training Dataset | Primary Focus & Domain | Dataset Characteristics & Vulnerability Coverage |
|---|---|---|---|---|
| **`VB-MLP_draper`** | MLP Dense | **Draper VDIS** | General C/C++ GitHub Benchmark | **1.2M+ C/C++ functions** collected by Draper Laboratory from open-source GitHub C projects. Focuses on broad vulnerability types including buffer overflows, NULL pointer dereferences, resource leaks, and array indexing errors. Serves as the primary general-purpose model. |
| **`VB-MLP_devign`** | MLP Dense | **Devign** | OS Kernel & Virtualization (Linux / QEMU) | Curated from security commits across 4 major C projects: **Linux Kernel, QEMU, Wireshark, and FFmpeg**. Targets low-level OS kernel bugs, concurrency flaws, memory corruption, driver vulnerabilities, and virtualization security breaches. |
| **`VB-CNN_devign`** | 1D-CNN | **Devign** | High-speed Linux Kernel Scan | 1D-CNN fast sliding-window variant trained on the Devign OS kernel dataset. |
| **`VB-MLP_reveal`** | MLP Dense | **ReVeal** | Imbalanced Chromium & Debian Codebases | Designed to address realistic class imbalance in software security. Derived from **Chromium browser** and **Debian Linux** security patches, where vulnerable functions constitute <10% of total code. Minimizes false positive alerts in production. |
| **`VB-CNN_reveal`** | 1D-CNN | **ReVeal** | High-speed Chromium/Debian Scan | 1D-CNN fast sliding-window variant trained on the ReVeal imbalanced browser dataset. |
| **`VB-MLP_vuldeepecker`** | MLP Dense | **VulDeePecker** | C API Misuse & Buffer Violations | Based on explicit code gadgets focusing on **CWE-119 (Buffer Overflow/Error)** and **CWE-399 (Resource Management/Memory Leak)**. Trained on parameter boundary violations and unsafe standard library calls (`strcpy`, `strcat`, `sprintf`, `gets`, `memcpy`). |
| **`VB-CNN_vuldeepecker`**| 1D-CNN | **VulDeePecker** | High-speed C API Violation Scan | 1D-CNN fast sliding-window variant trained on VulDeePecker library API misuse gadgets. |
| **`VB-MLP_mvd`** | MLP Dense | **MVD (Multi-Class)** | Multi-Class Vulnerability Classification | Trained across **40 distinct CWE vulnerability classes** (e.g., Out-of-bounds Read/Write, Format String, Double Free, Use-After-Free, Integer Overflow). Provides granular multi-class vulnerability scoring. |
| **`VB-CNN_mvd`** | 1D-CNN | **MVD (Multi-Class)** | High-speed Multi-Class Scan | 1D-CNN fast sliding-window variant trained on the 40 CWE class MVD dataset. |
| **`VB-MLP_d2a`** | MLP Dense | **D2A (IBM Benchmark)**| IBM Static Analysis False Positive Filter | Created by **IBM Research** by pairing static analysis reports (e.g., Infer) with GitHub fix commits across OpenSSL, FFmpeg, and HTTPd. Trained to **filter out false positives** generated by traditional static code analyzers. |

---

## 🛠️ Full Details of Work Completed

### 1. Backend & Machine Learning Pipeline (`Python / PyTorch / Transformers`)
* **Custom Tokenization**:
  * Integrated byte-pair encoding (BPE) tokenizers (`drapgh-vocab.json`, `drapgh-merges.txt`) trained specifically on C/C++ syntax constructs.
  * Tokenizer utility handles code normalization and tensor formatting (`utils/tokenizer_utils.py`).
* **Deep Learning Model Architectures (`models.py`)**:
  * Implemented `VulBERTa_Vanilla` head: RoBERTa pooler representation followed by Dense(768, 768) + Tanh activation and Dropout (0.1).
  * Implemented `VulBERTa_Extend` head: Multi-stage non-linear projection using Dense(768, 512) -> ReLU -> Dropout(0.1) -> Linear(512, 256) -> ReLU -> Linear(256, 2).
* **Model Checkpoints**:
  * Configured support for 10 distinct fine-tuned models across 6 security datasets (`Draper`, `Devign`, `MVD`, `Reveal`, `VulDeePecker`, `D2A`).
  * Managed model loader (`utils/model_loader.py`) supporting dynamic architecture detection and tensor loading on CUDA/CPU.
* **REST API Server (`api_server.py`)**:
  * Built Flask server with CORS support.
  * Pre-loads domain MLP models into RAM for sub-second scanning speed.
  * Endpoints created:
    * `GET /api/health` - Server status & list of active models.
    * `GET /api/models` - Model metadata and domain descriptions.
    * `POST /api/scan` - Performs multi-model code audit and returns per-model confidence, overall status (`VULNERABLE` vs `SAFE`), max-risk score, and line-level heatmap scores.
  * Windows compatibility fixes: Automated `libclang.dll` path resolution and patched Transformers `torch.load` security checks for PyTorch compatibility.

### 2. Frontend Studio & Fumadocs UI (`React / Vite / CSS`)
* **Design System**:
  * Styled with a Fumadocs-inspired dark velvet aesthetic (`#0b0d13` base background with `#6366f1` accent colors) and theme switcher to light alabaster print mode (`index.css`).
  * Responsive layout with sidebar navigation, top control bar, and card grid views.
* **Code Editor & Sample Presets**:
  * Integrated line-numbered code textarea.
  * Built preset code templates:
    1. *Buffer Overflow (Unbounded Copy)* - `strcpy` misuse.
    2. *Null Pointer Dereference* - Unchecked pointer access.
    3. *Use-After-Free Memory Bug* - Access after `free()`.
    4. *Safe Bounded Copy* - `strncpy` non-vulnerable baseline.
* **Multi-Model Risk Audit Dashboard**:
  * Dynamic Verdict Banner displaying overall classification and max risk score.
  * **Line-Level Heatmap**: Highlights specific lines containing risky C function patterns and high risk attention scores.
  * **Multi-Model Breakdown Table**: Displays risk score percentages across all loaded domain models.
  * **One-Click Audit Report Exporter**: Copy clean audit markdown summary to clipboard.
* **Model Catalog Explorer**:
  * Visual cards detailing model architectures (MLP vs 1D-CNN), checkpoint disk sizes (~500MB vs ~178MB), and domain focus descriptions.
* **API Documentation View**:
  * Embedded developer documentation guide with ready-to-use `curl` commands and Python `requests` integration code snippets.

### 3. CLI Terminal Scanner (`scan_all_models.py`)
* Created standalone command-line script to audit C/C++ code directly in terminal windows, displaying formatted ASCII table outputs with domain scores and max-risk classification.

---

## 📁 Repository Structure Overview

```
VulBERTa/
├── api_server.py             # Flask REST API backend server (port 5000)
├── config.py                 # Paths, device, and dataset configurations
├── custom.py                 # Custom DataCollator for language modeling
├── models.py                 # PyTorch VulBERTa classification heads
├── predict.py                # Standalone prediction script for single model
├── scan_all_models.py        # CLI script for auditing code across all domain models
├── requirements.txt          # Python dependencies (torch, transformers, flask, etc.)
├── README.md                 # Documentation overview
├── PROJECT_CONTEXT.md        # Comprehensive project context & implementation record
├── data/                     # Dataset storage directory
├── models/                   # Fine-tuned model checkpoint folders (VB-MLP_*, VB-CNN_*)
│   ├── VB-MLP_draper/
│   ├── VB-MLP_devign/
│   ├── VB-MLP_reveal/
│   ├── VB-MLP_vuldeepecker/
│   ├── VB-MLP_d2a/
│   └── ...
├── tokenizer/                # Pre-trained BPE tokenizer files
│   ├── drapgh-vocab.json
│   └── drapgh-merges.txt
├── utils/                    # Core Python utilities
│   ├── cleaner.py            # Code preprocessing cleaner
│   ├── metrics.py            # Evaluation metrics (F1, Precision, Recall, AUC)
│   ├── model_loader.py       # Model state deserializer and initializer
│   └── tokenizer_utils.py    # Byte-pair encoder loader
└── frontend/                 # Fumadocs React Frontend Application
    ├── package.json          # Node dependencies (vite, lucide-react, react)
    ├── vite.config.js        # Vite dev server configuration
    ├── index.html            # Application entry HTML
    └── src/
        ├── main.jsx          # React app entry point
        ├── App.jsx           # Main studio dashboard, editor, catalog & docs
        ├── index.css         # Fumadocs dark velvet & alabaster design system
        └── components/       # UI Subcomponents (Editor, Heatmap, Tables)
```

---

## 🚀 How to Run the Application

### 1. Launch Python Backend REST API
```bash
python api_server.py
```
* Serves live API on `http://localhost:5000`.

### 2. Launch Fumadocs Frontend UI Studio
```bash
cd frontend
npm run dev
```
* Opens interactive studio UI on `http://localhost:5173`.

### 3. Run CLI Multi-Model Scan
```bash
python scan_all_models.py
```
