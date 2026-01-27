# VPSS (Video Processing Subsystem) Module Reference

## Overview

VPSS provides hardware-accelerated video post-processing with **10 major features**:

1. **CROP (Crop)** - Group-level and channel-level cropping
2. **Scale (Scaling)** - Up to 32x upscale, 1/32 downscale
3. **Pixel Format Conversion** - YUV420/YUV422/RGB/BGR, planar/packed
4. **Mirror/Flip** - Horizontal mirror, vertical flip, 180° rotation
5. **Overlay/OverlayEx** - Video overlay regions
6. **Fixed Angle Rotation** - 0°/90°/180°/270° via GDC
7. **Stitch (Image Stitching)** - Multi-channel image stitching
8. **LDC (Lens Distortion Correction)** - Lens distortion correction
9. **Deep Learning Pre-processing** - Normalization for TPU
10. **Proc Amp (Color Control)** - Brightness, contrast, saturation, hue control

### Group-Channel Architecture

```
VPSS Group → VPSS Channel (CV181X/CV182X: 0-3, CV180X: 0-2)
     |            |
   Input      Scaled Output
  (1 source)  (Multi-resolution)
```

- **Group (Grp)**: Input processing unit (one input source)
- **Channel (Chn)**: Output stream with independent resolution/format

### Typical Data Flow

```
VI/User → VPSS Grp → VPSS Chn → VENC/VO/User
                        ├─ Chn0 (1080p)
                        ├─ Chn1 (720p)
                        └─ Chn2 (360p)
```

### Input Modes and Group Ownership

VPSS groups accept only one input type for their lifetime. Do not mix input modes within a single group.

Text diagram:
```
Group A (ISP input):  VI -> ISP -> VPSS -> GetFrame/Bind
Group B (MEM input):  User/VDEC -> VPSS (Bind VDEC or SendFrame) -> GetFrame
```

**Input mode matrix**:

| Input Type | Data Source | Binding | SendFrame | Notes |
| --- | --- | --- | --- | --- |
| ISP | VI/ISP pipeline | Recommended | Not used | Online flow, lowest latency. |
| MEM (bound) | VDEC | Supported | Optional | Bind for automatic flow; SendFrame for manual control. |
| MEM (manual) | User/CPU | Not used | Required | Offline flow, manual submission. |

**Design rule**:
- If a group uses ISP input, do not call `CVI_VPSS_SendFrame()` on that group.
- If a group uses MEM input, do not bind VI to that group; use SendFrame or bind VDEC.
- Use separate groups for camera and file pipelines.

### First-Frame Readiness (Camera Path)

VI/ISP/VPSS can report ready before valid frames are available. If the first `GetChnFrame` fails, treat it as readiness and verify upstream flow.

Text flowchart:
```
[Open Camera]
   |
[Bind VI->VPSS]
   |
[Warmup + Ready Poll]
   |
[GetChnFrame]
```

**Key checks**:
- `/proc/cvitek/vi` RecvPic should be increasing.
- `/proc/cvitek/vpss` RecvCnt should be increasing.
- If both are 0, verify binding and VB pools.
 
**See also**: `binding-cookbook.md` for minimal binding flows.
**See also**: `integration-guide.md` for cross-module design and triage.

## Essential APIs

### Group Management

- `CVI_VPSS_CreateGrp()` - Create VPSS group
- `CVI_VPSS_DestroyGrp()` - Destroy group
- `CVI_VPSS_StartGrp()` - Start group processing
- `CVI_VPSS_StopGrp()` - Stop group processing
- `CVI_VPSS_ResetGrp()` - Reset group (clear buffers)
- `CVI_VPSS_SetGrpAttr()` - Set group attributes (input size, pixel format)
- `CVI_VPSS_GetGrpAttr()` - Get group attributes

### Channel Management

- `CVI_VPSS_SetChnAttr()` - Configure channel (output size, format)
- `CVI_VPSS_GetChnAttr()` - Get channel attributes
- `CVI_VPSS_EnableChn()` - Enable channel output
- `CVI_VPSS_DisableChn()` - Disable channel output
- `CVI_VPSS_ShowChn()` - Resume channel output
- `CVI_VPSS_HideChn()` - Pause channel output

### Image Processing

- `CVI_VPSS_SetGrpCrop()` - Set group-level crop
- `CVI_VPSS_GetGrpCrop()` - Get group crop settings
- `CVI_VPSS_SetChnCrop()` - Set channel-level crop
- `CVI_VPSS_GetChnCrop()` - Get channel crop settings
- `CVI_VPSS_SetChnRotation()` - Set rotation (0/90/180/270)
- `CVI_VPSS_GetChnRotation()` - Get rotation setting
- `CVI_VPSS_SetChnLDCAttr()` - Set lens distortion correction
- `CVI_VPSS_GetChnLDCAttr()` - Get LDC attributes

### Image Enhancement

- `CVI_VPSS_SetGrpProcAmp()` - Set brightness/contrast/saturation/hue
- `CVI_VPSS_GetGrpProcAmp()` - Get enhancement settings

### Frame Operations

- `CVI_VPSS_SendFrame()` - Send frame to group (manual input)
- `CVI_VPSS_GetChnFrame()` - Get processed frame from channel
- `CVI_VPSS_ReleaseChnFrame()` - Release frame buffer
- `CVI_VPSS_SendChnFrame()` - Send frame directly to channel (bypass group)

### Memory Management

- `CVI_VPSS_AttachVbPool()` - Attach video buffer pool
- `CVI_VPSS_DetachVbPool()` - Detach buffer pool

### Advanced Features

- `CVI_VPSS_SetChnScaleCoefLevel()` - Set scaling quality (0-3)
- `CVI_VPSS_SetChnYRatio()` - Set Y/C ratio for format conversion
- `CVI_VPSS_GetRegionLuma()` - Calculate luma statistics for region

### Mirror/Flip

- `CVI_VPSS_SetChnMirror()` - Set horizontal/vertical mirror flip
- `CVI_VPSS_GetChnMirror()` - Get mirror/flip setting

**Supported Mirror Modes**:
- Mirror horizontal (left-right flip)
- Mirror vertical (up-down flip)
- Mirror both (equivalent to 180° rotation)

### Overlay/OverlayEx

- `CVI_VPSS_SetOvlCrop()` - Set overlay crop region
- `CVI_VPSS_GetOvlCrop()` - Get overlay crop settings

**Supported Overlay Formats**:
- ARGB4444, ARGB1555, ARGB8888
- 256 LUT, Font-based formats

### Stitch

- `CVI_VPSS_SetStitchAttr()` - Configure stitch attributes
- `CVI_VPSS_GetStitchAttr()` - Get stitch settings
- `CVI_STITCH_ATTR_S` - Stitch configuration structure

**Use Cases**:
- Multi-camera panorama
- Wide-angle surveillance
- 360° view stitching

### Deep Learning Pre-processing

- `VPSS_NORMALIZE_S` - Normalization configuration for TPU
- Processed images can be sent to TPU for AI inference

**Features**:
- Image normalization (mean, scale)
- Format conversion for TPU input
- Direct TPU integration support

### Scale Performance

- **Upscale**: Up to 32x magnification (`VPSS_MAX_ZOOMIN`)
- **Downscale**: Down to 1/32 of original size (`VPSS_MAX_ZOOMOUT`)
- **Scale quality levels**: 0-3 (higher = better quality, slower)

## VPSS Features Detail

## Common Workflows

### Online Mode (Auto-bind from VI)

**CRITICAL**: Order matters! Follow this sequence exactly (from official SDK sample):

```
1. CVI_VPSS_CreateGrp()      // Create group
2. CVI_VPSS_ResetGrp()       // Reset group (REQUIRED!)
3. CVI_VPSS_SetChnAttr()     // Configure channels (output sizes)
4. CVI_VPSS_EnableChn()      // Enable channels FIRST
5. CVI_VPSS_StartGrp()       // Start group AFTER enable
6. CVI_SYS_Bind(VI→VPSS)     // Bind LAST (after both VI and VPSS are started)
```

**Common Mistake**: Binding before StartGrp causes silent failure (empty binding table).
Verify binding: `cat /proc/cvitek/sys | grep -A 10 "BIND RELATION"`

### Offline Mode (Manual frame input)

1. Setup VPSS as above (steps 1-5)
2. Send frame: `CVI_VPSS_SendFrame()`
3. Get result: `CVI_VPSS_GetChnFrame()`
4. Process frame data
5. Release frame: `CVI_VPSS_ReleaseChnFrame()`

### Cleanup

1. Unbind connections: `CVI_SYS_UnBind()`
2. Disable channels: `CVI_VPSS_DisableChn()`
3. Stop group: `CVI_VPSS_StopGrp()`
4. Destroy group: `CVI_VPSS_DestroyGrp()`

## Key Structures

- `VPSS_GRP_ATTR_S` - Group attributes (input size, format)
- `VPSS_CHN_ATTR_S` - Channel attributes (output size, format, scaling quality)
- `VIDEO_FRAME_INFO_S` - Frame data
- `CROP_INFO_S` - Crop region
- `ROTATION_E` - Rotation enumeration
- `VPSS_LDC_ATTR_S` - LDC attributes
- `VPSS_PROC_AMP_S` - Image enhancement parameters

## Performance Considerations

### Scaling Limits

- **Upscale**: Maximum 32x (`VPSS_MAX_ZOOMIN`)
- **Downscale**: Maximum 1/32 (`VPSS_MAX_ZOOMOUT`)
- Best quality at 1:1 ratio
- Use `SetChnScaleCoefLevel()` for quality vs performance trade-off

### Channel Limitations

- CV181X/CV182X: Maximum 4 channels per group (Chn 0-3)
- CV180X: Maximum 3 channels per group (Chn 0-2)
- Channel 0: Highest resolution (up to input size)
- Channel 1-3: Downscaled outputs (Chn 1-2 on CV180X)

### Memory Optimization

- Disable unused channels to save memory
- Use appropriate pixel formats (YUV420 uses less memory than YUV422)
- Attach shared VB pools when possible

## Header Files

- `/cvi_mpi/include/cvi_vpss.h` - Main VPSS API
- `/cvi_mpi/include/linux/cvi_comm_vpss.h` - VPSS common definitions
- `/cvi_mpi/include/linux/cvi_cv181x_defines.h` - CV181X platform limits
- `/cvi_mpi/include/linux/cvi_cv180x_defines.h` - CV180X platform limits

## Related Modules

- **VI**: Video input source
- **VENC**: Video encoding destination
- **VO**: Video output destination
- **SYS**: System binding
- **VB**: Video buffer management

## Notes

- VPSS operates in **online mode** (auto-bind) or **offline mode** (manual SendFrame)
- Group-level crop applies before channel processing
- Channel-level crop applies after scaling
- Rotation and LDC have performance impact - use only when needed
- Multiple groups can run concurrently (hardware-dependent limits)
