---
schema_version: '1'
id: capability.spi
kind: capability
applies_to:
  capabilities:
  - spi
required_refs:
- common.linux-device-access
preconditions: []
refines: []
excludes: []
related: []
sources:
- source.linux-spidev
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-30'
---

[English](overview.md) | [简体中文](overview.zh-CN.md)

# SPI 应用接入

确认外部器件、电压、CS、模式、位序和速率。按实际设备身份解析节点；read/write 与组合事务的片选行为不同，选择符合器件协议的接口。现有驱动占用时使用驱动提供接口，不强制重绑。无设备时 SPI 调用成功也可能没有有效回应，应校验对端协议、数据或明确回环。

spidev 节点只证明枚举，不证明连接器路由、当前 mux、应用访问或屏幕初始化。先核对这些条件，再判断是否需要改设备树。PCB/模块未知的简短迁移问题，先补身份，不直接交付假设的完整接线表。

屏幕 DC/RST/BL 可能另用 GPIO，给输出命令前按[GPIO 识别](../../stacks/linux-gpio-chardev/detection.zh-CN.md)核对当前工具/API 版本、映射和占用。BL 可能是逻辑使能或 LED 供电，需查模块电路、电流和移位器/负载限制；标称电压相同、常见模块板载限流都不足以证明可由 GPIO 直驱。模块电路未知时，把 BL/RST 接到固定电平（含 3V3）同样是对未知电路通电，不写成默认首验步骤，不承诺「接上就亮/常亮」；使能极性与限流前提逐条列出，或按[SPI 验证](verification.zh-CN.md)用测量设界。BL 供电/使能前提未知时，接线表该行本身保留待确认；后文补条件不能使前面的可执行直驱步骤变成条件式。给 gpioset 命令前核对目标版本/help、line 占用与电气前提：2.x 用 `-c` 选择 chip，1.x 才用位置参数。SPI 模式/速率以实际模块要求选择，不用试错默认值代替规格。
