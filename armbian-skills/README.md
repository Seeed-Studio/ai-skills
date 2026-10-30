# Armbian Hardware Skill

One agent skill for understanding Armbian devices, extending hardware applications, deployment and diagnosis. It preserves the project language and business entry points. Board knowledge currently covers Seeed reComputer RK3576/RK3588 DevKit; unlisted targets retain generic investigation paths without inheriting another board's pins.

[简体中文](README.zh-CN.md) · [Quick start](QUICKSTART.md) · [Maintenance](MAINTAINING.md)

**Status: development preview.**

## Install

Use a complete built `skills/armbian-hardware/` directory or unpack `dist/armbian-hardware-2.0.0.skill`. The package is self-contained and includes knowledge, workflows, search/matching tools and a bounded read-only probe. Offline tools require Python 3.9+ standard library; application toolchains depend on your project. No MCP or daemon is required.

With a prebuilt archive, place the complete extracted `armbian-hardware/` folder under the project's `.agents/skills/` for Codex or `.claude/skills/` for Claude Code. No build or development dependencies are needed for that installation. CLI installation compatibility does not establish behavior quality for every model routed through that CLI.

From a development checkout, build first (development dependencies: `requirements-dev.txt`):

```bash
python3 scripts/refresh_catalog.py --check
python3 scripts/build_skills.py
bash install.sh --agent both --scope project --project-dir /path/to/project
```

Use `--agent codex` or `--agent claude` for one client. User-level installation is the default. `--dry-run` previews without writes; `--replace` backs up an existing directory before replacement and rolls back a failed batch. This installer manages only the new `armbian-hardware` package. Reload the agent after installation.

## Use

Describe the task naturally, or invoke `$armbian-hardware`:

- Explain this board's interfaces without changing the device.
- Add AHT20 sampling to my existing Go service, preserving its API.
- Diagnose why this container is using software video decode.

The entry reads only relevant workflow modules. Search discovers candidates; matching checks applicability; explain returns the required dependency closure and reasons. These tools never connect to the device. Actual hardware access uses the user's authorized connection and project tools. Unknown facts remain unknown.

Release manifests trace source commit, dirty-worktree status, skill/knowledge versions and file digests.

Offline queries: `info` summarizes provenance; `search --facts` reuses known facts; `pins --board ID --revision REV --connector NAME --pins N ...` returns selected documentary pin records with constraints. None grants hardware access.
