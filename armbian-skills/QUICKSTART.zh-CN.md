# Quick start / 快速开始

Install the complete built skill as described in README. 安装方法见 README。

Run these from the installed skill directory (absolute script paths also work from any cwd):

```bash
python3 scripts/armbian.py info
python3 scripts/armbian.py search "容器视频没有硬解"
python3 scripts/armbian.py search "GPIO LED" --facts /project/task-facts.json
python3 scripts/armbian.py match --facts /project/task-facts.json --kind board
python3 scripts/armbian.py explain --ref common.identity --facts /project/task-facts.json
python3 scripts/armbian.py pins --board seeed.recomputer-rk3588-devkit --revision v1.0 --connector J10 --pins 23 40
```

Search results without facts have unknown applicability. Read selected bodies and explain's full required closure. A high relevance score never grants pin access or establishes board identity. 无事实时返回未知，排名不证明兼容性或针脚身份。

For a long task, optionally copy `templates/task-facts.json` and `templates/plan.md` into the existing project's records or `.armbian/`. Keep missing values null; record evidence source, target and collection time in the plan. Refresh observations after target/runtime/application changes. No credentials. 简单问答无需创建文件。

When live metadata is needed and the target/connection is authorized:

```bash
ssh TARGET 'python3 -' < scripts/probe_device.py
```

This is bounded read-only metadata collection; it does not scan buses, request GPIO or run accelerator workloads. Read the capabilities workflow for interpretation. Do not treat a failed host/SSH probe as unsupported target hardware.
