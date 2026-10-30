---
schema_version: '1'
id: integration.rust.linux-i2c-dev
kind: integration
applies_to:
  languages:
  - rust
  capabilities:
  - i2c
  stack_ids:
  - linux-i2c-dev
required_refs:
- integration.rust.guide
- stack.linux-i2c-dev
preconditions: []
refines: []
excludes: []
related: []
sources:
- source.linux-i2c-api
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-19'
---

[English](linux-i2c-dev.md) | [简体中文](linux-i2c-dev.zh-CN.md)

# rust / linux-i2c-dev

I2C 优先采用已有内核器件驱动公开接口。裸 i2c-dev 需匹配传感器协议、能力检查、地址与组合事务语义；只实现目标器件需要的事务，不扫描内部总线。读数失败/超时保留错误和过期时间戳，不能把上次值当新读数。

具体库与锁定版本在用户项目实施时查证；本条是接入与验收约束，不声明已验证任何语言绑定。参数配置使用已解析设备身份/line，不能把其他板卡节点硬编码进源码。
