# Armbian 硬件应用技能

一个入口完成 Armbian 能力解释、已有应用硬件集成、部署和诊断。保留项目语言、原业务入口与原生工具。当前板级知识覆盖 Seeed reComputer RK3576/RK3588 DevKit；未知载板继续通用调查，不套用其他板针脚。

[English](README.md) · [快速开始](QUICKSTART.zh-CN.md) · [维护说明](MAINTAINING.md)

**状态：开发预览。**

## 安装

安装完整 `skills/armbian-hardware/` 目录，或解压 `dist/armbian-hardware-2.0.0.skill`。包内包含知识、按需工作流、离线搜索/匹配工具和只读采集器，不依赖开发仓库、其他技能、特定 MCP 或常驻服务。离线工具只需要 Python 3.9+ 标准库；应用编译器、SDK 和硬件条件由项目决定。

已有预构建包时，将解压后的完整 `armbian-hardware/` 目录放到项目的 `.agents/skills/`（Codex）或 `.claude/skills/`（Claude Code），无需构建或安装开发依赖。CLI 安装兼容不代表其中路由的所有模型都已通过行为验收。

开发检出先准备 `requirements-dev.txt` 中的开发依赖，再构建：

```bash
python3 scripts/refresh_catalog.py --check
python3 scripts/build_skills.py
bash install.sh --agent both --scope project --project-dir /path/to/project
```

可选 `--agent codex` 或 `--agent claude`；默认用户级安装。`--dry-run` 预览不写入；更新用 `--replace`，会备份并在批次失败时恢复。安装器只管理新架构 `armbian-hardware`，不迁移旧技能。安装后重新加载 Agent。

## 使用

自然描述需求或显式使用 `$armbian-hardware`：

- 只解释板卡接口及准备条件，不操作设备。
- 在现有 Go 服务中添加 AHT20，保留原 API。
- 诊断容器中视频为何回退到软件解码。

能力、开发、部署、验证是按需读取的工作流。搜索负责发现，匹配负责适用条件，explain 给出原因与必要依赖闭包；三者均不连接设备。设备访问使用已有授权的连接和原项目工具。长任务按需保存事实与方案，简单问答无需建目录。

发布清单关联源码提交、工作区是否有改动、技能/知识版本和文件摘要。

离线查询：`info` 提供版本摘要；`search --facts` 复用已有事实；`pins --board ID --revision REV --connector NAME --pins N ...` 定向返回针脚与约束。所有结果仅为资料，不授权硬件操作。
