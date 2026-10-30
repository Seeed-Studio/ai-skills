"""Package integrity and catalog loading, standard library only."""
import hashlib
import json
import subprocess
from pathlib import Path
from .applicability import validate_catalog, verify_files


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(root):
    result = {}
    for p in sorted(root.rglob('*')):
        if '__pycache__' in p.parts or p.suffix == '.pyc':
            continue
        if p.is_symlink():
            raise ValueError('Symlink in package: ' + str(p))
        if p.is_file() and p != root / 'manifest.json':
            result[p.relative_to(root).as_posix()] = digest(p)
    return result


def verify_package(root):
    root = Path(root).resolve()
    manifest = json.loads((root / 'manifest.json').read_text())
    if manifest.get('schema_version') != 2 or manifest.get('skill_name') != 'armbian-hardware':
        raise ValueError('Invalid package manifest')
    expected = manifest.get('files')
    if not isinstance(expected, dict) or not expected or inventory(root) != expected:
        raise ValueError('Package file inventory or digest mismatch')
    catalog = json.loads((root / 'references/catalog.json').read_text())
    if catalog['knowledge_release'] != manifest['knowledge_release']:
        raise ValueError('Mixed knowledge releases')
    validate_catalog(catalog)
    verify_files(catalog, root / 'references')
    return manifest


def load(root):
    if (root / 'manifest.json').exists():
        verify_package(root)
    references = root / 'references' if (root / 'references').is_dir() else root / 'knowledge/references'
    catalog = json.loads((references / 'catalog.json').read_text())
    validate_catalog(catalog)
    verify_files(catalog, references)
    return catalog


def info(root):
    """Return provenance without emitting the file hash map."""
    if (root / 'manifest.json').exists():
        manifest = verify_package(root)
        keys = ('skill_name', 'skill_version', 'knowledge_release', 'channel',
                'source_commit', 'source_dirty', 'validation_scope')
        return {**{k: manifest[k] for k in keys}, 'file_count': len(manifest['files'])}
    catalog = load(root)
    version = json.loads((root / 'release/version.json').read_text())
    try:
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True, stderr=subprocess.DEVNULL, timeout=5).strip()
        dirty = bool(subprocess.check_output(['git', 'status', '--porcelain', '--', '.'], cwd=root, text=True, stderr=subprocess.DEVNULL, timeout=5).strip())
    except (OSError, subprocess.SubprocessError):
        commit, dirty = None, None
    return {**version, 'mode': 'development-source', 'reference_count': len(catalog['entries']),
            'source_commit': commit, 'source_dirty': dirty,
            'validation_scope': 'Static knowledge only; current target acceptance is not established.'}
