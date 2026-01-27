# Integration Guide (VPSS/VENC/VB/Camera/ION)

This guide captures cross-module integration rules and failure patterns observed in this project. It is a design and debug companion to the per-module references.

## Design Intent and Ownership

- Use a single VB/SYS initialization point (one media context).
- Each pipeline owns its VPSS group configuration and VB pools.
- Frame ownership is strict: any module or user that gets a frame must release it.
- Do not reuse a VPSS group for mixed input types (ISP vs MEM).

## Pipeline Topologies (Text Diagrams)

Camera pipeline (ISP input):
```
Sensor -> VI -> ISP -> VPSS (ISP input, bind) -> VPSS Chn -> {VENC | USER | VO}
```

JPEG pipeline (MEM input):
```
JPEG -> VDEC -> VPSS (MEM input, bind or send) -> VPSS Chn -> {VENC | USER | VO}
```

## Pipeline Selection Matrix

| Pipeline | VPSS Input | Data Flow | Binding | VB Pools | Notes |
| --- | --- | --- | --- | --- | --- |
| Camera -> VPSS -> VENC | ISP | VI->ISP->VPSS | Recommended | Sensor NV21 + VENC outputs | Lowest latency path |
| Camera -> VPSS -> USER | ISP | VI->ISP->VPSS->GetFrame | Recommended | Sensor NV21 + VPSS outputs | First-frame readiness matters |
| JPEG -> VDEC -> VPSS | MEM | VDEC->VPSS | Optional | NV21 sized to JPEG | Bind for auto flow or SendFrame for manual control |
| CPU Mat -> VPSS | MEM | USER->VPSS | Required | BGR/RGB pool sized to input | Requires CPU copy + cache ops |

## VB and ION Resource Strategy

| Use Case | Required Format | Pool Planning | Common Failure | Guidance |
| --- | --- | --- | --- | --- |
| VI/ISP output | NV21 | Sensor resolution pool, count >= 3 | NOBUF / GetChnFrame fail | Add pool to match sensor size, avoid oversized pools |
| VDEC JPEG output | NV21 | Pool sized to JPEG dimensions | StartRecvStream NOMEM | Initialize VDEC to actual JPEG size |
| VPSS output | BGR/RGB | Pools for target sizes (e.g., 640x640) | No suitable pool | Ensure BGR pools exist for all output resolutions |
| CPU staging (ION) | N/A | Cached ION for CPU write | Stale data | Flush after CPU write, invalidate before CPU read |

## Camera Readiness and First-Frame Policy

Text flowchart:
```
[Open Camera]
   |
[Bind VI->VPSS]
   |
[Warmup + Ready Poll]
   |
[First GetChnFrame]
```

**Checks**:
- `/proc/cvitek/vi` RecvPic increases
- `/proc/cvitek/vpss` RecvCnt increases
- If both remain 0, verify binding and VB pools before retrying

## VDEC Initialization Rule (JPEG Path)

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
- Set VDEC max width/height to the actual JPEG dimensions.
- Ensure NV21 pools exist for the decoded size.
- Attach VB pool only when `enVdecVBSource` is user.

## VENC Linkage Rules

- Prefer VPSS output as VENC input to decouple sensor and encoder formats.
- Use one VPSS output channel per VENC profile (resolution + bitrate).
- Ensure VB pools exist for each VPSS output size and format.
- Bind after all modules are started; unbind before shutdown.

## Performance Decomposition (Project-Level)

| Stage | Typical Cost | Interpretation |
| --- | --- | --- |
| VPSS DMA (resize/cvtColor/crop) | Low (few ms) | Hardware path healthy |
| mat_to_video_frame | Medium | CPU memcpy + cache flush dominates |
| frame_to_tensor | High | CPU HWC->CHW + normalization bottleneck |
| OpenCV decode | High | Avoid for production; prefer VDEC |

## Error Patterns and Triage

| Symptom | Likely Cause | Primary Checks |
| --- | --- | --- |
| GetChnFrame 0xc006800e | VPSS NOBUF / not ready | VB free count, VI RecvPic, VPSS RecvCnt, readiness wait |
| StartRecvStream 0xc005800c | VDEC buffer NOMEM | VDEC init size, NV21 pool availability |
| /dev/cvi-* permission denied | Missing sudo | Run with sudo, check device nodes |
| Binding table empty | Bind order wrong | Start modules before binding, check /proc/cvitek/sys |

## Debug Flow (Text Flowchart)

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
[VB pool free > 0?]
   |
[Match pool size/format]
   |
[Retry with readiness wait]
```

## Related References

- `overview.md`, `binding-cookbook.md`
- `vi.md`, `vpss.md`, `vdec.md`, `venc.md`
- `vb.md`, `ion.md`, `troubleshooting.md`
