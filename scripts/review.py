#!/usr/bin/env python3
"""Validate human/agent-observed QA and suggest a repair; does not inspect pixels."""
import argparse,json
DIMS=('product','composition','title','interaction','hierarchy','support','style','finish')
def assess(q):
 issues=[]
 for k in ('product','text','structure'):
  if q.get('gates',{}).get(k)!='pass':issues.append('gate:'+k)
 for k in DIMS:
  row=q.get('dimensions',{}).get(k,{})
  if type(row.get('rating')) is not int or row['rating'] not in (0,1,2) or not row.get('evidence'):issues.append('missing-evidence:'+k)
  elif row['rating']<2:
   issues.append('repair:'+k)
   if not row.get('action'):issues.append('missing-action:'+k)
 if not q.get('text_absent',False):
  for k in ('glyph_beauty','identity','flow','spacing','illustration_fit','composition_role','weight'):
   row=q.get('type_review',{}).get(k,{})
   if type(row.get('rating')) is not int or row['rating'] not in (0,1,2) or not row.get('evidence'):issues.append('type-evidence:'+k)
   elif row['rating']<2:
    issues.append('type-repair:'+k)
    if not row.get('action'):issues.append('type-action:'+k)
 for k in ('concept','selection','relations','type_integration','casting_fit'):
  row=q.get('world_review',{}).get(k,{})
  if type(row.get('rating')) is not int or row['rating'] not in (0,1,2) or not row.get('evidence'):issues.append('world-evidence:'+k)
  elif row['rating']<2:
   issues.append('world-repair:'+k)
   if not row.get('action'):issues.append('world-action:'+k)
 return {'status':'revise' if issues else 'reviewed','issues':issues,'notice':'Recorded observations only; this is not automatic visual verification.'}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('qa');a=p.parse_args();r=assess(json.load(open(a.qa)));print(json.dumps(r,ensure_ascii=False,indent=2));raise SystemExit(1 if r['status']=='revise' else 0)
