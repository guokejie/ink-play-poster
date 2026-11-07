"""Deterministic checks for a design packet, not a visual quality oracle."""
DIMS=('identity','reference','hierarchy','interaction','novelty')
def validate(b):
 errors=[]
 d=b.get('decision',{});c=d.get('candidates',[])
 if not isinstance(c,list) or len(c)<3:return ['decision requires at least three candidates']
 fields=('id','family','anchor','reading_path','spatial_relation','reference_basis','risk')
 for x in c:
  if not isinstance(x,dict):return ['candidate must be an object']
  if any(not isinstance(x.get(k),str) or not x[k].strip() for k in fields):errors.append('candidate missing design fields')
  scores=x.get('scores',{})
  if any(type(scores.get(k)) is not int or scores[k] not in (0,1,2) for k in DIMS):errors.append('candidate scores must be integer 0..2')
 if len({x.get('id') for x in c})!=len(c):errors.append('candidate IDs must be unique')
 if len({x.get('family') for x in c})<3:errors.append('need three different composition families')
 for i,x in enumerate(c):
  for y in c[i+1:]:
   if sum(x.get(k)!=y.get(k) for k in ('anchor','reading_path','spatial_relation'))<2:errors.append('candidates must differ in at least two spatial decisions')
 chosen=next((x for x in c if x.get('id')==d.get('selected')),None)
 if not chosen:errors.append('selected must name a candidate')
 elif any(chosen.get('scores',{}).get(k,0)==0 for k in ('identity','reference')):errors.append('selected candidate fails identity/reference gate')
 if not isinstance(d.get('reason'),str) or not d['reason'].strip():errors.append('selection needs reason')
 product=b.get('product_contract',{})
 for k in ('name','silhouette','surface','protect','confusions'):
  if not isinstance(product.get(k),str) or not product[k].strip():errors.append('product_contract missing '+k)
 if not b.get('composition_plan'):errors.append('composition_plan required')
 if not (b.get('mode')=='art-only' and b.get('exact_text')==[]) and not b.get('type_plan'):errors.append('type_plan required')
 if not (b.get('mode')=='art-only' and b.get('exact_text')==[]):
  t=b.get('type_plan',{})
  for k in ('group_outline','stroke_logic','optical_spacing','product_echo','weight_balance'):
   if not isinstance(t,dict) or not isinstance(t.get(k),str) or not t[k].strip():errors.append('type_plan missing '+k)
 creative=b.get('creative_plan',{})
 for k in ('theme_reading','metaphor','casting','cohesion','restraint'):
  if not isinstance(creative.get(k),str) or not creative[k].strip():errors.append('creative_plan missing '+k)
 a=b.get('association_plan',{})
 for k in ('core_feature','concept','pruned_reason'):
  if not isinstance(a.get(k),str) or not a[k].strip():errors.append('association_plan missing '+k)
 pool=a.get('pool',[]);rel=a.get('relations',[])
 if not isinstance(pool,list) or not isinstance(rel,list):return errors+['association pool/relations must be arrays']
 ids={'hero','title'};selected=[]
 for x in pool:
  if not isinstance(x,dict):return errors+['association entry must be object']
  if not isinstance(x.get('id'),str) or x['id'] in ids:errors.append('association id missing/duplicate')
  ids.add(x.get('id'))
  if x.get('category') not in ('ingredient','form','prop','motion','graphic','information','human','animal','anthropomorphic','scene'):errors.append('invalid association category')
  if x.get('basis') not in ('user-supplied','source-observed','generic-serving','visual-only','unverified'):errors.append('invalid association basis')
  if type(x.get('selected')) is not bool:errors.append('association selected must be boolean')
  if x.get('selected'):
   selected.append(x)
   if x.get('basis')=='unverified':errors.append('unverified selected ingredient/claim')
   for k in ('name','relevance','role'):
    if not isinstance(x.get(k),str) or not x[k].strip():errors.append('selected association missing '+k)
 active={'hero','title'}|{x.get('id') for x in selected};edges=[]
 for x in rel:
  if not isinstance(x,dict):errors.append('relation must be object');continue
  if x.get('from') not in active or x.get('to') not in active:errors.append('relation uses unselected/unknown node')
  if not x.get('verb') or not x.get('effect'):errors.append('relation needs verb/effect')
  edges.append((x.get('from'),x.get('to')))
 connected={'hero','title'}
 for _ in range(len(active)):
  for u,v in edges:
   if u in connected:connected.add(v)
   if v in connected:connected.add(u)
 if any(x['id'] not in connected for x in selected):errors.append('selected association disconnected from hero/title')
 if selected and not any('hero' in (u,v) and ({u,v}-{'hero','title'}) for u,v in edges):errors.append('need direct product-support relation')
 return errors
