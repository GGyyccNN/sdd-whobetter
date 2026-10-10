from pathlib import Path
import base64, csv, html, io, json, math, zipfile
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Rectangle, Patch
import numpy as np

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output'
DATA=json.loads((OUT/'comparison.json').read_text())
S=DATA['summary']; C=DATA['categories']; R=DATA['inventory']
F='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
font_manager.fontManager.addfont(F)
plt.rcParams.update({'font.family':font_manager.FontProperties(fname=F).get_name(), 'axes.unicode_minus':False,
    'font.size':11,'svg.fonttype':'none','pdf.fonttype':42,'figure.facecolor':'#F7F8FC','axes.facecolor':'#F7F8FC'})
COLORS=['#6C7CBE','#2A9D8F','#E8AD43','#477FC1','#D07899','#A18ABD','#8E9AA5']
INK='#202D43'; MUTED='#627187'; GRID='#DBE0EA'
TOOLS=['#477FC1','#2A9D8F','#D89232','#8E75B5','#8E9AA5']

def txt(fig,x,y,t,size=11,color=INK,weight='normal',**kw):
    return fig.text(x,y,t,fontsize=size,color=color,fontweight=weight,**kw)
def clean(ax):
    for s in ax.spines.values():s.set_visible(False)
    ax.tick_params(length=0,labelcolor=MUTED)
def save(fig,name):
    for ext in ['png','svg','pdf']:
        fig.savefig(OUT/f'{name}.{ext}',dpi=180,facecolor=fig.get_facecolor())
    plt.close(fig)

# Slide 1: absolute inventory and composition. NA is never drawn as a zero bar.
fig=plt.figure(figsize=(16,9))
txt(fig,.045,.939,'SDD 工具自身，带来多大的提示词库存？',25,weight='bold')
txt(fig,.045,.895,'公开指令的静态盘点  ·  DeepSeek v4.1 目标估算  ·  未运行项目或模型',12,color=MUTED)
txt(fig,.045,.821,'01  库存总量',16,weight='bold')
txt(fig,.57,.821,'02  功能构成',16,weight='bold')
ax=fig.add_axes([.153,.30,.365,.46]); clean(ax)
ax.set_ylim(-.65,4.65);ax.invert_yaxis();ax.set_xlim(0,335)
ax.set_yticks(range(5));ax.set_yticklabels([s['tool'] for s in S],fontsize=13,color=INK)
ax.set_xticks([0,50,100,150,200,250,300]);ax.set_xlabel('估算 token（k = 千）',color=MUTED,labelpad=12)
ax.xaxis.grid(True,color=GRID,alpha=.75);ax.set_axisbelow(True)
for i,s in enumerate(S):
    if not s['observable']:
        ax.text(7,i,'不可统计 / 未获得内部指令',color=MUTED,fontsize=11,va='center')
        continue
    v=s['estimated_tokens']/1000;lo=s['low_tokens']/1000;hi=s['high_tokens']/1000
    ax.barh(i,v,height=.32,color=TOOLS[i],zorder=3)
    ax.plot([lo,hi],[i+.22]*2,color=MUTED,lw=1.2,zorder=4)
    ax.plot([lo,lo],[i+.17,i+.27],color=MUTED,lw=1.2)
    ax.plot([hi,hi],[i+.17,i+.27],color=MUTED,lw=1.2)
    ax.text(v+4,i-.035,f'≈ {v:.0f}k',fontsize=13,color=INK,weight='bold',va='center')
    ax.text(hi+3,i+.23,f'{lo:.0f}–{hi:.0f}k',fontsize=9,color=MUTED,va='center')
ax2=fig.add_axes([.575,.30,.365,.46]);clean(ax2)
ax2.set_ylim(-.65,4.65);ax2.invert_yaxis();ax2.set_xlim(0,100)
ax2.set_yticks([]);ax2.set_xticks([0,25,50,75,100]);ax2.set_xticklabels(['0%','25%','50%','75%','100%']);ax2.set_xlabel('占该工具估算库存的比例',color=MUTED,labelpad=12)
for i,s in enumerate(S):
    if not s['observable']:
        ax2.add_patch(Rectangle((0,i-.2),100,.4,facecolor='#E9EDF3',edgecolor='#D2D9E4',hatch='////'))
        ax2.text(50,i,'N/A：内部 Specs 指令不可见',ha='center',va='center',color=MUTED,fontsize=11)
        continue
    left=0
    for cat,color in zip(C,COLORS):
        w=100*s['categories'][cat]['estimated_tokens']/s['estimated_tokens']
        ax2.barh(i,w,left=left,height=.42,color=color,edgecolor='#F7F8FC',linewidth=1)
        if w>=6.3: ax2.text(left+w/2,i,f'{w:.0f}%',ha='center',va='center',fontsize=10,color='white' if color!='#E8AD43' else '#3E341F',weight='bold')
        left+=w
fig.legend([Patch(facecolor=c) for c in COLORS],C,loc='lower center',bbox_to_anchor=(.54,.18),ncol=7,frameon=False,fontsize=10,handlelength=1.2,columnspacing=1.45)
txt(fig,.045,.145,'读图提示',11,weight='bold')
txt(fig,.11,.145,'OpenSpec 默认 core 子集约 27.5k；Superpowers 约 40% 属于工具维护。主图仍统一展示所选完整库存。',10.5)
txt(fig,.045,.053,'口径：单套规范来源；含模板与按需参考；排除多平台重复副本、代码、README、项目产物。范围为字符换算的启发式区间，非置信区间。',9,color=MUTED)
txt(fig,.045,.026,'ASCII 字符约 3–5 字符/token，中心按 4；非 ASCII 单列估算。未用 DeepSeek v4.1 tokenizer 校准，不代表单次加载量、累计计费或质量排名。',9,color=MUTED)
txt(fig,.95,.895,'快照 2026-10-10',10,color=MUTED,ha='right')
save(fig,'01_overview')

# Slide 2: category values, exact character sizes, source counts and scope.
fig=plt.figure(figsize=(17,11))
txt(fig,.035,.949,'静态提示词明细：数量、功能与来源',25,weight='bold')
txt(fig,.035,.909,'每格显示「估算 k token / 功能占比」；按文件或配置字段的主要用途归类，非逐句编码。',11.5,color=MUTED)
ax=fig.add_axes([.035,.478,.93,.365]);ax.set_xlim(0,11.85);ax.set_ylim(0,6);ax.axis('off')
widths=[1.58]+[.96]*7+[1.24,1.05,1.23];xs=np.cumsum([0]+widths)
headers=['工具']+C+['总量 / 区间','字符 / 文件','入口 / 版本']
for j,h in enumerate(headers):
    ax.add_patch(Rectangle((xs[j],5),widths[j],1,color='#23344E'))
    ax.text(xs[j]+widths[j]/2,5.5,h,ha='center',va='center',color='white',fontsize=10)
for i,s in enumerate(S):
    y=4-i
    ax.add_patch(Rectangle((0,y),xs[-1],1,color='#FFFFFF' if i%2==0 else '#EDF1F7'))
    ax.text(.08,y+.56,s['tool'],ha='left',va='center',fontsize=12,weight='bold',color=INK)
    for j,cat in enumerate(C,1):
        x=xs[j]+widths[j]/2
        if not s['observable']:
            t='N/A';color=MUTED
        else:
            v=s['categories'][cat]['estimated_tokens']/1000;share=100*v/(s['estimated_tokens']/1000)
            ax.add_patch(Rectangle((xs[j]+.025,y+.075),widths[j]-.05,.85,color=COLORS[j-1],alpha=.12+min(.25,share/100)))
            t=f'≈{v:.1f}k\n{share:.1f}%';color=INK
        ax.text(x,y+.5,t,ha='center',va='center',fontsize=10.5,color=color,linespacing=1.7)
    tail=[f"≈{s['estimated_tokens']/1000:.1f}k\n{s['low_tokens']/1000:.0f}–{s['high_tokens']/1000:.0f}k",f"{s['chars']:,}\n{s['source_files']} 来源文件",f"{s['entrypoints']} 入口\n{s['version']}"] if s['observable'] else ['不可统计','内部指令\n未获得','产品提示词\n不可见']
    for j,t in enumerate(tail,8):ax.text(xs[j]+widths[j]/2,y+.5,t,ha='center',va='center',fontsize=9.5,color=INK if s['observable'] else MUTED,linespacing=1.75)
for x in xs:ax.plot([x,x],[0,6],color='#D6DDE7',lw=.65)
for y in range(7):ax.plot([0,xs[-1]],[y,y],color='#D6DDE7',lw=.65)
txt(fig,.035,.457,'0 表示没有文件被主归类到这一栏，不能据此判断工具缺少该功能。入口 = 所选可调用 skill / slash-command；BMAD 模块记录不算入口。',9,color=MUTED)

txt(fig,.035,.412,'统计范围与主要体量来源',16,weight='bold')
cardx=[.035,.272,.509,.746];cardw=.218
for s,x,col in zip(S[:4],cardx,TOOLS[:4]):
    fig.add_artist(Rectangle((x,.197),cardw,.18,transform=fig.transFigure,facecolor='white',edgecolor=GRID,lw=.7))
    txt(fig,x+.012,.352,s['tool'],13,col,weight='bold')
    scope={'OpenSpec':'12 工作流 + 默认 schema 指令/模板','Spec Kit':'10 核心命令 + 5 文档模板','BMAD Method':'Method + Core Tools；排除 Toolsmith','Superpowers':'15 skills + 按需参考；单套 Codex'}[s['tool']]
    txt(fig,x+.012,.325,scope,8.5,color=MUTED)
    top=sorted(s['modules'].items(),key=lambda kv:kv[1],reverse=True)[:3]
    for k,(m,v) in enumerate(top):
        m=m.removeprefix('bmad-').removeprefix('bmod-')
        txt(fig,x+.012,.295-k*.027,f'{m}   ≈ {v/1000:.1f}k',9.5)
    txt(fig,x+.012,.211,f"全文片段去重后 ≈ {s['whole_text_deduplicated_tokens']/1000:.1f}k",8.5,color=MUTED)
txt(fig,.035,.153,'Kiro Specs',11,weight='bold')
txt(fig,.122,.153,'官方公开仓库声明不包含产品源码；示例 requirements / design / tasks 是输出文档，未冒充内部提示词计入。',10)
txt(fig,.035,.111,'换算与边界',11,weight='bold')
txt(fig,.122,.111,'中心 = ASCII / 4 + 非 ASCII / 1.5；下界 = ASCII / 5 + 非 ASCII / 2；上界 = ASCII / 3 + 非 ASCII。',9.5)
txt(fig,.035,.074,'原始字符数与文件路径可复核；token 是未校准的量级估算。工具内重复文件保留在库存总量中，完整文本片段去重值另列。',9.5,color=MUTED)
txt(fig,.035,.045,'不含项目代码/产出文档、模型系统提示词、工具 schema、请求历史、运行时包装/索引、缓存、子代理重复加载或选装扩展。',9.5,color=MUTED)
txt(fig,.035,.022,'版本：官方默认分支固定 SHA（含 Spec Kit dev 与 BMAD next）；详见 sources_manifest.json 和文件明细。采集日期：2026-10-10。',9,color=MUTED)
save(fig,'02_detail')

# Evidence and presentation notes.
(OUT/'sources_manifest.json').write_text(json.dumps(DATA['sources'],ensure_ascii=False,indent=2),encoding='utf-8')
report=['# SDD 工具静态提示词对比\n',
    '本轮只盘点工具自身的公开文本，不代入项目，不调用模型，不运行 tokenizer，不推算费用。主比较包括 OpenSpec、Spec Kit、BMAD Method、Kiro Specs、Superpowers；GSD 按原计划保留为后续补充样本。\n',
    '## 可直接展示的结论\n',
    '在固定的官方源码快照和所选分发范围内，公开指令库存的中心估算为：Spec Kit 约 **4 万**、OpenSpec 约 **4.9 万**、Superpowers 约 **8.2 万**、BMAD Method 约 **23.1 万 token**。Kiro Specs 内部提示词未获得，保留为 **N/A**。这些是库存体量，**不等于每次任务额外输入、实际运行消耗或结果收益**。\n',
    '推荐讲述：“SDD 工具除了用户需求，还需要一套规则、工作流、模板与参考材料。我们静态盘点的可见库存约为 4 万到 23 万 token 量级；实际使用按需加载，不能把整个库存直接当成每轮账单。”\n',
    '## 总量\n',
    '| 工具 | 精确字符数 | 来源文件 | 入口数 | 中心估算 | 启发式范围 |\n|---|---:|---:|---:|---:|---:|']
for s in S:
    if s['observable']:
        report.append(f"| {s['tool']} | {s['chars']:,} | {s['source_files']} | {s['entrypoints']} | ≈{s['estimated_tokens']/1000:.1f}k | {s['low_tokens']/1000:.0f}–{s['high_tokens']/1000:.0f}k |")
    else:report.append('| Kiro Specs | N/A | N/A | N/A | N/A | N/A |')
report += ['\n## 统计口径\n',
    '- 盘点单套规范来源：技能/命令正文、步骤、agent 会读取的参考材料、空文档模板、配置中的指令字符串。Markdown 的标题、空白、frontmatter 与示例保持原文；换行统一为 LF。',
    '- OpenSpec：已提交的 12 个 `skills/*/SKILL.md`，默认 `spec-driven` schema 的 5 段 instruction 和 4 个模板；排除重复的命令适配器和 TS 源码。默认 core 只有其中 6 个工作流，加上 schema/模板约 **27.5k**。主图展示 12 个工作流的库存，不冒充默认初始化量。',
    '- Spec Kit：`templates/commands/*.md` 的 10 个核心命令和 `templates/*-template.md` 的 5 个模板；不含选装 extensions、presets、非提示词 workflow 编排配置、脚本以及其他 agent 输出副本。',
    '- BMAD：按官方 `bmod-method/bmod.toml` 和 `bmod-core-tools/bmod.toml` 声明的技能，加上这两个模块记录。计入其中 Markdown、CSV 方法库，以及 `customize.toml` 中承载指令的字段；去掉配置注释、路径、空占位、enum 和非指令元数据。`analyze.py` 内 `STRING_KEYS` 给出完整字段白名单。Toolsmith 是独立扩展，本轮排除。',
    '- Superpowers：15 个技能，正文及工作参考/模板；平台参考仅保留 Codex。一并计入 writing-skills 与 diagnosing-superpowers 这两个辅助技能；排除技能开发测试场景、历史创建日志和其他平台参考。工具维护约 **33.0k（40.3%）**；其余库存约 **48.9k**，这同样不是一次执行路径的加载估计。',
    '- Kiro：官方公开仓库 README 声明其为 issue/feedback tracker，产品源码不在这里。仓库内 `.kiro/specs/*` 是具体项目的生成产物，issue 自动化中的分类/回复提示词也是反馈仓库功能，均不属于产品 Specs 内部提示词。未用社区复刻、官方产品文档或泄露提示词填数。',
    '- 每个规范来源文件计一次；同一文件的多个配置字段分别计为片段，来源文件数去重。入口数只计可调用技能/命令正文，不把每个 Markdown 都叫作独立提示词；BMAD 的 2 个 bmod 模块记录不算入口。相同文本出现在不同规范文件时保留在原始库存；另给完整文本片段 SHA256 去重值，未做语义或段落级去重。',
    '- 配置字段与 schema 指令经 TOML/YAML 解析后按原字符串统计；格式化后的 runtime JSON 和 key 包装不在本次文本口径中。分段空白可能因运行时序列化变化。',
    '- 功能按文件/配置字段主要目的人工映射到七类，不逐句拆分复合功能；占比按中心估算 token 计算，不能解释为功能覆盖度或工程价值。来源文件可跨分类，分类文件数不应相加当作总文件数。',
    '\n## DeepSeek v4.1 token 估算\n',
    '本轮没有取得并验证 DeepSeek v4.1 的专用 tokenizer；数字是以该模型为目标的通用字符量级估算，不能称为该模型的实际 token 统计。公开文本超过 99.7% 的字符为 ASCII，以英文 Markdown 为主。',
    '\n设 A = ASCII 字符数，U = 非 ASCII 字符数：\n\n- 中心估算：`A / 4 + U / 1.5`\n- 下界：`A / 5 + U / 2`\n- 上界：`A / 3 + U / 1`\n',
    '这只是选择了一个宽的经验换算范围，**不是统计置信区间，也不是保证覆盖真实 tokenizer 的上下限**。路径、标点、代码示例、Markdown 表格和模型词表可能带来偏差。功能占比也依赖此换算与人工分类。原始字符数可用于后续换一种假设重新估算。',
    '\n## 版本与证据\n',
    '采集日期：2026-10-10。采用官方默认分支的固定提交；版本号只是仓库内声明，**不是声称所有样本都是稳定发布版**。Spec Kit 为 dev，BMAD 为 next。不同版本之间不可直接继承本图数字。\n',
    '| 工具 | 仓库声明版本 | 固定提交 | 提交日期 |\n|---|---|---|---|']
for repo,m in DATA['sources'].items():
    report.append(f"| {m['name']} | {m['declared_version']} | [{m['commit'][:12]}]({m['repository_url']}/tree/{m['commit']}) | {m['commit_date']} |")
report += ['\nKiro 可观测性证据：[官方 README 的 About this repository]('+DATA['sources']['kiro-public']['repository_url']+'/blob/'+DATA['sources']['kiro-public']['commit']+'/README.md)。官方站点 `kiro.dev` 和 `api-docs.deepseek.com` 在当前环境的请求返回代理 403，本轮未以这些页面作正文计量来源；这不影响已取得的源码盘点。',
    '\n## 文件说明\n',
    '- `01_overview.png / .svg / .pdf`：总量和功能占比，适合投屏。',
    '- `02_detail.png / .svg / .pdf`：分类总量、占比、字符数、来源与范围。',
    '- `comparison.html`：无需服务器的离线浏览页，含两张图及可筛选文件/字段明细；来源链接指向固定提交。',
    '- `prompt_inventory.csv`：逐文件/字段的字符、字节、估算区间、分类、SHA256、路径与来源链接。',
    '- `tool_summary.csv / category_summary.csv`：总量/分类汇总；Kiro 留空，不填 0。',
    '- `excluded_files.csv`：未纳入的文本候选文件及范围排除说明。',
    '- `comparison.json / sources_manifest.json`：完整数据、估算假设与固定提交信息。',
    '- `analyze.py / render.py`：统计与出图脚本；它们只处理官方源码文本，不执行所比较工具的 workflow。',
    '- 压缩包内 `sources/` 留存本轮纳入的原始文本和许可证，`output/` 保存成果。解压后在包根目录运行 `python analyze.py`、`python render.py` 可复核总量并出图（需要 PyYAML、NumPy、Matplotlib 和 Noto Sans CJK 字体）；源码裁剪归档模式从 `output/sources_manifest.json` 读取版本，不依赖 Git。完整仓库排除清单保留原采集结果。',
    '\n本次未改变 `sdd-whobetter` 仓库，也未进行项目实验、模型调用或新环境发布。']
(OUT/'README.md').write_text('\n'.join(report)+'\n',encoding='utf-8')

# Standalone interactive evidence page with no external dependencies.
inventory=json.dumps(R,ensure_ascii=False).replace('</','<\\/')
imgs={n:base64.b64encode((OUT/f'{n}.png').read_bytes()).decode() for n in ['01_overview','02_detail']}
page=r'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SDD 静态提示词对比</title>
<style>:root{color-scheme:light}*{box-sizing:border-box}body{margin:0;background:#f5f7fb;color:#20304a;font:15px/1.65 system-ui,"Noto Sans CJK SC",sans-serif}main{max-width:1400px;margin:auto;padding:26px}h1{font-size:29px;margin:0}h2{font-size:21px;margin-top:34px}.muted{color:#657287}a{color:#2861a3}nav{display:flex;gap:20px;position:sticky;top:0;background:#f5f7fb;padding:12px 0;z-index:2}figure{margin:18px 0;background:white;border:1px solid #dce3ee;border-radius:12px;overflow:hidden}img{width:100%;display:block}.card{padding:16px 20px;background:white;border:1px solid #dce3ee;border-radius:10px}.filters{display:flex;gap:12px;flex-wrap:wrap;margin:16px 0}select,input{border:1px solid #bdc9dc;background:white;border-radius:7px;padding:10px;font:inherit}input{min-width:300px;flex:1}.scroll{overflow:auto;border:1px solid #dce3ee;background:white;border-radius:8px;max-height:680px}table{border-collapse:collapse;width:100%;font-size:13px}th{position:sticky;top:0;background:#243650;color:white;text-align:left}th,td{padding:9px 12px;border-bottom:1px solid #e5eaf2}td.num{white-space:nowrap;text-align:right}td.path{max-width:500px;overflow-wrap:anywhere}tr:hover{background:#f0f4fa}button{cursor:pointer;border:1px solid #aebed5;background:#e7eef8;padding:10px 16px;border-radius:7px;font:inherit}details{margin-top:18px}footer{padding:32px 0;color:#657287}.badge{padding:3px 7px;border-radius:5px;background:#e9eef7;white-space:nowrap}@media print{nav,.filters,button{display:none}.scroll{max-height:none}}</style>
<main><h1>SDD 工具：静态提示词库存对比</h1><p class="muted">固定官方源码快照 · 2026-10-10 · 仅静态盘点，不运行项目、模型或 tokenizer</p>
<nav><a href="#overview">概览图</a><a href="#detail">详细图</a><a href="#inventory">文件明细</a><a href="#method">统计口径</a></nav>
<div class="card"><b>怎么解释：</b>这是工具需要维护的规则、流程、模板与参考材料的体量。<b>全部库存 ≠ 单次加载 ≠ 累计计费。</b>Kiro 的产品内部 Specs 指令未获得，因此保留 N/A。token 为未使用 DeepSeek v4.1 tokenizer 校准的字符启发式估算。</div>
<h2 id="overview">概览：总量与功能占比</h2><figure><img alt="SDD 静态提示词库存总量与功能占比" src="data:image/png;base64,OVERVIEW"></figure>
<h2 id="detail">详细：功能分布与来源范围</h2><figure><img alt="SDD 静态提示词分类详细统计" src="data:image/png;base64,DETAIL"></figure>
<h2 id="inventory">可核查的文件 / 配置字段明细</h2><p>点击路径可查看固定提交的原文。排序与筛选只影响当前表格；Kiro 无可比指令，不列伪造的零值。</p>
<div class="filters"><select id="tool"><option value="">全部工具</option></select><select id="category"><option value="">全部功能</option></select><input id="query" placeholder="搜索文件、模块、字段或材料类型"><select id="sort"><option value="tokens">按估算体量降序</option><option value="path">按工具和路径</option></select><button id="download">导出当前明细 CSV</button></div><p id="stats" class="muted"></p>
<div class="scroll"><table><thead><tr><th>工具 / 模块</th><th>功能 / 类型</th><th>来源与字段</th><th>精确字符</th><th>估算 token</th><th>经验区间</th></tr></thead><tbody id="rows"></tbody></table></div>
<h2 id="method">统计口径与来源</h2><div class="card"><p><b>估算假设：</b>ASCII 字符 A，非 ASCII 字符 U。中心 A/4 + U/1.5；下界 A/5 + U/2；上界 A/3 + U。是经验范围，不是置信区间或保证覆盖真实 tokenizer 的边界。原文超过 99.7% 为 ASCII 字符。</p><p><b>材料范围：</b>正文、步骤、按需参考、模板、配置指令字段。只计一套规范来源，排除平台重复副本、README、代码、项目产物、测试场景和未选装扩展。OpenSpec 为全工作流，默认 core 子集约 27.5k；BMAD 为 Method + Core Tools；Superpowers 包括工具维护技能，平台映射选 Codex。</p><p><b>分类：</b>按文件或字段的主要功能，非逐句编码。占比反映文本体量，不能等同于功能覆盖或质量。库内相同文本的不同规范文件仍计入总量，全文片段去重值单列。分类文件数可能交叉。</p><p><b>版本：</b>默认分支固定提交，含 Spec Kit dev、BMAD next；不声称均为稳定发布版。</p>SOURCES</div>
<footer>两张图及 CSV / PDF / SVG 均在同一成果包中。报告 README.md 包含完整解释和演示讲稿；源文本与脚本已留存以便复核。</footer></main>
<script>const data=DATA;const $=id=>document.getElementById(id);const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));for(const t of [...new Set(data.map(r=>r.tool))]){$('tool').append(new Option(t,t))}for(const c of [...new Set(data.map(r=>r.category))]){$('category').append(new Option(c,c))}let shown=[];function render(){const q=$('query').value.toLowerCase();shown=data.filter(r=>(!$('tool').value||r.tool===$('tool').value)&&(!$('category').value||r.category===$('category').value)&&(!q||[r.path,r.locator,r.module,r.kind].join(' ').toLowerCase().includes(q)));shown.sort($('sort').value==='tokens'?(a,b)=>b.estimated_tokens-a.estimated_tokens:(a,b)=>(a.tool+a.path+a.locator).localeCompare(b.tool+b.path+b.locator));$('rows').innerHTML=shown.map(r=>`<tr><td><b>${esc(r.tool)}</b><br>${esc(r.module)}</td><td><span class="badge">${esc(r.category)}</span><br>${esc(r.kind)}</td><td class="path"><a target="_blank" rel="noreferrer" href="${esc(r.source_url)}">${esc(r.path)}</a>${r.locator?'<br><code>'+esc(r.locator)+'</code>':''}${r.duplicate_of?'<br><small class="muted">有全文相同片段，原始库存保留</small>':''}</td><td class="num">${r.chars.toLocaleString()}</td><td class="num">≈${Math.round(r.estimated_tokens).toLocaleString()}</td><td class="num">${Math.round(r.low_tokens).toLocaleString()}–${Math.round(r.high_tokens).toLocaleString()}</td></tr>`).join('');const sum=shown.reduce((t,r)=>t+r.estimated_tokens,0),chars=shown.reduce((t,r)=>t+r.chars,0),files=new Set(shown.map(r=>r.tool+'|'+r.path)).size;$('stats').textContent=`${shown.length} 个文本片段 · ${files} 个来源文件 · ${chars.toLocaleString()} 字符 · 约 ${(sum/1000).toFixed(1)}k token（中心估算）`;}for(const id of ['tool','category','sort','query'])$(id).addEventListener(id==='query'?'input':'change',render);$('download').onclick=()=>{const keys=['tool','module','category','kind','path','locator','chars','estimated_tokens','low_tokens','high_tokens','source_url'];const quote=v=>'"'+String(v??'').replaceAll('"','""')+'"';const text='\uFEFF'+[keys.map(quote).join(','),...shown.map(r=>keys.map(k=>quote(r[k])).join(','))].join('\r\n');const u=URL.createObjectURL(new Blob([text],{type:'text/csv;charset=utf-8'}));const a=document.createElement('a');a.href=u;a.download='sdd-filtered-inventory.csv';a.click();setTimeout(()=>URL.revokeObjectURL(u),1000);};render();</script></html>'''
sources='<ul>'+''.join(f"<li>{html.escape(m['name'])} · {html.escape(m['declared_version'])} · <a href='{m['repository_url']}/tree/{m['commit']}'>{m['commit'][:12]}</a></li>" for m in DATA['sources'].values())+'</ul>'
page=page.replace('OVERVIEW',imgs['01_overview']).replace('DETAIL',imgs['02_detail']).replace('SOURCES',sources).replace('const data=DATA;','const data='+inventory+';')
(OUT/'comparison.html').write_text(page,encoding='utf-8')

# Self-contained deliverable: fixed canonical text corpus + scripts + charts/data.
with zipfile.ZipFile(OUT/'SDD静态提示词对比.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(OUT.iterdir()):
        if p.is_file() and p.suffix!='.zip':z.write(p,'output/'+p.name)
    for n in ['analyze.py','render.py']:z.write(ROOT/n,n)
    z.writestr('打开说明.txt','两张图、离线网页和详细 CSV 均在 output/ 文件夹。\n先打开 output/comparison.html 或查看 output/README.md。\n要复核统计，在包根目录运行 python analyze.py 和 python render.py。\n')
    for repo in sorted(set(r['repository'] for r in R)):
        for path in sorted(set(r['path'] for r in R if r['repository']==repo)):
            z.write(ROOT/'sources'/repo/path,'sources/'+repo+'/'+path)
        license_file=ROOT/'sources'/repo/'LICENSE'
        if license_file.exists():z.write(license_file,'sources/'+repo+'/LICENSE')
    for mod in ['bmod-method','bmod-core-tools']:
        path='skills/'+mod+'/bmod.toml'
        z.write(ROOT/'sources'/'bmad'/path,'sources/bmad/'+path)
    z.write(ROOT/'sources'/'kiro-public'/'README.md','sources/kiro-public/README.md')
print('Rendered charts, offline HTML, report and ZIP.')
