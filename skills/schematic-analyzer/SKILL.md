---
name: schematic-analyzer
description: |
  Use when analyzing KiCad schematics (.kicad_sch) or Cadence OrCAD/Allegro schematics,
  identifying what a component or IC does, tracing nets, buses, signal paths, or power distribution,
  extracting subsystem topology, or reviewing hardware architecture for design review, BSP bring-up,
  or test planning. Trigger on requests about I2C/SPI/UART/USB buses, power trees, signal flow,
  component roles, root schematic selection in hierarchical designs, and Chinese terms such as
  原理图分析, 拓扑提取, 器件角色, 信号流, 电源树.

compatibility: Requires python3. KiCad projects also require kicad-cli on PATH. Optional but often needed: pcbparts MCP, pdf skill, and ee-datasheet-master.
---

# Schematic Analyzer

Analysis of KiCad schematics, or Cadence OrCAD/Allegro schematics (Allegro netlist pstxnet.dat/pstxprt.dat
combined with OrCAD Capture XML export .xml) via CLI tools.
Produces accurate answers—query what's needed for reliable conclusions, never dumps
raw files, never guesses without grounding.

## Core Principle

```
Accuracy first, efficiency second.
Choose mode first, query what's needed for reliable conclusion.
Structure first, semantics when blocked.
```

## Instructions

### Step 1: Confirm the required environment

Before analyzing a project, confirm the inputs and runtime needed for that file type:
- For any project, `python3` must be available (Windows: `python`)
- For KiCad projects, `kicad-cli` must be available on `PATH`
- For Cadence projects, require `pstxnet.dat`, `pstxprt.dat`, and the OrCAD Capture XML export together
- For datasheet-dependent questions, require the relevant datasheet PDF or escalate to `ee-datasheet-master`

If a required dependency or input is missing:
- Stop before claiming the skill is usable for this task
- State exactly what is missing
- Tell the user the skill may be installed, but the current task is blocked until that requirement is provided

### Step 2: Choose the entry mode

Choose mode first, then query only what is needed for a reliable conclusion:
- Architecture or review tasks: start with `overview`
- Targeted component or net questions: start with direct `query`
- Pattern searches: use `query --pattern <yaml_file>`

### Step 3: Escalate only when structure is insufficient

Use this escalation order:
1. Structural evidence from the schematic
2. `pcbparts` MCP for part identity or package/spec clues
3. `ee-datasheet-master` for pin functions or electrical behavior
4. Re-ground the conclusion back to the schematic evidence

### Iron Rule

**Accuracy and evidence override coverage. Every claim requires direct evidence of the matching type.**

If evidence does not support a conclusion:
- Return `Unknown` or a lower-confidence result
- State which evidence is present and missing
- Avoid inventing roles or meanings to make output look complete

**No evidence, no assertion; weak evidence, weak conclusion.**

Each claim type demands specific evidence — a device's power domain requires checking its VDD/VCC pin, an interface mode requires tracing all signal lines to their endpoints, not just some. Inferences from device type, connector names, page location, or neighboring components are not sufficient on their own. See the evidence requirements table in [SCHEMATIC_STRATEGY.md](./SCHEMATIC_STRATEGY.md) Rule 6.

---

## MCP Tools

All analysis via MCP tools (no CLI paths). Tools return JSON.

Server: `sch` — invoke as `mcp__sch__<tool>(...)`.

### `overview` — Project First Look

**Tool:** `mcp__sch__overview(project="<path>")`

Output: page count, component count, net count, page index table, core candidates.

Use when: Architecture analysis, design review, or need page context.

### `comp` — Inspect a Component

**Tool:** `mcp__sch__comp(project="<path>", ref="<ref>")`

Returns: value, MPN, pins with net names, properties, neighbors (shared nets with fanout).

Set `full=true` to include unconnected pins (rarely needed).

### `net` — Inspect a Net

**Tool:** `mcp__sch__net(project="<path>", name="<net_name>")`

Returns: all connected pins with reference, pin name, and page.

### `page` — Inspect a Page

**Tool:** `mcp__sch__page(project="<path>", index=<n>)`

Returns: all components and nets on the page (1-based index from overview).

### Search & Utility Tools

| Tool | Purpose |
|------|---------|
| `mcp__sch__comp_search(project, text)` | Search components by MPN/value/ref text |
| `mcp__sch__net_search(project, text)` | Search nets by name (supports regex) |
| `mcp__sch__prop(project, key)` | Query property values across all components |
| `mcp__sch__pattern(project, file)` | Run custom YAML pattern query |

---

## Negative Evidence

**What is NOT connected is as important as what IS connected.**

- Unconnected signal lines indicate reduced operating mode
- DNP components indicate optional/alternative configuration
- Missing connections are facts, not gaps to fill with assumptions

When determining interface mode or device configuration:
1. Check ALL signal lines, not just the ones that are connected
2. Unconnected lines are evidence of operating mode, not "incomplete design"
3. Do not assume a function is active because the pin name suggests it

---

## Anti-Patterns

### Don't: Dump Raw Files

```
❌ Read the entire .kicad_sch, Cadence XML, or Allegro netlist files
❌ Paste full netlist into context
❌ Export all JSON and load into prompt
```

### Don't: Batch Everything

```
❌ Look up 50 MPNs in MCP before understanding the design
❌ Read all datasheets before identifying core components
```

### Don't: Guess Without Evidence

```
❌ "U10 is probably the main controller" (without connectivity evidence)
❌ "This is a power supply" (without checking nets)
```

### Don't: Always Run Overview

```
❌ Run overview before every targeted query (comp U10)
❌ Run overview when user asks about a specific net (net GND)

✓ Run overview only when: architecture mode, review mode, or need page context
```

### Don't: Infer From One Side of a Connection

```
❌ Conclude interface mode from connector pin names alone without tracing signal lines to controller
❌ Conclude device power domain from bus pull-up voltage or neighboring device power
❌ Assume devices on the same bus share the same power domain
❌ Assume a function is active because the pin name suggests it, without checking the other endpoint
```

### Don't: Ignore What's NOT Connected

```
❌ Skip unconnected signal lines when determining interface mode
❌ Overlook diode-connected power paths as "just protection"
❌ Fill in missing evidence with assumptions to make output look complete
```

---

## Reading Strategy

For entry mode selection, reading loop, and detailed workflow, see [SCHEMATIC_STRATEGY.md](./SCHEMATIC_STRATEGY.md).

**Never**: Dump full `.kicad_sch` files, Cadence XML files, Allegro netlist files, or exported JSON into context.

---

## MCP Integration

### pcbparts tools

- `mcp__pcbparts__jlc_search`: Search component by part number
- `mcp__pcbparts__jlc_get_part`: Get detailed specs by LCSC code

Use when: Component role unclear from structure alone, need part specs.

### ee-datasheet-master skill

Use when: MCP has no data and you need pin functions, electrical specs, or device-specific behavior.

**How to invoke**:
```
/ee-datasheet-master <datasheet_path> "<question>"
```

**Critical rules**:
1. **Invoke the skill explicitly** — do not read datasheets with general PDF tools
2. **No datasheet? Ask user** — if the required datasheet is not available, ask the user to provide it:
   - "I need the datasheet for <MPN> to answer about <specific question>. Can you provide the PDF?"
3. **Never guess datasheet content** — do not rely on prior knowledge or assume specifications

**Escalation order**: Structural evidence → pcbparts MCP → ee-datasheet-master → re-ground to schematic.

---

## Troubleshooting

Error: `No module named 'yaml'` or another Python import failure
Cause: Python dependencies are missing.
Solution: Run `pip install -r scripts/requirements.txt` before continuing.

Error: `kicad-cli: command not found`
Cause: KiCad CLI is required for KiCad netlist export but is not installed or not on `PATH`.
Solution: Install KiCad, ensure `kicad-cli` is on `PATH`, and do not continue KiCad analysis until this is fixed.

Error: KiCad project opens but connectivity is incomplete
Cause: Netlist export failed, project path is wrong, or the project is only partially available.
Solution: Verify the project root path, rerun `overview`, and in hierarchical designs confirm the correct root schematic was selected.

Error: Cadence query lacks pages or component metadata
Cause: Allegro netlist files and OrCAD XML are both required; one side is missing.
Solution: Require `pstxnet.dat`, `pstxprt.dat`, and the Capture XML export together. If any one is missing, state that the project is only partially analyzable.

Error: MCP lookup is unavailable
Cause: `pcbparts` MCP is optional and not configured.
Solution: Continue with structure-only analysis when possible, but state that part/spec lookup is limited without MCP.

Error: The question depends on a datasheet, but no datasheet is available
Cause: Structural evidence identifies the device but not the required pin function or electrical spec.
Solution: Ask for the datasheet PDF or invoke `ee-datasheet-master` if the PDF is available. Do not answer from prior knowledge.

Error: Query result is ambiguous
Cause: Multiple refs or nets match, or the evidence is incomplete.
Solution: Return the competing candidates, state what extra query would disambiguate the answer, and prefer `Unknown` over a confident guess.

---

## Examples

### Example 1: Targeted Query

```
User: "U10 是什么？"
```

Invoke `mcp__sch__comp(project="<project>", ref="U10")`. Read the value, mpn, and nets from the result. No overview needed.

### Example 2: Architecture Analysis

```
User: "分析这个项目的整体架构"
```

Step 1: `mcp__sch__overview(project="<project>")` — get page index + core candidates.

Step 2: `mcp__sch__page(project="<project>", page_index=<n>)` for each relevant page.

Step 3: `mcp__sch__comp(project="<project>", ref="<top_candidate>")` — trace cross-page nets.

Step 4: `mcp__sch__net(project="<project>", name="<cross_page_net>")` — find all participants.

Step 5: Repeat for secondary anchors (power, I/O). Build the picture incrementally.

### Example 3: Bus Detection

```
User: "I2C 总线上挂了哪些设备？"
```

Step 1: `mcp__sch__net_search(project="<project>", text="SDA|SCL|I2C")` — discover I2C signal names.

Step 2: If I2C uses GPIO naming, search with `$` anchor: `text="GPIO0$|GPIO1$"` (avoids matching GPIO10).

Step 3: `mcp__sch__net(project="<project>", name="<exact_net>")` — get ALL pins = bus participants.

### Example 4: Design Review

```
User: "电源设计有问题吗？"
```

Step 1: `mcp__sch__overview(project="<project>")` — find power pages.

Step 2: `mcp__sch__page(project="<project>", page_index=<power_page>)` — list power ICs.

Step 3: `mcp__sch__comp(project="<project>", ref="<power_ic>")` — check pin connections.

Step 4: Escalate to `pcbparts` MCP for part specs, or `ee-datasheet-master` for pin functions. Report findings with evidence.
