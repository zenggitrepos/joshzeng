#!/bin/bash
# ============================================================
#  Training Launcher Script
#  Usage: bash run_train.sh [optional custom notes]
# ============================================================

# ---- Configurable core parameters ----

# WEIGHT_MODULE1=0.5
# WEIGHT_MODULE2=0.2
# WEIGHT_MODULE1=1.5
# WEIGHT_MODULE2=1.0

# NUM_EPOCHS=50
# BATCH_SIZE=32 # (16 if VRAM tight)
# LR=3e-4
# WEIGHT_DECAY=1e-4

WEIGHT_MODULE1=0.6
WEIGHT_MODULE2=0.4

NUM_EPOCHS=80
BATCH_SIZE=16
LR=5e-4
WEIGHT_DECAY=3e-4

# ---- Paths & experiment naming ----
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
EXP_NAME="affinity_exp_${TIMESTAMP}"

# Create output directories
mkdir -p logs checkpoints

OUTFILE="logs/${EXP_NAME}.log"
SAVE_PREFIX="checkpoints/${EXP_NAME}"


python train_v2.py \
    --weight-module1 ${WEIGHT_MODULE1} \
    --weight-module2 ${WEIGHT_MODULE2} \
    --num-epochs ${NUM_EPOCHS} \
    --batch-size ${BATCH_SIZE} \
    --lr ${LR} \
    --weight-decay ${WEIGHT_DECAY} \
    --outfile ${OUTFILE} \
    --save-prefix ${SAVE_PREFIX} \
    --seed 48 \
    --device 0 


# ---- Done ----
echo ">>> Training complete: ${EXP_NAME}"
echo ">>> Logs saved to: ${OUTFILE}"
echo ">>> Checkpoints in: checkpoints/"

