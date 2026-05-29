---
name: ee-datasheet-master
description: "Use when user has/is reading a component datasheet or spec sheet to find chip parameters: pinout, voltage, I2C address, timing, register map, electrical characteristics. Trigger on PDF+chip questions. Also: 规格书, 数据手册, 芯片参数. All IC types."
compatibility: Requires python3 and the Python packages listed in scripts/requirements.txt.
---

# EE Datasheet Master

## Instructions

### Step 1: Confirm the required inputs and environment

- Require a valid PDF path
- Require `python3` (Windows: `python`)
- MCP server `ds` must be configured in `.claude/mcp.json`

If a required dependency or input is missing:
- Stop before claiming the skill is usable for this task
- State exactly what is missing
- Tell the user the skill may be installed, but the current task is blocked until that requirement is provided

### Step 2: Follow the PDF-only extraction rule

All factual output must come from the PDF itself. If the PDF cannot provide the answer, return `NOT SPECIFIED IN DATASHEET` and explain the most direct way to obtain that information.

### Step 3: Handle errors — STOP, don't work around

All MCP tools return `{"error": true, "type": "...", "message": "...", "fix": "..."}` when something is wrong. When you see this:

1. **STOP immediately.** Do NOT try another approach, guess data, or "try anyway."
2. **Relay the `fix` field verbatim to the user** — it tells them exactly what to install or correct.
3. **Do not proceed** until the user confirms the fix is applied.

Common error types:

| `type` | Meaning |
|--------|---------|
| `missing_dependency` | Python package not installed (fastmcp, pymupdf, pdfplumber, etc.) |
| `missing_file` | PDF file not found at the given path |
| `invalid_file` | File exists but is not a valid PDF (corrupted or wrong format) |
| `invalid_input` | Bad parameters passed to the tool |
| `not_found` | Content not found in the PDF |

## Iron Law: PDF Content Only

```
ALL DATA MUST ORIGINATE FROM THE PDF.
Allowed: Extract → Calculate from extracted data
Forbidden: Use prior knowledge → Fill gaps with guesses
```

### Allowed Derivations

| Type | Example |
|------|---------|
| Mathematical calculation | P = V × I from voltage and current |
| Unit conversion | dBm → mW, binary → hex |
| Address calculation | "001000x" → 0x10/0x11 |
| Counting | Pin count from Pin Description table |

**When deriving: Show source data (page) + calculation steps + result**

### Forbidden Behaviors

| Behavior | Correction |
|----------|------------|
| "I know this chip..." | Find the spec in PDF |
| "Typical value is..." | Read the actual value from PDF |
| "Similar chips have..." | This one may differ |
| Guessing to fill gaps | Output "NOT SPECIFIED IN DATASHEET" + acquisition path (see below) |

---

## When the PDF Cannot Provide the Answer

"NOT SPECIFIED IN DATASHEET" is not a dead end. Always follow it with **how to obtain the missing information**.

### Response Template

> "[Parameter] is not specified in this datasheet.
> To obtain it: [specific method below]."

If the datasheet references an application note or supplementary doc by name, cite it:
> "Section X references Application Note [AN-xxx] for this topic — search [Manufacturer] website."

### Reasoning Framework for Missing Parameters

When a parameter is absent, reason through these questions to give a concrete, actionable path:

**1. Why is it missing?**
- *Wrong document* — this is a brief/product datasheet; the full reference manual or application note contains it → identify the correct document by name
- *Test-condition mismatch* — the spec exists but not at the user's specific conditions (load, frequency, temperature) → explain which conditions differ and how that affects the value
- *Application-dependent* — the value depends on external components or PCB layout the user controls → explain what determines it and how to calculate or simulate
- *Manufacturer-controlled* — the data is from qualification testing, not released publicly → identify the right contact channel

**2. What does the user actually need it for?**
- Design margin check → an approximation or worst-case bound may be sufficient
- Debugging a failure → direct measurement in the actual circuit is more reliable than a datasheet value
- Qualification / compliance → only manufacturer-provided data is acceptable

**3. What is the most direct path given the above?**
Tailor the recommendation to the specific parameter and context — a thermal resistance question for an LDO in a hot enclosure calls for a different answer than the same question for a signal-path op-amp. Reason about: what equipment would give this measurement, what document would contain this spec, or what formula derives this value from things the user can measure or control.

---

## 6-Phase Workflow

```
┌─────────────────────────────────────────────────────────────┐
│  Phase 0: Pre-scan        →  全文扫描，建结构地图            │
│  Phase 1: Diagnosis       →  text vs image PDF 决策         │
│  Phase 2: Device ID       →  确认器件，推断关键参数          │
│  Phase 2b: Targeted Scan  →  推断 patterns，二次精准扫描     │
│  Phase 3: Section Mapping →  定位各功能区页码               │
│  Phase 4: Extraction      →  精准提取 + TEMPLATES 结构化输出 │
└─────────────────────────────────────────────────────────────┘
```

**See [PDF_STRATEGY.md](PDF_STRATEGY.md) for the entry-point decision table and detailed workflow. Read that first — it tells you which phase to start at before running any command.**

### MCP Tools

Server: `ds` — invoke as `mcp__ds__<tool>(...)`.

| Tool | Purpose |
|------|---------|
| `mcp__ds__info(pdf)` | PDF metadata: pages, title, author |
| `mcp__ds__search(pdf, keyword)` | Full-text search across entire PDF |
| `mcp__ds__search_table(pdf, keyword)` | Search inside tables only |
| `mcp__ds__text(pdf, page)` | Extract plain text from a page |
| `mcp__ds__tables(pdf, page)` | Extract tables from a page |
| `mcp__ds__toc(pdf)` | Table of contents / outline |
| `mcp__ds__page_hints(pdf)` | Scan for register maps, pinouts, specs |
| `mcp__ds__page_stats(pdf)` | Text density, table count per page |
| `mcp__ds__search_caption(pdf)` | Figure/table caption search |
| `mcp__ds__nearby(pdf, page, pattern)` | Text near a pattern match |
| `mcp__ds__render(pdf, page)` | Render page to PNG image |
| `mcp__ds__patterns()` | Dump built-in search patterns |

### Quick Reference

**Most common — device named, 1–2 specific parameters:**
```
mcp__ds__search_table(pdf="<path>", keyword="<parameter>")
mcp__ds__search(pdf="<path>", keyword="<parameter>")       # alternate phrasing

mcp__ds__text(pdf="<path>", page=<n>)
mcp__ds__tables(pdf="<path>", page=<n>)
```

**Less common — unknown PDF, open-ended analysis:**
```
mcp__ds__info(pdf="<path>")
mcp__ds__page_hints(pdf="<path>")                           # scan all pages

mcp__ds__text(pdf="<path>", page=1)                         # identify device

mcp__ds__search_caption(pdf="<path>")                       # section mapping
mcp__ds__search(pdf="<path>", keyword="Electrical Characteristics")
```

---

## Parameter Inference (LLM Decision)

### Universal Parameters (for full-analysis queries only)

When the user asks for a complete analysis or overview, extract these 5 baseline parameters. **Skip this for targeted single-parameter queries** — if the user asks "what is the dropout voltage?", go find that, not the package outline.

| Parameter | Search Keywords | Notes |
|-----------|----------------|-------|
| **Manufacturer** | First page header/footer | Company name |
| **Part Number** | First page title | Full part number |
| **Package** | "Package", "封装" | Must include pin count (e.g., QFN-32) |
| **Operating Voltage** | "VDD", "VCC", "Supply Voltage", "电源电压" | Range: min to max |
| **Operating Temperature** | "Operating Temperature", "工作温度" | Range: min to max |

### Device-Specific Parameters (Inferred by LLM)

After identifying the device, infer what specs matter:

```
1. Read device description (first 3 pages)
2. Understand: What does this device DO?
3. Infer: What specs matter for this device?
4. Search: Use MCP tools to locate those specs
```

For the complete device-type → key specs lookup table and per-device extraction shortcuts, see **[PDF_STRATEGY.md → Phase 2 and Device-Type Shortcuts](PDF_STRATEGY.md)**.

**Key insight:** Device description tells you what to measure. Don't use predefined lists.

---

## Output Format

```markdown
# [Part Number] Datasheet Analysis

## Summary
[1-2 sentences]

## Key Specifications
| Parameter | Min | Typ | Max | Unit | Source | Notes |
|-----------|-----|-----|-----|------|--------|-------|
| ... | ... | ... | ... | ... | Page X, "Table Name" | |
| [unavailable param] | — | — | — | ... | NOT SPECIFIED | Measure: [method] |

## Pin Configuration
- Package: [Type]-[Pin Count]
- Power Domains: [List ALL with pin numbers]
- Interfaces: [I2C/SPI/UART with addresses]

## Critical Design Considerations
1. [Issue with guidance]

## Common Pitfalls
- [Pitfall]: [How to avoid]
```

---

## Common Mistakes

| Mistake | Example | Correction |
|---------|---------|------------|
| Missing pin count | "QFN package" | "QFN-32 package" |
| Partial power domains | "VDD" only | "VDD (pins 1, 13, 32)" |
| I2C address wrong | "0x18" | Show calculation from format |
| Missing source | "SNR: 93 dB" | "SNR: 93 dB (Page 8, Typ)" |
| Hallucinated specs | Any value without source | Always cite page and table |

---

## Troubleshooting

Error: `ModuleNotFoundError: fitz` or `No module named 'pdfplumber'`
Cause: Python dependencies are not installed.
Solution: Run `pip install -r scripts/requirements.txt` before continuing.

Error: `File not found` or the PDF path does not exist
Cause: The PDF was not provided or the path is wrong.
Solution: Ask the user for the exact PDF path. Do not answer from memory or general web knowledge.

Error: `is_text_based: false` or extracted text is mostly garbage
Cause: The PDF is image-based or uses difficult font encoding.
Solution: Use `render_page`, read visually, and lower confidence. If manufacturer or part number cannot be confirmed from the rendered page, return `UNABLE TO VERIFY`.

Error: The requested parameter is not in the datasheet
Cause: The value is genuinely absent from this document, or the wrong document was provided.
Solution: Return `NOT SPECIFIED IN DATASHEET` and follow it with the most direct acquisition path.

Error: Tool commands keep failing
Cause: Broken Python environment, unsupported PDF edge case, or damaged file.
Solution: Report the failing command and classify the issue as dependency, file integrity, or extraction quality. Do not present guesses as extracted facts.

---

## Red Flags - STOP and Verify

If you think:
- "I know this chip..."
- "Typically this value is..."
- "Based on my experience..."
- "Similar chips have..."

**STOP → Re-read PDF → Extract from source**

---

## Reference Files

| File | Purpose |
|------|---------|
| [PDF_STRATEGY.md](PDF_STRATEGY.md) | 6-phase workflow, device-type extraction shortcuts |
| [TEMPLATES.md](TEMPLATES.md) | Structured output templates: device_info, power_domains, I2C, SPI, electrical_specs |
| [scripts/pdf_tools.py](scripts/pdf_tools.py) | PDF extraction tools (legacy CLI) |
| [scripts/datasheet_mcp.py](scripts/datasheet_mcp.py) | MCP server (FastMCP) |
