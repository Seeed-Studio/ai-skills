# Schematic Analyzer — Project Context

## Architecture

```
scripts/
  schematic-cli.py          # CLI entry point (argparse)
  cli_commands.py           # Command handlers (overview, query, cache)
  analyzer.py               # Core 3-phase analysis engine
  tools/
    connectivity_builder.py # Unified connectivity graph builder
    project_indexer.py      # Project scope + component indexing
    core_ranker.py          # Core candidate ranking (with DNP filter)
    constants.py            # Shared constants (format IDs, net types, thresholds)
    cadence/
      xml_parser.py         # OrCAD XML parsing + coordinate matching
      netlist_dat_parser.py # Allegro netlist (pstxnet/pstxprt) parsing
      connectivity.py       # Cadence-specific connectivity builder
    kicad/
      schematic_parser.py   # KiCad .kicad_sch parsing
      netlist_parser.py     # KiCad netlist XML parsing
      pcb_parser_kicad.py   # KiCad PCB parsing
```

## Dual Parsing Modes (Cadence)

1. **Authoritative**: pstxnet.dat (Allegro netlist) — engine-computed, precise pin-net mapping
2. **Fallback**: XML coordinate matching — when .dat unavailable, less accurate

## DNP Detection

- Property-based: ASSY, DNP, POPULATE, EXCLUDE_FROM_BOM, Status
- Value-based: DNP, NC, NF, DNI, etc.
- DNP components filtered from core candidates but included in queries

## Test Samples

Located in `Cadence_data/`:
- BeagleBone (478 components)
- GMSL (224 components)
- SICK (387 components)
- PAMIRAI (1102 components)

## Fix Methodology

When processing feedback or fixing bugs, follow [FEEDBACK_FIX_METHODOLOGY.md](./FEEDBACK_FIX_METHODOLOGY.md).

Key principles:
- Read feedback files independently (problem_feedback/*.md)
- Consider all edge cases before modifying code
- Minimal changes only — no refactoring or cosmetic improvements
- Self-review before testing, iterate until confident
- Test with all 4 Cadence samples, prefer complex scenarios
