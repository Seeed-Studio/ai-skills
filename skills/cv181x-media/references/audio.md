# Audio Module Reference

## Overview

The Audio module provides comprehensive audio functionality for multimedia applications. It consists of five sub-modules:

1. **Audio Input (AI)** - Audio capture and recording
2. **Audio Output (AO)** - Audio playback
3. **Audio Encoding (AENC)** - Audio encoding
4. **Audio Decoding (ADEC)** - Audio decoding
5. **Voice Quality Enhancement (VQE)** - Speech quality improvement (AEC, ANR, AGC)

## Core Concepts

### Audio Frame

The basic unit of audio processing is a **Frame**, measured in **samples** (not bytes). Frame size affects latency and processing efficiency.

**Frame Size Requirements**:
- **Without VQE**: 160, 320, or 480 samples (max 512)
- **With VQE**: Must be a multiple of 160 samples

**VQE Operating Frequencies**: 8kHz, 16kHz

### Supported Sample Rates

Input/Output: 8kHz, 11.025kHz, 16kHz, 22.05kHz, 24kHz, 32kHz, 44.1kHz, 48kHz

### Audio Interface

**AIO (Audio Input/Output)** interface connects with Audio Codec via:
- **I2S** timing mode
- **PCM** timing mode

**Device Mapping**:
- **AIP** - Input-only interface (AiDev)
- **AOP** - Output-only interface (AoDev)

**ALSA Integration**: Audio modules interface with Linux kernel through ALSA (Advanced Linux Sound Architecture)

### Codec Integration

Audio Codec acts as the translator between analog and digital domains:
- **Input**: Analog signal → I2S/PCM timing → Digital data (AI module)
- **Output**: Digital data → I2S/PCM timing → DAC → Analog signal (Speaker)

RISC-V/DMA controls data transfer between DDR and Codec.

### Resample

Supports conversion between different sample rates (mainly 8kHz frequency doubling). Note:
- Audio Input resampling: Input rate = device rate, output rate ≠ device rate
- Audio Output resampling: Output rate = device rate, input rate ≠ device rate
- **Invalid** when using system bind between AI and AO

## Essential APIs

### Audio Input (AI)

#### Device Management
- `CVI_AI_SetPubAttr()` - Set audio input device properties (sample rate, bit width, frame size)
- `CVI_AI_GetPubAttr()` - Get audio input device properties
- `CVI_AI_Enable()` - Enable audio input device
- `CVI_AI_Disable()` - Disable audio input device
- `CVI_AI_ClrPubAttr()` - Clear audio input device properties

#### Channel Management
- `CVI_AI_EnableChn()` - Enable audio input channel
- `CVI_AI_DisableChn()` - Disable audio input channel
- `CVI_AI_SetChnParam()` - Set channel parameters
- `CVI_AI_GetChnParam()` - Get channel parameters

#### Frame Operations
- `CVI_AI_GetFrame()` - Get audio frame
- `CVI_AI_ReleaseFrame()` - Release audio frame buffer

#### Volume Control
- `CVI_AI_SetVolume()` - Set audio input device volume
- `CVI_AI_GetVolume()` - Get audio input device volume

#### Resampling
- `CVI_AI_EnableReSmp()` - Enable audio input resampling
- `CVI_AI_DisableReSmp()` - Disable audio input resampling

#### Recording
- `CVI_AI_SaveFile()` - Enable audio file recording
- `CVI_AI_QueryFileStatus()` - Query recording status

#### AEC Reference Frame
- `CVI_AI_EnableAecRefFrame()` - Enable AEC reference frame (when AEC is off)
- `CVI_AI_DisableAecRefFrame()` - Disable AEC reference frame

### Audio Output (AO)

#### Device Management
- `CVI_AO_SetPubAttr()` - Set audio output device properties
- `CVI_AO_GetPubAttr()` - Get audio output device properties
- `CVI_AO_Enable()` - Enable audio output device
- `CVI_AO_Disable()` - Disable audio output device
- `CVI_AO_ClrPubAttr()` - Clear audio output device properties

#### Channel Management
- `CVI_AO_EnableChn()` - Enable audio output channel
- `CVI_AO_DisableChn()` - Disable audio output channel
- `CVI_AO_SetChnParam()` - Set channel parameters
- `CVI_AO_GetChnParam()` - Get channel parameters

#### Frame Operations
- `CVI_AO_SendFrame()` - Send audio frame for playback
- `CVI_AO_ClearChnBuf()` - Clear audio output channel buffer

#### Volume Control
- `CVI_AO_SetVolume()` - Set audio output device volume
- `CVI_AO_GetVolume()` - Get audio output device volume

#### Resampling
- `CVI_AO_EnableReSmp()` - Enable audio output resampling
- `CVI_AO_DisableReSmp()` - Disable audio output resampling

### Audio Encoding (AENC)

- `CVI_AENC_CreateChn()` - Create audio encoding channel
- `CVI_AENC_DestroyChn()` - Destroy audio encoding channel
- `CVI_AENC_StartRecvStream()` - Start accepting audio data
- `CVI_AENC_StopRecvStream()` - Stop accepting audio data
- `CVI_AENC_GetStream()` - Get encoded audio stream
- `CVI_AENC_ReleaseStream()` - Release audio stream buffer

### Audio Decoding (ADEC)

- `CVI_ADEC_CreateChn()` - Create audio decoding channel
- `CVI_ADEC_DestroyChn()` - Destroy audio decoding channel
- `CVI_ADEC_SendStream()` - Send encoded audio stream to decoder
- `CVI_ADEC_RegisterExternalDecoder()` - Register external decoder (e.g., AAC)

### Voice Quality Enhancement (VQE)

#### AI (Audio Input) VQE
- `CVI_AI_SetVqeAttr()` - Set VQE attributes
- `CVI_AI_SetTalkVqeAttr()` - Set talk VQE attributes (IPC scenarios)
- `CVI_AI_GetTalkVqeAttr()` - Get talk VQE attributes
- `CVI_AI_SetRecordVqeAttr()` - Set record VQE attributes (not supported)
- `CVI_AI_GetRecordVqeAttr()` - Get record VQE attributes (not supported)
- `CVI_AI_EnableVqe()` - Enable VQE for audio input
- `CVI_AI_DisableVqe()` - Disable VQE for audio input
- `CVI_AI_SetVqeVolume()` - Set VQE volume
- `CVI_AI_GetVqeVolume()` - Get VQE volume
- `CVI_AI_VqeFunConfig()` - Configure VQE features
- `CVI_AI_SetTrackMode()` - Set track mode
- `CVI_AI_GetTrackMode()` - Get track mode

#### AO (Audio Output) VQE
- `CVI_AO_SetVqeAttr()` - Set VQE attributes
- `CVI_AO_GetVqeAttr()` - Get VQE attributes
- `CVI_AO_EnableVqe()` - Enable VQE for audio output
- `CVI_AO_DisableVqe()` - Disable VQE for audio output

#### Global VQE
- `CVI_VQE_PathSelect()` - Select VQE algorithm path

### Resampler

- `CVI_Resampler_Create()` - Create and initialize audio resampler
- `CVI_Resampler_GetMaxOutputNum()` - Get output sample count
- `CVI_Resampler_Process()` - Process resampling
- `CVI_Resampler_Destroy()` - Destroy resampler

### System Binding

- `CVI_AUD_SYS_Bind()` - Bind two audio media modules
- `CVI_AUD_SYS_UnBind()` - Unbind two audio media modules

## Common Workflows

### Basic Audio Capture

```c
// 1. Set device attributes
AIO_ATTR_S stAiAttr = {
    .enSamplerate = AUDIO_SAMPLE_RATE_16000,
    .enBitwidth = AUDIO_BIT_WIDTH_16,
    .u32FrmNum = 20,  // Frame size (in samples)
    .u32PtNumPerFrm = 160,  // Frame size: 160 samples
    .enWorkmode = AIO_MODE_I2S,
    .u32ChnCnt = 1,  // Mono
};
CVI_AI_SetPubAttr(AiDevId, &stAiAttr);

// 2. Enable device
CVI_AI_Enable(AiDevId);

// 3. Enable channel
CVI_AI_EnableChn(AiDevId, AiChn);

// 4. Capture frames
while (recording) {
    AUDIO_FRAME_S stFrame;
    CVI_AI_GetFrame(AiDevId, AiChn, &stFrame, -1);  // Blocking

    // Process audio data...
    // stFrame.pstFrame->u64PhyAddr - physical address
    // stFrame.pstFrame->u32Len - data length
    // stFrame.u32SeqNumber - frame sequence number

    CVI_AI_ReleaseFrame(AiDevId, AiChn, &stFrame);
}

// 5. Cleanup
CVI_AI_DisableChn(AiDevId, AiChn);
CVI_AI_Disable(AiDevId);
```

### Basic Audio Playback

```c
// 1. Set device attributes
AIO_ATTR_S stAoAttr = {
    .enSamplerate = AUDIO_SAMPLE_RATE_16000,
    .enBitwidth = AUDIO_BIT_WIDTH_16,
    .u32FrmNum = 20,
    .u32PtNumPerFrm = 160,
    .enWorkmode = AIO_MODE_I2S,
    .u32ChnCnt = 1,
};
CVI_AO_SetPubAttr(AoDevId, &stAoAttr);

// 2. Enable device
CVI_AO_Enable(AoDevId);

// 3. Enable channel
CVI_AO_EnableChn(AoDevId, AoChn);

// 4. Send frames for playback
while (playing) {
    AUDIO_FRAME_S stFrame = { /* audio data */ };
    CVI_AO_SendFrame(AoDevId, AoChn, &stFrame, -1);  // Blocking
}

// 5. Cleanup
CVI_AO_DisableChn(AoDevId, AoChn);
CVI_AO_Disable(AoDevId);
```

### Audio Encoding Workflow

```c
// 1. Set up AI (as above)
CVI_AI_SetPubAttr(AiDevId, &stAiAttr);
CVI_AI_Enable(AiDevId);
CVI_AI_EnableChn(AiDevId, AiChn);

// 2. Create AENC channel
AENC_CHN_ATTR_S stAencAttr = { /* encoder config */ };
CVI_AENC_CreateChn(AencChn, &stAencAttr);

// 3. Start receiving audio
CVI_AENC_StartRecvStream(AencChn);

// 4. Capture and encode
while (encoding) {
    AUDIO_FRAME_S stFrame;
    CVI_AI_GetFrame(AiDevId, AiChn, &stFrame, -1);

    // Get encoded stream
    AUDIO_STREAM_S stStream;
    CVI_AENC_GetStream(AencChn, &stStream, -1);

    // Save or transmit stream...

    CVI_AENC_ReleaseStream(AencChn, &stStream);
    CVI_AI_ReleaseFrame(AiDevId, AiChn, &stFrame);
}

// 5. Cleanup
CVI_AENC_StopRecvStream(AencChn);
CVI_AENC_DestroyChn(AencChn);
```

### VQE (Voice Quality Enhancement) Setup

```c
// VQE Configuration (UpVQE - front-end)
AI_TALKVQE_CONFIG_S stVqeConfig = {
    .u32OpenMask = AI_TALKVQE_MASK_AGC | AI_TALKVQE_MASK_ANR,  // Enable AGC + NR
    .stAecCfg = { /* AEC config */ },
    .stAnrCfg = { /* NR config */ },
    .stAgcCfg = {
        .para_agc_max_gain = 30,
        .para_agc_target_high = -3,
        .para_agc_target_low = -12,
        .para_agc_vad_ena = CVI_TRUE,
    },
};

// Set VQE attributes (must enable channel first)
CVI_AI_EnableChn(AiDevId, AiChn);
CVI_AI_SetTalkVqeAttr(AiDevId, AiChn, AoDevId, AoChn, &stVqeConfig);

// Enable VQE
CVI_AI_EnableVqe(AiDevId, AiChn);
```

**VQE Features** (controlled by `u32OpenMask`):
- `AI_TALKVQE_MASK_AGC` - Automatic Gain Control
- `AI_TALKVQE_MASK_ANR` - Noise Reduction (NR)
- `AI_TALKVQE_MASK_AEC` - Acoustic Echo Cancellation
- Additional: Notch Filter, DC Filter, DG (Dynamic Gain), Delay

### System Binding (AI → AO)

```c
// Bind AI to AO for automatic data flow
CVI_AUD_SYS_Bind(AiDevId, AiChn, AoDevId, AoChn);

// Automatic transfer from AI to AO
// No manual GetFrame/SendFrame needed

// Unbind when done
CVI_AUD_SYS_UnBind(AiDevId, AiChn, AoDevId, AoChn);
```

**Note**: Resampling is invalid when using system bind between AI and AO.

## Key Structures

### Device Attributes

- `AIO_ATTR_S` - Audio device attributes
  - `enSamplerate` - Sample rate (8kHz-48kHz)
  - `enBitwidth` - Bit depth (8/16/24 bit)
  - `u32FrmNum` - Frame count (buffer size)
  - `u32PtNumPerFrm` - Samples per frame (frame size)
  - `enWorkmode` - I2S/PCM mode
  - `u32ChnCnt` - Channel count (1=mono, 2=stereo)

### Frame Data

- `AUDIO_FRAME_S` - Audio frame structure
  - `pstFrame` - Frame data pointer
  - `u32Len` - Data length (bytes)
  - `u64PhyAddr` - Physical address
  - `u32SeqNumber` - Frame sequence number

### Stream Data

- `AUDIO_STREAM_S` - Encoded audio stream
  - `pStream` - Stream data pointer
  - `u32Len` - Stream length
  - `u64PTS` - Presentation timestamp

### VQE Configuration

- `AI_TALKVQE_CONFIG_S` - Talk VQE configuration
- `AI_VQE_CONFIG_S` - General VQE configuration
- `AEC_CFG_S` - AEC parameters
- `ANR_CFG_S` - Noise Reduction parameters
- `AGC_CFG_S` - AGC parameters

## Module Properties

### Sample Rate Enum

```c
typedef enum {
    AUDIO_SAMPLE_RATE_8000 = 8000,
    AUDIO_SAMPLE_RATE_11025 = 11025,
    AUDIO_SAMPLE_RATE_16000 = 16000,
    AUDIO_SAMPLE_RATE_22050 = 22050,
    AUDIO_SAMPLE_RATE_24000 = 24000,
    AUDIO_SAMPLE_RATE_32000 = 32000,
    AUDIO_SAMPLE_RATE_44100 = 44100,
    AUDIO_SAMPLE_RATE_48000 = 48000,
} AUDIO_SAMPLE_RATE_E;
```

### Bit Width Enum

```c
typedef enum {
    AUDIO_BIT_WIDTH_8 = 0,
    AUDIO_BIT_WIDTH_16,
    AUDIO_BIT_WIDTH_24,
    AUDIO_BIT_WIDTH_32,
} AUDIO_BIT_WIDTH_E;
```

### Sound Mode Enum

```c
typedef enum {
    AUDIO_SOUND_MODE_MONO = 0,
    AUDIO_SOUND_MODE_STEREO,
    AUDIO_SOUND_MODE_QUAD,
} AIO_SOUND_MODE_E;
```

## Header Files

- `cvi_audio.h` - Main audio API
- `cvi_comm_aio.h` - Audio common definitions
- `cvi_comm_aenc.h` - Audio encoder definitions
- `cvi_comm_adec.h` - Audio decoder definitions

## Related Modules

- **VENC**: Video encoding with audio (AV synchronization)
- **VDEC**: Video decoding with audio
- **SYS**: System binding for audio modules
- **VB**: Video/audio buffer pool

**See also**: `integration-guide.md` for cross-module design and triage.

## Notes

### Parameter Consistency

**CRITICAL**: When using Audio Input and AENC together, ensure these parameters match:
- Sample rate
- Frame size (samples per frame)
- Number of channels

When using ADEC and Audio Output together, parameters must also match. Mismatched parameters will cause audio abnormalities.

### Channel Mode

**Default**: Device 0 (AiDevId = 0, AoDevId = 0)
- Maximum device ID is 2 (unless customization requires expansion)
- Multiple channels under the same device can access the same audio source

### Timing Configuration

- Audio Input/Output controls the clock to synchronize timing
- Refer to `SAMPLE_COMM_AUDIO_CfgAcodec()` in `cvi_sample_comm_audio.c` for timing setup
- Built-in Audio Codec vs external Audio Codec have different timing setup methods

### I2S Multiplex Mode

When Audio Input uses multiplexed I2S receiving mode:
- Standard I2S protocol only has left/right channel concepts
- Maximum 128-bit audio data from left and right channels

### VQE Limitations

- **Currently supported**: UpVQE (front-end VQE) only
- **Not supported**: DnVQE (back-end VQE)
- **Supported rates**: 8kHz, 16kHz
- **Supported formats**: Mono, 16-bit

### Memory Management

Audio frames use Video Buffer (VB) pool for memory management. Attach/detach operations similar to video modules.

## Typical Use Cases

1. **Audio Recording** - Capture microphone input
2. **Audio Playback** - Play audio through speaker
3. **Two-Way Audio** - Real-time communication (intercom)
4. **Audio Encoding** - Encode to PCM/ADPCM/AAC
5. **Audio Decoding** - Decode audio files for playback
6. **Voice Enhancement** - Improve call quality with VQE
7. **Resampling** - Convert between different sample rates
8. **File Recording** - Save audio to file
9. **AEC** - Echo cancellation for full-duplex communication
10. **Noise Reduction** - Reduce background noise

## Performance Considerations

- **Frame size**: Smaller frames = lower latency but more overhead
- **VQE**: Adds processing delay; use only when needed
- **Resampling**: Adds computational overhead
- **System binding**: Reduces latency compared to manual GetFrame/SendFrame
- **Buffer size**: Larger buffer = smoother playback but more memory

## References

- `markdown_docs/Audio_Frequency/README.md`
- `markdown_docs/Audio_Frequency/API_Reference.md`
- `cvi_mpi/sample/source/audio/cvi_sample_audio.c`
