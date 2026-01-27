# VDEC (Video Decoding) Module Reference

## Overview

VDEC module provides video decoding services for compressed image data. It supports decoding JPEG, MJPEG, and H.264 bitstreams and outputs original image frames.

## Platform Support

| Platform | Supported Protocols |
|----------|---------------------|
| CV181X   | PT_JPEG, PT_MJPEG, PT_H264 |
| CV180X   | PT_JPEG, PT_MJPEG (no H.264 support) |

**Note**: CV180X does NOT support H.264 decoding.

## Core Concepts

### Bitstream Delivery Mode

VDEC supports **frame-by-frame** mode (`VIDEO_MODE_FRAME`):
- Each call to `CVI_VDEC_SendStream()` sends one complete frame
- The decoder considers the stream ended and starts decoding immediately
- Ensure each send contains exactly one frame

### Output Order

According to video standards (e.g., H.264), the output image sequence may differ from input sequence. Two playback orders are available:

**Decoding Order**:
- Output order matches input stream order
- Faster frame retrieval
- User must ensure correct playback order
- Required for streams with B-frames

**Display Order**:
- Output order matches playback order
- Frames are ready to display directly
- **Current setting**: Display order (default)

### PTS (Presentation Timestamp)

PTS indicates when a frame should be played. The PTS of a decoded frame (from `CVI_VDEC_GetFrame`) equals the PTS attached to the sent stream (from `CVI_VDEC_SendStream`).

## Essential APIs

### Channel Management

- `CVI_VDEC_CreateChn()` - Create video decoding channel
- `CVI_VDEC_DestroyChn()` - Destroy decoding channel
- `CVI_VDEC_SetChnAttr()` - Set channel attributes (type, resolution, mode)
- `CVI_VDEC_GetChnAttr()` - Get channel attributes

### Channel Parameters

- `CVI_VDEC_SetChnParam()` - Set channel parameters (pixel format, frame count, etc.)
- `CVI_VDEC_GetChnParam()` - Get current channel parameters

### Stream Control

- `CVI_VDEC_StartRecvStream()` - Start accepting stream data
- `CVI_VDEC_StopRecvStream()` - Stop accepting stream data
- `CVI_VDEC_SendStream()` - Send bitstream data to decoder
- `CVI_VDEC_QueryStatus()` - Query decoder status

### Frame Operations

- `CVI_VDEC_GetFrame()` - Get decoded frame
- `CVI_VDEC_ReleaseFrame()` - Release frame buffer
- `CVI_VDEC_ResetChn()` - Reset decoding channel

### Memory Management

- `CVI_VDEC_AttachVbPool()` - Bind decoder channel to VB pool
- `CVI_VDEC_DetachVbPool()` - Unbind from VB pool

**CRITICAL**: For JPEG/MJPEG decoding, ensure an NV21 VB pool exists for the decode size before creating the channel. If `enVdecVBSource` is **USER**, create and attach a dedicated pool; if **COMMON**, size the common pool and skip attach. Refer to `vdecInitVBPool()` in sample code for sizing.

## JPEG Sizing and Initialization (Critical)

JPEG decode stability depends on matching VDEC max dimensions to the actual JPEG resolution.

Text flowchart:
```
[Read JPEG Header]
   |
[Get Width/Height]
   |
[Init VDEC]
   |
[StartRecvStream]
   |
[Decode]
```

**Rules**:
- Initialize `u32PicWidth/u32PicHeight` to the JPEG width/height, not a fixed 1920x1080.
- Ensure a matching NV21 VB pool exists for that size.
- If `enVdecVBSource` is common, skip `CVI_VDEC_AttachVbPool`.

**Symptom mapping**:
- `CVI_VDEC_StartRecvStream` NOMEM → Missing or oversized VB pool for the JPEG size.
 
**See also**: `binding-cookbook.md` for end-to-end JPEG pipeline flow.
**See also**: `integration-guide.md` for cross-module design and triage.

### Module Parameters

- `CVI_VDEC_SetModParam()` - Set module-level parameters
- `CVI_VDEC_GetModParam()` - Get module parameters

## Common Workflows

### Basic Decoding Workflow

```c
// 1. Create VB pool (required for JPEG/MJPEG)
CVI_VB_CreatePool(&vb_pool_config);

// 2. Set channel attributes
VDEC_CHN_ATTR_S stChnAttr = {
    .enType = PT_JPEG,              // or PT_H264
    .enMode = VIDEO_MODE_FRAME,      // frame mode
    .u32PicWidth = 1920,
    .u32PicHeight = 1080,
    .u32StreamBufSize = 1920 * 1080,
    .u32FrameBufCnt = 3,
};

// For JPEG/MJPEG, calculate frame buffer size
if (stChnAttr.enType == PT_JPEG || stChnAttr.enType == PT_MJPEG) {
    stChnAttr.u32FrameBufSize = VDEC_GetPicBufferSize(
        stChnAttr.enType,
        stChnAttr.u32PicWidth,
        stChnAttr.u32PicHeight,
        enPixelFormat,
        DATA_BITWIDTH_8,
        0
    );
}

// 3. Create channel
CVI_VDEC_CreateChn(VdChn, &stChnAttr);

// 4. Get and set parameters
VDEC_CHN_PARAM_S stChnParam;
CVI_VDEC_GetChnParam(VdChn, &stChnParam);
stChnParam.stVdecPictureParam.enPixelFormat = PIXEL_FORMAT_YUV_PLANAR_420;
stChnParam.u32DisplayFrameNum = 3;
CVI_VDEC_SetChnParam(VdChn, &stChnParam);

// 5. Start receiving
CVI_VDEC_StartRecvStream(VdChn);

// 6. Send stream and get frames
while (running) {
    // Send encoded data
    CVI_VDEC_SendStream(VdChn, &stStream, -1);

    // Get decoded frame
    VIDEO_FRAME_INFO_S stFrameInfo;
    CVI_VDEC_GetFrame(VdChn, &stFrameInfo, -1);

    // Process frame...
    // stFrameInfo.pstFrame->u64PhyAddr - physical address
    // stFrameInfo.pstFrame->u32PTS - timestamp

    // Release frame
    CVI_VDEC_ReleaseFrame(VdChn, &stFrameInfo);
}

// 7. Cleanup
CVI_VDEC_StopRecvStream(VdChn);
CVI_VDEC_DestroyChn(VdChn);
```

### Cleanup Sequence

```c
// 1. Stop receiving: CVI_VDEC_StopRecvStream()
// 2. Destroy channel: CVI_VDEC_DestroyChn()
// 3. Detach VB pool: CVI_VDEC_DetachVbPool() (if attached)
// 4. Destroy VB pool: CVI_VB_DestroyPool() (if created)
```

## Key Structures

### Channel Attributes

- `VDEC_CHN_ATTR_S` - Channel configuration
  - `enType` - Protocol type (PT_JPEG, PT_MJPEG, PT_H264)
  - `enMode` - VIDEO_MODE_FRAME for frame-by-frame
  - `u32PicWidth` / `u32PicHeight` - Resolution
  - `u32StreamBufSize` - Stream buffer size
  - `u32FrameBufCnt` - Number of frame buffers

### Channel Parameters

- `VDEC_CHN_PARAM_S` - Runtime parameters
  - `stVdecPictureParam.enPixelFormat` - Output pixel format
  - `stVdecPictureParam.u32Alpha` - Alpha value
  - `u32DisplayFrameNum` - Display frame count

### Stream Data

- `VDEC_STREAM_S` - Input bitstream
  - `u64PTS` - Presentation timestamp
  - `u32Len` - Stream data length
  - `pu8Addr` - Pointer to stream data
  - `bEndOfFrame` - End of frame flag

### Frame Data

- `VIDEO_FRAME_INFO_S` - Decoded frame information
  - `pstFrame` - Frame data pointer
  - `u32Width` / `u32Height` - Frame dimensions
  - `enPixelFormat` - Pixel format
  - `u64PTS` - Timestamp

## Protocol Types

- `PT_JPEG` - JPEG image format
- `PT_MJPEG` - Motion JPEG
- `PT_H264` - H.264/AVC video format

## Pixel Formats

Common output formats:
- `PIXEL_FORMAT_YUV_PLANAR_420` - YUV 4:2:0 planar
- `PIXEL_FORMAT_YUV_PLANAR_422` - YUV 4:2:2 planar
- `PIXEL_FORMAT_NV12` - YUV 4:2:0 semi-planar
- `PIXEL_FORMAT_NV16` - YUV 4:2:2 semi-planar

## Header Files

- `cvi_vdec.h` - Main VDEC API
- `cvi_comm_vdec.h` - VDEC common definitions
- `cvi_comm_video.h` - Video frame structures

## Related Modules

- **VPSS**: Post-processing of decoded frames
- **VO**: Direct display of decoded frames
- **VENC**: Re-encoding (transcoding scenarios)
- **VB**: Video buffer pool for frame storage
- **SYS**: Module binding for automatic data flow

## Notes

### Memory Requirements

**CRITICAL**: For JPEG/MJPEG decoding, create a dedicated VB pool before creating the decoding channel. The block size varies by protocol:

```c
// Calculate required buffer size
u32Size = VDEC_GetPicBufferSize(
    PT_JPEG,
    width,
    height,
    PIXEL_FORMAT_YUV_PLANAR_420,
    DATA_BITWIDTH_8,
    0
);
```

Reference `vdecInitVBPool()` in `sample_vdec_lib.c` for exact calculations.

### Blocking vs Non-Blocking

`s32MilliSec` parameter in `CVI_VDEC_SendStream()` and `CVI_VDEC_GetFrame()`:
- `-1`: Blocking (wait indefinitely)
- `0`: Non-blocking (return immediately)
- `>0`: Wait for specified milliseconds

### Error Handling

Common error codes:
- `CVI_ERR_VDEC_NOMEM` (0xC001800C) - Out of memory
- `CVI_ERR_VDEC_NOBUF` (0xC001800D) - No buffer available
- `CVI_ERR_VDEC_BUSY` (0xC0018012) - System busy
- `ERR_CVI_VDEC_SEND_STREAM` - Stream send failed

### Thread Safety

- VDEC APIs are thread-safe
- Multiple threads can operate on different channels
- Use proper synchronization when accessing the same channel

## Typical Use Cases

1. **Video File Playback** - Decode JPEG/MJPEG/H.264 files for display
2. **Network Streaming** - Decode received video streams (e.g., RTSP)
3. **Image Decoding** - Decode JPEG images from storage
4. **Transcoding** - Decode and re-encode with different parameters

## Performance Considerations

- Use Display Order for most applications (default)
- For JPEG/MJPEG, create dedicated VB pool to avoid buffer conflicts
- Adjust `u32FrameBufCnt` based on application requirements
- Higher frame count = smoother playback but more memory usage
- For H.264 with B-frames, minimum 3 frame buffers recommended

## References

- `markdown_docs/Video_Decoding/Function_Overview.md`
- `markdown_docs/Video_Decoding/Design_Overview.md`
- `markdown_docs/Video_Decoding/API_Reference.md`
- `cvi_mpi/sample/source/vdec/sample_vdec_lib.c`
