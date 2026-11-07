#!/usr/bin/env python3
"""Find local references or build an unlabeled model-facing sheet. Requires Pillow."""
import argparse,json
from pathlib import Path
from PIL import Image,ImageOps
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--style',required=True);p.add_argument('--axis',choices=['title','line','mass','accent'],required=True);p.add_argument('--out');a=p.parse_args()
rows=[r for r in json.loads((ROOT/'references/detail-index.json').read_text())['assets'] if r['parent']==a.style and r['axis']==a.axis]
if not rows:p.error('no reference for requested style/axis; do not silently borrow another style')
if not a.out:
 print(json.dumps(rows,ensure_ascii=False,indent=2));raise SystemExit
out=Path(a.out)
if out.resolve().is_relative_to((ROOT/'assets').resolve()):p.error('output must not overwrite library assets')
sheet=Image.new('RGB',(1000,600*len(rows)),'white')
for i,r in enumerate(rows):
 im=Image.open(ROOT/r['path']).convert('RGB');im.thumbnail((920,520));sheet.paste(im,((1000-im.width)//2,i*600+(600-im.height)//2))
out.parent.mkdir(parents=True,exist_ok=True);sheet.save(out)
out.with_suffix('.references.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2));print(out)
