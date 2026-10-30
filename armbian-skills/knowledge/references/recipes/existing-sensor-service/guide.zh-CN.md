---
schema_version: '1'
id: recipe.existing-sensor-service.guide
kind: recipe_guide
applies_to:
  capabilities:
  - i2c
  operations:
  - sensor.read
required_refs:
- recipe.existing-sensor-service
preconditions: []
refines: []
excludes: []
related: []
sources: []
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-19'
---

[English](guide.md) | [简体中文](guide.zh-CN.md)

# 扩展已有采集服务

检查已有业务/采集入口，保留原语言/构建方式；准备经确认传感器协议与外部总线。新增读数、时间戳、过期/错误状态并接入原 API，长期持有资源由单一采集任务负责。验收实际响应、断开/恢复、超时和原业务回归；部署使用服务真实用户。当前没有指定器件、真实项目或硬件，因此没有可直接执行的寄存器/地址默认值。
