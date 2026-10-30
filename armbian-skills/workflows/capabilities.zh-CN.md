# Armbian 设备能力

帮助用户了解设备能做什么、通过哪个接口、还需准备什么，以及如何接入应用。只查询能力时交付带证据的解释和下一步。

## 资料与目标

从本包 [资料入口](../references/INDEX.zh-CN.md)、[身份规则](../references/common/identity.zh-CN.md) 开始，运行 `python3 scripts/armbian.py info` 读取实际版本。历史报告不是当前设备状态。

区分工作区、构建主机和运行设备。使用用户指定且已授权的本机、SSH 或终端连接器，不规定某一种 MCP；连接失败不能改在 Host 操作硬件。以当前 compatible、系统/kernel 和硬件身份确定 board/SoC 候选；未知 revision 保留未知，同 SoC 不能继承另一载板排针/电气。

## 采集与匹配

Python 3 可用时，在已确认目标运行本包 `scripts/probe_device.py`。远程可从操作者终端执行 `ssh TARGET 'python3 -' < scripts/probe_device.py`，认证由正常 SSH 或连接器处理，不将凭据写入命令/文件。没有 Python 时按任务使用已有只读接口，不默认安装依赖。

probe 只做有界元数据采集，不申请 GPIO、不扫描 I2C、不做器件事务、服务/overlay 变更或加速测试。工具缺失、拒绝访问、截断或超时均保留为未知，不能据此断言硬件不支持。EEPROM 识别是显式可选项，仅在已确认适用时使用。

按 [匹配契约](../references/common/reference-matching.zh-CN.md) 传入当前已采集事实和任务 JSON，缺失值保留 null；无需持久化时用 `--facts -` 从 stdin 读取：

```bash
python3 scripts/armbian.py match --facts /path/to/task-facts.json
```

程序只在操作者主机筛选本地资料，Python 标准库即可，不连接设备。按任务读 board/revision、capability、platform 和实际 stack；`matches` 不是硬件可用声明，冲突/歧义不能取第一项。

## 能力解释

按 [四层证据](../references/common/capability-evidence.zh-CN.md) 分别报告硬件/接口、系统就绪、实际应用可访问和功能实测，逐操作使用 available/needs-setup/busy/unsupported/unknown。注明来源、采集时间、目标/版本与未测试项。

- 排针：区分连接器物理位置、协议/电气、SoC pad 和 Linux 控制器/line。官方标注与运行时PIN标签冲突时并列记录，不按标签输出；控制器label不是固定设备路径，按[GPIO识别](../references/stacks/linux-gpio-chardev/detection.zh-CN.md)解析当前候选。
- 加速：NPU、GPU 图形/计算、VPU 解码/编码分别判断。节点、库、功能列表或标称性能不能证明真实后端。
- 应用：root shell 枚举不证明服务/容器可访问。已有项目将能力关联到采集模块、业务 API 或媒体流水线。
- 未知平台/组合继续用通用接口查证，缺少排针资料不阻止独立加速调查或离线开发。

先用“可做什么、接口、准备条件、下一步”解释，再按需展开 API/节点。只询问影响任务的缺失条件，不默认运行有副作用的测试或部署服务。

任务需要用户接线或测量时，按[接线图指南](../references/common/wiring-diagrams.zh-CN.md)给出本次板卡/连接器的高亮针脚图、外设端子与电压接线表；针脚行列、1脚位置和观察面必须与对应主板一致，按板级wiring-layout或可靠实物图绘制；方向依据不足时只给逐线图和接线表，不画猜测的定位图。

查询物理针脚时优先使用 `scripts/armbian.py pins`，按精确板卡/revision/连接器及所需物理位置读取，保留共网、冲突和所有电气约束；不先打印整份表。

先给本次结论、交付、检查结果与下一步。长步骤放进项目文档并链接。验收数值以现有业务条件为依据；缺少周期/SLA等依据时保留参数，不把示例值变成默认要求。

涉及 LED 等负载接线时，GPIO 标称电压不能证明驱动电流能力。最大电流或元件规格未知时，不保证直驱可行，也不指定经验电阻值；可给符合实际规格的外部驱动器信号端点方案，或询问缺失的元件/电流依据。
