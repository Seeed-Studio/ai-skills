"""Static routing invariants; no device, current mux or physical continuity claims."""
import hashlib
from pathlib import Path
import re
import unittest

import yaml

R = Path(__file__).resolve().parents[1] / 'knowledge' / 'references'
V = R / 'boards/seeed/recomputer-rk3588-devkit/revisions/v1.0'


class RK3588PinoutTests(unittest.TestCase):
    def setUp(self):
        self.data = yaml.safe_load((V / 'interfaces.yaml').read_text())
        self.pins = {p['physical_pin']: p for p in self.data['pins']}

    def test_complete_positions_and_bank_local_identities(self):
        self.assertEqual(len(self.data['pins']), 40)
        self.assertEqual(set(self.pins), set(range(1, 41)))
        self.assertEqual(self.data['coverage']['reviewed_physical_positions'], list(range(1, 41)))
        controllers = {0: 'fd8a0000', 1: 'fec20000', 2: 'fec30000', 3: 'fec40000', 4: 'fec50000'}
        signals = [p for p in self.pins.values() if p['type'] == 'signal']
        self.assertEqual(len(signals), 28)
        self.assertEqual(len({p['soc_pad'] for p in signals}), 27)
        for p in signals:
            bank, group, bit = re.fullmatch(r'GPIO([0-4])_([A-D])([0-7])', p['soc_pad']).groups()
            self.assertEqual(p['local_line_offset'], 8 * 'ABCD'.index(group) + int(bit))
            self.assertEqual(p['chip_label'], 'gpio' + bank)
            self.assertEqual(p['controller_node'], 'gpio@' + controllers[int(bank)])
            self.assertLess(p['local_line_offset'], p['line_count'])
            self.assertEqual(p['header_nominal_voltage_v'], 3.3)
        for p in self.pins.values():
            self.assertFalse(p['pin_writes_allowed'])
            self.assertIsNone(p['measured_voltage_v'])
        self.assertFalse(self.data['coverage']['all_pins_functional_tested'])

    def test_shared_header_positions_and_unpopulated_alternative(self):
        a, b = self.pins[23], self.pins[40]
        for key in ['net', 'soc_pad', 'controller_node', 'local_line_offset', 'level_shifter']:
            self.assertEqual(a[key], b[key])
        self.assertEqual((b['net'], b['soc_pad'], b['local_line_offset']),
                         ('GPIO2_C0_3V3', 'GPIO2_C0', 16))
        for pin in [a, b]:
            self.assertEqual(pin['shared_physical_pins_in_schematic'], [23, 40])
            self.assertTrue(pin['gpio_candidate'])
            self.assertEqual(pin['mapping_status'], 'schematic_trace')
            self.assertEqual(pin['gpio_write_readiness'], 'requires_current_target_checks')
        group = next(g for g in self.data['shared_net_groups'] if g['physical_pins'] == [23, 40])
        self.assertEqual(group['schematic_net'], b['net'])
        self.assertFalse(group['target_continuity_confirmed'])
        # An unpopulated alternative must not become an extra GPIO route.
        alternative = self.pins[24]['unpopulated_alternative']
        self.assertEqual(alternative['alternative_soc_pad'], 'GPIO0_C6')
        self.assertEqual(alternative['assembly_in_schematic'], 'DNP')
        self.assertFalse(alternative['routed_to_header_in_schematic'])
        self.assertEqual(self.pins[24]['soc_pad'], 'GPIO2_C3')

    def test_translator_package_pin_consistency_and_mapping_regression(self):
        a_pins = {1: 1, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7, 7: 8, 8: 9}
        b_pins = {1: 20, 2: 18, 3: 17, 4: 16, 5: 15, 6: 14, 7: 13, 8: 12}
        for pin in self.pins.values():
            if 'level_shifter' not in pin:
                continue
            t = pin['level_shifter']
            channel = int(t['soc_channel'][1:])
            self.assertEqual(t['header_channel'], 'B' + str(channel))
            self.assertEqual(t['soc_package_pin'], a_pins[channel])
            self.assertEqual(t['header_package_pin'], b_pins[channel])
            self.assertEqual(pin['soc_nominal_voltage_v'], 1.8)
        p = self.pins[15]
        self.assertEqual((p['soc_pad'], p['controller_node'], p['local_line_offset']),
                         ('GPIO1_C6', 'gpio@fec20000', 22))
        self.assertEqual((p['level_shifter']['soc_package_pin'], p['level_shifter']['header_package_pin']), (4, 17))
        self.assertFalse(p['cached_vendor_PIN_label']['matches_schematic_pad'])

    def test_bundled_source_excerpts_match_recorded_hashes(self):
        sources = yaml.safe_load((R / 'sources/index.yaml').read_text())['source_entries']
        for source in sources:
            if source['id'] == 'source.seeed-rk3588-v1-schematic':
                for crop in source['bundled_excerpts']:
                    self.assertEqual(hashlib.sha256((R / crop['path']).read_bytes()).hexdigest(), crop['sha256'])


if __name__ == '__main__':
    unittest.main()
