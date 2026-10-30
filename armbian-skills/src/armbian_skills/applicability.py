#!/usr/bin/env python3
"""Select local references using explicit facts. Python 3 stdlib; no device I/O."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import sys

DIMENSIONS = {
    'board_ids': 'target.board_ids', 'soc_ids': 'target.soc_ids',
    'hardware_revisions': 'target.hardware_revisions', 'architectures': 'target.architectures',
    'kernel_releases': 'target.kernel_releases', 'image_ids': 'target.image_ids',
    'capabilities': 'task.capabilities', 'operations': 'task.operations',
    'languages': 'task.languages', 'stack_ids': 'facts.stack_ids',
}
OPS = {'eq', 'in', 'contains_exact'}
TRACE_KINDS = {'source', 'source_registry', 'index', 'report', 'compatibility', 'runtime_snapshot', 'compatibility_observation'}


class FormatError(ValueError):
    pass


def get(data, field):
    for part in field.split('.'):
        if not isinstance(data, dict) or part not in data:
            return None
        data = data[part]
    return data


def strings(value):
    return isinstance(value, list) and bool(value) and all(isinstance(x, str) and x for x in value)


def validate_condition(c):
    if not isinstance(c, dict) or not isinstance(c.get('field'), str) or not c['field']:
        raise FormatError('Condition needs field')
    if c.get('operator') not in OPS:
        raise FormatError(f'Unknown operator: {c.get("operator")}')
    key = 'values' if c['operator'] == 'in' else 'value'
    if key not in c or c[key] is None:
        raise FormatError(f'Condition needs {key}: {c["field"]}')
    if c['operator'] == 'in' and (not isinstance(c[key], list) or not c[key]):
        raise FormatError('in requires a nonempty values list')


def references(entry):
    hard = list(entry.get('required_refs', [])) + [x['target_ref'] for x in entry.get('refines', [])]
    if 'platform_ref' in entry:
        hard.append(entry['platform_ref'])
    nav = list(entry.get('related', [])) + list(entry.get('candidate_stack_refs', []))
    nav += [x['interface_ref'] for x in entry.get('revision_profiles', [])]
    nav += [entry[k] for k in ('detection_ref', 'integration_ref', 'verification_ref', 'official_pinout_ref') if k in entry]
    trace = list(entry.get('sources', [])) + list(entry.get('validation_refs', []))
    trace += [x['report_ref'] for x in entry.get('cases', []) if 'report_ref' in x]
    trace += [x['source_ref'] for x in entry.get('overlays', [])]
    trace += [r for x in entry.get('excludes', []) for r in x.get('evidence_refs', [])]
    return hard, nav, trace


def validate_catalog(catalog):
    if not isinstance(catalog, dict) or catalog.get('schema_version') != '1' or not isinstance(catalog.get('knowledge_release'), str):
        raise FormatError('Invalid catalog header')
    if not isinstance(catalog.get('entries'), list):
        raise FormatError('Catalog entries must be a list')
    index = {}
    for e in catalog['entries']:
        if not isinstance(e, dict) or not re.fullmatch(r'[a-z][a-z0-9._-]*', e.get('id', '')):
            raise FormatError('Invalid reference ID')
        if e['id'] in index:
            raise FormatError('Duplicate ID: ' + e['id'])
        if not isinstance(e.get('path'), str) or Path(e['path']).is_absolute() or '..' in Path(e['path']).parts:
            raise FormatError('Unsafe reference path: ' + e['id'])
        if not re.fullmatch(r'sha256:[a-f0-9]{64}', e.get('content_digest', '')):
            raise FormatError('Invalid content_digest: ' + e['id'])
        index[e['id']] = e
        if e.get('kind') == 'source':
            continue
        for key in ('schema_version', 'kind', 'applies_to', 'required_refs', 'preconditions', 'refines', 'excludes', 'related', 'sources', 'validation_refs', 'maturity', 'owner', 'updated_at'):
            if key not in e:
                raise FormatError(f'Missing {key}: {e["id"]}')
        if e['schema_version'] != '1' or e['maturity'] not in {'draft', 'documented', 'validated', 'deprecated'}:
            raise FormatError('Invalid schema/maturity: ' + e['id'])
        if not isinstance(e['kind'], str) or not isinstance(e['owner'], str) or not e['owner'] or not isinstance(e['updated_at'], str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', e['updated_at']):
            raise FormatError('Invalid kind/owner/date: ' + e['id'])
        if not isinstance(e['applies_to'], dict):
            raise FormatError('applies_to must be a map')
        for key, values in e['applies_to'].items():
            if key not in DIMENSIONS or not strings(values):
                raise FormatError(f'Invalid applies_to dimension/values: {e["id"]}: {key}')
        for key in ('required_refs', 'related', 'sources', 'validation_refs'):
            if not isinstance(e[key], list) or any(not isinstance(x, str) for x in e[key]):
                raise FormatError(f'{key} must be an ID list: {e["id"]}')
        for key in ('preconditions', 'refines', 'excludes', 'runtime_constraints', 'identity_rules'):
            if not isinstance(e.get(key, []), list):
                raise FormatError(f'{key} must be a list: {e["id"]}')
        for c in e['preconditions']:
            validate_condition(c)
        for c in e.get('runtime_constraints', []):
            if not isinstance(c, dict) or not isinstance(c.get('component'), str) or not c.get('version_scheme'):
                raise FormatError('Invalid runtime constraint')
            validate_condition({**c, 'field': 'facts.versions.' + c['component']})
        for c in e.get('identity_rules', []):
            validate_condition({**c, 'field': c.get('evidence')})
        for refinement in e['refines']:
            if not isinstance(refinement, dict) or not isinstance(refinement.get('target_ref'), str) or not strings(refinement.get('field_paths')) or not isinstance(refinement.get('when'), list):
                raise FormatError('Invalid refinement: ' + e['id'])
            for c in refinement['when']:
                validate_condition(c)
        for exclusion in e['excludes']:
            if not isinstance(exclusion, dict) or not exclusion.get('reason') or not isinstance(exclusion.get('when'), list) or not exclusion['when'] or not strings(exclusion.get('evidence_refs')):
                raise FormatError('Exclusion needs when/reason/evidence_refs: ' + e['id'])
            for c in exclusion['when']:
                validate_condition(c)
    graph = {}
    for id, e in index.items():
        hard, nav, trace = references(e)
        for ref in hard + nav + trace:
            if not isinstance(ref, str) or ref not in index:
                raise FormatError(f'Missing reference: {id}: {ref}')
        graph[id] = hard
    active, done = set(), set()
    def visit(id):
        if id in active:
            raise FormatError('Required/refines dependency cycle at ' + id)
        if id in done:
            return
        active.add(id)
        for child in graph[id]:
            visit(child)
        active.remove(id)
        done.add(id)
    for id in graph:
        visit(id)
    return index


def condition(c, facts):
    actual = get(facts, c['field'])
    result = {'field': c['field'], 'operator': c['operator'], 'actual': actual,
              'expected': c.get('values') if c['operator'] == 'in' else c.get('value')}
    if actual is None or actual == []:
        return {**result, 'result': 'unknown', 'reason': 'missing_fact'}
    expected = result['expected']
    # Do not coerce bool/number/string or sort vendor/package versions.
    if c['operator'] == 'eq':
        passed = type(actual) is type(expected) and actual == expected
    elif c['operator'] == 'in':
        passed = any(type(actual) is type(x) and actual == x for x in expected)
    else:
        if not isinstance(actual, list):
            return {**result, 'result': 'unknown', 'reason': 'expected_list_fact'}
        passed = any(type(x) is type(expected) and x == expected for x in actual)
    return {**result, 'result': 'match' if passed else 'no_match'}


def conjunction(checks):
    states = {x['result'] for x in checks}
    return 'no_match' if 'no_match' in states else 'unknown' if 'unknown' in states else 'match'


def resolve_identity(index, data):
    data = deepcopy(data)
    target = data.setdefault('target', {})
    candidates, conflicts, evidence = {}, [], []
    for kind, dimension in [('board', 'board_ids'), ('platform', 'soc_ids')]:
        hits = set()
        for entry in index.values():
            if entry.get('kind') != kind:
                continue
            for rule in entry.get('identity_rules', []):
                check = condition({**rule, 'field': 'target.' + rule['evidence']}, data)
                if check['result'] == 'match':
                    stable_ids = entry.get('applies_to', {}).get(dimension, [])
                    hits.update(stable_ids)
                    evidence.append({'reference_id': entry['id'], 'dimension': dimension, **check})
        supplied = set(target.get(dimension) or [])
        combined = supplied | hits
        candidates[dimension] = sorted(combined)
        if len(combined) > 1:
            target[dimension] = None
            conflicts.append({'dimension': dimension, 'candidates': sorted(combined), 'reason': 'ambiguous_or_contradictory_identity'})
        elif combined:
            target[dimension] = sorted(combined)
        else:
            target[dimension] = None
    if len(target.get('hardware_revisions') or []) > 1:
        conflicts.append({'dimension': 'hardware_revisions', 'candidates': target['hardware_revisions'], 'reason': 'ambiguous_revision'})
        target['hardware_revisions'] = None
    return data, {'candidates': candidates, 'evidence': evidence, 'conflicts': conflicts,
                  'note': 'Identity candidates only; no hardware revision or pin permission inferred from reference snapshots.'}


def match(catalog, data, kinds=None):
    index = validate_catalog(catalog)
    if not isinstance(data, dict) or data.get('schema_version') != '1':
        raise FormatError('Input requires schema_version "1"')
    if data.get('expected_knowledge_release') is not None and data['expected_knowledge_release'] != catalog['knowledge_release']:
        raise FormatError('Knowledge release mismatch; review mixed reference versions')
    for section in ('target', 'task', 'facts'):
        if section in data and not isinstance(data[section], dict):
            raise FormatError(section + ' must be an object')
    for field in DIMENSIONS.values():
        value = get(data, field)
        if value is not None and not strings(value):
            raise FormatError(field + ' must be null or a nonempty list of exact strings')
    compatible = get(data, 'target.device_tree.compatible')
    if compatible is not None and not strings(compatible):
        raise FormatError('target.device_tree.compatible must be null or a nonempty string list')
    data, identity = resolve_identity(index, data)
    cache = {}
    def evaluate(id):
        if id in cache:
            return cache[id]
        e = index[id]
        checks = []
        for dim, allowed in e.get('applies_to', {}).items():
            actual = get(data, DIMENSIONS[dim])
            checks.append({'field': DIMENSIONS[dim], 'expected_any': allowed, 'actual': actual,
                           'result': 'unknown' if not actual else 'match' if set(actual) & set(allowed) else 'no_match'})
        for c in e.get('preconditions', []):
            checks.append(condition(c, data))
        for c in e.get('runtime_constraints', []):
            check = condition({**c, 'field': 'facts.versions.' + c['component']}, data)
            if c['version_scheme'] != 'exact':
                check.update(result='unknown', reason='version_scheme_requires_review')
            checks.append(check)
        status = conjunction(checks)
        exclusions = []
        for exclusion in e.get('excludes', []):
            exc_checks = [condition(c, data) for c in exclusion['when']]
            outcome = conjunction(exc_checks)
            exclusions.append({'result': outcome, 'reason': exclusion['reason'], 'checks': exc_checks,
                               'evidence_refs': exclusion['evidence_refs']})
            if outcome == 'match':
                status = 'excluded'
            elif outcome == 'unknown' and status == 'match':
                status = 'unknown'
        dependencies = []
        # refines declares background but never auto-merges fields, or grants access.
        for dep in references(e)[0]:
            dependency_status = evaluate(dep)['status']
            dependencies.append({'id': dep, 'status': dependency_status})
            if status == 'match' and dependency_status != 'match':
                status = 'unknown'
        result = {'id': id, 'kind': e['kind'], 'path': e['path'], 'content_digest': e['content_digest'],
                  'maturity': e.get('maturity'), 'status': status, 'checks': checks,
                  'exclusions': exclusions, 'required_references': dependencies,
                  'refinements_for_review': [{**r, 'condition_result': conjunction([condition(c, data) for c in r['when']])} for r in e.get('refines', [])]}
        if e.get('maturity') in {'draft', 'deprecated'} and status == 'match':
            result.update(status='unknown', review_reason='draft_or_deprecated_reference')
        if e.get('kind') in TRACE_KINDS:
            result['evidence_only'] = True
        cache[id] = result
        return result
    buckets = {'matches': [], 'unknown': [], 'no_match': [], 'excluded': []}
    for id, e in index.items():
        if e['kind'] in TRACE_KINDS or (kinds and e['kind'] not in kinds):
            continue
        result = evaluate(id)
        bucket = 'matches' if result['status'] == 'match' else result['status']
        buckets[bucket].append(result)
    return {'schema_version': '1', 'knowledge_release': catalog['knowledge_release'],
            'identity': identity, **buckets,
            'limits': ['Reference selection is not a capability availability or support declaration.',
                       'Historical reports/snapshots never populate current facts.',
                       'No arbitrary commands executed; refinements require review; pin operations require separate verified mapping.']}


def verify_files(catalog, root):
    root = Path(root).resolve()
    for e in catalog['entries']:
        path = (root / e['path']).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise FormatError('Missing/outside bundled reference: ' + e['path'])
        if 'sha256:' + hashlib.sha256(path.read_bytes()).hexdigest() != e['content_digest']:
            raise FormatError('Reference digest mismatch: ' + e['path'])
