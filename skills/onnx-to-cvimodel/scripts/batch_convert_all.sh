#!/bin/bash
# Batch Conversion Script - Convert all YOLO models to CVIMODEL
# =============================================================

set -e

GREEN='\033[0;32m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

# Configuration
WORKSPACE_ROOT="./batch_workspace"
DATASET_DIR="./dataset"
MODEL_SIZE="n"
CHIP="cv181x"
CALIB_EPOCHS=20

# Create dataset directory
mkdir -p "$DATASET_DIR"

# Add calibration images if dataset is empty
if [[ $(ls -A "$DATASET_DIR" 2>/dev/null | wc -l) -eq 0 ]]; then
    log_info "Dataset is empty. Please add calibration images to $DATASET_DIR"
    log_info "You can copy images from your COCO2017 folder:"
    echo "  cp /path/to/COCO2017/*.jpg $DATASET_DIR/"
    exit 1
fi

log_info "Using dataset: $DATASET_DIR ($(ls "$DATASET_DIR" | wc -l) images)"

# List of models to convert
MODELS=(
    # YOLO11 models
    "yolo11n.onnx:yolo11:detect"
    "yolo11n-cls.onnx:yolo11:cls"
    "yolo11n-pose.onnx:yolo11:pose"
    "yolo11n-seg.onnx:yolo11:seg"

    # YOLO26 models
    "yolo26n.onnx:yolo26:detect"
    "yolo26n-cls.onnx:yolo26:cls"
)

# Count total models
TOTAL=${#MODELS[@]}
CURRENT=0

for model_config in "${MODELS[@]}"; do
    IFS=':' read -r onnx_file model_type task <<< "$model_config"

    if [[ ! -f "$onnx_file" ]]; then
        log_warn "Skipping $onnx_file (not found)"
        continue
    fi

    CURRENT=$((CURRENT + 1))
    log_info "=========================================="
    log_info "Converting [$CURRENT/$TOTAL]: $onnx_file"
    log_info "=========================================="

    MODEL_TYPE="$model_type" TASK="$task" MODEL_SIZE="$MODEL_SIZE" \
        CHIP="$CHIP" CALIBRATION_EPOCHS="$CALIB_EPOCHS" \
        WORK_DIR="$WORKSPACE_ROOT" \
        ./convert_to_cvimodel.sh "$onnx_file" "$DATASET_DIR"

    if [[ $? -eq 0 ]]; then
        log_info "✅ $onnx_file conversion completed"
    else
        log_info "❌ $onnx_file conversion failed"
    fi
    echo ""
done

log_info "=========================================="
log_info "Batch conversion complete!"
log_info "=========================================="
log_info "Check current directory for .cvimodel files"
ls -lh *.cvimodel 2>/dev/null || log_info "No cvimodel files found"
