---
schema_version: '1'
id: integration.javascript.linux-gpio-chardev
kind: integration
applies_to:
  languages:
  - javascript
  capabilities:
  - gpio
  stack_ids:
  - linux-gpio-chardev
required_refs:
- integration.javascript.guide
- stack.linux-gpio-chardev
preconditions: []
refines: []
excludes: []
related: []
sources:
- source.linux-gpio-api
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-19'
---

[English](linux-gpio-chardev.md) | [简体中文](linux-gpio-chardev.zh-CN.md)

# javascript / linux-gpio-chardev

GPIO 先确定项目使用内核 GPIO UAPI 还是 libgpiod；两者 ABI 和绑定版本分别核对。request 对象需由一个 owner 持有到时限/取消，初始值和方向一并配置，busy 返回业务错误而非强占。

具体库与锁定版本在用户项目实施时查证；本条是接入与验收约束，不声明已验证任何语言绑定。参数配置使用已解析设备身份/line，不能把其他板卡节点硬编码进源码。
