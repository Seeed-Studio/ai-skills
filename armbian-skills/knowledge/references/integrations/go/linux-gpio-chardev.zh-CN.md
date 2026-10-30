---
schema_version: '1'
id: integration.go.linux-gpio-chardev
kind: integration
applies_to:
  languages:
  - go
  capabilities:
  - gpio
  stack_ids:
  - linux-gpio-chardev
required_refs:
- integration.go.guide
- stack.linux-gpio-chardev
preconditions: []
refines: []
excludes: []
related: []
sources:
- source.linux-gpio-api
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-19'
---

[English](linux-gpio-chardev.md) | [简体中文](linux-gpio-chardev.zh-CN.md)

# go / linux-gpio-chardev

GPIO 先确定项目使用内核 GPIO UAPI 还是 libgpiod；两者 ABI 和绑定版本分别核对。request 对象需由一个 owner 持有到时限/取消，初始值和方向一并配置，busy 返回业务错误而非强占。

## 接入已有业务

保留原模块、入口和测试，给新增硬件路径配置开关与明确错误。在硬件不可访问时按业务要求降级；例如硬件不可用时，可按项目约定保留独立的health和样本业务。不把所有初始化失败都扩大为整个服务不可用，也不在需要硬件才能成立的业务上伪报成功。

HTTP等短请求若启动跨请求持续的操作，不直接沿用会在handler返回后取消的request context。由应用生命周期管理限时操作，保留操作标识与取消入口；应用关闭也取消并等待清理。同步短操作仍可使用请求context，不为它强加后台任务协议。

同一资源的owner保持到配置恢复/释放完成，清理期间仍视为busy；预检之外仍处理实际申请竞争。软件状态区分启动、保持、结束、取消和清理失败，回读注明观察阶段，不能将开始时的值当成持续测量。恢复只使用已知且适合电路的原状态，见[恢复流程](../../stacks/linux-gpio-chardev/recovery.zh-CN.md)。

若直接定义Go ioctl结构，需要按目标架构核对布局、偏移及请求编号；应对照目标C头文件检查结构体大小、对齐和ioctl编号；不同架构或metadata格式需分别验证，不把某块板的pinmux索引当作通用规则。

验收覆盖原业务在操作前/中/后的行为、同实例和外部owner冲突、API取消、应用退出、硬件不可用路径，以及实际运行用户。pinmux预检拒绝不能证明设备ioctl权限检查的结果。物理电压由仪表单独证明，详见[GPIO栈验收](../../stacks/linux-gpio-chardev/verification.zh-CN.md)。
