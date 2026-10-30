"""Read-only knowledge commands; never connects to a target."""
import argparse
import json
import sys
from pathlib import Path
from . import applicability as engine
from .catalog import load, info
from .search import search
from .pins import lookup


def main(root, argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('info', help='Compact version, provenance and validation scope')
    for name in ('search', 'match', 'explain', 'pins'):
        cmd = sub.add_parser(name)
        cmd.add_argument('--facts', help='Current task-facts JSON; - reads stdin')
        if name == 'search':
            cmd.add_argument('query')
            cmd.add_argument('--limit', type=int, choices=range(1, 21), default=5)
        elif name == 'explain':
            cmd.add_argument('--ref', required=True)
        elif name == 'pins':
            cmd.add_argument('--board', required=True, help='Exact stable board ID')
            cmd.add_argument('--revision', required=True)
            cmd.add_argument('--connector', required=True)
            cmd.add_argument('--pins', nargs='+', type=int, required=True, help='Physical connector positions')
        else:
            cmd.add_argument('--kind', action='append')
    args = parser.parse_args(argv)
    try:
        if args.command == 'info':
            print(json.dumps(info(root), ensure_ascii=False, indent=2))
            return 0
        catalog = load(root)
        facts = (json.load(sys.stdin) if args.facts == '-' else
                 json.loads(Path(args.facts).read_text())) if args.facts else None
        if args.command == 'search':
            result = search(catalog, args.query, args.limit, facts, engine)
        elif args.command == 'pins':
            result = lookup(catalog, args.board, args.revision, args.connector, args.pins, facts)
        else:
            if args.command == 'match' and facts is None:
                raise ValueError('match requires --facts; missing facts must not be invented')
            result = engine.match(catalog, facts or {'schema_version': '1'}, getattr(args, 'kind', None))
            if args.command == 'explain':
                entries = {e['id']: e for e in catalog['entries']}
                if args.ref not in entries:
                    raise ValueError('Unknown reference ID: ' + args.ref)
                states = {e['id']: e for key in ('matches', 'unknown', 'no_match', 'excluded') for e in result[key]}
                closure, seen = [], set()
                def collect(id):
                    if id in seen:
                        return
                    seen.add(id)
                    entry = entries[id]
                    closure.append({'reference_id': id, 'path': entry['path'],
                                    'assessment': states.get(id, {'status': 'evidence_only'})})
                    for child in engine.references(entry)[0]:
                        collect(child)
                collect(args.ref)
                result = {'knowledge_release': catalog['knowledge_release'], 'references': closure,
                          'limits': result['limits']}
        reference_root = root / ('references' if (root / 'references').is_dir() else 'knowledge/references')
        paths = {e['id']: e['path'] for e in catalog['entries']}
        def readable_paths(node):
            if isinstance(node, dict):
                id = node.get('reference_id', node.get('id'))
                if isinstance(id, str) and id in paths and node.get('path') == paths[id]:
                    node['read_path'] = str((reference_root / paths[id]).resolve())
                for value in list(node.values()):
                    readable_paths(value)
            elif isinstance(node, list):
                for value in node:
                    readable_paths(value)
        readable_paths(result)
        result['reference_root'] = str(reference_root.resolve())
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({'error': str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2
