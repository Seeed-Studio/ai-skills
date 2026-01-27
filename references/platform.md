# Platform and SDK Reference

This document consolidates platform-level facts that apply across modules. Values are taken from SDK headers under `cvi_mpi/include/linux/` unless noted.

## SDK Layout

**Repository layout**:
- Headers: `cvi_mpi/include/`
- Libraries: `cvi_mpi/lib/`
- Samples: `cvi_mpi/sample/`

**Installed SDK layout**:
- Use the SDK root and locate the same `include/`, `lib/`, and `sample/` subtrees.

**Common headers**:
- `cvi_vi.h`, `cvi_vpss.h`, `cvi_venc.h`, `cvi_vdec.h`, `cvi_vo.h`
- `cvi_sys.h`, `cvi_vb.h`, `cvi_region.h`, `cvi_gdc.h`
- `linux/cvi_comm_*.h` (common structures and enums)

**Common libraries**:
- `libsys.so`, `libvpss.so`, `libvi.so`, `libvenc.so`, `libvdec.so`, `libvo.so`
- `libvb.so`, `librgn.so`, `libgdc.so`

**Sample locations**:
- `sample/vio/`, `sample/venc/`, `sample/region/`

## Platform Differences (CV181X vs CV180X)

| Feature | CV181X | CV180X | Source |
| --- | --- | --- | --- |
| VI max resolution | 5M (2880x1620) | 4M (2560x1440) | `vi.md` |
| HDR/WDR | Supported | Not supported | `vi.md` |
| VO module | Supported | Not supported | `sys.md` |
| VDEC H.264 | Supported | Not supported | `vdec.md` |
| VDEC JPEG/MJPEG | Supported | Supported | `vdec.md` |
| VPSS channels per group | 4 | 3 | `cvi_cv181x_defines.h`, `cvi_cv180x_defines.h` |

## Shared Limits (Both Platforms)

Values from `cvi_cv181x_defines.h` and `cvi_cv180x_defines.h`:
- VPSS max groups: `VPSS_MAX_GRP_NUM = 16`
- VPSS max image size: `VPSS_MAX_IMAGE_WIDTH = 2880`, `VPSS_MAX_IMAGE_HEIGHT = 4096`
- VPSS scaling ratio: `VPSS_MAX_ZOOMIN = 32`, `VPSS_MAX_ZOOMOUT = 32`

## Supported Pixel Formats (PIXEL_FORMAT_E)

From `cvi_comm_video.h`:

**RGB/BGR**:
- `PIXEL_FORMAT_RGB_888`, `PIXEL_FORMAT_BGR_888`
- `PIXEL_FORMAT_RGB_888_PLANAR`, `PIXEL_FORMAT_BGR_888_PLANAR`

**ARGB**:
- `PIXEL_FORMAT_ARGB_1555`, `PIXEL_FORMAT_ARGB_4444`, `PIXEL_FORMAT_ARGB_8888`

**Bayer (RAW)**:
- `PIXEL_FORMAT_RGB_BAYER_8BPP`, `PIXEL_FORMAT_RGB_BAYER_10BPP`
- `PIXEL_FORMAT_RGB_BAYER_12BPP`, `PIXEL_FORMAT_RGB_BAYER_14BPP`, `PIXEL_FORMAT_RGB_BAYER_16BPP`

**YUV Planar**:
- `PIXEL_FORMAT_YUV_PLANAR_422`, `PIXEL_FORMAT_YUV_PLANAR_420`
- `PIXEL_FORMAT_YUV_PLANAR_444`, `PIXEL_FORMAT_YUV_400`

**YUV Semi-Planar**:
- `PIXEL_FORMAT_NV12`, `PIXEL_FORMAT_NV21`
- `PIXEL_FORMAT_NV16`, `PIXEL_FORMAT_NV61`

**YUV Packed**:
- `PIXEL_FORMAT_YUYV`, `PIXEL_FORMAT_UYVY`, `PIXEL_FORMAT_YVYU`, `PIXEL_FORMAT_VYUY`

**HSV**:
- `PIXEL_FORMAT_HSV_888`, `PIXEL_FORMAT_HSV_888_PLANAR`

**Deep Learning**:
- `PIXEL_FORMAT_FP32_C1`, `PIXEL_FORMAT_FP32_C3_PLANAR`
- `PIXEL_FORMAT_INT32_C1`, `PIXEL_FORMAT_INT32_C3_PLANAR`
- `PIXEL_FORMAT_UINT32_C1`, `PIXEL_FORMAT_UINT32_C3_PLANAR`
- `PIXEL_FORMAT_BF16_C1`, `PIXEL_FORMAT_BF16_C3_PLANAR`
- `PIXEL_FORMAT_INT16_C1`, `PIXEL_FORMAT_INT16_C3_PLANAR`
- `PIXEL_FORMAT_UINT16_C1`, `PIXEL_FORMAT_UINT16_C3_PLANAR`
- `PIXEL_FORMAT_INT8_C1`, `PIXEL_FORMAT_INT8_C3_PLANAR`
- `PIXEL_FORMAT_UINT8_C1`, `PIXEL_FORMAT_UINT8_C3_PLANAR`

**Other enum values**:
- `PIXEL_FORMAT_8BIT_MODE` (mode flag)
- `PIXEL_FORMAT_MAX` (sentinel)

**Note**: Each module supports a subset of formats. Verify per-module constraints in `vi.md`, `vpss.md`, `venc.md`, and `vdec.md`.

## Alignment and Stride

- Alignment rules vary by module and pixel format.
- Use VB helpers (`COMMON_GetPicBufferConfig` / `COMMON_GetPicBufferSize`) for exact block sizing.
- VPSS channel alignment can be queried or set via `CVI_VPSS_GetChnAlign` / `CVI_VPSS_SetChnAlign`.

See `vb.md` for alignment examples and buffer sizing guidance.
