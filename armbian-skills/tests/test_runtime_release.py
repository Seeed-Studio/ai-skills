import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import yaml
import jsonschema

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from armbian_skills import applicability as engine
from armbian_skills.catalog import load, verify_package
from armbian_skills.search import search
spec = importlib.util.spec_from_file_location('installer', ROOT/'scripts/install_skills.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)
PACKAGE = ROOT/'skills/armbian-hardware'


class RuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load(ROOT)

    def test_chinese_and_english_discover_relevant_topics(self):
        for query, topic in [('容器视频没有硬解', 'vpu'), ('GPU rendering llvmpipe','gpu'), ('GPIO LED', 'gpio'), ('温湿度 AHT20','i2c'), ('模型推理','npu')]:
            result = search(self.catalog, query)
            self.assertTrue(any(topic in x['reference_id'] for x in result['results']), query)
            self.assertTrue(all(x['applicability']=='unknown' for x in result['results']))

    def test_empty_and_unrelated_query_abstain(self):
        for query in ['', '量子烹饪食谱', 'zzzznonexistent']:
            self.assertEqual(search(self.catalog, query)['results'], [])

    def test_search_cannot_override_strict_mismatch(self):
        facts = json.loads((ROOT/'tests/fixtures/rk3588-gpu.json').read_text())
        result = search(self.catalog, 'rk3576 gpio', 20, facts, engine)
        rejected = {x['id'] for key in ('no_match','excluded') for x in engine.match(self.catalog, facts)[key]}
        self.assertFalse(rejected & {x['reference_id'] for x in result['results']})

    def test_all_reference_schemas_and_bilingual_metadata(self):
        schema=json.loads((ROOT/'schemas/reference-metadata.schema.json').read_text())
        for p in (ROOT/'knowledge/references').rglob('*'):
            if p.suffix not in {'.yaml','.md'} or p.name=='catalog.yaml':
                continue
            text=p.read_text()
            data=yaml.safe_load(text.split('---\n',2)[1] if p.suffix=='.md' else text)
            jsonschema.validate(data,schema)
            if p.suffix=='.md' and not p.name.endswith('.zh-CN.md'):
                translated=p.with_name(p.stem+'.zh-CN.md')
                self.assertEqual(data,yaml.safe_load(translated.read_text().split('---\n',2)[1]))

    def test_install_and_execute_without_development_tree_or_site_packages(self):
        with tempfile.TemporaryDirectory() as temp:
            package=Path(temp)/'standalone'
            shutil.copytree(PACKAGE, package)
            for argv in [['search','容器视频没有硬解'],['match','--facts',str(ROOT/'tests/fixtures/rk3588-gpu.json')],['explain','--ref','capability.gpio']]:
                run=subprocess.run([sys.executable,'-I',str(package/'scripts/armbian.py'),*argv],cwd=temp,capture_output=True,text=True)
                self.assertEqual(run.returncode,0,run.stderr)
                self.assertEqual(json.loads(run.stdout)['knowledge_release'],'armbian-knowledge-2.0.0')
            explain=json.loads(subprocess.check_output([sys.executable,'-I',str(package/'scripts/armbian.py'),'explain','--ref','capability.gpio'],text=True))
            self.assertGreater(len(explain['references']),1)

    def test_tampered_files_extra_files_and_mixed_versions_rejected(self):
        for change in ('reference','helper','extra','version'):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as temp:
                package=Path(temp)/'pkg';shutil.copytree(PACKAGE,package)
                p=package/({'reference':'references/common/identity.md','helper':'scripts/probe_device.py','extra':'unexpected','version':'manifest.json'}[change])
                if change=='version':
                    d=json.loads(p.read_text());d['knowledge_release']='other';p.write_text(json.dumps(d))
                else:p.write_text((p.read_text() if p.exists() else '')+'\nchanged')
                with self.assertRaises(ValueError):verify_package(package)

    def test_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            package=Path(temp)/'pkg';shutil.copytree(PACKAGE,package)
            (package/'escape').symlink_to('/tmp')
            with self.assertRaises(ValueError):verify_package(package)

    def test_installer_dry_run_and_source_overlap(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)/'not-created'
            self.assertEqual(installer.main(['--agent','codex','--dest',str(root),'--dry-run']),0)
            self.assertFalse(root.exists())
            self.assertEqual(installer.main(['--agent','codex','--dest',str(ROOT/'skills'),'--replace','--dry-run']),1)

    def test_corrupt_source_is_not_installable(self):
        with patch.object(installer,'verify_package',side_effect=ValueError('corrupt source')):
            with tempfile.TemporaryDirectory() as temp:
                root=Path(temp)/'dest'
                self.assertEqual(installer.main(['--agent','codex','--dest',str(root)]),1)
                self.assertFalse(root.exists())

    def test_update_failure_restores_both_agent_directories(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            args=['--agent','both','--scope','project','--project-dir',str(root)]
            self.assertEqual(installer.main(args),0)
            one=root/'.agents/skills/armbian-hardware';two=root/'.claude/skills/armbian-hardware'
            (one/'user.txt').write_text('keep')
            self.assertEqual(installer.main(args),1)
            real=installer.os.replace
            def fail(source,target):
                if Path(target)==two and '.armbian-install-' in str(source):
                    raise OSError('injected second-agent failure')
                return real(source,target)
            with patch.object(installer.os,'replace',side_effect=fail):
                self.assertEqual(installer.main(args+['--replace']),1)
            self.assertEqual((one/'user.txt').read_text(),'keep')
            verify_package(two)

    def test_repeated_build_produces_identical_archive(self):
        archive=ROOT/'dist/armbian-hardware-2.0.0.skill'
        first=archive.read_bytes()
        subprocess.run([sys.executable,str(ROOT/'scripts/build_skills.py')],check=True,capture_output=True)
        self.assertEqual(first,archive.read_bytes())


class ManifestTests(unittest.TestCase):
    def test_manifest_has_valid_release_provenance(self):
        manifest=verify_package(PACKAGE)
        jsonschema.validate(manifest,json.loads((ROOT/'schemas/manifest.schema.json').read_text()))
        self.assertEqual(manifest['channel'],'development')


if __name__=='__main__':
    unittest.main()
