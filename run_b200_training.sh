#!/bin/bash
# run_b200_training.sh
# One-click execution script for VulBERTa_Extend Unified Training on NVIDIA B200

set -e

WORKSPACE_DIR="$HOME/VulBERTa"

echo "=================================================================="
echo " 🚀 VULBERTA_EXTEND B200 CLUSTER LAUNCHER (CodeSentinel-AI)"
echo "=================================================================="
echo " Target GPU : GPU 7 (B200)"
echo " Workspace  : $WORKSPACE_DIR"
echo "=================================================================="

mkdir -p "$WORKSPACE_DIR"
cd "$WORKSPACE_DIR"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment 'venv'..."
    python3 -m venv venv
fi

source venv/bin/activate

echo ""
echo "Starting Unified Fine-Tuning..."
CUDA_VISIBLE_DEVICES=GPU-afc82ce1-fb80-2c9e-66c4-510afe22d38a python3 finetune_unified.py \
    --data_file data/merged/merged_deduped.jsonl \
    --output_dir models/VulBERTa_Unified \
    --batch_size 256 \
    --epochs 5 \
    --backbone_lr 3.2e-4 \
    --head_lr 1.6e-3 \
    --mixed_precision bf16 \
    --num_workers 0

echo "=================================================================="
echo " ✅ TRAINING COMPLETED SUCCESSFULLY!"
echo " Checkpoint saved to: models/VulBERTa_Unified/best_model"
echo " Summary saved to:    models/VulBERTa_Unified/training_summary.json"
echo "=================================================================="
