---
schema_version: '1'
id: common.platform-onboarding
kind: common
applies_to: {}
required_refs:
- common.reference-matching
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

[English](platform-onboarding.md) | [简体中文](platform-onboarding.zh-CN.md)

# 新增平台与资料维护

复用统一入口内的工作流模块，不按板型复制入口。先添加有来源的 platform/board 稳定 ID 与 compatible 候选，SoC 和载板分开；未知 revision 不创建猜测 pinout。新镜像优先补 stack/兼容记录，不复制物理引脚资料。

读取 schemas 中的元数据约定，在 applies_to 填明确条件；必需依赖与 refines 无环，导航可双向。受保护电气/针脚限制不被 recipe 或语言资料解除。新增实际软件 API 时才增加 stack，不根据 SoC 名称自动宣称 runtime 可用。

用精确匹配、缺失字段、别名歧义、revision 冲突、排除及 RK35xx 板型/SoC 差异场景做匹配测试。再选择实际平台应用完成能力识别、实现/集成、部署、物理功能与生命周期验收；没有硬件时明确待验收，fixtures 不计实机通过。

记录来源/版本/摘要、维护者、验证范围和失效条件。只发布经审核的静态知识；验证记录、现场输出与凭据留在项目本地。运行 host 的 refresh_catalog.py、测试及 build_skills.py；更新发布锁后生成完整技能包，独立目录检查完整引用和摘要。

英文.md为规范入口，相邻.zh-CN.md是独立中文翻译，共用同一引用ID和适用元数据，不增加索引条目。保持两种语言一致；索引解析英文文件，包摘要覆盖两种语言。设备标识、针脚名、schema键与来源原件不翻译。
