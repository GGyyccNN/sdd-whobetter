from pathlib import Path
import collections, csv, hashlib, json, re, subprocess, tomllib
import yaml

ROOT = Path(__file__).resolve().parent
SRC = ROOT / 'sources'
OUT = ROOT / 'output'
OUT.mkdir(exist_ok=True)
CATS = ['引导与角色', '需求与规格', '设计与规划', '执行与编排', '验证与调试', '同步与收尾', '工具维护']
NAMES = {'openspec':'OpenSpec', 'spec-kit':'Spec Kit', 'bmad':'BMAD Method', 'superpowers':'Superpowers'}
URLS = {'openspec':'https://github.com/Fission-AI/OpenSpec', 'spec-kit':'https://github.com/github/spec-kit', 'bmad':'https://github.com/bmad-code-org/BMAD-METHOD', 'superpowers':'https://github.com/obra/superpowers'}
rows, excluded = [], []
def add(tool, path, text=None, *, category, kind, module, locator='', scope='完整库存'):
    p=SRC/tool/path
    text = p.read_text(encoding='utf-8') if text is None else text
    text = text.replace('\r\n','\n').replace('\r','\n')
    if not text.strip(): return
    asc=sum(ord(c)<128 for c in text); other=len(text)-asc
    rows.append(dict(tool=NAMES[tool], repository=tool, path=path, locator=locator,
        category=category, kind=kind, module=module, scope=scope,
        chars=len(text), ascii_chars=asc, nonascii_chars=other, utf8_bytes=len(text.encode()),
        estimated_tokens=asc/4+other/1.5,
        low_tokens=asc/5+other/2, high_tokens=asc/3+other,
        sha256=hashlib.sha256(text.encode()).hexdigest()))

# OpenSpec: committed skills.sh canonical export, not duplicate adapter variants.
op_map={'explore':2,'propose':1,'new-change':0,'continue-change':2,'ff-change':2,
        'apply-change':3,'update-change':1,'sync-specs':5,'archive-change':5,
        'bulk-archive-change':5,'verify-change':4,'onboard':0}
core={'explore','propose','apply-change','update-change','sync-specs','archive-change'}
for p in sorted((SRC/'openspec'/'skills').glob('*/SKILL.md')):
    name=p.parent.name.removeprefix('openspec-')
    add('openspec',str(p.relative_to(SRC/'openspec')),category=CATS[op_map[name]],kind='技能正文',module=name,scope='默认 core' if name in core else '扩展工作流')
schema_path='schemas/spec-driven/schema.yaml'
schema=yaml.safe_load((SRC/'openspec'/schema_path).read_text())
for art in schema['artifacts']:
    cat=CATS[1 if art['id'] in ['proposal','specs'] else 2]
    add('openspec',schema_path,art['instruction'],category=cat,kind='动态指令',module='schema/'+art['id'],locator=f"artifacts[id={art['id']}].instruction",scope='默认 core')
    path='schemas/spec-driven/templates/'+art['template']
    add('openspec',path,category=cat,kind='文档模板',module='schema/'+art['id'],scope='默认 core')
add('openspec',schema_path,schema['apply']['instruction'],category=CATS[3],kind='动态指令',module='schema/apply',locator='apply.instruction',scope='默认 core')

# Spec Kit: the bundled core pack. Optional extensions/presets excluded.
sk_map={'specify':1,'clarify':1,'constitution':0,'plan':2,'tasks':2,'implement':3,
        'analyze':4,'checklist':4,'converge':4,'taskstoissues':3}
for p in sorted((SRC/'spec-kit'/'templates'/'commands').glob('*.md')):
    add('spec-kit',str(p.relative_to(SRC/'spec-kit')),category=CATS[sk_map[p.stem]],kind='命令正文',module=p.stem)
for p in sorted((SRC/'spec-kit'/'templates').glob('*.md')):
    cat={'constitution':0,'spec':1,'plan':2,'tasks':2,'checklist':4}[p.stem.removesuffix('-template')]
    add('spec-kit',str(p.relative_to(SRC/'spec-kit')),category=CATS[cat],kind='文档模板',module=p.stem)

# BMAD: official Method + Core Tools, omitting the separate Toolsmith module.
bbase=SRC/'bmad'/'skills'
bskills=set()
for mod in ['bmod-method','bmod-core-tools']:
    bskills.add(mod)
    bskills.update(tomllib.loads((bbase/mod/'bmod.toml').read_text())['bmod']['skills'])
bmap={
    'bmad':0,'bmod-method':0,'bmod-core-tools':0,
    'bmad-advanced-elicitation':1,'bmad-brainstorming':1,'bmad-forge-idea':1,
    'bmad-deep-recon':1,'bmad-prd':1,'bmad-prfaq':1,'bmad-product-brief':1,'bmad-spec':1,
    'bmad-architecture':2,'bmad-ux':2,'bmad-ticket':2,
    'bmad-build':3,'bmad-build-auto':3,'bmad-party-mode':3,
    'bmad-code-review':4,'bmad-review':4,'bmad-qa-generate-e2e-tests':4,'bmad-walkthrough':4,
    'bmad-correct-course':5,'bmad-retrospective':5,'bmad-project-context':0,'bmad-customize':6,
}
for n in bskills:
    if n.startswith('bmad-agent-'): bmap[n]=0

def bcat(module, rel):
    cat=bmap[module]
    if module in ['bmad-build','bmad-build-auto']:
        if 'review' in rel or 'claims-check' in rel or 'deletion-check' in rel: cat=4
        elif 'step-02' in rel or 'plan-template' in rel: cat=2
        elif 'step-01' in rel: cat=1
        elif 'step-05' in rel: cat=5
    elif module=='bmad':
        if rel in ['references/setup.md','references/migrate.md']: cat=6
    elif module=='bmad-ticket':
        if 'validate' in rel:cat=4
        elif 'store-setup' in rel:cat=6
    elif module in ['bmad-prd','bmad-ux','bmad-architecture'] and ('validat' in rel or 'reviewer' in rel):cat=4
    elif module.startswith('bmod-') and rel!='SKILL.md':
        stem=Path(rel).stem
        if stem in ['analysis-skills','research']:cat=1
        elif stem in ['planning-skills','ticketing-and-epics','prototyping']:cat=2
        elif stem in ['implementation-skills','unattended-builds','party-mode']:cat=3
        elif stem in ['validation-skills','review-choices']:cat=4
        elif stem=='artifact-lifetime':cat=5
        elif stem in ['customization','modules','ticketing-setup']:cat=6
    return CATS[cat]

STRING_KEYS={'role','identity','communication_style','principles','persona','scene','prompt',
             'description','title','capabilities','instruction','when','route_selection',
             'implementation_handoff','design_handoffs','finalize_reviewers','on_complete',
             'activation_steps_prepend','activation_steps_append','persistent_facts',
             'preferences','open_plan'}
def strings(obj, parts=()):
    if isinstance(obj,dict):
        for k,v in obj.items():yield from strings(v,parts+(k,))
    elif isinstance(obj,list):
        for i,v in enumerate(obj):yield from strings(v,parts+(str(i),))
    elif isinstance(obj,str) and obj.strip(): yield parts,obj

for module in sorted(bskills):
    base=bbase/module
    for p in sorted(base.rglob('*')):
        if not p.is_file() or 'scripts' in p.relative_to(base).parts or 'tests' in p.relative_to(base).parts: continue
        rel=str(p.relative_to(base)); path=str(p.relative_to(SRC/'bmad'))
        if p.suffix in ['.md','.csv']:
            kind='技能正文' if p.name=='SKILL.md' else ('参考方法库' if p.suffix=='.csv' else ('文档模板' if 'assets' in p.parts or 'template' in p.stem else '步骤与参考'))
            add('bmad',path,category=bcat(module,rel),kind=kind,module=module,scope='Method + Core Tools')
        elif p.name=='customize.toml':
            data=tomllib.loads(p.read_text())
            for parts,val in strings(data):
                key=next((k for k in reversed(parts) if not k.isdigit()),'')
                if key not in STRING_KEYS:continue
                cat=bcat(module,rel)
                if any('lens' in part or 'reviewer' in part for part in parts):cat=CATS[4]
                elif key in ['persona','role','identity','communication_style','principles','title','capabilities']:cat=CATS[0]
                elif key in ['implementation_handoff','route_selection','scene']:cat=CATS[3]
                add('bmad',path,val,category=cat,kind='配置指令字段',module=module,locator='.'.join(parts),scope='Method + Core Tools')

# Superpowers: complete skill library + agent-read references, one Codex tool mapping.
sp_map={'using-superpowers':0,'brainstorming':1,'writing-plans':2,'executing-plans':3,
        'subagent-driven-development':3,'dispatching-parallel-agents':3,'using-git-worktrees':3,
        'test-driven-development':4,'systematic-debugging':4,'requesting-code-review':4,
        'receiving-code-review':4,'verification-before-completion':4,
        'finishing-a-development-branch':5,'writing-skills':6,'diagnosing-superpowers':6}
sp_skip={'CREATION-LOG.md','test-pressure-1.md','test-pressure-2.md','test-pressure-3.md','test-academic.md'}
for p in sorted((SRC/'superpowers'/'skills').rglob('*.md')):
    rel=p.relative_to(SRC/'superpowers'); module=rel.parts[1]
    if p.name in sp_skip or 'examples' in rel.parts:continue
    if module=='using-superpowers' and 'references' in rel.parts and p.name!='codex-tools.md':continue
    cat=CATS[sp_map[module]]
    if module=='subagent-driven-development' and p.name in ['task-reviewer-prompt.md','re-review-prompt.md']:cat=CATS[4]
    kind='技能正文' if p.name=='SKILL.md' else ('文档模板' if 'templates' in rel.parts else '步骤与参考')
    add('superpowers',str(rel),category=cat,kind=kind,module=module,scope='全技能库 / Codex 参考')

# Per-tool whole-text duplicates are reported separately, not silently dropped.
summary=[]
meta={}
for repo,name in NAMES.items():
    p=SRC/repo
    if (p/'.git').exists():
        sha=subprocess.check_output(['git','-C',str(p),'rev-parse','HEAD'],text=True).strip()
        date=subprocess.check_output(['git','-C',str(p),'log','-1','--format=%cs'],text=True).strip()
        branch=subprocess.check_output(['git','-C',str(p),'branch','--show-current'],text=True).strip()
    else:
        archived=json.loads((OUT/'sources_manifest.json').read_text())[repo]
        sha,date,branch=archived['commit'],archived['commit_date'],archived['branch']
    version={'openspec':'1.14.1','spec-kit':'1.1.4.dev0','bmad':'6.13.0-next','superpowers':'7.0.0'}[repo]
    meta[repo]={'name':name,'repository_url':URLS[repo],'commit':sha,'commit_date':date,'branch':branch,'declared_version':version,'collected_date':'2026-10-10'}
    selected=[r for r in rows if r['repository']==repo]
    seen=set(); unique=[]
    for r in selected:
        r['duplicate_of']=''
        if r['sha256'] in seen:
            first=next(x for x in unique if x['sha256']==r['sha256'])
            r['duplicate_of']=first['path']+'#'+first['locator']
        else:seen.add(r['sha256']);unique.append(r)
        r['source_url']=URLS[repo]+'/blob/'+sha+'/'+r['path']
    measured=True
    s=dict(tool=name,repository=repo,observable=measured,source_files=len(set(r['path'] for r in selected)) if measured else None,
        fragments=len(selected) if measured else None,
        entrypoints=sum(r['kind'] in ['技能正文','命令正文'] and not r['module'].startswith('bmod-') for r in selected) if measured else None,
        version=version,commit=sha)
    for key in ['chars','utf8_bytes','ascii_chars','nonascii_chars','estimated_tokens','low_tokens','high_tokens']:
        s[key]=sum(r[key] for r in selected) if measured else None
    s['whole_text_deduplicated_tokens']=sum(r['estimated_tokens'] for r in unique) if measured else None
    s['categories']={cat:dict(estimated_tokens=sum(r['estimated_tokens'] for r in selected if r['category']==cat),chars=sum(r['chars'] for r in selected if r['category']==cat),source_files=len(set(r['path'] for r in selected if r['category']==cat))) for cat in CATS} if measured else None
    s['modules']={m:sum(r['estimated_tokens'] for r in selected if r['module']==m) for m in sorted(set(r['module'] for r in selected))} if measured else None
    summary.append(s)
    included_paths={r['path'] for r in selected}
    for f in sorted(p.rglob('*')):
        if not f.is_file() or '.git' in f.parts or f.suffix not in ['.md','.csv','.toml','.yaml','.yml','.txt','.xml','.json']:continue
        path=str(f.relative_to(p))
        if path in included_paths:continue
        reason='非提示词源：代码、文档、元数据、测试或非所选分发范围'
        if repo=='bmad' and path.startswith(('skills/bmad-toolsmith/','skills/bmad-eval/','skills/bmod-toolsmith/')):reason='独立 Toolsmith 扩展模块，不属于 Method + Core Tools'
        elif repo=='superpowers' and 'using-superpowers/references/' in path:reason='其他平台适配参考；本轮只选 Codex 一套'
        elif repo=='superpowers' and ('examples/' in path or f.name in sp_skip):reason='技能开发测试样例/历史记录，不是 agent 工作指令'
        excluded.append({'tool':name,'path':path,'reason':reason})

def write_csv(name, data):
    with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
write_csv('prompt_inventory.csv',rows)
if all((SRC/repo/'.git').exists() for repo in NAMES):
    write_csv('excluded_files.csv',excluded)
elif (OUT/'excluded_files.csv').exists():
    with (OUT/'excluded_files.csv').open(encoding='utf-8-sig',newline='') as f:
        retained=[r for r in csv.DictReader(f) if r['tool'] in NAMES.values()]
    if retained:
        write_csv('excluded_files.csv',retained)
write_csv('tool_summary.csv',[{k:v for k,v in s.items() if k not in ['categories','modules']} for s in summary])
cat_rows=[]
for s in summary:
    for cat in CATS:
        v=s['categories'][cat] if s['observable'] else None
        cat_rows.append({'tool':s['tool'],'category':cat,'chars':v['chars'] if v else None,'estimated_tokens':v['estimated_tokens'] if v else None,'share':v['estimated_tokens']/s['estimated_tokens'] if v else None,'source_files':v['source_files'] if v else None})
write_csv('category_summary.csv',cat_rows)
(OUT/'comparison.json').write_text(json.dumps({'method':{'scope':'公开规范来源文件的静态库存；包含按需材料和模板；不等于单次加载或计费 token','model_target':'DeepSeek v4.1（字符启发式，未用该模型 tokenizer 校准）','estimate':'ASCII/4 + non-ASCII/1.5','low':'ASCII/5 + non-ASCII/2','high':'ASCII/3 + non-ASCII','categorization':'文件或配置字段按主要功能人工映射；非逐句分类','date':'2026-10-10'},'categories':CATS,'sources':meta,'summary':summary,'inventory':rows},ensure_ascii=False,indent=2),encoding='utf-8')
for s in summary:
    print(s['tool'],s['chars'],s['source_files'],s['entrypoints'],None if not s['observable'] else round(s['estimated_tokens']/1000,1),None if not s['observable'] else [round(s[k]/1000,1) for k in ['low_tokens','high_tokens']], 'unique',None if not s['observable'] else round(s['whole_text_deduplicated_tokens']/1000,1))
