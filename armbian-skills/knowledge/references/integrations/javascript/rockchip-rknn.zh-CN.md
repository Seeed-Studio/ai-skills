---
schema_version: '1'
id: integration.javascript.rockchip-rknn
kind: integration
applies_to:
  languages:
  - javascript
  capabilities:
  - npu
  stack_ids:
  - rockchip-rknn
  soc_ids:
  - rockchip.rk3576
  - rockchip.rk3588
required_refs:
- integration.javascript.guide
- stack.rockchip-rknn
preconditions: []
refines: []
excludes: []
related: []
sources:
- source.node-child-process
- source.rknn-v232-sdk
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-20'
---

[English](rockchip-rknn.md) | [简体中文](rockchip-rknn.zh-CN.md)

# JavaScript接入Rockchip RKNN

保留原JS入口、业务score/错误语义、package与测试。RKNN提供C/C++与PythonAPI不意味着应用必须改成Python；可按项目选择已有绑定、N-API addon、FFI、原服务接口或有限native worker。核对Node ABI/架构、C头文件/runtime及目标模型；外部进程不是每帧媒体任务的默认方案。

同步业务可保留CPU接口，新增明确的异步硬件入口；不要用同步spawn阻塞事件循环。若桥接进程，使用参数数组、shell=false、有界输入/输出、超时/AbortSignal与error/close处理。终止请求和实际进程退出分开记录，旧owner未退出前不叠加重试；SIGKILL或内核不可中断I/O不能保证用户态destroy或立即停止。

固定模型摘要、目标SoC、布局/shape/dtype、量化与预处理。ONNX原始属性不等于转换后RKNN属性；运行时query后按实际格式提交数据，明确pass_through及输出转换。不能只凭qnt_type枚举认定INT8，须核对实际dtype、构建设置及字段含义。不同通道/布局需要真实重排，单通道连续存储相同的特例不能套用RGB。

调用成功、存在节点或文本里出现“NPU”都不足以通过。使用已知输入/期望输出检查数值；逐算子核对Target/计算cycles与实际NPU设备关联。初始/最终CPU回归、缺runtime/模型、错误target、取消/释放分开记录。回退必须显式返回backend=cpu及原因；不能把基线或fallback当NPU结果。输入/输出转换在CPU不等于神经网络计算全部回退，按阶段说明。

runtime可能打开primary DRM card而非render节点；两者均从sysfs关联驱动，实际FD作证，不硬编码card2/renderD130。root shell枚举不足以证明实际服务/容器访问，按最终运行用户检查实际SDK所需节点。
