# GDC (Geometric Distortion Correction) Module Reference

## Overview

GDC (Geometric Distortion Correction) module provides hardware-accelerated image warping and correction capabilities:
- **LDC (Lens Distortion Correction)**: Correct wide-angle lens barrel/pincushion distortion
- **Rotation**: Arbitrary angle rotation with high quality
- **Perspective Correction**: Correct perspective distortion (keystone correction)
- **Fisheye Unwarp**: Convert fisheye images to rectilinear view

## Core Concepts

### GDC Processing Model

GDC operates on a job-based model:
```
Create Job → Add Tasks → Begin Job → Process → End Job
```

**Task Types**:
1. **LDC Task**: Lens distortion correction (barrel/pincushion)
2. **Rotation Task**: Rotate image by arbitrary angle
3. **Custom Mesh Task**: Apply custom geometric transformation

### Mesh-Based Warping

GDC uses a **mesh (lookup table)** to define the transformation:
- Input image divided into grid
- Each grid point mapped to output coordinate
- Hardware performs bilinear interpolation

```
Input Grid        Mesh Mapping      Output Image
+-+-+-+-+         Transform LUT     Corrected/Rotated
| | | | |    →    (X, Y coords) →   Result
+-+-+-+-+
| | | | |
+-+-+-+-+
```

## Essential APIs

### Job Management

- `CVI_GDC_BeginJob()` - Create and start a GDC job
- `CVI_GDC_EndJob()` - Execute job and wait for completion
- `CVI_GDC_CancelJob()` - Cancel pending job

### Task Operations

- `CVI_GDC_AddLDCTask()` - Add lens distortion correction task
- `CVI_GDC_AddRotationTask()` - Add rotation task
- `CVI_GDC_LoadMesh()` - Load custom transformation mesh
- `CVI_GDC_LoadMeshWithBuf()` - Load mesh from buffer
- `CVI_GDC_LoadLDCMesh()` - Load pre-computed LDC mesh

### Mesh Utilities

- `CVI_GDC_DumpMesh()` - Export mesh to file (for debugging)
- `CVI_GDC_GenLDCMesh()` - Generate LDC mesh from parameters (helper)

### Advanced

- `CVI_GDC_SetBufWrapAttr()` - Set buffer wrap mode
- `CVI_GDC_GetBufWrapAttr()` - Get buffer wrap configuration

### MESH Management Structures

GDC provides structures for managing mesh tables and attaching them to VI/VPSS channels:

- **MESH_DUMP_ATTR_S** - Mesh dump attributes for import/export
- **VI_MESH_ATTR_S** - VI channel mesh attachment
- **VPSS_MESH_ATTR_S** - VPSS channel mesh attachment

#### MESH_DUMP_ATTR_S Structure

```c
typedef struct _MESH_DUMP_ATTR_S {
    CVI_CHAR binFileName[128];  // Mesh binary file path
    MOD_ID_E enModId;            // Module ID (MOD_ID_VI or MOD_ID_VPSS)
    union {
        VI_MESH_ATTR_S viMeshAttr;      // VI mesh attributes
        VPSS_MESH_ATTR_S vpssMeshAttr;  // VPSS mesh attributes
    };
} MESH_DUMP_ATTR_S;
```

#### VI_MESH_ATTR_S and VPSS_MESH_ATTR_S

```c
// VI mesh attachment
typedef struct _VI_MESH_ATTR_S {
    VI_CHN chn;  // VI channel to attach mesh
} VI_MESH_ATTR_S;

// VPSS mesh attachment
typedef struct _VPSS_MESH_ATTR_S {
    VPSS_GRP grp;  // VPSS group
    VPSS_CHN chn;  // VPSS channel
} VPSS_MESH_ATTR_S;
```

#### Mesh Import/Export Workflow

```c
// Export mesh from calibration to file
MESH_DUMP_ATTR_S dump_attr = {
    .binFileName = "/tmp/fisheye_mesh.bin",
    .enModId = MOD_ID_VPSS,
    .vpssMeshAttr = {
        .grp = 0,
        .chn = 0
    }
};

// Dump mesh to file (after calibration)
CVI_GDC_DumpMesh(&dump_attr);

// Later: Import mesh file and attach to VI/VPSS
MESH_DUMP_ATTR_S import_attr = {
    .binFileName = "/tmp/fisheye_mesh.bin",
    .enModId = MOD_ID_VI,
    .viMeshAttr = {
        .chn = 0  // Attach to VI channel 0
    }
};

// Load and attach mesh
CVI_GDC_LoadMeshWithFile(&import_attr);
```

#### Use Cases for MESH Management

- **Fisheye dewarp calibration**: Generate mesh offline, import at runtime
- **Lens distortion correction**: Export calibrated mesh for multiple devices
- **Custom transformations**: Import externally generated mesh tables
- **Mesh versioning**: Save/load different mesh profiles for different scenarios

## Common Workflows

### 1. Lens Distortion Correction (LDC)

Used to correct barrel or pincushion distortion from wide-angle lenses.

```c
// Input/output frame info
VIDEO_FRAME_INFO_S stSrcFrame;  // Input frame (distorted)
VIDEO_FRAME_INFO_S stDstFrame;  // Output frame (corrected)

// Get input frame from VI or VPSS
CVI_VPSS_GetChnFrame(VpssGrp, VpssChn, &stSrcFrame, 1000);

// Prepare output frame buffer
// (Allocate from VB pool with same resolution)
VB_BLK blk = CVI_VB_GetBlock(VB_INVALID_POOLID, frameSize, CVI_ID_USER);
// ... setup stDstFrame with VB block ...

// Begin GDC job
GDC_HANDLE hHandle;
CVI_GDC_BeginJob(&hHandle);

// Add LDC task
GDC_TASK_ATTR_S stTask;
memset(&stTask, 0, sizeof(GDC_TASK_ATTR_S));

stTask.stImgIn = stSrcFrame;   // Input frame
stTask.stImgOut = stDstFrame;  // Output frame

// LDC parameters
FISHEYE_ATTR_S stLDCAttr;
stLDCAttr.bEnable = CVI_TRUE;
stLDCAttr.bBgColor = CVI_TRUE;
stLDCAttr.u32BgColor = 0x000000;  // Black background for unmapped areas
stLDCAttr.s32HorOffset = 0;       // Horizontal offset
stLDCAttr.s32VerOffset = 0;       // Vertical offset
stLDCAttr.u32TrapezoidCoef = 0;   // Trapezoid correction (0 = disabled)
stLDCAttr.s32FanStrength = 50;    // Fan strength (0-100, for barrel correction)
stLDCAttr.enMountMode = FISHEYE_DESKTOP_MOUNT;  // Camera mount mode

CVI_GDC_AddLDCTask(hHandle, &stTask, &stLDCAttr);

// Execute job
CVI_GDC_EndJob(hHandle);

// stDstFrame now contains corrected image

// Release frames
CVI_VPSS_ReleaseChnFrame(VpssGrp, VpssChn, &stSrcFrame);
CVI_VB_ReleaseBlock(blk);
```

### 2. Image Rotation (Arbitrary Angle)

Rotate image by any angle (not limited to 90° increments).

```c
// Begin job
GDC_HANDLE hHandle;
CVI_GDC_BeginJob(&hHandle);

// Setup task
GDC_TASK_ATTR_S stTask;
stTask.stImgIn = stSrcFrame;
stTask.stImgOut = stDstFrame;

// Rotation parameters
ROTATION_ATTR_S stRotationAttr;
stRotationAttr.s32Angle = 45;  // 45 degrees clockwise
stRotationAttr.enYuvDataFmt = DATA_BITWIDTH_8;
stRotationAttr.stDstSize.u32Width = dstWidth;
stRotationAttr.stDstSize.u32Height = dstHeight;

CVI_GDC_AddRotationTask(hHandle, &stTask, &stRotationAttr);

// Execute
CVI_GDC_EndJob(hHandle);
```

### 3. Fisheye Dewarp (180° → Rectilinear)

Convert fisheye camera image to normal rectilinear view.

```c
// Similar to LDC, but with fisheye-specific parameters
FISHEYE_ATTR_S stFisheyeAttr;
stFisheyeAttr.bEnable = CVI_TRUE;
stFisheyeAttr.bBgColor = CVI_TRUE;
stFisheyeAttr.u32BgColor = 0x000000;

// Fisheye specific
stFisheyeAttr.enMountMode = FISHEYE_CEILING_MOUNT;  // Ceiling mount
stFisheyeAttr.u32RegionNum = 4;  // Split into 4 regions (quad view)

// Define regions (e.g., 4-way split for 360° coverage)
for (int i = 0; i < 4; i++) {
    stFisheyeAttr.astFishEyeRegionAttr[i].enViewMode = FISHEYE_VIEW_NORMAL;
    stFisheyeAttr.astFishEyeRegionAttr[i].u32InRadius = 500;
    stFisheyeAttr.astFishEyeRegionAttr[i].u32OutRadius = 1000;
    stFisheyeAttr.astFishEyeRegionAttr[i].u32Pan = i * 90;  // 0°, 90°, 180°, 270°
    stFisheyeAttr.astFishEyeRegionAttr[i].u32Tilt = 0;
    stFisheyeAttr.astFishEyeRegionAttr[i].u32HorZoom = 100;
    stFisheyeAttr.astFishEyeRegionAttr[i].u32VerZoom = 100;
    stFisheyeAttr.astFishEyeRegionAttr[i].stOutRect = region_rects[i];
}

CVI_GDC_AddLDCTask(hHandle, &stTask, &stFisheyeAttr);
CVI_GDC_EndJob(hHandle);
```

### 4. Custom Mesh Transformation

Apply pre-computed or custom transformation mesh.

```c
// Load custom mesh
GDC_FISHEYE_POINT_2D_S *pMesh;  // Mesh data: array of (x, y) points
CVI_U32 meshSize;

// Calculate mesh size
meshSize = meshWidth * meshHeight * sizeof(GDC_FISHEYE_POINT_2D_S);

// Allocate mesh buffer
pMesh = (GDC_FISHEYE_POINT_2D_S *)malloc(meshSize);

// Fill mesh with transformation data
// pMesh[i].x = output_x_coordinate
// pMesh[i].y = output_y_coordinate
for (int i = 0; i < meshWidth * meshHeight; i++) {
    pMesh[i].x = /* calculated x */;
    pMesh[i].y = /* calculated y */;
}

// Load mesh
CVI_GDC_LoadMeshWithBuf(hHandle, pMesh, meshSize);

// Add task (will use loaded mesh)
GDC_TASK_ATTR_S stTask;
stTask.stImgIn = stSrcFrame;
stTask.stImgOut = stDstFrame;

CVI_GDC_AddTask(hHandle, &stTask);

// Execute
CVI_GDC_EndJob(hHandle);

free(pMesh);
```

## Use Cases

### 1. Surveillance Camera with Wide-Angle Lens

**Problem**: Barrel distortion on edges
**Solution**: LDC with positive fan strength

```c
stLDCAttr.s32FanStrength = 50;  // Correct barrel distortion
```

### 2. Document Scanner with Perspective Distortion

**Problem**: Skewed document due to camera angle
**Solution**: Perspective correction using custom mesh or trapezoid coefficient

```c
stLDCAttr.u32TrapezoidCoef = 30;  // Correct trapezoidal distortion
```

### 3. 360° Panorama Camera

**Problem**: Fisheye lens creates circular image
**Solution**: Fisheye dewarp to multiple rectilinear views

```c
stFisheyeAttr.u32RegionNum = 4;  // 4 directional views
stFisheyeAttr.enMountMode = FISHEYE_CEILING_MOUNT;
```

### 4. Rotating Camera Feed

**Problem**: Camera mounted at odd angle
**Solution**: GDC rotation task

```c
stRotationAttr.s32Angle = 30;  // Rotate 30° to level horizon
```

## Performance Considerations

### Hardware Acceleration

- GDC is **hardware-accelerated** - very efficient
- Can process 1080p @ 30fps with minimal CPU usage
- Multiple jobs can be queued

### Mesh Size and Memory

- Larger mesh = higher quality but more memory
- Typical mesh: 65×65 to 129×129 grid points
- Mesh memory ≈ meshWidth × meshHeight × 8 bytes

### Processing Time

- **LDC**: ~5-10ms for 1080p
- **Rotation**: ~5-10ms for 1080p
- **Custom Mesh**: Depends on mesh complexity

**Optimization**:
- Pre-compute and cache meshes when possible
- Use `CVI_GDC_LoadLDCMesh()` for reusable LDC parameters
- Batch multiple tasks in one job when possible

## Integration with Media Pipeline

### Option 1: Offline Processing (Manual)

```
VI → GetFrame → GDC → VPSS/VENC
```

Use when:
- Need full control over GDC parameters per frame
- Processing specific frames (not continuous)
- Dynamic corrections based on scene

### Option 2: Integrated in VI/VPSS

Some platforms support LDC directly in VI or VPSS:

```c
// VI LDC (if supported)
CVI_VI_SetChnLDCAttr(ViPipe, ViChn, &stLDCAttr);

// VPSS LDC (if supported)
CVI_VPSS_SetChnLDCAttr(VpssGrp, VpssChn, &stLDCAttr);
```

Check platform documentation for integrated LDC support.

### Option 3: Pre-Processing Pipeline

```
VI → GDC (offline) → VPSS → VENC/VO
```

Apply GDC before entering main processing pipeline for consistent correction.

## Key Structures

- `GDC_TASK_ATTR_S` - Task configuration (input/output frames)
- `FISHEYE_ATTR_S` - LDC and fisheye parameters
- `ROTATION_ATTR_S` - Rotation parameters
- `GDC_FISHEYE_POINT_2D_S` - Mesh point (x, y coordinates)

## Error Handling with CancelJob

**Use Case**: Cancel a GDC job when an error occurs during task preparation.

**CancelJob vs EndJob**:
- **EndJob**: Submit job to hardware and wait for completion
- **CancelJob**: Abort job without submitting (use when error occurs before EndJob)

### Error Handling Pattern

```c
GDC_HANDLE hHandle;
CVI_S32 ret;

// Begin job
ret = CVI_GDC_BeginJob(&hHandle);
if (ret != CVI_SUCCESS) {
    printf("Failed to begin GDC job: 0x%x\n", ret);
    return -1;
}

// Add tasks
ret = CVI_GDC_AddLDCTask(hHandle, &stSrcFrame, &stDstFrame, &stLdcAttr);
if (ret != CVI_SUCCESS) {
    printf("Failed to add LDC task: 0x%x\n", ret);
    CVI_GDC_CancelJob(hHandle);  // ← Cancel instead of EndJob
    return -1;
}

// Verify output buffer is valid
if (stDstFrame.stVFrame.pu8VirAddr[0] == NULL) {
    printf("Invalid output buffer\n");
    CVI_GDC_CancelJob(hHandle);  // ← Cancel job
    return -1;
}

// All checks passed - execute job
ret = CVI_GDC_EndJob(hHandle);
if (ret != CVI_SUCCESS) {
    printf("GDC job execution failed: 0x%x\n", ret);
    // Note: Job already submitted, cannot cancel at this point
    return -1;
}

printf("GDC job completed successfully\n");
```

### When to Use CancelJob

- **Task preparation fails**: After BeginJob, if AddLDCTask/AddRotationTask fails
- **Invalid parameters**: If output buffer allocation fails or validation fails
- **Resource constraints**: If you detect resource exhaustion before submitting job
- **Early termination**: If application needs to abort processing before submission

### When NOT to Use CancelJob

- **After EndJob**: Once job is submitted, CancelJob has no effect
- **Normal completion**: Use EndJob for successful jobs
- **Already executing**: Cannot cancel jobs already being processed by hardware

### Cleanup Pattern

```c
GDC_HANDLE hHandle;
CVI_S32 ret = CVI_SUCCESS;

ret = CVI_GDC_BeginJob(&hHandle);
if (ret == CVI_SUCCESS) {
    ret = CVI_GDC_AddLDCTask(hHandle, ...);
    if (ret == CVI_SUCCESS) {
        ret = CVI_GDC_AddRotationTask(hHandle, ...);
    }
}

if (ret == CVI_SUCCESS) {
    // All tasks added successfully - execute
    CVI_GDC_EndJob(hHandle);
} else {
    // Error occurred - cancel
    CVI_GDC_CancelJob(hHandle);
}
```

## Header Files

- `/cvi_mpi/include/cvi_gdc.h` - Main GDC API
- `/cvi_mpi/include/linux/cvi_comm_gdc.h` - GDC common definitions

## Related Modules

- **VI/VPSS**: May have integrated LDC support
- **VB**: Buffer management for GDC input/output frames

**See also**: `integration-guide.md` for cross-module design and triage.

## Notes

- GDC is **job-based**: Must use BeginJob/EndJob pattern
- Multiple tasks can be added to one job for batching
- Input and output frames must be in VB pool or ION memory
- Unmapped areas (due to correction) are filled with background color
- GDC operates on YUV format (supports YUV420/YUV422)
- For real-time correction, consider using VI/VPSS integrated LDC instead of GDC module
- Mesh generation can be done offline with calibration tools

## Debugging

### Check GDC Status

```bash
# View GDC processing status
cat /proc/cvitek/gdc
```

### Common Issues

**Issue**: Black areas in output
- **Cause**: Distortion correction leaves unmapped regions
- **Solution**: Adjust `u32BgColor` or crop output to valid region

**Issue**: Poor quality output
- **Cause**: Mesh resolution too coarse
- **Solution**: Increase mesh grid size (e.g., 65×65 → 129×129)

**Issue**: Processing too slow
- **Cause**: Inefficient mesh or large resolution
- **Solution**: Pre-compute mesh, reduce resolution, or use hardware LDC in VI/VPSS

**Issue**: Incorrect correction
- **Cause**: Wrong LDC parameters (fan strength, mount mode)
- **Solution**: Calibrate camera and adjust parameters incrementally

## Calibration Tips

1. **Capture calibration pattern**: Use checkerboard pattern
2. **Run calibration tool**: Use OpenCV or vendor-provided tools
3. **Extract distortion coefficients**: k1, k2, p1, p2
4. **Map to GDC parameters**: Convert to fan strength and other GDC parameters
5. **Test and iterate**: Adjust until straight lines appear straight in output
