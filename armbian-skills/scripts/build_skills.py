#!/usr/bin/env python3
"""Build/check a self-contained skill from reviewed source; no target access."""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from armbian_skills.catalog import inventory, verify_package, digest
NAME = 'armbian-hardware'


def populate(out):
    shutil.copytree(ROOT / 'skills' / NAME, out, ignore=shutil.ignore_patterns('references', 'scripts', 'workflows', 'templates', 'manifest.json', '__pycache__'))
    for source, target in [('knowledge/references', 'references'), ('workflows', 'workflows'), ('templates', 'templates'), ('src/armbian_skills', 'scripts/lib/armbian_skills')]:
        inventory(ROOT / source)  # reject symlinks in maintained sources
        shutil.copytree(ROOT / source, out / target, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    shutil.copyfile(ROOT / 'scripts/armbian.py', out / 'scripts/armbian.py')
    shutil.copyfile(ROOT / 'probes/probe_device.py', out / 'scripts/probe_device.py')
    for p in out.rglob('*.md'):
        for link in re.findall(r'\]\(([^)]+)\)', p.read_text()):
            if re.match(r'^[a-z]+://', link) or link.startswith('#'):
                continue
            target = (p.parent / link.split('#')[0]).resolve()
            if not target.is_relative_to(out.resolve()) or not target.exists():
                raise ValueError('Broken/outside bundle link: ' + str(p) + ': ' + link)
    return inventory(out)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--update-lock', action='store_true')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.update_lock and args.check:
        parser.error('--check and --update-lock are exclusive')
    try:
        subprocess.run([sys.executable, str(ROOT / 'scripts/refresh_catalog.py'), '--check'], check=True)
        version = json.loads((ROOT / 'release/version.json').read_text())
        with tempfile.TemporaryDirectory() as tmp:
            stage = Path(tmp) / NAME
            files = populate(stage)
            lock = {'schema_version': 2, **version, 'files': files}
            lock_path = ROOT / 'release/lock.json'
            if args.update_lock:
                lock_path.write_text(json.dumps(lock, indent=2, sort_keys=True) + '\n')
            if not lock_path.exists() or json.loads(lock_path.read_text()) != lock:
                raise ValueError('Release lock stale; review source and use --update-lock')
            commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
            dirty = bool(subprocess.check_output(['git', 'status', '--porcelain', '--', '.'], cwd=ROOT, text=True).strip())
            manifest = {**lock, 'source_commit': commit, 'source_dirty': dirty,
                        'validation_scope': 'Static references and tools; no current hardware acceptance implied.'}
            (stage / 'manifest.json').write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
            verify_package(stage)
            target = ROOT / 'skills' / NAME
            if args.check:
                actual = verify_package(target)
                if actual != manifest:
                    raise ValueError('Generated package stale; rebuild')
            else:
                # Only replace generated paths, never the hand-maintained entry.
                for name in ('references', 'scripts', 'workflows', 'templates'):
                    dest = target / name
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(stage / name, dest)
                shutil.copyfile(stage / 'manifest.json', target / 'manifest.json')
                dist = ROOT / 'dist'
                dist.mkdir(exist_ok=True)
                archive = dist / (NAME + '-' + version['skill_version'] + '.skill')
                with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as z:
                    for p in sorted(stage.rglob('*')):
                        if p.is_file():
                            info = zipfile.ZipInfo(NAME + '/' + p.relative_to(stage).as_posix(), (2026, 1, 1, 0, 0, 0))
                            info.compress_type = zipfile.ZIP_DEFLATED
                            info.external_attr = 0o100644 << 16
                            z.writestr(info, p.read_bytes())
                (dist / 'SHA256SUMS').write_text(digest(archive) + '  ' + archive.name + '\n')
            print('OK: self-contained ' + NAME + ', ' + str(len(files)) + ' files, reviewed release lock')
        return 0
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        print('ERROR: ' + str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
