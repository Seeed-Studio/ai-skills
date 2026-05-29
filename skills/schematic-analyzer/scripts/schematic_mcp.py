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
from functools import wraps
from pathlib import Path
from typing import Callable

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

# ── Dependency checks at import time ────────────────────────────────────

_IMPORT_ERRORS: list[str] = []

try:
    from fastmcp import FastMCP
except ImportError:
    _IMPORT_ERRORS.append(
        "fastmcp not installed. Run: pip install fastmcp"
    )

try:
    from analyzer import SchematicAnalyzer
    from cli_support import find_schematic
except ImportError as e:
    _IMPORT_ERRORS.append(
        f"Missing schematic-analyzer module: {e}. "
        "Run: pip install -r scripts/requirements.txt"
    )

mcp = FastMCP("schematic-analyzer") if not _IMPORT_ERRORS else None


# ── Error helpers ───────────────────────────────────────────────────────

def _err(error_type: str, message: str, fix: str) -> str:
    """Return a structured error that the LLM can relay to the user."""
    return json.dumps({
        "error": True,
        "type": error_type,
        "message": message,
        "fix": fix,
    }, indent=2, ensure_ascii=False)


def _safe(fn: Callable) -> Callable:
    """Decorator: catch exceptions, serialize to JSON.
    Tool functions should return plain dicts; this wrapper handles JSON serialization
    and error normalization.
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        if _IMPORT_ERRORS:
            return _err("missing_dependency", _IMPORT_ERRORS[0],
                        "Install the missing Python package(s) above.")

        try:
            result = fn(*args, **kwargs)
            return _json_result(result)
        except FileNotFoundError as e:
            msg = str(e)
            if "No supported schematic files" in msg:
                return _err(
                    "missing_files",
                    f"No supported schematic files found: {msg.split('in: ')[-1] if 'in: ' in msg else msg}",
                    "Provide a directory with .kicad_sch files, or for Cadence: "
                    "pstxnet.dat + pstxprt.dat + OrCAD Capture XML export together.")
            return _err("missing_files", msg,
                        "Verify the project path exists and contains supported schematic files.")
        except (ValueError, TypeError) as e:
            msg = str(e)
            if "Not a supported schematic file" in msg:
                return _err(
                    "invalid_project",
                    msg,
                    "Provide a KiCad .kicad_sch file, or a Cadence OrCAD Capture XML export "
                    "with accompanying pstxnet.dat and pstxprt.dat files.")
            return _err("invalid_project", msg,
                        "Check that the project path points to a valid schematic file.")
        except LookupError as e:
            return _err("not_found", str(e),
                        "Check the spelling of the component reference or net name.")

    return wrapper


def _json_result(payload) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=False, default=str)


def _get_analyzer(project: str):
    schematic_path = find_schematic(project)
    return SchematicAnalyzer(str(schematic_path))


# ── Tools ──────────────────────────────────────────────────────────────


@mcp.tool
@_safe
def overview(project: str) -> str:
    """Get structural project overview: page count, component count, net count,
    page navigation table, and core component candidates ranked by connectivity.
    Use this first for architecture analysis or design review.
    """
    return _get_analyzer(project).build_overview()


@mcp.tool
@_safe
def page(project: str, index: int) -> str:
    """Query all components and nets on a schematic page by its 1-based index.
    Use page indices from the overview output.
    """
    return _get_analyzer(project).query_page(index)


@mcp.tool
@_safe
def comp(project: str, ref: str, full: bool = False) -> str:
    """Query a component by reference designator (e.g. 'U1', 'R5', 'C3').
    Returns value, MPN, pins with net names, properties, and neighbors (shared nets).
    Set full=True to include unconnected pins.
    """
    return _get_analyzer(project).query_component(ref, include_full=full)


@mcp.tool
@_safe
def net(project: str, name: str) -> str:
    """Query a net by exact name (e.g. 'VCC_LED', 'N17210693').
    Returns all connected pins with reference, pin name, and page.
    """
    return _get_analyzer(project).query_net(name)


@mcp.tool
@_safe
def comp_search(project: str, text: str) -> str:
    """Search components whose value, MPN, or reference contains the given text.
    Returns matching components with summary info.
    """
    return _get_analyzer(project).query_component_match(text)


@mcp.tool
@_safe
def net_search(project: str, text: str) -> str:
    """Search nets whose name matches the given text (supports regex).
    Returns matching net names with page and pin counts.
    """
    return _get_analyzer(project).query_net_match(text)


@mcp.tool
@_safe
def prop(project: str, key: str) -> str:
    """Query all property values for a given property key across all components.
    Returns grouped values with MPNs and reference lists.
    """
    return _get_analyzer(project).query_property(key)


@mcp.tool
@_safe
def pattern(project: str, file: str) -> str:
    """Run a custom pattern query from a YAML file.
    The pattern file defines signals, roles, and detection rules.
    """
    analyzer = SchematicAnalyzer(str(find_schematic(project)), pattern_sources=[file])
    return analyzer.query_pattern([file])


if __name__ == "__main__":
    if _IMPORT_ERRORS:
        for err in _IMPORT_ERRORS:
            print(err, file=sys.stderr)
        sys.exit(1)
    mcp.run()
