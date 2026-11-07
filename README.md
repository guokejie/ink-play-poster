# ink-play-poster

黑墨手绘海报创作技能。包含九张内置风格参考、字体与空间设计系统、创意联想流程、提示词生成与人工视觉评估工具，支持准确中文排版和局部修改。

## 安装

将整个仓库目录复制到 `~/.codex/skills/ink-play-poster/`，确保 `SKILL.md`、`assets/`、`references/` 与 `scripts/` 保持相对位置。

## 使用

在支持技能的助手中调用 `ink-play-poster`，提供主题、需要上版的原文及可选风格编号 P01–P09。例如：

> 生成咖啡店概念海报，标题 COFFEE & SLOW LIFE，地址用小字：上海市静安区愚园路 128 号。

默认竖版 3:4、黑白、数字屏幕用途。实际生成需要助手可调用图像生成工具；仓库脚本本身不调用模型。生成后仍需查看实际结果并逐字核验。

## 工具

Python 3；部分图像辅助工具依赖 Pillow：

```sh
python -m pip install -r requirements.txt
python scripts/prompt.py --list
python scripts/prompt.py brief.json --ready --out prompt.txt
python scripts/review.py qa.json
python -m unittest discover -s tests -v
```

完整流程见 [SKILL.md](SKILL.md)。质量检查脚本验证设计记录，不替代人工视觉检查。

## 目录

- `assets/`：完整参考图与局部参考
- `references/`：风格、字体、构图、产品识别与生成规范
- `scripts/`：提示词、标题参考与合成、评估工具
- `tests/`：工具测试
- `evals/`：回归用例与协议
- `agents/`：助手配置

参考图的原有品牌、签名与文案不应复制进新海报；参考素材随技能保留，不在此另行授予素材版权许可。
