---
schema_version: '1'
id: references.index
kind: index
applies_to: {}
required_refs:
- common.identity
- common.reference-matching
- common.project-integration
preconditions: []
refines: []
excludes: []
related: []
sources: []
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-29'
---

[English](INDEX.md) | [简体中文](INDEX.zh-CN.md)

# 多平台 Armbian 硬件应用资料入口

本集合提供通用工作流与静态硬件、源码和软件栈资料，当前板卡资料为 reComputer RK3576 / RK3588 DevKit。资料匹配不表示当前设备可用或允许输出；每次任务分别确认硬件接口、系统就绪、实际应用权限和功能结果。

| 任务 | 阅读资料 |
|---|---|
| 用户需要接线或测量 | [接线示意图](common/wiring-diagrams.zh-CN.md)、精确板型/revision及外设资料 |
| 认识设备、解释接口 | [身份](common/identity.zh-CN.md)、[四层证据](common/capability-evidence.zh-CN.md)、匹配的 board/platform 与 capability |
| 扩展已有应用或协助新手 | [项目集成](common/project-integration.zh-CN.md)、实际 stack、语言 integration 和适用 recipe |
| 构建部署与服务维护 | [部署](common/deployment.zh-CN.md)、[设备访问](common/linux-device-access.zh-CN.md)、项目 stack/integration |
| 验证与排障 | [验收方法](common/verification.zh-CN.md)、能力及 stack 的 verification |

## 平台资料

- [RK3576 整机 DevKit](boards/seeed/recomputer-rk3576-devkit/overview.zh-CN.md)：官方40-pin标注、原理图/SoC映射、错误Linux标签差异、overlay候选与软件栈。
- [RK3588 整机 DevKit](boards/seeed/recomputer-rk3588-devkit/overview.zh-CN.md)：精确身份规则、V1.0全部40位置的J10资料映射（23/40脚同网）与软件栈候选。
- [来源索引](sources/index.yaml)：官方硬件资料、API文档和版本化源码依据。未收录不表示不支持。

## 匹配与目录职责

先运行 `python3 scripts/armbian.py info` 确认版本，按[匹配契约](common/reference-matching.zh-CN.md)准备当前事实，再运行 `scripts/armbian.py match`。匹配器仅需Python 3.9+标准库；catalog.json与catalog.yaml同源生成。

索引按ID记录适用条件、文件摘要、必需依赖和导航来源。不同维度AND、同维度OR，条件缺失保持unknown，歧义不取第一项。必需依赖与细化关系无环，导航互链允许；资料细化不自动合并。

common为通用流程，capabilities为接口语义，platforms为SoC差异，boards/revisions为连接器、电气和映射，stacks为实际API/driver/runtime，integrations为语言接入，recipes为工程模式。

未知平台、revision或语言绑定不阻止不依赖它的调查和离线开发。需要物理映射的操作等条件齐备后再做；runtime/API改变后刷新相关证据。

完整技能携带知识集合、工作流、工具与只读 probe，不依赖其他 Skill 或开发仓库。输出留在用户项目本地。本集合不携带方案、评估记录、设备快照、用户测量、凭据、SDK、模型或应用产物。新增平台见[平台维护](common/platform-onboarding.zh-CN.md)。

英文文件为规范入口，相邻.zh-CN.md为中文说明；引用ID、适用条件、结构化YAML与原始图片共用，中文翻译不作为独立资料重复匹配。
