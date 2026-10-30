---
schema_version: '1'
id: stack.linux-gpio-chardev.recovery
kind: stack_guide
applies_to:
  capabilities:
  - gpio
  stack_ids:
  - linux-gpio-chardev
required_refs: []
preconditions: []
refines: []
excludes: []
related:
- stack.linux-gpio-chardev.integration
- stack.linux-gpio-chardev.verification
sources:
- source.linux-gpio-api
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-19'
---

[English](recovery.md) | [简体中文](recovery.zh-CN.md)

# GPIO 生命周期、退出与恢复

释放request、软件方向/配置恢复、物理电压和外部器件状态是不同结果。`released`或consumer为空只证明没有该owner，不能写成“恢复原电平/方向”。

## 操作前记录

记录当前目标、控制器身份和局部offset、原方向、可读的bias/active-low/mux/owner、外接电路及任务约定的退出值。未读到的字段保留未知，软件配置不代替测量。操作范围应与用户目标相符；已有服务持有资源时使用其接口或修改其实现，不为恢复而抢占它。

## 正常结束、取消与失败

按应用约定持有request，输出初值尽量随请求原子配置。结束/取消时的输出值由电路与任务决定，不能把本例“低200ms”扩展为所有平台/负载的默认安全态。清理失败要报告并尽力释放；SIGKILL或掉电无法执行用户态清理。重连后先确认原进程/request是否还在，不直接重复输出。

## 恢复已知状态

任务要求恢复时，仅对已知且仍适用的原状态安排动作；重新检查当前owner/mux，并用实际独占申请处理竞争。原方向/bias/mux未知时，不通过额外请求猜测恢复。恢复动作本身可能改变电平，应考虑外接电路，必要时继续获取实际条件；不要因此阻止不依赖该条件的代码工作。

这不是通用“运行一次gpioget就恢复”的方法。gpioget会申请line，某些版本默认强制input；如当前版本的 `--as-is` 表示保留方向，就不能用它完成上述方向恢复。CLI选项必须核对当前版本，不把gpioget当作被动inventory。

## 验收记录

分别记录保持窗口内的仪表值、退出/信号/释放事件、恢复动作与最后metadata、以及恢复后是否再次物理测量。无法测到短暂清理脉冲就记录未测量，不能用软件回读补成波形通过。恢复方向后没有重测的电压保持未知。
