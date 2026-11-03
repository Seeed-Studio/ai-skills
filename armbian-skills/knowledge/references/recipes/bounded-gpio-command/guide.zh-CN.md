---
schema_version: '1'
id: recipe.bounded-gpio-command.guide
kind: recipe_guide
applies_to:
  capabilities:
  - gpio
  operations:
  - gpio.output
required_refs:
- recipe.bounded-gpio-command
preconditions: []
refines: []
excludes: []
related:
- stack.linux-gpio-chardev.recovery
sources:
- source.libgpiod-tools
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-11-03'
---

[English](guide.md) | [简体中文](guide.zh-CN.md)

# 新手有限时 GPIO 功能

先解释连接器、逻辑电平、外部负载与限流/测量准备。确认可靠 pin-to-net、电气、mux 和当前资源归属后，选择符合项目的命令/程序，持有 request 到时限/取消，记录退出与释放后的行为。验收物理效果、忙/取消/失败路径；默认不创建 daemon 或服务。无可靠映射时可以先完成代码与逻辑测试，但不输出。

## 交付带前提的有限时 CLI 检查

解析板型/修订、连接器、物理脚 → pad → 控制器 → **当前** chip路径/局部offset。读取所选电气路径和[接线指导](../../common/wiring-diagrams.zh-CN.md)，再按[检测指导](../../stacks/linux-gpio-chardev/detection.zh-CN.md)核对当前元数据与工具版本/help。consumer为空不代表mux、外接电路或申请竞争都已解决。选错控制器或短暂持有后释放，不能作为GPIO损坏证据。

驱动电流/负载兼容性未知时，不重新接上LED试亮；先交付断开LED、仅用高阻电压表的条件式测压步骤，画清信号/红表笔与GND/黑表笔端点，有方向依据时同时给板卡定位。命令不在开发机执行。

若目标 `gpioset --help` 确认支持 **2.x `-c`、`--hold-period` 和末项为0的 `--toggle`**，映射、电气、mux/owner核对后可交付以下步骤；它不是发现命令。变量由已核对的当前映射填写，不提供默认chip或line：

```sh
: "${chip:?填写已核对的 /dev/gpiochipN 路径}"
: "${offset:?填写已核对的chip内数字offset}"
# 10秒仅为可调整的读表窗口示例，不是验收阈值。
gpioset -c "$chip" --hold-period 10s --toggle 0 "${offset}=1"
```

`--hold-period` 指最短保持时间，**单独使用不是停止计时器**；末项 `--toggle 0` 让本检查在保持结束后退出，不再循环请求另一个电平。保持前台，Ctrl+C可提前取消。在请求仍持有时读表；到时释放前没读到就记为未测量，不用释放后的电压冒充保持期间结果。需要低电平读数时，重新核对归属，再把同一有限命令改成 `${offset}=0`；不把释放当低电平测试，不用 `gpioget` 抢读正在输出的脚。

正常退出或取消后，用目标版本支持的 `gpioinfo` 与mux元数据核对自己的consumer已消失。busy、权限、选项或bias不支持都停止该阶段，不强占、不静默回退。按[恢复指导](../../stacks/linux-gpio-chardev/recovery.zh-CN.md)分别记录释放、方向/配置与实测电压；只恢复已知且适当的设置，明确原bias、恢复后电压等未知项。有限命令仍需考虑电路的故障/掉电行为，不是硬件安全联锁。

目标选项不同或缺失时，以项目已核对的原生API或进程管理方式实现有限生命周期，不为一次GPIO检查安装新daemon。

语法参考：[官方 gpioset 文档](https://libgpiod.readthedocs.io/en/master/gpioset.html)；上游开发文档不代表目标已安装版本。
