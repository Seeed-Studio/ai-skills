"""Command handlers for the light-refactor schematic analyzer CLI."""

from __future__ import annotations

import sys

from cache_manager import CacheManager
from cli_support import build_analyzer, find_schematic, print_overview_summary, write_json_output


def cmd_overview(args):
    """Render the structural overview for one project."""
    try:
        schematic_path = find_schematic(args.schematic)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    analyzer = build_analyzer(schematic_path, args)
    payload = analyzer.build_overview()
    if args.output:
        write_json_output(payload, args.output)
    else:
        print_overview_summary(payload)
    return 0


def cmd_query(args):
    """Render one structured query result."""
    try:
        schematic_path = find_schematic(args.schematic)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    analyzer = build_analyzer(schematic_path, args)
    try:
        if args.page is not None:
            payload = analyzer.query_page(args.page)
        elif args.component is not None:
            if args.match:
                payload = analyzer.query_component_match(args.match, include_all=args.all)
            elif not args.component:
                raise ValueError("--component requires a reference unless used with --match")
            else:
                payload = analyzer.query_component(args.component, include_full=args.full)
        elif args.net is not None:
            if args.match:
                payload = analyzer.query_net_match(args.match, include_all=args.all)
            elif not args.net:
                raise ValueError("--net requires an exact net name")
            else:
                payload = analyzer.query_net(args.net)
        elif args.property is not None:
            payload = analyzer.query_property(args.property, include_all=args.all)
        elif args.pattern is not None:
            payload = analyzer.query_pattern([args.pattern])
        else:
            raise ValueError("No query type selected")
    except (LookupError, ValueError) as exc:
        # Return structured error JSON
        error_msg = str(exc)
        error_payload = {
            "error": "not_found" if "not found" in error_msg.lower() else "validation_error",
            "message": error_msg,
        }
        # Try to extract suggestion for not_found errors
        if "Did you mean" in error_msg:
            error_payload["suggestion"] = error_msg.split("Did you mean '")[1].rstrip("'?")
        write_json_output(error_payload, args.output)
        return 1

    write_json_output(payload, args.output)
    return 0


def cmd_cache(args):
    """Show or clear cache state."""
    try:
        schematic_path = find_schematic(args.schematic)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    cache = CacheManager(str(schematic_path.parent))
    if args.clear:
        cache.clear_cache()
        print(f"Cache cleared for: {schematic_path.parent}")
        return 0

    need_refresh, reason, _cache_key = cache.should_refresh(str(schematic_path))
    print(f"Cache Status: {'STALE' if need_refresh else 'VALID'}")
    print(f"Reason: {reason}")
    return 0
