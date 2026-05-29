#!/usr/bin/env python3
"""MCP server for ee-datasheet-master — exposes PDF tools via FastMCP.

Tools: mcp__ds__search, mcp__ds__info, mcp__ds__text, mcp__ds__tables, etc.
Server name in mcp.json should be "ds".
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from fastmcp import FastMCP
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

mcp = FastMCP("ee-datasheet-master")


def _json_result(payload) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=False, default=str)


@mcp.tool
def info(pdf: str) -> str:
    """Get PDF metadata: page count, title, author, file size, encryption status."""
    return _json_result(pdf_info(pdf))


@mcp.tool
def search(pdf: str, keyword: str, context_lines: int = 2) -> str:
    """Full-text search for a keyword across the entire PDF.
    Returns matching passages with surrounding context.
    """
    return _json_result(search_text(pdf, keyword, context_lines))


@mcp.tool
def text(pdf: str, page: int) -> str:
    """Extract plain text from a specific PDF page (1-based)."""
    return _json_result(extract_page_text(pdf, page))


@mcp.tool
def tables(pdf: str, page: int) -> str:
    """Extract all tables from a specific PDF page (1-based)."""
    return _json_result(extract_page_tables(pdf, page))


@mcp.tool
def search_table(pdf: str, keyword: str) -> str:
    """Search for a keyword across all tables in the PDF.
    Returns matching table rows with context.
    """
    return _json_result(search_in_tables(pdf, keyword))


@mcp.tool
def toc(pdf: str) -> str:
    """Extract the table of contents / outline from the PDF."""
    return _json_result(extract_toc(pdf))


@mcp.tool
def page_hints(pdf: str, page: int | None = None) -> str:
    """Scan pages for content hints: register maps, pinout tables, electrical specs.
    If page is None, scans all pages (may be slow on large PDFs).
    """
    return _json_result(collect_page_hints(pdf, page_num=page))


@mcp.tool
def page_stats(pdf: str, page: int | None = None) -> str:
    """Get statistics for a page or all pages: text density, table count, image count."""
    return _json_result(collect_page_stats(pdf, page_num=page))


@mcp.tool
def search_caption(pdf: str, keyword: str | None = None) -> str:
    """Search figure and table captions. If keyword is omitted, returns all captions."""
    return _json_result(search_captions(pdf, keyword))


@mcp.tool
def nearby(pdf: str, page: int, pattern: str, context_lines: int = 2) -> str:
    """Extract text near a pattern match on a given page.
    Useful for finding pin functions around a pin name, or register descriptions around an address.
    """
    return _json_result(extract_nearby_text(pdf, page, pattern, context_lines))


@mcp.tool
def render(pdf: str, page: int, dpi: int = 180, out: str | None = None) -> str:
    """Render a PDF page to a PNG image.
    Returns the output path. Set out to control the filename.
    """
    return _json_result(render_page(pdf, page, dpi, out_path=out))


@mcp.tool
def patterns() -> str:
    """Dump the built-in search patterns (register maps, pinout tables, etc.) as JSON."""
    return _json_result(dump_default_patterns())


if __name__ == "__main__":
    mcp.run()
