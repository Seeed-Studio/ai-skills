# PDF Reading Strategy

## Step 0: Choose Your Entry Point (Do This First)

Before running any command, decide where to start. `page_hints` on a 100-page PDF takes minutes — only run it when you genuinely need a structural map of an unknown document.

| Situation | Start at | Why |
|-----------|----------|-----|
| **Device named + 1–2 specific parameters** | **Phase 3** | You already know what and where to look — go directly to `search` / `search_table`. `page_hints` adds no value here. |
| Follow-up question on same document | Phase 3 or 4 | Document already known; rescanning wastes time. |
| Unknown PDF, open-ended analysis ("tell me about this chip") | Phase 0 | Need structural map before anything. |
| Suspected or confirmed image-based PDF | Phase 0 | Must confirm PDF type before choosing read path. |
| Complex IC (charger, MCU, CODEC) + many parameters at once | Phase 0–2b | Proprietary section names need targeted patterns to locate. |

**Fallback rule:** If targeted extraction fails (parameter not found, table malformed), then step back to an earlier phase — run `page_hints` or `search` rather than guessing.

---

## Core Principle

**Navigate first, extract second.** Never read pages blindly. The phases below are a toolkit — pick the right tool for the job.

```
┌─────────────────────────────────────────────────────────────────┐
│  Phase 0: Pre-scan        →  默认 patterns 扫全文，建粗粒度地图  │
│  Phase 1: Diagnosis       →  决定读取路径 (text vs image)        │
│  Phase 2: Device ID       →  确认器件身份，推断要提取的参数      │
│  Phase 2b: Targeted Scan  →  用推断出的关键词二次扫描，细化地图  │
│  Phase 3: Section Mapping →  精确定位各功能区的页码              │
│  Phase 4: Extraction      →  按器件类型执行有针对性的提取        │
└─────────────────────────────────────────────────────────────────┘
```

## Table of Contents

- [Phase 0: Pre-scan](#phase-0-pre-scan-unknown-pdfs-and-open-ended-queries-only)
- [Phase 1: Diagnosis](#phase-1-diagnosis)
- [Phase 2: Device Identification](#phase-2-device-identification)
- [Phase 2b: Targeted Re-scan with Inferred Patterns](#phase-2b-targeted-re-scan-with-inferred-patterns)
- [Phase 3: Section Mapping](#phase-3-section-mapping)
- [Phase 4: Targeted Extraction](#phase-4-targeted-extraction)
- [Device-Type Extraction Shortcuts](#device-type-extraction-shortcuts)
- [Error Recovery](#error-recovery)
- [Image PDF: Full Workflow](#image-pdf-full-workflow)

---

## Phase 0: Pre-scan (unknown PDFs and open-ended queries only)

**Purpose:** Build a structural map of the entire document in one pass. Use this when you don't yet know where to look — if the device and parameter are already known, go to Phase 3 instead. `page_hints` on a large datasheet is the slowest operation available; only run it when the structural map will actually inform your next step.

```bash
mcp__ds__info(pdf="<pdf_path>")
mcp__ds__page_hints(pdf="<pdf_path>")   # scan ALL pages
```

`page_hints` returns per-page signals and heuristic labels. Use this to identify candidate pages for each section:

| Hint Label | Target Section |
|------------|---------------|
| `likely_pinout_page` | Pin configuration, Pin description table |
| `likely_timing_diagram` | Timing waveforms (almost always image, use render_page) |
| `likely_block_diagram` | Functional diagram (image, use render_page) |
| `likely_curve_page` | Electrical characteristics curves (image) |
| `likely_package_page` | Package outline, mechanical dimensions |
| `likely_register_figure` | Register map, bit field descriptions |
| `likely_table_page` | Electrical specs table, absolute maximum ratings |

**Treat hints as candidates, not facts.** A `score > 0.5` with 2+ reasons is reliable. A page that matches `likely_table_page` near a `search` hit for "Electrical Characteristics" is almost certainly correct.

### Pre-scan Output (Record This)

```
PDF: <filename>
Pages: N | Type: text / image
Candidate Pages:
  - Pinout: [p12, p13]
  - Timing diagrams: [p18, p19, p22]
  - Block diagram: [p4]
  - Electrical specs tables: [p8, p9, p10]
  - Package: [p27]
  - Registers: [p30-p45]
```

---

## Phase 1: Diagnosis

Use the `info` result already obtained in Phase 0 — no need to re-run.

| `is_text_based` | Strategy |
|-----------------|----------|
| `true` | Text extraction path. Use `page_hints` scan + targeted reads. |
| `false` | **Image path.** Render key pages with `render_page`, read visually. |

### Image PDF Path

```bash
# Render first 3 pages to identify device
mcp__ds__render(pdf=<pdf_path> 1 180)
mcp__ds__render(pdf=<pdf_path> 2 180)
mcp__ds__render(pdf=<pdf_path> 3 180)
```

Read rendered images visually. Cross-validate: manufacturer + part number from image must match filename/context. If mismatch → output `UNABLE TO VERIFY`.

For image PDFs, use `render_page` for ALL sections. Typical flow:
1. Render cover → identify device
2. Render pre-scan candidate pages → confirm section locations
3. Render target pages → extract specs visually

---

## Phase 2: Device Identification

```bash
mcp__ds__text(pdf=<pdf_path>, page=1)
# If page 1 is cover only (short text):
mcp__ds__text(pdf=<pdf_path>, page=2)
```

Extract:
1. **Part number** — first page title, usually `[A-Z]+[0-9]+` pattern
2. **Manufacturer** — first page header/footer
3. **Device function** — Features or Description section

From the device function, **infer which parameters matter:**

| Device Type | Key Specs to Extract |
|-------------|---------------------|
| **LDO / Linear Regulator** | Vout accuracy, dropout voltage, quiescent current, PSRR, load regulation |
| **DC-DC Converter** | Vin/Vout range, efficiency, switching frequency, Iq, feedback voltage |
| **Battery Charger** | Charge voltage, charge current, termination, power path, DPM threshold |
| **MCU / SoC** | Core voltage, I/O voltage, clock speed, flash/RAM, peripherals, startup time |
| **ADC / DAC** | Resolution, INL/DNL, SNR, THD+N, sample rate, reference voltage |
| **Audio CODEC** | ADC/DAC SNR, THD+N, sample rate, I2S format, PLL, analog gain range |
| **Sensor (IMU/Temp/etc.)** | Range, sensitivity/resolution, ODR, noise density, supply current |
| **Flash / EEPROM** | Capacity, read/write speed, erase time, endurance cycles, retention |
| **Interface (USB/CAN/RS485)** | Data rate, voltage levels, bus capacitance, propagation delay |
| **Power Mux / Load Switch** | Ron, Ilim, transition time, Vgs threshold |
| **Port Expander / MUX / Analog Switch** | Ron, bandwidth, leakage, VOH/VOL |

---

## Phase 2b: Targeted Re-scan with Inferred Patterns

**Purpose:** After reading the device description, you now know this chip's proprietary feature names, functional blocks, and internal terminology. Use that knowledge to build a custom `--patterns` JSON and re-run `page_hints` to find sections that default patterns miss.

### When to Trigger

Run Phase 2b when the device has **domain-specific subsystems** not covered by default patterns:
- Complex power ICs (charger, PMU, fuel gauge) — state machines, protection modes
- MCU/SoC — clock tree, DMA, interrupt controller, peripheral registers
- Audio CODEC — signal path, mixer routing, PLL, analog stages
- Memory — command set, erase architecture, status registers
- Interface/Protocol ICs — protocol state machine, enumeration flow, negotiation

Skip Phase 2b for simple devices: LDO, discrete MOSFET, gate logic, op-amp, diode, EEPROM (basic), RTC.

### How to Construct Patterns

**Source material** for inferring patterns — read in this order:

1. **Features list** (page 1-2): Proprietary feature names are the best patterns.
   > "VINDPM tracking" → pattern: `"VINDPM"`
   > "Automatic clock switching between HSE and HSI" → pattern: `"clock switching"`
   > "On-chip FIFO with 32 levels" → pattern: `"FIFO"`

2. **Table of Contents** (if extracted): Section titles are exact patterns.
   > "4.3 Charge State Machine" → pattern: `"charge state machine"`
   > "6.2 DMA Controller" → pattern: `"DMA controller"`

3. **Section headings seen in page text** (from Phase 0 text samples): reuse them verbatim.

### Pattern Quality Rules

| Good Pattern | Bad Pattern | Why |
|---|---|---|
| `"VINDPM"` | `"voltage"` | Specific term, won't false-positive |
| `"charge state machine"` | `"charge"` | Phrase-level, matches section headings |
| `"clock tree"` | `"clock"` | Discriminative for MCU clock config page |
| `"FIFO mode"` | `"mode"` | Too generic otherwise |
| `"DMA controller"` | `"memory"` | Targets a specific section |

**Keep patterns short (2–4 words), prefer exact subsystem names over common words.**

### Execution

```bash
# Step 1: Get default patterns as base (to not lose default coverage)
mcp__ds__patterns() > /tmp/custom_patterns.json

# Step 2: Edit /tmp/custom_patterns.json — ADD new labels with inferred patterns.
# Do NOT remove existing default keys. Example additions:
# {
#   ...existing defaults...,
#   "likely_charge_state_machine": ["charge state machine", "charging operation", "VINDPM"],
#   "likely_clock_config":         ["clock tree", "system clock", "PLL configuration"],
#   "likely_dma_section":          ["DMA controller", "DMA channel", "direct memory access"]
# }

# Step 3: Re-scan with custom patterns
mcp__ds__page_hints(pdf="<pdf_path>") --patterns /tmp/custom_patterns.json
```

### Merge Results

After Phase 2b, merge the two scan results:
- Phase 0 result → gives structural pages (pinout, timing, block diagram, package)
- Phase 2b result → gives domain-specific pages (state machine, clock tree, FIFO config)

Together they form the complete section map for Phase 3 targeted extraction.

---

## Phase 3: Section Mapping

Combine pre-scan hints with targeted searches to build a precise section map.

### Step 3a: Use Caption Search (Primary)

```bash
mcp__ds__search_caption(pdf="<pdf_path>")
```

Datasheet figure/table captions are the most reliable section locators. Look for:
- `Table X. Absolute Maximum Ratings`
- `Table X. Recommended Operating Conditions`
- `Table X. Electrical Characteristics`
- `Table X. Pin Functions` / `Pin Description`
- `Figure X. Functional Block Diagram`
- `Figure X. Timing Diagram`

### Step 3b: Keyword Search (Backup)

```bash
mcp__ds__search(pdf=<pdf_path>, keyword="Absolute Maximum")
mcp__ds__search(pdf=<pdf_path>, keyword="Electrical Characteristics")
mcp__ds__search(pdf=<pdf_path>, keyword="Pin Functions")
mcp__ds__search(pdf=<pdf_path>, keyword="Block Diagram")
```

Multi-language keywords:

| Section | English | Chinese |
|---------|---------|---------|
| Absolute Max | "Absolute Maximum Ratings", "Max Ratings" | "绝对最大额定值" |
| Electrical Specs | "Electrical Characteristics", "DC Characteristics" | "电气特性" |
| Pin Config | "Pin Functions", "Pin Description", "Pinout" | "引脚功能", "引脚说明" |
| Timing | "Timing Diagram", "Timing Requirements" | "时序图", "时序要求" |
| Package | "Package Information", "Mechanical Data" | "封装信息", "封装尺寸" |
| Application | "Typical Application", "Application Circuit" | "典型应用" |

### Step 3c: TOC (If Available)

```bash
mcp__ds__toc(pdf="<pdf_path>")
```

Most datasheets don't have a machine-parseable TOC. Use this as a bonus, not a primary strategy. If it returns entries, cross-check page numbers with Phase 0 hints.

### Confirm Pages

For each candidate page, confirm it's the right section:

```bash
mcp__ds__text(pdf="<pdf_path>", page=<page_num>)
```

---

## Phase 4: Targeted Extraction

Before extracting, consider opening **[TEMPLATES.md](TEMPLATES.md)** for structured output formats:
- `device_info` — manufacturer, part number, package, temperature range
- `power_domains` — all VDD/GND pins with pin numbers
- `i2c_interface` — address calculation, speed, pull-up
- `electrical_specs` — absolute max / operating conditions / key parameters

### 4a. Electrical Characteristics Tables

**This is the core extraction.** Most datasheets have 3 mandatory tables:

| Table | Always Present | Search Keyword |
|-------|---------------|----------------|
| Absolute Maximum Ratings | Yes | "Absolute Maximum" |
| Recommended Operating Conditions | Yes | "Recommended Operating" |
| DC Electrical Characteristics | Yes | "Electrical Characteristics", "DC Characteristics" |

```bash
# Extract tables from the identified pages
mcp__ds__tables(pdf="<pdf_path>", page=<page_num>)

# Or search directly in tables
mcp__ds__search_table(pdf=<pdf_path>, keyword="output voltage")
mcp__ds__search_table(pdf=<pdf_path>, keyword="quiescent current")
```

**LLM decision after table extraction:**
1. Is this the correct table? (Check table header row)
2. Which row is the target parameter? (Exact name match, not partial)
3. Which column: Min / Typ / Max? (Use Typ for nominal design, Min/Max for margin analysis)
4. Are there footnotes? (Often contain critical conditions: temperature range, load, frequency)
5. What are the test conditions? (Check rows above table, or separate "Test Conditions" column)

### 4b. Pin Description

Pin description tables are often multi-page. Read ALL pages of the pin section.

```bash
# Find pin section start
mcp__ds__search(pdf=<pdf_path>, keyword="Pin Functions")

# Extract tables from each page of the section
mcp__ds__tables(pdf="<pdf_path>", page=<page_num>)
# Repeat for each subsequent page until pin table ends (increment page number manually)
mcp__ds__tables(pdf=<pdf_path>, page=<next_page_num>)
```

For the pin diagram (image in all PDFs):
```bash
mcp__ds__render(pdf=<pdf_path> <pinout_diagram_page> 200)
```

### 4c. Timing Diagrams

**Timing diagrams are almost always images**, even in text-based PDFs. Never try to extract timing from text.

```bash
mcp__ds__render(pdf=<pdf_path> <timing_page> 200)
```

For timing parameters (setup/hold/pulse width), these appear as tables alongside the diagram:
```bash
mcp__ds__tables(pdf=<pdf_path>, page=<timing_page>)
mcp__ds__nearby(pdf=<pdf_path>, page=<timing_page>, pattern="t[SHDWRCP]", context_lines=3)
```

### 4d. Inline Parameter Extraction

Some parameters appear inline in text, not in tables (especially in Chinese datasheets):

```bash
mcp__ds__nearby(pdf=<pdf_path>, page=<page_num>, pattern="output voltage", context_lines=2)
mcp__ds__nearby(pdf=<pdf_path>, page=<page_num>, pattern="V[oO][uU][tT]\s*=?\s*[\d\.]+", context_lines=2)
```

### 4e. Application Circuit & Block Diagram

Always image. Render and read visually:

```bash
mcp__ds__render(pdf=<pdf_path> <page_num> 180)
```

These pages provide design context: recommended external components, power sequencing, PCB layout hints. Do NOT skip them even if specs are already extracted.

### 4f. Package Information

```bash
mcp__ds__render(pdf=<pdf_path> <package_page> 200)
mcp__ds__tables(pdf=<pdf_path> <package_page>  # for dimension, page=tables)
```

Record: package type, pin count, exposed pad (if any), land pattern reference.

---

## Device-Type Extraction Shortcuts

### Power Management ICs (LDO, DC-DC, Charger)

Priority order:
1. `search_table "output voltage"` → Vout range
2. `search_table "input voltage"` → Vin range
3. `search_table "quiescent"` or `"Iq"` → standby current
4. `search_table "efficiency"` → but efficiency is usually a **curve** → `render_page`
5. `search_table "feedback voltage"` → Vfb (for adjustable output calculation)
6. `nearby_text` on application page → Rsense, Rfb values in example circuits

**Trap:** Charger ICs have multiple current specs (precharge, fast charge, termination). Read the full charging state machine diagram — always `render_page`.

### MCU / SoC

Priority order:
1. `text page 1-2` → core architecture, max frequency, flash/RAM size
2. `search "Supply Voltage"` → VDD range
3. `search "I/O"` → GPIO voltage tolerance (3.3V only vs 5V tolerant)
4. `page_hints` to find register section → `render_page` for register bit diagrams
5. `tables` for peripheral electrical specs (I2C, SPI, UART timing)

**Trap:** MCU datasheets often have a separate "Electrical Characteristics" doc. If page count is low, it may be a brief datasheet only — check if there's a full reference manual.

### Sensors (IMU, Temperature, Pressure)

Priority order:
1. `search_table "sensitivity"` → scale factor
2. `search_table "noise"` or `"noise density"` → resolution floor
3. `search_table "output data rate"` or `"ODR"` → sampling speed
4. `search_table "supply current"` → active vs sleep
5. `render_page` on any page with `likely_curve_page` hint → noise vs ODR curves

**Trap:** Sensitivity and full-scale range are linked. A ±2g range at 1mg/LSB ≠ a ±16g range at 1mg/LSB. Always extract the range-sensitivity pair together.

### Memory (Flash, EEPROM, SRAM)

Priority order:
1. `search_table "read"` → read speed (MHz/ns)
2. `search_table "program"` or `"write"` → write time per page/byte
3. `search_table "erase"` → sector/block/chip erase time
4. `search_table "endurance"` → erase cycles
5. `search_table "retention"` → data retention years
6. `render_page` for command table page (often image in legacy datasheets)

### Interface ICs (USB, CAN, RS-485, Ethernet PHY)

Priority order:
1. `search "data rate"` or `"bit rate"` → max speed
2. `search_table "propagation delay"` → driver/receiver delay
3. `render_page` on timing diagram pages
4. `search_table "input threshold"` → VOH/VOL, VIH/VIL
5. `search_table "bus capacitance"` → drive strength requirements

---

## Error Recovery

### Parameter Not Found in Expected Table

```
1. Try search_table with alternative keywords:
   "SNR" → also try "signal to noise", "信噪比"
2. Try nearby_text with regex on the identified page
3. Check if parameter is in a different section (e.g., specs split across pages)
4. Try search across full document
5. If genuinely absent: output "NOT SPECIFIED IN DATASHEET"
```

### Table Extraction Malformed / Empty

```
1. Extract page text: pdf_tools.py text <pdf_path> <page>
2. Use nearby_text with regex to find value in text
3. render_page to visually read the table
4. Note extraction method: "Extracted from page text" or "Read from rendered image"
```

### Multiple Matches for Same Parameter

```
1. Check if one match is in "Absolute Maximum" (stress limit, not operating)
2. Check if one match is in "Recommended Operating Conditions" (normal range)
3. Prefer "Electrical Characteristics" table for typical/min/max specs
4. If still ambiguous: cite ALL sources with different values
```

---

## Image PDF: Full Workflow

```bash
# 1. Confirm image-based
mcp__ds__info(pdf="<pdf_path>")
# → is_text_based: false

# 2. Render cover pages
mcp__ds__render(pdf=<pdf_path> 1 180)
mcp__ds__render(pdf=<pdf_path> 2 180)

# 3. Identify device from rendered images (visual reading)
# Cross-validate: part number + manufacturer must match context

# 4. Pre-scan with page_hints (works on image PDFs via text layer detection)
mcp__ds__page_hints(pdf="<pdf_path>")

# 5. Render candidate pages for each section
mcp__ds__render(pdf=<pdf_path> <page> 200)

# 6. Extract specs visually from rendered images
# All image PDF extractions → confidence: LOW
# Cross-validation passed → confidence: MEDIUM
```

**Confidence for image PDFs:**

| Level | Condition |
|-------|-----------|
| `MEDIUM` | Cross-validation passed, value clearly readable in rendered image |
| `LOW` | Default for all image-based extractions |
| `UNVERIFIED` | Cross-validation failed (part number mismatch) |
