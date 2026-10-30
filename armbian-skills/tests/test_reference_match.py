import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

K = Path(__file__).resolve().parents[1] / 'knowledge'
sys.path.insert(0, str(K.parent / 'src'))
from armbian_skills import applicability as engine


def entry(id, **changes):
    value = dict(schema_version='1', id=id, kind='common', path=id + '.md', content_digest='sha256:'+'0'*64,
                 applies_to={}, required_refs=[], preconditions=[], refines=[], excludes=[], related=[], sources=[],
                 validation_refs=[], maturity='documented', owner='test', updated_at='2026-10-19')
    return {**value, **changes}


def catalog(*entries):
    return {'schema_version':'1','knowledge_release':'test-only','entries':list(entries)}


def outcome(cat, data, id='test.rule'):
    result = engine.match(cat, {'schema_version':'1',**data})
    for bucket in ('matches','unknown','no_match','excluded'):
        if any(e['id']==id for e in result[bucket]):return bucket
    raise AssertionError('Reference not returned: ' + id)


class MatcherTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.real = json.loads((K/'references/catalog.json').read_text())

    def test_rk3588_does_not_inherit_rk3576_board_or_gpio_stack(self):
        facts=json.loads((K.parent/'tests/fixtures/rk3588-gpu.json').read_text())
        result=engine.match(self.real,facts)
        ids={x['id'] for x in result['matches']}
        self.assertIn('board.seeed.recomputer-rk3588-devkit',ids)
        self.assertIn('integration.javascript.guide',ids)
        self.assertFalse(any('rk3576' in id for id in ids))
        self.assertNotIn('stack.linux-gpio-chardev',ids)

    def test_unknown_revision_never_selects_rk3576_pin_table(self):
        facts=json.loads((K.parent/'tests/fixtures/rk3576-gpio.json').read_text())
        result=engine.match(self.real,facts)
        ids={'board.seeed.recomputer-rk3576-devkit.v1.0.'+suffix
             for suffix in ('official-pinout','schematic-mapping','schematic-mapping.guide')}
        self.assertTrue(ids <= {e['id'] for e in result['unknown']})
        facts['target']['hardware_revisions']=['v1.0']
        result=engine.match(self.real,facts)
        self.assertTrue(ids <= {e['id'] for e in result['matches']})
        # Even a reference match does not remove the source's pin-write constraint.
        import yaml
        pin=yaml.safe_load((K/'references/boards/seeed/recomputer-rk3576-devkit/revisions/v1.0/official-pinout.yaml').read_text())
        self.assertFalse(pin['operation_policy']['pin_writes_allowed'])

    def test_wrong_user_board_hint_is_not_silently_accepted(self):
        facts=json.loads((K.parent/'tests/fixtures/contradictory-board.json').read_text())
        result=engine.match(self.real,facts)
        self.assertTrue(result['identity']['conflicts'])
        self.assertFalse(any(e['kind']=='board' for e in result['matches']))

    def test_rk3588_selects_panthor_not_panfrost(self):
        facts=json.loads((K.parent/'tests/fixtures/rk3588-gpu.json').read_text())
        result=engine.match(self.real,facts)
        ids={x['id'] for x in result['matches']}
        self.assertIn('stack.mesa-panthor',ids)
        self.assertNotIn('stack.mesa-panfrost',ids)

    def test_unrecorded_device_keeps_generic_development_path(self):
        facts=json.loads((K.parent/'tests/fixtures/unknown-device.json').read_text())
        result=engine.match(self.real,facts)
        ids={x['id'] for x in result['matches']}
        self.assertIn('common.project-integration',ids)
        self.assertIn('capability.i2c',ids)
        self.assertIn('integration.go.guide',ids)
        self.assertFalse(any(e['kind']=='board' for e in result['matches']))

    def test_dimensions_and_allowed_sets(self):
        cat=catalog(entry('test.rule',applies_to={'languages':['go','rust'],'capabilities':['gpio']}))
        self.assertEqual(outcome(cat,{'task':{'languages':['rust'],'capabilities':['gpio']}}),'matches')
        self.assertEqual(outcome(cat,{'task':{'languages':['javascript'],'capabilities':['gpio']}}),'no_match')
        self.assertEqual(outcome(cat,{'task':{'languages':['rust']}}),'unknown')

    def test_conditions_exact_set_and_list_membership(self):
        c=[{'field':'facts.api','operator':'in','values':['2.1','2.2']},
           {'field':'facts.features','operator':'contains_exact','value':'events'},
           {'field':'facts.application.device_access','operator':'eq','value':True}]
        cat=catalog(entry('test.rule',preconditions=c))
        data={'facts':{'api':'2.2','features':['events'],'application':{'device_access':True}}}
        self.assertEqual(outcome(cat,data),'matches')
        data['facts']['application']['device_access']=False
        self.assertEqual(outcome(cat,data),'no_match')

    def test_no_boolean_numeric_coercion(self):
        cat=catalog(entry('test.rule',preconditions=[{'field':'facts.access','operator':'eq','value':True}]))
        self.assertEqual(outcome(cat,{'facts':{'access':1}}),'no_match')
        self.assertEqual(outcome(cat,{}),'unknown')

    def test_version_never_lexically_sorted(self):
        constraint={'component':'lib','version_scheme':'exact','operator':'in','values':['2.9','2.10-vendor']}
        cat=catalog(entry('test.rule',runtime_constraints=[constraint]))
        self.assertEqual(outcome(cat,{'facts':{'versions':{'lib':'2.10-vendor'}}}),'matches')
        self.assertEqual(outcome(cat,{'facts':{'versions':{'lib':'2.10'}}}),'no_match')
        self.assertEqual(outcome(cat,{}),'unknown')
        constraint['version_scheme']='vendor-range'
        self.assertEqual(outcome(cat,{'facts':{'versions':{'lib':'2.10-vendor'}}}),'unknown')

    def test_explicit_negative_evidence_and_missing_exclusion_fact(self):
        cat=catalog(entry('test.source',kind='source'),entry('test.rule',excludes=[{'when':[{'field':'facts.api','operator':'eq','value':'bad'}],'reason':'documented incompatible API','evidence_refs':['test.source']}]))
        self.assertEqual(outcome(cat,{'facts':{'api':'bad'}}),'excluded')
        self.assertEqual(outcome(cat,{'facts':{'api':'ok'}}),'matches')
        self.assertEqual(outcome(cat,{}),'unknown')

    def test_identical_identity_rules_are_ambiguous(self):
        boards=[entry('board.'+name,kind='board',applies_to={'board_ids':[name]},identity_rules=[{'evidence':'device_tree.compatible','operator':'contains_exact','value':'vendor,alias'}]) for name in ('first','second')]
        result=engine.match(catalog(*boards),{'schema_version':'1','target':{'device_tree':{'compatible':['vendor,alias']}}})
        self.assertEqual(len(result['identity']['conflicts']),1)
        self.assertFalse(result['matches'])

    def test_model_alias_does_not_prove_board(self):
        b=entry('board.test',kind='board',applies_to={'board_ids':['test']},identity_rules=[{'evidence':'device_tree.compatible','operator':'contains_exact','value':'vendor,test'}])
        self.assertEqual(outcome(catalog(b),{'target':{'model':'vendor,test'}},'board.test'),'unknown')

    def test_revision_conflict_stays_unknown(self):
        e=entry('test.rule',applies_to={'hardware_revisions':['v1']})
        self.assertEqual(outcome(catalog(e),{'target':{'hardware_revisions':['v1','v2']}}),'unknown')

    def test_navigation_cycle_allowed_but_required_or_refines_cycle_rejected(self):
        a=entry('test.a',related=['test.b']);b=entry('test.b',related=['test.a'])
        engine.validate_catalog(catalog(a,b))
        a['required_refs']=['test.b'];b['required_refs']=['test.a']
        with self.assertRaises(engine.FormatError):engine.validate_catalog(catalog(a,b))
        a['required_refs']=[]
        a['refines']=[{'target_ref':'test.b','field_paths':['constraint'],'when':[]}]
        with self.assertRaises(engine.FormatError):engine.validate_catalog(catalog(a,b))

    def test_precondition_is_not_treated_as_reference(self):
        e=entry('test.rule',preconditions=[{'field':'facts.path_not_a_document','operator':'eq','value':'anything'}])
        self.assertEqual(outcome(catalog(e),{}),'unknown')

    def test_refinement_reports_review_without_merging(self):
        base=entry('test.base');rule=entry('test.rule',refines=[{'target_ref':'test.base','field_paths':['pin_writes_allowed'],'when':[{'field':'facts.known','operator':'eq','value':True}]}])
        result=engine.match(catalog(base,rule),{'schema_version':'1','facts':{'known':True}})
        r=next(x for x in result['matches'] if x['id']=='test.rule')
        self.assertEqual(r['refinements_for_review'][0]['condition_result'],'match')
        self.assertNotIn('pin_writes_allowed',r)

    def test_draft_not_recommended_and_required_conditions_not_skipped(self):
        dep=entry('test.dep',applies_to={'soc_ids':['one']});e=entry('test.rule',required_refs=['test.dep'])
        self.assertEqual(outcome(catalog(dep,e),{'target':{'soc_ids':['two']}}),'unknown')
        dep['applies_to']={};dep['maturity']='draft'
        self.assertEqual(outcome(catalog(dep,e),{}),'unknown')

    def test_historical_runtime_does_not_fill_facts(self):
        e=entry('test.rule',applies_to={'hardware_revisions':['v1']},historical_observations=[{'hardware_revisions':['v1']}])
        self.assertEqual(outcome(catalog(e),{}),'unknown')

    def test_expected_release_prevents_silent_mixed_versions(self):
        with self.assertRaises(engine.FormatError):
            engine.match(catalog(entry('test.rule')),{'schema_version':'1','expected_knowledge_release':'other-release'})

    def test_gpio_recipe_retains_protected_signal_exclusion(self):
        facts=json.loads((K.parent/'tests/fixtures/rk3576-gpio.json').read_text())
        facts['facts']['hardware']={'pin_mapping_verified':True,'signal_voltage_verified':True,'line_busy':False,'protected':True}
        self.assertEqual(outcome(self.real,facts,'recipe.bounded-gpio-command'),'excluded')
        facts['facts']['hardware']['protected']=False
        self.assertEqual(outcome(self.real,facts,'recipe.bounded-gpio-command'),'matches')

    def test_invalid_metadata_rejected_instead_of_ignored(self):
        changes=[{'applies_to':{'typo':['x']}}, {'preconditions':[{'field':'facts.x','operator':'shell','value':'true'}]},
                 {'required_refs':['missing']},{'path':'../../outside'},{'id':'Bad ID'},
                 {'excludes':[{'when':[],'reason':'no evidence'}]}]
        for change in changes:
            with self.subTest(change=change), self.assertRaises(engine.FormatError):
                engine.validate_catalog(catalog({**entry('test.rule'),**change}))

    def test_commands_are_inert_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            marker=Path(tmp)/'executed'
            e=entry('test.rule',command=f'touch {marker}',preconditions=[{'field':'facts.command','operator':'eq','value':f'touch {marker}'}])
            self.assertEqual(outcome(catalog(e),{'facts':{'command':f'touch {marker}'}}),'matches')
            self.assertFalse(marker.exists())

    def test_digest_and_outside_symlink_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);p=root/'test.md';p.write_text('reference')
            e=entry('test.rule',path='test.md',content_digest='sha256:'+hashlib.sha256(p.read_bytes()).hexdigest())
            engine.verify_files(catalog(e),root)
            p.write_text('tampered')
            with self.assertRaises(engine.FormatError):engine.verify_files(catalog(e),root)
            p.unlink();p.symlink_to(K/'README.md')
            with self.assertRaises(engine.FormatError):engine.verify_files(catalog(e),root)


if __name__=='__main__':unittest.main()
