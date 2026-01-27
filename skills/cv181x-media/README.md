# CV181X/CV182X/CV180X Multimedia API Skill

> **Maintained by**: Seeed Studio  
> **Repository**: https://github.com/Seeed-Studio/ai-skills  
> **Original work by**: [Pillar1989](https://github.com/Pillar1989/cv181x-media)

Expert guidance skill for CV181X/CV182X/CV180X multimedia development on Sophgo platforms (reCamera).

## Overview

This skill provides comprehensive knowledge of:
- VI (Video Input)
- VPSS (Video Processing)
- VENC (Video Encoding)
- VDEC (Video Decoding)
- VO (Video Output)
- Audio (AI/AO/AENC/ADEC/VQE)
- SYS (System Control)
- VB (Video Buffer Pool)
- REGION (Regional Management/OSD)
- GDC (Geometric Distortion Correction Subsystem)
- Debugging and troubleshooting

## Version

Current Version: **v2.3.0**

## What's New in v2.3.0

- **Overview + Platform References**: Added `overview.md` and `platform.md` for system workflow, SDK layout, and pixel formats
- **Integration Guide**: Added `integration-guide.md` for cross-module design and triage
- **Binding Cookbook Consolidation**: Concurrent scenarios fully consolidated into `binding-cookbook.md`
- **Binding Matrix Clarified**: VDEC -> VPSS bind vs SendFrame options clarified and aligned with SDK samples
- **VPSS Limits Aligned**: Scaling limits and channel counts aligned with SDK defines

## What's New in v2.1.0

- **Source Code Verification**: All APIs verified against cvi_mpi source code
- **Critical Fixes**: VENC SendFrame memory requirements corrected (must use VB Pool)
- **Missing APIs Added**: VENC SendFrameEx, USER_FRAME_INFO_S, GDC CancelJob, GDC MESH structures
- **Module List Complete**: Added H265D, H264D, VPSSF, TPU to MOD_ID_E enumeration
- **ION Cache Management**: Added IonFlushCache/IonInvalidateCache documentation
- **VPSS Constraints**: Documented input source mode restrictions (Bind vs SendFrame)
- **Binding Cookbook**: Consolidated concurrent scenarios with TPU inference path
- **VB Pool Enhancements**: VB_INVALID_POOLID clarification and EX mode documentation

See [CHANGELOG.md](CHANGELOG.md) for complete details.

## Structure

```
cv181x-media/
├── SKILL.md              # Main skill definition
├── references/           # Module reference documentation
│   ├── vi.md            # Video Input (4-layer architecture)
│   ├── vpss.md          # Video Processing (10 features)
│   ├── venc.md          # Video Encoding
│   ├── vdec.md          # Video Decoding (NEW)
│   ├── vo.md            # Video Output
│   ├── audio.md         # Audio Subsystem (NEW)
│   ├── sys.md           # System Control (11 categories)
│   ├── vb.md            # Video Buffer (8 categories)
│   ├── rgn.md           # Region Management
│   ├── gdc.md           # Geometric Distortion Correction
│   ├── debug.md         # Debugging guide
│   ├── troubleshooting.md
│   ├── overview.md      # System overview and workflow
│   ├── platform.md      # SDK layout and platform limits
│   ├── integration-guide.md # Cross-module integration rules
│   └── scenarios.md     # Common scenarios
├── scripts/              # Automation scripts
│   ├── update_from_sdk.sh
│   ├── learn_from_usage.py
│   └── validate_skill.sh
└── .skillrc              # Skill configuration
```

## Self-Learning and Auto-Update

This skill is designed to continuously improve through:

### 1. SDK Updates
Automatically extract and integrate new API information from SDK releases:
```bash
./scripts/update_from_sdk.sh /path/to/new/sdk
```

### 2. Usage Learning
Learn from actual usage patterns and collect feedback:
```bash
./scripts/learn_from_usage.py --feedback-file usage_log.txt
```

### 3. Version Control
All changes are tracked via git:
```bash
git log --oneline  # View change history
git diff v1.0.0    # Compare with previous version
```

## Update Workflow

1. **Detect SDK Update**: Monitor SDK release notes
2. **Extract Changes**: Parse new headers and documentation
3. **Update References**: Regenerate affected reference docs
4. **Validate**: Run validation checks
5. **Commit**: Version control with semantic versioning
6. **Package**: Create new .skill file

## Usage

Install this skill in Claude Code or Codex:

```bash
# Claude
claude skills install git+https://github.com/Seeed-Studio/ai-skills#subdirectory=skills/cv181x-media

# Codex
codex skills install git+https://github.com/Seeed-Studio/ai-skills#subdirectory=skills/cv181x-media
```

Once installed, ask your AI assistant questions like:
- "How to configure VI module to capture 1080p video?"
- "Show me how to add timestamp OSD to video stream"
- "How to correct barrel distortion from wide-angle lens?"

## Contributing

To improve this skill, please contribute to the main repository: https://github.com/Seeed-Studio/ai-skills

1. Fork the repository
2. Create feature branch: `git checkout -b feature/cv181x-media-improvement`
3. Make improvements
4. Submit pull request

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for detailed guidelines.

### Feedback Collection

When using this skill, report issues or improvements:
- API changes discovered
- Missing information
- Incorrect documentation
- New use cases

## Maintenance

### Regular Tasks

- [ ] Monthly: Check for SDK updates
- [ ] Quarterly: Review usage patterns and update common scenarios
- [ ] Annually: Major version release with comprehensive review

### Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## License

This skill is licensed under the [MIT License](LICENSE).

## Acknowledgments

This skill was originally created by [Pillar1989](https://github.com/Pillar1989/cv181x-media) and is now maintained by Seeed Studio for the reCamera developer community.

## Authors

- Original creation: Pillar1989, 2026-01-17
- Maintained by: Seeed Studio, 2026-01-27+
- Auto-update system: Enabled
