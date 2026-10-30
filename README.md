# Seeed AI Skills

This repository collects and maintains AI skill libraries for Seeed products, providing developers with professional technical guidance and API references.

## 📚 Skills

- **[ee-datasheet-master](skills/ee-datasheet-master/README.md)** - Electronic component datasheet extraction with full source citations, supporting power management, MCU/SoC, sensors, and optimized for Multi-chart *(requires: pdf skill)*

  > ⭐ **Why choose ee-datasheet-master over Google NotebookLLM?**
  > - **Accuracy-first**: All data extracted directly from PDF with page citations — no hallucinations
  > - **Structured output**: Device info, power domains, pin configurations in consistent JSON format
  > - **Multi-chart support**: Optimized for complex tables, timing diagrams, characteristic curves, and register maps
  > - **Specialized for EE**: Understands electrical specs, I2C addresses, timing diagrams, register maps
  > - **Verified extraction**: Tested on 1000+ datasheets with 100% text extraction success

- **[schematic-analyzer](skills/schematic-analyzer/README.md)** - KiCad and Cadence OrCAD/Allegro schematic analysis with accuracy-first principles, providing structured JSON output for components, nets, pages, and subsystems *(requires: pdf, ee-datasheet-master skills, pcbparts MCP)*

- **[onnx-to-cvimodel](skills/onnx-to-cvimodel/README.md)** - ONNX to CVIMODEL conversion guide for YOLO models on Sophgo CV181x TPU, with ready-to-use scripts and tested configurations for YOLO11/YOLO26 (detect/pose/seg/cls)

- **[cv181x-media](skills/cv181x-media/README.md)** - Complete multimedia application development guide for reCamera with Sophgo CV181X/CV182X/CV180X chips, covering 15+ core modules including video input/output, encoding/decoding, and audio processing

- **[armbian-hardware](armbian-skills/README.md)** - One skill for Armbian capabilities, hardware application integration, deployment and diagnosis, using the existing project's language and native tools.

The development package is version 2.0.0, with static board references covering Seeed reComputer RK3576/RK3588 DevKit. Build the self-contained skill before installing from a source checkout; runtime tools use Python 3.9+ standard library. No v1 compatibility or migration is provided. See [installation](armbian-skills/README.md), [quick start](armbian-skills/QUICKSTART.md) and [简体中文](armbian-skills/QUICKSTART.zh-CN.md).

## 🚀 Installation

This repository contains independent skills under `skills/` and the [Armbian suite](armbian-skills/README.md) under `armbian-skills/`. Build and install the complete `armbian-skills/skills/armbian-hardware/` directory; the suite parent contains maintenance sources.

To use a skill from this repository:

1. Open the target skill's `README.md`
2. Follow that skill's dependency and environment setup
3. Integrate the skill using the current workflow supported by your assistant tooling

Important: using a skill is not just copying skill files. Many skills also require extra tools, Python packages, SDKs, Docker images, KiCad CLI, or MCP services. The dependency and environment setup must be completed from that skill's own `README.md` before use.

### Skill-Specific Setup

After installing a skill, open its README and complete its dependency setup before using it:

- **[onnx-to-cvimodel](skills/onnx-to-cvimodel/README.md)**: conversion scripts, Docker/TPU-MLIR environment, model assets
- **[cv181x-media](skills/cv181x-media/README.md)**: skill usage and project-specific workflow
- **[ee-datasheet-master](skills/ee-datasheet-master/README.md)**: Python dependencies for `scripts/pdf_tools.py`
- **[schematic-analyzer](skills/schematic-analyzer/README.md)**: Python dependencies, KiCad CLI, `pcbparts` MCP, and `ee-datasheet-master` / `pdf` prerequisites
- **Armbian hardware**: build and install the complete `armbian-skills/skills/armbian-hardware/` package; see [Armbian README](armbian-skills/README.md). One entry covers capability, integration, deployment and diagnosis; offline tools use Python standard library.

Recommended install order when you need schematic analysis:

1. Install and verify the built-in `pdf` skill
2. Install `ee-datasheet-master` and complete its Python dependency setup
3. Install `schematic-analyzer` and complete its KiCad CLI / MCP setup

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

**Armbian Hardware Applications:**
- "Explain which interfaces are available on this Armbian device and what is needed to use them."
- "Add AHT20 collection to my existing Go service while preserving its API."
- "Integrate NPU inference into this JavaScript application and verify the actual backend."

**Datasheet Analysis:**
- "What is the I2C address of BQ25895?"
- "Extract the pin configuration from this datasheet"
- "Find the quiescent current specification"

**Schematic Analysis:**
- "What is U10 in this schematic?"
- "Which devices are on the I2C bus?"
- "Analyze the power tree of this design"

The AI assistant will automatically invoke the relevant skills to provide professional technical guidance.

## 🤝 Contributing

Contributions of new skills or improvements to existing skills are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📄 License

This repository is licensed under the [MIT License](LICENSE).
