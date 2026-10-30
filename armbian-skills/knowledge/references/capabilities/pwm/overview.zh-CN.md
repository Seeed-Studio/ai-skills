---
schema_version: '1'
id: capability.pwm
kind: capability
applies_to:
  capabilities:
  - pwm
required_refs:
- common.linux-device-access
preconditions: []
refines: []
excludes: []
related: []
sources:
- source.linux-pwm
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-29'
---

[English](overview.md) | [简体中文](overview.zh-CN.md)

# PWM 应用接入

识别实际 provider/channel、连接器电气和占用，使用系统实际提供的 PWM API。不得占用热管理风扇/背光等系统资源。记录 period/duty/polarity、启动/停止和异常行为；软件配置读回不等于实际波形，输出频率与占空比需测量。disabled 后的电平不能无依据保证。

文档中的 pinmux 备选只是候选，不代表目标通道空闲、启用或已引出。缺 pwmchip 节点不能确定原因，也不能证明加 overlay 即可使用。pwm-fan requested/enabled 只证明软件占用，不证明风扇已安装或转动；后者须有测速或明确现场观察。

sysfs 的 period、duty_cycle 单位为纳秒：50Hz 是 20,000,000ns，1–2ms 脉宽是 1,000,000–2,000,000ns；换算本身不选择实际通道。外部供电和共地不证明信号阈值、移位器/负载兼容，给驱动接法前核对实际元件规格。
