---
schema_version: '1'
id: capability.i2c.aht20
kind: capability_guide
applies_to:
  capabilities:
  - i2c
required_refs:
- capability.i2c
- common.linux-device-access
preconditions: []
refines: []
excludes: []
related:
- stack.linux-i2c-dev.detection
sources:
- source.asair-aht20-v11
- source.linux-i2c-api
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-11-03'
---

[English](aht20.md) | [简体中文](aht20.zh-CN.md)

# AHT20 I2C地址、状态与准备证据

仅用于已确认的AHT20协议。板级路由、适配器身份、模块供电/信号、当前地址归属与原应用执行用户分别核对。裸传感器供电范围不代表模块或板卡信号也允许该电压。

## 地址字节不是命令

制造商V1.1第8页§5.3与时序图将七位地址和读写位分开。§5.4“发送0x71”应在该上下文解释：

| 含义 | 数值 | Linux用户态解释 |
|---|---|---|
| 七位从地址 | `0x38` | 通过I2C_SLAVE或消息地址指定 |
| 线上写地址 | `(0x38 << 1) + 0 = 0x70` | 适配器生成，不是payload |
| 线上读地址 | `(0x38 << 1) + 1 = 0x71` | 适配器生成，不是payload |
| 状态字节 | 返回的一字节 | 直接读取，前面不写`0x71` payload |

使用i2c-dev时，先将`I2C_SLAVE`设为`0x38`，再直接读一字节；`write(0x71); read(1)`不是该状态操作。仅在当前接线/归属、实际用户权限确认且该器件访问已获授权后，兼容的`i2ctransfer`单次读消息对应为：

```sh
: "${bus:?填写已核对的当前适配器编号}"
i2ctransfer -y "$bus" r1@0x38
```

该操作**不能**写成`w1@0x38 0x71 r1`。事务含`w1`就是写payload，不能因为名为“检查”就称为只读。仅列准备缺口不需要`-f`、盲扫、复位或初始化。器件读仍是主动事务，不是被动元数据。

## 分清状态、转换与验收

状态bit3表示校准使能、bit7表示busy；任意状态值/ACK不能单独唯一识别传感器。校准状态要求的初始化（`BE 08 00`）和转换触发（`AC 33 00`）都是**写操作**，不是状态查询，不属于只查元数据。真正实现读取器时，遵循手册时序、有界busy等待、独立完整帧CRC后再解码；错误后不复用旧样本。不把这些操作码直接用于AHT10/AHT21或其他未经核实器件。

审查一条命令，只需说明该事务、有依据的替代和证据边界，不追加用户未请求的初始化、转换或复位命令序列。未文档化payload的影响未知，不猜它会被忽略、无害或保证不改变状态。

没有`N-0038`注册项，只表示该快照未列出相应内核客户端。已注册地址不同（如0x22、0x51）不证明0x38没有其他用户或竞争；不能由该列表推出“无冲突”“不会争用驱动”或“可安全直接访问”。缺少观测时保留当前归属未知，已有授权的请求前核对；busy、权限或I/O错误停止，不强制访问。该注册项缺失本身不证明地址可用、历史上从未应答或当前用户有权限。“未采集到应答证据”不同于“传感器从未应答”。root发现不证明服务/容器可访问，状态读取也不能验收温湿度精度、带载、上拉/时序余量或经过校准的供电电压。

**只做准备判断**时，缺失的实际用户/节点访问和物理测量仍为未知；最小下一步可以是原项目的运行身份/节点权限，而非总线事务。其他物理/功能条件尚未测量时，摘要不能把缺口缩成“仅应用访问”或“仅电压/ACK”。`id`、节点列表和`test -r/-w`只预测权限，成功不等于实际open、API事务或应用访问验收；只陈述该有限结论和下一项已有授权的步骤，原访问事实仍保留未知。给SoC电源域供电的电阻不是SDA/SCL信号串联电阻，按所选针脚的真实路由陈述；不凭假设的模块上拉推导并联阻值或时序裕量。

来源：[ASAIR AHT20 V1.1，第8页](https://files.seeedstudio.com/wiki/Grove-AHT20_I2C_Industrial_Grade_Temperature_and_Humidity_Sensor/AHT20-datasheet-2020-4-16.pdf)、[Linux i2c-dev地址/读取语义](https://docs.kernel.org/i2c/dev-interface.html)。仅是协议与资料依据，不是当前目标或功能验收。
