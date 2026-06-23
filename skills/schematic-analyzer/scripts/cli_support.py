"""Shared helpers for the light-refactor schematic analyzer CLI."""

from __future__ import annotations

import json
from pathlib import Path

from analyzer import SchematicAnalyzer
from tools.scope_resolver import ScopeResolver


def find_schematic(path: str) -> Path:
    """Find the root schematic for a file, project, or directory input."""
    return ScopeResolver.find_schematic(path)


def build_analyzer(schematic_path: Path, args) -> SchematicAnalyzer:
    """Build the analyzer for the new overview/query/cache command surface."""
    pattern_sources = []
    pattern = getattr(args, "pattern", None)
    if pattern:
        pattern_sources = [pattern]
    return SchematicAnalyzer(str(schematic_path), pattern_sources=pattern_sources)


def write_json_output(payload: dict, output: str | None) -> None:
    """Emit JSON payload to stdout or file."""
    content = json.dumps(payload, indent=2, ensure_ascii=False)
    if output:
        Path(output).write_text(content, encoding="utf-8")
        return
    print(content)


def print_overview_summary(payload: dict) -> None:
    """Render the human-readable overview contract."""
    project = payload["project_overview"]
    print("Project Overview")
    print(f"Project Pages: {project['project_page_count']}")
    print(f"Project Components: {project['project_component_count']}")
    dnp = project.get("project_dnp_count")
    if dnp:
        print(f"Project DNP (filtered): {dnp}")
    print(f"Project Nets: {project['project_net_count']}")
    print(f"Root Schematic: {project['root_schematic_filename']}")
    print(f"Referenced Pages: {project['referenced_page_count']}")
    print("")
    print("Page Navigation")
    for page in payload["page_navigation"]:
        print(
            f"{page['page_index']}. {page['page_name']} "
            f"[{page['page_type']}] {page['page_source_file']} "
            f"symbols={page['symbol_count']}"
        )
    print("")
    print("Core Component Candidates")
    for candidate in payload["core_component_candidates"]:
        print(
            f"{candidate['candidate_index']}. {candidate['reference']} {candidate['value']} "
            f"page={candidate['page_index']}({candidate['page_name']}) "
            f"nets={candidate['connected_net_count']} "
            f"neighbors={candidate['neighboring_symbol_count']}"
        )
