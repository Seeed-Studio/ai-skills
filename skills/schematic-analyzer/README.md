# Schematic Analyzer

A Claude Code skill for analyzing KiCad schematics and Cadence OrCAD/Allegro schematics with accuracy-first principles.

## Overview

Schematic Analyzer helps you understand hardware designs by querying KiCad (.kicad_sch) and Cadence OrCAD/Allegro schematic files (Allegro netlist pstxnet.dat/pstxprt.dat combined with OrCAD Capture XML export .xml) directly, without dumping raw files into context. It provides structured JSON output for components, nets, pages, and subsystems.

## Key Features

- **Architecture Analysis**: Understand project structure, identify core components, trace subsystems
- **Component Inspection**: Query any component by reference, get connectivity, neighbors, properties
- **Net Tracing**: Follow signal paths across pages, find connected components
- **Bus Detection**: Identify I2C/SPI/UART/USB buses via pattern matching
- **Design Review**: Check power domains, interface modes, unconnected pins

## Core Principle

```
Accuracy first, efficiency second.
Choose mode first, query what's needed for reliable conclusion.
Structure first, semantics when blocked.
```

## Quick Start

Configure the MCP server in `.claude/mcp.json`:

```json
{
  "mcpServers": {
    "sch": {
      "command": "python3",
      "args": ["<path>/schematic_mcp.py"]
    }
  }
}
```

Then invoke tools directly (no CLI paths):

```
mcp__sch__overview(project="<project>")
mcp__sch__comp(project="<project>", ref="U10")
mcp__sch__net(project="<project>", name="VCC_LED")
mcp__sch__page(project="<project>", index=3)
```

## Entry Modes

| Mode | Trigger | First Action |
|------|---------|--------------|
| Architecture | "整体架构", "power tree", "subsystems" | `mcp__sch__overview` |
| Targeted | "U10是什么", "I2C_SDA在哪" | `mcp__sch__comp` or `mcp__sch__net` |
| Pattern | "I2C设备有哪些", "USB拓扑" | `mcp__sch__pattern` |
| Review | "设计有问题吗", "review" | `mcp__sch__overview` |

## Output Structure

| Tool | Top-level Keys | Sub-object Keys |
|------|----------------|-----------------|
| `page` | index, name, file, type, components, nets | components[i]: ref, value, mpn; nets[i]: name, pin_count |
| `comp` | ref, value, mpn, page_index, properties, nets, neighbors | nets[i]: name, pin; neighbors: shared_nets |
| `net` | name, hierarchical_labels, global_labels, local_labels, pages, pins | pins[i]: ref, pin |
| `prop` | key, values | values[i]: mpn, refs |

## File Structure

```
schematic-analyzer/
├── SKILL.md              # Skill definition (trigger, rules, MCP tools)
├── SCHEMATIC_STRATEGY.md # Reading strategy (workflows, principles)
├── scripts/              # Analysis engine + MCP server
│   ├── schematic-cli.py  # CLI entry point (legacy)
│   ├── schematic_mcp.py  # MCP server (FastMCP)
│   ├── tools/
│   │   ├── kicad/        # KiCad format parsers
│   │   ├── cadence/      # Cadence OrCAD/Allegro parsers (XML + DAT netlist)
│   │   └── parser_factory.py  # Auto-detect format and dispatch
│   └── requirements.txt  # Python dependencies
├── patterns/             # Pattern YAML examples (i2c, spi, uart, etc.)
├── evals/                # Evaluation test cases
└── tests/                # Unit tests
```

## MCP Integration

- **pcbparts**: Component search and specs lookup (`jlc_search`, `jlc_get_part`)
  - User must install and configure pcbparts MCP server separately
  - See: https://pcbparts.dev/mcp

## Skill Dependencies

- **pdf**: Used for reading datasheets when device-specific information is needed
- **ee-datasheet-master**: Used for detailed datasheet analysis (pin functions, electrical specs, device-specific behavior)

## Datasheet Preparation

Schematic analysis often requires datasheets for core components (MCU, PMIC, transceiver, etc.) to determine pin functions, electrical specs, and device-specific behavior. Place datasheets under a shared `datasheets/` directory at the project root, with filenames containing the **MPN (Manufacturer Part Number)** for easy discovery. Multiple schematics can share the same datasheet library.

### Recommended Project Structure

```
project/
├── datasheets/                    # Shared datasheet library
│   ├── RK3576_Datasheet_V1.2.pdf
│   ├── BQ25895_Datasheet.pdf
│   └── ESP32-S3_Datasheet.pdf
├── E1005/                         # KiCad schematic
│   └── E1005.kicad_sch
├── Denali/                        # Cadence OrCAD/Allegro schematic
│   ├── denali.xml                 # OrCAD Capture XML export
│   └── netlist/                   # Allegro netlist directory
│       ├── pstxnet.dat
│       └── pstxprt.dat
└── E1005_v02/                     # Another version
    └── E1005.kicad_sch
```

### Naming Convention

- **Required**: Filename must contain the MPN (e.g., `RK3576`, `BQ25895`, `ESP32-S3`)
- **Recommended**: `MPN_Datasheet[_Version].pdf` format
- **Purpose**: Enables the skill to locate datasheets by MPN when escalation to `ee-datasheet-master` is needed

## Supported Formats

| Format | Files Required | Notes |
|--------|----------------|-------|
| KiCad | `.kicad_sch` | Requires `kicad-cli` for netlist export |
| Cadence OrCAD/Allegro | `pstxnet.dat` + `pstxprt.dat` + `.xml` | Allegro netlist (.dat) provides precise connectivity; OrCAD Capture XML export (.xml) provides component/page info. Both are needed together. |

Format is auto-detected from file content.

## Dependencies

### Required

- **Python 3.10+**
- **KiCad CLI** - Required only for KiCad schematics (netlist export and connectivity analysis)
  - Not needed for Cadence OrCAD/Allegro analysis
  - Linux: `kicad-cli` (installed with KiCad)
  - Windows: `kicad-cli.exe` (add KiCad install directory to PATH)

### Python Packages

```bash
pip install -r scripts/requirements.txt
```

| Package | Version | Required? | Purpose |
|---------|---------|-----------|---------|
| PyYAML | >=6.0 | **Yes** | Pattern YAML file loading for bus detection (I2C/SPI/UART/USB) |
| pymupdf | >=1.23 | **Yes** | Datasheet PDF parsing (via ee-datasheet-master skill) |
| pdfplumber | >=0.10 | **Yes** | Datasheet parsing fallback for edge cases |
| pypdfium2 | >=4.0 | **Yes** | PDF page rendering fallback |

All other dependencies use Python standard library modules (`re`, `pathlib`, `dataclasses`, `xml.etree.ElementTree`, `json`, `argparse`)

## Platform Support

All platforms: configure the MCP server in `.claude/mcp.json`, then use MCP tools directly. No CLI paths needed.

```json
{
  "mcpServers": {
    "sch": {
      "command": "python3",
      "args": ["/path/to/schematic_mcp.py"]
    }
  }
}
```

**Windows:** Use `python` instead of `python3`, and Windows-style paths for the `args` value.

## Documentation

- [SKILL.md](./SKILL.md) - Skill definition, MCP tools, anti-patterns
- [SCHEMATIC_STRATEGY.md](./SCHEMATIC_STRATEGY.md) - Reading loop, verification, circuit reasoning
