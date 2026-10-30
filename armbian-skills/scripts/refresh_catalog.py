#!/usr/bin/env python3
"""Regenerate/check the reference inventory, typed dependencies and digests.

Requires Python 3 and PyYAML on the development host. The generated JSON index
and matcher need only Python's standard library on installed hosts.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from armbian_skills.applicability import validate_catalog
from armbian_skills.pins import CONTEXT_FIELDS

ROOT = Path(__file__).resolve().parents[1] / "knowledge/references"
FIELDS = ["schema_version", "id", "kind", "applies_to", "required_refs", "preconditions",
          "refines", "excludes", "related", "sources", "validation_refs", "maturity", "owner", "updated_at",
          "identity_rules", "runtime_constraints", "platform_ref", "revision_profiles", "candidate_stack_refs",
          "detection_ref", "integration_ref", "verification_ref", "official_pinout_ref", "cases", "overlays"]


def metadata(path):
    text = path.read_text()
    if path.suffix == ".md":
        match = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
        if not match:
            raise ValueError(f"Missing YAML front matter: {path}")
        return yaml.safe_load(match.group(1))
    return yaml.safe_load(text)


def digest(path):
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def build():
    records, metas = [], {}
    all_paths = sorted(p for p in ROOT.rglob("*") if p.is_file() and p.suffix in {".yaml", ".md"} and p.name != "catalog.yaml")
    # Translations share canonical IDs and conditions; do not create duplicate matches.
    paths = [p for p in all_paths if not p.name.endswith(".zh-CN.md")]
    for path in all_paths:
        if path.suffix != ".md":
            continue
        if path.name.endswith(".zh-CN.md"):
            canonical = path.with_name(path.name.replace(".zh-CN.md", ".md"))
            if not canonical.is_file() or metadata(path) != metadata(canonical):
                raise ValueError(f"Translation metadata differs from canonical reference: {path}")
        elif not path.with_name(path.stem + ".zh-CN.md").is_file():
            raise ValueError(f"Missing Chinese reference translation: {path}")
    for path in paths:
        data = metadata(path)
        if not isinstance(data, dict) or not isinstance(data.get("id"), str):
            raise ValueError(f"Invalid reference metadata: {path}")
        if data["id"] in metas:
            raise ValueError(f"Duplicate ID: {data['id']}")
        metas[data["id"]] = data
        records.append({**{key: data[key] for key in FIELDS if key in data},
                        "summary": (re.search(r"^# (.+)$", path.read_text(), re.M).group(1) if path.suffix == ".md" and re.search(r"^# (.+)$", path.read_text(), re.M) else data["id"]),
                        "path": str(path.relative_to(ROOT)), "content_digest": digest(path)})
        if isinstance(data.get("pins"), list):
            # Derived from the same canonical YAML; no separately maintained pin map.
            records[-1]["pin_data"] = {k: data[k] for k in (*CONTEXT_FIELDS, "pins", "shared_net_groups") if k in data}
        if data["kind"] == "source_registry":
            for source in data["source_entries"]:
                if source["id"] in metas:
                    raise ValueError(f"Duplicate source: {source['id']}")
                metas[source["id"]] = source
                records.append({"id": source["id"], "kind": "source", "path": str(path.relative_to(ROOT)),
                                "entry_id": source["id"], "content_digest": digest(path)})

    graph = {}
    for id, data in metas.items():
        hard = list(data.get("required_refs", [])) + [item["target_ref"] for item in data.get("refines", [])]
        # Board->platform is required. Board revision lists and candidate stacks
        # are navigation: interfaces depend on board identity, not vice versa.
        if "platform_ref" in data:
            hard.append(data["platform_ref"])
        revision_nav = [item["interface_ref"] for item in data.get("revision_profiles", [])]
        refs = hard + revision_nav + list(data.get("candidate_stack_refs", [])) + list(data.get("related", [])) + list(data.get("sources", [])) + list(data.get("validation_refs", []))
        refs.extend(data[key] for key in ["detection_ref", "integration_ref", "verification_ref"] if key in data)
        refs.extend(case["report_ref"] for case in data.get("cases", []) if "report_ref" in case)
        refs.extend(item["source_ref"] for item in data.get("overlays", []))
        for ref in refs:
            if not isinstance(ref, str) or ref not in metas:
                raise ValueError(f"Missing/invalid reference in {id}: {ref}")
        for key in ["preconditions", "excludes", "refines"]:
            if not isinstance(data.get(key, []), list):
                raise ValueError(f"Invalid {key} in {id}")
        graph[id] = hard

    done, active = set(), set()
    def visit(id):
        if id in active:
            raise ValueError(f"Required dependency/refinement cycle: {id}")
        if id in done:
            return
        active.add(id)
        for child in graph[id]:
            visit(child)
        active.remove(id)
        done.add(id)
    for id in graph:
        visit(id)

    for path in all_paths:
        if path.suffix != ".md":
            continue
        text = path.read_text()
        if sum(line.startswith("```") for line in text.splitlines()) % 2:
            raise ValueError(f"Unbalanced code fences: {path}")
        for link in re.findall(r"\]\(([^)]+)\)", text):
            if re.match(r"^[a-z]+://", link) or link.startswith("#"):
                continue
            target = (path.parent / link.split("#", 1)[0]).resolve()
            if not target.is_relative_to(ROOT.resolve()) or not target.exists():
                raise ValueError(f"Broken/outside local link: {path}: {link}")

    result = {"schema_version": "1", "knowledge_release": json.loads((ROOT.parents[1] / "release/version.json").read_text())["knowledge_release"],
              "scope": "static hardware/software references; no validation history or current target state",
              "entries": sorted(records, key=lambda item: item["id"])}
    validate_catalog(result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate and check without rewriting the catalog")
    args = parser.parse_args()
    result = build()
    path = ROOT / "catalog.yaml"
    json_path = ROOT / "catalog.json"
    if args.check:
        if not path.exists() or yaml.safe_load(path.read_text()) != result:
            raise ValueError("Catalog is stale; regenerate with refresh_catalog.py")
        if not json_path.exists() or json.loads(json_path.read_text()) != result:
            raise ValueError("JSON catalog is stale; regenerate with refresh_catalog.py")
    else:
        path.write_text(yaml.safe_dump(result, allow_unicode=True, sort_keys=False, width=110))
        json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(f"OK: {len(result['entries'])} indexed references/sources, typed links, dependency graph and digests")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, TypeError, yaml.YAMLError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
