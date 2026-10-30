---
schema_version: '1'
id: common.identity
kind: common
applies_to: {}
required_refs:
- common.capability-evidence
preconditions: []
refines: []
excludes: []
related: []
sources: []
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-19'
---

[English](identity.md) | [简体中文](identity.zh-CN.md)

# 设备身份和跨平台边界

将工程工作区、构建主机、运行设备分别标明。通过已授权的 SSH、终端连接器或本机终端采集；连接失败后不能把硬件命令改在 Host 执行。

Device Tree compatible 精确匹配只提供候选身份，用户提示和名称别名只作线索；对照硬件产品、revision 和不同来源冲突。SoC 匹配不证明载板引出或电气条件。revision 未知时可以读平台资料、编写应用、验证不依赖排针的功能，不能挑最新 revision 套用针脚。

匹配辅助不会读取历史快照补齐当前事实，也不依据 board ID 自动授权输出。对 GPIO 写操作，需要连接器、物理编号/方向、电气、SoC 到控制器/line 的可靠映射，以及当前 mux/consumer。缺少一项时仅暂停依赖它的操作。

重新连接或更改内核、overlay、用户/容器、runtime 后，刷新相应事实；证据注明时间、目标和来源。不要将 SSH 地址、密码、用户文件或原始采集结果提交到共享资料。
