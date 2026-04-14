"""Argument parser construction for the schematic analyzer CLI."""

from __future__ import annotations

import argparse

from cli_commands import cmd_cache, cmd_overview, cmd_query


def build_parser() -> argparse.ArgumentParser:
    """Build the top-level CLI parser."""
    parser = argparse.ArgumentParser(
        description="KiCad Schematic Analyzer CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command")

    overview_parser = subparsers.add_parser("overview", help="Project first-look overview")
    overview_parser.add_argument("schematic", help="Schematic file, project file, or project directory")
    overview_parser.add_argument("--output", "-o", help="Optional JSON output path")
    overview_parser.set_defaults(func=cmd_overview)

    query_parser = subparsers.add_parser("query", help="Inspect pages, components, nets, properties, or patterns")
    query_parser.add_argument("schematic", help="Schematic file, project file, or project directory")
    query_group = query_parser.add_mutually_exclusive_group(required=True)
    query_group.add_argument("--page", type=int, help="Page index from overview")
    query_group.add_argument("--component", nargs="?", const="", help="Component reference or selector for --match")
    query_group.add_argument("--net", nargs="?", const="", help="Net name or selector for --match")
    query_group.add_argument("--property", help="Property key such as MPN or Footprint")
    query_group.add_argument("--pattern", help="Pattern YAML file")
    query_parser.add_argument("--match", help="Search text for component or net query mode")
    query_parser.add_argument("--all", action="store_true", help="Reserved full-result mode")
    query_parser.add_argument("--full", action="store_true", help="Return full component pin-net details")
    query_parser.add_argument("--output", "-o", help="Write JSON result to file")
    query_parser.set_defaults(func=cmd_query)

    cache_parser = subparsers.add_parser("cache", help="Cache maintenance")
    cache_parser.add_argument("schematic", help="Schematic file, project file, or project directory")
    cache_parser.add_argument("--clear", action="store_true", help="Clear cache for the project")
    cache_parser.set_defaults(func=cmd_cache)

    return parser
