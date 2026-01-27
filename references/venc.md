# VENC (Video Encoding) Module Reference

## Overview

VENC provides hardware-accelerated video encoding with support for:
- **H.264/AVC** - Main/High profile
- **H.265/HEVC** - Main profile
- **JPEG** - Baseline sequential
- **MJPEG** - Motion JPEG

## Core Concepts

### Channel-Based Architecture

```
VENC Channel
    |
Input Frame → Encoder → Bitstream
```

- **Channel (Chn)**: Independent encoding instance
- Each channel has its own codec type, resolution, and rate control

### Typical Data Flow

```
VI/VPSS → VENC Chn → Bitstream → File/Network
```

### VPSS to VENC Linkage (Recommended)

For camera pipelines, prefer VPSS output as VENC input. This isolates encoding from sensor format and allows multi-resolution outputs.

Text table:

| Source | VENC Input | Binding | VB Pool Requirement |
| --- | --- | --- | --- |
| VPSS Chn | VIDEO_FRAME_INFO_S | Recommended | Pool sized to VPSS output format/size |
| VI Chn (direct) | VIDEO_FRAME_INFO_S | Optional | Pool sized to VI output format/size |

**Design notes**:
- Use one VPSS channel per encoded stream (e.g., 1080p + 720p).
- Ensure VB pools exist for each VPSS output size used by VENC.
- Start VI/VPSS/VENC before binding to avoid silent bind failure.
 
**See also**: `binding-cookbook.md` for minimal binding flows.
**See also**: `integration-guide.md` for cross-module design and triage.

## Essential APIs

### Channel Management

- `CVI_VENC_CreateChn()` - Create encoding channel
- `CVI_VENC_DestroyChn()` - Destroy channel
- `CVI_VENC_ResetChn()` - Reset channel (clear buffers)
- `CVI_VENC_SetChnAttr()` - Configure channel (codec, resolution, bitrate)
- `CVI_VENC_GetChnAttr()` - Get channel attributes

### Encoding Control

- `CVI_VENC_StartRecvFrame()` - Start accepting frames
- `CVI_VENC_StopRecvFrame()` - Stop accepting frames
- `CVI_VENC_SendFrame()` - Send frame for encoding (manual mode)
- `CVI_VENC_SendFrameEx()` - Send frame with extended parameters

### Bitstream Retrieval

- `CVI_VENC_GetStream()` - Get encoded bitstream (blocking/non-blocking)
- `CVI_VENC_ReleaseStream()` - Release bitstream buffer
- `CVI_VENC_QueryStatus()` - Query channel status (frames encoded, bitrate, etc.)
- `CVI_VENC_GetStreamBufInfo()` - Get stream buffer status

### Rate Control

- `CVI_VENC_SetRcParam()` - Set rate control parameters (bitrate, QP, etc.)
- `CVI_VENC_GetRcParam()` - Get rate control settings
- `CVI_VENC_SetRcAdvParam()` - Set advanced RC parameters
- `CVI_VENC_GetRcAdvParam()` - Get advanced RC settings

### H.264/H.265 Features

- `CVI_VENC_RequestIDR()` - Force IDR frame
- `CVI_VENC_EnableIDR()` - Enable periodic IDR
- `CVI_VENC_SetH264SliceSplit()` / `CVI_VENC_SetH265SliceSplit()` - Configure slice splitting
- `CVI_VENC_SetH264Entropy()` / `CVI_VENC_SetH265Entropy()` - Set entropy coding (CABAC/CAVLC)
- `CVI_VENC_SetH264Vui()` / `CVI_VENC_SetH265Vui()` - Set VUI parameters
- `CVI_VENC_SetH264Dblk()` / `CVI_VENC_SetH265Dblk()` - Set deblocking filter
- `CVI_VENC_SetIntraRefresh()` - Configure intra refresh

### ROI (Region of Interest)

- `CVI_VENC_SetRoiAttr()` - Set ROI for better quality in specific regions
- `CVI_VENC_GetRoiAttr()` - Get ROI settings
- `CVI_VENC_SetRoiAttrEx()` - Set extended ROI attributes

### JPEG/MJPEG

- `CVI_VENC_SetJpegParam()` - Set JPEG quality (Q-factor)
- `CVI_VENC_GetJpegParam()` - Get JPEG parameters
- `CVI_VENC_SetMjpegParam()` - Set MJPEG parameters
- `CVI_VENC_GetMjpegParam()` - Get MJPEG settings

### Advanced Features

- `CVI_VENC_SetSuperFrameStrategy()` - Handle frames exceeding bitrate budget
- `CVI_VENC_SetFrameLostStrategy()` - Configure frame drop policy
- `CVI_VENC_InsertUserData()` - Insert SEI user data

### Memory Management

- `CVI_VENC_AttachVbPool()` - Attach video buffer pool
- `CVI_VENC_DetachVbPool()` - Detach buffer pool

### SendFrame Memory Requirements

**CRITICAL**: `CVI_VENC_SendFrame()` requires VB Pool memory, **NOT** direct ION memory.

#### Correct Usage - VB Pool Allocation

```c
// ✅ Correct: Use VB Pool (all official samples follow this pattern)
VB_BLK blk = CVI_VB_GetBlock(VB_INVALID_POOLID, frame_size);

VIDEO_FRAME_INFO_S frame = {
    .stVFrame.u64PhyAddr[0] = CVI_VB_Handle2PhysAddr(blk),
    .stVFrame.pu8VirAddr[0] = CVI_VB_GetBlockVirAddr(blk),
    .u32PoolId = CVI_VB_Handle2PoolId(blk),  // ← Required!
    // Set other fields (width, height, format, stride, etc.)
};

CVI_VENC_SendFrame(chn, &frame, -1);

// Release after encoding completes
CVI_VB_ReleaseBlock(blk);
```

#### Incorrect Usage - Direct ION Memory

```c
// ❌ Incorrect: Direct ION usage is NOT supported
CVI_SYS_IonAlloc(&ion_paddr, &ion_vaddr, "Frame", frame_size);

VIDEO_FRAME_INFO_S frame = {
    .stVFrame.u64PhyAddr[0] = ion_paddr,
    .stVFrame.pu8VirAddr[0] = ion_vaddr,
    .u32PoolId = VB_INVALID_POOL_ID,  // ← May cause issues
    // ...
};

CVI_VENC_SendFrame(chn, &frame, -1);  // ← May fail or behave unexpectedly
```

#### Key Points

- **VB_INVALID_POOLID**: Means "get block from any available common pool", NOT "don't use a pool"
- **u32PoolId**: Must be set to a valid pool ID (from `CVI_VB_Handle2PoolId()`)
- **Source**: All official SDK samples use `CVI_VB_GetBlock()` for SendFrame
- **File Input**: For file→VENC scenarios, copy file data to VB pool before SendFrame

#### File Input Example (with VB Pool)

```c
// Read file into temporary buffer
void *file_data = read_file_to_memory("frame.yuv");

// Allocate VB block
VB_CAL_CONFIG_S vb_cfg;
COMMON_GetPicBufferConfig(1920, 1080, PIXEL_FORMAT_YUV_PLANAR_420,
                         DATA_BITWIDTH_8, COMPRESS_MODE_NONE,
                         DEFAULT_ALIGN, &vb_cfg);

VB_BLK blk = CVI_VB_GetBlock(VB_INVALID_POOLID, vb_cfg.u32VBSize);

// Construct frame
VIDEO_FRAME_INFO_S frame;
frame.stVFrame.u64PhyAddr[0] = CVI_VB_Handle2PhysAddr(blk);
frame.stVFrame.pu8VirAddr[0] = CVI_VB_GetBlockVirAddr(blk);
frame.u32PoolId = CVI_VB_Handle2PoolId(blk);

// Copy file data to VB block
memcpy(frame.stVFrame.pu8VirAddr[0], file_data, vb_cfg.u32VBSize);

// Send to encoder
CVI_VENC_SendFrame(chn, &frame, -1);

// Cleanup
free(file_data);
CVI_VB_ReleaseBlock(blk);
```

**See also**: [VB Module Reference](vb.md) for pool configuration and buffer allocation.

### SendFrameEx (Advanced Mode)

`CVI_VENC_SendFrameEx()` provides extended frame submission with custom rate control information.

#### API Signature

```c
CVI_S32 CVI_VENC_SendFrameEx(VENC_CHN VeChn,
                              const USER_FRAME_INFO_S *pstFrame,
                              CVI_S32 s32MilliSec);
```

#### USER_FRAME_INFO_S Structure

```c
typedef struct _USER_FRAME_INFO_S {
    VIDEO_FRAME_INFO_S stUserFrame;   // Standard video frame info
    USER_RC_INFO_S stUserRcInfo;      // Custom rate control info (per-frame)
} USER_FRAME_INFO_S;
```

#### Difference from SendFrame

| API | Frame Structure | Features |
|-----|----------------|----------|
| **SendFrame** | `VIDEO_FRAME_INFO_S` | Standard frame submission |
| **SendFrameEx** | `USER_FRAME_INFO_S` | Adds custom rate control per frame |

#### Use Cases

- **Per-frame rate control**: Adjust QP, bitrate, or priority for specific frames
- **Advanced encoding**: Custom RC parameters for I/P/B frames
- **Complex scenarios**: Region-specific quality adjustments
- **Adaptive streaming**: Real-time quality adaptation based on network conditions

#### Example: Custom Rate Control

```c
// Allocate VB block and construct frame
VB_BLK blk = CVI_VB_GetBlock(VB_INVALID_POOLID, frame_size);
VIDEO_FRAME_INFO_S video_frame = {
    .stVFrame.u64PhyAddr[0] = CVI_VB_Handle2PhysAddr(blk),
    .stVFrame.pu8VirAddr[0] = CVI_VB_GetBlockVirAddr(blk),
    .u32PoolId = CVI_VB_Handle2PoolId(blk),
    // ... set width, height, format, etc.
};

// Configure custom RC for this frame
USER_RC_INFO_S rc_info = {
    .s32Qp = 28,                    // Custom QP value
    .u32Bitrate = 2000000,          // Target bitrate (bps)
    .enPriority = RC_PRIORITY_HIGH, // Frame priority
};

// Construct extended frame
USER_FRAME_INFO_S user_frame = {
    .stUserFrame = video_frame,
    .stUserRcInfo = rc_info,
};

// Send with custom RC parameters
CVI_VENC_SendFrameEx(chn, &user_frame, -1);
```

**Note**: `USER_RC_INFO_S` structure details depend on codec type and platform. Refer to SDK headers for complete field definitions.

## Common Workflows

### H.264/H.265 Encoding (Online Mode)

1. Create channel: `CVI_VENC_CreateChn()` with codec type and attributes
2. Configure rate control: `CVI_VENC_SetRcParam()`
3. (Optional) Configure GOP/Entropy/VUI: `CVI_VENC_SetH264*()` / `CVI_VENC_SetH265*()`
4. Start receiving frames: `CVI_VENC_StartRecvFrame()`
5. Bind from VI/VPSS: `CVI_SYS_Bind(VI/VPSS, VENC)`
6. **Retrieve bitstream loop**:
   - `CVI_VENC_GetStream()` (blocking or polling)
   - Save bitstream to file/network
   - `CVI_VENC_ReleaseStream()`

### JPEG Snapshot

1. Create JPEG channel: `CVI_VENC_CreateChn()` with PT_JPEG
2. Set quality: `CVI_VENC_SetJpegParam()`
3. Start receiving: `CVI_VENC_StartRecvFrame()`
4. Send single frame: `CVI_VENC_SendFrame()`
5. Get JPEG data: `CVI_VENC_GetStream()`
6. Release: `CVI_VENC_ReleaseStream()`

### Cleanup

1. Unbind: `CVI_SYS_UnBind()`
2. Stop receiving: `CVI_VENC_StopRecvFrame()`
3. Destroy channel: `CVI_VENC_DestroyChn()`

## Key Structures

### Channel Attributes

- `VENC_CHN_ATTR_S` - Channel configuration
  - `stVencAttr` - Encoder attributes (codec type, resolution, profile)
  - `stRcAttr` - Rate control mode (CBR, VBR, FIXQP, etc.)
  - `stGopAttr` - GOP structure

### Rate Control Modes

- **CBR** (Constant Bitrate) - Fixed bitrate, variable quality
- **VBR** (Variable Bitrate) - Variable bitrate, target quality
- **AVBR** (Adaptive VBR) - Adaptive bitrate for scene complexity
- **FIXQP** (Fixed QP) - Fixed quantization parameter

### Bitstream

- `VENC_STREAM_S` - Encoded bitstream
  - `pstPack` - Array of bitstream packets
  - `u32PackCount` - Number of packets
  - Each packet has address, length, frame type (I/P/B)

### GOP Types

- `VENC_GOPMODE_NORMALP` - I + P frames
- `VENC_GOPMODE_SMARTP` - Smart P (long-term reference)
- `VENC_GOPMODE_BIPREDB` - I + P + B frames

## Performance Considerations

### Encoding Capacity

- Maximum encoding capability varies by chip model
- Typical: 4K@30fps or 1080p@60fps (H.265)
- Use `CVI_VENC_QueryStatus()` to monitor performance

### Rate Control Tips

- **CBR**: Best for streaming (constant bandwidth)
- **VBR**: Best for storage (better quality in complex scenes)
- **FIXQP**: Best for quality testing (predictable quality)

### Bitrate Guidelines

- **1080p H.265**: 2-4 Mbps (medium quality)
- **1080p H.264**: 4-8 Mbps (medium quality)
- **720p H.265**: 1-2 Mbps
- Adjust based on scene complexity and quality requirements

## Header Files

- `/cvi_mpi/include/cvi_venc.h` - Main VENC API
- `/cvi_mpi/include/linux/cvi_comm_venc.h` - VENC common definitions
- `/cvi_mpi/include/linux/cvi_comm_rc.h` - Rate control definitions

## Related Modules

- **VI/VPSS**: Video input source
- **SYS**: System binding
- **VB**: Video buffer management

## Notes

- Each channel operates independently
- Maximum channels depend on hardware resources and resolution
- For JPEG snapshots, create dedicated JPEG channel
- For MJPEG, use H.264/H.265 channel APIs with PT_MJPEG codec type
- Always release bitstream after use to prevent buffer overflow
- Use `CVI_VENC_GetStreamBufInfo()` to monitor buffer usage
- IDR frames increase bitstream size but enable seeking and error recovery
