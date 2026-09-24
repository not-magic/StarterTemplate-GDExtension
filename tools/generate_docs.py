#!/usr/bin/env python3
"""Generate Markdown documentation from Godot-style class XML files.

Reads every *.xml file in doc_classes/ and writes a corresponding
*.md file to docs/, one per class.

Usage:
    python3 tools/generate_docs.py [--src doc_classes] [--out docs]
"""

import argparse
import xml.etree.ElementTree as ET
from pathlib import Path


def text(el):
    """Return the stripped text content of an element, or '' if empty/None."""
    if el is None or el.text is None:
        return ""
    return el.text.strip()


def format_description(raw):
    """Convert BBCode-ish Godot doc markup into plain Markdown text."""
    if not raw:
        return ""
    out = raw
    replacements = [
        ("[b]", "**"), ("[/b]", "**"),
        ("[i]", "_"), ("[/i]", "_"),
        ("[code]", "`"), ("[/code]", "`"),
        ("[codeblock]", "\n```\n"), ("[/codeblock]", "\n```\n"),
    ]
    for old, new in replacements:
        out = out.replace(old, new)
    return out.strip()


def format_type(type_name):
    return f"`{type_name}`" if type_name else ""


def render_params(params):
    parts = []
    for p in params:
        name = p.get("name", "")
        ptype = p.get("type", "")
        default = p.get("default")
        piece = f"{format_type(ptype)} {name}"
        if default is not None:
            piece += f" = {default}"
        parts.append(piece)
    return ", ".join(parts)


def render_class(root, class_name):
    lines = []
    inherits = root.get("inherits")

    lines.append(f"# {class_name}")
    lines.append("")
    if inherits:
        lines.append(f"**Inherits:** `{inherits}`")
        lines.append("")

    brief = format_description(text(root.find("brief_description")))
    if brief:
        lines.append(brief)
        lines.append("")

    description = format_description(text(root.find("description")))
    if description:
        lines.append("## Description")
        lines.append("")
        lines.append(description)
        lines.append("")

    tutorials = root.find("tutorials")
    if tutorials is not None:
        links = tutorials.findall("link")
        if links:
            lines.append("## Tutorials")
            lines.append("")
            for link in links:
                title = link.get("title")
                url = text(link)
                label = title if title else url
                if url:
                    lines.append(f"- [{label}]({url})")
            lines.append("")

    members = root.find("members")
    if members is not None:
        member_list = members.findall("member")
        if member_list:
            lines.append("## Properties")
            lines.append("")
            lines.append("| Type | Name | Default | Description |")
            lines.append("|------|------|---------|-------------|")
            for m in member_list:
                mtype = format_type(m.get("type", ""))
                name = m.get("name", "")
                default = m.get("default", "")
                desc = format_description(text(m)).replace("\n", " ")
                lines.append(f"| {mtype} | {name} | `{default}` | {desc} |")
            lines.append("")

    methods = root.find("methods")
    if methods is not None:
        method_list = methods.findall("method")
        if method_list:
            lines.append("## Methods")
            lines.append("")
            for meth in method_list:
                name = meth.get("name", "")
                ret_el = meth.find("return")
                ret_type = ret_el.get("type") if ret_el is not None else "void"
                params = meth.findall("param")
                qualifiers = meth.get("qualifiers", "")
                sig = f"{format_type(ret_type)} **{name}**({render_params(params)})"
                if qualifiers:
                    sig += f" {qualifiers}"
                lines.append(f"### {name}")
                lines.append("")
                lines.append(sig)
                lines.append("")
                desc = format_description(text(meth.find("description")))
                if desc:
                    lines.append(desc)
                    lines.append("")

    signals = root.find("signals")
    if signals is not None:
        signal_list = signals.findall("signal")
        if signal_list:
            lines.append("## Signals")
            lines.append("")
            for sig in signal_list:
                name = sig.get("name", "")
                params = sig.findall("param")
                lines.append(f"### {name}({render_params(params)})")
                lines.append("")
                desc = format_description(text(sig.find("description")))
                if desc:
                    lines.append(desc)
                    lines.append("")

    constants = root.find("constants")
    if constants is not None:
        const_list = constants.findall("constant")
        if const_list:
            lines.append("## Constants")
            lines.append("")
            lines.append("| Name | Value | Description |")
            lines.append("|------|-------|-------------|")
            for c in const_list:
                name = c.get("name", "")
                value = c.get("value", "")
                desc = format_description(text(c)).replace("\n", " ")
                lines.append(f"| {name} | `{value}` | {desc} |")
            lines.append("")

    theme_items = root.find("theme_items")
    if theme_items is not None:
        item_list = theme_items.findall("theme_item")
        if item_list:
            lines.append("## Theme Properties")
            lines.append("")
            lines.append("| Type | Name | Default | Description |")
            lines.append("|------|------|---------|-------------|")
            for item in item_list:
                itype = format_type(item.get("type", ""))
                name = item.get("name", "")
                default = item.get("default", "")
                desc = format_description(text(item)).replace("\n", " ")
                lines.append(f"| {itype} | {name} | `{default}` | {desc} |")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_sidebar(class_names):
    lines = ["# Classes", ""]
    for name in sorted(class_names, key=str.lower):
        lines.append(f"- [{name}]({name})")
    return "\n".join(lines).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--src", default="doc_classes", help="Directory containing class XML files")
    parser.add_argument("--out", default="docs", help="Output directory for Markdown files")
    args = parser.parse_args()

    src_dir = Path(args.src)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    xml_files = sorted(src_dir.glob("*.xml"))
    if not xml_files:
        print(f"No XML files found in {src_dir}")
        return

    class_names = []
    for xml_path in xml_files:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        class_name = root.get("name", xml_path.stem)
        class_names.append(class_name)
        markdown = render_class(root, class_name)
        out_path = out_dir / f"{xml_path.stem}.md"
        out_path.write_text(markdown, encoding="utf-8")
        print(f"Wrote {out_path}")

    sidebar_path = out_dir / "_Sidebar.md"
    sidebar_path.write_text(render_sidebar(class_names), encoding="utf-8")
    print(f"Wrote {sidebar_path}")


if __name__ == "__main__":
    main()
