---
schema_version: '1'
id: capability.npu.verification
kind: capability_guide
applies_to:
  capabilities:
  - npu
required_refs:
- capability.npu
- common.verification
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

[English](verification.md) | [简体中文](verification.zh-CN.md)

# NPU 验证

固定模型摘要/目标、输入 shape/layout/dtype、量化和预处理，使用已知输入与期望结果比较。记录 driver/runtime、真实设备/执行后端和语言桥接的 ABI。宿主示例通过后仍需测试实际服务/容器；CPU fallback 单独记录。

转换前ONNX属性与实际runtime属性分别记录；query后决定输入布局/转换，不以一个量化枚举代替dtype与数据解释。SDK返回成功也可能伴随转换错误，须检查日志及已知数值。出现“NPU”字样不等于计算在NPU；关联实际应用/runtime/设备与当前版本支持的 profiling 或追踪。可用时看编译图的计算 Target/cycles，考虑融合、优化节点和不支持的查询，不要求每个算子都有正 NPU cycles。输入/输出胶合或预处理在CPU应单独说明，不混同全模型CPU回退。负载采样作旁证，不强求采到正值，也不单独证明某进程执行。

“未发现”的措辞按来源范围：标准库路径、包缓存或 pip 清单里没有 runtime，只支持“在这些来源未发现”；私有安装路径、SDK 目录、容器或另一用户环境未查时，结论保留“未发现，可能存在于未查位置”，禁止升级为“板上没有 runtime”或把它列为唯一缺失项，也不据此把安装某软件写成必经步骤。记录实际查过的来源清单，缺失结论随来源范围表述。补 runtime 的步骤顺序是「先在应用实际运行环境（venv/rpath/容器镜像）查，确认缺失才装」：查是第 1 步，装不是；给安装建议时取该驱动版本 release 文档标注配套的固定 tag 并附校验和；结尾状态句不用「运行时是空白」这类跨来源概括，按来源范围收尾。

root 或宿主会话的采集不证明实际应用可访问：不同用户、容器或服务的设备节点、库路径与权限可能不同，应用访问在应用真实运行环境内核对。负载采样两个方向都保留：短任务可能漏采，采不到非零负载不能反推“在 CPU 运行”；采样窗口内负载不变也只是旁证，归因需与该版本支持的 profile/tracing 或执行后端输出相互印证，单独采样结果不写成确定回退。
