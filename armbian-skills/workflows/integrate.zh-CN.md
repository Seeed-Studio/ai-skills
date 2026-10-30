# Armbian 硬件应用开发

交付用户要求的应用功能。已有应用扩展、新手协助和新项目使用同一工作流；语言和运行形态由项目决定。

## 理解项目与目标

读取仓库约定、入口、依赖/锁文件、硬件访问层、测试和部署方式，保留用户改动。按 [项目集成](../references/common/project-integration.zh-CN.md) 找到原业务扩展点；独立硬件 demo 不能替代应用内集成。不因缺少绑定而重建应用或换语言。

确认工作区、构建环境、运行设备、实际用户/容器和交付范围。先从项目/会话取得条件，避免重复询问。新手先解释接口用途、准备和预期现象，不默认 Python 或服务化。

从本包 [资料入口](../references/INDEX.zh-CN.md) 与 `python3 scripts/armbian.py info` 的版本摘要读取版本，已有能力证据按目标/内核/overlay/runtime/应用环境的变化刷新。其他 Skill 不必安装，不假定存在自动调用其他 Skill 的 API。

## 匹配与集成计划

按 [匹配契约](../references/common/reference-matching.zh-CN.md) 提供本次事实和任务：

```bash
python3 scripts/armbian.py match --facts /path/to/task-facts.json
```

按需读 capability、精确 board/revision、platform、实际 stack、项目语言 integration 和适用 recipe。结论关联到资料 ID/版本和当前证据；历史观测不能补齐当前事实。未知平台可用通用接口与官方资料继续开发，未收录不等于不兼容。

形成规模合适的计划：原业务入口与数据流、资源 owner、接口/依赖、已知与未知条件、异常/取消、构建部署、验收回归和恢复。计划不是额外批准流程，已有授权持续有效。

## 实现与交付

- 在原项目完成代码、配置与业务接入，沿用构建/错误/配置约定。新项目才建立必要结构，不停在工具说明或“增加 adapter”的建议。
- 按项目选原生绑定、Linux API、厂商 C API/FFI 或既有服务接口；核对版本、ABI/架构与生命周期，不强制统一 CLI、SDK 或控制 daemon。
- 明确打开/关闭、并发、超时、取消和释放。已有应用持有硬件时使用其接口或修改其内部实现，不旁路抢占；预检不能消除实际申请的竞争。
- GPIO 输出要有可靠板型/revision/连接器/电气/控制器映射和当前 mux/consumer。未知时暂停对应输出，继续可完成代码。保持由request生命周期定义，释放后不保证电平或原方向；需要恢复时记录已知原状态，按[恢复流程](../references/stacks/linux-gpio-chardev/recovery.zh-CN.md)处理，不无条件拉低或切input。
- 通信按器件协议、电气与实际总线接入，不扫描内部 I2C 或强制访问驱动地址。UART TTL/RS232/RS485、CAN TX/RX 与 CAN_H/L 分开说明。
- NPU/GPU/VPU 按实际模型/媒体/API 和 driver/runtime 集成，分别验证输出与真实后端，CPU/软件回退不算硬件通过。

细节按需读 [能力资料](../references/INDEX.zh-CN.md) 和对应语言 integration。持续硬件 I/O 不阻塞业务事件循环；短命令不扩大成通用控制框架。

按 [部署](../references/common/deployment.zh-CN.md) 与 [验收](../references/common/verification.zh-CN.md) 完成任务相关阶段：构建、项目测试、旧功能回归、已授权部署与硬件验收。持续操作检查原业务在操作前/中/后的行为；具体语言的异步生命周期和错误接入按对应integration处理。短命令无需完整服务流程。

设备不可达时完成离线实现与业务测试，明确实机未验证。人工接线/测量给出位置、动作与预期，不伪造已完成。

交付实际改动/业务接入位置、依赖/构建/运行方法、通过的验收与回归、未验证项及恢复。跨阶段记录目标、产物摘要、变化和证据，不含凭据。

任务需要用户接线或测量时，按[接线图指南](../references/common/wiring-diagrams.zh-CN.md)给出本次板卡/连接器的高亮针脚图、外设端子与电压接线表；针脚行列、1脚位置和观察面必须与对应主板一致，按板级wiring-layout或可靠实物图绘制；方向依据不足时只给逐线图和接线表，不画猜测的定位图。

先给本次结论、交付、检查结果与下一步。长步骤放进项目文档并链接。验收数值以现有业务条件为依据；缺少周期/SLA等依据时保留参数，不把示例值变成默认要求。
