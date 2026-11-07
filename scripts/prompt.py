#!/usr/bin/env python3
"""Build a model-neutral prompt; no network calls. Python 3 standard library only."""
import argparse,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('brief',nargs='?');p.add_argument('--list',action='store_true');p.add_argument('--out');p.add_argument('--ready',action='store_true');a=p.parse_args()
styles=json.loads((ROOT/'references/styles.json').read_text())['styles'];index={s['id']:s for s in styles}
if a.list:
 for s in styles: print(s['id'],s['name'],','.join(s['tags']))
 raise SystemExit
if not a.brief:p.error('provide brief.json or --list')
b=json.loads(Path(a.brief).read_text());topic=b.get('topic')
if not isinstance(topic,str) or not topic.strip():p.error('topic must be a nonempty string')
texts=b.get('exact_text',[])
if not isinstance(texts,list) or any(not isinstance(t,str) for t in texts):p.error('exact_text must be an array of strings')
ids=b.get('styles',['P08'])
if not isinstance(ids,list) or not 1<=len(ids)<=2 or any(i not in index for i in ids):p.error('styles requires 1–2 valid IDs')
if b.get('mode','integrated') not in ('integrated','art-only'):p.error('mode must be integrated or art-only')
if a.ready:
 from decision import validate
 errors=validate(b)
 if errors:p.error('; '.join(errors))
parts=['原创黑墨手绘海报。主题：'+topic,'画幅：'+b.get('format','3:4 vertical'),'主体/动作：'+b.get('subject','由主题构思一个清楚可辨的原创主体与动作，勿照抄参考角色。'),'受众：'+b.get('audience','一般观众'),'场景：'+b.get('use','数字展示')]
if a.ready:
 selected=next(x for x in b['decision']['candidates'] if x['id']==b['decision']['selected'])
 parts+=['选中构图（不传入落选方案）：',json.dumps(selected,ensure_ascii=False),'选案理由：'+b['decision']['reason'],'产品识别合同：',json.dumps(b['product_contract'],ensure_ascii=False)]
 if a.ready:
  parts+=['主题构思与选角（仅此选案，不强制加入人或动物）：',json.dumps(b['creative_plan'],ensure_ascii=False)]
  world=b['association_plan']
  chosen_world={k:world[k] for k in ('core_feature','concept')}
  chosen_world['elements']=[x for x in world['pool'] if x.get('selected')]
  chosen_world['relations']=world['relations']
  parts+=['产品关联与视觉叙事（只实现筛选后的元素，不能把搭配当配方宣称）：',json.dumps(chosen_world,ensure_ascii=False)]
else:parts+=['诊断草稿：实际生成前需补齐三案决策与产品合同并运行--ready。']
axes=b.get('aux_axes',[])
if len(ids)==2 and (not isinstance(axes,list) or not axes or any(x not in ('palette','typography','line','composition') for x in axes)):
 p.error('two styles require explicit aux_axes: palette, typography, line, composition')
for j,i in enumerate(ids):
 s=index[i]
 parts+= [('主风格' if j==0 else '辅风格：仅允许指定维度，禁止带入其余特征')+': '+i+' '+s['name']]
 if j==0: parts += [s['aesthetic'],s['composition'],s['palette'],s['typography'],s['transfer']]
 else:
  for axis in axes:
   parts += [axis+': '+(s[axis] if axis in s else '仅从局部线条参考提取笔触；不转移主体、姿态、文字与配色。')]
parts+=['融合维度：'+b.get('blend','不融合；如有辅风格，由设计者明确仅借一个维度。'),'新版空间组织：'+b.get('layout','根据当前标题长短与主体动作重组，不照搬原坐标。'),'背景依所选参考组织，不自动留空或铺满；笔触作用于具体结构，密区与缓冲区有主次。']
space_config=json.loads((ROOT/'references/composition.json').read_text())['profiles'][ids[0]]
space=b.get('composition_plan')
if space is not None:
 keys=('reference_evidence','density_map','subject_scale','spatial_relation','layers','support_elements','background','whitespace_purpose')
 if not isinstance(space,dict) or any(not isinstance(space.get(k),str) or not space[k].strip() for k in keys):
  p.error('composition_plan requires nonempty '+','.join(keys))
 parts+=['本次空间、层次与密度方案：',json.dumps(space,ensure_ascii=False)]
else:
 parts+=['空间方案尚待设计：依据主风格实证补齐composition_plan；不得默认大留白居中单品。',json.dumps(space_config,ensure_ascii=False)]
type_config=json.loads((ROOT/'references/typography.json').read_text())['profiles'][ids[0]]
parts+=['所选字体的参考实证（仅迁移所选风格，不复制原文；中文为独立适配）：',json.dumps(type_config,ensure_ascii=False)]
plan=b.get('type_plan')
if plan is not None:
 required=('profile','intent','glyph','rhythm','layout','interaction','hierarchy','legibility','group_outline','stroke_logic','optical_spacing','product_echo','weight_balance')
 if not isinstance(plan,dict) or any(not isinstance(plan.get(k),str) or not plan[k].strip() for k in required):
  p.error('type_plan requires nonempty profile,intent,glyph,rhythm,layout,interaction,hierarchy,legibility')
 parts+=['本次字体与图文创意方案（在画面生成前锁定）：',json.dumps(plan,ensure_ascii=False)]
else:
 parts+=['字体方案尚待设计：根据以下主风格语法补齐type_plan后再实际生成；不可直接沿用顶部统一胖字。',json.dumps(type_config,ensure_ascii=False)]
parts+=['文案与版式执行：只实现exact_text，不再增加副文案。严格落实type_plan.hierarchy中各条信息的相对字号与重量，以及layout/interaction中的分组位置；核心信息先读、必要信息随后。避免辅助句字号相近且等距堆叠、地址与主标题争夺焦点，不能以全体加粗或随机歪排替代尺度与疏密设计。']
parts+=['字体准确还原或已反馈字体呆板时，优先按production.md采用无字底图、三级参考板、独立标题层与合成流程。标题必须落实选定参考的字形与书写特征：依据type_plan.glyph/rhythm/stroke_logic设计具体目标字的骨架、字面收放、内部空间与笔画伸缩；不以标准字加粗糙墨边替代选定骨架；P02/P07允许原参考支持的规整展示字与手写字对比，其余也不强制全部歪扭。不能靠旋转字块冒充手写。文字可读与手写风格成立分别满足。']
parts+=['手绘感必须在去掉纹理后仍由字形骨架、比例、字腔、笔画伸缩与书写节奏成立；不可仅用标准字叠墨迹或旋转。不将不同参考统一成胖字或细字，只执行本案选定的字体语言。先设计标题整组外轮廓、字间负形和重心，再设计各字与笔触；不默认粗重毛笔或机械阶梯排列。字体须保持原文逐字准确；主标题控制骨架、字宽、节奏和与主体的空间关系，非仅加粗糙纹理；事实信息不变形。']
if b.get('mode')=='art-only':parts+=['仅生成插画底图：不出现任何文字、字母、数字、签名或标志。为后期文字预留以下区域：'+b.get('text_zones','严格依据type_plan的图文关系留出区域，不自动留顶部矩形空白')]
else:parts+=['只允许出现以下文字，逐字准确，不翻译、不增删：',json.dumps(texts,ensure_ascii=False),'没有给出的活动时间、地点、优惠和品牌不出现。']
parts+=['避免：照片感、3D、真实光照、立体字、彩虹渐变、矢量般完全光滑的轮廓、原图品牌与签名、无意义堆砌。','用户附加限制：'+b.get('constraints','无')]
out='\n\n'.join(parts)+'\n'
if a.out:Path(a.out).write_text(out)
else:print(out)
