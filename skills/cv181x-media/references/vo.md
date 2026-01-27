# VO (Video Output) Module Reference

## Overview

VO module handles video display output to screens (LCD, HDMI, etc.) with features:
- Multiple video layers
- Hardware-accelerated scaling
- Format conversion
- Rotation and mirroring
- Gamma correction

## Core Concepts

### Device-Layer-Channel Architecture

```
VO Device
   └─ Video Layer
       ├─ Channel 0
       ├─ Channel 1
       └─ Channel N
```

- **Device (Dev)**: Physical display interface (LCD controller, HDMI, etc.)
- **Layer**: Video overlay layer (can have multiple layers for composition)
- **Channel (Chn)**: Individual video window/region

### Typical Data Flow

```
VI/VPSS → VO Chn → VO Layer → VO Dev → Display
```

## Essential APIs

### Device Management

- `CVI_VO_SetPubAttr()` - Set device public attributes (interface type, resolution)
- `CVI_VO_GetPubAttr()` - Get device attributes
- `CVI_VO_Enable()` - Enable video output device
- `CVI_VO_Disable()` - Disable device

### Layer Management

- `CVI_VO_SetVideoLayerAttr()` - Configure video layer (position, size)
- `CVI_VO_GetVideoLayerAttr()` - Get layer attributes
- `CVI_VO_EnableVideoLayer()` - Enable video layer
- `CVI_VO_DisableVideoLayer()` - Disable video layer

### Channel Management

- `CVI_VO_SetChnAttr()` - Configure channel (position, size, priority)
- `CVI_VO_GetChnAttr()` - Get channel attributes
- `CVI_VO_EnableChn()` - Enable channel display
- `CVI_VO_DisableChn()` - Disable channel
- `CVI_VO_ShowChn()` - Show channel (resume display)
- `CVI_VO_HideChn()` - Hide channel (pause display)
- `CVI_VO_SetChnRotation()` - Set rotation (0/90/180/270)
- `CVI_VO_GetChnRotation()` - Get rotation setting

### Frame Operations

- `CVI_VO_SendFrame()` - Send frame to channel (manual mode)
- `CVI_VO_PauseChn()` - Pause channel (freeze on last frame)
- `CVI_VO_ResumeChn()` - Resume channel
- `CVI_VO_ClearChnBuf()` - Clear channel buffer

### Display Enhancement

- `CVI_VO_SetLayerProcAmp()` - Set brightness/contrast/saturation/hue
- `CVI_VO_GetLayerProcAmp()` - Get enhancement settings
- `CVI_VO_SetGammaInfo()` - Set gamma correction
- `CVI_VO_GetGammaInfo()` - Get gamma settings

### Debug

- `CVI_VO_ShowPattern()` - Display test pattern

## Common Workflows

### Basic Display (Online Mode)

1. Configure device: `CVI_VO_SetPubAttr()` (interface type, resolution)
2. Enable device: `CVI_VO_Enable()`
3. Configure layer: `CVI_VO_SetVideoLayerAttr()` (display region)
4. Enable layer: `CVI_VO_EnableVideoLayer()`
5. Configure channel: `CVI_VO_SetChnAttr()` (window position/size)
6. Enable channel: `CVI_VO_EnableChn()`
7. Bind from VI/VPSS: `CVI_SYS_Bind(VI/VPSS, VO)`

### Manual Frame Display (Offline Mode)

1. Setup VO as above (steps 1-6)
2. Send frame: `CVI_VO_SendFrame()`

### Cleanup

1. Unbind: `CVI_SYS_UnBind()`
2. Disable channel: `CVI_VO_DisableChn()`
3. Disable layer: `CVI_VO_DisableVideoLayer()`
4. Disable device: `CVI_VO_Disable()`

## Key Structures

- `VO_PUB_ATTR_S` - Device public attributes (interface type, resolution, frame rate)
- `VO_VIDEO_LAYER_ATTR_S` - Video layer attributes (position, size, pixel format)
- `VO_CHN_ATTR_S` - Channel attributes (position, size, priority)
- `VIDEO_FRAME_INFO_S` - Frame data
- `VO_PROC_AMP_S` - Image enhancement parameters

## Supported Interfaces

- **MIPI DSI** - For MIPI LCD panels
- **I8080** - For MCU LCD panels
- **RGB** - For parallel RGB LCD
- **BT656/BT1120** - For standard video output

## Performance Considerations

### Resolution Limits

- Maximum output resolution depends on interface type
- Typical MIPI DSI: Up to 1080p
- Typical I8080: Up to 480x320

### Layer Composition

- Multiple layers can be composited
- Layer priority determines overlay order
- Alpha blending supported for composition

## Header Files

- `/cvi_mpi/include/cvi_vo.h` - Main VO API
- `/cvi_mpi/include/linux/cvi_comm_vo.h` - VO common definitions

## Related Modules

- **VI/VPSS**: Video source
- **SYS**: System binding
- **Panel**: LCD panel initialization

**See also**: `integration-guide.md` for cross-module design and triage.

## Notes

- VO operates in **online mode** (auto-bind) or **offline mode** (manual SendFrame)
- For LCD displays, panel must be initialized before VO setup
- Channel display priority: Lower value = higher priority (displayed on top)
- Use `ShowChn()`/`HideChn()` for temporary on/off without disabling
- Use `PauseChn()`/`ResumeChn()` to freeze/unfreeze display
- Rotation has performance impact on some platforms
