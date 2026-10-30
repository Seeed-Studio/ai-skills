"""Small offline lexical discovery. Relevance never establishes applicability."""
import math
import re
from collections import Counter

ALIASES = {
    'gpio': ['点灯', '灯不亮', '灯关不掉', '针脚', '排针', '引脚', '电平', 'led'],
    'i2c': ['温湿度', '温度传感器', 'aht20', 'sensor'],
    'spi': ['spidev', 'st7789', '背光', 'backlight', 'spi屏'],
    'thermal': ['风扇', '降频', '热降频', '温控', '过热', 'throttling', 'fan', 'thermal'],
    'vpu': ['硬解', '硬编', '视频', '转码', 'jellyfin', 'codec', 'decode', 'encode'],
    'npu': ['推理', '模型', 'rknn', 'inference'],
    'gpu': ['图形', '渲染', 'opencl', 'llvmpipe'],
    'deployment': ['部署', '容器', 'container', 'docker', 'service', '服务'],
    'verification': ['验证', '诊断', '报错', '失败', '错误', '排障'],
    'onewire': ['ds18b20', '单总线', '1-wire', 'one-wire'],
}


def tokens(text):
    text = text.casefold()
    words = re.findall(r'[a-z0-9][a-z0-9._+-]*', text)
    for canonical, aliases in ALIASES.items():
        if any((alias in text if re.search('[\u4e00-\u9fff]', alias)
                else re.search(r'(?<!\w)' + re.escape(alias) + r'(?!\w)', text)) for alias in aliases):
            words.append(canonical)
    return words


def search(catalog, query, limit=5, facts=None, engine=None):
    query_tokens = set(tokens(query))
    documents = []
    states = {}
    if facts is not None:
        matched = engine.match(catalog, facts)
        for bucket in ('matches', 'unknown', 'no_match', 'excluded'):
            for item in matched[bucket]:
                states[item['id']] = item
    for entry in catalog['entries']:
        if entry['kind'] in {'source', 'source_registry', 'index', 'report', 'runtime_snapshot', 'compatibility_observation'}:
            continue
        if entry.get('maturity') in {'draft', 'deprecated'}:
            continue
        state = states.get(entry['id'])
        if state and state['status'] in {'no_match', 'excluded'}:
            continue
        text = ' '.join([entry['id'], entry['path'], entry.get('summary', ''),
                         ' '.join(v for values in entry.get('applies_to', {}).values() for v in values)])
        documents.append((entry, Counter(tokens(text)), state))
    n = len(documents)
    average = sum(sum(c.values()) for _, c, _ in documents) / max(n, 1)
    frequencies = {t: sum(t in counts for _, counts, _ in documents) for t in query_tokens}
    results = []
    for entry, counts, state in documents:
        score = 0.0
        hit = []
        for term in query_tokens:
            frequency = counts[term]
            if not frequency:
                continue
            hit.append(term)
            idf = math.log(1 + (n - frequencies[term] + 0.5) / (frequencies[term] + 0.5))
            score += idf * frequency * 2.2 / (frequency + 1.2 * (0.25 + 0.75 * sum(counts.values()) / max(average, 1)))
        if score:
            results.append({'reference_id': entry['id'], 'path': entry['path'],
                            'summary': entry.get('summary', entry['id']), 'score': round(score, 5),
                            'matched_terms': sorted(hit),
                            'applicability': state['status'] if state else 'unknown',
                            'checks': state['checks'] if state else [],
                            'required_refs': entry.get('required_refs', []),
                            'note': 'Read the full reference and required dependencies; relevance is not hardware availability.'})
    results.sort(key=lambda x: (-x['score'], x['reference_id']))
    return {'knowledge_release': catalog['knowledge_release'], 'query': query,
            'results': results[:limit], 'total_candidates': len(results),
            'note': 'No matches; try a specific interface or symptom.' if not results else 'Unknown facts remain unknown.'}
