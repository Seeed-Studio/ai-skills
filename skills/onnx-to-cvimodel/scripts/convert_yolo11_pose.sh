#!/bin/bash
# Quick conversion for YOLO11 Pose
./convert_to_cvimodel.sh "$1" "$2" \
    MODEL_TYPE=yolo11 \
    TASK=pose \
    MODEL_SIZE=n \
    CHIP=cv181x \
    CALIBRATION_EPOCHS=100
