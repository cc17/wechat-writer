---
name: wechat-writer
description: Create polished WeChat Official Account article assets from Markdown or article content. Use when Codex needs to convert a Markdown file into a WeChat-ready HTML preview with a copy button for pasting styled content into the WeChat editor, generate or refine a WeChat article intro/summary, or create cover-image prompts/assets for a WeChat article.
---

# WeChat Writer

Use this skill to turn article content into publishable WeChat Official Account materials: styled HTML that can be copied into the WeChat editor, a concise article intro, and optional cover art.

## Core Workflow

1. Read the user's Markdown file or pasted article content.
2. Identify the article topic, audience, desired tone, and any existing title/subtitle.
3. Generate or refine:
   - A WeChat-friendly title when requested.
   - A short article intro/summary suitable for the WeChat article description field.
   - An enhanced Markdown draft when visual modules would improve the article.
   - A polished HTML preview page with inline styles and a copy button.
   - A cover image when requested.
4. Write output files next to the source Markdown unless the user specifies another directory.

## Two-Stage Rendering

Use a two-stage workflow by default when the user wants a polished article, better visual style, or output similar to the reference screenshots:

1. **AI planning stage**: Rewrite ordinary Markdown into enhanced Markdown using the module syntax below. Keep the user's argument, facts, and voice; only restructure where it improves reading and visual clarity.
2. **Deterministic rendering stage**: Run `scripts/md_to_wechat_html.py` on the enhanced Markdown to produce copyable WeChat HTML.

Use plain Markdown conversion only when the user asks for a quick conversion or the article is too short/simple to benefit from modules.

## Enhanced Markdown Modules

Use these blocks sparingly. A good article usually needs one hero/comparison module near the top, 2-4 callouts, and 1-3 structured modules.

### Comparison Hero

Use when the article compares two products, paths, people, strategies, or ideas.

```markdown
:::hero-compare
left_label: 即梦
left_value: 15s
left_title: 出境 · 惊艳一刻
left_subtitle: toC 玩梗 / 社交传播
left_tags: 真人入画, AI 生图, 续写
right_label: 小云雀 AI
right_value: 180s
right_title: 端到端 · 完整叙事
right_subtitle: toB 量产 / 短剧电商
right_tags: 智能成片, 数字人, Agent 接入
:::
```

### Callout

Use for thesis statements, reality checks, risks, or key takeaways.

```markdown
:::callout warning
「一次生成、结果不可控」，才是 toB 落地最大的风险敞口。
:::
```

Types: `primary` for creative/toC/user-experience points, `secondary` for productivity/toB/opportunity points, and `warning` for cost/risk/reality-check points.

### Compare Cards

Use for two-column structured product or idea comparisons.

```markdown
:::compare-cards
即梦 | 核心功能: 出境 · AI 生图 · 续写 | 单次时长: 15 秒（可续写） | 目标用户: toC 创作者 / 玩梗
小云雀 AI | 核心功能: 端到端 Agent · 场景模板 | 单次时长: 最长 180 秒 | 目标用户: toB 内容团队 / 电商
:::
```

### Timeline

Use for duration, process, roadmap, or staged capability comparison.

```markdown
:::timeline
即梦出境 | 15s | 出境高光 | primary
即梦续写 | 60s | 多段拼接 | primary
小云雀最长 | 180s | 完整视频 | secondary
:::
```

### Placeholder

Use when the article should contain a screenshot or image slot but no asset is available.

```markdown
:::placeholder
title: 即梦出境效果截图
hint: 建议放 1-2 张个人实测截图
:::
```

## Enhancement Heuristics

When transforming ordinary Markdown into enhanced Markdown:

- Convert the strongest comparison in the intro into `hero-compare`.
- Convert the article's central thesis and risk statements into `callout` blocks.
- Convert dense comparison tables into `compare-cards` when there are only two main objects; keep normal tables for many-row reference data.
- Convert duration/process lists into `timeline`.
- Convert parenthetical screenshot suggestions into `placeholder`.
- Preserve all facts and avoid inventing data.
- Do not over-module: if every paragraph becomes a visual block, the article feels noisy.

## HTML Conversion

Prefer the bundled script for Markdown-to-HTML output:

```bash
python3 ~/.codex/skills/wechat-writer/scripts/md_to_wechat_html.py input.md -o output.html
```

The script creates a standalone preview page. The visible page includes a copy button; clicking it copies only the styled article body HTML, not the preview chrome. The copied HTML is optimized for pasting into the WeChat Official Account editor.

The script uses `markdown-it-py` plus `BeautifulSoup` for the standard Markdown layer when available, then applies WeChat-safe inline styles and replaces enhanced module placeholders. This supports common Markdown more broadly than the old hand-written parser: headings, paragraphs, nested lists, blockquotes, links, images, fenced code, inline code, emphasis, strikethrough, thematic breaks, and tables. If those libraries are unavailable, the script falls back to a smaller built-in parser so basic conversion still works.

Do not try to encode every visual layout as ordinary Markdown. Use standard Markdown for article content and enhanced modules for editorial design intent.

If editing by hand, keep these constraints:

- Use inline styles on article elements because WeChat strips many external styles.
- Avoid external CSS, scripts, web fonts, remote images, SVG, and complex layout.
- Keep the article body within a single root container.
- Use semantic tags where useful, but style every important element inline.
- Use readable mobile-first sizing: 16px body text, 1.75 line height, strong spacing, and high contrast.
- Use restrained visual accents: one primary color, soft section backgrounds, border-left callouts, and simple dividers.
- Do not rely on JavaScript inside the copied article body. JavaScript is only allowed in the standalone preview page for the copy button.

## Visual Style Guidance

Default to the screenshot-derived style in `references/style-guide.md`: a clean, analytical, product-review editorial look with white space, dark readable text, purple/green semantic contrast, amber reality-check callouts, comparison cards, and simple data-like modules. Read that reference before designing custom HTML sections, cover prompts, or article visuals.

For ordinary Markdown conversion, keep this baseline:

- Body text: dark neutral, generous line height, short paragraphs.
- Headings: clear hierarchy, not oversized; prefer colored-dot section headings for H2/H3 when appropriate.
- Quotes/callouts: left border, soft tinted background, concise padding; choose purple, green, or amber by meaning.
- Lists: comfortable indentation and spacing.
- Code: monospaced, wrapped, warm neutral background, small border radius.
- Tables: avoid when possible; if needed, use simple borders and compact cells.

Adapt the palette to the article topic, but preserve the default semantic color system: purple for creative/toC/user-experience points, green for productivity/toB/opportunity points, and amber for cost/risk/reality-check points.

## Intro Generation

When the user asks for an article intro, produce 1-3 options unless they request one final version. Keep each intro within 60-120 Chinese characters by default. Make it concrete, curiosity-building, and faithful to the article; avoid clickbait, exaggerated claims, and empty motivational language.

## Cover Generation

When the user asks to generate a cover:

1. First derive the core visual metaphor from the article topic.
2. Use the `imagegen` skill/tool if available.
3. Follow `references/style-guide.md` for the default cover direction: editorial/product-analysis composition, purple-vs-green contrast when comparing two sides, clean cards/dividers, strong negative space, and no tiny text.
4. Prefer a 2.35:1 landscape composition for main WeChat cover images unless the user gives another size.
5. Generate a cover prompt that includes style, subject, palette, lighting, composition, and "no text" unless the user explicitly asks for text in the image.

If image generation is unavailable, provide a precise prompt the user can run later.

## Output Naming

Use predictable filenames:

- `<source-name>.wechat.html` for the copyable preview page.
- `<source-name>.intro.md` for generated intros when saved separately.
- `<source-name>.cover.png` for generated cover images when available.

## Quality Check

Before finishing:

- Open or inspect the generated HTML enough to verify the copy button exists.
- Confirm the article body root has `id="wechat-article"`.
- Confirm important article styles are inline.
- Mention the output path and any generated intro/cover assets.
