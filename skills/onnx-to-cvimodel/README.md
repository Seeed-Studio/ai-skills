# ONNX to CVIMODEL Conversion Skill

> **Maintained by**: [LynnL4](https://github.com/LynnL4)
> **License**: MIT

Expert guidance skill for converting YOLO models (YOLO11/YOLO26) from ONNX to CVIMODEL format for Sophgo CV181x TPU platforms (reCamera, SG200x).

## Overview

This skill provides practical scripts and tested configurations for:
- YOLO11: detection, pose, segmentation, classification
- YOLO26: detection, classification
- Hybrid quantization with qtable support
- Ready-to-use conversion scripts

## Version

Current Version: **v1.0.0**

## What's Supported

| Model | Detection | Pose | Segmentation | Classification |
|-------|-----------|------|--------------|----------------|
| YOLO11 | ✅ | ✅ | ✅ | ✅ |
| YOLO26 | ✅ | ❌ | ❌ | ✅ |

> **Note**: YOLO26 pose/seg are NOT supported (uses Mod operation not in TPU-MLIR)

## Structure

```
onnx-to-cvimodel/
├── SKILL.md              # Main skill definition
├── LICENSE.txt           # MIT License
├── README.md             # This file
├── .skillrc              # Skill configuration
├── scripts/              # Conversion scripts
│   ├── convert_to_cvimodel.sh      # Universal conversion script
│   ├── batch_convert_all.sh        # Batch conversion
│   ├── convert_yolo11_detect.sh    # YOLO11 detection
│   ├── convert_yolo11_pose.sh      # YOLO11 pose
│   ├── convert_yolo11_seg.sh       # YOLO11 segmentation
│   ├── convert_yolo11_cls.sh       # YOLO11 classification
│   ├── convert_yolo26_detect.sh    # YOLO26 detection
│   └── convert_yolo26_cls.sh       # YOLO26 classification
└── assets/               # Quantization tables
    ├── yolo11n_pose_qtable         # Pose hybrid quantization
    └── yolo11n_seg                 # Segmentation hybrid quantization
```

## Quick Start

### 1. Export YOLO to ONNX

```python
from ultralytics import YOLO

# Detection
YOLO('yolo11n.pt').export(format='onnx', imgsz=640, simplify=False, opset=12)

# Pose
YOLO('yolo11n-pose.pt').export(format='onnx', imgsz=640, simplify=False, opset=12)

# Segmentation
YOLO('yolo11n-seg.pt').export(format='onnx', imgsz=640, simplify=False, opset=12)
```

### 2. Convert to CVIMODEL

```bash
# Universal conversion
./scripts/convert_to_cvimodel.sh model.onnx dataset/

# Task-specific conversion
MODEL_TYPE=yolo11 TASK=pose ./scripts/convert_to_cvimodel.sh yolo11n-pose.onnx dataset/
```

### 3. Use Q-table for Better Accuracy

```bash
# Copy qtable from skill assets
cp ~/.claude/skills/skills/onnx-to-cvimodel/assets/yolo11n_pose_qtable ./
cp ~/.claude/skills/skills/onnx-to-cvimodel/assets/yolo11n_seg ./
```

## Tested Conversions

| Model | ONNX Size | CVIMODEL Size | Command |
|-------|-----------|---------------|---------|
| YOLO11n detect | 10.7 MB | 3.0 MB | `./scripts/convert_yolo11_detect.sh yolo11n.onnx dataset/` |
| YOLO11n pose | 11.3 MB | 3.6 MB | `./scripts/convert_yolo11_pose.sh yolo11n-pose.onnx dataset/` |
| YOLO11n seg | 11.7 MB | 4.0 MB | `./scripts/convert_yolo11_seg.sh yolo11n-seg.onnx dataset/` |
| YOLO11n cls | 10.8 MB | 3.0 MB | `./scripts/convert_yolo11_cls.sh yolo11n-cls.onnx dataset/` |
| YOLO26n detect | 9.4 MB | 2.9 MB | `./scripts/convert_yolo26_detect.sh yolo26n.onnx dataset/` |
| YOLO26n cls | 11.3 MB | 3.0 MB | `./scripts/convert_yolo26_cls.sh yolo26n-cls.onnx dataset/` |

## Requirements

- Docker with `sophgo/tpuc_dev:v3.1` image
- Calibration images (100+ recommended for production)
- ONNX model file

## Common Issues

### "Op not support: Mod"
**Problem**: YOLO26 pose/seg uses Mod operation
**Solution**: Use YOLO11 instead

### "model_transform: command not found"
**Solution**: `source /workspace/tpu-mlir/envsetup.sh && ./build.sh`

### Wrong output order
**Solution**: For detection, outputs MUST be alternating (Box, Class, Box, Class...)

## Contributing

To improve this skill:

1. Test conversions with new models
2. Report issues or provide feedback
3. Submit pull requests

## License

This skill is licensed under the [MIT License](LICENSE.txt).

## Acknowledgments

- Based on TPU-MLIR by Sophgo
- Original conversion scripts and qtables from Seeed Studio
