# SDD 工具静态提示词对比

本轮只盘点工具自身的公开文本，不代入项目，不调用模型，不运行 tokenizer，不推算费用。主比较包括 OpenSpec、Spec Kit、BMAD Method、Superpowers；GSD 按原计划保留为后续补充样本。

## 主要结果

在固定的官方源码快照和所选分发范围内，公开指令库存的中心估算为：Spec Kit 约 **4 万**、OpenSpec 约 **4.9 万**、Superpowers 约 **8.2 万**、BMAD Method 约 **23.1 万 token**。这些是库存体量，**不等于每次任务额外输入、实际运行消耗或结果收益**。

## 总量

| 工具 | 精确字符数 | 来源文件 | 入口数 | 中心估算 | 启发式范围 |
|---|---:|---:|---:|---:|---:|
| OpenSpec | 195,613 | 17 | 12 | ≈49.0k | 39–65k |
| Spec Kit | 157,715 | 15 | 10 | ≈39.5k | 32–53k |
| BMAD Method | 919,741 | 196 | 28 | ≈230.9k | 185–308k |
| Superpowers | 326,354 | 48 | 15 | ≈81.9k | 65–109k |

## 统计口径

- 盘点单套规范来源：技能/命令正文、步骤、agent 会读取的参考材料、空文档模板、配置中的指令字符串。Markdown 的标题、空白、frontmatter 与示例保持原文；换行统一为 LF。
- OpenSpec：已提交的 12 个 `skills/*/SKILL.md`，默认 `spec-driven` schema 的 5 段 instruction 和 4 个模板；排除重复的命令适配器和 TS 源码。默认 core 只有其中 6 个工作流，加上 schema/模板约 **27.5k**。主图展示 12 个工作流的库存，不冒充默认初始化量。
- Spec Kit：`templates/commands/*.md` 的 10 个核心命令和 `templates/*-template.md` 的 5 个模板；不含选装 extensions、presets、非提示词 workflow 编排配置、脚本以及其他 agent 输出副本。
- BMAD：按官方 `bmod-method/bmod.toml` 和 `bmod-core-tools/bmod.toml` 声明的技能，加上这两个模块记录。计入其中 Markdown、CSV 方法库，以及 `customize.toml` 中承载指令的字段；去掉配置注释、路径、空占位、enum 和非指令元数据。`analyze.py` 内 `STRING_KEYS` 给出完整字段白名单。Toolsmith 是独立扩展，本轮排除。
- Superpowers：15 个技能，正文及工作参考/模板；平台参考仅保留 Codex。一并计入 writing-skills 与 diagnosing-superpowers 这两个辅助技能；排除技能开发测试场景、历史创建日志和其他平台参考。工具维护约 **33.0k（40.3%）**；其余库存约 **48.9k**，这同样不是一次执行路径的加载估计。
- 每个规范来源文件计一次；同一文件的多个配置字段分别计为片段，来源文件数去重。入口数只计可调用技能/命令正文，不把每个 Markdown 都叫作独立提示词；BMAD 的 2 个 bmod 模块记录不算入口。相同文本出现在不同规范文件时保留在原始库存；另给完整文本片段 SHA256 去重值，未做语义或段落级去重。
- 配置字段与 schema 指令经 TOML/YAML 解析后按原字符串统计；格式化后的 runtime JSON 和 key 包装不在本次文本口径中。分段空白可能因运行时序列化变化。
- 功能按文件/配置字段主要目的人工映射到七类，不逐句拆分复合功能；占比按中心估算 token 计算，不能解释为功能覆盖度或工程价值。来源文件可跨分类，分类文件数不应相加当作总文件数。

## DeepSeek v4.1 token 估算

本轮没有取得并验证 DeepSeek v4.1 的专用 tokenizer；数字是以该模型为目标的通用字符量级估算，不能称为该模型的实际 token 统计。公开文本超过 99.7% 的字符为 ASCII，以英文 Markdown 为主。

设 A = ASCII 字符数，U = 非 ASCII 字符数：

- 中心估算：`A / 4 + U / 1.5`
- 下界：`A / 5 + U / 2`
- 上界：`A / 3 + U / 1`

这只是选择了一个宽的经验换算范围，**不是统计置信区间，也不是保证覆盖真实 tokenizer 的上下限**。路径、标点、代码示例、Markdown 表格和模型词表可能带来偏差。功能占比也依赖此换算与人工分类。原始字符数可用于后续换一种假设重新估算。

## 版本与证据

采集日期：2026-10-10。采用官方默认分支的固定提交；版本号只是仓库内声明，**不是声称所有样本都是稳定发布版**。Spec Kit 为 dev，BMAD 为 next。不同版本之间不可直接继承本图数字。

| 工具 | 仓库声明版本 | 固定提交 | 提交日期 |
|---|---|---|---|
| OpenSpec | 1.14.1 | [9111a7654d78](https://github.com/Fission-AI/OpenSpec/tree/9111a7654d7800391459431fff4eaf66e33a3d2e) | 2026-10-06 |
| Spec Kit | 1.1.4.dev0 | [0443760542e7](https://github.com/github/spec-kit/tree/0443760542e7e5269724744a2ac55c4bd386d095) | 2026-10-09 |
| BMAD Method | 6.13.0-next | [bda3c5929f67](https://github.com/bmad-code-org/BMAD-METHOD/tree/bda3c5929f672019b90f39a3ea27259d35d00974) | 2026-10-06 |
| Superpowers | 7.0.0 | [bb92a7774141](https://github.com/obra/superpowers/tree/bb92a77741419a4ab5f06e711a283343f1ada0c3) | 2026-10-09 |

## 文件说明

- `01_overview_v4.png / .svg / .pdf`：总量和功能占比，适合投屏。
- `02_detail_v2.png / .svg / .pdf`：分类总量、占比、字符数、来源与范围。
- `comparison.html`：无需服务器的离线浏览页，含两张图及可筛选文件/字段明细；来源链接指向固定提交。
- `prompt_inventory.csv`：逐文件/字段的字符、字节、估算区间、分类、SHA256、路径与来源链接。
- `tool_summary.csv / category_summary.csv`：四个工具的总量/分类汇总。
- `excluded_files.csv`：未纳入的文本候选文件及范围排除说明。
- `comparison.json / sources_manifest.json`：完整数据、估算假设与固定提交信息。
- `analyze.py / render.py`：统计与出图脚本；它们只处理官方源码文本，不执行所比较工具的 workflow。
- 压缩包内 `sources/` 留存本轮纳入的原始文本和许可证，`output/` 保存成果。解压后在包根目录运行 `python analyze.py`、`python render.py` 可复核总量并出图（需要 PyYAML、NumPy、Matplotlib 和 Noto Sans CJK 字体）；源码裁剪归档模式从 `output/sources_manifest.json` 读取版本，不依赖 Git。完整仓库排除清单保留原采集结果。

本轮为静态源码统计，未进行项目实验或模型调用。
