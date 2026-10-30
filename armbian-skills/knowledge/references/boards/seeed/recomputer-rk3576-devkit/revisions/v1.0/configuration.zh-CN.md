---
schema_version: '1'
id: board.seeed.recomputer-rk3576-devkit.v1.0.configuration
kind: board_guide
applies_to:
  board_ids:
  - seeed.recomputer-rk3576-devkit
  hardware_revisions:
  - v1.0
required_refs:
- board.seeed.recomputer-rk3576-devkit.overlays
preconditions: []
refines: []
excludes: []
related: []
sources:
- source.local-board-config
- source.local-bootscript
- source.local-overlays-note
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-19'
---

[English](configuration.md) | [简体中文](configuration.zh-CN.md)

# 镜像配置和启用前检查

Host board 配置声明 vendor/edge；vendor 指向 `rockchip/rk3576-recomputer-rk3576-devkit.dtb`，非 vendor 分支改用 `rockchip/rk3576-recomputer-devkit.dtb`。当前分支需结合实际内核、启动配置和来源核对。启动脚本还可能使用 EEPROM 路由或 `.dist` 回退，不能将配置的 fdtfile 当作实际加载文件证明。

EEPROM 的前六字节 magic 为 `rk35xx`，后四字节 `00A0` 路由到本板，`01A0` 路由到 Module Dev Kit；前十字节足够检查。该路由码不等于 PCB V1.0，完整 EEPROM 不应作为通用 probe 输出。若实际内容不符合路由格式，保持未知，不修改EEPROM来迎合启动脚本约定。

`overlay-inventory.yaml` 逐个记录 Host 找到的 overlay。启用前核对目标上的 DTBO 是否实际存在、当前 overlays、boot 路径、资源冲突与精确 pinctrl，再决定修改。不要为了资料填充修改 overlays 或重启。

特别注意：uart5 overlay 会禁用 spi3；CAN0/1、UART3、PWM2 等使用不同 pinctrl，不能机械套用物理针脚标签。恢复应保留原启动配置并使用实际镜像的启动方式；Secure Boot FIT 与普通文件启动不能共享未经验证的配置流程。

DTBO文件存在不等于当前已启用；从当前运行DT与启动路径分别核对。
