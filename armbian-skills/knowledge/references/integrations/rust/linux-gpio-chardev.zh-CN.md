---
schema_version: '1'
id: integration.rust.linux-gpio-chardev
kind: integration
applies_to:
  languages:
  - rust
  capabilities:
  - gpio
  stack_ids:
  - linux-gpio-chardev
required_refs:
- integration.rust.guide
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
updated_at: '2026-10-20'
---

[English](linux-gpio-chardev.md) | [简体中文](linux-gpio-chardev.zh-CN.md)

# rust / linux-gpio-chardev

GPIO 先确定项目使用内核 GPIO UAPI 还是 libgpiod；两者 ABI 和绑定版本分别核对。request 对象需由一个 owner 持有到时限/取消，初始值和方向一并配置，busy 返回业务错误而非强占。

OwnedFd/Drop能关闭request，配置恢复与物理状态仍需显式设计。需要报告恢复错误时，正常/取消路径显式finish；Drop作为错误/unwind释放的补充，不把Drop写成SIGKILL/掉电保证。清理第一步失败后仍尝试恢复与释放，避免错误传播提前跳过后续动作。

手工UAPI的unsafe边界限定在正确repr(C)结构与有效fd的FFI调用；按目标架构核对布局、偏移、ioctl和libc链接。对Linux x86_64/aarch64核对过的布局不证明其他架构可用；不同项目可选择合适crate/FFI，无需照抄某个实现。

信号回调只通知持有者，在正常流程恢复和释放，不在handler中做文件I/O/分配。原子初值、实际独占竞争、已知原方向与active-low语义分别核实。软件回读注明阶段，人工窗口与默认命令时长分开记录；inspect不能为了“只读检查”暗中申请line。
