"""Guard board-view geometry, not just the electrical endpoint labels."""
import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

import yaml

K = Path(__file__).resolve().parents[1] / 'knowledge'
spec = importlib.util.spec_from_file_location('wiring_renderer', K.parent / 'scripts/render_wiring_examples.py')
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)


class WiringDiagramTests(unittest.TestCase):
    def test_both_boards_preserve_recorded_rows_and_right_hand_pin1(self):
        for soc, connector, bus, filename in [('rk3576', 'J3', 'I2C4', 'schematic-mapping.yaml'),
                                               ('rk3588', 'J10', 'I2C6', 'interfaces.yaml')]:
            with self.subTest(board=soc):
                path, svg = renderer.render(soc, connector, bus, filename)
                self.assertEqual(path.read_text(), svg)
                root = ET.fromstring(svg)
                points = {int(e.attrib['data-pin']): (float(e.attrib['cx']), float(e.attrib['cy']))
                          for e in root.iter() if 'data-pin' in e.attrib}
                self.assertEqual(set(points), set(range(1, 41)))
                self.assertEqual(points[1][0], max(x for x, y in points.values()))
                self.assertEqual(points[1][0], points[2][0])
                self.assertLess(points[1][1], points[2][1])
                for odd in range(1, 40, 2):
                    self.assertEqual(points[odd][0], points[odd+1][0])
                    self.assertLess(points[odd][1], points[odd+1][1])
                self.assertLess(points[39][0], points[1][0])
                self.assertLess(points[40][0], points[2][0])

    def changed_layout(self, mutate):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        rel = Path('boards/seeed/recomputer-rk3588-devkit/revisions/v1.0')
        base = root / rel
        base.mkdir(parents=True)
        shutil.copyfile(renderer.R / rel / 'interfaces.yaml', base / 'interfaces.yaml')
        layout = yaml.safe_load((renderer.R / rel / 'wiring-layout.yaml').read_text())
        mutate(layout)
        (base / 'wiring-layout.yaml').write_text(yaml.safe_dump(layout))
        return root

    def test_mirrored_rows_are_rejected_instead_of_silently_rotated(self):
        root = self.changed_layout(lambda d: d.update(pin_rows=[list(range(1, 40, 2)), list(range(2, 41, 2))]))
        with patch.object(renderer, 'R', root), self.assertRaises(ValueError):
            renderer.render('rk3588', 'J10', 'I2C6', 'interfaces.yaml')

    def test_changed_observation_side_requires_explicit_renderer_support(self):
        root = self.changed_layout(lambda d: d['view'].update(side='solder'))
        with patch.object(renderer, 'R', root), self.assertRaises(ValueError):
            renderer.render('rk3588', 'J10', 'I2C6', 'interfaces.yaml')

    def test_unknown_orientation_has_endpoints_but_no_guessed_pin_locator(self):
        root = self.changed_layout(lambda d: d.update(orientation_status='unconfirmed',
                                                     header_location_diagram_allowed=False,
                                                     view=None, pin_rows=None))
        with patch.object(renderer, 'R', root):
            _, svg = renderer.render('rk3588', 'J10', 'I2C6', 'interfaces.yaml')
        elements = list(ET.fromstring(svg).iter())
        self.assertFalse(any('data-pin' in e.attrib for e in elements))
        text = ' '.join(ET.fromstring(svg).itertext())
        self.assertIn('J10-27', text)
        self.assertIn('physical orientation NOT confirmed', text)


if __name__ == '__main__':
    unittest.main()
