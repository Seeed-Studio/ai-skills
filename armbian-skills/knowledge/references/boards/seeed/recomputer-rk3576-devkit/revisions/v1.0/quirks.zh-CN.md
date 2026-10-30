---
schema_version: '1'
id: board.seeed.recomputer-rk3576-devkit.v1.0.quirks
kind: board_guide
applies_to:
  board_ids:
  - seeed.recomputer-rk3576-devkit
  hardware_revisions:
  - v1.0
required_refs:
- board.seeed.recomputer-rk3576-devkit.v1.0.interfaces
preconditions: []
refines: []
excludes: []
related: []
sources:
- source.cached-vendor-dts
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-19'
---

[English](quirks.md) | [简体中文](quirks.zh-CN.md)

# 板级限制与已知差异

- 区分整机 DevKit 与 Module Dev Kit；主板、连接器和 pinout 不能互用。
- 缓存 Linux vendor compatible 带空格，mainline/U-Boot 使用连字符。匹配精确字符串时保留来源，不能“规范化”后丢掉差异。
- 26 个本地 PIN 标签与原理图 J3 pad 不一致；见 [文档映射](schematic-mapping.zh-CN.md)，保留错误标签声明用于追溯，不按标签输出。
- 源码将user-led关联GPIO expander offset 9；确认当前驱动后优先LED子系统，不直接抢占line。
- USB/PCIe 电源复位、Wi-Fi/BT、风扇和 EEPROM WP 是系统资源，默认不开放应用直接控制。
- 相机功能需检查实际sensor、IQ/3A、彩色、曝光/白平衡与输出，不能只确认capture或服务running。
