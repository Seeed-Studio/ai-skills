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
updated_at: '2026-11-03'
---

[English](overview.md) | [简体中文](overview.zh-CN.md)

# GPIO 应用开发

用户指定连接器和物理针脚，依据匹配板级资料解析，不使用未经验证的 line-name 代替 pin-to-net。运行时定位 gpiochip 与 line，检查 consumer/mux，并让实际独占申请处理竞争。

优先 GPIO character device 和与已装版本匹配的 libgpiod/API；使用已有 LED/input 子系统管理的功能时通过该子系统。输出方向与初始值应同次配置，物理高/低与 active-low 逻辑区分。

命令或 daemon 持有 line request 才能定义保持生命周期；请求释放后用户态不再保证输出电平。异常安全态需硬件配合。输出回读也不独立证明外部电压。

参考：[Linux GPIO API](https://docs.kernel.org/userspace-api/gpio/chardev.html)、[请求生命周期](https://docs.kernel.org/userspace-api/gpio/gpio-v2-get-line-ioctl.html)。

给出接线或输出步骤前，把所选针脚的**排针侧电压、SoC侧电压和转换路径**写入答复，不能只留在针脚表中。按[接线指导](../../common/wiring-diagrams.zh-CN.md)说明端点与极性。LED 接电源能亮不证明 GPIO/转换器具备相应驱动电流；串联电阻也不自动证明可以直接驱动。

短时 CLI 检查按[有限时 GPIO 指导](../../recipes/bounded-gpio-command/guide.zh-CN.md)交付与版本匹配的有限保持、取消和释放检查。负载规格缺失可以阻止直驱 LED，但不阻止先交付带明确前提的空载测压步骤；实际接线、仪表、mux和归属条件确认前不能执行。
