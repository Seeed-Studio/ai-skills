---
schema_version: '1'
id: capability.camera
kind: capability
applies_to:
  capabilities:
  - camera
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
updated_at: '2026-10-30'
---

[English](overview.md) | [简体中文](overview.zh-CN.md)

# CAMERA 应用开发

识别 sensor、CSI/USB、media graph、video node、输出格式、IQ/3A 与运行权限。不要固定 /dev/video0。样帧验证颜色/曝光和内容，单纯可抓帧不足以验证正确图像。

按实际 driver 和采集能力辨认节点：video 节点可能是 HDMI 输入、ISP/编解码或元数据，不一定是用户要的 USB 摄像头。不预测下一个设备号。

所需输入未枚举时，当前交付是连接/枚举核查、什么输出能识别该输入，以及如何查看其支持模式；不追加基于假设输入的可执行安装、采集或推流配置。采集命令的分辨率/像素格式/帧率只能来自目标节点实际枚举输出：以占位设备号（如 /dev/videoN）给出命令，不使未经枚举验证的格式选择变成条件式——待确认的是格式参数本身，不只是设备号。用户要求路线图时，可说明有条件的链路阶段；交付可运行配置前须明确实际格式、帧率、编码及接收/发布服务。不用常见摄像头规格、猜测配置语法或包/性能保证补缺口。「最少就两样/只需装 X 和 Y」的依赖下限句式与「…即可」的收尾承诺，在实际格式、接收/发布服务与目标机已装软件核对前不使用：软件现状如实写「已查为空」，且「已查为空」只覆盖查过的来源（如这几个命令），不据此断言零安装不可能、目标机没有硬件编码构建或必须安装某组合——其余来源、容器与私有工具未查时保留未知，也不写「大概率不在本机/在别处」这类带对冲的位置推断——位置就是未知，写「位置未知，需确认」；装什么列为格式与接收端核对后的条件动作，不写成默认必经阶段；分段验收与措辞另见[摄像头验证](verification.zh-CN.md)。若用户要求项目实现，继续独立代码工作，将这部分硬件配置保留待确认。

未收录平台可继续核对官方接口并做有界测试；关键接线或兼容性未知时，继续离线实现并将相关实机步骤标为未验证。
