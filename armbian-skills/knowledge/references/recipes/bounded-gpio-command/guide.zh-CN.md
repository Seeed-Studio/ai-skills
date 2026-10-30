---
schema_version: '1'
id: recipe.bounded-gpio-command.guide
kind: recipe_guide
applies_to:
  capabilities:
  - gpio
  operations:
  - gpio.output
required_refs:
- recipe.bounded-gpio-command
preconditions: []
refines: []
excludes: []
related:
- stack.linux-gpio-chardev.recovery
sources: []
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-20'
---

[English](guide.md) | [简体中文](guide.zh-CN.md)

# 新手有限时 GPIO 功能

先解释连接器、逻辑电平、外部负载与限流/测量准备。确认可靠 pin-to-net、电气、mux 和当前资源归属后，选择符合项目的命令/程序，持有 request 到时限/取消，记录退出与释放后的行为。验收物理效果、忙/取消/失败路径；默认不创建 daemon 或服务。无可靠映射时可以先完成代码与逻辑测试，但不输出。
