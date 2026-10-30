#!/usr/bin/env python3
"""Render/check documentary AHT20 wiring examples using canonical board pin data.

Maintenance only: PyYAML is required. Installed Skills use the bundled diagrams;
this script neither probes a target nor authorizes or performs hardware I/O.
"""
import argparse
from html import escape
from pathlib import Path

import yaml

R = Path(__file__).resolve().parents[1] / 'knowledge/references'
COLORS = {1: '#b91c1c', 14: '#334155', 27: '#15803d', 28: '#c2410c'}
ROLES = {1: ('3.3V', 'VCC'), 14: ('GND', 'GND'), 27: ('SDA', 'SDA'), 28: ('SCL', 'SCL')}


def render(soc, connector, bus, source_name):
    base = R / f'boards/seeed/recomputer-{soc}-devkit/revisions/v1.0'
    data = yaml.safe_load((base / source_name).read_text())
    pins = {p['physical_pin']: p for p in data['pins']}
    assert set(pins) == set(range(1, 41)), 'Expected a complete40-position source'
    for number, (signal, _) in ROLES.items():
        p = pins[number]
        net = p.get('schematic_net', p.get('net'))
        kind = p.get('pin_type', p.get('type'))
        if number == 1:
            voltage = p.get('documented_supply_voltage_v', p.get('nominal_voltage_v'))
            assert kind == 'power' and voltage == 3.3
        elif number == 14:
            assert kind == 'ground' and net == 'GND'
        else:
            assert kind == 'signal' and f'{bus}_{signal}' in net
            voltage = p.get('documented_header_nominal_voltage_v', p.get('header_nominal_voltage_v'))
            assert voltage == 3.3
    layout = yaml.safe_load((base / 'wiring-layout.yaml').read_text())
    show_header = layout['orientation_status'] == 'documented' and layout['header_location_diagram_allowed']
    if show_header:
        rows = layout['pin_rows']
        if len(rows) != 2 or any(len(row) != 20 for row in rows) or sorted(p for row in rows for p in row) != list(range(1, 41)):
            raise ValueError('Invalid physical connector layout: ' + str(base))
        expected_view = {'side': 'component', 'header_edge_in_view': 'top', 'pin1_end': 'right', 'odd_row': 'upper', 'even_row': 'lower'}
        if layout['view'] != expected_view or rows != [list(range(39, 0, -2)), list(range(40, 1, -2))]:
            raise ValueError('This renderer does not support the changed board view; adapt coordinates explicitly rather than silently mirroring it.')
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="970" viewBox="0 0 1200 970" role="img" aria-labelledby="title desc">',
           f'<title id="title">reComputer {soc.upper()} {connector} to AHT20 wiring example</title>',
           f'<desc id="desc">Board-specific header layout is shown only when its observation side and orientation are documented. {connector}-1 3.3V to VCC; {connector}-14 GND to GND; {connector}-27 {bus} SDA to SDA; {connector}-28 {bus} SCL to SCL. Verify target and module before wiring. Module terminal order is not depicted.</desc>',
           '<rect width="1200" height="970" fill="#f8fafc"/>',
           '<g font-family="DejaVu Sans, sans-serif" fill="#0f172a">']
    def text(x, y, value, size=19, fill='#0f172a', anchor='start', weight='normal'):
        svg.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}">{escape(value)}</text>')
    def rect(x, y, width, height, fill='#ffffff', stroke='#cbd5e1', radius=12):
        svg.append(f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{radius}" fill="{fill}" stroke="{stroke}"/>')
    text(56, 58, f'reComputer {soc.upper()} DevKit V1.0  |  {connector} + AHT20', 30, weight='bold')
    text(56, 96, 'Example wiring: 3.3V module, SDA/SCL at 3.3V. Match the actual module labels.', 19)
    rect(56, 140, 1088, 274)
    if show_header:
        text(80, 179, f'{connector}: component side, header along TOP edge', 23, weight='bold')
        rect(92, 218, 1016, 112, '#e2e8f0', '#94a3b8')
        for ri, row in enumerate(rows):
            for ci, number in enumerate(row):
                x = 112 + ci * 51.5
                y = 244 + ri * 60
                color = COLORS.get(number, '#ffffff')
                svg.append(f'<circle data-pin="{number}" cx="{x}" cy="{y}" r="15" fill="{color}" stroke="#94a3b8"/>')
                text(x, y+5, str(number), 15, '#ffffff' if number in COLORS else '#475569', 'middle', 'bold')
                if number in ROLES:
                    text(x, y-25 if ri == 0 else y+38, ROLES[number][0], 17, COLORS[number], 'middle', 'bold')
        text(80, 375, 'Upper row: 39 to 1. Lower row: 40 to 2. Pin1/2 are at the RIGHT end.', 19)
        evidence = 'official board photo' if layout['orientation_evidence_type'] == 'official_image' else 'maintainer-confirmed board view'
        text(80, 399, f'Orientation source: {evidence}. Confirm the actual PCB/view.', 17)
    else:
        text(80, 188, f'{connector}: physical orientation NOT confirmed', 25, weight='bold')
        text(80, 241, 'Header locator omitted: do not infer its layout from another board.', 22)
        text(80, 288, 'Need component-side view, connector position, pin1 end and row order.', 20)
        text(80, 361, 'The endpoint diagram below is a connection list, not a physical pin layout.', 19)
    rect(56, 440, 1088, 350)
    text(80, 478, 'Wire endpoints (module terminal order is not depicted)', 23, weight='bold')
    for i, (number, (signal, terminal)) in enumerate(ROLES.items()):
        y = 528 + i * 70; color = COLORS[number]
        rect(108, y-24, 270, 48); rect(824, y-24, 276, 48)
        text(130, y+7, f'{connector}-{number}  {signal}', 22, weight='bold')
        svg.append(f'<line x1="378" y1="{y}" x2="824" y2="{y}" stroke="{color}" stroke-width="5"/>')
        text(600, y-13, signal, 18, color, 'middle', 'bold')
        text(850, y+7, f'AHT20 {terminal}', 22, weight='bold')
    text(56, 831, f'{bus}: shared bus. Check current clients/address conflicts and module 3.3V compatibility.', 19)
    text(56, 870, 'POWER OFF before changing wiring; match the actual board and module markings.', 22, weight='bold')
    text(56, 907, 'Physical connector numbers; not Linux PIN labels or GPIO offsets. Do not mirror the board view.', 18)
    svg.append('</g></svg>\n')
    return base / 'assets/aht20-wiring.svg', '\n'.join(svg)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Check existing examples without rewriting them')
    args = parser.parse_args()
    for soc, connector, bus, filename in [('rk3576', 'J3', 'I2C4', 'schematic-mapping.yaml'),
                                           ('rk3588', 'J10', 'I2C6', 'interfaces.yaml')]:
        path, svg = render(soc, connector, bus, filename)
        if args.check:
            if not path.is_file() or path.read_text() != svg:
                raise ValueError('Wiring example stale or missing: ' + str(path))
        else:
            path.write_text(svg)
    print('OK: two wiring examples agree with canonical connector/power/I2C data')


if __name__ == '__main__':
    main()
