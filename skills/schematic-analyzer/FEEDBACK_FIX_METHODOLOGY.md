# Feedback Fix Methodology for Schematic Analyzer

## Scope

This document defines the workflow for fixing bugs, addressing feedback, and optimizing
the schematic-analyzer codebase. It applies when:
- Processing problem reports from `problem_feedback/*.md`
- Fixing bugs discovered during testing or analysis
- Optimizing code for reliability without changing behavior

**Invariant**: No fix shall degrade functionality, accuracy, or reliability.

---

## Seven-Step Workflow

```
Step 1  Read Feedback       Read problem_feedback/*.md independently, do not rely on user summaries.
Step 2  Locate Code         Use Grep/Glob to pinpoint exact functions/lines. Read surrounding context.
Step 3  Consider Thoroughly Edge cases, case sensitivity, data formats, cross-file impact, backward compat.
Step 4  Minimal Change      Only fix what's necessary. No refactoring, no "while we're here" improvements.
Step 5  Self-Review         Read the complete modified function. Verify logic correctness, no side effects.
Step 6  Iterate             If issues found in review, repeat Steps 3-5 until confident.
Step 7  Real-Sample Test    Test against all 4 Cadence samples, choosing complex scenarios first.
```

### Step 1: Read Feedback

- Read `problem_feedback/*.md` files directly
- Extract the specific issue, expected behavior, and actual behavior
- Do NOT ask the user to re-explain what's already written in feedback
- If feedback is ambiguous, re-read the related code to understand context before asking

### Step 2: Locate Code

- Use `Grep` to find the exact function/class causing the issue
- Use `Glob` to find all files that might be affected
- Read the complete function, not just the line that seems wrong
- Trace the call chain: who calls this function? What does it call?

### Step 3: Consider Thoroughly

Before writing any code change, consider:

| Aspect | What to check |
|--------|--------------|
| Boundary conditions | Empty input, None, zero-length strings, very large values |
| Case sensitivity | `.upper()` / `.lower()` consistency across callers |
| Data format | Does the fix handle both XML and DAT parsing modes? |
| Cross-file impact | Does changing a constant/function signature break other files? |
| Backward compatibility | Will existing cached data or saved results still work? |
| Error paths | Does the fix handle exceptions gracefully? |
| DNP components | Does the fix preserve DNP filtering behavior? |

### Step 4: Minimal Change

Rules for the modification itself:

1. **One fix = one logical change**. Do not bundle unrelated improvements.
2. **Safe input -> identical behavior**. The fix must not change output for valid inputs.
3. **Unsafe input -> graceful degradation**. Return sensible defaults, never crash.
4. **Dead code -> delete, don't comment**. No `# removed` comments.
5. **No speculative additions**. Don't add error handling for impossible states.
6. **No cosmetic changes**. Don't reformat, rename, or restructure surrounding code.

### Step 5: Self-Review

After making changes:

1. Read the **complete modified function** (not just the diff)
2. Verify: does the logic still work for the normal case?
3. Verify: does the logic handle the error case that was reported?
4. Verify: are there any new side effects?
5. Check: did the change accidentally affect imports or constants used elsewhere?

### Step 6: Iterate

If self-review reveals issues:
- Do not proceed to testing with known problems
- Go back to Step 3, reconsider the approach
- Each iteration should make the fix smaller and more targeted, not larger

### Step 7: Real-Sample Test

Test against all 4 Cadence samples. Prioritize complex scenarios.

**Test samples** (relative to project root):
```
Cadence_data/BeagleBone Green Eco_V1.0_XML_BOM_netlist/    # 478 components
Cadence_data/GMSL board for reComputer Robotics_V1.0_netlist_BOM_xml/  # 224 components
Cadence_data/SICK SEC200 ETHERNET_V2.2/                     # 387 components
Cadence_data/src/PAMIRAI DENALI V01 20260331_BOM_XML_netlist/  # 1102 components
```

**Test sequence**:
1. Run `overview` on each sample — verify no crashes
2. Query 2-3 components per sample (mix of ICs, passives, connectors)
3. Query common nets (GND, VCC, power rails)
4. If the fix relates to DNP: verify DNP components are correctly filtered
5. If the fix relates to connectivity: verify pin-net accuracy against DAT source

**Complex test examples to prefer**:
- PAMIRAI (1102 components) — largest sample, stress test
- Components with many pins (SoCs, FPGAs)
- Multi-page hierarchical nets
- Components with mux pin names (FUNC1 | FUNC2 | GPIO)

---

## Common Fix Patterns

| Pattern | Detection | Fix Strategy |
|---------|-----------|-------------|
| Type conversion crash | `int()` without guard | `_safe_int()` or `try/except` with default |
| Regex over-constraint | Missing optional group | Add `(?:\s+...)? ` |
| Dead code/branch | `elif` with same condition as `if` | Merge into the `if` block or delete |
| Non-deterministic hash | `hash() % N` | `hashlib.md5(...encode())[:N]` |
| Hardcoded magic value | Bare number or string | Extract to `constants.py` |
| Exception leak | No top-level handler | `try/except` + user-friendly message |
| Case inconsistency | `.add(ref)` vs `.add(ref.upper())` | Normalize consistently |
| Temp resource leak | Exception path no cleanup | `try/finally` or unlink on error |
| Missing default | `dict.get(key)` without default | `dict.get(key, default)` |
| Bare except | `except:` | `except Exception:` |

---

## Regression Checklist

After any fix, verify ALL of the following before reporting completion:

- [ ] All 4 samples produce valid `overview` output (no crashes)
- [ ] Random component queries return correct pin-net data
- [ ] GND/VCC net queries return connected pins
- [ ] DNP components correctly identified and filtered from core candidates
- [ ] No Python exceptions or tracebacks in any command
- [ ] No new warnings introduced (check stderr)
- [ ] If constants changed: verify both KiCad and Cadence code paths

---

## Anti-Patterns

### Don't: Fix and Refactor

```
BAD:  Fix the int() crash AND restructure the function AND add type hints
GOOD: Fix the int() crash only
```

### Don't: Assume Single Cause

```
BAD:  "The query returns empty — must be a parsing bug"
GOOD: Trace the full path: CLI -> analyzer -> connectivity -> parser, find where data is lost
```

### Don't: Test Only the Fixed Case

```
BAD:  Only test the specific scenario from the feedback
GOOD: Test the fixed case AND all 4 samples to catch regressions
```

### Don't: Skip Self-Review

```
BAD:  Make the change, immediately run tests
GOOD: Read the full modified function, then test
```

---

## Architecture Reference

```
scripts/
  schematic-cli.py          # CLI entry point (argparse)
  cli_commands.py           # Command handlers (overview, query, cache)
  analyzer.py               # Core 3-phase analysis engine
  tools/
    connectivity_builder.py # Unified connectivity graph builder
    project_indexer.py      # Project scope + component indexing
    core_ranker.py          # Core candidate ranking (with DNP filter)
    constants.py            # Shared constants
    cadence/
      xml_parser.py         # OrCAD XML parsing + coordinate matching
      netlist_dat_parser.py # Allegro netlist (pstxnet/pstxprt) parsing
      connectivity.py       # Cadence-specific connectivity builder
    kicad/
      schematic_parser.py   # KiCad .kicad_sch parsing
      netlist_parser.py     # KiCad netlist XML parsing
      pcb_parser_kicad.py   # KiCad PCB parsing
```
