#!/bin/bash
# Quick conversion for YOLO11 Detection
./convert_to_cvimodel.sh "$1" "$2" \
    MODEL_TYPE=yolo11 \
    TASK=detect \
    MODEL_SIZE=n \
    CHIP=cv181x \
    CALIBRATION_EPOCHS=100
