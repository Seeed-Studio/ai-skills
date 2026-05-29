# EE Datasheet Master

A skill for extracting specifications from electronic component datasheets with full source citations. All data must originate from the PDF — no prior knowledge, no guessing.

## Supported Device Types

Power management · MCU/SoC · ADC/DAC/CODEC · Sensor (IMU, temperature, pressure) · Flash/EEPROM · Interface (USB, Ethernet, CAN, RS-485) · Discretes (MOSFET, diode, gate logic) · Clock/PLL · Port expander · Battery charger/gauge

Optimized for English and Chinese datasheets. Other languages have degraded accuracy.

---

## Workflow Overview

```
Phase 0   → page_hints (all pages, default patterns)  → coarse structural map
Phase 1   → info                                       → text vs image PDF
Phase 2   → text page 1-2                             → device ID + infer params
Phase 2b  → page_hints --patterns (inferred keywords)  → fine-grained section map
Phase 3   → search_caption + search                    → confirm page numbers
Phase 4   → tables / search_table / nearby_text        → extract values
           render_page                                 → timing / diagram pages
```

See [PDF_STRATEGY.md](PDF_STRATEGY.md) for the complete workflow with decision rules.

---

## Dependencies

MCP server `datasheet_mcp.py` requires: (Windows: use `python` instead of `python3`)

```bash
pip install -r scripts/requirements.txt
```

| Package | Role | Required? |
|---------|------|-----------|
| `pymupdf` | Primary PDF engine: text, tables, page rendering, CID font handling | **Yes** |
| `pdfplumber` | Fallback for edge cases | **Yes** |
| `pypdfium2` | Page rendering fallback (`render_page`) | **Yes** |

### Why pymupdf?

pymupdf (MuPDF) is the primary engine because it:
- **Handles CID-encoded fonts** — some datasheets use custom font encodings that pdfplumber cannot decode
- **Faster performance** — MuPDF engine is highly optimized
- **Unified API** — text, tables, and rendering in one package
- **Better coverage** — tested on 101 datasheets with 100% text extraction success

---

## Tools

| Command | Purpose |
|---------|---------|
| `info` | Page count, text vs image detection |
| `page_hints [page] [--patterns json]` | Per-page structural signals + heuristic section labels |
| `page_stats [page]` | Raw metrics: char/word/image/rect/line/curve/table counts |
| `dump_patterns` | Print default patterns JSON (base for `--patterns` customization) |
| `text <page>` | Extract text from a page |
| `search <keyword>` | Find keyword across all pages with context |
| `search_caption [keyword]` | Find Figure/Table captions (en + zh) |
| `nearby_text <page> <regex>` | Regex match with surrounding context lines |
| `tables <page>` | Extract all tables from a page |
| `search_table <keyword>` | Find table rows containing keyword |
| `toc` | Extract table of contents (when available) |
| `render_page <page> [dpi] [out]` | Render page to PNG (pymupdf → pypdfium2 fallback) |

### `--patterns` Usage

`page_hints --patterns` accepts a custom JSON that **replaces** the default pattern set. Use it for a targeted second-pass scan after device identification:

1. `dump_patterns > /tmp/p.json` — get defaults as base
2. Add device-specific labels using proprietary terms from the Features list (e.g., `"VINDPM"`, `"clock tree"`, `"DMA controller"`)
3. Re-run `page_hints --patterns /tmp/p.json` to locate domain-specific sections

Patterns should be **section heading phrases or proprietary feature names**, not generic words. Good: `"charge state machine"`. Bad: `"charge"`.

---

## Known Limitations

### CID-Encoded Fonts
Some datasheets use CID (Character ID) font encoding where characters map to numeric IDs instead of Unicode. pymupdf handles these automatically, but very old or non-standard encodings may still produce partial garbage. Check `info` output for `cid_ratio` warning.

### Image-based PDFs
When `is_text_based: false`, text extraction fails entirely. Use `render_page` to render pages as PNG and read visually. **Cross-validate mandatory**: manufacturer + part number from rendered image must match context. If mismatch → output `UNABLE TO VERIFY`. All image-PDF extractions default to `LOW` confidence.

### Complex Table Structures
Merged cells, multi-row headers, and rotated text may mis-extract. Fallback: use `text` to get page text, or `render_page` to read visually. Note: "Extracted from page text / rendered image".

### Graph Data
Numerical values from characteristic curves cannot be extracted precisely. Look for an accompanying data table. If absent: note "Approximate — read from curve".

### Multi-Variant Datasheets
Datasheets covering a product family (e.g., STM32F103C**x**T6) may have variant-specific tables. Always confirm which variant's column applies.

### `page_hints` False Positives
Hints are heuristic. Generic words like `"sequence"` or `"efficiency"` can fire on many pages. Use `score` + `reasons` together — a single low-confidence hit is not reliable. Cross-confirm with `search_caption` or `search`.

---

## What This Skill Cannot Do

| Task | Reason |
|------|--------|
| Guarantee 100% accuracy | LLM extraction has inherent limits |
| Decrypt password-protected PDFs | Not supported |
| Extract 3D models / CAD data | Text and tables only |
| Analyze circuit behavior | Extracts component values, does not simulate |
| Read non-text vector graphics | Render page and read visually |

---

## File Reference

| File | Purpose |
|------|---------|
| `SKILL.md` | Skill trigger rules, iron law, quick reference |
| `PDF_STRATEGY.md` | Full 6-phase workflow with decision trees and device-type shortcuts |
| `TEMPLATES.md` | JSON extraction templates (device info, power domains, I2C, electrical specs) |
| `mcp__ds__*` | MCP tools — see SKILL.md for full reference |
