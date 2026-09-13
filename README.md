# CodeSentinel-AI: Deep Learning Vulnerability Scanner & Fumadocs Studio

![CodeSentinel Architecture](VB.png)

CodeSentinel-AI is a deep learning-based source code vulnerability detection platform powered by pre-trained RoBERTa representations and fine-tuned classifiers (MLP and 1D-CNN) trained across real-world open-source C/C++ projects and benchmark security datasets.

## 🌟 Key Features
- **Fumadocs Frontend Studio UI**: Modern dark velvet interface styled with Fumadocs design system, code editor, sample presets, and line risk heatmaps.
- **Max-Risk Multi-Model Audit**: Evaluates C/C++ code functions across 5 fine-tuned domain models (`VB-MLP_draper`, `VB-MLP_devign`, `VB-MLP_reveal`, `VB-MLP_vuldeepecker`, `VB-MLP_d2a`) to catch worst-case security risks.
- **REST API Backend**: Flask REST API server (`api_server.py`) serving live model predictions and line-level attention scores.

## 🚀 Quickstart

### 1. Start Backend REST API
```bash
python api_server.py
```
Serves scanning API on `http://localhost:5000/api/scan`.

### 2. Start Fumadocs Frontend Studio
```bash
cd frontend
npm install
npm run dev
```
Launches interactive Vulnerability Studio on `http://localhost:5173/`.
