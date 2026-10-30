# Maintenance

Edit only maintained sources: `skills/armbian-hardware/SKILL*.md`, its `agents/`, `workflows/`, `knowledge/references/`, `src/armbian_skills/`, `probes/`, `templates/`, `schemas/` and tests. Knowledge keeps stable IDs, applicability, exclusions, required dependencies and provenance. English/Chinese reference metadata must match. Generated package paths under the skill are ignored by Git and must not be edited.

```bash
python3 scripts/render_wiring_examples.py --check
python3 scripts/refresh_catalog.py
# Review knowledge, workflow, helper and version changes before freezing:
python3 scripts/build_skills.py --update-lock
python3 scripts/build_skills.py --check
python3 -m unittest discover -s tests -v
```

The lock covers the complete runtime payload. Update `release/version.json` intentionally; refresh the index when its knowledge release changes. Installation packages are generated before tests/installation in a source checkout. Release archives have deterministic ordering and timestamps. `source_commit` plus `source_dirty` distinguish development builds; file hashes identify exact bytes. Publish from a clean committed checkout and rebuild so the manifest identifies that commit. Do not claim unpublished changes were released.

Add boards via identity/electrical/revision knowledge, stacks via detection/integration/verification references and tests. Do not add board-name branches to core tooling. Search aliases are in `src/armbian_skills/search.py`; use regression queries and strict applicability tests. Read-only probe changes require boundary and timeout tests.

Project facts, raw board records, credentials, SDKs, models and generated application outputs never enter the runtime payload. Agent behavior evaluation cases will be designed separately; evals/ changes are excluded from this refactor. Core tests do not depend on that directory. Future evaluations must isolate scoring assertions and future-turn inputs from execution, and keep raw runs outside the runtime payload.

The index generator derives pin_data from canonical YAML, including selected pin records and document-wide electrical/operation constraints. Do not maintain a second pin map in code or manually edit generated catalog pin_data. Extend the canonical fields and CONTEXT_FIELDS together when adding constraints. Verify compact info, exact profile lookup, shared nets, missing/ambiguous identity, and installed standard-library-only execution after changes.
