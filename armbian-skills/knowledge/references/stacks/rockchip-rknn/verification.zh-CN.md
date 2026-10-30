---
schema_version: '1'
id: stack.rockchip-rknn.verification
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

[English](verification.md) | [简体中文](verification.zh-CN.md)

# Rockchip RKNPU + compatible RKNN runtime: verification

固定模型/输入与正确性标准，保留 runtime 设备执行证据和端到端/推理耗时。当前内核driver、用户态runtime、绑定、模型与功能就绪需在目标检查，静态资料不提供本次结果。

对用户自己的程序分别验收：

| 核查 | 证据 |
| --- | --- |
| 应用访问 | 实际服务用户/容器加载已记录的 runtime，并能访问 SDK 实际使用的 DRM/设备节点；root 枚举或另一 SDK demo 不代替该项 |
| 输出正确性 | 该程序用固定输入和已记录的预处理运行，输出与已知期望及误差界比较 |
| 计算归因 | 关联该次运行与版本支持的 profiling/追踪或执行后端输出；支持时看计算 Target/cycles，并考虑图融合/优化 |

runtime 可用和模型已转换是前提，不是验收结果。最小证明清单及结尾摘要保留上述三项，不缩成「装 runtime＋转模型＋看负载」。归因查询不受支持时该证据仍待补，不要求每个算子行或某个特定 API 都存在。CPU 预处理/输入输出与整模型 CPU 回退分别说明，显式回退单独记录。

计数仅作可选旁证：零值可能漏采短任务，正值可能来自其他进程。负载或设备 FD 打开本身都不证明输出正确及计算归因。结束/错误/取消后检查 context/进程/FD，不能用 power 状态代替资源释放。
