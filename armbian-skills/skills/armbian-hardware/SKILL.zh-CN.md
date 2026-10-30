---
name: armbian-hardware
description: 识别 Armbian 设备能力，在现有应用中集成硬件功能，部署并诊断外设与 NPU/GPU/VPU 应用。
---

# Armbian 硬件应用

保留项目语言、业务入口、构建与部署约定，完成用户请求。区分工作区、构建主机和实际运行设备；目标不可达时继续独立的离线工作。

按任务只读相应工作流：[能力说明](workflows/capabilities.zh-CN.md)、[应用集成](workflows/integrate.zh-CN.md)、[部署](workflows/deploy.zh-CN.md)、[验证诊断](workflows/verify.zh-CN.md)。直接从用户所需阶段开始，必要时才读取下一工作流，不自动执行整套流程。

诊断先回答当前问题，再给用户范围内最小的有效核查。观测、原因推断和未验证效果分别说明；有限查找没有结果不等于不存在，硬件已注册/启用不等于物理运作或已被应用使用。在据此给安装、接线或负载建议前，按[证据解释](references/common/verification.zh-CN.md)判断结论能到哪一层。

先在技能目录运行 `python3 scripts/armbian.py info` 获取版本、来源和验证范围，不输出完整 manifest 哈希清单。随后运行 `python3 scripts/armbian.py search "容器视频没有硬解"` 找候选资料；以 `match --facts /project/task-facts.json` 判断适用条件，以 `explain --ref common.identity --facts /project/task-facts.json` 查看原因和必要依赖。以上仅在主机离线检索，需要 Python 3.9+ 标准库，不连接或控制设备。已有事实时搜索也应加 `--facts`，避免重复整理或猜测事实。搜索分数不证明身份、针脚、电压或兼容性。按返回的绝对 `read_path` 读取资料；`path` 相对于 `reference_root`，不是技能根目录。读取选中资料及必要依赖，遵循[匹配契约](references/common/reference-matching.zh-CN.md)。缺失事实保留未知，不套用其他载板针脚。

针对排针位置，运行 `python3 scripts/armbian.py pins --board seeed.recomputer-rk3588-devkit --revision v1.0 --connector J10 --pins 23 40` 定向查看完整选中记录、共网关系、电气约束和来源，替代整份针脚表读取。只使用任务有依据的精确板卡、revision、连接器选择器；它们不证明当前设备身份。已有当前事实可加 `--facts`；未知组合不套用相似板卡。驱动电流和元件规格未知时，不由标称电压推导 GPIO 直驱负载/LED 可行或指定电阻值。用 explain 查看必要依赖，遇缺失或冲突再读完整资料。

没有 Python 时直接读工作流与[导航](references/INDEX.zh-CN.md)，不为查询默认安装依赖。可按能力工作流，经已有授权的连接执行包内只读 `scripts/probe_device.py`；采集器不扫描总线、不申请 GPIO、不执行加速负载。

长任务可复用原项目记录，或按需将[事实模板](templates/task-facts.json)与[方案模板](templates/plan.md)保存在项目 `.armbian/` 下；简单问答无需建目录。保留事实来源、目标、时间与知识版本，不保存凭据；目标、内核/镜像、路由、用户/容器、应用或输入变化后刷新相关观测。已有事实和授权跨阶段复用，不逐阶段重复确认。

分别说明硬件接口、系统准备、实际应用访问和功能结果；区分静态资料、用户报告、软件观测、离线测试与物理测量。节点存在、命令成功或输出正确不能单独证明实际后端或电气行为。需要接线时读取[接线规范](references/common/wiring-diagrams.zh-CN.md)。

完成授权工作和相关业务回归，交付改动、构建运行、验证范围、未知项与恢复方法。主答复先给结论、改动、验证和下一步；较长部署/恢复细节写入项目交付文档并链接，不在主答复重复全文。验收时间、样本数与阈值来自项目 SLA、采样周期或权威要求，未明确时保留待确认，不编造默认值。用 info 获取版本摘要，完整 manifest 仅在审计文件清单时读取。不虚报设备连接或物理验收。
