---
schema_version: '1'
id: capability.spi.verification
kind: capability_guide
applies_to:
  capabilities:
  - spi
required_refs:
- capability.spi
- common.verification
preconditions: []
refines: []
excludes: []
related: []
sources: []
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-29'
---

[English](verification.md) | [简体中文](verification.zh-CN.md)

# SPI 验证

分层取证：节点枚举 → 引脚复用 → 连接器路由与电气 → 应用访问 → 器件通信。每层证据只支持本层结论，不向下层延伸。

spidev 节点存在只证明控制器已枚举。引脚复用可在目标机用 `/sys/kernel/debug/pinctrl/*/pinmux-pins` 核对（如 `function spi1 group spi1m0-cs0`）：该记录证明 pad 已被控制器占用，仍不证明排针走线、电平移位后的对端连接或应用可访问。禁止用「overlay 列表无 SPI 条目 + 节点已存在」直接断言「无需 overlay/已路由到连接器」——基础 DTB 也能启用节点，overlay 只是配置来源之一。

## 背光与 GPIO 直驱

模块电路未知时，BL 驱动拓扑（逻辑使能输入、LED 供电端、经晶体管/运放驱动）未知：不得断言其中任意一种，也不得据此给出直驱可行性、限流电阻值或上电顺序保证。把 BLK 接到固定电平（含 3V3）同样是对未知电路的通电动作：使能极性与板载限流是否存在都未确认，不得写成默认首验步骤，也不得承诺「接上就亮/常亮」；需要此类排查时逐条列前提（高/低有效使能、有无板载限流），并用串阻压降或电流测量设界。核查来源是模块原理图/规格书；无法取得时交付多种可能性与区分方法，保持条件式。gpioget 回读本身会请求 line，可能改变其方向/电平，不作为无扰动测量或物理电压证明。

## 回环验证的边界

MOSI↔MISO 跳线回环只证明控制器到排针的数据通路（含电平移位器）。数据回读相等不证明 CS 线路由正确——回环不依赖 CS 对端；也不证明外部器件协议、初始化或显示功能。CS 物理路由需仪表（示波器/逻辑分析仪）或真实器件的协议响应。回环仅回答「数据线通/不通」，不作为屏幕等外设功能验收。

## spi_ioc_transfer 结构布局

禁止凭记忆手写 `struct spi_ioc_transfer` 布局。内核版本不同字段不同（较新内核含 `word_delay_usecs`，`pad` 为单字节；旧内核尾部为 2 字节 `pad`），先读目标机 `/usr/include/linux/spi/spidev.h` 并断言 `struct.calcsize` 与 `SPI_IOC_MESSAGE(1)` 尺寸位一致（当前均为 32 字节，`0x40206b00`）。最小回环（需先跳线 MOSI↔MISO 并获得接线授权；无跳线时 FAIL 是预期结果，不是故障证据）：

```bash
python3 - <<'EOF'
import ctypes, fcntl, os, struct
DEV = '/dev/spidev1.0'  # 以目标机实际节点为准
FMT = '=QQIIHBBBBBB'    # 按目标机 spidev.h 核对：u64 u64 u32 u32 u16 6*u8
assert struct.calcsize(FMT) == 32 == ((0x40206B00 >> 16) & 0x3FFF)
fd = os.open(DEV, os.O_RDWR)
fcntl.ioctl(fd, 0x40016B01, struct.pack('=B', 0))        # SPI_IOC_WR_MODE
fcntl.ioctl(fd, 0x40016B03, struct.pack('=B', 8))        # SPI_IOC_WR_BITS_PER_WORD
fcntl.ioctl(fd, 0x40046B04, struct.pack('=I', 1000000))  # SPI_IOC_WR_MAX_SPEED_HZ
tx = bytes(range(16)); n = len(tx)
bi = ctypes.create_string_buffer(tx); bo = ctypes.create_string_buffer(n)
xf = struct.pack(FMT, ctypes.addressof(bi), ctypes.addressof(bo), n,
                 1000000, 0, 8, 0, 0, 0, 0, 0)
fcntl.ioctl(fd, 0x40206B00, xf)                          # SPI_IOC_MESSAGE(1)
print('loopback:', 'OK' if bo.raw[:n] == tx else 'FAIL ' + bo.raw[:n].hex())
EOF
```

总线号/CS、速率与模式上限以目标机节点和模块规格为准。脚本能运行只证明 ABI 正确，不证明对端连接；交付回环步骤时同时说明预期结果、失败含义与所需接线。
