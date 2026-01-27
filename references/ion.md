# ION Memory Integration Reference

## Overview

ION provides physically contiguous memory for CPU and hardware engines. It is the right tool for custom buffers, CPU preprocessing, or bridging external memory into the media pipeline.

Text diagram:
```
CPU (cached) <-> ION (phys/virt) <-> VB EX Pool (optional) <-> Media Modules
```

## When to Use ION

- **CPU pre-processing** before VPSS/VENC/TPU when input is not already in VB.
- **Custom buffers** that are not managed by VB.
- **External memory integration** via VB EX pools.

## ION vs VB (Text Table)

| Item | ION | VB |
| --- | --- | --- |
| Ownership | User | VB system |
| Allocation | On demand | Preconfigured pools |
| Best for | Custom buffers | Media pipelines |
| Cache ops | Required (cached) | Managed by module |
| Typical use | CPU staging | VI/VPSS/VENC/VDEC |

## Cache Coherency Rules

Text flowchart (CPU write -> HW read):
```
[CPU writes cached ION]
   |
[CVI_SYS_IonFlushCache]
   |
[HW reads]
```

Text flowchart (HW write -> CPU read):
```
[HW writes]
   |
[CVI_SYS_IonInvalidateCache]
   |
[CPU reads]
```

**Guidance**:
- Use cached ION for CPU-heavy work; always flush after CPU writes.
- Use non-cached ION for direct HW access if CPU touches are minimal.
- Never skip cache operations when CPU and HW share the same buffer.

## ION to VB Integration

If a module requires VB ownership, wrap ION into a VB EX pool:

- **Use VB EX pool** to register ION physical addresses.
- **Attach EX pool** only when the module VB source is USER.
- **Do not attach** if the module uses common pools.

## Minimal Example (ION Cache Ops)

```c
CVI_U64 paddr = 0;
void* vaddr = CVI_SYS_IonAlloc_Cached(&paddr, size);

// CPU write
memcpy(vaddr, src, size);
CVI_SYS_IonFlushCache(paddr, vaddr, size);

// HW read/write ...

// CPU read after HW write
CVI_SYS_IonInvalidateCache(paddr, vaddr, size);
memcpy(dst, vaddr, size);

CVI_SYS_IonFree(paddr, vaddr);
```

## Related References

- `vb.md` for VB EX pools and pool sizing
- `sys.md` for ION APIs and binding rules
