# System Overview and Workflow

This document captures the cross-module guidance that applies to all CV181X/CV182X/CV180X multimedia pipelines. It is a summary of project-level design rules and workflow ordering. Module details live in the per-module references.

## Module Selection (Decision Framework)

Text flow:
```
[Data Source] -> [Processing] -> [Output] -> [Connection Model]
```

**Data Source**:
- Camera sensor -> VI (ISP pipeline)
- Compressed stream (JPEG/MJPEG/H.264) -> VDEC
- CPU/Custom buffers -> VPSS (SendFrame) or VENC (SendFrame)

**Processing**:
- Scale/crop/format conversion -> VPSS
- OSD/overlay -> RGN (attach to VI/VPSS/VENC)
- Geometric corrections -> GDC

**Output**:
- Encode to bitstream -> VENC
- Display -> VO
- Custom processing -> GetFrame from VI/VPSS/VDEC

**Connection Model**:
- Online: CVI_SYS_Bind for zero-copy, low latency
- Offline: GetFrame/SendFrame for custom processing

## Common Pipelines (Text Table)

| Use Case | Pipeline | Notes |
| --- | --- | --- |
| Video surveillance | VI -> VPSS -> VENC | Lowest latency, online mode preferred |
| Doorbell preview + record | VI -> VPSS -> VO + VENC | Two outputs from VPSS channels |
| Video conference | VI -> VPSS -> VENC + VDEC -> VPSS -> VO | Bidirectional pipeline |
| AI vision | VI -> VPSS -> USER -> VPSS -> VENC/VO | Use VPSS for inference input |
| Decode and re-encode | VDEC -> VPSS -> VENC | Use MEM input VPSS group |
| Display decoded stream | VDEC -> VPSS -> VO | Use separate VPSS group from camera |

See `scenarios.md` and `binding-cookbook.md` for complete flows.

## Common Tasks (Checklist)

### Build a Video Surveillance Camera

1. Use the VI -> VPSS -> VENC pipeline from `scenarios.md` (Scenario 1).
2. Configure multi-resolution outputs on VPSS (main + sub streams).
3. Bind VPSS channels to VENC channels for each stream.
4. Retrieve encoded bitstream from VENC.

### Add AI Vision Processing

1. Use VPSS to generate inference input (for example, 640x640).
2. Get frames from VPSS, run TPU inference, and release frames.
3. Draw results on a display or encode path.
4. Keep inference buffers separate from encode buffers to avoid VB starvation.

### Add Local Display

1. Configure VO for the target interface and resolution.
2. Bind VPSS output channel to VO.
3. Match VPSS output size to the display resolution to avoid extra scaling.

## Standard Initialization Workflow

Text flowchart:
```
[VB SetConfig] -> [VB Init] -> [SYS Init]
   -> [Configure Modules] -> [Start Modules]
   -> [Bind if Online] -> [Processing]
   -> [Unbind] -> [Stop Modules] -> [SYS Exit] -> [VB Exit]
```

**Notes**:
- Start modules before binding.
- Unbind before stopping modules.

## Online vs Offline Mode (Summary)

| Mode | Data Flow | CPU Involvement | Best For | Key Rule |
| --- | --- | --- | --- | --- |
| Online (Bind) | Hardware push (zero-copy) | Low | Real-time pipelines | Bind after module start |
| Offline (SendFrame) | User push (manual) | Higher | Custom processing | No bind on that VPSS group |

See `sys.md` and `vpss.md` for mode constraints.

## Memory Management Summary

| Memory Type | Used By | Ownership | Notes |
| --- | --- | --- | --- |
| VB pools | VI/VPSS/VDEC/VENC/VO | Media system | Preferred for module IO |
| ION | CPU/TPU/custom | Application | Use cache flush/invalidate rules |

See `vb.md` and `ion.md` for details.

## Performance Guidance (Project-Level)

- Prefer online bind paths for steady-state pipelines.
- Use VPSS to generate inference input instead of CPU resize/cvtColor.
- Align sensor -> VPSS -> VENC resolutions to avoid extra scaling.
- Plan VB pools for every output resolution and format.
- For JPEG, use VDEC and size pools to the actual image dimensions.
- Choose codec based on latency vs compatibility (H.265 vs H.264).
- Use module QueryStatus APIs and `/proc/cvitek/*` to validate throughput.

## Error Handling and Diagnostics

- All CVI APIs return `CVI_S32`; treat non-zero as failure and log the code.
- Use `/proc/cvitek/*` to confirm module state and binding.
- When failures occur, collect logs and compare against `troubleshooting.md`.

## References

- `vi.md`, `vpss.md`, `venc.md`, `vdec.md`, `vo.md`
- `sys.md`, `vb.md`, `ion.md`
- `binding-cookbook.md`, `integration-guide.md`, `scenarios.md`
- `debug.md`, `troubleshooting.md`
