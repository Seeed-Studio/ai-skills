---
schema_version: '1'
id: stack.rockchip-rknn.integration
kind: stack_guide
applies_to:
  capabilities:
  - npu
  stack_ids:
  - rockchip-rknn
  soc_ids:
  - rockchip.rk3576
  - rockchip.rk3588
required_refs: []
preconditions: []
refines: []
excludes: []
related: []
sources:
- source.local-kernel-config
- source.cached-vendor-dts
- source.rknn-project
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-30'
---

[English](integration.md) | [简体中文](integration.zh-CN.md)

# Rockchip RKNPU + compatible RKNN runtime: integration

先核对当前目标 driver/runtime 与模型目标，再按用户语言选已有绑定、C ABI/FFI 或原服务接口。转换、校准和运行分别处理；不直接套用外接 RK182x 案例。

使用官方仓库的明确tag/文件摘要，记录模型由哪个Toolkit版本转换、目标SoC、实际runtime/header/driver与应用架构。master或最新版本不代表设备安装版本；已有模型/绑定优先沿用项目，示例版本不成为未来组合白名单。

按实际应用环境选择依赖分支：

| 证据 | runtime 状态 | 下一步 |
| --- | --- | --- |
| 包/缓存没有条目，应用路径/环境未检查 | unknown | 找应用配置/加载的 runtime，不要求先安装 |
| 找到应用 runtime | 已识别，兼容性/访问仍待查 | 复用并记录路径/版本与实际加载结果 |
| 确认该应用环境缺依赖或存在未解决的加载失败 | 该依赖/加载条件 needs-setup | 准备匹配的任务局部依赖，或修复查找/访问；不直接推导需换驱动 |

开头结论、状态表和建议动作保持同一证据等级。后文补一句私有库未查，不能合理化开头断言 runtime 缺失。应用/模型尚未提供时，说明缺少的输入和有条件路线，不假设必须安装。对有界运行选择该版本支持的后端证据；负载上升是可选旁证，不是每次有效推理都必须满足的条件。

结论句式对照：开头不写「真正缺的是用户态 runtime」「板上没有 runtime」这类跨来源判定；写「内核侧已确认（驱动已绑定）；用户态 runtime 在已查的〈逐项列出来源〉未发现，是否缺失取决于应用私有路径/容器/SDK 目录检查」。装 runtime 的步骤按「先在应用实际环境查，确认缺失才装」顺序表述，不写成无条件待办，也不写成「唯一要补的东西」。runtime 与驱动的配套按该驱动版本对应 release 文档标注选择，不以「版本较新即可」代替配套说明；SDK 的 perf/profiling 入口名以实际安装的版本为准，不凭记忆写工具名。

运行时query真实输入输出数量/shape/layout/dtype，不用原ONNX属性盲填RKNN输入；pass_through、输入归一化和输出float转换明确。保留原业务入口，持续应用按语言异步生命周期管理，释放output/context，错误/取消检查实际owner退出。
