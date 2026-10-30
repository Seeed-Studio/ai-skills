import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

K=Path(__file__).resolve().parents[1] / 'knowledge'
spec=importlib.util.spec_from_file_location('probe',K.parent/'probes/probe_device.py')
probe=importlib.util.module_from_spec(spec);spec.loader.exec_module(probe)

class ProbeTests(unittest.TestCase):
    def test_missing_tool_and_bounded_processes(self):
        self.assertEqual(probe.command(['armbian_nonexistent_test_command'])['reason'],'tool_missing')
        ok=probe.command([sys.executable,'-c','print("ok")'])
        self.assertEqual(ok['status'],'ok')
        with patch.object(probe,'LIMIT',1024):
            huge=probe.command([sys.executable,'-c','import sys; sys.stdout.write("x"*100000)'])
        self.assertEqual(huge['reason'],'output_limit');self.assertEqual(len(huge['output']),1024)
        slow=probe.command([sys.executable,'-c','import time; time.sleep(5)'],timeout=.05)
        self.assertEqual(slow['reason'],'timeout')

    def test_release_allowlist_does_not_emit_secrets(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'release';path.write_text('BOARD=test\nPASSWORD=do-not-emit\nUSER_SECRET=private\n')
            result=probe.release(path,{'BOARD'})
            self.assertEqual(result['value'],{'BOARD':'test'})

    def test_filter_keeps_relevant_lines_after_large_unrelated_output(self):
        run=probe.command([sys.executable,'-c','import sys; sys.stdout.write("unrelated\\n"*10000 + "libGPIOD.so => /usr/lib/libgpiod.so\\n")'],include_lines=['libgpiod'])
        self.assertEqual(run['status'],'ok')
        self.assertEqual(run['output'],'libGPIOD.so => /usr/lib/libgpiod.so\n')
        self.assertGreater(run['raw_output_bytes'],probe.LIMIT)
        self.assertEqual(run['selected_line_patterns'],['libgpiod'])

    def test_filtered_collection_still_enforces_limits(self):
        run=probe.command([sys.executable,'-c','import sys; sys.stdout.write("selected\\n"*10000)'],include_lines=['selected'])
        self.assertEqual(run['reason'],'output_limit')
        self.assertEqual(run['status'],'unknown')
        self.assertLessEqual(len(run['output']),probe.LIMIT)
        run=probe.command([sys.executable,'-c','import sys; sys.stdout.write("x"*100000)'],include_lines=['selected'])
        self.assertEqual(run['status'],'unknown')
        self.assertEqual(run['reason'],'line_length_limit')

    def run_probe(self,payload,argv):
        calls=[]
        def fake_read(path,binary=False,limit=probe.LIMIT):
            calls.append(path)
            return {'status':'ok','value':list(payload),'truncated':True} if path.endswith('/eeprom') else {'status':'unknown'}
        output=io.StringIO()
        with patch.object(probe,'read',side_effect=fake_read), patch.object(probe.glob,'glob',side_effect=lambda p:['/sys/bus/i2c/devices/4-0057/eeprom'] if p.endswith('/eeprom') else []), patch.object(probe,'command',return_value={'status':'unknown','reason':'tool_missing'}), patch.object(probe.sys,'stdout',output):
            probe.main(argv)
        return json.loads(output.getvalue()),calls

    def test_default_probe_does_not_read_eeprom(self):
        result,calls=self.run_probe(b'SN:private',[])
        self.assertFalse(any(p.endswith('/eeprom') for p in calls))
        self.assertIn('eeprom_identity_read',result['not_performed'])
        self.assertFalse(result['execution_context']['application_access_tested'])

    def test_opt_in_identity_redacts_unknown_or_serial_payloads(self):
        for payload in (b'SN:1234567',b'0123456789'):
            result,_=self.run_probe(payload,['--eeprom-identity'])
            value=next(iter(result['eeprom_identity_prefix'].values()))
            self.assertIsNone(value['value'])
            self.assertNotIn(payload.decode(),json.dumps(result))
        result,_=self.run_probe(b'rk35xx00A0',['--eeprom-identity'])
        self.assertEqual(next(iter(result['eeprom_identity_prefix'].values()))['value'],{'magic':'rk35xx','board_code':'00A0'})

if __name__=='__main__':unittest.main()
