# Schematic Reading Strategy for LLM

## Mission

This document defines how an LLM should read KiCad schematics and Cadence OrCAD/Allegro schematics using the schematic-analyzer MCP tools.

**Goal**: Produce accurate answers to user questions—query what's needed for reliable conclusions, never dump raw files, never guess without grounding.

---

## Quick Reference

For MCP tools and core principles, see [SKILL.md](./SKILL.md).

**Output format**: All `query` commands output JSON. `mcp__sch__overview` outputs text.

**Pattern query**: `pattern` requires explicit YAML file. See Rule 1 for fallback strategy when pattern doesn't match.

---

The LLM should behave like a disciplined engineer:

1. **Choose entry mode** based on the question type
2. **Query the minimum path** — skip overview for targeted queries
3. **Read compact evidence** via `query` — not raw files
4. **Expand only when blocked** around the current uncertainty
5. **Escalate semantics** (MCP/datasheet) only when structure is insufficient
6. **Answer with confidence levels** — uncertainty is valid output

---

## Circuit Reasoning Principles

The tools output raw structural data (pin-net tables, connectivity, neighbors). These principles teach how to interpret that data — turning structure into meaning.

### Pin-Net Table Interpretation

| Pin Type | Interpretation |
|----------|---------------|
| VDD / VCC / VBAT | Device power domain — the **only** authoritative source for "what powers this IC" |
| GND / VSS / PGND | Ground domain |
| Signal pins | Interface connections — trace to determine actual usage |

- **Pin name** = device's physical definition (what the silicon provides)
- **Net name** = designer's functional intent (what the design uses it for)
- These may diverge — always verify both sides

### Network Topology Interpretation

| Topology Pattern | Likely Meaning |
|-----------------|----------------|
| Net connects IC + only passives (R/C/L/D) | Local signal: filtering, protection, pull-up/down, or decoupling |
| Net connects multiple ICs | Shared bus or power rail |
| Net passes through diode(s) | Power path selection, OR-ing, or reverse protection |
| Net fanout = 2 (IC + decoupling cap) | Dedicated power domain for that IC |
| Net connects IC pin to nothing else | Unused/reserved function, or design error |

### Physical Identity ≠ Functional Identity

- **Connector pin names** describe physical interface capability, NOT actual usage mode
  - Actual mode is determined by which signal lines are connected to a controller
- **Multi-function IC pins** may use only a subset of capabilities
  - Actual function depends on what's connected on the other end
- **Determining actual function requires tracing to both endpoints**
  - Don't conclude from one side alone — follow the signal to the IC that drives/receives it
  - If signal lines are not connected to a controller, the function is unused regardless of pin names

---

## Non-Negotiable Rules

### Rule 1: Choose Entry Mode First

Before any tool call, decide which mode fits the question:

| Mode | Trigger | First Action |
|------|---------|--------------|
| Architecture | "分析整体架构" "power tree" "subsystems" | `mcp__sch__overview` |
| Targeted | "U10是什么" "I2C_SDA在哪" 明确目标 | Direct `query` |
| Pattern | "I2C设备有哪些" "USB拓扑" | `pattern(file=<yaml_file>)` |
| Review | "设计有问题吗" "review" | `mcp__sch__overview` |

**Key principle**: For targeted queries with clear targets, skip overview and query directly.

**Pattern mode requires explicit YAML**: No builtin patterns. You must provide a pattern file.

**Pattern failure fallback**: If no matching YAML exists or pattern returns no results, do NOT skip the analysis:

1. Use broad text search to find candidate signals:
   `mcp__sch__net_search(project, text="SCK|CLK|MOSI|MISO|CS")`
   `mcp__sch__net_search(project, text="SDA|SCL")`
2. Group discovered nets by prefix (e.g., `SD_*`, `EP_*` indicate separate buses)
3. Verify each candidate bus by tracing connections
4. Do NOT conclude "no buses found" just because pattern failed

**How to obtain a pattern YAML**:

The files in `.claude/skills/schematic-analyzer/patterns/` (i2c.yaml, spi.yaml, etc.) are **schema examples only** — they show the YAML structure and generic net-name regexes. They may not match the actual net naming conventions in the project under analysis.

The correct workflow for pattern mode:
1. First use structural queries (`net_search`, `comp`) to discover the actual net names used for the bus in this project
2. Write a custom YAML pattern using the specific net names discovered (or regexes derived from them)
3. Run `pattern(file=<custom.yaml>)` to validate the bus topology across all participants

Example: if structural queries reveal nets named `FG_I2C_SDA` and `FG_I2C_SCL`, write a YAML with patterns targeting those specific names, not the generic `(?i)I2C.*SDA` from the example file.

The example YAMLs in `patterns/` are reference material for understanding the schema — not files to blindly pass to `pattern`.

**Pattern YAML Schema**:

```yaml
name: "I2C"                    # Pattern name (required)
category: bus                  # Category: bus, interface, power, etc.
description: "I2C interface"   # Human-readable description

signals:                       # Signal definitions (required)
  - role: scl                  # Signal role identifier
    patterns:                  # List of regex patterns (Python re syntax)
      - "(?i)^SCL$"
      - "(?i)^GPIO0$"
    required: true             # Must match for detection (default: true)
    group_key: true            # Use for grouping multiple buses (default: false)

  - role: sda
    patterns:
      - "(?i)^SDA$"
      - "(?i)^GPIO1$"
    required: true
    group_key: true

controller:                    # Controller detection config (optional)
  detect_by: core_component    # Method: core_component, reference_prefix, etc.

participants:                  # Participant filtering config (optional)
  filter:
    - reference_prefix: ["R", "C", "L", "D", "TP"]  # Exclude passives
  exclude_controller: true

extra_fields:                  # Additional metadata fields (optional)
  field_name:
    type: string               # Field type: string, boolean, integer
    source: infer              # Source: infer, property, net
    description: "Field desc"
```

**Key fields explained**:

| Field | Purpose |
|-------|---------|
| `signals[].patterns` | Python regex patterns matched against net names. Use `^`/`$` anchors for exact matching. |
| `signals[].required` | If true, bus detection requires this signal to match. |
| `signals[].group_key` | If true, signals with same suffix are grouped into one bus instance (e.g., I2C_0_SDA + I2C_0_SCL → one bus). |
| `controller.detect_by` | How to identify the bus controller. `core_component` uses the detected core MCU/SoC. |
| `participants.filter` | Exclude components by reference prefix (passives, test points, etc.). |

### Rule 2: Page Queries Require Overview

`page` uses numeric indices from `mcp__sch__overview` output. If you need page-level analysis, run overview first.

### Rule 3: References Are Globally Unique

The parser assumes **ERC-clean hierarchy**: each reference (U17, R5, C10) is unique across the entire project.

If a reference is not found: the component does not exist — check spelling or use `comp_search` to search.

**Net names** may be hierarchical (e.g., `/SCH_TOP/I2C_SDA`). Use exact name or `comp_search`. `net(name=<name>)` returns the root net name plus any connected `hierarchical_labels`, `global_labels`, and `local_labels` visible through the page hierarchy, including parent-sheet `sheet pin` aliases that rename a signal between pages.

### Rule 4: Structure Before Semantics

Start with structural evidence:
- Page placement, connectivity, neighbor counts
- Net names, pin assignments, property values

Do NOT start with:
- Datasheet reading
- MCP batch lookups
- Full netlist dumps into context

### Rule 5: Expand Around the Blocker

At every step, identify the **current blocker**:
- What prevents answering the user's question?
- What single object needs clarification?

Only expand evidence to resolve that blocker.

### Rule 6: Re-Ground All Inferred Conclusions

Any conclusion not directly read from MCP tool output is an inference and must be verified against schematic evidence. This applies to:

- **MCP/datasheet results**: Explain what a part *can* do, not what it *is doing* in this design
- **Device model inference**: A part's type/category does not determine its power domain, interface mode, or configuration
- **Connector type inference**: A connector's physical interface capability does not determine actual usage mode
- **Page/sheet name inference**: A page named "Power" does not mean every component on it is power-related

Every inference must tie back to:
- Actual connected pins (especially VDD/VCC for power domain claims)
- Actual net names and their endpoints
- Actual neighboring components
- Actual signal line connectivity (all lines, not just some)

**Evidence requirements by claim type**:

| Claim Type | Required Evidence | Insufficient Evidence |
|------------|-------------------|----------------------|
| Device power domain | VDD/VCC pin → actual net name | Bus pull-up voltage, page location, neighboring device power |
| Interface mode | All signal lines traced to controller endpoints | Connector pin names, partial signal tracing |
| Bus participants | Device signal pin connected to bus net | Device type, same page, same power domain |
| Power conversion | Converter input/output pin net names | Device model implying function |
| Backup/redundant power | Power pin connected to multiple sources via diode/switch | Device type typically needing backup |

### Rule 7: Uncertainty Is Valid

Valid outputs:
- `Unknown`, `Ambiguous`, `Low confidence`
- `Needs datasheet confirmation`
- `Component not found` (reference does not exist in project)

Invalid outputs:
- Guessing to make results look complete
- Datasheet conclusions without schematic grounding

---

## Reading Loop

Apply this loop adaptively based on entry mode.

### Step 1: Execute Minimum Path

**For Architecture/Review Mode**: `mcp__sch__overview(project)`
Output establishes: project scope, page index, core candidates.

**For Targeted/Pattern Mode**: skip overview, query directly
mcp__sch__comp(project, ref)
# → Filter large output:
#   | python -c "import sys,json; d=json.load(sys.stdin); print(d.get('value'), d.get('mpn'))"
#   | python -c "import sys,json; import json as j; d=j.load(sys.stdin); del d['neighbors']; print(j.dumps(d, indent=2))"

mcp__sch__pattern(project, file="/path/to/pattern.yaml")  # explicit file required
```

### Step 2: Form or Refine Hypothesis

From evidence gathered, state a working hypothesis:
- "U10 with 53 nets is likely the main MCU"
- "Pattern match found 2 I2C buses, U23 is the controller"
- "Net VIN_5V connects to 5 components, likely main power input"

### Step 3: Query Target Object

Use appropriate query type:

| Question | Command |
|----------|---------|
| What's on this page? | `page(index=<index>)` |
| What does this component do? | `comp(ref=<ref>)` (filtered) |
| Which pins are unconnected/floating? | `comp(ref=<ref>, full=true)` |
| Where does this net go? | `net(name=<name>)` |
| Find components with text | `comp_search(text=<text>)` |
| Find nets with text | `net_search(text=<text>)` |
| What MPN values exist? | `prop(key="MPN")` |
| Detect buses/subsystems | `pattern(file=<yaml_file>)` (explicit file required) |

### Step 3A: Handle Large Core Components Differently

If `mcp__sch__overview` shows a component with very high `connected_net_count` or `neighboring_symbol_count`, do **not** assume one `comp` result should be fully consumed inline.

**Choose the right output mode first**:

| Mode | Command | Output Content | Use Case |
|------|---------|----------------|----------|
| Filtered (default) | `comp <ref>` | Active pins only, hides `unconnected-*` | First inspection, role ID, connectivity questions |
| Full | `comp(ref=<ref>, full=true)` | All pins including unconnected | Pin audit, N/C check, datasheet cross-reference |

**Decision rule**: Start with filtered view. Only use `full=true` when the blocker explicitly requires unconnected pin visibility (N/C audit, pin count verification, floating pin check).

**For large components**: run filtered once to establish role and key connections. If payload is too large to consume inline, switch to indexed retrieval: scan once to identify key signals and neighbor refs, then follow up with targeted `net` / `comp` queries. Do not re-read the full dump.

Key principle: Filtered output = reading mode; Full output = audit mode.

### Step 4: Identify Blocker

Ask: What prevents a reliable answer?

| Blocker | Action Chain |
|---------|--------------|
| Component role unclear | `comp(ref=<ref>)` → check value/MPN → MCP lookup if needed |
| Net source unclear | `net(name=<name>)` → inspect `connected_refs` in output → `comp` on each |
| Bus ownership unclear | `pattern(file=<yaml_file>)` → check controller/participant roles |
| Design intent unclear | MCP spec lookup → datasheet → re-ground to schematic pins |

**Action chain format**: Each blocker maps to a concrete MCP tool sequence. No abstract verbs like "trace" or "check" without specifying how.

### Step 5: Expand Locally

From current query result, extract expansion targets:

**From `comp` output**:
- Find interesting net names → `net(name=<name>)` for signal tracing
- Find neighbor component refs in neighbors section → `comp(ref=<ref>)` to continue investigation
- Note the page_index → `page(index=<index>)` for page context

**From `net` output**:
- Find component refs connected to this net → `comp(ref=<ref>)` on each participant
- Check pages list to identify cross-page signals

**From `page` output**:
- Find components of interest → `comp(ref=<ref>)` for details
- Find interesting net names → `net(name=<name>)` for signal tracing

Do NOT jump to full-project analysis unless local path fails.

### Step 6: Escalate Semantics (Conditional)

If structure is insufficient:

```
structural evidence → pcbparts MCP → ee-datasheet-master skill → re-ground to schematic
```

**Escalation conditions**:
- Basic role cannot be determined from structure
- Pin functions need datasheet interpretation
- Answer depends on device-specific behavior (power, reset, address, boot)
- User explicitly asks for datasheet-backed explanation

**Datasheet policy**:

1. **Use ee-datasheet-master skill explicitly**: When datasheet information is needed, invoke the skill:
   ```
   /ee-datasheet-master <datasheet_path> "<question>"
   ```

2. **No datasheet available? Ask user**: If the required datasheet is not in the current environment, ask the user to provide it:
   - "I need the datasheet for <MPN> to answer this question. Can you provide the PDF file?"
   - Do NOT rely on prior knowledge or guess datasheet contents

3. **Re-ground to schematic**: Datasheet explains what a part *can* do. Verify against what it *is doing* in this design:
   - Check actual pin connections
   - Verify configuration against schematic evidence

### Step 6.5: Verify Claims Before Output

Before synthesizing, run this verification loop:

```
For each key claim:
  1. Does collected evidence support this conclusion?
  2. Are there obvious gaps or contradictions?
  3. If uncertain → expand search, do not guess
  4. If evidence contradicts → revise hypothesis, retry from Step 2
  5. Only proceed to Answer when verification passes
```

**Verification checklist**:

1. **Classify** — what type of claim is this? (power domain, interface mode, bus participant…)
2. **Check evidence** — do I have the required evidence type for this claim? (see Rule 6 table)
3. **Fill gaps** — if evidence is missing, issue the specific query to obtain it. Do not guess.
4. **Contradict check** — does any collected evidence contradict this claim? If yes, revise and loop back.
5. **Downgrade** — if evidence cannot be obtained, downgrade to `Low confidence` or `Unknown`

**This step is mandatory.** Do not skip to Answer when verification fails — expand and retry instead.

### Step 7: Synthesize Answer

When verification passes, synthesize:
- State the conclusion
- List supporting evidence
- Note remaining uncertainty
- Stay within requested scope

---

## Context Management

### What to Keep in Context

- `mcp__sch__overview` output (compact, ~50 lines)
- Query results for current investigation path
- Hypothesis and blocker status
- Key component/nets for current answer

### What NOT to Load

- Full project JSON exports
- Full netlists
- All sheets at once
- Long pin dumps for large ICs
- Large batches of MCP results

### Large Object Navigation

For large core components (SoM, MCU, FPGA with dozens/hundreds of nets), large output signals a mode switch from "direct reading" to "indexed retrieval":

1. Scan once to identify key elements: main power rails, interface buses, control signals
2. Note relevant net names and neighbor refs for follow-up queries
3. Issue targeted queries instead of re-reading the full dump:
   - `net(name=<name>)` for specific signals
   - `comp(ref=<neighbor_ref>)` for adjacent components
   - `page(index=<index>)` for page context

This is a reasoning strategy within the current session.

### Project Cache (Automatic)

```bash
# Check cache status
(removed — cache is automatic)

# Clear if schematic changed
(removed — cache is automatic)
```

Cache is project-level, automatic for repeated queries. Manual clear only when schematic file changed. It does NOT provide object-level result storage for LLM reasoning.

---

## Output Contracts

### For Explanation Tasks

Answer should state:
- What the object likely is
- Why that conclusion follows from schematic evidence
- What remains uncertain

### For Architecture Tasks

Answer should state:
- Main structural anchors (core components)
- Important subsystem relationships
- Supporting evidence for each relationship
- Weakly supported areas

### For Review Tasks

Answer should state:
- Concrete findings with evidence trails
- Open risks or missing confirmations
- What was not checked or proven

---

## Recovery Rules

If the answer is weak, improve one of:

1. **Reference check**: Does the reference exist? Is it spelled correctly?
2. **Evidence quality**: Is the query output sufficient?
3. **Local expansion**: Did we trace enough neighbors?
4. **Semantic escalation**: Did we check MCP/datasheet?
5. **Re-grounding**: Did we tie datasheet knowledge back to schematic?

Then reason again.

---

## Summary

| Principle | Action |
|-----------|--------|
| Choose mode first | Architecture/Review → overview; Targeted/Pattern → direct query |
| Query minimum | Only load evidence needed for current blocker |
| Structure first | Use connectivity and placement before datasheets |
| Expand locally | Trace neighbors, don't analyze everything |
| Verify before output | Audit each claim against its required evidence type (Step 6.5) |
| Trace both endpoints | Don't conclude from one side of a connection — check both ends |
| Escalate conditionally | MCP/datasheet only when structure is insufficient |
| Ground all inferences | Every non-tool-derived conclusion must tie back to pin/net evidence |
| Accept uncertainty | "Unknown" is valid; guessing is not |
