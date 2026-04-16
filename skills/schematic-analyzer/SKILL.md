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
- For any project, `python3` and the CLI script must be available
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

## CLI Commands

The skill uses three commands only:

### `overview` — Project First Look

```bash
python scripts/schematic-cli.py overview <project>
```

Output:
- Project page count, component count, net count
- Page navigation (numbered index for `--page` queries)
- Core component candidates (ranked by structural connectivity)

Use when: Architecture analysis, design review, or need page context.

### `query` — Inspect Objects

All `query` commands output JSON. Key fields for filtering:

| Query Type | Top-level Keys | Sub-object Keys |
|------------|----------------|-----------------|
| `--page` | index, name, file, type, components, nets | components[i]: ref, value, mpn; nets[i]: name, pin_count |
| `--component` | ref, value, mpn, page_index, properties, nets, neighbors | nets[i]: name, pin; neighbors: shared_nets |
| `--net` | name, hierarchical_labels, global_labels, local_labels, pages, pins | pins[i]: ref, pin |
| `--property` | key, values | values[i]: mpn, refs |

```bash
# Query by page index (from overview)
python scripts/schematic-cli.py query <project> --page <index>
# → Filter large output:
#   | python -c "import sys,json; d=json.load(sys.stdin); print([c['ref'] for c in d['components']])"
#   | python -c "import sys,json; d=json.load(sys.stdin); print([n['name'] for n in d['nets']])"

# Query component by reference
python scripts/schematic-cli.py query <project> --component <ref>           # filtered (active pins)
python scripts/schematic-cli.py query <project> --component <ref> --full    # complete (includes unconnected)
# → Filter large output:
#   | python -c "import sys,json; d=json.load(sys.stdin); print(d.get('value'), d.get('mpn'))"
#   | python -c "import sys,json; import json as j; d=j.load(sys.stdin); del d['neighbors']; print(j.dumps(d, indent=2))"

# Search components by text
python scripts/schematic-cli.py query <project> --component --match <text>

# Query net by exact name
python scripts/schematic-cli.py query <project> --net <name>

# Search nets by text
python scripts/schematic-cli.py query <project> --net --match <text>

# Query property values
python scripts/schematic-cli.py query <project> --property <key>
# → Filter large output:
#   | python -c "import sys,json; d=json.load(sys.stdin); print([v['mpn'] for v in d['values'] if v['mpn']])"

# Pattern matching (explicit YAML required)
python scripts/schematic-cli.py query <project> --pattern <yaml_file>
```

**`--full` switch**: Use only when blocker requires complete pin-net mapping (e.g., "which pins are unconnected"). Default filtered output hides `unconnected-*` pins.

### `cache` — Cache Management

```bash
python scripts/schematic-cli.py cache <project> --status
python scripts/schematic-cli.py cache <project> --clear
```

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
❌ Run overview before every targeted query (--component U10)
❌ Run overview when user asks about a specific net (--net GND)

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

```bash
# Direct query, no overview - extract basic identity
python scripts/schematic-cli.py query data/E1005/ --component U10 \
  | python -c "import sys,json; d=json.load(sys.stdin); print(f\"Value: {d['value']}, MPN: {d.get('mpn')}, Page: {d['page_name']}\")"

# If need net summary for context:
#   | python -c "import sys,json; d=json.load(sys.stdin); print(f\"Nets ({len(d['nets'])}): {[n['name'].split('/')[-1] for n in d['nets'][:5]]}...\")"

# If role unclear, escalate to MCP
```

### Example 2: Architecture Analysis

```
User: "分析这个项目的整体架构"
```

```bash
# Architecture mode follows SCHEMATIC_STRATEGY.md Rule 1 + Reading Loop:
# start with project scope, then page decomposition, then core anchors, then cross-page nets.

# Step 1: overview establishes page index + core candidates
python scripts/schematic-cli.py overview data/E1005/

# From overview, identify:
# - top core candidate(s)
# - page indices for main logic, power, peripherals, display, etc.

# Step 2: inspect the populated architecture pages identified by overview
python scripts/schematic-cli.py query data/E1005/ --page 8 \
  | python -c "import sys,json; d=json.load(sys.stdin); print(f\"MCU page {d['index']} {d['name']}: components={[c['ref'] + ':' + c['value'] for c in d['components'] if c['ref'].startswith('U')][:8]}, nets={[n['name'].split('/')[-1] for n in d['nets'][:8]]}\")"

python scripts/schematic-cli.py query data/E1005/ --page 6 \
  | python -c "import sys,json; d=json.load(sys.stdin); print(f\"Power page {d['index']} {d['name']}: components={[c['ref'] + ':' + c['value'] for c in d['components'] if c['ref'].startswith('U')][:8]}, nets={[n['name'].split('/')[-1] for n in d['nets'][:8]]}\")"

python scripts/schematic-cli.py query data/E1005/ --page 10 \
  | python -c "import sys,json; d=json.load(sys.stdin); print(f\"I/O page {d['index']} {d['name']}: components={[c['ref'] + ':' + c['value'] for c in d['components'] if c['ref'].startswith(('U','J','USB'))][:8]}, nets={[n['name'].split('/')[-1] for n in d['nets'][:8]]}\")"

# Step 3: inspect the top core component from overview, but read it as an index into the design
python scripts/schematic-cli.py query data/E1005/ --component U10 \
  | python -c "import sys,json; d=json.load(sys.stdin); neighbors = sorted(d['neighbors']['shared_nets'], key=lambda x: x['fanout'], reverse=True)[:8]; print(f\"Core {d['ref']} {d['value']} on {d['page_name']}: top_shared_nets={[(n['net'].split('/')[-1], n['fanout']) for n in neighbors]}\")"

# Step 4: expand around one verified cross-page net from the core to identify subsystem participants
python scripts/schematic-cli.py query data/E1005/ --net /SCH_TOP/USB_DP \
  | python -c "import sys,json; d=json.load(sys.stdin); refs=sorted(set(p['ref'] for p in d['pins'])); print(f\"Net {d['name'].split('/')[-1]}: pages={d['pages']}, refs={refs}\")"

# Step 5: only after the structure is grounded, inspect secondary anchors such as power or peripherals
python scripts/schematic-cli.py query data/E1005/ --component U1 \
  | python -c "import sys,json; d=json.load(sys.stdin); nets=[n['name'].split('/')[-1] for n in d['nets'] if any(k in n['name'].upper() for k in ['VIN','VBUS','VSYS','3V3','BAT'])]; print(f\"Power anchor {d['ref']} {d['value']}: nets={nets}\")"

# At this point, do not rush to summarize the whole project.
# These commands should tell you whether the design skeleton is clear: who is the main controller,
# where power comes in and is converted, and how one major external interface reaches the core.
# If that skeleton is still incomplete, look at the missing subsystem next rather than jumping around.
# A good architecture answer should read like connected blocks: controller, power, I/O, peripherals, display/storage.
# If one of those blocks is still vague, keep expanding from the nearest confirmed page, net, or anchor component.
```

### Example 3: Bus Detection

```
User: "I2C 总线上挂了哪些设备？"
```

```bash
# Pattern mode workflow (see SCHEMATIC_STRATEGY.md Rule 1):
# Step 1: Discover actual I2C signal names in this project (--match supports regex)
python scripts/schematic-cli.py query data/E1005/ --net --match "SDA|SCL|I2C"
# Output shows hierarchical_labels: MISC_I2C_SCL, BFG_I2C_SDA, etc.
# Each match includes: name, kind (net/hierarchical_label/local_label), pages, pin_count

# Step 2: If I2C uses GPIO naming, search with $ anchor for exact match:
python scripts/schematic-cli.py query data/E1005/ --net --match "GPIO0$|GPIO1$"
# Use $ to avoid matching GPIO10, GPIO11, etc.
# Output reveals: GPIO0/GPIO1 are used for main I2C in this design

# Step 3: Trace the net to get ALL participants on the bus
python scripts/schematic-cli.py query data/E1005/ --net "/SCH_TOP/ESP32-S3R8/GPIO0" \
  | python -c "import sys,json; d=json.load(sys.stdin); refs = sorted(set(p['ref'] for p in d['pins'])); print(f\"I2C participants: {refs}\")"
# Output: I2C participants: ['R58', 'U10', 'U14', 'U15', 'U16', 'U5', 'U6']
# This answers the user's question directly!

# Step 4: (Optional) Write a custom pattern YAML for validation
# Create /tmp/i2c_custom.yaml:
#   name: "I2C"
#   category: bus
#   description: "I2C bus"
#   signals:
#     - role: scl
#       patterns: ["(?i)GPIO0$"]
#       required: true
#       group_key: true
#     - role: sda
#       patterns: ["(?i)GPIO1$"]
#       required: true
#       group_key: true
#   controller:
#     detect_by: core_component

# Step 5: (Optional) Run pattern query with custom YAML
python scripts/schematic-cli.py query data/E1005/ --pattern /tmp/i2c_custom.yaml
```

### Example 4: Design Review

```
User: "电源设计有问题吗？"
```

```bash
# Review mode: overview to find power page
python scripts/schematic-cli.py overview data/E1005/

# Query power page - extract power ICs only (U-prefix components)
python scripts/schematic-cli.py query data/E1005/ --page 6 \
  | python -c "import sys,json; d=json.load(sys.stdin); ics = [c for c in d['components'] if c['ref'].startswith('U')]; print(f\"Power ICs: {[(c['ref'], c['value'], c.get('mpn','')) for c in ics]}\")"

# Or extract power-related nets (VDD, VSYS, GND, etc.)
python scripts/schematic-cli.py query data/E1005/ --page 6 \
  | python -c "import sys,json; d=json.load(sys.stdin); power = [n for n in d['nets'] if any(k in n['name'].upper() for k in ['VDD','VSYS','VBAT','VIN','GND','3V3','5V'])]; print(f\"Power nets: {[(n['name'].split('/')[-1], n['pin_count']) for n in power[:10]]}\")"

# Identify power ICs, escalate to MCP for specs
# Check against schematic: capacitors present? enable pins correct?
# Report findings with evidence
```
