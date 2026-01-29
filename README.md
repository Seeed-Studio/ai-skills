# Seeed AI Skills

This repository collects and maintains AI skill libraries for Seeed products, providing developers with professional technical guidance and API references.

## 📚 Skills

- **[onnx-to-cvimodel](skills/onnx-to-cvimodel/README.md)** - ONNX to CVIMODEL conversion guide for YOLO models on Sophgo CV181x TPU, with ready-to-use scripts and tested configurations for YOLO11/YOLO26 (detect/pose/seg/cls)

- **[cv181x-media](skills/cv181x-media/README.md)** - Complete multimedia application development guide for reCamera with Sophgo CV181X/CV182X/CV180X chips, covering 15+ core modules including video input/output, encoding/decoding, and audio processing

## 🚀 Installation

### Claude

```bash
# Install all skills
claude skills install git+https://github.com/Seeed-Studio/ai-skills

# Install individual skill
claude skills install git+https://github.com/Seeed-Studio/ai-skills#subdirectory=skills/onnx-to-cvimodel
claude skills install git+https://github.com/Seeed-Studio/ai-skills#subdirectory=skills/cv181x-media
```

### Codex

```bash
# Install all skills
codex skills install git+https://github.com/Seeed-Studio/ai-skills

# Install individual skill
codex skills install git+https://github.com/Seeed-Studio/ai-skills#subdirectory=skills/onnx-to-cvimodel
codex skills install git+https://github.com/Seeed-Studio/ai-skills#subdirectory=skills/cv181x-media
```

## 📖 How to Use

Once installed, you can ask your AI assistant directly:

**Model Conversion:**
- "Help me convert YOLO11n to CVIMODEL format"
- "What output names do I need for YOLO11 detection?"
- "How to use qtable for pose model conversion?"

**Multimedia Development:**
- "How to configure VI module to capture 1080p video?"
- "Show me how to add timestamp OSD to video stream"
- "How to correct barrel distortion from wide-angle lens?"

The AI assistant will automatically invoke the relevant skills to provide professional technical guidance.

## 🤝 Contributing

Contributions of new skills or improvements to existing skills are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📄 License

This repository is licensed under the [MIT License](LICENSE).
