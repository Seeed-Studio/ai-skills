---
schema_version: '1'
id: capability.thermal.verification
kind: capability_guide
applies_to:
  capabilities:
  - thermal
required_refs:
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

# 温度与风扇验证

诊断热问题先分层：温区归属与 trip、CPU policy/governor/上下限、负载、时间。引用任何数值标注来源（静态快照还是采样序列）与时刻；静态快照的范围不写成序列全范围，序列中存在更低/更高值时不得写「全部温度」。

结论句式对照：

- 不写「风扇已装且在慢转」「原配风扇在加速」。PWM enabled/duty 或 duty 随温度上升只证明控制输出：写「风扇通道已由 pwm-fan 接管，占空比 X%；物理上是否装扇、是否转动未验证」。括号补注「转速/气流未验证」不能翻转主句的物理断言。物理证据是转动观察、转速反馈（tach/RPM）或可复现的温差/气流变化。
- 不写「完全空转/完全没有负载」。舍入的 loadavg 0.00 只写「loadavg 采样为 0.00（舍入值）」，不等于各核瞬时状态。
- 低频归因保持条件式：写「与该 governor 的空载调频行为一致；排除热限幅需同刻观测」，同刻指同一次循环里同时读取当前频率与 `scaling_max_freq`/`cooling_device*/cur_state`，不跨快照与序列拼接。

负载与采样句式：诊断性负载不把某个固定时长写成必须（如「必须十分钟满载」）；判据优先于时长——达到「温度是否接近 trip、max 是否被压低」的判据即可停止。无项目依据时给短时有界负载并注明可调。后备负载命令自带时限（如 `timeout 300 stress-ng --cpu 8` 或 `timeout 60 yes >/dev/null`），不给无界循环；采样器写明次数或总时长（如 `for i in $(seq N)` 循环固定轮数），不给无停止方式的常驻 `watch`。加风扇/降频建议在满载与物理证据之前保持条件式。
