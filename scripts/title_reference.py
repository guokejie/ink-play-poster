#!/usr/bin/env python3
"""Build an unlabeled title/glyph/stroke board from this skill's own references.

No target characters or system-font labels are drawn. Region coordinates are
observed Latin specimens, never Chinese glyph templates or final title assets.
"""
import argparse,json
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]

def build(style,out):
 profiles=json.loads((ROOT/'references/typography.json').read_text())['profiles']
 if style not in profiles:raise ValueError('unknown style')
 rows=[x for x in json.loads((ROOT/'references/detail-index.json').read_text())['assets'] if x['parent']==style and x['axis']=='title']
 if not rows:raise ValueError('no title reference')
 out=Path(out)
 if out.suffix.lower()!='.png':raise ValueError('output must be PNG')
 if out.resolve().is_relative_to((ROOT/'assets').resolve()):raise ValueError('do not overwrite library assets')
 im=Image.open(ROOT/rows[0]['path']).convert('RGB')
 board=Image.new('RGB',(1200,1100),'white')
 def fit(image,box):
  image=image.copy();x,y,w,h=box;image.thumbnail((w,h));board.paste(image,(x+(w-image.width)//2,y+(h-image.height)//2))
 fit(im,(40,30,1120,500))
 regions=profiles[style]['specimen_regions']
 for key,box in [('glyph',(40,580,520,470)),('stroke',(640,580,520,470))]:
  region=regions[key]
  if len(region)!=4 or not(0<=region[0]<region[2]<=1 and 0<=region[1]<region[3]<=1):raise ValueError('invalid specimen region')
  crop=im.crop(tuple(round(v*(im.width if i%2==0 else im.height)) for i,v in enumerate(region)))
  # Enlarge actual specimens, not standard-font approximations.
  scale=min(box[2]/crop.width,box[3]/crop.height)
  crop=crop.resize((max(1,round(crop.width*scale)),max(1,round(crop.height*scale))),Image.Resampling.LANCZOS)
  fit(crop,box)
 out.parent.mkdir(parents=True,exist_ok=True);board.save(out)
 out.with_suffix('.references.json').write_text(json.dumps(dict(style=style,source=rows[0],regions=regions,role='top=word group; lower-left=glyph; lower-right=stroke. Reference language only; no target glyphs.',observations=profiles[style]),ensure_ascii=False,indent=2))
 return out
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--style',required=True);p.add_argument('--out',required=True);a=p.parse_args()
 try:print(build(a.style,a.out))
 except ValueError as e:p.error(str(e))
