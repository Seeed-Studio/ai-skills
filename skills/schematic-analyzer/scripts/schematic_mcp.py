#!/usr/bin/env python3
"""MCP server for schematic-analyzer — exposes CLI tools via FastMCP.

Configure in .claude/mcp.json:

    {
      "mcpServers": {
        "sch": {
          "command": "python3",
          "args": ["/path/to/schematic_mcp.py"]
        }
      }
    }

Tools: mcp__sch__overview, mcp__sch__comp, mcp__sch__net, mcp__sch__page, etc.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from fastmcp import FastMCP
from analyzer import SchematicAnalyzer
from cli_support import find_schematic

mcp = FastMCP("schematic-analyzer")


def _get_analyzer(project: str) -> SchematicAnalyzer:
    schematic_path = find_schematic(project)
    return SchematicAnalyzer(str(schematic_path))


def _json_result(payload: dict) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=False, default=str)


# ── Tools ──────────────────────────────────────────────────────────────


@mcp.tool
def overview(project: str) -> str:
    """Get structural project overview: page count, component count, net count,
    page navigation table, and core component candidates ranked by connectivity.
    Use this first for architecture analysis or design review.
    """
    return _json_result(_get_analyzer(project).build_overview())


@mcp.tool
def page(project: str, index: int) -> str:
    """Query all components and nets on a schematic page by its 1-based index.
    Use page indices from the overview output.
    """
    return _json_result(_get_analyzer(project).query_page(index))


@mcp.tool
def comp(project: str, ref: str, full: bool = False) -> str:
    """Query a component by reference designator (e.g. 'U1', 'R5', 'C3').
    Returns value, MPN, pins with net names, properties, and neighbors (shared nets).
    Set full=True to include unconnected pins.
    """
    return _json_result(_get_analyzer(project).query_component(ref, include_full=full))


@mcp.tool
def net(project: str, name: str) -> str:
    """Query a net by exact name (e.g. 'VCC_LED', 'N17210693').
    Returns all connected pins with reference, pin name, and page.
    """
    return _json_result(_get_analyzer(project).query_net(name))


@mcp.tool
def comp_search(project: str, text: str) -> str:
    """Search components whose value, MPN, or reference contains the given text.
    Returns matching components with summary info.
    """
    return _json_result(_get_analyzer(project).query_component_match(text))


@mcp.tool
def net_search(project: str, text: str) -> str:
    """Search nets whose name matches the given text (supports regex).
    Returns matching net names with page and pin counts.
    """
    return _json_result(_get_analyzer(project).query_net_match(text))


@mcp.tool
def prop(project: str, key: str) -> str:
    """Query all property values for a given property key across all components.
    Returns grouped values with MPNs and reference lists.
    """
    return _json_result(_get_analyzer(project).query_property(key))


@mcp.tool
def pattern(project: str, file: str) -> str:
    """Run a custom pattern query from a YAML file.
    The pattern file defines signals, roles, and detection rules.
    """
    analyzer = SchematicAnalyzer(str(find_schematic(project)), pattern_sources=[file])
    return _json_result(analyzer.query_pattern([file]))


if __name__ == "__main__":
    mcp.run()
