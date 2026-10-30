---
schema_version: '1'
id: capability.camera.verification
kind: capability_guide
applies_to:
  capabilities:
  - camera
required_refs:
- capability.camera
- common.verification
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

[English](verification.md) | [简体中文](verification.zh-CN.md)

# 摄像头与视频链路验证

按阶段分别取证：输入枚举 → 格式/帧率 → 编码后端 → 封装/传输 → 接收端解码/显示。命令成功或链路跑通只覆盖实际经过的阶段，任一阶段未验证都保留为未验证，不用其余阶段的通过补足。

输入识别：v4l2 枚举列出的是该节点能力（如 MJPG 1920x1080 30fps、YUYV 1920x1080 5fps），只约束节点可输出什么，不约束后续编码、传输或接收端能否承载。采帧参数从已枚举格式中选择，不预测未列出的模式，也不把高帧率格式当作低帧率格式的替代结论。

编码后端按目标机构建核对：命令里出现 libx264 只证明该命令用了软件编码。硬件编码是否存在，以目标机实际 FFmpeg 构建的 `-encoders`/`-hwaccels` 输出为准（不依赖记忆中的条目名）：构建内没有相关条目只说明「该构建未编译此后端」，禁止写成「板没有硬件编码能力」；同一板上不同构建或容器内结果可能不同。验收以实际编码日志与输出流参数为准，未运行前不预先断言走软编或硬编。

接收端与部署位置：RTSP URL 存在不证明接收/转发服务已配置或正在运行。Home Assistant、go2rtc 等组件运行在哪台主机/容器未核对前保持条件式；「本机没有 Docker/没有某进程」既不能证明部署不在本机，也不能证明在别处，加对冲词同样不行——不写「大概率不在本机/大概率在别处」，写「已查的〈来源〉没有该组件；位置未知，需确认」。不设「最少必须安装 X 和 Y」这类依赖下限断言：先核对已有发布/接收服务、目标机已装软件与应用权限，缺什么以核对结果为准。装包写成格式与接收端核对后的条件动作，不用「…即可」收尾承诺串联未核对的前提；「已查命令里没有编码/推流工具」不写成「零安装不可能」，未查来源保留未知。

分段验收示例：采集（帧到达、格式与预期一致）→ 编码（实际后端、输出参数）→ 传输（接收端实际收到完整流）→ 显示/录制（接收端解码出帧并核对内容）。每段记录目标、时间、命令与证据；下游段的用户报告不回溯证明上游段。
