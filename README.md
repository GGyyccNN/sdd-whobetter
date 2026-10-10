# SDD 工具静态提示词对比

对比 **OpenSpec、GitHub Spec Kit、BMAD Method、Kiro Specs、Superpowers** 自身的公开提示词体量及功能构成。

本轮只做静态盘点：不代入实际项目，不调用模型，不运行 tokenizer，不测算运行费用或结果收益。官方源码快照固定于 **2026-10-10**；以 DeepSeek v4.1 为目标，使用字符启发式估算 token 量级。

## 概览图：总量与功能占比

![SDD 工具静态提示词库存总量与功能占比](output/01_overview_v2.png)

## 详细图：分类统计与来源范围

![SDD 工具静态提示词分类详细统计](output/02_detail.png)

## 主要结果

| 工具 | 来源字符数 | 库存中心估算 | 启发式范围 |
|---|---:|---:|---:|
| OpenSpec | 195,613 | 约 49.0k token | 39–65k |
| Spec Kit | 157,715 | 约 39.5k token | 32–53k |
| BMAD Method | 919,741 | 约 230.9k token | 185–308k |
| Superpowers | 326,354 | 约 81.9k token | 65–109k |
| Kiro Specs | 不可统计 | N/A | N/A |

**这些数字表示所选完整可见指令库存，不代表每次任务的额外输入或累计计费。** 实际使用按需加载。估算未用 DeepSeek v4.1 tokenizer 校准；范围不是统计置信区间，也不保证覆盖真实 tokenizer 的结果。

- OpenSpec 主图包含全部 12 个工作流；默认 core 子集加 schema/模板约 27.5k。
- BMAD 范围为 Method + Core Tools，不包含独立 Toolsmith 扩展。
- Superpowers 约 40.3% 的库存属于技能编写和工具诊断；其余库存约 48.9k，仍不是一次任务的加载量。
- Kiro 的公开仓库不包含产品源码，内部 Specs 指令未获得；项目示例规格与反馈自动化提示词不用于替代统计。
- 使用默认分支的固定提交，包含 Spec Kit dev 和 BMAD next 快照，不声称所有样本均为稳定发布版。

## 查看与下载

- [完整统计报告与口径](output/README.md)
- [离线浏览页](output/comparison.html)：下载后用浏览器打开，支持按工具、功能、文件筛选与 CSV 导出。
- [完整成果包](output/SDD静态提示词对比.zip)：图片、PDF、SVG、数据、脚本和原始文本快照。
- 概览图：[PNG](output/01_overview_v2.png) · [SVG](output/01_overview_v2.svg) · [PDF](output/01_overview_v2.pdf)
- 详细图：[PNG](output/02_detail.png) · [SVG](output/02_detail.svg) · [PDF](output/02_detail.pdf)
- [逐文件/配置字段明细](output/prompt_inventory.csv) · [工具汇总](output/tool_summary.csv) · [功能分类汇总](output/category_summary.csv)
- [固定版本来源](output/sources_manifest.json) · [完整数据与假设](output/comparison.json) · [排除文件清单](output/excluded_files.csv)

## 复核统计与重新出图

需要 Python 3.11+、依赖清单中的库，以及 Noto Sans CJK 字体。本轮渲染使用 Linux 字体路径 `/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc`；Ubuntu/Debian 可通过 `fonts-noto-cjk` 软件包提供。

在仓库根目录执行：

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python analyze.py
python render.py
```

`sources/` 保存本轮纳入的原始文本及统计所需模块清单，**不是工具的完整检出，也不用于安装或执行这些工具**。脚本从 `output/sources_manifest.json` 读取固定提交信息，不要求来源目录带有 Git 元数据。完整仓库的排除清单保留采集时的结果。

统计按文件或配置字段的主要功能归类，未逐句拆分。空白、标题、frontmatter 和示例保留；TOML/YAML 指令字段解析为原字符串。完整文本片段的重复量另列 SHA256 去重值，不做语义去重。

原始文本来源与许可证见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。GSD 按原计划保留为后续补充样本，本轮未纳入。
