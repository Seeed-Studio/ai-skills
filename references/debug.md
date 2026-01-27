# Debugging and Troubleshooting Guide

## Overview

CV181X/CV182X platforms provide multiple debugging mechanisms through the `/proc` filesystem, log system, and diagnostic APIs. This guide covers essential debugging techniques for multimedia applications.

## Proc Filesystem

The `/proc/cvitek/` filesystem provides runtime status and statistics for all media modules.

### System-Wide Information

#### 1. View All Media Module Status

```bash
# List all CVI MPI proc entries
ls /proc/cvitek/
```

Common entries:
- `vi` - Video Input status
- `vpss` - Video Processing status
- `venc` - Video Encoding status
- `vdec` - Video Decoding status
- `vo` - Video Output status
- `vb` - Video Buffer Pool status
- `rgn` - Region (OSD) status
- `gdc` - Geometric Distortion Correction status
- `sys` - System information
- `isp` - ISP status
- `log` - Log level control

#### 2. System Version and Chip Info

```bash
# Get SDK version
cat /proc/cvitek/version

# Get chip information
cat /proc/cvitek/chipinfo
```

### Module-Specific Debugging

#### VI (Video Input)

```bash
# View VI status
cat /proc/cvitek/vi

# Output shows:
# - Device status (enabled/disabled)
# - Pipe status (resolution, frame rate)
# - Channel status (frames captured, dropped frames)
# - Sensor information

# Example output:
# -----VI DEV[0] ATTR-----
# Interface: MIPI
# Status: Enabled
# -----VI PIPE[0] ATTR-----
# Size: 1920x1080
# PixelFormat: YUV420
# FrameRate: 30
# -----VI CHN[0] STATUS-----
# FrameCount: 12345
# LostFrames: 0
```

**Key metrics**:
- `FrameCount`: Total frames captured
- `LostFrames`: Dropped frames (indicates buffer shortage or timing issues)

#### VPSS (Video Processing)

```bash
# View VPSS status
cat /proc/cvitek/vpss

# Output shows:
# - Group status (input resolution, state)
# - Channel status (output resolution, frames processed)
# - Processing time statistics
```

**Troubleshooting**:
- High `LostCnt` → Increase VB buffer count
- Low frame rate → Check binding or buffer allocation

#### VENC (Video Encoding)

```bash
# View VENC status
cat /proc/cvitek/venc

# Output shows:
# - Channel status (codec type, resolution)
# - Bitrate statistics (current, average, peak)
# - Frame statistics (I/P/B frame counts)
# - Buffer status (stream buffer usage)
```

**Key metrics**:
- `Bitrate`: Current encoding bitrate
- `FrameCount`: Total encoded frames
- `StreamBufUsage`: Percentage of stream buffer used
  - High usage (>80%) → Increase buffer or retrieve bitstream faster

#### VO (Video Output)

```bash
# View VO status
cat /proc/cvitek/vo

# Output shows:
# - Device status (interface type, resolution)
# - Layer status (enabled/disabled, size)
# - Channel status (frames displayed)
```

#### VB (Video Buffer Pool)

```bash
# View VB pool status
cat /proc/cvitek/vb

# Output shows:
# -----COMMON POOL INFORMATION------
# Pool ID  BlkSize   BlkCnt  Free  MaxUsed
#   0      3110400    6       4      5
#   1      1382400    4       2      3

# -----PRIVATE POOL INFORMATION------
# (Shows private pools if any)
```

**Interpreting VB status**:
- `Free`: Available buffers (should never reach 0)
- `MaxUsed`: Peak buffer usage (tune `BlkCnt` based on this)
- If `Free = 0`: Buffer exhaustion - increase `BlkCnt` or reduce buffer size

#### RGN (Region/OSD)

```bash
# View RGN status
cat /proc/cvitek/rgn

# Output shows:
# - Region handles
# - Attachment info (which channel)
# - Display attributes
```

#### GDC (Geometric Distortion Correction)

```bash
# View GDC status
cat /proc/cvitek/gdc

# Output shows:
# - Job status
# - Processing statistics
```

### SYS Binding Information

```bash
# View module bindings
cat /proc/cvitek/sys_bind

# Output shows all active bindings:
# SrcMod   SrcDev  SrcChn  →  DstMod   DstDev  DstChn
# VI       0       0       →  VPSS     0       0
# VPSS     0       0       →  VENC     0       0
```

**Use case**: Verify bindings are correct when data flow is not working.

## Debug Triage Flow (Text Flowchart)

Use this order to avoid chasing secondary symptoms:

```
[Failure]
   |
[Check /dev permissions]
   |
[VB/SYS initialized?]
   |
[Binding table OK?]
   |
[VI RecvPic > 0?]
   |
[VPSS RecvCnt > 0?]
   |
[VB pool Free > 0?]
   |
[Match pool size/format]
```

**Notes**:
- Permission issues cause early VB/SYS failures and hide downstream errors.
- Empty binding table indicates bind order issues or wrong channel IDs.
- If RecvPic and RecvCnt are 0, fix upstream before tuning pools.

## Log System

### Log Levels

CV181X uses a unified log system with 5 levels:

- **0**: Emergency (system unusable)
- **1**: Alert (immediate action required)
- **2**: Critical (critical conditions)
- **3**: Error (error conditions)
- **4**: Warning (warning conditions)
- **5**: Notice (normal but significant)
- **6**: Info (informational messages)
- **7**: Debug (debug-level messages)

### Control Log Verbosity

```bash
# Set log level for all modules
echo "ALL=6" > /proc/cvitek/log

# Set log level for specific module
echo "VI=7" > /proc/cvitek/log      # VI debug mode
echo "VPSS=4" > /proc/cvitek/log    # VPSS warnings only
echo "VENC=6" > /proc/cvitek/log    # VENC info mode

# View current log levels
cat /proc/cvitek/log
```

**Modules**: `ALL`, `VI`, `VPSS`, `VENC`, `VO`, `VB`, `SYS`, `RGN`, `GDC`, `ISP`

### View Kernel Logs

```bash
# View kernel messages (includes driver logs)
dmesg | grep -i cvi

# Monitor kernel logs in real-time
dmesg -w | grep -i cvi

# Filter by module
dmesg | grep -i "vi\|vpss\|venc"

# Check for errors
dmesg | grep -i error
```

### Application Logs

Enable debug output in your application:

```c
// In your code, check return values and log errors
CVI_S32 ret = CVI_VI_EnableDev(ViDev);
if (ret != CVI_SUCCESS) {
    printf("CVI_VI_EnableDev failed: 0x%x\n", ret);
    // Use error code to diagnose issue
}
```

## Diagnostic APIs

### Query Status APIs

Most modules provide `Query*Status` APIs for runtime diagnostics:

#### VI Status Query

```c
VI_CHN_STATUS_S stChnStatus;
CVI_VI_QueryChnStatus(ViPipe, ViChn, &stChnStatus);

printf("VI Channel Status:\n");
printf("  Frame Count: %u\n", stChnStatus.u32FrameCount);
printf("  Lost Frames: %u\n", stChnStatus.u32LostFrames);
printf("  VB Fail Count: %u\n", stChnStatus.u32VbFail);
```

#### VENC Status Query

```c
VENC_CHN_STATUS_S stStatus;
CVI_VENC_QueryStatus(VencChn, &stStatus);

printf("VENC Channel Status:\n");
printf("  Left Frames: %u\n", stStatus.u32LeftFrames);      // Frames waiting to encode
printf("  Left Stream Bytes: %u\n", stStatus.u32LeftStreamBytes);  // Bitstream buffered
printf("  Left Stream Frames: %u\n", stStatus.u32LeftStreamFrames);
printf("  Current FPS: %u\n", stStatus.u32CurPacks);
```

### Dump Hardware Registers (Advanced)

```c
// Dump VI registers to file for analysis
CVI_VI_DumpHwRegisterToFile(ViPipe, "/tmp/vi_regs.txt");
```

**Use case**: Share with vendor support for low-level debugging.

## Common Issues and Solutions

### 1. No Video Output

**Symptoms**: Black screen, no frames

**Debug steps**:
```bash
# 1. Check if VI is capturing
cat /proc/cvitek/vi
# Look for FrameCount incrementing

# 2. Check bindings
cat /proc/cvitek/sys_bind
# Verify VI → VPSS → VENC/VO bindings

# 3. Check buffer availability
cat /proc/cvitek/vb
# Ensure Free > 0 for all pools

# 4. Check kernel logs
dmesg | tail -50
```

**Common causes**:
- VI device not enabled
- Sensor not initialized properly
- Broken binding
- VB pool exhausted

### 2. Frame Drops / Lost Frames

**Symptoms**: `LostFrames` > 0 in `/proc/cvitek/vi` or `/proc/cvitek/vpss`

**Debug steps**:
```bash
# Check VB status
cat /proc/cvitek/vb

# Monitor in real-time
watch -n 1 "cat /proc/cvitek/vi | grep LostFrames"
```

**Solutions**:
- Increase VB buffer count in `VB_CONFIG_S`
- Reduce resolution or frame rate
- Check if VENC is retrieving bitstream fast enough (`CVI_VENC_GetStream`)

### 3. Low Frame Rate

**Symptoms**: Frame rate lower than expected

**Debug steps**:
```bash
# Check each module's FPS
cat /proc/cvitek/vi    # VI input FPS
cat /proc/cvitek/vpss  # VPSS output FPS
cat /proc/cvitek/venc  # VENC output FPS
```

**Common causes**:
- CPU overload → Check system load (`top`)
- Encoding too slow → Reduce bitrate or resolution
- Buffer blocking → Check VB pool status

### 4. Memory Allocation Failures

**Symptoms**: `CVI_VB_GetBlock failed` or `Out of memory` errors

**Debug steps**:
```bash
# Check total VB usage
cat /proc/cvitek/vb

# Check system memory
free -m

# Check ION memory (if using)
cat /proc/ion
```

**Solutions**:
- Reduce VB pool sizes or counts
- Use smaller resolutions
- Check for memory leaks (unreleased VB blocks)

### 5. Encoding Bitrate Issues

**Symptoms**: Bitrate too high/low, or unstable

**Debug steps**:
```bash
# Monitor real-time bitrate
watch -n 1 "cat /proc/cvitek/venc"

# Check stream buffer usage
cat /proc/cvitek/venc | grep StreamBuf
```

**Solutions**:
- For CBR mode: Adjust target bitrate in `CVI_VENC_SetRcParam`
- For VBR mode: Adjust QP range
- If buffer full: Retrieve bitstream more frequently

### 6. OSD Not Appearing

**Symptoms**: RGN overlay not visible

**Debug steps**:
```bash
# Check RGN status
cat /proc/cvitek/rgn

# Verify region is attached
# Check bShow = true
```

**Solutions**:
- Verify `CVI_RGN_AttachToChn` succeeded
- Check position is within frame bounds
- Verify `bShow = CVI_TRUE` in display attributes
- Check layer order (may be behind other layers)

## Performance Profiling

### Frame Rate Measurement

```c
// Measure actual frame rate
#include <sys/time.h>

struct timeval tv_start, tv_end;
int frame_count = 0;

gettimeofday(&tv_start, NULL);

while (running) {
    CVI_VENC_GetStream(VencChn, &stStream, -1);
    frame_count++;

    CVI_VENC_ReleaseStream(VencChn, &stStream);

    gettimeofday(&tv_end, NULL);
    double elapsed = (tv_end.tv_sec - tv_start.tv_sec) +
                     (tv_end.tv_usec - tv_start.tv_usec) / 1000000.0;

    if (elapsed >= 1.0) {
        printf("FPS: %.2f\n", frame_count / elapsed);
        frame_count = 0;
        gettimeofday(&tv_start, NULL);
    }
}
```

### CPU Usage

```bash
# Monitor CPU usage by process
top -p $(pidof your_app)

# Monitor system-wide CPU
mpstat 1

# Check specific threads
top -H -p $(pidof your_app)
```

### Memory Usage

```bash
# Application memory
ps aux | grep your_app

# Detailed memory map
cat /proc/$(pidof your_app)/maps

# Memory leaks detection (use valgrind on development machine)
valgrind --leak-check=full ./your_app
```

## Best Practices

1. **Always check return values**: Every CVI API returns status code
2. **Enable debug logs during development**: Set log level to 7 for detailed info
3. **Monitor VB pool usage**: Check `/proc/cvitek/vb` regularly
4. **Use QueryStatus APIs**: Poll status periodically to detect issues early
5. **Check dmesg for driver errors**: Kernel logs reveal low-level issues
6. **Test under load**: Run stress tests to expose buffer/timing issues
7. **Profile before optimizing**: Measure actual performance bottlenecks

## Debugging Checklist

When encountering issues, follow this checklist:

- [ ] Check API return values (non-zero = error)
- [ ] Verify initialization order (VB → SYS → Modules)
- [ ] Check module bindings (`/proc/cvitek/sys_bind`)
- [ ] Verify VB pools have free buffers (`/proc/cvitek/vb`)
- [ ] Check frame counts in module proc files (incrementing = working)
- [ ] Review kernel logs for driver errors (`dmesg | grep -i cvi`)
- [ ] Enable debug logs for problematic module
- [ ] Query module status with API (`CVI_*_QueryStatus`)
- [ ] Test modules independently (isolate issue)
- [ ] Check hardware connections (sensor, display cables)

## Remote Debugging

### Using gdbserver

```bash
# On device
gdbserver :1234 ./your_app

# On development machine
arm-linux-gdb ./your_app
(gdb) target remote 192.168.42.1:1234
(gdb) break main
(gdb) continue
```

### Core Dump Analysis

```bash
# Enable core dumps
ulimit -c unlimited

# Run application
./your_app
# (crash occurs)

# Analyze core dump
gdb ./your_app core
(gdb) bt  # Backtrace
```

## Support Resources

When reporting issues to vendor support, provide:
1. SDK version (`cat /proc/cvitek/version`)
2. Chip info (`cat /proc/cvitek/chipinfo`)
3. Relevant proc output (`/proc/cvitek/vi`, `/proc/cvitek/vb`, etc.)
4. Kernel logs (`dmesg`)
5. Application logs with debug level
6. Hardware register dump (if requested)
7. Minimal reproducible code
