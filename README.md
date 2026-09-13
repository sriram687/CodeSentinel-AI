# CodeSentinel-AI: Deep Learning Source Code Vulnerability Scanner

![CodeSentinel Architecture](VB.png)

CodeSentinel-AI is a deep learning-based vulnerability detection system powered by pre-trained RoBERTa representations and fine-tuned classifiers (MLP and 1D-CNN) trained across real-world open-source C/C++ projects and benchmark datasets.

## Key Features
- **C-AST Tokenization**: Integrates `libclang` to parse C/C++ Abstract Syntax Trees before Byte-Level BPE tokenization.
- **Multi-Domain Intelligence**: Evaluated across 6 benchmark security datasets (Draper, Devign, ReVeAL, MVD, VulDeePecker, D2A).
- **Max-Risk Security Scanner**: Runs unknown source code functions across all fine-tuned models to flag worst-case security risks.
