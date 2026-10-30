"""Documentary pin lookup; selectors do not prove target identity or grant access."""
from . import applicability as engine


CONTEXT_FIELDS = (
    'connector', 'coverage', 'electrical_limits', 'electrical_scope',
    'operation_policy', 'verification', 'numbering', 'mux_scope',
    'revision_association_basis', 'unresolved_fields', 'orientation_claim',
)


def lookup(catalog, board, revision, connector, pins, facts=None):
    if not pins or any(p < 1 for p in pins):
        raise ValueError('Specify positive physical pin numbers')
    states, identity = {}, None
    if facts is not None:
        assessed = engine.match(catalog, facts)
        identity = assessed['identity']
        states = {e['id']: e for key in ('matches', 'unknown', 'no_match', 'excluded') for e in assessed[key]}
    results = []
    for entry in catalog['entries']:
        data = entry.get('pin_data')
        scope = entry.get('applies_to', {})
        if not data or board not in scope.get('board_ids', []) or revision not in scope.get('hardware_revisions', []):
            continue
        if data.get('connector', {}).get('designator') != connector:
            continue
        if entry.get('maturity') in {'draft', 'deprecated'}:
            continue
        state = states.get(entry['id'])
        if state and state['status'] in {'no_match', 'excluded'}:
            raise ValueError('Requested pin reference conflicts with supplied facts: ' + entry['id'])
        selected = [row for row in data['pins'] if row['physical_pin'] in pins]
        missing = sorted(set(pins) - {row['physical_pin'] for row in selected})
        if missing:
            raise ValueError('Physical pins absent from this reference: ' + ', '.join(map(str, missing)))
        results.append({
            'reference_id': entry['id'], 'path': entry['path'], 'content_digest': entry['content_digest'],
            'applicability': state['status'] if state else 'unknown',
            'checks': state['checks'] if state else [],
            'pins': selected,
            'context': {k: data[k] for k in CONTEXT_FIELDS if k in data},
            'shared_net_groups': [group for group in data.get('shared_net_groups', [])
                                  if set(pins) & set(group.get('physical_pins', []))],
            'required_refs': engine.references(entry)[0], 'sources': entry.get('sources', []),
        })
    if not results:
        raise ValueError('No documented pin table for the exact board/revision/connector; do not substitute another profile')
    return {'knowledge_release': catalog['knowledge_release'],
            'selectors': {'board': board, 'revision': revision, 'connector': connector, 'physical_pins': sorted(set(pins))},
            'identity': identity, 'references': results,
            'limits': ['Selectors choose static documentation; they are not current target observations.',
                       'Unknown identity, revision, mux, ownership, electrical state and application access remain unknown.',
                       'Query results never authorize GPIO output or establish functional acceptance.',
                       'Nominal voltage does not establish load drive capability. When current limits or component specifications are unknown, do not recommend direct GPIO load/LED drive or a resistor value.']}
