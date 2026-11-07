import unittest,json,sys,subprocess,copy,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from decision import validate
from review import assess

def packet():
 candidates=[]
 for i in range(3):
  x={k:f'{k}-{i}' for k in ('id','family','anchor','reading_path','spatial_relation','reference_basis','risk')};x['scores']={k:2 for k in ('identity','reference','hierarchy','interaction','novelty')};candidates.append(x)
 return {'creative_plan':{k:'主题适配，选择静物' for k in ('theme_reading','metaphor','casting','cohesion','restraint')},'association_plan':{'core_feature':'圆拱','concept':'单品识别','pruned_reason':'此测试只验证既有单品请求','pool':[],'relations':[]},'topic':'测试','styles':['P04'],'exact_text':['测试'],'decision':{'candidates':candidates,'selected':'id-1','reason':'主题适配'},'product_contract':{k:'可识别' for k in ('name','silhouette','surface','protect','confusions')},'composition_plan':{k:'空间关系' for k in ('reference_evidence','density_map','subject_scale','spatial_relation','layers','support_elements','background','whitespace_purpose')},'type_plan':{k:'文字关系' for k in ('profile','intent','glyph','rhythm','layout','interaction','hierarchy','legibility','group_outline','stroke_logic','optical_spacing','product_echo','weight_balance')}}
class Decision(unittest.TestCase):
 def test_rejects_cosmetic_variants(self):
  b=packet();self.assertEqual(validate(b),[])
  b['decision']['candidates'][1]['family']=b['decision']['candidates'][0]['family'];self.assertTrue(validate(b))
 def test_identity_gate(self):
  b=packet();b['decision']['candidates'][1]['scores']['identity']=0;self.assertTrue(validate(b))
 def test_selected_only(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'b.json';b=packet();b['decision']['candidates'][0]['risk']='REJECTED_SENTINEL';b['decision']['candidates'][1]['risk']='SELECTED_SENTINEL';p.write_text(json.dumps(b))
   run=subprocess.run([sys.executable,str(ROOT/'scripts/prompt.py'),str(p),'--ready'],capture_output=True,text=True)
   self.assertEqual(run.returncode,0,run.stderr);self.assertIn('SELECTED_SENTINEL',run.stdout);self.assertNotIn('REJECTED_SENTINEL',run.stdout)
 def test_qa_gate_not_average(self):
  q={'gates':{'product':'pass','text':'unknown','structure':'pass'},'dimensions':{k:{'rating':2,'evidence':'已看图'} for k in ('product','composition','title','interaction','hierarchy','support','style','finish')}}
  q['world_review']={k:{'rating':2,'evidence':'已看图检查关系'} for k in ('concept','selection','relations','type_integration','casting_fit')};q['type_review']={k:{'rating':2,'evidence':'字腔与轮廓已检查'} for k in ('glyph_beauty','identity','flow','spacing','illustration_fit','composition_role','weight')};self.assertEqual(assess(q)['status'],'revise');q['gates']['text']='pass';self.assertEqual(assess(q)['status'],'reviewed');q['dimensions']['title']['rating']=1;self.assertEqual(assess(q)['status'],'revise')

class Associations(unittest.TestCase):
 def test_unverified_and_disconnected(self):
  b=packet();x={'id':'butter','category':'ingredient','name':'黄油','basis':'unverified','selected':True,'role':'夹入','relevance':'搭配'};b['association_plan']['pool']=[x]
  self.assertIn('unverified selected ingredient/claim',validate(b))
  x['basis']='generic-serving';self.assertIn('selected association disconnected from hero/title',validate(b))
  b['association_plan']['relations']=[{'from':'butter','to':'hero','verb':'夹入','effect':'呈现吃法'}];self.assertEqual(validate(b),[])
 def test_only_selected_world_in_prompt(self):
  b=packet();a=b['association_plan'];a['pool']=[{'id':'knife','category':'prop','name':'KNIFE_SELECTED','basis':'generic-serving','selected':True,'role':'切开','relevance':'动作'},{'id':'fruit','category':'ingredient','name':'FRUIT_REJECTED','basis':'unverified','selected':False,'role':'无','relevance':'不明'}];a['relations']=[{'from':'knife','to':'hero','verb':'切开','effect':'显示内部'}]
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'b.json';p.write_text(json.dumps(b));run=subprocess.run([sys.executable,str(ROOT/'scripts/prompt.py'),str(p),'--ready'],capture_output=True,text=True);self.assertEqual(run.returncode,0,run.stderr);self.assertIn('KNIFE_SELECTED',run.stdout);self.assertNotIn('FRUIT_REJECTED',run.stdout)
 def test_type_review_required(self):
  q={'gates':{k:'pass' for k in ('product','text','structure')},'dimensions':{k:{'rating':2,'evidence':'观察'} for k in ('product','composition','title','interaction','hierarchy','support','style','finish')},'world_review':{k:{'rating':2,'evidence':'关系'} for k in ('concept','selection','relations','type_integration','casting_fit')}}
  self.assertIn('type-evidence:weight',assess(q)['issues'])

class Casting(unittest.TestCase):
 def test_character_is_optional_and_connected(self):
  b=packet();self.assertEqual(validate(b),[])
  b['creative_plan']['casting']='原创水獭推书，动作解释阅读主题'
  b['association_plan']['pool']=[{'id':'otter','category':'animal','name':'原创水獭','basis':'visual-only','selected':True,'role':'推开大书','relevance':'把阅读比作进入新世界'}]
  b['association_plan']['relations']=[{'from':'otter','to':'hero','verb':'推开','effect':'建立阅读动作'}]
  self.assertEqual(validate(b),[])
  b['association_plan']['relations']=[];self.assertIn('selected association disconnected from hero/title',validate(b))
 def test_creative_plan_cannot_be_omitted(self):
  b=packet();del b['creative_plan'];self.assertIn('creative_plan missing casting',validate(b))

if __name__=='__main__':unittest.main()
