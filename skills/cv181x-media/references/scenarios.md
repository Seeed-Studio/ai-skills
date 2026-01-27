# Common Multimedia Scenarios

This document describes common multimedia application scenarios and recommended module combinations for CV181X/CV182X platforms.

## Scenario 1: Video Surveillance Camera

**Requirements**: Capture video → Encode H.265 → Stream to network

**Pipeline**: `VI → VPSS → VENC → Network`

**Key Features**:
- Multi-resolution encoding (main stream + sub stream)
- ROI encoding for important regions
- Motion detection integration

**Module Configuration**:
1. **VI**: Capture from sensor (1080p@30fps)
2. **VPSS**:
   - Chn0: 1080p (main stream)
   - Chn1: 720p (sub stream)
   - Chn2: D1 (mobile stream)
3. **VENC**:
   - Chn0: H.265 1080p 4Mbps CBR
   - Chn1: H.265 720p 2Mbps CBR
   - Chn2: H.265 D1 1Mbps CBR

**API Workflow**:
```
CVI_SYS_Init()
→ VI: SetDevAttr → EnableDev → CreatePipe → StartPipe → EnableChn
→ VPSS: CreateGrp → SetGrpAttr → SetChnAttr (×3) → StartGrp → EnableChn (×3)
→ VENC: CreateChn (×3) → SetRcParam (×3) → StartRecvFrame (×3)
→ Bind: VI→VPSS, VPSS_Chn0→VENC_Chn0, VPSS_Chn1→VENC_Chn1, VPSS_Chn2→VENC_Chn2
→ Loop: GetStream → SendToNetwork → ReleaseStream
```

---

## Scenario 2: Smart Doorbell with Display

**Requirements**: Capture video → Display locally → Encode when motion detected → Two-way audio

**Pipeline**: `VI → VPSS → VO` (display) + `VPSS → VENC` (recording)

**Key Features**:
- Local preview on LCD
- Event-triggered recording
- Snapshot capture

**Module Configuration**:
1. **VI**: Capture 1080p@30fps
2. **VPSS**:
   - Chn0: 480x800 (LCD display)
   - Chn1: 1080p (recording)
3. **VO**: LCD display (480x800)
4. **VENC**: H.265 1080p (on-demand)

**API Workflow**:
```
CVI_SYS_Init()
→ VI: Setup and start
→ VPSS: CreateGrp → SetChnAttr(Chn0: 480x800, Chn1: 1080p) → StartGrp → EnableChn(×2)
→ VO: SetPubAttr → Enable → SetVideoLayerAttr → EnableVideoLayer → SetChnAttr → EnableChn
→ Bind: VI→VPSS, VPSS_Chn0→VO (always on for preview)
→ On motion detection:
  - VENC: CreateChn → StartRecvFrame
  - Bind: VPSS_Chn1→VENC
  - Record for N seconds
  - UnBind, DestroyChn
```

---

## Scenario 3: Image Processing Device

**Requirements**: Capture RAW → Apply custom ISP → Process → Save JPEG

**Pipeline**: `VI (RAW) → Custom Processing → VPSS → VENC (JPEG)`

**Key Features**:
- RAW frame access
- Custom algorithm integration
- High-quality JPEG snapshot

**Module Configuration**:
1. **VI**: Offline mode (manual frame fetch)
2. **VPSS**: Offline mode (manual frame input)
3. **VENC**: JPEG encoder

**API Workflow**:
```
CVI_SYS_Init()
→ VI: Setup pipe for RAW output
→ Loop:
  - VI: GetPipeFrame (RAW data)
  - Custom ISP processing (CPU/TPU)
  - VPSS: SendFrame (processed YUV)
  - VPSS: GetChnFrame
  - VENC: SendFrame (JPEG encoder)
  - VENC: GetStream (JPEG data)
  - Save to file
  - ReleaseStream, ReleaseChnFrame, ReleasePipeFrame
```

---

## Scenario 4: Video Conference Device

**Requirements**: Capture video → Encode → Network + Decode incoming → Display

**Pipeline**:
- Outgoing: `VI → VPSS → VENC → Network`
- Incoming: `Network → VDEC → VPSS → VO`

**Key Features**:
- Low latency encoding
- PIP (Picture-in-Picture) display
- Adaptive bitrate

**Module Configuration**:
1. **VI**: 1080p@30fps
2. **VPSS Grp0** (local camera):
   - Chn0: 1080p (encode)
   - Chn1: 240p (local PIP)
3. **VPSS Grp1** (remote video):
   - Chn0: 1080p (main display)
4. **VENC**: H.264 1080p low-latency mode
5. **VDEC**: H.264 decoder
6. **VO**:
   - Chn0: Remote video (main)
   - Chn1: Local video (PIP overlay)

**API Workflow**:
```
CVI_SYS_Init()
→ Setup VI → VPSS_Grp0 → VENC (outgoing)
→ Setup VDEC → VPSS_Grp1 → VO (incoming)
→ Bind: VI→VPSS_Grp0, VPSS_Grp0_Chn0→VENC, VDEC→VPSS_Grp1, VPSS_Grp1_Chn0→VO_Chn0, VPSS_Grp0_Chn1→VO_Chn1
→ Threads:
  - Encoder thread: GetStream → Send
  - Decoder thread: Receive → SendStream
```

---

## Scenario 5: AI-Powered Security Camera

**Requirements**: Capture video → TPU inference → Draw results → Encode + Display

**Pipeline**: `VI → VPSS → User (TPU) → VPSS → VENC/VO`

**Key Features**:
- Object detection (YOLO)
- Face recognition
- OSD overlay (bounding boxes)

**Module Configuration**:
1. **VI**: 1080p@30fps
2. **VPSS Grp0** (preprocessing):
   - Chn0: 1080p (passthrough)
   - Chn1: 640x640 (TPU input)
3. **VPSS Grp1** (post-processing):
   - Chn0: 1080p (with OSD)
4. **VENC**: H.265 1080p
5. **VO**: Display output

**API Workflow**:
```
CVI_SYS_Init()
→ Setup VI → VPSS_Grp0
→ Loop:
  - VPSS_Grp0_Chn1: GetChnFrame (640x640)
  - Run TPU inference
  - ReleaseChnFrame
  - VPSS_Grp0_Chn0: GetChnFrame (1080p)
  - Draw bounding boxes on frame
  - VPSS_Grp1: SendFrame (modified frame)
  - VPSS_Grp1: GetChnFrame
  - VENC/VO: SendFrame or Bind
  - ReleaseChnFrame
```

---

## Scenario 6: Multi-Channel NVR (Network Video Recorder)

**Requirements**: Decode 4 network streams → Display in quad view → Record

**Pipeline**: `Network → VDEC (×4) → VPSS (×4) → VO (quad) + VENC (×4)`

**Key Features**:
- 4-channel decoding
- Quad-split display
- Independent recording per channel

**Module Configuration**:
1. **VDEC**: 4 channels (H.265 1080p)
2. **VPSS**: 4 groups
   - Each Grp Chn0: 1080p (record)
   - Each Grp Chn1: 540p (display quarter)
3. **VO**: 1080p display with 4 channels (2×2 grid)
4. **VENC**: 4 channels (H.265 1080p)

**API Workflow**:
```
CVI_SYS_Init()
→ Setup 4× VDEC channels
→ Setup 4× VPSS groups
→ Setup 4× VENC channels
→ Setup VO with 4 channels (layout: 2×2)
→ Bind: Each VDEC→VPSS→VENC (recording), VPSS_Chn1→VO_Chn (display)
→ Threads:
  - 4× Decoder threads: Receive → VDEC_SendStream
  - 4× Encoder threads: VENC_GetStream → Save
```

---

## Module Combination Guidelines

### Online vs Offline Mode

**Use Online (Bind) when**:
- Low latency required
- Standard video pipeline (no custom processing)
- CPU load should be minimized

**Use Offline (SendFrame/GetFrame) when**:
- Custom processing needed (AI, watermark, etc.)
- Frame timing must be controlled
- Selective frame processing

### Performance Optimization

1. **Minimize VPSS groups**: Reuse groups when possible
2. **Use hardware binding**: Avoid GetFrame/SendFrame loops
3. **Choose appropriate resolution**: Match sensor → VPSS → VENC resolutions
4. **Rate control**: Use CBR for streaming, VBR for storage
5. **Buffer management**: Attach VB pools to avoid memory allocation overhead

### Common Pitfalls

1. **Forgetting CVI_SYS_Init()**: Always call before any module operation
2. **Wrong binding order**: Configure modules BEFORE binding
3. **Not releasing frames**: Always ReleaseChnFrame after GetChnFrame
4. **Mismatched resolutions**: Ensure VPSS input matches VI output
5. **Buffer overflow**: Monitor with QueryStatus, adjust buffer size if needed

---

## Reference Documentation

For detailed API documentation, see:
- [vi.md](vi.md) - Video Input module
- [vpss.md](vpss.md) - Video Processing module
- [venc.md](venc.md) - Video Encoding module
- [vo.md](vo.md) - Video Output module
- [sys.md](sys.md) - System Control and binding
