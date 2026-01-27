# Binding Cookbook (Concurrent Scenarios + Minimal Flows)

This reference consolidates the former concurrent scenarios guidance into a single, compact cookbook. It focuses on binding order, input ownership, buffer planning, and the minimal steps required to make each pipeline reliable.

## Design Checklist

- Use one VPSS group per input type (ISP vs MEM).
- Use VPSS_MODE_DUAL when ISP and MEM inputs are active at the same time.
- Plan VB pools for every active output size and format.
- Start modules before binding; bind after VI and VPSS are running.

## Architecture (Text Diagram)

```
Camera (VI/ISP) -> VPSS Group 0 (Bind, ISP input) -> Chn0/Chn1 -> Display/Encode
File/JPEG       -> VDEC -> VPSS Group 1 (Bind or SendFrame, MEM input) -> Chn0 -> VENC
                                           |
                                           -> Chn1 -> TPU Inference -> Draw -> Save
```

## Binding Rules (Text Table)

| Direction | Source | Destination | Channel ID Rule |
| --- | --- | --- | --- |
| VI -> VPSS | VI Pipe/Chn | VPSS Group | Dest ChnId must be 0 |
| VPSS -> VENC | VPSS Chn | VENC Chn | Src ChnId is output channel |
| VDEC -> VPSS | VDEC Chn | VPSS Group | Dest ChnId must be 0 |

## Scenario 1: Camera -> VPSS -> Save/Display (Online Mode)

Text flowchart:
```
[VB/SYS Init]
   |
[VI/ISP Init + Enable Chn]
   |
[VPSS Grp (ISP input) Create/Start]
   |
[Bind VI -> VPSS]
   |
[Warmup + Ready Poll]
   |
[GetChnFrame -> Release]
```

**Notes**:
- Use VPSS channel 0 for main stream, channel 1 for sub stream.
- VB pools must include NV21 at sensor size and output BGR/RGB as needed.

Minimal binding snippet:
```c
MMF_CHN_S vi = {CVI_ID_VI, 0, 0};
MMF_CHN_S vpss = {CVI_ID_VPSS, 0, 0};
CVI_SYS_Bind(&vi, &vpss);
```

## Scenario 2: File/JPEG -> VDEC -> VPSS -> VENC (MEM input)

Text flowchart:
```
[VB/SYS Init]
   |
[Read JPEG Header -> Get Size]
   |
[Init VDEC with JPEG size]
   |
[StartRecvStream -> Decode]
   |
[VPSS Grp (MEM input) Start]
   |
[Bind VDEC->VPSS] or [SendFrame -> GetChnFrame -> Release]
   |
[Bind VPSS Chn -> VENC]
```

**Notes**:
- VDEC -> VPSS supports bind mode or SendFrame mode; choose one and do not mix.
- Use bind for automatic flow; use SendFrame for manual control.
- Ensure NV21 pool exists for the JPEG size.

Minimal binding snippet:
```c
MMF_CHN_S vpss = {CVI_ID_VPSS, grp, chn};
MMF_CHN_S venc = {CVI_ID_VENC, 0, 0};
CVI_SYS_Bind(&vpss, &venc);
```

## Scenario 3: Camera -> VPSS -> TPU Inference -> Draw -> Save

Text flowchart:
```
[Camera -> VPSS Chn (640x640)]
   |
[GetChnFrame]
   |
[TPU Inference]
   |
[Draw on Frame]
   |
[Release Frame]
```

**Notes**:
- TPU preprocessing should use VPSS output to avoid CPU resize/cvtColor.
- Keep a dedicated 640x640 pool for inference output.

## Scenario 4: Complete Concurrent Example

Text flowchart:
```
[Thread A] Camera pipeline -> VPSS G0 -> VENC/Display
[Thread B] JPEG pipeline -> VDEC -> VPSS G1 -> VENC
[Thread C] Inference pipeline -> VPSS G1 Chn -> TPU -> Draw
```

**Concurrency rules**:
- Separate VPSS groups for ISP and MEM inputs.
- Avoid shared output pools between unrelated pipelines.
- Use /proc/cvitek/vb to validate Free counts under load.

## Common Traps

- Binding before module start: bind table is empty and data flow stops.
- ISP input group used with SendFrame: invalid flow, fails or stalls.
- Missing VB pools for output sizes: GetChnFrame NOBUF.
- VDEC initialized with oversized dimensions: StartRecvStream NOMEM.
