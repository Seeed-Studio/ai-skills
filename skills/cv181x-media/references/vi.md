# VI (Video Input) Module Reference

## Overview

VI module handles video input from camera sensors through the ISP (Image Signal Processor) pipeline. It manages:
- Device configuration (sensor interface)
- Pipe configuration (ISP processing pipeline)
- Channel configuration (output streams)

## Core Concepts

### Four-Layer Architecture

```
Sensor → DEV → ISP_FE → ISP_BE → CHN → Output
         |      |        |        |
      Timing  Stats   Image    Crop/
      Parse  Store   Process  Rotate
```

- **DEV (Device)**: Physical sensor interface that parses timing signals
- **ISP_FE (ISP Front End)**: Image capture - extracts AE/AWB/AF statistics, stores RAW to DDR
- **ISP_BE (ISP Back End)**: Image processing - color space conversion, image quality adjustment
- **CHN (Channel)**: Image correction - crop, rotation, distortion correction

#### DEV (Device Layer)
- Parses timing signals from sensor
- Supports multiple interface types: MIPI, LVDS, HISPI, SLVS, BT.1120, BT.656, BT.601
- Manages physical connection to camera sensor

#### ISP_FE (ISP Front End)
- Extracts statistical data:
  - **AE** (Auto Exposure) - Exposure statistics
  - **AWB** (Auto White Balance) - White balance statistics
  - **AF** (Auto Focus) - Focus statistics
- Stores RAW data to DDR memory
- Supports online (direct) and offline (memory) modes

#### ISP_BE (ISP Back End)
- Color space conversion (RAW → YUV/RGB)
- Image quality adjustment:
  - Brightness, contrast, saturation
  - Noise reduction (3DNR)
  - Sharpness enhancement
- Supports online and offline modes

#### CHN (Channel)
- Image correction features:
  - **Crop** - Extract region of interest
  - **Rotation** - 0°/90°/180°/270°
  - **Mirror/Flip** - Horizontal/vertical flip
  - **LDC** - Lens distortion correction
- Outputs processed frames to VPSS/VENC/User

### Typical Data Flow

```
Sensor → VI Dev → VI Pipe → VI Chn → VPSS/VENC/User
```

### Readiness and First-Frame Behavior

The first valid frame can arrive after a short warm-up period even when VI/ISP appears enabled.

Text flowchart:
```
[Enable VI Chn]
   |
[Bind to VPSS]
   |
[Warmup + Ready Poll]
   |
[First Frame]
```

**What to check**:
- `/proc/cvitek/vi` RecvPic should be increasing.
- `/proc/cvitek/vpss` RecvCnt should be increasing for bound pipelines.
- If both remain 0, verify binding table and VB pools before retrying.
 
**See also**: `binding-cookbook.md` for minimal camera pipeline flow.
**See also**: `integration-guide.md` for cross-module design and triage.

## Essential APIs

### Device Management

- `CVI_VI_SetDevAttr()` - Configure device attributes (interface type, data format)
- `CVI_VI_EnableDev()` - Enable video input device
- `CVI_VI_DisableDev()` - Disable video input device
- `CVI_VI_SetDevBindPipe()` - Bind device to pipe
- `CVI_VI_GetDevBindPipe()` - Query device-pipe binding

### Pipe Management

- `CVI_VI_CreatePipe()` - Create ISP processing pipe
- `CVI_VI_DestroyPipe()` - Destroy pipe
- `CVI_VI_SetPipeAttr()` - Configure pipe attributes (resolution, frame rate)
- `CVI_VI_StartPipe()` - Start pipe processing
- `CVI_VI_StopPipe()` - Stop pipe processing
- `CVI_VI_GetPipeFrame()` - Get RAW frame from pipe (for offline ISP)
- `CVI_VI_ReleasePipeFrame()` - Release RAW frame

### Channel Management

- `CVI_VI_SetChnAttr()` - Configure channel attributes (resolution, pixel format)
- `CVI_VI_EnableChn()` - Enable channel output
- `CVI_VI_DisableChn()` - Disable channel output
- `CVI_VI_GetChnFrame()` - Get processed frame from channel
- `CVI_VI_ReleaseChnFrame()` - Release frame buffer

### Image Processing

- `CVI_VI_SetChnCrop()` - Set channel crop region
- `CVI_VI_GetChnCrop()` - Get channel crop settings
- `CVI_VI_SetChnRotation()` - Set rotation (0/90/180/270)
- `CVI_VI_GetChnRotation()` - Get rotation setting
- `CVI_VI_SetChnFlipMirror()` - Set flip/mirror mode
- `CVI_VI_GetChnFlipMirror()` - Get flip/mirror setting
- `CVI_VI_SetChnLDCAttr()` - Set lens distortion correction
- `CVI_VI_GetChnLDCAttr()` - Get LDC attributes

### Advanced Features

- `CVI_VI_SetPipeBypassMode()` - Set pipe bypass mode
- `CVI_VI_SetDevAttrEx()` - Set advanced device attributes (WDR mode)
- `CVI_VI_SetDevTimingAttr()` - Set self-generating timing attributes
- `CVI_VI_GetDevTimingAttr()` - Get timing attributes

#### WDR (Wide Dynamic Range)
- **CV181X**: Supports WDR modes (2To1, 3To1, 4To1 Line/Frame)
- **CV180X**: Does NOT support HDR
- Configured via `VI_WDR_ATTR_S` in device attributes
- Modes: WDR_MODE_BUILT_IN, WDR_MODE_QUDRA, WDR_MODE_2To1_LINE, etc.

#### LDC (Lens Distortion Correction)
- Corrects lens distortion and fisheye effects
- Enabled via `VI_LDC_ATTR_S`
- Must allocate additional VB pool for LDC function

#### 3DNR (3D Noise Reduction)
- Temporal noise reduction
- Reduces noise in video sequences
- Configured via pipe attributes

#### Sharpen
- Image sharpness enhancement
- Improves perceived image quality
- Configured via pipe attributes

#### Bypass Modes
- **bIspBypass** - Disable ISP processing
- **bYuvSkip** - Skip downsampling and CSC
- **b3dnrBypass** - Bypass 3DNR (ALIOS/DUAL OS only)

### Memory Management

- `CVI_VI_AttachVbPool()` - Attach video buffer pool to channel
- `CVI_VI_DetachVbPool()` - Detach buffer pool

### Status Query

- `CVI_VI_QueryDevStatus()` - Query device status
- `CVI_VI_QueryPipeStatus()` - Query pipe status
- `CVI_VI_QueryChnStatus()` - Query channel status (frame count, lost frames, etc.)

## Common Workflows

### Basic Video Capture (Online Mode)

1. Initialize system: `CVI_SYS_Init()`
2. Configure and enable device: `CVI_VI_SetDevAttr()` → `CVI_VI_EnableDev()`
3. Bind device to pipe: `CVI_VI_SetDevBindPipe()`
4. Create and configure pipe: `CVI_VI_CreatePipe()` → `CVI_VI_SetPipeAttr()`
5. Start pipe: `CVI_VI_StartPipe()`
6. Configure and enable channel: `CVI_VI_SetChnAttr()` → `CVI_VI_EnableChn()`
7. Bind to next module (VPSS/VENC): `CVI_SYS_Bind()`

### Manual Frame Capture

1. Setup VI as above (steps 1-6)
2. Get frame: `CVI_VI_GetChnFrame()`
3. Process frame data
4. Release frame: `CVI_VI_ReleaseChnFrame()`

### Cleanup

1. Unbind: `CVI_SYS_UnBind()`
2. Disable channel: `CVI_VI_DisableChn()`
3. Stop pipe: `CVI_VI_StopPipe()`
4. Destroy pipe: `CVI_VI_DestroyPipe()`
5. Disable device: `CVI_VI_DisableDev()`

## Key Structures

- `VI_DEV_ATTR_S` - Device attributes
- `VI_PIPE_ATTR_S` - Pipe attributes (resolution, frame rate, pixel format)
- `VI_CHN_ATTR_S` - Channel attributes
- `VIDEO_FRAME_INFO_S` - Frame data (used in Get/Release)
- `CROP_INFO_S` - Crop region
- `ROTATION_E` - Rotation enumeration
- `VI_LDC_ATTR_S` - Lens distortion correction attributes

## Header Files

- `/cvi_mpi/include/cvi_vi.h` - Main VI API
- `/cvi_mpi/include/linux/cvi_comm_vi.h` - VI common definitions
- `/cvi_mpi/include/linux/cvi_comm_video.h` - Video frame structures

## Related Modules

- **ISP**: Low-level image tuning (AE, AWB, etc.)
- **VPSS**: Post-processing (scaling, rotation, etc.)
- **SYS**: System binding and buffer management
- **VB**: Video buffer pool allocation

## Notes

- VI channels can operate in **online mode** (auto-bind to VPSS/VENC) or **offline mode** (manual frame fetch)
- Maximum VI channels per pipe: 3 physical + 2 virtual (see `VI_MAX_PHY_CHN_NUM` and `VI_MAX_VIR_CHN_NUM` in platform defines)
- Channel 0 is typically the main stream (highest resolution)
- RAW format requires offline ISP processing
- YUV format can be directly encoded or displayed

### Supported Interface Types (VI_INTF_MODE_E)

**MIPI Interfaces**:
- `VI_MODE_MIPI` - MIPI RAW mode
- `VI_MODE_MIPI_YUV420_NORMAL` - MIPI YUV420 normal mode
- `VI_MODE_MIPI_YUV420_LEGACY` - MIPI YUV420 legacy mode
- `VI_MODE_MIPI_YUV422` - MIPI YUV422 mode

**Other Digital Interfaces**:
- `VI_MODE_LVDS` - LVDS mode
- `VI_MODE_HISPI` - HISPI mode
- `VI_MODE_SLVS` - SLVS mode

**Parallel Interfaces**:
- `VI_MODE_BT1120_STANDARD` - BT.1120 progressive mode
- `VI_MODE_BT1120_INTERLEAVED` - BT.1120 interlaced mode
- `VI_MODE_BT656` - BT.656 mode
- `VI_MODE_BT601` - BT.601 mode
- `VI_MODE_DIGITAL_CAMERA` - Digital camera mode

### Maximum Resolution by Platform

| Platform | Max Resolution | Frame Rate |
|----------|---------------|------------|
| **CV181X** | 5M (2880x1620) | 30fps |
| **CV180X** | 4M (2560x1440) | 30fps |

**Note**: CV180X does NOT support HDR/WDR functions.
