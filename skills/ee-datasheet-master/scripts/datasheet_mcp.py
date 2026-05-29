#!/usr/bin/env python3
"""MCP server for ee-datasheet-master — exposes PDF tools via FastMCP.

Tools: mcp__ds__search, mcp__ds__info, mcp__ds__text, mcp__ds__tables, etc.
Server name in mcp.json should be "ds".
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
    _IMPORT_ERRORS.append("fastmcp not installed. Run: pip install fastmcp")

try:
    from pdf_tools import (
        pdf_info,
        search_text,
        extract_page_tables,
        extract_page_text,
        search_in_tables,
        extract_toc,
        collect_page_stats,
        collect_page_hints,
        search_captions,
        extract_nearby_text,
        render_page,
        dump_default_patterns,
    )
except ImportError as e:
    _IMPORT_ERRORS.append(
        f"Missing pdf_tools module or its dependencies: {e}. "
        "Run: pip install -r scripts/requirements.txt"
    )

mcp = FastMCP("ee-datasheet-master") if not _IMPORT_ERRORS else None


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
    """Decorator: catch exceptions, check return values for error dicts, serialize to JSON.
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
        except FileNotFoundError as e:
            return _err("missing_file", str(e),
                        "Verify the PDF file path is correct and the file exists.")
        except (ValueError, TypeError) as e:
            msg = str(e)
            if "not a valid PDF" in msg.lower() or "cannot open" in msg.lower():
                return _err("invalid_file", msg,
                            "The file may be corrupted or not a valid PDF. "
                            "Try re-downloading or opening with a PDF viewer first.")
            return _err("invalid_input", msg,
                        "Check the tool parameters. The PDF may require different arguments.")
        except LookupError as e:
            return _err("not_found", str(e),
                        "The requested content was not found in this PDF.")

        # Check for error dicts returned by pdf_tools functions
        if isinstance(result, dict) and "error" in result:
            return _err("invalid_input", str(result["error"]),
                        "Verify the PDF file path is correct and the file is a valid PDF.")

        return _json_result(result)

    return wrapper


def _json_result(payload) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=False, default=str)


# ── Tools ──────────────────────────────────────────────────────────────


@mcp.tool
@_safe
def info(pdf: str) -> str:
    """Get PDF metadata: page count, title, author, file size, encryption status."""
    return pdf_info(pdf)


@mcp.tool
@_safe
def search(pdf: str, keyword: str, context_lines: int = 2) -> str:
    """Full-text search for a keyword across the entire PDF.
    Returns matching passages with surrounding context.
    """
    return search_text(pdf, keyword, context_lines)


@mcp.tool
@_safe
def text(pdf: str, page: int) -> str:
    """Extract plain text from a specific PDF page (1-based)."""
    return extract_page_text(pdf, page)


@mcp.tool
@_safe
def tables(pdf: str, page: int) -> str:
    """Extract all tables from a specific PDF page (1-based)."""
    return extract_page_tables(pdf, page)


@mcp.tool
@_safe
def search_table(pdf: str, keyword: str) -> str:
    """Search for a keyword across all tables in the PDF.
    Returns matching table rows with context.
    """
    return search_in_tables(pdf, keyword)


@mcp.tool
@_safe
def toc(pdf: str) -> str:
    """Extract the table of contents / outline from the PDF."""
    return extract_toc(pdf)


@mcp.tool
@_safe
def page_hints(pdf: str, page: int | None = None) -> str:
    """Scan pages for content hints: register maps, pinout tables, electrical specs.
    If page is None, scans all pages (may be slow on large PDFs).
    """
    return collect_page_hints(pdf, page_num=page)


@mcp.tool
@_safe
def page_stats(pdf: str, page: int | None = None) -> str:
    """Get statistics for a page or all pages: text density, table count, image count."""
    return collect_page_stats(pdf, page_num=page)


@mcp.tool
@_safe
def search_caption(pdf: str, keyword: str | None = None) -> str:
    """Search figure and table captions. If keyword is omitted, returns all captions."""
    return search_captions(pdf, keyword)


@mcp.tool
@_safe
def nearby(pdf: str, page: int, pattern: str, context_lines: int = 2) -> str:
    """Extract text near a pattern match on a given page."""
    return extract_nearby_text(pdf, page, pattern, context_lines)


@mcp.tool
@_safe
def render(pdf: str, page: int, dpi: int = 180, out: str | None = None) -> str:
    """Render a PDF page to a PNG image. Set out to control the filename."""
    return render_page(pdf, page, dpi, out_path=out)


@mcp.tool
@_safe
def patterns() -> str:
    """Dump the built-in search patterns as JSON."""
    return dump_default_patterns()


if __name__ == "__main__":
    if _IMPORT_ERRORS:
        for err in _IMPORT_ERRORS:
            print(err, file=sys.stderr)
        sys.exit(1)
    mcp.run()
