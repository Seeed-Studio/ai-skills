"""Focused provenance and pin queries preserve applicability and electrical limits."""
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from armbian_skills.catalog import load,info
from armbian_skills.pins import lookup
from armbian_skills.cli import main

BOARD='seeed.recomputer-rk3588-devkit'


class QueryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog=load(ROOT)

    def test_info_is_compact_and_provenance_is_preserved(self):
        package=ROOT/'skills/armbian-hardware'
        manifest=json.loads((package/'manifest.json').read_text())
        result=info(package)
        for key in ('source_commit','source_dirty','knowledge_release','validation_scope'):
            self.assertEqual(result[key],manifest[key])
        self.assertNotIn('files',result)
        self.assertEqual(result['file_count'],len(manifest['files']))
        self.assertLess(len(json.dumps(result)),1500)
        self.assertEqual(info(ROOT)['mode'],'development-source')

    def test_spi_display_queries_reach_spi_capability_references(self):
        from armbian_skills.search import search
        for query in ('ST7789 spidev CS backlight GPIO header','背光 SPI 屏接线'):
            results=search(self.catalog,query,limit=5)['results']
            self.assertTrue({r['reference_id'] for r in results}&{'capability.spi','capability.spi.verification'},
                            f'{query}: {[(r["reference_id"],r["score"]) for r in results]}')

    def test_thermal_fan_queries_reach_thermal_verification(self):
        from armbian_skills.search import search
        for query in ('thermal throttling cpufreq fan','温度 风扇 降频 判定'):
            results=search(self.catalog,query,limit=5)['results']
            self.assertIn('capability.thermal.verification',{r['reference_id'] for r in results[:3]},
                          f'{query}: {[(r["reference_id"],r["score"]) for r in results]}')

    def test_exact_pin_rows_shared_net_and_unknown_limits_survive(self):
        result=lookup(self.catalog,BOARD,'v1.0','J10',[23,40])
        entry=result['references'][0]
        self.assertEqual([p['physical_pin'] for p in entry['pins']],[23,40])
        self.assertEqual({p['soc_pad'] for p in entry['pins']},{'GPIO2_C0'})
        self.assertEqual(entry['shared_net_groups'][0]['physical_pins'],[23,40])
        self.assertFalse(entry['context']['operation_policy']['pin_writes_allowed'])
        self.assertIsNone(entry['context']['electrical_limits']['max_drive_current_ma'])
        self.assertEqual(entry['applicability'],'unknown')
        self.assertTrue(entry['sources'])
        self.assertTrue(entry['required_refs'])

    def test_single_pin_still_reports_partner(self):
        entry=lookup(self.catalog,BOARD,'v1.0','J10',[23])['references'][0]
        self.assertEqual(len(entry['pins']),1)
        self.assertIn(40,entry['shared_net_groups'][0]['physical_pins'])

    def test_unknown_profile_connector_pin_and_alias_never_fall_back(self):
        for board,revision,connector,pins in [(BOARD,'unknown','J10',[23]),(BOARD,'v1.0','J3',[23]),('rk3588','v1.0','J10',[23]),(BOARD,'v1.0','J10',[41]),(BOARD,'v1.0','J10',[0])]:
            with self.subTest(board=board,revision=revision,connector=connector,pins=pins):
                with self.assertRaises(ValueError):lookup(self.catalog,board,revision,connector,pins)

    def test_conflicting_current_facts_reject_the_selected_reference(self):
        facts={'schema_version':'1','target':{'board_ids':['seeed.recomputer-rk3576-devkit'],'hardware_revisions':['v1.0']}}
        with self.assertRaises(ValueError):lookup(self.catalog,BOARD,'v1.0','J10',[23],facts)

    def test_ambiguous_facts_do_not_become_target_confirmation(self):
        facts={'schema_version':'1','target':{'board_ids':[BOARD,'seeed.recomputer-rk3576-devkit'],'hardware_revisions':['v1.0']}}
        result=lookup(self.catalog,BOARD,'v1.0','J10',[23],facts)
        self.assertEqual(result['references'][0]['applicability'],'unknown')
        self.assertTrue(result['identity']['conflicts'])

    def test_derived_index_matches_every_canonical_pin_field(self):
        import yaml
        for entry in self.catalog['entries']:
            if 'pin_data' not in entry:continue
            canonical=yaml.safe_load((ROOT/'knowledge/references'/entry['path']).read_text())
            for key,value in entry['pin_data'].items():
                self.assertEqual(value,canonical[key],(entry['id'],key))

    def test_pins_and_info_work_in_isolated_installed_package(self):
        import subprocess
        with tempfile.TemporaryDirectory() as temp:
            package=Path(temp)/'pkg';shutil.copytree(ROOT/'skills/armbian-hardware',package)
            for args in [['info'],['pins','--board',BOARD,'--revision','v1.0','--connector','J10','--pins','23','40']]:
                run=subprocess.run([sys.executable,'-I',str(package/'scripts/armbian.py'),*args],cwd=temp,capture_output=True,text=True)
                self.assertEqual(run.returncode,0,run.stderr)
                result=json.loads(run.stdout)
                self.assertEqual(result['knowledge_release'],self.catalog['knowledge_release'])
                if args[0]=='pins':
                    self.assertTrue(Path(result['references'][0]['read_path']).is_file())
                    self.assertTrue(Path(result['reference_root']).is_dir())
            manifest=package/'manifest.json'
            d=json.loads(manifest.read_text());d['knowledge_release']='other';manifest.write_text(json.dumps(d))
            run=subprocess.run([sys.executable,'-I',str(package/'scripts/armbian.py'),'info'],capture_output=True,text=True)
            self.assertNotEqual(run.returncode,0)

    def test_reference_paths_resolve_from_the_actual_reference_root(self):
        for args in [['search','i2c service'],['explain','--ref','common.deployment']]:
            out=io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(main(ROOT,args),0)
            result=json.loads(out.getvalue())
            for record in result.get('results',result.get('references',[])):
                self.assertTrue(Path(record['read_path']).is_file())
                self.assertEqual(Path(record['read_path']),Path(result['reference_root'])/record['path'])

    def test_bad_cli_pin_selection_is_a_structured_error(self):
        out,err=io.StringIO(),io.StringIO()
        with redirect_stdout(out),redirect_stderr(err):
            result=main(ROOT,['pins','--board',BOARD,'--revision','v1.0','--connector','J10','--pins','99'])
        self.assertEqual(result,2)
        self.assertIn('error',json.loads(err.getvalue()))
        self.assertEqual(out.getvalue(),'')


if __name__=='__main__':unittest.main()
