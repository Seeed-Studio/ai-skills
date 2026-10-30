---
schema_version: '1'
id: common.reference-matching
kind: common
applies_to: {}
required_refs:
- common.identity
preconditions: []
refines: []
excludes: []
related: []
sources: []
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-29'
---

[English](reference-matching.md) | [简体中文](reference-matching.zh-CN.md)

# 离线匹配契约与读取顺序

先运行 `python3 scripts/armbian.py info` 获取版本摘要，再按任务使用索引或搜索结果选择资料。catalog.yaml 是维护用 YAML，catalog.json 是同源生成的运行时索引；匹配程序只依赖 Python 3 标准库，不安装目标应用依赖，不连接设备或执行资料里的命令。

在 Skill 目录运行：

```bash
python3 scripts/armbian.py match --facts /path/to/task-facts.json
```

事实输入包含 schema_version="1"，可选 target/task/facts 对象。所有缺失值保留 null 或省略，不填推测值。数组必须非空、大小写精确；默认不归一化版本/架构名称。示例是输入结构，不是当前设备事实：

```json
{
  "schema_version": "1",
  "target": {
    "device_tree": {"compatible": ["vendor,example-board", "vendor,example-soc"]},
    "board_ids": null,
    "soc_ids": null,
    "hardware_revisions": null,
    "architectures": ["aarch64"],
    "kernel_releases": null,
    "image_ids": null
  },
  "task": {"capabilities": ["gpio"], "operations": ["gpio.output"], "languages": ["rust"]},
  "facts": {"stack_ids": null, "versions": {}, "application": {"device_access": null}}
}
```

board_ids/soc_ids 可从当前 compatible 精确规则提取为候选，不能用名称别名证明身份。revision 只接受本次提供的证据；不从历史快照或“最新目录”推断。输入是已采集/审核事实，调用者仍负责来源真实性；程序不判断电气是否安全。

applies_to 支持 board_ids/soc_ids/hardware_revisions/architectures/kernel_releases/image_ids/capabilities/operations/languages/stack_ids，不同维度 AND，同维度允许集合 OR。前七个设备维度按 target 映射，capabilities/operations/languages 按 task，stack_ids 按 facts。缺失值为 unknown；unknown 不等于 unsupported。

preconditions 与 refines.when/excludes.when 的条件使用 field 点路径、operator 和 value（in 使用 values）。只实现 eq、in、contains_exact；比较严格类型和精确值，不做字符串版本排序。runtime_constraints 使用 component、version_scheme、operator 和期望值，读取 facts.versions 对应组件；exact 以外 scheme 返回 unknown/待复核。不认识的操作符和无效元数据以错误码 2 退出，绝不 eval/source 命令。

结果分 matches/unknown/no_match/excluded，逐条件列出依据、ID/路径/摘要与 knowledge release，身份歧义在 identity.conflicts。缺少必需引用阻止解析；必需资料不匹配时资料不会直接匹配成功。related 可以互链；refines 只报告条件与字段供复核，不自动覆盖或解除保护。

matches 表示资料条件符合，不代表能力可用或授权硬件输出。历史报告只供追溯，不参与当前事实生成。先读结果中的相关正文，再形成四层能力报告和项目方案。通过 --kind 可缩小显示类别，完整元数据/依赖仍会校验。

输入可选 expected_knowledge_release，用于延续任务时防止静默切换资料版本；与本包不一致则报格式错误并先复核。以 manifest.json 核对 knowledge_release 与文件摘要；切换发布版本时明确刷新相关任务事实。未收录平台仍可用 common/capability 和官方接口继续调查，不继承相近板卡针脚。
