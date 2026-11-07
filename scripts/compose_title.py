#!/usr/bin/env python3
"""Composite generated black lettering while preserving the base outside its ink mask.
Requires Pillow. Never edits input files. Text correctness still needs visual review.
"""
import argparse,json
from pathlib import Path
from PIL import Image,ImageChops

def extract_ink(image, white=245, black=40):
    if not 0 <= black < white <= 255: raise ValueError('require 0 <= black < white <= 255')
    rgba=image.convert('RGBA');gray=rgba.convert('RGB').convert('L')
    # Continuous alpha retains antialiasing and gray pressure; respect original transparency.
    mask=gray.point(lambda x: round(max(0,min(1,(white-x)/(white-black)))*255))
    mask=ImageChops.multiply(mask,rgba.getchannel('A'));box=mask.getbbox()
    if not box: raise ValueError('title contains no visible dark ink')
    ink=Image.new('RGBA',(box[2]-box[0],box[3]-box[1]),'black');ink.putalpha(mask.crop(box))
    return ink

def compose(base,title,x,y,width,white=245,black=40):
    ink=extract_ink(title,white,black)
    if width <= 0: raise ValueError('width must be positive')
    height=max(1,round(ink.height*width/ink.width))
    if x<0 or y<0 or x+width>base.width or y+height>base.height:raise ValueError('title exceeds canvas; change position or width')
    ink=ink.resize((width,height),Image.Resampling.LANCZOS)
    out=base.convert('RGBA').copy();out.alpha_composite(ink,(x,y));return out,(x,y,width,height)

def measure(value,total):return round(float(value[:-1])*total/100) if value.endswith('%') else round(float(value))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for arg in ('base','title','out'):p.add_argument('--'+arg,required=True)
    p.add_argument('--x',default='8%');p.add_argument('--y',default='7%');p.add_argument('--width',default='84%')
    p.add_argument('--white',type=int,default=245);p.add_argument('--black',type=int,default=40)
    a=p.parse_args();out=Path(a.out)
    if out.resolve() in (Path(a.base).resolve(),Path(a.title).resolve()):p.error('output must not overwrite either input')
    if out.suffix.lower()!='.png':p.error('output must be .png to preserve transparency')
    try:
        base=Image.open(a.base);title=Image.open(a.title)
        result,box=compose(base,title,measure(a.x,base.width),measure(a.y,base.height),measure(a.width,base.width),a.white,a.black)
    except ValueError as e:p.error(str(e))
    out.parent.mkdir(parents=True,exist_ok=True);result.save(out)
    manifest={'base':str(Path(a.base).resolve()),'title_layer':str(Path(a.title).resolve()),'placement_xywh':box,'white':a.white,'black':a.black,'text_check':'pending visual review'}
    out.with_suffix('.layers.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    print(out)
if __name__=='__main__':main()
