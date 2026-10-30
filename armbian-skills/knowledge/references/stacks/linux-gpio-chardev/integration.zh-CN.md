---
schema_version: '1'
id: stack.linux-gpio-chardev.integration
kind: stack_guide
applies_to:
  capabilities:
  - gpio
  stack_ids:
  - linux-gpio-chardev
required_refs: []
preconditions: []
refines: []
excludes: []
related:
- stack.linux-gpio-chardev.recovery
sources:
- source.cached-vendor-dts
- source.linux-gpio-api
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-19'
---

[English](integration.md) | [简体中文](integration.zh-CN.md)

# GPIO 应用集成

沿用项目语言与运行形态，根据实际kernel UAPI/libgpiod版本选择原生API、绑定、FFI或已有应用接口；CLI参数须匹配当前工具。不要求Go/Rust/JS经由统一CLI包装层。

明确request的打开/持有/关闭、初值、并发、超时、取消与错误；输出初值尽量与request原子设置。结束值取决于电路，关闭request后不保证电平或方向。需要恢复时，按[生命周期与恢复](recovery.zh-CN.md)记录已知原状态并核验实际恢复结果。

已有service按原业务/事件循环接入，不因硬件I/O阻塞业务。预检不消除占用竞争，实际申请失败按错误返回，不强占内核或共享应用。设备路径由本次控制器身份解析，不写死chip编号或未经验证的PIN标签。
