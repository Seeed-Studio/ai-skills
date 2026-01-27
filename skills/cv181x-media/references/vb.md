# VB (Video Buffer Pool) Module Reference

## Overview

VB (Video Buffer) module provides **8 major categories** of functionality:

1. **Unified Physical Memory Management** - Manage large physical memory for all media modules (VI/VPSS/VO/VDEC/VENC/GDC)
2. **Common Buffer Pool Management** - Shared pools accessible by all modules
3. **Dynamic Pool Management** - Create/destroy private pools at runtime
4. **Block Allocation/Release** - Acquire and return buffer blocks
5. **Pool Configuration Management** - Configure and initialize pool system
6. **Address Translation** - Convert between physical/virtual addresses and handles
7. **Memory Mapping** - Map physical memory to user space
8. **User Block Management** - Support external user-defined blocks

### Buffer Pool Architecture

```
VB Pool (Common Pool or Private Pool)
   ├─ Buffer Block 1 (Fixed size)
   ├─ Buffer Block 2
   ├─ Buffer Block 3
   └─ ...
```

- **Common Pool**: Shared by all modules (allocated at system init)
- **Private Pool**: Dedicated to specific module/channel

### Buffer Lifecycle

```
Allocate Pool → Get Block → Use Buffer → Release Block → Destroy Pool
```

### VB Pool Types (VB_SOURCE_E)

- **VB_SOURCE_COMMON** - Common pool, shared by all modules
- **VB_SOURCE_MODULE** - Module-specific pool for dedicated use
- **VB_SOURCE_PRIVATE** - Private pool for exclusive use
- **VB_SOURCE_USER** - User-defined pool for custom memory management

**Usage Guidelines**:
- Use **COMMON** for most scenarios (shared memory efficiency)
- Use **PRIVATE** when module needs guaranteed buffer availability
- Use **USER** for importing external memory (e.g., from other processes)

## Pool Sizing Guidance (Camera + VDEC + VPSS)

- Start with NV21 pools sized to the active sensor output. Avoid allocating worst-case 5M pools unless the sensor requires it.
- Oversized pools can cause `CVI_VB_Init` to fail or make `CVI_VI_EnableChn` return NOMEM (ION allocation failure).
- JPEG VDEC outputs NV21; ensure a common pool exists for the decode resolution (e.g., add a 1280x720 NV21 pool when decoding 720p JPEG). Missing this pool can make `CVI_VDEC_StartRecvStream` fail.
- Keep large BGR pools minimal and only at the resolutions needed for CPU/VPSS paths.
- For VDEC, only attach a VB pool when the module VB source is **USER**. When VB source is common, rely on common pools and skip attach.

### Pool Planning Matrix (Text Table)

| Pipeline Stage | Format | Pool Size Basis | Suggested Count | Why It Matters |
| --- | --- | --- | --- | --- |
| VI/ISP output | NV21 | Sensor width/height | >= 3 | Prevents first-frame NOBUF and GetChnFrame failures. |
| VDEC JPEG output | NV21 | JPEG width/height | 2-3 | Avoids StartRecvStream NOMEM for decode. |
| VPSS output | BGR/RGB | Target output sizes | 2-3 per size | Ensures VPSS output allocation succeeds. |
| CPU staging (VB) | BGR/RGB | Input Mat sizes | 1-2 | Reduces pressure on large pools. |

### Pool Count and Concurrency

Text diagram:
```
Total VB demand = (VI/ISP pools) + (VDEC pools) + (VPSS outputs) + (VENC inputs)
```

**Guidance**:
- If multiple outputs run concurrently (e.g., 1080p + 720p + 640x640), add pool counts per output size.
- Keep large pools minimal; oversized pools frequently cause VB init failures on memory-limited systems.
- Track Free and MaxUsed in `/proc/cvitek/vb` to tune counts.

### VB_INVALID_POOLID - Special Pool ID

**Definition**: `#define VB_INVALID_POOLID (-1U)`

**Meaning**: "Get block from **any available common pool**"

**Common Misconception**: ❌ Does NOT mean "don't use a pool" or "use ION memory"

#### Correct Usage

```c
// Get block from any available common pool
VB_BLK blk = CVI_VB_GetBlock(VB_INVALID_POOLID, size);
if (blk == VB_INVALID_HANDLE) {
    printf("No available buffer in any common pool\n");
    return -1;
}

// Get the actual pool ID that provided the block
VB_POOL actual_pool = CVI_VB_Handle2PoolId(blk);

printf("Got block from pool ID: %u\n", actual_pool);

// Use the block...
CVI_VB_Handle2PhysAddr(blk);
CVI_VB_GetBlockVirAddr(VB_INVALID_POOLID, phy_addr, NULL);

// Release when done
CVI_VB_ReleaseBlock(blk);
```

#### Key Points

- **Searches all common pools**: Tries each common pool in order until finding an available block
- **Returns actual pool ID**: Use `CVI_VB_Handle2PoolId()` to find which pool provided the block
- **Not for private pools**: Only searches common pools (not private/user pools)
- **Common in samples**: Most SDK examples use `VB_INVALID_POOLID` for flexibility

#### When to Use VB_INVALID_POOLID

- **Multi-pool configurations**: When you have multiple common pools and don't care which one provides the buffer
- **Simplified code**: When you don't need to track specific pool IDs
- **Standard workflows**: All official SDK samples use this pattern

#### When NOT to Use VB_INVALID_POOLID

- **Specific pool requirement**: When you need a buffer from a particular pool
- **Private pool usage**: Use the specific private pool ID returned from `CVI_VB_CreatePool()`
- **Performance optimization**: When you want to avoid pool search overhead

## Essential APIs

### Pool Configuration and Initialization

- `CVI_VB_SetConfig()` - Configure VB pool (must call before CVI_VB_Init)
- `CVI_VB_GetConfig()` - Get current VB configuration
- `CVI_VB_Init()` - Initialize VB module with configured pools
- `CVI_VB_Exit()` - Cleanup and destroy all pools
- `CVI_VB_IsInited()` - Check if VB is initialized

### Buffer Block Operations

- `CVI_VB_GetBlock()` - Acquire buffer block from pool (blocking/timeout)
- `CVI_VB_ReleaseBlock()` - Release buffer block back to pool
- `CVI_VB_GetBlockVirAddr()` - Get virtual address of buffer block
- `CVI_VB_InquireUserCnt()` - Query reference count of buffer

### Pool Management

- `CVI_VB_CreatePool()` - Create private buffer pool
- `CVI_VB_CreatePoolWithoutCompact()` - Create pool without memory compaction
- `CVI_VB_DestroyPool()` - Destroy private pool
- `CVI_VB_PrintPool()` - Print pool information for debugging

### Address Translation

- `CVI_VB_Handle2PhysAddr()` - Get physical address from block handle
- `CVI_VB_PhysAddr2Handle()` - Get block handle from physical address
- `CVI_VB_Handle2PoolId()` - Get pool ID from block handle
- `CVI_VB_GetBlockVirAddr()` - Get virtual address from physical address

### Memory Mapping

- `CVI_VB_MmapPool()` - Map entire pool to user space
- `CVI_VB_MunmapPool()` - Unmap pool from user space
- `CVI_VB_GetBlockVirAddr()` - Get virtual address of specific block

### User Block Management

- `VB_USER_BLOCK_S` - Structure for user-defined external blocks
- Supports importing external memory into VB system
- User blocks must follow VB block alignment requirements

### VB Pool EX Mode (User-Managed Blocks)

**Overview**: VB Pool EX mode allows you to create pools with **user-managed memory blocks**, giving you fine-grained control over memory allocation. This is useful for integrating external memory (e.g., ION memory) into the VB system.

#### VB_POOL_CONFIG_EX_S Structure

```c
typedef struct _VB_POOL_CONFIG_EX_S {
    CVI_U32 u32BlkSize;                          // Block size in bytes
    CVI_U32 u32BlkCnt;                           // Number of blocks
    VB_REMAP_MODE_E enRemapMode;                 // Remap mode (normally NONE)
    CVI_CHAR acName[MAX_VB_POOL_NAME_LEN];      // Pool name for debugging
    VB_USER_BLOCK_S astUserBlk[VB_POOL_MAX_BLK]; // User-managed blocks
} VB_POOL_CONFIG_EX_S;
```

#### Key Difference from Standard Pool

| Feature | Standard Pool (`VB_POOL_CONFIG_S`) | EX Mode Pool (`VB_POOL_CONFIG_EX_S`) |
|---------|-----------------------------------|-------------------------------------|
| **Memory allocation** | VB system allocates memory | User provides physical addresses |
| **Use case** | General purpose | External memory integration |
| **API** | `CVI_VB_CreatePool()` | `CVI_VB_CreatePoolEx()` |

#### Use Cases for EX Mode

- **ION memory integration**: Import ION-allocated memory into VB system
- **Shared memory**: Use memory shared between processes
- **Specific memory regions**: Use memory from specific physical addresses
- **Fine-grained control**: Manage memory allocation manually
 - **Reference**: See `ion.md` for cache coherency and allocation guidance.

#### Example: ION Memory Integration

```c
// 1. Allocate ION memory
CVI_U64 ion_paddr[4];  // Up to 4 planes (Y, U, V, ...)
void *ion_vaddr[4];
CVI_SYS_IonAlloc(&ion_paddr[0], &ion_vaddr[0], "Plane0", plane0_size);
CVI_SYS_IonAlloc(&ion_paddr[1], &ion_vaddr[1], "Plane1", plane1_size);
CVI_SYS_IonAlloc(&ion_paddr[2], &ion_vaddr[2], "Plane2", plane2_size);

// 2. Configure EX mode pool with user blocks
VB_POOL_CONFIG_EX_S pool_cfg = {
    .u32BlkSize = total_size,
    .u32BlkCnt = 1,
    .enRemapMode = VB_REMAP_MODE_NONE,
    .acName = "ION_Pool",
    .astUserBlk[0] = {
        .au64PhyAddr = { ion_paddr[0], ion_paddr[1], ion_paddr[2], 0 },
        // Set other fields as needed
    }
};

// 3. Create pool with EX mode
VB_POOL pool = CVI_VB_CreatePoolEx(&pool_cfg);
if (pool == VB_INVALID_POOLID) {
    printf("Failed to create EX mode pool\n");
    return -1;
}

// 4. Use pool with media modules
CVI_VPSS_AttachVbPool(VpssGrp, VpssChn, pool);

// ... use the module ...

// 5. Cleanup
CVI_VPSS_DetachVbPool(VpssGrp, VpssChn);
CVI_VB_DestroyPool(pool);

// Note: ION memory is NOT freed by VB_DestroyPool
// You must free ION memory separately:
CVI_SYS_IonFree(ion_paddr[0], ion_vaddr[0]);
CVI_SYS_IonFree(ion_paddr[1], ion_vaddr[1]);
CVI_SYS_IonFree(ion_paddr[2], ion_vaddr[2]);
```

#### Important Notes

- **Memory ownership**: User retains ownership of external memory
- **Manual cleanup**: VB_DestroyPool does NOT free user-provided memory
- **Alignment**: User blocks must follow VB alignment requirements (typically 32-byte aligned)
- **Multi-plane support**: Each user block can have up to 4 physical addresses (planes)
- **Error handling**: Check `VB_INVALID_POOLID` return value

#### Advanced: Multiple User Blocks

```c
VB_POOL_CONFIG_EX_S pool_cfg = {
    .u32BlkSize = block_size,
    .u32BlkCnt = 4,  // 4 user blocks
    .acName = "MultiBlockPool",
    .astUserBlk = {
        [0] = { .au64PhyAddr = { ion_addr0_plane0, ion_addr0_plane1, ... } },
        [1] = { .au64PhyAddr = { ion_addr1_plane0, ion_addr1_plane1, ... } },
        [2] = { .au64PhyAddr = { ion_addr2_plane0, ion_addr2_plane1, ... } },
        [3] = { .au64PhyAddr = { ion_addr3_plane0, ion_addr3_plane1, ... } },
    }
};

VB_POOL pool = CVI_VB_CreatePoolEx(&pool_cfg);
```

**See also**: [SYS Module Reference](sys.md) for ION memory allocation APIs.

## Common Workflows

### Standard System Initialization (Common Pool)

```c
// 1. Configure VB pools before system init
VB_CONFIG_S stVbConf;
memset(&stVbConf, 0, sizeof(VB_CONFIG_S));

// Configure common pools
stVbConf.u32MaxPoolCnt = 2;

// Pool 0: For 1080p YUV420 frames
stVbConf.astCommPool[0].u32BlkSize = 1920 * 1080 * 3 / 2;  // YUV420
stVbConf.astCommPool[0].u32BlkCnt = 6;  // 6 buffers

// Pool 1: For 720p YUV420 frames
stVbConf.astCommPool[1].u32BlkSize = 1280 * 720 * 3 / 2;
stVbConf.astCommPool[1].u32BlkCnt = 4;

CVI_VB_SetConfig(&stVbConf);

// 2. Initialize VB (allocates all common pools)
CVI_VB_Init();

// 3. Initialize system
CVI_SYS_Init();

// 4. Setup media modules (VI, VPSS, VENC, etc.)
// Modules automatically use common pools
```

### Creating Private Pool for Specific Module

```c
// Create private pool for specific resolution/format
VB_POOL_CONFIG_S stPoolConfig;
stPoolConfig.u32BlkSize = width * height * 3 / 2;  // YUV420
stPoolConfig.u32BlkCnt = 4;
stPoolConfig.enRemapMode = VB_REMAP_MODE_NONE;

VB_POOL hPrivatePool = CVI_VB_CreatePool(&stPoolConfig);

// Attach private pool to module channel
CVI_VPSS_AttachVbPool(VpssGrp, VpssChn, hPrivatePool);

// ... use the module ...

// Detach and destroy when done
CVI_VPSS_DetachVbPool(VpssGrp, VpssChn);
CVI_VB_DestroyPool(hPrivatePool);
```

### Manual Buffer Operations (Advanced)

```c
// Get buffer from pool
VB_BLK blk = CVI_VB_GetBlock(VB_INVALID_POOLID, size, CVI_ID_USER);
if (blk == VB_INVALID_HANDLE) {
    printf("Failed to get buffer\n");
    return -1;
}

// Get physical address
CVI_U64 phyAddr = CVI_VB_Handle2PhysAddr(blk);

// Get virtual address
void *vaddr = CVI_VB_GetBlockVirAddr(VB_INVALID_POOLID, phyAddr, NULL);

// Use buffer (write data)
memcpy(vaddr, data, size);

// Release buffer
CVI_VB_ReleaseBlock(blk);
```

### Cleanup Sequence

```c
// 1. Destroy media modules (VI, VPSS, VENC, VO)
// 2. Exit system
CVI_SYS_Exit();

// 3. Exit VB (frees all pools)
CVI_VB_Exit();
```

## Buffer Size Calculation

### YUV Format Sizes

**YUV420 (Semi-planar)**:
- Size = Width × Height × 3 / 2
- Example: 1920×1080 = 3,110,400 bytes

**YUV422 (Semi-planar)**:
- Size = Width × Height × 2
- Example: 1920×1080 = 4,147,200 bytes

**YUYV/UYVY (Packed)**:
- Size = Width × Height × 2

### Alignment Requirements

- Width alignment: Typically 16 or 32 bytes
- Height alignment: Typically 2 or 4 lines
- Use `ALIGN(value, alignment)` macro for calculation

**Example with alignment**:
```c
#define ALIGN(x, a) (((x) + (a) - 1) & ~((a) - 1))

CVI_U32 width = 1920;
CVI_U32 height = 1080;
CVI_U32 aligned_width = ALIGN(width, 32);
CVI_U32 aligned_height = ALIGN(height, 2);
CVI_U32 blkSize = aligned_width * aligned_height * 3 / 2;  // YUV420
```

### Buffer Size Calculation Helper

SDK provides helper interfaces for calculating VB block sizes:

- `COMMON_GetPicBufferConfig()` - Get data size for each component in linear format
- `COMMON_GetPicBufferSize()` - Get block pool size for linear format

**Example**:
```c
SIZE_S stSize;
stSize.u32Width = 1920;
stSize.u32Height = 1080;
stSize.enPixelFormat = PIXEL_FORMAT_YUV_PLANAR_420;

CVI_U32 blkSize = COMMON_GetPicBufferSize(&stSize, DATA_BITWIDTH_8, 0);
```

### Buffer Count Guidelines

**Calculation Rules**:

When configuring buffer pools, account for these factors:

1. **Per-channel buffers**: Each channel adds 2 buffers (ping-pong buffer)
2. **VO exception**: VO uses `DisplayBufLen`, minimum 3 buffers
3. **Depth setting**: If channel's `u32Depth` ≠ 0, add `u32Depth` buffers
4. **LDC features**: Each LDC feature (lens correction, rotation) adds 1 memory block

**Memory Strategies**:
- **Ample memory**: Use maximum space for common video buffer pool
- **Constrained memory**: Use multiple common pools of different sizes

**VB Data Flow Example**:
```
1. VI gets buffer Ai from common pool A for sensor data
2. VI completes capture, sends Ai to VPSS
3. VPSS channel 0 and 1 get Aj and Ak from pool A
4. VPSS completes processing, releases Ai to pool
5. VPSS sends Aj to VENC, Ak to VO
6. VENC completes encoding, releases Aj to pool
7. VO completes display, releases Ak to pool
```

**Minimum buffer count per module**:
- **VI**: 2-3 buffers (double/triple buffering)
- **VPSS**: 2-4 buffers per channel
- **VENC**: 2-6 buffers (depends on GOP structure)
- **VO**: 2-3 buffers

**Total buffers** = Sum of all module requirements + margin (10-20%)

## Memory Optimization Strategies

### 1. Use Common Pools

Group buffers by size to minimize pool count:
```c
// Good: Group similar sizes
Pool 0: 1920×1080 (1080p for VI/VPSS/VENC)
Pool 1: 1280×720  (720p for VPSS channel)
Pool 2: 640×640   (AI inference input)

// Bad: Too many pools
Pool 0: 1920×1080 for VI
Pool 1: 1920×1080 for VPSS
Pool 2: 1920×1080 for VENC
```

### 2. Attach Private Pools Selectively

Only use private pools when:
- Module needs unique buffer size not in common pool
- Module needs guaranteed buffer availability
- Module has special memory requirements

### 3. Minimize Buffer Count

Calculate minimum buffers needed:
- For 30fps pipeline: 3-4 buffers usually sufficient
- For offline processing: 2 buffers may be enough
- For complex GOP (H.264/H.265): Add 2-4 more buffers

### 4. Monitor Buffer Usage

Check buffer status in `/proc/cvitek/vb`:
```bash
cat /proc/cvitek/vb
```

Output shows:
- Pool size and block count
- Free/busy blocks
- Maximum used blocks

## Key Structures

### VB_CONFIG_S

Configure common pools:
```c
typedef struct _VB_CONFIG_S {
    CVI_U32 u32MaxPoolCnt;            // Number of common pools (max 16)
    struct {
        CVI_U32 u32BlkSize;           // Block size in bytes
        CVI_U32 u32BlkCnt;            // Number of blocks
        VB_REMAP_MODE_E enRemapMode;  // Remap mode (usually NONE)
    } astCommPool[VB_MAX_COMM_POOLS];
} VB_CONFIG_S;
```

### VB_POOL_CONFIG_S

Configure private pool:
```c
typedef struct _VB_POOL_CONFIG_S {
    CVI_U32 u32BlkSize;               // Block size
    CVI_U32 u32BlkCnt;                // Block count
    VB_REMAP_MODE_E enRemapMode;      // Remap mode
} VB_POOL_CONFIG_S;
```

## Header Files

- `/cvi_mpi/include/cvi_vb.h` - Main VB API
- `/cvi_mpi/include/linux/cvi_comm_vb.h` - VB common definitions

## Related Modules

- **SYS**: System initialization (must init VB before SYS)
- **VI/VPSS/VENC/VO**: Buffer consumers (automatically use VB pools)

**See also**: `integration-guide.md` for cross-module design and triage.

## Notes

- **Initialization order**: `CVI_VB_SetConfig()` → `CVI_VB_Init()` → `CVI_SYS_Init()`
- **Cleanup order**: Destroy modules → `CVI_SYS_Exit()` → `CVI_VB_Exit()`
- Common pools are allocated at `CVI_VB_Init()` time
- Private pools can be created/destroyed dynamically
- Always configure VB **before** system initialization
- Buffer size must account for alignment requirements
- Over-provisioning buffers wastes memory; under-provisioning causes frame drops
- Use `/proc/cvitek/vb` to monitor buffer usage and tune configuration

## Debugging

### Check VB Status

```bash
# View all VB pools
cat /proc/cvitek/vb

# Example output:
# -----COMMON POOL INFORMATION------
# Pool ID  BlkSize   BlkCnt  Free  MaxUsed
#   0      3110400    6       4      2
#   1      1382400    4       3      1
```

### Common Issues

**Issue**: "VB_GetBlock failed"
- **Cause**: Not enough free buffers in pool
- **Solution**: Increase `u32BlkCnt` for the pool

**Issue**: "Out of memory"
- **Cause**: Total pool size exceeds available memory
- **Solution**: Reduce buffer count or resolution

**Issue**: Frame drops
- **Cause**: Insufficient buffers causing blocking
- **Solution**: Add 1-2 more buffers to the bottleneck pool
