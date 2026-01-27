# SYS (System Control) Module Reference

## Overview

SYS module provides system-level control for media processing:
- **Module Binding** - Connect modules for automatic data flow
- **Memory Management** - ION memory allocation for zero-copy
- **System Configuration** - VI/VPSS working modes
- **DMA Operations** - Fast memory copy

## Essential APIs

### 1. System Initialization and Cleanup

- `CVI_SYS_Init()` - Initialize MMF system (must call first)
- `CVI_SYS_Exit()` - Cleanup MMF system (call before exit)
- `CVI_SYS_IsInited()` - Check if system is initialized
- **Note**: Must call `CVI_VB_Init()` **before** `CVI_SYS_Init()`

### 2. Module Binding Management

- `CVI_SYS_Bind()` - Bind source module to destination module
- `CVI_SYS_UnBind()` - Unbind modules
- `CVI_SYS_GetBindbyDest()` - Query source bound to destination
- `CVI_SYS_GetBindbySrc()` - Query destination bound to source

**Supported Binding Paths**:
```
Data Source      →  Data Receiver
─────────────────────────────────
VI               →  VPSS, VENC, VO
VDEC             →  VPSS → VENC, VO
Audio Input      →  AENC
Audio Output     →  ADEC
```

### 3. Working Mode Configuration

- `CVI_SYS_SetVIVPSSMode()` - Set VI-VPSS working mode
- `CVI_SYS_GetVIVPSSMode()` - Get VI-VPSS mode
- `CVI_SYS_SetVPSSMode()` - Set VPSS working mode (SINGLE/DUAL/RGNEX)
- `CVI_SYS_GetVPSSMode()` - Get VPSS mode
- `CVI_SYS_SetVPSSModeEx()` - Set extended VPSS mode
- `CVI_SYS_GetVPSSModeEx()` - Get extended VPSS mode

### 4. VI Device Management

- `CVI_SYS_VI_Open()` - Open VI device
- `CVI_SYS_VI_Close()` - Close VI device

### 5. ION Memory Management

- `CVI_SYS_IonAlloc()` - Allocate ION memory (non-cached)
- `CVI_SYS_IonAlloc_Cached()` - Allocate cached ION memory
- `CVI_SYS_IonFree()` - Free ION memory
- `CVI_SYS_IonFlushCache()` - Flush cache to memory and invalidate
- `CVI_SYS_IonInvalidateCache()` - Invalidate cache from memory
- `CVI_SYS_IonGetFd()` - Get ION file descriptor

### 6. Memory Mapping

- `CVI_SYS_Mmap()` - Map physical address to virtual (non-cached)
- `CVI_SYS_MmapCache()` - Map physical address (cached)
- `CVI_SYS_Munmap()` - Unmap memory

### 7. TPU DMA Operations

- `CVI_SYS_TDMACopy()` - 1D DMA copy via TPU
- `CVI_SYS_TDMACopy2D()` - 2D DMA copy with stride via TPU

### 8. System Information Query

- `CVI_SYS_GetVersion()` - Get MMF version
- `CVI_SYS_GetChipId()` - Get chip ID (CV1800/CV1810/CV1811/CV1812/CV1813, etc.)
- `CVI_SYS_GetChipVersion()` - Get chip version
- `CVI_SYS_GetModName()` - Get module name string
- `CVI_SYS_GetPowerOnReason()` - Get power-on reason
- `CVI_SYS_GetCurPTS()` - Get current timestamp

### 9. Temperature Monitoring

- `CVI_SYS_RegisterThermalCallback()` - Register thermal callback for temperature control
- `CVI_SYS_StartThermalThread()` - Start temperature monitoring (not supported in dual-OS SDK)
- `CVI_SYS_StopThermalThread()` - Stop temperature monitoring

### 10. Debug Tracing

- `CVI_SYS_TraceBegin()` - Begin debug tracing
- `CVI_SYS_TraceEnd()` - End debug tracing
- `CVI_SYS_TraceCounter()` - Record counter value during trace

### 11. Dual-OS Communication (dual-OS SDK only)

- `CVI_MSG_Init()` - Initialize dual-core message communication
- `CVI_MSG_Deinit()` - Deinitialize dual-core communication

## Common Workflows

### System Initialization Pattern

```c
// Initialize system
CVI_SYS_Init();

// Setup modules (VI, VPSS, VENC, etc.)
// ...

// Bind modules
MMF_CHN_S stSrcChn = {.enModId = CVI_ID_VI, .s32DevId = 0, .s32ChnId = 0};
MMF_CHN_S stDestChn = {.enModId = CVI_ID_VPSS, .s32DevId = 0, .s32ChnId = 0};
CVI_SYS_Bind(&stSrcChn, &stDestChn);

// Processing happens automatically via binding
// ...

// Cleanup
CVI_SYS_UnBind(&stSrcChn, &stDestChn);
CVI_SYS_Exit();
```

### ION Memory Pattern

```c
// Allocate ION memory
CVI_U64 paddr;
void *vaddr = CVI_SYS_IonAlloc(&paddr, size);

// Use memory for DMA/hardware operations
// ...

// Free ION memory
CVI_SYS_IonFree(paddr, vaddr);
```

### Module Binding Examples

**Example 1: VI → VPSS → VENC (Video encoding pipeline)**
```c
MMF_CHN_S vi_chn = {CVI_ID_VI, 0, 0};
MMF_CHN_S vpss_chn = {CVI_ID_VPSS, 0, 0};
MMF_CHN_S venc_chn = {CVI_ID_VENC, 0, 0};

CVI_SYS_Bind(&vi_chn, &vpss_chn);     // VI feeds VPSS
CVI_SYS_Bind(&vpss_chn, &venc_chn);   // VPSS feeds VENC
```

**Example 2: VI → VO (Direct display)**
```c
MMF_CHN_S vi_chn = {CVI_ID_VI, 0, 0};
MMF_CHN_S vo_chn = {CVI_ID_VO, 0, 0};

CVI_SYS_Bind(&vi_chn, &vo_chn);       // VI directly to VO
```

**Example 3: Multi-channel encoding**
```c
MMF_CHN_S vpss_chn0 = {CVI_ID_VPSS, 0, 0};  // 1080p
MMF_CHN_S vpss_chn1 = {CVI_ID_VPSS, 0, 1};  // 720p
MMF_CHN_S venc_chn0 = {CVI_ID_VENC, 0, 0};
MMF_CHN_S venc_chn1 = {CVI_ID_VENC, 0, 1};

CVI_SYS_Bind(&vpss_chn0, &venc_chn0);
CVI_SYS_Bind(&vpss_chn1, &venc_chn1);
```

## Key Structures

- `MMF_CHN_S` - Module channel identifier
  - `enModId` - Module ID (CVI_ID_VI, CVI_ID_VPSS, CVI_ID_VENC, CVI_ID_VO)
  - `s32DevId` - Device ID
  - `s32ChnId` - Channel ID
- `VI_VPSS_MODE_E` - VI-VPSS working mode enumeration
- `VPSS_MODE_E` - VPSS working mode enumeration

## VI/VPSS Working Modes

### Four VI-VPSS Working Modes

VI PIPE can be configured in 4 different modes that determine how data flows between VI and VPSS:

#### 1. VI_OFFLINE_VPSS_OFFLINE

**Data Flow**:
- **VI**: VI_CAP writes RAW to memory, VI_PROC reads from memory
- **VPSS**: VI_PROC writes YUV to memory, VPSS reads from memory

**Supported Features**:
- ✅ Group clipping
- ✅ Zoom
- ✅ Channel clipping

**Use Case**: Maximum flexibility, supports all features but has highest latency

#### 2. VI_OFFLINE_VPSS_ONLINE

**Data Flow**:
- **VI**: VI_CAP writes RAW to memory, VI_PROC reads from memory
- **VPSS**: VI_PROC directly sends data stream to VPSS (does NOT write YUV to memory)

**Supported Features**:
- ❌ Group clipping (NOT supported)
- ✅ Zoom
- ✅ Channel clipping

**Use Case**: Lower latency than full offline, but sacrifices group clipping

#### 3. VI_ONLINE_VPSS_OFFLINE

**Data Flow**:
- **VI**: VI_CAP directly sends data stream to VI_PROC (does NOT write RAW to memory)
- **VPSS**: VI_PROC writes YUV to memory, VPSS reads from memory

**Supported Features**:
- ✅ Group clipping
- ✅ Zoom
- ✅ Channel clipping

**Use Case**: Reduced memory bandwidth for RAW data, maintains most features

#### 4. VI_ONLINE_VPSS_ONLINE

**Data Flow**:
- **VI**: VI_CAP directly sends data stream to VI_PROC
- **VPSS**: VI_PROC directly sends data stream to VPSS

**Supported Features**:
- ❌ Group clipping (NOT supported)
- ✅ Zoom
- ✅ Channel clipping

**Use Case**: Lowest latency, zero memory copy, but limited features

### Important Limitations

- **VPSS ONLINE mode**: Can only receive data from **maximum 2** front-end sensors
- **PIPES marked "-"**: Cannot operate independently, must perform HDR together with previous PIPE
- **Feature trade-off**: ONLINE modes sacrifice group clipping for lower latency

### VPSS Working Modes

**VPSS_MODE_E** - VPSS operating modes:

- **VPSS_MODE_SINGLE** - Single mode (default, one input)
- **VPSS_MODE_DUAL** - Dual mode (two inputs for stitching or PIP)
- **VPSS_MODE_RGNEX** - RGN expansion mode

**Configuration Requirements**:
- Must be set **after** `CVI_SYS_Init()` and **before** creating any VPSS groups
- Use `CVI_SYS_SetVPSSMode()` to configure
- Use `CVI_SYS_GetVPSSMode()` to query current mode

## Binding and Input Mode Matrix

Binding needs to match the VPSS input type and source. Use one strategy consistently.

Text table:

| Source | VPSS Input | Data Path | Binding | SendFrame |
| --- | --- | --- | --- | --- |
| VI (any VI_VPSS mode) | ISP | VI->ISP->VPSS (direct or via memory) | Recommended | Not used |
| VDEC | MEM | VDEC->VPSS | Supported | Optional |
| User/CPU | MEM | User->VPSS | Not used | Required |

**Notes**:
- If VPSS input is ISP, bind VI to VPSS for explicit ownership and easier debug.
- If VPSS input is MEM, do not bind VI; use SendFrame or bind VDEC.
- A VPSS group cannot switch input types after start.

## Memory Management Notes

### ION vs VB (Video Buffer)
- **ION**: General-purpose physical memory allocation (for custom buffers)
- **VB**: Video buffer pool (for automatic frame management in VI/VPSS/VENC)
 - **See also**: `ion.md` for cache coherency and ION-to-VB integration.

### Cache Considerations
- Use **non-cached** for hardware DMA (faster hardware access)
- Use **cached** for CPU-intensive operations (faster CPU access)
- Always flush cache after CPU writes to cached memory
- Always invalidate cache before CPU reads from cached memory

## Header Files

- `/cvi_mpi/include/cvi_sys.h` - Main SYS API
- `/cvi_mpi/include/linux/cvi_comm_sys.h` - SYS common definitions
- `/cvi_mpi/include/linux/cvi_defines.h` - Module ID definitions

## Related Modules

- **VB**: Video buffer pool (automatic memory management for media modules)
- **VI/VPSS/VENC/VO**: Media processing modules

**See also**: `integration-guide.md` for cross-module design and triage.

## All Modules Managed by SYS (MOD_ID_E)

SYS provides unified management for 39 module types:

**Video Modules**:
- **VI** (Video Input) - Camera sensor capture, ISP pipeline
- **VPSS** (Video Process Sub-System) - Video post-processing
- **VPSSF** (VPSS Frontend) - VPSS frontend module
- **VDEC** (Video Decoder) - JPEG/MJPEG/H.264 decoding
- **VENC** (Video Encoder) - H.264/H.265/JPEG/MJPEG encoding
- **H264E** (H.264 Encoder) - H.264 encoding
- **H264D** (H.264 Decoder) - H.264 decoding
- **H265E** (H.265 Encoder) - H.265 encoding
- **H265D** (H.265 Decoder) - H.265 decoding
- **JPEGE** (JPEG Encoder) - JPEG/MJPEG encoding
- **JPEGD** (JPEG Decoder) - JPEG/MJPEG decoding
- **VO** (Video Output) - Display output (CV181X only, CV180X not supported)

**Audio Modules**:
- **AIO** (Audio I/O) - Audio input/output
- **AI** (Audio Input) - Audio capture
- **AO** (Audio Output) - Audio playback
- **AENC** (Audio Encoder) - Audio encoding
- **ADEC** (Audio Decoder) - Audio decoding
- **AUD** (Audio) - Audio processing

**Image Processing**:
- **ISP** (Image Signal Processor) - Low-level image tuning (AE/AWB/AF)
- **GDC** (Geometric Distortion Correction) - Lens correction, rotation
- **DIS** (Digital Image Stabilization) - Image stabilization
- **RC** (Rate Control) - Bitrate control

**System Modules**:
- **VB** (Video Buffer) - Video buffer pool management
- **SYS** (System) - System control and initialization
- **RGN** (Region) - OSD/Region management (also called REGION)
- **VPU** (Video Process Unit) - Video processing unit
- **TPU** (Tensor Processing Unit) - AI inference acceleration
- **LOG** (Log) - Logging system
- **IVE** (Intelligent Video Engine) - Intelligent video analysis

**Other Modules**:
- **USER** - User-defined modules
- **PROC** - Process management
- **PHOTO** - Photo capture
- **FB** (Frame Buffer) - Frame buffer for display
- **CHNL** (Channel) - Channel management
- **CMPI** (Common MPI) - Common MPI interfaces

**Note**: This is the complete MOD_ID_E enumeration. Not all modules may be available on all platforms (e.g., CV180X does not support VO or H.264 decoding).

## Dual-OS Communication (dual-OS SDK only)

In dual-OS SDK environments (e.g., Linux + RTOS), communication between cores is required:

**Initialization Requirements**:
- **CVI_MSG_Init()** - Must be called at the beginning to initialize dual-core message communication
- **CVI_MSG_Deinit()** - Call when shutting down to deinitialize communication

**Important Notes**:
- Only after establishing communication with the small core can subsequent APIs be called
- This is specific to dual-OS SDK configurations
- Single-OS SDK does not require this initialization

**Example**:
```c
// In dual-OS environment, initialize communication first
CVI_MSG_Init();

// Now proceed with normal initialization
CVI_VB_Init();
CVI_SYS_Init();
// ... rest of initialization

// Cleanup
CVI_SYS_Exit();
CVI_VB_Exit();
CVI_MSG_Deinit();
```

## Temperature Monitoring

SYS provides thermal management for temperature control:

**APIs**:
- **CVI_SYS_RegisterThermalCallback()** - Register callback for thermal events
  - Used for reducing frame rate when temperature is too high
  - Allows dynamic performance adjustment based on thermal state
- **CVI_SYS_StartThermalThread()** - Start temperature monitoring thread
  - **NOT supported** in dual-OS SDK
- **CVI_SYS_StopThermalThread()** - Stop temperature monitoring

**Use Case**:
- Prevent overheating in enclosed environments
- Dynamic performance scaling based on temperature
- Thermal protection for industrial applications

## Notes

- Always call `CVI_SYS_Init()` before any media module operations
- Always call `CVI_SYS_Exit()` when shutting down
- **CRITICAL**: Binding must be established AFTER modules are configured and **started**
  - For VI: after `CVI_VI_EnableChn()`
  - For VPSS: after `CVI_VPSS_StartGrp()`
- Unbinding must be done BEFORE modules are stopped
- ION memory is for custom usage; most media modules use VB pools automatically
- Use `CVI_SYS_TDMACopy()` for fast memory-to-memory copy instead of memcpy
 - For minimal binding sequences, see `binding-cookbook.md`.

## Binding Parameter Rules (from official documentation)

**When VPSS is the destination (receiver)**:
```c
stDestChn.enModId = CVI_ID_VPSS;
stDestChn.s32DevId = VpssGrp;   // VPSS Group ID
stDestChn.s32ChnId = 0;         // MUST be 0 (group receives, not channel)
```

**When VPSS is the source (sender)**:
```c
stSrcChn.enModId = CVI_ID_VPSS;
stSrcChn.s32DevId = VpssGrp;    // VPSS Group ID
stSrcChn.s32ChnId = VpssChn;    // Output channel ID
```

**Verify binding success**:
```bash
cat /proc/cvitek/sys | grep -A 10 "BIND RELATION"
# Empty table = binding failed silently
```
