#!/bin/bash
# Universal ONNX to CVIMODEL Conversion Script
# ===========================================
# Supports: YOLO11/YOLO26 Detection, Pose, Segmentation, Classification
# Target: Sophgo CV181x TPU (reCamera, SG200x)

set -e

# Default values
MODEL_TYPE="${MODEL_TYPE:-yolo11}"        # yolo11 or yolo26
TASK="${TASK:-detect}"                     # detect, pose, seg, cls
MODEL_SIZE="${MODEL_SIZE:-n}"             # n, s, m, l, x
CHIP="${CHIP:-cv181x}"
CALIBRATION_EPOCHS="${CALIBRATION_EPOCHS:-100}"
WORK_DIR="${WORK_DIR:-./work_dir}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check dependencies
check_dependencies() {
    log_info "Checking dependencies..."

    if ! command -v docker &> /dev/null; then
        log_error "Docker not found. Please install Docker first."
        exit 1
    fi

    if ! docker images sophgo/tpuc_dev:v3.1 | grep -q sophgo; then
        log_info "Pulling TPU-MLIR Docker image..."
        docker pull sophgo/tpuc_dev:v3.1
    fi
}

# Get model name
get_model_name() {
    local model_type="$1"
    local task="$2"
    local size="$3"

    if [[ "$task" == "cls" ]]; then
        echo "${model_type}${size}-cls"
    else
        echo "${model_type}${size}-${task}"
    fi
}

# Get input size
get_input_size() {
    local task="$1"
    if [[ "$task" == "cls" ]]; then
        echo "224"
    else
        echo "640"
    fi
}

# Get output names based on model type and task
get_output_names() {
    local model_type="$1"
    local task="$2"

    case "$task" in
        detect)
            if [[ "$model_type" == "yolo26" ]]; then
                echo "/model.23/one2one_cv2.0/one2one_cv2.0.2/Conv_output_0,/model.23/one2one_cv3.0/one2one_cv3.0.2/Conv_output_0,/model.23/one2one_cv2.1/one2one_cv2.1.2/Conv_output_0,/model.23/one2one_cv3.1/one2one_cv3.1.2/Conv_output_0,/model.23/one2one_cv2.2/one2one_cv2.2.2/Conv_output_0,/model.23/one2one_cv3.2/one2one_cv3.2.2/Conv_output_0"
            else
                echo "/model.23/cv2.0/cv2.0.2/Conv_output_0,/model.23/cv3.0/cv3.0.2/Conv_output_0,/model.23/cv2.1/cv2.1.2/Conv_output_0,/model.23/cv3.1/cv3.1.2/Conv_output_0,/model.23/cv2.2/cv2.2.2/Conv_output_0,/model.23/cv3.2/cv3.2.2/Conv_output_0"
            fi
            ;;
        seg)
            echo "output0,output1"
            ;;
        pose|cls)
            echo "output0"
            ;;
        *)
            log_error "Unknown task: $task"
            exit 1
            ;;
    esac
}

# Check if model is supported
check_model_support() {
    local model_type="$1"
    local task="$2"

    if [[ "$model_type" == "yolo26" ]] && [[ "$task" == "pose" || "$task" == "seg" ]]; then
        log_error "YOLO26 $task is NOT supported by TPU-MLIR (uses Mod operation)"
        log_error "Please use YOLO11 instead for $task tasks"
        exit 1
    fi
}

# Main conversion function
convert_model() {
    local onnx_file="$1"
    local dataset_dir="$2"

    if [[ ! -f "$onnx_file" ]]; then
        log_error "ONNX file not found: $onnx_file"
        exit 1
    fi

    if [[ ! -d "$dataset_dir" ]]; then
        log_error "Dataset directory not found: $dataset_dir"
        exit 1
    fi

    check_model_support "$MODEL_TYPE" "$TASK"

    local model_name=$(get_model_name "$MODEL_TYPE" "$TASK" "$MODEL_SIZE")
    local input_size=$(get_input_size "$TASK")
    local output_names=$(get_output_names "$MODEL_TYPE" "$TASK")

    log_info "Converting: $model_name"
    log_info "Input size: ${input_size}x${input_size}"
    log_info "Task: $TASK"
    log_info "Chip: $CHIP"
    log_info "Dataset: $dataset_dir"

    # Create workspace
    mkdir -p "$WORK_DIR"
    local workspace="$WORK_DIR/$model_name"
    mkdir -p "$workspace"

    # Prepare directories
    cp "$onnx_file" "$workspace/"
    local onnx_basename=$(basename "$onnx_file")

    # Check for qtable
    local use_qtable=false
    local qtable_path=""

    if [[ "$TASK" == "pose" ]] && [[ "$MODEL_TYPE" == "yolo11" ]]; then
        if [[ -f "yolo11n_pose_qtable" ]]; then
            use_qtable=true
            qtable_path="$workspace/yolo11n_pose_qtable"
            cp yolo11n_pose_qtable "$workspace/"
            log_info "Using qtable for pose (hybrid quantization)"
        fi
    elif [[ "$TASK" == "seg" ]] && [[ "$MODEL_TYPE" == "yolo11" ]]; then
        if [[ -f "yolo11n_seg" ]]; then
            use_qtable=true
            qtable_path="$workspace/yolo11n_seg"
            cp yolo11n_seg "$workspace/"
            log_info "Using qtable for segmentation (hybrid quantization)"
        fi
    fi

    # Run conversion in Docker
    log_info "Starting Docker conversion..."

    docker run --privileged --rm --name "${model_name}_convert" \
        -v "$(pwd)/$WORK_DIR:/work" \
        -w "/work/$model_name" \
        sophgo/tpuc_dev:v3.1 bash -c "
        source /workspace/tpu-mlir/envsetup.sh

        echo '=== Step 1: Model Transform ==='
        mkdir -p workspace && cd workspace
        cp ../$onnx_basename .
        $use_qtable && cp ../$(basename $qtable_path) . || true

        model_transform.py \\
            --model_name $model_name \\
            --model_def $onnx_basename \\
            --input_shapes '[[1,3,$input_size,$input_size]]' \\
            --mean '0.0,0.0,0.0' \\
            --scale '0.0039216,0.0039216,0.0039216' \\
            --keep_aspect_ratio \\
            --pixel_format rgb \\
            --output_names '$output_names' \\
            --test_input /tmp/test.jpg \\
            --test_result ${model_name}_top_outputs.npz \\
            --mlir ${model_name}.mlir

        echo '=== Step 2: Calibration ==='
        run_calibration.py ${model_name}.mlir \\
            --dataset /work/dataset \\
            --input_num $CALIBRATION_EPOCHS \\
            -o ${model_name}_calib_table

        echo '=== Step 3: Deploy ==='
        local deploy_args='--mlir ${model_name}.mlir --quantize INT8 --quant_input --processor $CHIP --calibration_table ${model_name}_calib_table --test_input /tmp/test.jpg --test_reference ${model_name}_top_outputs.npz --customization_format RGB_PACKED --fuse_preprocess --aligned_input'

        if $use_qtable; then
            model_deploy.py \$deploy_args \\
                --quantize_table $(basename $qtable_path) \\
                --model ${model_name}_${CHIP}_mix.cvimodel
        else
            model_deploy.py \$deploy_args \\
                --model ${model_name}_${CHIP}_int8.cvimodel
        fi

        ls -la *.cvimodel
        "

    # Copy result to current directory
    local cvimodel_file=$(find "$workspace" -name "*.cvimodel" | head -1)
    if [[ -n "$cvimodel_file" ]]; then
        cp "$cvimodel_file" ./
        log_info "CVIMODEL created: $(basename "$cvimodel_file")"
    fi
}

# Print usage
print_usage() {
    cat << EOF
Universal ONNX to CVIMODEL Conversion Script
===========================================

Usage:
    $0 <onnx_file> <dataset_dir> [options]

Arguments:
    onnx_file       Path to ONNX model file
    dataset_dir     Path to calibration images directory

Options:
    MODEL_TYPE      yolo11 or yolo26 (default: yolo11)
    TASK            detect, pose, seg, cls (default: detect)
    MODEL_SIZE      n, s, m, l, x (default: n)
    CHIP            cv181x, cv183x, cv186x (default: cv181x)
    CALIBRATION_EPOCHS  Number of calibration images (default: 100)
    WORK_DIR        Working directory (default: ./work_dir)

Examples:
    # YOLO11n detection
    MODEL_TYPE=yolo11 TASK=detect $0 yolo11n.onnx ./dataset

    # YOLO11n pose (with qtable)
    MODEL_TYPE=yolo11 TASK=pose $0 yolo11n-pose.onnx ./dataset

    # YOLO11n segmentation
    MODEL_TYPE=yolo11 TASK=seg $0 yolo11n-seg.onnx ./dataset

    # YOLO11n classification
    MODEL_TYPE=yolo11 TASK=cls $0 yolo11n-cls.onnx ./dataset

    # YOLO26n detection
    MODEL_TYPE=yolo26 TASK=detect $0 yolo26n.onnx ./dataset

    # YOLO26n classification
    MODEL_TYPE=yolo26 TASK=cls $0 yolo26n-cls.onnx ./dataset

Supported Models:
    YOLO11:  detect ✅, pose ✅, seg ✅, cls ✅
    YOLO26:  detect ✅, pose ❌, seg ❌, cls ✅

Note: YOLO26 pose/seg are NOT supported (Mod operation not in TPU-MLIR)

EOF
}

# Main
main() {
    if [[ $# -lt 2 ]]; then
        print_usage
        exit 1
    fi

    local onnx_file="$1"
    local dataset_dir="$2"

    check_dependencies
    convert_model "$onnx_file" "$dataset_dir"
}

main "$@"
