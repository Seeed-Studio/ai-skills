---
schema_version: '1'
id: capability.gpio
kind: capability
applies_to:
  capabilities:
  - gpio
required_refs:
- common.capability-evidence
preconditions: []
refines: []
excludes: []
related: []
sources:
- source.linux-gpio-api
- source.linux-gpio-lifetime
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-19'
---

[English](overview.md) | [简体中文](overview.zh-CN.md)

# GPIO 应用开发

用户指定连接器和物理针脚，依据匹配板级资料解析，不使用未经验证的 line-name 代替 pin-to-net。运行时定位 gpiochip 与 line，检查 consumer/mux，并让实际独占申请处理竞争。

优先 GPIO character device 和与已装版本匹配的 libgpiod/API；使用已有 LED/input 子系统管理的功能时通过该子系统。输出方向与初始值应同次配置，物理高/低与 active-low 逻辑区分。

命令或 daemon 持有 line request 才能定义保持生命周期；请求释放后用户态不再保证输出电平。异常安全态需硬件配合。输出回读也不独立证明外部电压。

参考：[Linux GPIO API](https://docs.kernel.org/userspace-api/gpio/chardev.html)、[请求生命周期](https://docs.kernel.org/userspace-api/gpio/gpio-v2-get-line-ioctl.html)。
