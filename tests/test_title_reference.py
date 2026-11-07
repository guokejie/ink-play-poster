import json,sys,tempfile,unittest
from pathlib import Path
from PIL import Image,ImageChops
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from title_reference import build
class TitleBoard(unittest.TestCase):
 def test_all_styles_have_visible_three_level_specimens(self):
  with tempfile.TemporaryDirectory() as d:
   for i in range(1,10):
    sid=f'P{i:02d}';out=build(sid,Path(d)/f'{sid}.png')
    with Image.open(out) as im:
     self.assertEqual(im.size,(1200,1100))
     for box in [(40,30,1160,530),(40,580,560,1050),(640,580,1160,1050)]:
      crop=im.crop(box);self.assertIsNotNone(ImageChops.difference(crop,Image.new('RGB',crop.size,'white')).getbbox())
    record=json.loads(out.with_suffix('.references.json').read_text())
    self.assertEqual(record['style'],sid)
    self.assertTrue((ROOT/record['source']['path']).exists())
 def test_reject_library_overwrite_and_unknown_style(self):
  with self.assertRaises(ValueError):build('P04',ROOT/'assets/details/P04-title.png')
  with self.assertRaises(ValueError):build('P99',Path('/tmp/not-written.png'))
if __name__=='__main__':unittest.main()
