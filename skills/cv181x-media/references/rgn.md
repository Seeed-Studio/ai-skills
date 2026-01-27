# RGN (Region Management) Module Reference

## Overview

RGN (Region) module provides on-screen graphics overlay capabilities for video streams. It's primarily used for:
- **OSD (On-Screen Display)**: Timestamps, channel names, system info
- **Cover**: Privacy masking, logo covering
- **Overlay**: Transparent graphics, watermarks
- **Line/Mosaic**: Detection boxes, privacy blur

## Core Concepts

### Region Types

1. **OVERLAY**: Bitmap graphics with transparency (ARGB)
   - Use case: Text, icons, logos with alpha channel
   - Supports: Arbitrary colors, transparency levels

2. **COVER**: Solid color rectangle (privacy mask)
   - Use case: Block sensitive areas (license plates, faces)
   - Supports: Solid color only, no transparency

3. **COVEREX**: Advanced cover with invert color
   - Use case: Highlight regions by inverting colors
   - Supports: Color inversion effect

4. **LINE**: Draw lines and rectangles
   - Use case: Bounding boxes for object detection
   - Supports: Multiple line segments, configurable thickness

5. **MOSAIC**: Pixelation effect
   - Use case: Privacy blur for sensitive areas
   - Supports: Configurable mosaic block size

### Region Architecture

```
RGN Handle (Region Object)
   ↓
Attach to Channel (VI/VPSS/VENC)
   ↓
Display on Video Stream
```

**Workflow**:
1. Create region (get RGN handle)
2. Set region attributes (type, size, bitmap)
3. Attach to module channel (VI/VPSS/VENC)
4. Set display attributes (position, layer)
5. Update content (optional, for dynamic OSD)

## Essential APIs

### Region Creation and Destruction

- `CVI_RGN_Create()` - Create region object (get handle)
- `CVI_RGN_Destroy()` - Destroy region object

### Region Configuration

- `CVI_RGN_SetAttr()` - Set region attributes (size, format, bitmap)
- `CVI_RGN_GetAttr()` - Get region attributes

### Channel Attachment

- `CVI_RGN_AttachToChn()` - Attach region to module channel
- `CVI_RGN_DetachFromChn()` - Detach region from channel
- `CVI_RGN_SetDisplayAttr()` - Set display position and layer
- `CVI_RGN_GetDisplayAttr()` - Get display attributes

### Content Update (for dynamic OSD)

- `CVI_RGN_GetCanvasInfo()` - Get canvas buffer for drawing
- `CVI_RGN_UpdateCanvas()` - Update canvas content
- `CVI_RGN_SetBitMap()` - Update bitmap directly
- `CVI_RGN_SetChnPalette()` - Set color palette for channel

## Common Workflows

### 1. Create Timestamp OSD (OVERLAY type)

```c
// Step 1: Create region
RGN_HANDLE hOverlay = 0;
RGN_ATTR_S stRegion;
stRegion.enType = OVERLAY_RGN;
stRegion.unAttr.stOverlay.enPixelFmt = PIXEL_FORMAT_ARGB_1555;
stRegion.unAttr.stOverlay.stSize.u32Width = 400;   // OSD width
stRegion.unAttr.stOverlay.stSize.u32Height = 50;   // OSD height
stRegion.unAttr.stOverlay.u32BgColor = 0x7FFF;     // Transparent background

CVI_RGN_Create(hOverlay, &stRegion);

// Step 2: Prepare bitmap (text rendering - use freetype or pre-rendered)
CVI_U8 *pBitmap = malloc(400 * 50 * 2);  // ARGB1555: 2 bytes per pixel
// ... render timestamp to pBitmap ...

// Step 3: Set bitmap
BITMAP_S stBitmap;
stBitmap.enPixelFormat = PIXEL_FORMAT_ARGB_1555;
stBitmap.u32Width = 400;
stBitmap.u32Height = 50;
stBitmap.pData = pBitmap;

CVI_RGN_SetBitMap(hOverlay, &stBitmap);

// Step 4: Attach to VENC channel (OSD on encoded stream)
MMF_CHN_S stChn;
stChn.enModId = CVI_ID_VENC;
stChn.s32DevId = 0;
stChn.s32ChnId = 0;

RGN_CHN_ATTR_S stChnAttr;
stChnAttr.bShow = CVI_TRUE;
stChnAttr.enType = OVERLAY_RGN;
stChnAttr.unChnAttr.stOverlayChn.stPoint.s32X = 20;   // Position X
stChnAttr.unChnAttr.stOverlayChn.stPoint.s32Y = 20;   // Position Y
stChnAttr.unChnAttr.stOverlayChn.u32Layer = 0;        // Layer 0 (bottom)

CVI_RGN_AttachToChn(hOverlay, &stChn, &stChnAttr);

// Step 5: Update timestamp periodically
// (In a thread/timer)
while (running) {
    // Get canvas
    RGN_CANVAS_INFO_S stCanvasInfo;
    CVI_RGN_GetCanvasInfo(hOverlay, &stCanvasInfo);

    // Update timestamp on canvas
    char timestamp[64];
    time_t now = time(NULL);
    strftime(timestamp, sizeof(timestamp), "%Y-%m-%d %H:%M:%S", localtime(&now));
    // ... render timestamp to stCanvasInfo.pu8VirtAddr ...

    // Apply update
    CVI_RGN_UpdateCanvas(hOverlay);

    sleep(1);
}
```

### 2. Create Privacy Mask (COVER type)

```c
// Create cover region
RGN_HANDLE hCover = 1;
RGN_ATTR_S stRegion;
stRegion.enType = COVER_RGN;
// COVER type has no size in attributes (set at attach time)

CVI_RGN_Create(hCover, &stRegion);

// Attach to VI channel (mask before processing)
MMF_CHN_S stChn;
stChn.enModId = CVI_ID_VI;
stChn.s32DevId = 0;
stChn.s32ChnId = 0;

RGN_CHN_ATTR_S stChnAttr;
stChnAttr.bShow = CVI_TRUE;
stChnAttr.enType = COVER_RGN;
stChnAttr.unChnAttr.stCoverChn.enCoverType = AREA_RECT;           // Rectangle
stChnAttr.unChnAttr.stCoverChn.stRect.s32X = 100;
stChnAttr.unChnAttr.stCoverChn.stRect.s32Y = 100;
stChnAttr.unChnAttr.stCoverChn.stRect.u32Width = 200;
stChnAttr.unChnAttr.stCoverChn.stRect.u32Height = 200;
stChnAttr.unChnAttr.stCoverChn.u32Color = 0x000000;               // Black
stChnAttr.unChnAttr.stCoverChn.u32Layer = 0;

CVI_RGN_AttachToChn(hCover, &stChn, &stChnAttr);
```

### 3. Draw Bounding Boxes (LINE type)

```c
// Create line region for detection boxes
RGN_HANDLE hLine = 2;
RGN_ATTR_S stRegion;
stRegion.enType = LINE_RGN;

CVI_RGN_Create(hLine, &stRegion);

// Attach to VPSS channel
MMF_CHN_S stChn;
stChn.enModId = CVI_ID_VPSS;
stChn.s32DevId = 0;
stChn.s32ChnId = 0;

RGN_CHN_ATTR_S stChnAttr;
stChnAttr.bShow = CVI_TRUE;
stChnAttr.enType = LINE_RGN;
stChnAttr.unChnAttr.stLineChn.u32Color = 0xFF0000;    // Red
stChnAttr.unChnAttr.stLineChn.u32Thickness = 2;       // 2 pixels thick
stChnAttr.unChnAttr.stLineChn.u32Layer = 1;

// Define rectangle (4 line segments)
stChnAttr.unChnAttr.stLineChn.stLinePoint[0].s32X = 100;
stChnAttr.unChnAttr.stLineChn.stLinePoint[0].s32Y = 100;
stChnAttr.unChnAttr.stLineChn.stLinePoint[1].s32X = 300;
stChnAttr.unChnAttr.stLineChn.stLinePoint[1].s32Y = 100;
stChnAttr.unChnAttr.stLineChn.stLinePoint[2].s32X = 300;
stChnAttr.unChnAttr.stLineChn.stLinePoint[2].s32Y = 300;
stChnAttr.unChnAttr.stLineChn.stLinePoint[3].s32X = 100;
stChnAttr.unChnAttr.stLineChn.stLinePoint[3].s32Y = 300;
stChnAttr.unChnAttr.stLineChn.stLinePoint[4].s32X = 100;
stChnAttr.unChnAttr.stLineChn.stLinePoint[4].s32Y = 100;
stChnAttr.unChnAttr.stLineChn.u32PointNum = 5;

CVI_RGN_AttachToChn(hLine, &stChn, &stChnAttr);

// Update bounding box dynamically (AI detection results)
void update_detection_box(int x, int y, int w, int h) {
    RGN_CHN_ATTR_S stChnAttr;
    CVI_RGN_GetDisplayAttr(hLine, &stChn, &stChnAttr);

    stChnAttr.unChnAttr.stLineChn.stLinePoint[0] = (POINT_S){x, y};
    stChnAttr.unChnAttr.stLineChn.stLinePoint[1] = (POINT_S){x+w, y};
    stChnAttr.unChnAttr.stLineChn.stLinePoint[2] = (POINT_S){x+w, y+h};
    stChnAttr.unChnAttr.stLineChn.stLinePoint[3] = (POINT_S){x, y+h};
    stChnAttr.unChnAttr.stLineChn.stLinePoint[4] = (POINT_S){x, y};

    CVI_RGN_SetDisplayAttr(hLine, &stChn, &stChnAttr);
}
```

### 4. Create Mosaic (Privacy Blur)

```c
// Create mosaic region
RGN_HANDLE hMosaic = 3;
RGN_ATTR_S stRegion;
stRegion.enType = MOSAIC_RGN;

CVI_RGN_Create(hMosaic, &stRegion);

// Attach to channel
MMF_CHN_S stChn;
stChn.enModId = CVI_ID_VPSS;
stChn.s32DevId = 0;
stChn.s32ChnId = 0;

RGN_CHN_ATTR_S stChnAttr;
stChnAttr.bShow = CVI_TRUE;
stChnAttr.enType = MOSAIC_RGN;
stChnAttr.unChnAttr.stMosaicChn.stRect.s32X = 200;
stChnAttr.unChnAttr.stMosaicChn.stRect.s32Y = 200;
stChnAttr.unChnAttr.stMosaicChn.stRect.u32Width = 150;
stChnAttr.unChnAttr.stMosaicChn.stRect.u32Height = 150;
stChnAttr.unChnAttr.stMosaicChn.enBlkSize = MOSAIC_BLK_SIZE_8;  // 8x8 pixel blocks
stChnAttr.unChnAttr.stMosaicChn.u32Layer = 0;

CVI_RGN_AttachToChn(hMosaic, &stChn, &stChnAttr);
```

### Cleanup

```c
// Detach from channel
CVI_RGN_DetachFromChn(hOverlay, &stChn);

// Destroy region
CVI_RGN_Destroy(hOverlay);
```

## Attachment Targets

Regions can be attached to:
- **VI channels**: OSD applied before processing (affects all downstream)
- **VPSS channels**: OSD applied after processing (per channel)
- **VENC channels**: OSD only in encoded stream (not in preview)

**Choose attachment point based on use case**:
- Attach to **VI**: OSD on all outputs (preview, recording, streaming)
- Attach to **VPSS**: OSD on specific resolution stream
- Attach to **VENC**: OSD only in recorded/streamed video, not live preview

## Layer and Priority

- Multiple regions can attach to same channel
- **Layer number** determines overlay order (0 = bottom, higher = top)
- Lower layer number = drawn first (behind higher layers)
- Maximum layers: Typically 4-8 (hardware dependent)

**Example**:
```
Layer 0: Background logo (bottom)
Layer 1: Timestamp OSD
Layer 2: Bounding boxes
Layer 3: Privacy mask (top, blocks everything below)
```

## Pixel Formats for OVERLAY

- **ARGB1555**: 1-bit alpha + 5-bit RGB (2 bytes/pixel)
  - Good for: Simple transparency (on/off)
  - Memory efficient

- **ARGB4444**: 4-bit alpha + 4-bit RGB (2 bytes/pixel)
  - Good for: 16 transparency levels
  - Better gradients than ARGB1555

- **ARGB8888**: 8-bit alpha + 8-bit RGB (4 bytes/pixel)
  - Good for: Smooth transparency, anti-aliased text
  - High quality but memory intensive

## Performance Considerations

### Memory Usage

Each OVERLAY region consumes memory for bitmap:
- Memory = Width × Height × BytesPerPixel
- Example: 400×50 ARGB1555 = 40,000 bytes (~39 KB)

Multiple regions can add up quickly - monitor total memory usage.

### Processing Overhead

- OVERLAY: Moderate overhead (alpha blending)
- COVER: Minimal overhead (simple fill)
- LINE: Low overhead (vector drawing)
- MOSAIC: Moderate overhead (downsampling + upsampling)

**Optimization tips**:
- Use smallest possible OSD size
- Choose ARGB1555 over ARGB8888 when possible
- Minimize number of regions (combine OSDs when possible)
- Update canvas only when content changes (not every frame)

## Key Structures

- `RGN_ATTR_S` - Region attributes (type, size, format)
- `RGN_CHN_ATTR_S` - Channel display attributes (position, layer)
- `BITMAP_S` - Bitmap data structure
- `RGN_CANVAS_INFO_S` - Canvas info for dynamic updates

## Header Files

- `/cvi_mpi/include/cvi_region.h` - Main RGN API
- `/cvi_mpi/include/linux/cvi_comm_region.h` - RGN common definitions

## Related Modules

- **VI/VPSS/VENC**: Region attachment targets
- **VB**: Buffer management for region bitmaps

**See also**: `integration-guide.md` for cross-module design and triage.

## Notes

- Regions are global objects - can be attached to multiple channels
- OVERLAY bitmap must be allocated in VB pool or ION memory for zero-copy
- Update canvas operations should be synchronized to avoid tearing
- Maximum region size depends on hardware capabilities
- Coordinate system origin (0,0) is top-left corner
- Regions outside video bounds are clipped automatically
- Always detach before destroying region
- Use `bShow = CVI_FALSE` to temporarily hide region without detaching

## Debugging

### Check Region Status

```bash
# View region information
cat /proc/cvitek/rgn
```

### Common Issues

**Issue**: OSD not visible
- Check `bShow = CVI_TRUE`
- Verify position is within video bounds
- Check layer order (may be behind other regions)
- Verify bitmap is not fully transparent

**Issue**: OSD position incorrect
- Coordinate system is (0,0) at top-left
- Check alignment requirements (may need multiple of 2 or 4)

**Issue**: Flickering OSD
- Synchronize UpdateCanvas with frame timing
- Avoid updating too frequently

**Issue**: Memory allocation failure
- Reduce OSD size or pixel format (use ARGB1555 instead of ARGB8888)
- Check VB pool configuration
