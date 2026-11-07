import unittest,sys,json,subprocess,tempfile
from pathlib import Path
from PIL import Image,ImageChops
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from compose_title import extract_ink,compose
class Tools(unittest.TestCase):
 def test_alpha(self):
  im=Image.new('RGBA',(3,1));im.putdata([(0,0,0,0),(140,140,140,255),(0,0,0,128)])
  ink=extract_ink(im);self.assertEqual(ink.size,(2,1));self.assertTrue(0<ink.getpixel((0,0))[3]<255);self.assertEqual(ink.getpixel((1,0))[3],128)
 def test_preserves_base(self):
  base=Image.new('RGBA',(100,100),(120,160,170,255));title=Image.new('RGB',(5,5),'black')
  out,box=compose(base,title,20,30,10);self.assertIsNone(ImageChops.difference(base.crop((0,0,100,30)),out.crop((0,0,100,30))).getbbox());self.assertEqual(out.getpixel((25,35)),(0,0,0,255));self.assertEqual(base.getpixel((25,35)),(120,160,170,255))
 def test_rejects(self):
  with self.assertRaises(ValueError):extract_ink(Image.new('RGB',(5,5),'white'))
  with self.assertRaises(ValueError):compose(Image.new('RGB',(10,10)),Image.new('RGB',(5,5)),8,0,5)
 def test_index(self):
  rows=json.loads((ROOT/'references/detail-index.json').read_text())['assets'];self.assertEqual(len({r['id'] for r in rows}),len(rows))
  for r in rows:
   im=Image.open(ROOT/r['path']);self.assertGreater(min(im.size),0);im.close();self.assertTrue((ROOT/f"assets/posters/{r['parent']}.png").exists())
 def test_aux_scope(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'brief.json';p.write_text(json.dumps({'topic':'花市','exact_text':['花市','09:30—17:00'],'styles':['P06','P02'],'aux_axes':['palette']}))
   run=subprocess.run([sys.executable,str(ROOT/'scripts/prompt.py'),str(p)],capture_output=True,text=True);self.assertEqual(run.returncode,0,run.stderr)
   aux=run.stdout.split('辅风格：')[1];self.assertNotIn('弧形标题',aux);self.assertNotIn('衬线大写',aux);self.assertIn('09:30—17:00',run.stdout)
class Typography(unittest.TestCase):
 def test_dynamic_defaults(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'brief.json';outputs=[]
   for sid in ('P05','P08','P09'):
    p.write_text(json.dumps({'topic':'可颂','exact_text':['可颂'],'styles':[sid]}))
    run=subprocess.run([sys.executable,str(ROOT/'scripts/prompt.py'),str(p)],capture_output=True,text=True)
    self.assertEqual(run.returncode,0,run.stderr);outputs.append(run.stdout)
   self.assertIn('轻干印',outputs[0]);self.assertIn('弹性',outputs[1]);self.assertIn('连笔',outputs[2])
 def test_plan_and_invalid_plan(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'brief.json';brief={'topic':'可颂','exact_text':['CROISSANT','可颂'],'styles':['P08'],'type_plan':{'profile':'elastic-display'}}
   p.write_text(json.dumps(brief));run=subprocess.run([sys.executable,str(ROOT/'scripts/prompt.py'),str(p)],capture_output=True,text=True);self.assertNotEqual(run.returncode,0)
   plan={k:'沿轮廓组织' for k in ('profile','intent','glyph','rhythm','layout','interaction','hierarchy','legibility','group_outline','stroke_logic','optical_spacing','product_echo','weight_balance')};brief['type_plan']=plan
   p.write_text(json.dumps(brief));run=subprocess.run([sys.executable,str(ROOT/'scripts/prompt.py'),str(p)],capture_output=True,text=True);self.assertEqual(run.returncode,0,run.stderr);self.assertIn('沿轮廓组织',run.stdout);self.assertIn('CROISSANT',run.stdout)
class Composition(unittest.TestCase):
 def test_space_plan(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'brief.json';b={'topic':'可颂','styles':['P03'],'composition_plan':{'layers':'重叠'}}
   p.write_text(json.dumps(b));run=subprocess.run([sys.executable,str(ROOT/'scripts/prompt.py'),str(p)],capture_output=True,text=True);self.assertNotEqual(run.returncode,0)
   b['composition_plan']={k:'大主体与手臂互叠，背景桌线被遮挡' for k in ('reference_evidence','density_map','subject_scale','spatial_relation','layers','support_elements','background','whitespace_purpose')}
   p.write_text(json.dumps(b));run=subprocess.run([sys.executable,str(ROOT/'scripts/prompt.py'),str(p)],capture_output=True,text=True);self.assertEqual(run.returncode,0,run.stderr);self.assertIn('背景桌线被遮挡',run.stdout)
if __name__=='__main__':unittest.main()
