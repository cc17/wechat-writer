#!/usr/bin/env python3
"""Convert Markdown into a standalone WeChat copy-preview HTML file."""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

try:
    from bs4 import BeautifulSoup
    from markdown_it import MarkdownIt
except ImportError:  # pragma: no cover - fallback keeps the script usable without optional deps.
    BeautifulSoup = None
    MarkdownIt = None


DEFAULT_THEME = {
    "primary": "#6253C9",
    "secondary": "#5B8F22",
    "warning": "#9A5B08",
    "text": "#1F1F1F",
    "muted": "#6F6F68",
    "border": "#DDDCD5",
    "soft": "#EFEDFF",
    "secondarySoft": "#EDF6E4",
    "warningSoft": "#FFF2DC",
    "panel": "#F5F4EE",
    "codeBackground": "#F7F5EE",
}


def load_theme(theme_path: Path | None) -> dict[str, str]:
    if not theme_path:
        bundled = Path(__file__).resolve().parents[1] / "assets" / "default-theme.json"
        theme_path = bundled if bundled.exists() else None
    if not theme_path:
        return DEFAULT_THEME
    data = json.loads(theme_path.read_text(encoding="utf-8"))
    return {**DEFAULT_THEME, **{k: str(v) for k, v in data.items()}}


def inline_markdown(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"__([^_]+)__", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", escaped)
    escaped = re.sub(r"_([^_]+)_", r"<em>\1</em>", escaped)
    escaped = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', escaped)
    return escaped


def style_inline(html_text: str, theme: dict[str, str]) -> str:
    html_text = html_text.replace("<strong>", f'<strong style="color:{theme["text"]};font-weight:700;">')
    html_text = html_text.replace("<em>", '<em style="font-style:italic;">')
    html_text = html_text.replace(
        "<code>",
        f'<code style="font-family:Menlo,Consolas,monospace;font-size:0.92em;background:{theme["codeBackground"]};border:1px solid {theme["border"]};border-radius:4px;padding:2px 5px;color:{theme["text"]};word-break:break-word;">',
    )
    html_text = re.sub(
        r'<a href="([^"]+)">([^<]+)</a>',
        rf'<a href="\1" style="color:{theme["primary"]};text-decoration:none;border-bottom:1px solid {theme["primary"]};">\2</a>',
        html_text,
    )
    return html_text


def styled_text(text: str, theme: dict[str, str]) -> str:
    return style_inline(inline_markdown(text.strip()), theme)


def parse_key_values(lines: list[str]) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in lines:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()
    return values


def accent_for(kind: str, theme: dict[str, str]) -> tuple[str, str]:
    if kind == "secondary":
        return theme["secondary"], theme["secondarySoft"]
    if kind == "warning":
        return theme["warning"], theme["warningSoft"]
    return theme["primary"], theme["soft"]


def render_hero_compare(lines: list[str], theme: dict[str, str]) -> str:
    data = parse_key_values(lines)
    left_tags = [tag.strip() for tag in data.get("left_tags", "").split(",") if tag.strip()]
    right_tags = [tag.strip() for tag in data.get("right_tags", "").split(",") if tag.strip()]

    def tag_html(tags: list[str], color: str) -> str:
        return "".join(
            f'<span style="display:inline-block;margin:0 8px 8px 0;padding:5px 10px;border:1px solid {color};border-radius:999px;color:{color};font-size:13px;line-height:1.2;font-weight:700;">{html.escape(tag)}</span>'
            for tag in tags
        )

    left = f"""
      <section style="box-sizing:border-box;width:48%;min-width:0;padding:0 20px 0 0;">
        <div style="display:inline-block;margin:0 0 18px;padding:7px 14px;border-radius:999px;background:{theme["primary"]};color:#ffffff;font-size:15px;line-height:1.2;font-weight:800;">{html.escape(data.get("left_label", "左侧"))}</div>
        <div style="margin:0 0 10px;color:{theme["primary"]};font-size:48px;line-height:1;font-weight:900;">{html.escape(data.get("left_value", ""))}</div>
        <div style="margin:0 0 8px;color:#F4F1FF;font-size:18px;line-height:1.35;font-weight:800;">{styled_text(data.get("left_title", ""), theme)}</div>
        <div style="margin:0 0 18px;color:#8E82DD;font-size:15px;line-height:1.45;font-weight:700;">{styled_text(data.get("left_subtitle", ""), theme)}</div>
        <div>{tag_html(left_tags, "#8E82DD")}</div>
      </section>
    """
    right = f"""
      <section style="box-sizing:border-box;width:48%;min-width:0;padding:0 0 0 20px;">
        <div style="display:inline-block;margin:0 0 18px;padding:7px 14px;border-radius:999px;background:{theme["secondary"]};color:#ffffff;font-size:15px;line-height:1.2;font-weight:800;">{html.escape(data.get("right_label", "右侧"))}</div>
        <div style="margin:0 0 10px;color:{theme["secondary"]};font-size:48px;line-height:1;font-weight:900;">{html.escape(data.get("right_value", ""))}</div>
        <div style="margin:0 0 8px;color:#ECFFD9;font-size:18px;line-height:1.35;font-weight:800;">{styled_text(data.get("right_title", ""), theme)}</div>
        <div style="margin:0 0 18px;color:#80B941;font-size:15px;line-height:1.45;font-weight:700;">{styled_text(data.get("right_subtitle", ""), theme)}</div>
        <div>{tag_html(right_tags, "#80B941")}</div>
      </section>
    """
    return (
        '<section data-wechat-module="hero-compare" style="position:relative;margin:0 0 34px;padding:30px 28px;background:#1B1128;border-radius:14px;">'
        f'<div style="display:flex;gap:0;align-items:flex-start;justify-content:space-between;">{left}'
        f'<div style="position:absolute;left:50%;top:30px;bottom:30px;width:1px;background:#6552C8;"></div>'
        f'<div style="position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:48px;height:48px;border-radius:999px;background:#332553;border:1px solid #6552C8;color:#ffffff;text-align:center;line-height:48px;font-size:15px;font-weight:800;">VS</div>'
        f"{right}</div></section>"
    )


def render_callout(kind: str, lines: list[str], theme: dict[str, str]) -> str:
    color, background = accent_for(kind, theme)
    text = styled_text(" ".join(line.strip() for line in lines if line.strip()), theme)
    return (
        f'<blockquote data-wechat-module="callout" style="margin:4px 0 28px;padding:16px 18px;background:{background};border-left:5px solid {color};'
        f'border-radius:0 8px 8px 0;color:{color};font-size:17px;line-height:1.85;font-weight:700;">{text}</blockquote>'
    )


def render_compare_cards(lines: list[str], theme: dict[str, str]) -> str:
    cards = []
    colors = [(theme["primary"], theme["soft"]), (theme["secondary"], theme["secondarySoft"])]
    for index, line in enumerate(line for line in lines if line.strip()):
        parts = [part.strip() for part in line.split("|") if part.strip()]
        if not parts:
            continue
        color, soft = colors[index % len(colors)]
        title = parts[0]
        rows = []
        for item in parts[1:]:
            if ":" in item:
                label, value = item.split(":", 1)
                rows.append(
                    f'<div style="display:flex;justify-content:space-between;gap:12px;margin:0 0 9px;color:{theme["text"]};font-size:15px;line-height:1.5;">'
                    f'<span style="color:{theme["muted"]};">{html.escape(label.strip())}</span>'
                    f'<strong style="text-align:right;color:{theme["text"]};font-weight:700;">{styled_text(value, theme)}</strong></div>'
                )
            else:
                rows.append(f'<p style="margin:0 0 9px;color:{theme["text"]};font-size:15px;line-height:1.55;">{styled_text(item, theme)}</p>')
        cards.append(
            f'<section data-wechat-module="compare-card" style="box-sizing:border-box;width:48%;min-width:0;margin:0 0 18px;padding:18px 18px 16px;background:#ffffff;border:1px solid {theme["border"]};border-radius:12px;">'
            f'<div style="display:flex;align-items:center;gap:12px;margin:0 0 14px;padding-bottom:12px;border-bottom:1px solid {theme["border"]};">'
            f'<span style="display:inline-block;min-width:42px;height:42px;border-radius:10px;background:{soft};color:{color};font-size:20px;line-height:42px;text-align:center;font-weight:900;">{html.escape(title[:1])}</span>'
            f'<strong style="color:{theme["text"]};font-size:19px;line-height:1.3;font-weight:800;">{html.escape(title)}</strong></div>'
            f'{"".join(rows)}</section>'
        )
    return f'<section data-wechat-module="compare-cards" style="display:flex;flex-wrap:wrap;justify-content:space-between;margin:8px 0 30px;">{"".join(cards)}</section>'


def render_timeline(lines: list[str], theme: dict[str, str]) -> str:
    parsed_items = []
    max_value = 0.0
    for line in lines:
        parts = [part.strip() for part in line.split("|")]
        if len(parts) < 3:
            continue
        label, value, desc = parts[:3]
        kind = parts[3] if len(parts) > 3 else "primary"
        numeric_match = re.search(r"\d+(?:\.\d+)?", value)
        numeric_value = float(numeric_match.group(0)) if numeric_match else 0.0
        max_value = max(max_value, numeric_value)
        parsed_items.append((label, value, desc, kind, numeric_value))

    items = []
    for label, value, desc, kind, numeric_value in parsed_items:
        color, background = accent_for(kind, theme)
        width = 100 if max_value <= 0 else max(16, min(100, int(numeric_value / max_value * 100)))
        items.append(
            f'<div style="margin:0 0 14px;">'
            f'<div style="display:flex;align-items:center;gap:12px;margin:0 0 5px;">'
            f'<strong style="width:86px;color:{color};font-size:15px;line-height:1.3;">{html.escape(label)}</strong>'
            f'<div style="flex:1;height:18px;background:#D8D6CF;border-radius:999px;overflow:hidden;">'
            f'<div style="width:{width}%;height:18px;background:{color};border-radius:999px;color:#ffffff;text-align:center;font-size:12px;line-height:18px;font-weight:800;">{html.escape(value)}</div></div></div>'
            f'<div style="margin-left:98px;color:{theme["muted"]};font-size:13px;line-height:1.5;">{styled_text(desc, theme)}</div></div>'
        )
    return (
        f'<section data-wechat-module="timeline" style="margin:8px 0 30px;padding:20px 18px;background:{theme["panel"]};border-radius:12px;">'
        f'<div style="margin:0 0 16px;color:{theme["text"]};font-size:16px;font-weight:800;">叙事空间对比</div>'
        f'{"".join(items)}</section>'
    )


def render_placeholder(lines: list[str], theme: dict[str, str]) -> str:
    data = parse_key_values(lines)
    title = data.get("title", "图片占位")
    hint = data.get("hint", "可在这里放置截图、封面或数据图")
    return (
        f'<section data-wechat-module="placeholder" style="margin:8px 0 30px;padding:28px 18px;background:{theme["panel"]};border:1px dashed #C8C5BA;border-radius:12px;text-align:center;">'
        f'<div style="margin:0 auto 10px;width:34px;height:34px;border:2px solid #8A8981;border-radius:8px;color:#8A8981;line-height:30px;font-size:20px;font-weight:800;">□</div>'
        f'<div style="margin:0 0 6px;color:#77766F;font-size:16px;line-height:1.5;font-weight:800;">{html.escape(title)}</div>'
        f'<div style="color:#999891;font-size:14px;line-height:1.6;">{html.escape(hint)}</div></section>'
    )


def render_directive(name: str, arg: str, lines: list[str], theme: dict[str, str]) -> str:
    if name == "hero-compare":
        return render_hero_compare(lines, theme)
    if name == "callout":
        return render_callout(arg or "warning", lines, theme)
    if name == "compare-cards":
        return render_compare_cards(lines, theme)
    if name == "timeline":
        return render_timeline(lines, theme)
    if name == "placeholder":
        return render_placeholder(lines, theme)
    fallback = "\n".join(lines)
    return render_callout("primary", [fallback], theme)


def extract_directives(markdown: str, theme: dict[str, str]) -> tuple[str, dict[str, str]]:
    lines = markdown.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    output: list[str] = []
    modules: dict[str, str] = {}
    in_code = False
    in_directive = False
    directive_name = ""
    directive_arg = ""
    directive_lines: list[str] = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            if not in_directive:
                output.append(line)
            else:
                directive_lines.append(line)
            continue

        directive_start = re.match(r"^:::\s*([a-zA-Z0-9_-]+)(?:\s+([a-zA-Z0-9_-]+))?\s*$", stripped)
        if in_directive:
            if stripped == ":::" and not in_code:
                token = f"@@WECHAT_MODULE_{len(modules)}@@"
                modules[token] = render_directive(directive_name, directive_arg, directive_lines, theme)
                output.append("")
                output.append(token)
                output.append("")
                in_directive = False
                directive_name = ""
                directive_arg = ""
                directive_lines = []
            else:
                directive_lines.append(line)
            continue

        if directive_start and not in_code:
            in_directive = True
            directive_name = directive_start.group(1)
            directive_arg = directive_start.group(2) or ""
            directive_lines = []
            continue

        output.append(line)

    if in_directive:
        token = f"@@WECHAT_MODULE_{len(modules)}@@"
        modules[token] = render_directive(directive_name, directive_arg, directive_lines, theme)
        output.append("")
        output.append(token)
        output.append("")

    return "\n".join(output), modules


def add_style(tag, style: str) -> None:
    existing = tag.get("style", "").strip()
    tag["style"] = f"{existing};{style}" if existing else style


def inside_wechat_module(tag) -> bool:
    current = tag
    while current is not None:
        if getattr(current, "attrs", None) and current.get("data-wechat-module"):
            return True
        current = getattr(current, "parent", None)
    return False


def style_markdown_html(markdown_html: str, modules: dict[str, str], theme: dict[str, str]) -> str:
    if BeautifulSoup is None:
        return markdown_html
    soup = BeautifulSoup(markdown_html, "html.parser")

    for token, module_html in modules.items():
        token_node = soup.find(string=lambda value: value and value.strip() == token)
        if not token_node:
            continue
        replacement = BeautifulSoup(module_html, "html.parser")
        parent = token_node.parent
        if parent and parent.name == "p" and parent.get_text(strip=True) == token:
            parent.replace_with(replacement)
        else:
            token_node.replace_with(replacement)

    for tag in soup.find_all("h1"):
        add_style(tag, f'margin:0 0 28px;color:{theme["text"]};font-size:28px;line-height:1.35;font-weight:800;letter-spacing:0;')
    for tag in soup.find_all("h2"):
        tag.insert(
            0,
            BeautifulSoup(
                f'<span style="display:inline-block;width:9px;height:9px;margin:0 10px 3px 0;border-radius:50%;background:{theme["primary"]};vertical-align:middle;"></span>',
                "html.parser",
            ),
        )
        add_style(tag, f'margin:36px 0 18px;color:{theme["text"]};font-size:22px;line-height:1.42;font-weight:800;letter-spacing:0;')
    for tag in soup.find_all(["h3", "h4", "h5", "h6"]):
        tag.insert(
            0,
            BeautifulSoup(
                f'<span style="display:inline-block;width:8px;height:8px;margin:0 9px 3px 0;border-radius:50%;background:{theme["secondary"]};vertical-align:middle;"></span>',
                "html.parser",
            ),
        )
        add_style(tag, f'margin:30px 0 14px;color:{theme["text"]};font-size:20px;line-height:1.45;font-weight:800;letter-spacing:0;')
    for tag in soup.find_all("p"):
        add_style(tag, f'margin:0 0 22px;color:{theme["text"]};font-size:17px;line-height:1.88;letter-spacing:0;')
    for tag in soup.find_all(["ul", "ol"]):
        add_style(tag, "margin:0 0 24px 24px;padding:0;")
    for tag in soup.find_all("li"):
        add_style(tag, f'margin:0 0 10px;color:{theme["text"]};font-size:17px;line-height:1.78;')
    for tag in soup.find_all("blockquote"):
        if tag.get("data-wechat-module"):
            continue
        add_style(tag, f'margin:4px 0 28px;padding:16px 18px;background:{theme["warningSoft"]};border-left:5px solid {theme["warning"]};border-radius:0 8px 8px 0;color:{theme["warning"]};font-size:17px;line-height:1.85;font-weight:700;')
        for child in tag.find_all("p"):
            child.unwrap()
    for tag in soup.find_all("strong"):
        if inside_wechat_module(tag):
            continue
        add_style(tag, f'color:{theme["text"]};font-weight:700;')
    for tag in soup.find_all("em"):
        if inside_wechat_module(tag):
            continue
        add_style(tag, "font-style:italic;")
    for tag in soup.find_all("a"):
        tag["target"] = "_blank"
        add_style(tag, f'color:{theme["primary"]};text-decoration:none;border-bottom:1px solid {theme["primary"]};')
    for tag in soup.find_all("img"):
        add_style(tag, f'display:block;max-width:100%;height:auto;margin:8px auto 28px;border-radius:12px;border:1px solid {theme["border"]};')
    for tag in soup.find_all("hr"):
        add_style(tag, f'border:0;border-top:1px solid {theme["border"]};margin:30px 0;')
    for tag in soup.find_all("del"):
        add_style(tag, f'color:{theme["muted"]};text-decoration:line-through;')

    for tag in soup.find_all("code"):
        if tag.parent and tag.parent.name == "pre":
            continue
        add_style(tag, f'font-family:Menlo,Consolas,monospace;font-size:0.92em;background:{theme["codeBackground"]};border:1px solid {theme["border"]};border-radius:4px;padding:2px 5px;color:{theme["text"]};word-break:break-word;')
    for tag in soup.find_all("pre"):
        add_style(tag, f'margin:8px 0 26px;padding:16px 18px;background:{theme["codeBackground"]};border:1px solid {theme["border"]};border-radius:10px;overflow-x:auto;white-space:pre-wrap;word-break:break-word;')
        code = tag.find("code")
        if code:
            add_style(code, f'font-family:Menlo,Consolas,monospace;font-size:14px;line-height:1.7;color:{theme["text"]};')

    for table in list(soup.find_all("table")):
        add_style(table, "width:100%;border-collapse:collapse;table-layout:fixed;")
        for th in table.find_all("th"):
            add_style(th, f'padding:12px 10px;color:{theme["muted"]};font-size:14px;line-height:1.5;text-align:left;border-bottom:1px solid {theme["border"]};font-weight:700;')
        for row in table.find_all("tr"):
            for index, td in enumerate(row.find_all("td")):
                color = theme["primary"] if index == 1 else theme["secondary"] if index == 2 else theme["text"]
                add_style(td, f'padding:13px 10px;color:{color};font-size:15px;line-height:1.55;text-align:left;border-bottom:1px solid {theme["border"]};vertical-align:top;')
        wrapper = soup.new_tag("section")
        wrapper["style"] = f'margin:8px 0 28px;padding:16px;background:#ffffff;border:1px solid {theme["border"]};border-radius:12px;overflow-x:auto;'
        table.wrap(wrapper)

    return str(soup)


def render_blocks(markdown: str, theme: dict[str, str]) -> str:
    if MarkdownIt is not None and BeautifulSoup is not None:
        markdown_without_directives, modules = extract_directives(markdown, theme)
        md = MarkdownIt("commonmark", {"html": False, "linkify": True, "typographer": False}).enable("table").enable("strikethrough")
        return style_markdown_html(md.render(markdown_without_directives), modules, theme)
    return render_blocks_fallback(markdown, theme)


def render_blocks_fallback(markdown: str, theme: dict[str, str]) -> str:
    lines = markdown.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    blocks: list[str] = []
    paragraph: list[str] = []
    list_items: list[str] = []
    table_rows: list[list[str]] = []
    ordered = False
    in_code = False
    code_lines: list[str] = []
    in_directive = False
    directive_name = ""
    directive_arg = ""
    directive_lines: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            text = " ".join(part.strip() for part in paragraph if part.strip())
            body = style_inline(inline_markdown(text), theme)
            blocks.append(
                f'<p style="margin:0 0 22px;color:{theme["text"]};font-size:17px;line-height:1.88;letter-spacing:0;">{body}</p>'
            )
            paragraph.clear()

    def flush_list() -> None:
        nonlocal ordered
        if list_items:
            tag = "ol" if ordered else "ul"
            items = "".join(
                f'<li style="margin:0 0 10px;color:{theme["text"]};font-size:17px;line-height:1.78;">{style_inline(inline_markdown(item), theme)}</li>'
                for item in list_items
            )
            blocks.append(f'<{tag} style="margin:0 0 24px 24px;padding:0;">{items}</{tag}>')
            list_items.clear()
            ordered = False

    def is_table_separator(cells: list[str]) -> bool:
        return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells)

    def split_table_row(line: str) -> list[str] | None:
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            return None
        return [cell.strip() for cell in stripped.strip("|").split("|")]

    def flush_table() -> None:
        if not table_rows:
            return
        rows = [row for row in table_rows if not is_table_separator(row)]
        table_rows.clear()
        if not rows:
            return
        header = rows[0]
        body_rows = rows[1:]
        head_html = "".join(
            f'<th style="padding:12px 10px;color:{theme["muted"]};font-size:14px;line-height:1.5;text-align:left;border-bottom:1px solid {theme["border"]};font-weight:700;">{style_inline(inline_markdown(cell), theme)}</th>'
            for cell in header
        )
        body_html = ""
        for row in body_rows:
            padded = row + [""] * max(0, len(header) - len(row))
            body_html += "<tr>"
            for index, cell in enumerate(padded[: len(header)]):
                color = theme["primary"] if index == 1 else theme["secondary"] if index == 2 else theme["text"]
                body_html += (
                    f'<td style="padding:13px 10px;color:{color};font-size:15px;line-height:1.55;text-align:left;border-bottom:1px solid {theme["border"]};vertical-align:top;">'
                    f"{style_inline(inline_markdown(cell), theme)}</td>"
                )
            body_html += "</tr>"
        blocks.append(
            f'<section style="margin:8px 0 28px;padding:16px;background:#ffffff;border:1px solid {theme["border"]};border-radius:12px;">'
            f'<table style="width:100%;border-collapse:collapse;table-layout:fixed;">'
            f"<thead><tr>{head_html}</tr></thead><tbody>{body_html}</tbody></table></section>"
        )

    for raw in lines:
        line = raw.rstrip()
        directive_start = re.match(r"^:::\s*([a-zA-Z0-9_-]+)(?:\s+([a-zA-Z0-9_-]+))?\s*$", line.strip())
        if in_directive:
            if line.strip() == ":::": 
                blocks.append(render_directive(directive_name, directive_arg, directive_lines, theme))
                directive_lines.clear()
                in_directive = False
                directive_name = ""
                directive_arg = ""
            else:
                directive_lines.append(line)
            continue
        if directive_start and not in_code:
            flush_paragraph()
            flush_list()
            flush_table()
            in_directive = True
            directive_name = directive_start.group(1)
            directive_arg = directive_start.group(2) or ""
            directive_lines = []
            continue

        if line.strip().startswith("```"):
            if in_code:
                code = html.escape("\n".join(code_lines))
                blocks.append(
                    f'<pre style="margin:8px 0 26px;padding:16px 18px;background:{theme["codeBackground"]};border:1px solid {theme["border"]};border-radius:10px;overflow-x:auto;white-space:pre-wrap;word-break:break-word;"><code style="font-family:Menlo,Consolas,monospace;font-size:14px;line-height:1.7;color:{theme["text"]};">{code}</code></pre>'
                )
                code_lines.clear()
                in_code = False
            else:
                flush_paragraph()
                flush_list()
                in_code = True
            continue
        if in_code:
            code_lines.append(line)
            continue

        if not line.strip():
            flush_paragraph()
            flush_list()
            flush_table()
            continue

        heading = re.match(r"^(#{1,4})\s+(.+)$", line)
        unordered_item = re.match(r"^\s*[-*+]\s+(.+)$", line)
        ordered_item = re.match(r"^\s*\d+[.)]\s+(.+)$", line)
        quote = re.match(r"^>\s?(.+)$", line)
        table_row = split_table_row(line)

        if heading:
            flush_paragraph()
            flush_list()
            flush_table()
            level = len(heading.group(1))
            text = style_inline(inline_markdown(heading.group(2).strip()), theme)
            if level == 1:
                blocks.append(
                    f'<h1 style="margin:0 0 28px;color:{theme["text"]};font-size:28px;line-height:1.35;font-weight:800;letter-spacing:0;">{text}</h1>'
                )
            elif level == 2:
                blocks.append(
                    f'<h2 style="margin:36px 0 18px;color:{theme["text"]};font-size:22px;line-height:1.42;font-weight:800;letter-spacing:0;"><span style="display:inline-block;width:9px;height:9px;margin:0 10px 3px 0;border-radius:50%;background:{theme["primary"]};vertical-align:middle;"></span>{text}</h2>'
                )
            else:
                blocks.append(
                    f'<h3 style="margin:30px 0 14px;color:{theme["text"]};font-size:20px;line-height:1.45;font-weight:800;letter-spacing:0;"><span style="display:inline-block;width:8px;height:8px;margin:0 9px 3px 0;border-radius:50%;background:{theme["secondary"]};vertical-align:middle;"></span>{text}</h3>'
                )
            continue

        if quote:
            flush_paragraph()
            flush_list()
            flush_table()
            text = style_inline(inline_markdown(quote.group(1).strip()), theme)
            blocks.append(
                f'<blockquote style="margin:4px 0 26px;padding:16px 18px;background:{theme["warningSoft"]};border-left:5px solid {theme["warning"]};border-radius:0 8px 8px 0;color:{theme["warning"]};font-size:17px;line-height:1.85;">{text}</blockquote>'
            )
            continue

        if unordered_item or ordered_item:
            flush_paragraph()
            flush_table()
            is_ordered = ordered_item is not None
            if list_items and ordered != is_ordered:
                flush_list()
            ordered = is_ordered
            list_items.append((ordered_item or unordered_item).group(1).strip())
            continue

        if table_row:
            flush_paragraph()
            flush_list()
            table_rows.append(table_row)
            continue

        paragraph.append(line)

    flush_paragraph()
    flush_list()
    flush_table()
    if in_directive:
        blocks.append(render_directive(directive_name, directive_arg, directive_lines, theme))
    if in_code:
        code = html.escape("\n".join(code_lines))
        blocks.append(
            f'<pre style="margin:8px 0 26px;padding:16px 18px;background:{theme["codeBackground"]};border:1px solid {theme["border"]};border-radius:10px;overflow-x:auto;white-space:pre-wrap;word-break:break-word;"><code style="font-family:Menlo,Consolas,monospace;font-size:14px;line-height:1.7;color:{theme["text"]};">{code}</code></pre>'
        )
    return "\n".join(blocks)


def render_page(article_html: str, title: str, theme: dict[str, str]) -> str:
    article = (
        f'<section id="wechat-article" style="box-sizing:border-box;max-width:677px;margin:0 auto;padding:34px 20px 44px;background:#ffffff;color:{theme["text"]};font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,PingFang SC,Hiragino Sans GB,Microsoft YaHei,sans-serif;">'
        f"{article_html}\n</section>"
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    body {{ margin:0; background:#f5f4ee; color:#1f1f1f; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif; }}
    .toolbar {{ position:sticky; top:0; z-index:10; display:flex; justify-content:center; gap:12px; padding:12px; background:rgba(255,255,255,.94); border-bottom:1px solid {theme["border"]}; backdrop-filter:blur(10px); }}
    button {{ border:0; border-radius:6px; background:{theme["primary"]}; color:#fff; padding:10px 14px; font-size:14px; cursor:pointer; }}
    .status {{ align-self:center; min-width:8em; color:{theme["muted"]}; font-size:13px; }}
    main {{ padding:24px 12px 48px; }}
  </style>
</head>
<body>
  <div class="toolbar">
    <button type="button" id="copyBtn">复制到公众号</button>
    <span class="status" id="copyStatus">复制正文样式</span>
  </div>
  <main>
    {article}
  </main>
  <script>
    const btn = document.getElementById('copyBtn');
    const status = document.getElementById('copyStatus');
    btn.addEventListener('click', async () => {{
      const article = document.getElementById('wechat-article');
      const html = article.outerHTML;
      try {{
        await navigator.clipboard.write([
          new ClipboardItem({{
            'text/html': new Blob([html], {{ type: 'text/html' }}),
            'text/plain': new Blob([article.innerText], {{ type: 'text/plain' }})
          }})
        ]);
        status.textContent = '已复制，可粘贴';
      }} catch (error) {{
        const range = document.createRange();
        range.selectNode(article);
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
        document.execCommand('copy');
        selection.removeAllRanges();
        status.textContent = '已复制，可粘贴';
      }}
    }});
  </script>
</body>
</html>
"""


def first_heading(markdown: str, fallback: str) -> str:
    for line in markdown.splitlines():
        match = re.match(r"^#\s+(.+)$", line.strip())
        if match:
            return match.group(1).strip()
    return fallback


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert Markdown to WeChat-ready HTML preview.")
    parser.add_argument("input", type=Path, help="Markdown input file")
    parser.add_argument("-o", "--output", type=Path, help="Output HTML file")
    parser.add_argument("--theme", type=Path, help="Optional JSON theme file")
    args = parser.parse_args()

    markdown = args.input.read_text(encoding="utf-8")
    theme = load_theme(args.theme)
    title = first_heading(markdown, args.input.stem)
    article_html = render_blocks(markdown, theme)
    output = args.output or args.input.with_suffix(".wechat.html")
    output.write_text(render_page(article_html, title, theme), encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
