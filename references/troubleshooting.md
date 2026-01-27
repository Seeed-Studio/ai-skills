# Troubleshooting Guide

This document provides systematic debugging procedures for common issues in CV181X/CV182X multimedia development.

## Error Code Reference

### VPSS Error Codes

| Error Code | Macro | Hex Value | Meaning | Common Causes |
|------------|-------|-----------|---------|---------------|
| CVI_ERR_VPSS_INVALID_DEVID | - | - | Invalid VPSS GROUP ID | Group ID out of range [0, VPSS_MAX_GRP_NUM) |
| CVI_ERR_VPSS_INVALID_CHNID | - | - | Invalid VPSS channel ID | Channel ID out of range [0, VPSS_MAX_CHN_NUM) |
| CVI_ERR_VPSS_ILLEGAL_PARAM | - | - | Invalid parameter | Null pointer or invalid attribute value |
| CVI_ERR_VPSS_EXIST | - | - | Group already exists | CreateGrp called twice without DestroyGrp |
| CVI_ERR_VPSS_UNEXIST | - | - | Group not created | Operation before CreateGrp |
| CVI_ERR_VPSS_NULL_PTR | - | - | Null pointer | Parameter is NULL |
| CVI_ERR_VPSS_NOT_SUPPORT | - | - | Operation not supported | Hardware limitation |
| CVI_ERR_VPSS_NOT_PERM | - | - | Operation not permitted | Wrong module state |
| CVI_ERR_VPSS_NOMEM | - | - | Memory allocation failed | System out of memory |
| **CVI_ERR_VPSS_NOBUF** | - | **0xc006800e** | **Buffer allocation failed** | **VB pool exhausted or not configured** |
| CVI_ERR_VPSS_BUF_EMPTY | - | - | Image queue empty | No frames available, check upstream |
| CVI_ERR_VPSS_NOTREADY | - | - | System not initialized | CVI_SYS_Init not called |
| CVI_ERR_VPSS_BUSY | - | - | System busy | Too many pending operations |

### VI Error Codes

| Error Code | Meaning | Common Causes |
|------------|---------|---------------|
| ERR_VI_FAILED_NOBUF | No buffer available | VB pool exhausted, check VB configuration |
| ERR_VI_FAILED_NOTCONFIG | Not configured | SetDevAttr/SetPipeAttr not called |
| ERR_VI_FAILED_NOTENABLE | Not enabled | EnableDev/EnableChn not called |

## Common Runtime Symptoms (Non-Module)

| Symptom | Likely Cause | Fix |
| --- | --- | --- |
| `/dev/cvi-*` permission denied | Missing sudo | Run with sudo; confirm device nodes exist. |
| First GetChnFrame fails (NOBUF) | ISP/VPSS not ready yet | Warm up and poll readiness; check RecvPic/RecvCnt. |

## VDEC JPEG Init Failures

**Symptoms**
- `CVI_VDEC_StartRecvStream` fails during JPEG decode init.
- `CVI_VDEC_AttachVbPool` fails when VDEC is configured for common VB.
- HW JPEG decode init fails even though channel creation succeeded.

**Likely Causes**
- Missing common VB pool sized for the JPEG output format and resolution (usually NV21).
- JPEG buffer sizing based on generic picture sizing instead of JPEG-aligned sizing.
- Attaching a VDEC pool while the module VB source is common (attach is only valid for user VB).
- VDEC channel max size larger than actual JPEG dimensions, inflating buffer demand.

**Resolution Checklist**
- Size JPEG output buffers with JPEG-aligned sizing (use the VDEC buffer sizing helpers).
- Align the stream buffer size to the SDK-required boundary (0x4000).
- Configure VDEC max width/height to the actual JPEG dimensions whenever possible.
- Ensure a common VB pool exists for the JPEG output size (add a dedicated 1280x720 NV21 pool when decoding 720p JPEG).
- Only attach VDEC VB pools when `enVdecVBSource` is user; use common pools otherwise.

### Common Error Pattern: 0xc006800e (ERR_VPSS_NOBUF)

**Symptom**: `CVI_VPSS_GetChnFrame` returns 0xc006800e

**Diagnostic Decision Tree**:

```
ERR_VPSS_NOBUF (0xc006800e)
    │
    ├─► Step 1: Check /proc/cvitek/sys binding table
    │   │
    │   └─► Binding table EMPTY?
    │       │
    │       ├─► YES → Binding failed silently
    │       │   ├─► Check: Were VI and VPSS started before Bind?
    │       │   ├─► Check: Is ViPipe/ViChn correct?
    │       │   └─► Check: Is VpssGrp correct?
    │       │
    │       └─► NO (binding exists) → Continue to Step 2
    │
    ├─► Step 2: Check /proc/cvitek/vpss status
    │   │
    │   └─► RecvCnt = 0?
    │       │
    │       ├─► YES → VPSS not receiving frames from VI
    │       │   └─► Check VI is outputting: /proc/cvitek/vi
    │       │
    │       └─► NO (RecvCnt > 0) → Continue to Step 3
    │
    ├─► Step 3: Check /proc/cvitek/vb buffer usage
    │   │
    │   └─► All buffers in use (Free = 0)?
    │       │
    │       ├─► YES → Buffer leak or insufficient pool size
    │       │   ├─► Increase VB pool blkCnt
    │       │   └─► Ensure ReleaseChnFrame is called
    │       │
    │       └─► NO → Check output channel configuration
    │
    └─► Step 4: Check VPSS channel depth (u32Depth)
        │
        └─► u32Depth = 0?
            │
            ├─► YES → Set depth to at least 1
            │
            └─► NO → Check pixel format mismatch
```

## Correct Initialization Sequence

### Complete VI → VPSS → Bind Sequence

Based on official SDK sample code (`sample_common_vpss.c`, `sample_vio.c`):

```
Phase 1: System Initialization
├─► CVI_VB_SetConfig()           // Configure VB pools (BEFORE Init)
├─► CVI_VB_Init()                // Initialize VB system
├─► CVI_SYS_Init()               // Initialize MMF system
├─► CVI_SYS_SetVIVPSSMode()      // Set VI-VPSS working mode (optional)
└─► CVI_SYS_SetVPSSModeEx()      // Set VPSS mode (optional)

Phase 2: VI Initialization (in order)
├─► CVI_VI_SetDevAttr()          // Configure device
├─► CVI_VI_EnableDev()           // Enable device
├─► CVI_VI_CreatePipe()          // Create ISP pipe
├─► CVI_VI_SetPipeAttr()         // Configure pipe
├─► CVI_VI_StartPipe()           // ★ Start pipe (REQUIRED before bind)
├─► CVI_VI_SetChnAttr()          // Configure channel
└─► CVI_VI_EnableChn()           // ★ Enable channel (REQUIRED before bind)

Phase 3: VPSS Initialization (in order - from sample_common_vpss.c)
├─► CVI_VPSS_CreateGrp()         // Create group
├─► CVI_VPSS_ResetGrp()          // Reset group (CRITICAL!)
├─► CVI_VPSS_SetChnAttr()        // Set channel attributes
├─► CVI_VPSS_EnableChn()         // ★ Enable channel FIRST
└─► CVI_VPSS_StartGrp()          // ★ Start group AFTER enable

Phase 4: Binding (AFTER both VI and VPSS are fully started)
└─► CVI_SYS_Bind(VI→VPSS)        // ★ Bind LAST
```

### VPSS Initialization Order Detail

**Official order from `SAMPLE_COMM_VPSS_Init` + `SAMPLE_COMM_VPSS_Start`**:

```c
// From SAMPLE_COMM_VPSS_Init():
CVI_VPSS_CreateGrp(VpssGrp, &grpAttr);    // 1. Create
CVI_VPSS_ResetGrp(VpssGrp);               // 2. Reset
CVI_VPSS_SetChnAttr(VpssGrp, VpssChn, &chnAttr);  // 3. Set attributes
CVI_VPSS_EnableChn(VpssGrp, VpssChn);     // 4. Enable channel ★

// From SAMPLE_COMM_VPSS_Start():
CVI_VPSS_StartGrp(VpssGrp);               // 5. Start group ★

// From sample_vio.c:
SAMPLE_COMM_VI_Bind_VPSS(ViPipe, ViChn, VpssGrp);  // 6. Bind LAST ★
```

### Binding Parameter Reference

**VI as Source**:
```c
MMF_CHN_S stSrcChn;
stSrcChn.enModId = CVI_ID_VI;
stSrcChn.s32DevId = ViPipe;   // VI Pipe ID (usually 0)
stSrcChn.s32ChnId = ViChn;    // VI Channel ID (usually 0)
```

**VPSS as Destination** (from official documentation p.2299-2300):
> "When VPSS serves as the data receiver, the device (GROUP) serves as the receiver to receive data from other modules. **The user sets the channel ID to 0**"

```c
MMF_CHN_S stDestChn;
stDestChn.enModId = CVI_ID_VPSS;
stDestChn.s32DevId = VpssGrp;  // VPSS Group ID
stDestChn.s32ChnId = 0;        // ★ MUST be 0 for VPSS destination
```

## Debug Commands

### Check Binding Status

```bash
# View binding table - should show VI→VPSS relationship
cat /proc/cvitek/sys | grep -A 10 "BIND RELATION"

# Expected output when binding is successful:
# 1stMod  1stDev  1stChn  2ndMod  2ndDev  2ndChn
# VI      0       0       VPSS    0       0

# Empty table indicates binding failed
```

### Check VI Status

```bash
# View VI runtime status
cat /proc/cvitek/vi

# Key fields to check:
# - IntCnt: Interrupt count (should be increasing)
# - RecvPic: Received pictures from sensor
# - SendOK: Frames sent successfully
# - VbFail: VB buffer allocation failures (should be 0)
# - LostFrame: Lost frames (should be 0)
```

### Check VPSS Status

```bash
# View VPSS runtime status
cat /proc/cvitek/vpss

# Key fields to check:
# - RecvCnt: Frames received from VI (should be increasing)
# - SendOK: Frames sent successfully
# - BufEmpty: Output buffer empty count
# - NoBuf: No buffer available count (correlates with NOBUF error)
```

### Check VB Pool Usage

```bash
# View VB pool status
cat /proc/cvitek/vb

# Key fields to check:
# - BlkCnt: Total blocks in pool
# - Free: Currently free blocks
# - MinFree: Minimum free blocks ever (helps size pool)
# - UseCnt: Usage count per block

# If Free = 0 and MinFree = 0, pool is exhausted
```

### Enable Debug Logs

```bash
# Enable module-level debug logging (level 7 = all)
echo "VI=7" > /proc/cvitek/log
echo "VPSS=7" > /proc/cvitek/log
echo "SYS=7" > /proc/cvitek/log

# Check kernel log for errors
dmesg | grep -i "cvi\|vi\|vpss\|vb"
```

## Common Pitfalls

### 1. Binding Before Start

**Wrong**:
```c
CVI_VPSS_CreateGrp(grp, &attr);
CVI_SYS_Bind(&vi_chn, &vpss_chn);  // ❌ Too early!
CVI_VPSS_StartGrp(grp);
```

**Correct**:
```c
CVI_VPSS_CreateGrp(grp, &attr);
CVI_VPSS_ResetGrp(grp);
CVI_VPSS_SetChnAttr(grp, chn, &chn_attr);
CVI_VPSS_EnableChn(grp, chn);
CVI_VPSS_StartGrp(grp);
CVI_SYS_Bind(&vi_chn, &vpss_chn);  // ✓ After start
```

### 2. Missing VPSS ResetGrp

**Wrong**:
```c
CVI_VPSS_CreateGrp(grp, &attr);
// Missing ResetGrp!
CVI_VPSS_SetChnAttr(grp, chn, &chn_attr);
```

**Correct**:
```c
CVI_VPSS_CreateGrp(grp, &attr);
CVI_VPSS_ResetGrp(grp);  // ✓ Required after create
CVI_VPSS_SetChnAttr(grp, chn, &chn_attr);
```

### 3. Insufficient VB Pool Size

**Problem**: VB pool too small causes NOBUF errors

**Solution**: Calculate required buffer size:
```c
// For YUV420 (NV21):
buffer_size = width * height * 3 / 2;

// For RGB888:
buffer_size = width * height * 3;

// Account for alignment (typically 64-byte aligned):
aligned_width = (width + 63) & ~63;
buffer_size = aligned_width * height * bytes_per_pixel;
```

### 4. Channel Depth Too Small

**Problem**: `u32Depth = 0` causes NOBUF in binding mode

**Solution**: Set channel depth to at least 1-2:
```c
chn_attr.u32Depth = 2;  // Allow buffering 2 frames
```

### 5. Not Releasing Frames

**Problem**: Frames not released cause VB pool exhaustion

**Wrong**:
```c
CVI_VPSS_GetChnFrame(grp, chn, &frame, 1000);
// Process frame
// ❌ Missing release!
```

**Correct**:
```c
CVI_VPSS_GetChnFrame(grp, chn, &frame, 1000);
// Process frame
CVI_VPSS_ReleaseChnFrame(grp, chn, &frame);  // ✓ Always release
```

## Recovery Procedures

### Clean State Recovery

If the system is in an unknown state after failed tests:

```bash
# Option 1: Restart application with clean init
# In application: call cleanup sequence
CVI_SYS_UnBind(...)
CVI_VPSS_StopGrp(...)
CVI_VPSS_DisableChn(...)
CVI_VPSS_DestroyGrp(...)
CVI_VI_DisableChn(...)
CVI_VI_StopPipe(...)
CVI_VI_DestroyPipe(...)
CVI_VI_DisableDev(...)
CVI_SYS_Exit()
CVI_VB_Exit()

# Option 2: Reboot device (for corrupted kernel state)
reboot
```

### Kernel Module State

Sometimes kernel modules retain state from previous runs. Check with:

```bash
# Check kernel logs for previous errors
dmesg | tail -100 | grep -i "tuning_buf\|already allocated\|error"

# If "already allocated" appears, reboot may be required
```
