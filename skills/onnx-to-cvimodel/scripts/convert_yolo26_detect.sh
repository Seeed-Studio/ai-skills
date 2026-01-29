#!/bin/bash
# Quick conversion for YOLO26 Detection
./convert_to_cvimodel.sh "$1" "$2" \
    MODEL_TYPE=yolo26 \
    TASK=detect \
    MODEL_SIZE=n \
    CHIP=cv181x \
    CALIBRATION_EPOCHS=100
