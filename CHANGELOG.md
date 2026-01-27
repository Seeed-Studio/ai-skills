# Changelog

All notable changes to the CV181X Media Skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.3.0] - 2026-01-20

### Added

- `references/overview.md` for system workflow, online/offline modes, and common pipelines
- `references/platform.md` for SDK layout, platform differences, and pixel formats
- `references/integration-guide.md` for cross-module design and triage
- Consolidated concurrent scenarios into `references/binding-cookbook.md`

### Changed

- Clarified VDEC -> VPSS bind vs SendFrame options in system guidance
- Aligned VPSS scaling limits and channel counts with SDK defines
- Updated index and README navigation to point to new references

### Removed

- `references/concurrent.md` (superseded by binding cookbook)

## [2.1.0] - 2026-01-18

### Source Code Verification Release - Critical Fixes and Missing APIs

This release addresses critical errors and missing content identified through comprehensive source code verification against cvi_mpi SDK headers and sample code.

### Fixed - Critical Errors (P0)

- **VENC SendFrame Memory Requirements**:
  - Corrected documentation to clarify SendFrame **requires VB Pool** memory
  - Added explicit ✅ Correct / ❌ Incorrect usage examples
  - Documented that VB_INVALID_POOLID means "get from any common pool", not "don't use pool"
  - Added complete file input example with VB GetBlock pattern
  - **Impact**: Prevents incorrect ION memory usage that could cause failures

- **VENC SendFrameEx API Added**:
  - Added `CVI_VENC_SendFrameEx()` documentation
  - Added `USER_FRAME_INFO_S` structure with custom rate control
  - Documented differences between SendFrame and SendFrameEx
  - **Impact**: Enables advanced encoding scenarios with per-frame rate control

- **MOD_ID_E Module List Completed**:
  - Added **H264D** (H.264 Decoder) module
  - Added **H265D** (H.265 Decoder) module
  - Added **VPSSF** (VPSS Frontend) module
  - Added **TPU** (Tensor Processing Unit) module
  - **Impact**: Prevents attempts to use non-existent module IDs

### Added - Important Missing Content (P1)

- **ION Cache Management APIs**:
  - Added `CVI_SYS_IonAlloc_Cached()` documentation
  - Added `CVI_SYS_IonFlushCache()` - Flush cache before hardware access
  - Added `CVI_SYS_IonInvalidateCache()` - Invalidate cache after hardware access
  - Added `CVI_SYS_IonGetFd()` - Get ION file descriptor
  - Added complete cache management pattern with code examples
  - **Files**: SKILL.md

- **GDC CancelJob API**:
  - Added `CVI_GDC_CancelJob()` documentation
  - Added error handling patterns with CancelJob vs EndJob
  - Documented when to use/cannot use CancelJob
  - Added cleanup pattern for robust error handling
  - **Files**: references/gdc.md

- **GDC MESH Functionality**:
  - Added `MESH_DUMP_ATTR_S` structure documentation
  - Added `VI_MESH_ATTR_S` structure
  - Added `VPSS_MESH_ATTR_S` structure
  - Added mesh import/export workflow examples
  - Documented use cases for fisheye dewarp calibration and mesh versioning
  - **Files**: references/gdc.md

- **VB Pool EX Mode**:
  - Added `VB_POOL_CONFIG_EX_S` structure documentation
  - Documented user-managed memory blocks
  - Added ION memory integration example with EX mode
  - Explained difference from standard pools
  - Added multi-user-block configuration example
  - **Files**: references/vb.md

- **VB_INVALID_POOLID Clarification**:
  - Added dedicated section explaining VB_INVALID_POOLID meaning
  - Clarified it means "get from any common pool", not "don't use pool"
  - Added when to use/when not to use guidelines
  - Documented pool ID retrieval with `CVI_VB_Handle2PoolId()`
  - **Files**: references/vb.md

- **VPSS Input Source Constraints**:
  - Documented that VPSS Groups **cannot** dynamically switch input modes
  - Added Online Mode (Bind) vs Offline Mode (SendFrame) comparison
  - Listed prohibited operations (switching, mixing modes)
  - Added multi-scenario solution with separate VPSS Groups
  - Added complete code example for Camera → VPSS + File → VPSS
  - **Files**: SKILL.md

### Added - Enhancements (P2)

- **Binding Cookbook (Concurrent Scenarios)**:
  - Created comprehensive new file: `references/binding-cookbook.md`
  - **Scenario 1**: Camera → VPSS → Save/Display (Online Mode)
  - **Scenario 2**: File → VPSS → VENC → Save Bitstream (Offline Mode)
  - **Scenario 3**: VPSS → TPU Inference → Draw → Save (NEW!)
    - TPU input buffer allocation with alignment (4096-byte)
    - YUV to RGB format conversion
    - Zero-copy vs copy strategies
    - Drawing bounding boxes on frames
    - Complete memory management examples
  - **Scenario 4**: Complete Concurrent Example
    - Multi-threaded implementation
    - Camera + File + TPU running simultaneously
    - VB pool design for multi-scenario
  - **Size**: ~800 lines with complete code examples
  - **Impact**: Enables complex multi-scenario applications with AI integration

- **Audio API Naming Verification**:
  - Verified all audio APIs use correct naming (CVI_AI_xxx, CVI_AO_xxx)
  - Confirmed `CVI_AUD_SYS_Bind()` is correct (not CVI_AIO_SYS_Bind)
  - No changes needed - documentation was already correct

### Changed

- **VENC Module** (references/venc.md):
  - Added "SendFrame Memory Requirements" section
  - Added "SendFrameEx (Advanced Mode)" section
  - Reorganized with clearer subsections
  - Added cross-references to VB module

- **VB Module** (references/vb.md):
  - Added "VB_INVALID_POOLID - Special Pool ID" section
  - Added "VB Pool EX Mode" section
  - Enhanced with decision tables and use case guidelines

- **SYS Module** (references/sys.md):
  - Updated MOD_ID_E list with 4 new modules
  - Updated module count to reflect additions
  - Added TPU description

- **GDC Module** (references/gdc.md):
  - Added "Error Handling with CancelJob" section
  - Added "MESH Management Structures" section
  - Enhanced with practical patterns

- **SKILL.md**:
  - Added "VPSS Input Source Constraints" section
  - Added "ION Cache Management" section
  - Added link to binding cookbook reference
  - Enhanced with critical warnings about VPSS limitations

### Documentation Sources

All changes based on comprehensive analysis of:
- `cvi_mpi/include/*.h` - Complete API header files (CVI_VI, CVI_VPSS, CVI_VENC, CVI_VDEC, etc.)
- `cvi_mpi/sample/*` - Official SDK sample code
- `linux/cvi_comm_*.h` - Common definitions and structures
- Analysis reports: SKILL_VS_SOURCE_ANALYSIS.md, VENC_MEMORY_VPSS_INPUT_ANALYSIS.md

### Migration Notes

- **Breaking Change**: This is a minor version update (v2.0.0 → v2.1.0)
- **Critical Correction**: VENC SendFrame **must** use VB Pool (not direct ION)
- **New Capabilities**: SendFrameEx, MESH management, binding cookbook with TPU
- **No API Changes**: All existing code patterns remain valid
- **Recommended Action**: Review VENC memory usage if using ION directly

### Verification

- ✅ All new APIs verified against source code
- ✅ All code examples compile with SDK headers
- ✅ All cross-references valid
- ✅ No duplicate content
- ✅ Consistent formatting and structure

## [2.0.0] - 2026-01-18

### Major Release - Complete Module Coverage and Platform Documentation

This release adds comprehensive documentation for all CV181X/CV182X/CV180X multimedia modules, including previously missing VDEC and Audio subsystems, complete API coverage, platform differences, and advanced features.

### Added - New Modules

- **Video Decoding (VDEC)** Module Reference (`references/vdec.md`):
  - JPEG/MJPEG/H.264 decoding support
  - Frame mode decoding workflow
  - PTS (Presentation Timestamp) handling
  - Platform differences (CV181X vs CV180X for H.264)
  - Complete API documentation with code examples

- **Audio Subsystem** Reference (`references/audio.md`):
  - 5 audio sub-modules: AI (Audio Input), AO (Audio Output), AENC, ADEC, VQE
  - Supported sample rates (8kHz - 48kHz)
  - Frame size requirements (160/320/480 samples)
  - VQE (Voice Quality Enhancement): AEC, ANR, AGC
  - ALSA integration
  - Resample APIs
  - Complete workflows for capture, playback, encoding

### Added - Module Enhancements

- **VI (Video Input)** Module (`references/vi.md`):
  - 4-layer architecture: DEV, ISP_FE, ISP_BE, CHN
  - Supported interface types (VI_INTF_MODE_E): MIPI, LVDS, HISPI, SLVS, BT.1120, BT.656, BT.601
  - Advanced features: WDR, LDC, 3DNR, Sharpen, Bypass modes
  - Maximum resolution by platform (CV181X: 5M, CV180X: 4M)

- **VPSS (Video Processing)** Module (`references/vpss.md`):
  - 10 major features explicitly documented
  - Mirror/Flip operations
  - Overlay/OverlayEx support
  - Stitch functionality
  - Deep Learning Pre-processing for TPU
  - Scale performance (32x upscale, 1/32 downscale)

- **SYS (System Control)** Module (`references/sys.md`):
  - Expanded from 4 to 11 function categories
  - Complete MOD_ID_E enumeration (39 modules)
  - VI-VPSS working modes: 4 modes with detailed data flow
  - VPSS modes: SINGLE/DUAL/RGNEX
  - Dual-OS communication (CVI_MSG_Init/Deinit)
  - Temperature monitoring with thermal callbacks

- **VB (Video Buffer)** Module (`references/vb.md`):
  - 8 major function categories
  - VB pool types: COMMON/MODULE/PRIVATE/USER
  - Buffer count calculation rules
  - VB data flow example
  - Block size calculation helper APIs

### Added - Platform Documentation

- **Platform Details** section in SKILL.md:
  - Complete PIXEL_FORMAT_E enumeration (60+ formats)
  - RGB/BGR/ARGB formats
  - Bayer (sensor RAW) formats
  - YUV planar/semi-planar/packed formats
  - Deep learning formats for TPU (FP32/INT32/BF16/etc.)
  - Alignment requirements with calculation examples
  - Platform differences table (CV181X vs CV180X):
    - Resolution (5M vs 4M)
    - HDR/WDR support
    - VO module availability
    - VDEC H.264 support
    - VPSS channel counts

### Added - System Integration

- **System Binding Mechanism** documentation in SKILL.md:
  - Complete binding table (VI/VDEC/Audio to all receivers)
  - One-to-many binding examples
  - Binding behavior explanation
  - Audio module bindings (AI→AENC, AO→ADEC)

- **VB-SYS Initialization Dependency** clarification:
  - CRITICAL initialization order with warning
  - Correct sequence: CVI_VB_SetConfig → CVI_VB_Init → CVI_SYS_Init
  - Deinit sequence: CVI_SYS_Exit → CVI_VB_Exit

### Changed - Module Names

- **RGN** → **REGION (Regional Management)**:
  - Clarified that RGN is abbreviation
  - Documented types: OVERLAY, COVER, LINE, MOSAIC

- **GDC** → **Geometric Distortion Correction Subsystem (GDC)**:
  - Added "Subsystem" suffix
  - Documented JOB/TASK architecture

### Changed - Skill Description

- Updated YAML frontmatter with 15 use scenarios
- Added all missing modules: VDEC, Audio (AI/AO/AENC/ADEC/VQE)
- Expanded supported interfaces list
- Added platform coverage: CV181X/CV182X/CV180X
- Reorganized Core Capabilities into Video/Audio/System sections

### Added - Use Scenarios

Expanded from 10 to 15 use scenarios:
1. Video capture from camera sensors via multiple interfaces
2. Video encoding with ROI, GOP, frame skipping
3. Video decoding (JPEG/MJPEG/H.264)
4. Video processing with stitching
5. Video display output (CV181X only)
6. On-screen display and graphics overlay
7. Audio capture, playback, encoding, decoding, voice enhancement
8. Fisheye correction and lens distortion correction
9. Module binding and system integration
10. Video buffer memory management
11. System monitoring (temperature, thermal callbacks)
12. Deep learning pre-processing and TPU integration
13. Dual-OS communication
14. Debugging multimedia applications
15. Building multimedia applications

### Documentation Sources

All changes based on comprehensive analysis of:
- `markdown_docs/Video_Decoding/` - VDEC module documentation
- `markdown_docs/Audio_Frequency/` - Audio subsystem documentation (193KB)
- `markdown_docs/System_Control/` - SYS, VB, and working mode documentation
- `markdown_docs/Video_Input/` - VI architecture and interfaces
- `markdown_docs/Video_Processing_Subsystem/` - VPSS features and TPU integration
- Official SDK sample code and API references

### Migration Notes

- **Breaking Change**: This is a major version update (v1.1.0 → v2.0.0)
- **New Modules**: Applications can now access VDEC and Audio documentation
- **Platform Awareness**: Documentation now explicitly covers CV180X limitations
- **Enhanced Accuracy**: Corrected module names and architecture descriptions
- **Complete Coverage**: All 29 todo.md items have been implemented

## [1.1.0] - 2026-01-18

### Added
- **Troubleshooting Guide** (`references/troubleshooting.md`):
  - Complete error code reference table for VPSS, VI modules
  - Diagnostic decision tree for ERR_VPSS_NOBUF (0xc006800e)
  - Correct initialization sequence from official SDK sample code
  - Binding parameter rules from official documentation
  - Debug commands for /proc/cvitek filesystem
  - Common pitfalls with code examples (correct vs incorrect)
  - Recovery procedures for corrupted kernel state

### Changed
- **SKILL.md**:
  - Updated VPSS Quick Start with correct initialization order (EnableChn → StartGrp → Bind)
  - Added CRITICAL note about binding timing requirement
  - Enhanced Module Binding Pattern with detailed parameter rules
  - Added binding verification command (`cat /proc/cvitek/sys`)
  - Updated debug section with ERR_VPSS_NOBUF quick diagnosis steps
  - Fixed all `/proc/umap/` references to `/proc/cvitek/`

- **references/vpss.md**:
  - Corrected Online Mode workflow with proper order (from official sample_common_vpss.c)
  - Added ResetGrp requirement after CreateGrp
  - Added binding verification note

- **references/sys.md**:
  - Enhanced Notes section with specific binding timing requirements
  - Added Binding Parameter Rules section (VPSS as receiver vs sender)
  - Added binding verification command

### Fixed
- Corrected VPSS initialization order: CreateGrp → ResetGrp → SetChnAttr → EnableChn → StartGrp → Bind
- Previous documentation had incorrect order (StartGrp before EnableChn)
- Fixed /proc filesystem path from /proc/umap to /proc/cvitek

### Documentation Sources
- Official SDK MediaProcessingSoftwareDevelopmentReference_en.pdf (p.2299-2300 for binding rules)
- cvi_mpi/sample/common/sample_common_vpss.c (SAMPLE_COMM_VPSS_Init, SAMPLE_COMM_VPSS_Start)
- cvi_mpi/sample/vio/sample_vio.c (complete VI→VPSS→Bind workflow)

## [1.0.0] - 2026-01-17

### Added
- Initial release of CV181X/CV182X multimedia API skill
- **Core Modules Documentation**:
  - VI (Video Input) - Complete API reference with 60+ APIs
  - VPSS (Video Processing Subsystem) - 50+ APIs for scaling, rotation, cropping
  - VENC (Video Encoding) - 100+ APIs for H.264/H.265/JPEG/MJPEG encoding
  - VO (Video Output) - 30+ APIs for LCD/HDMI display
  - SYS (System Control) - Module binding and memory management
  - VB (Video Buffer Pool) - Unified memory management with 11 APIs
  - RGN (Region Management) - OSD overlay and graphics with 12 APIs
  - GDC (Geometric Distortion Correction) - LDC, fisheye dewarp, rotation with 11 APIs
- **Reference Documentation**:
  - Complete API lists extracted from SDK headers
  - Workflow guides for each module
  - Performance optimization tips
  - Common pitfalls and solutions
- **Debugging Guide** (`debug.md`):
  - /proc filesystem usage for runtime monitoring
  - Log system control
  - Common issue troubleshooting
  - Performance profiling methods
- **Scenarios** (`scenarios.md`):
  - 6 real-world application examples
  - Video surveillance camera
  - Smart doorbell with display
  - Image processing device
  - Video conference device
  - AI-powered security camera
  - Multi-channel NVR
- **Auto-Update System**:
  - `update_from_sdk.sh` - Extract API changes from new SDK releases
  - `learn_from_usage.py` - Analyze usage patterns and collect feedback
  - `validate_skill.sh` - Validate skill integrity
- **Git Version Control**:
  - Repository initialization
  - Semantic versioning support
  - Changelog tracking
- **Configuration**:
  - `.skillrc` - Skill configuration file
  - `.gitignore` - Git ignore rules

### Documentation Structure
```
cv181x-media/
├── SKILL.md              # Main skill (11 capability sections)
├── README.md             # Skill overview and usage
├── CHANGELOG.md          # Version history
├── .skillrc              # Configuration
├── references/           # 10 module reference docs
│   ├── vi.md
│   ├── vpss.md
│   ├── venc.md
│   ├── vo.md
│   ├── sys.md
│   ├── vb.md
│   ├── rgn.md
│   ├── gdc.md
│   ├── debug.md
│   └── scenarios.md
└── scripts/              # Automation scripts
    ├── update_from_sdk.sh
    ├── learn_from_usage.py
    └── validate_skill.sh
```

### Features
- **Comprehensive Coverage**: 11 core capability sections covering all multimedia modules
- **Progressive Disclosure**: Core workflows in SKILL.md, detailed APIs in references
- **Real-World Scenarios**: 6 complete application examples with full pipelines
- **Self-Learning**: Automatic feedback collection and improvement suggestions
- **Version Controlled**: Full git integration for tracking changes
- **Auto-Update**: Detect SDK changes and extract new APIs automatically

### Technical Details
- Total APIs documented: 300+
- Modules covered: 8 (VI, VPSS, VENC, VO, SYS, VB, RGN, GDC)
- Reference documentation: 10 files (~15,000 words)
- Code examples: 30+ workflow examples
- Debug commands: 20+ /proc filesystem checks

### Platform Support
- SG2002 (CV182X)
- SG2000 (CV180X)
- Compatible with reCamera-OS SDK

### Known Limitations
- Manual review required after SDK updates (auto-extraction only)
- Learning system requires user feedback logs
- Some platform-specific features may vary

## [Unreleased]

### Planned
- ISP (Image Signal Processor) module documentation
- VDEC (Video Decoding) module documentation
- Audio module (AIO, AENC, ADEC) integration
- More scenario examples (PTZ camera, object tracking, etc.)
- Interactive troubleshooting flowcharts
- Performance benchmarking tools

---

## Version History

- **v1.0.0** (2026-01-17): Initial release with 8 core modules and auto-update system
