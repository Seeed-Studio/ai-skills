#!/usr/bin/env python3
"""Install the complete Armbian hardware skill for Codex and/or Claude Code (Python3.9+, stdlib only)."""
import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from armbian_skills.catalog import verify_package

SUITE = Path(__file__).resolve().parents[1]
NAMES = ('armbian-hardware',)
AGENTS = {'codex': '.agents', 'claude': '.claude'}
IGNORE = shutil.ignore_patterns('__pycache__', '*.pyc', '*.pyo')


def destinations(agent, scope, project_dir, dest):
    agents = tuple(AGENTS) if agent == 'both' else (agent,)
    if dest:
        if len(agents) != 1 or scope != 'user' or project_dir:
            raise ValueError('--dest requires a single --agent and cannot be combined with project scope')
        return [(agents[0], Path(dest).expanduser().resolve())]
    if project_dir and scope != 'project':
        raise ValueError('--project-dir requires --scope project')
    base = Path(project_dir or Path.cwd()).expanduser() if scope == 'project' else Path.home()
    return [(a, (base / AGENTS[a] / 'skills').resolve()) for a in agents]


def fingerprint(root):
    files = {}
    if root.is_symlink():
        raise ValueError('Skill source must not be a symlink: ' + str(root))
    for path in root.rglob('*'):
        rel = path.relative_to(root)
        if '__pycache__' in rel.parts or path.suffix in {'.pyc', '.pyo'}:
            continue
        if path.is_symlink():
            raise ValueError('Symlinks are not copied from skill packages: ' + str(path))
        if path.is_file():
            files[str(rel)] = hashlib.sha256(path.read_bytes()).hexdigest()
        elif not path.is_dir():
            raise ValueError('Non-regular source file: ' + str(path))
    return files


def plan_install(names, roots, replace):
    plan, releases = [], set()
    for name in names:
        source = SUITE / 'skills' / name
        for rel in ('SKILL.md', 'manifest.json', 'references/catalog.json', 'scripts/armbian.py'):
            if not (source / rel).is_file():
                raise ValueError('Missing source package file: ' + str(source / rel))
        verify_package(source)
        catalog = json.loads((source / 'references/catalog.json').read_text())
        releases.add(catalog['knowledge_release'])
        digest = fingerprint(source)
        for agent, root in roots:
            target = root / name
            if root == source.resolve() or root.is_relative_to(source.resolve()) or source.resolve().is_relative_to(root):
                raise ValueError('Installation destination overlaps source packages: ' + str(root))
            if target.is_symlink():
                raise ValueError('Refusing to replace a symlink: ' + str(target))
            if target.exists() and (not replace or not target.is_dir()):
                raise ValueError('Destination exists; use --replace for a directory update: ' + str(target))
            if root.exists() and not root.is_dir():
                raise ValueError('Destination root is not a directory: ' + str(root))
            plan.append({'agent': agent, 'source': source, 'target': target, 'digest': digest})
    if len(releases) != 1:
        raise ValueError('Selected source packages have different knowledge releases; rebuild them together first')
    targets = [item['target'] for item in plan]
    if len(set(targets)) != len(targets):
        raise ValueError('Agent destinations resolve to the same skill directories; select a single agent')
    return plan, releases.pop()


def install(plan):
    staging, backup_roots, journal = {}, {}, []
    try:
        # Stage and check every package before changing any existing installation.
        for item in plan:
            root = item['target'].parent
            if root not in staging:
                root.parent.mkdir(parents=True, exist_ok=True)
                staging[root] = Path(tempfile.mkdtemp(prefix='.armbian-install-', dir=root.parent))
            staged = staging[root] / item['target'].name
            shutil.copytree(item['source'], staged, ignore=IGNORE)
            verify_package(staged)
            if fingerprint(staged) != item['digest']:
                raise ValueError('Source changed or copy verification failed: ' + str(item['source']))
            item['staged'] = staged
        for item in plan:
            target, backup = item['target'], None
            target.parent.mkdir(parents=True, exist_ok=True)
            # Recheck ownership of the path immediately before moving it.
            if target.is_symlink() or (target.exists() and not target.is_dir()):
                raise ValueError('Destination type changed during installation: ' + str(target))
            if target.exists():
                if not item['replace']:
                    raise ValueError('Destination appeared during installation: ' + str(target))
                root = target.parent
                if root not in backup_roots:
                    backup_base = root.parent / 'armbian-skills-backups'
                    backup_base.mkdir(parents=True, exist_ok=True)
                    stamp = datetime.now().strftime('%Y%m%d-%H%M%S-')
                    backup_roots[root] = Path(tempfile.mkdtemp(prefix=stamp, dir=backup_base))
                backup = backup_roots[root] / target.name
            record = {'target': target, 'backup': None, 'installed': False}
            journal.append(record)
            if backup:
                os.replace(target, backup)
                record['backup'] = backup
            os.replace(item['staged'], target)
            record['installed'] = True
    except BaseException:
        # Restore all old directories if any member of this batch fails.
        for record in reversed(journal):
            if record['installed']:
                shutil.rmtree(record['target'])
            if record['backup']:
                os.replace(record['backup'], record['target'])
        raise
    finally:
        for path in staging.values():
            shutil.rmtree(path, ignore_errors=True)
    return list(backup_roots.values())


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--agent', required=True, choices=('codex', 'claude', 'both'))
    parser.add_argument('--scope', choices=('user', 'project'), default='user')
    parser.add_argument('--project-dir', help='Project root (default: current directory with --scope project)')
    parser.add_argument('--dest', help='Explicit skills directory for one agent, including legacy Codex paths')
    parser.add_argument('--skill', action='append', choices=NAMES, help='Install only this skill; repeat to select several')
    parser.add_argument('--replace', action='store_true', help='Back up and replace existing complete skill directories')
    parser.add_argument('--dry-run', action='store_true', help='Validate and print the plan without writing anything')
    args = parser.parse_args(argv)
    try:
        names = tuple(dict.fromkeys(args.skill or NAMES))
        roots = destinations(args.agent, args.scope, args.project_dir, args.dest)
        plan, release = plan_install(names, roots, args.replace)
        print('Knowledge release: ' + release)
        for item in plan:
            item['replace'] = args.replace
            action = 'replace (with backup)' if item['target'].exists() else 'install'
            print(f'{item["agent"]}: {action} {item["target"]}')
        if args.dry_run:
            print('Dry run: no files changed.')
            return 0
        backups = install(plan)
        print(f'Installed {len(plan)} complete skill directories.')
        for path in backups:
            print('Previous installation backup: ' + str(path))
        print('If new skills are not visible, reload/restart the agent in the same user/environment.')
        return 0
    except (OSError, ValueError, KeyError) as exc:
        print('ERROR: ' + str(exc), file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print('Interrupted; attempted to restore previous installations.', file=sys.stderr)
        return 130


if __name__ == '__main__':
    sys.exit(main())
