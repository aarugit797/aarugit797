#!/usr/bin/env python3
"""Generate the animated terminal SVG from the static ASCII header source.

Run from the repository root or any directory:
    python scripts/animate_header.py

Uses only Python's standard library. The pre-converted ASCII portrait and the
terminal text are in assets/profile-hero-base.svg. This script adds self-contained
SVG SMIL clipping animations so GitHub can display them as an animated image.
"""
from pathlib import Path
import xml.etree.ElementTree as ET

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)
def q(tag: str) -> str:
    return f"{{{SVG_NS}}}{tag}"

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SOURCE = ASSETS / "profile-hero-base.svg"
OUTPUT = ASSETS / "profile-hero.svg"

PORTRAIT_X = 708.0
PORTRAIT_WIDTH = 478.0
PORTRAIT_START = 0.48
PORTRAIT_STAGGER = 0.055
PORTRAIT_DURATION = 0.58
TEXT_DURATION = 0.40


def main() -> None:
    tree = ET.parse(SOURCE)
    root = tree.getroot()
    defs = next((element for element in root if element.tag == q("defs")), None)
    if defs is None:
        defs = ET.Element(q("defs"))
        root.insert(0, defs)

    portrait_rows = []
    terminal_text = []
    for element in root.iter(q("text")):
        try:
            x = float(element.attrib.get("x", "9999"))
            y = float(element.attrib.get("y", "-1"))
            font_size = float(element.attrib.get("font-size", "13"))
        except ValueError:
            continue
        text_content = "".join(element.itertext())
        if not text_content.strip():
            continue
        if abs(x - PORTRAIT_X) < 0.1:
            portrait_rows.append((element, x, y, font_size, text_content))
        elif x < 700 and y >= 30:
            terminal_text.append((element, x, y, font_size, text_content))

    portrait_cursors = []
    for index, (element, x, y, font_size, text_content) in enumerate(portrait_rows):
        start = PORTRAIT_START + index * PORTRAIT_STAGGER
        clip_id = f"portrait-row-clip-{index:03d}"
        clip = ET.SubElement(defs, q("clipPath"), {
            "id": clip_id, "clipPathUnits": "userSpaceOnUse"
        })
        clip_rect = ET.SubElement(clip, q("rect"), {
            "x": f"{x:g}", "y": f"{y - 6.2:g}", "width": "0", "height": "8.2"
        })
        ET.SubElement(clip_rect, q("animate"), {
            "attributeName": "width", "values": f"0;{PORTRAIT_WIDTH:g}",
            "begin": f"{start:.3f}s", "dur": f"{PORTRAIT_DURATION:.3f}s",
            "fill": "freeze", "calcMode": "linear"
        })
        element.set("clip-path", f"url(#{clip_id})")

        # Skip the blank leading spaces when positioning the cursor, so it follows
        # the visible ASCII characters instead of crossing empty space.
        leading = len(text_content) - len(text_content.lstrip())
        right_edge = len(text_content.rstrip())
        char_width = font_size * 0.60
        cursor_start = x + leading * char_width
        cursor_end = x + right_edge * char_width
        cursor_begin = start + ((cursor_start - x) / PORTRAIT_WIDTH) * PORTRAIT_DURATION
        cursor_duration = max(0.08, ((cursor_end - cursor_start) / PORTRAIT_WIDTH) * PORTRAIT_DURATION)
        cursor = ET.Element(q("rect"), {
            "x": f"{cursor_start:g}", "y": f"{y - 5.8:g}", "width": "2.5",
            "height": "5.8", "rx": "0.5", "fill": "#58a6ff", "opacity": "0",
            "pointer-events": "none"
        })
        ET.SubElement(cursor, q("animate"), {
            "attributeName": "x", "values": f"{cursor_start:g};{cursor_end:g}",
            "begin": f"{cursor_begin:.3f}s", "dur": f"{cursor_duration:.3f}s", "fill": "freeze"
        })
        ET.SubElement(cursor, q("animate"), {
            "attributeName": "opacity", "values": "0;0.95;0", "keyTimes": "0;0.06;1",
            "begin": f"{cursor_begin:.3f}s", "dur": f"{cursor_duration:.3f}s", "fill": "freeze"
        })
        portrait_cursors.append(cursor)

    baselines = sorted({round(row[2], 2) for row in terminal_text})
    baseline_rank = {baseline: index for index, baseline in enumerate(baselines)}
    for index, (element, x, y, font_size, text_content) in enumerate(terminal_text):
        # Rows sharing a baseline reveal at the same time, keeping key/value pairs together.
        start = 0.22 + baseline_rank[round(y, 2)] * 0.13
        target_width = max(12.0, min(670.0 - x, len(text_content.strip()) * font_size * 0.615 + 6.0))
        clip_id = f"terminal-text-clip-{index:03d}"
        clip = ET.SubElement(defs, q("clipPath"), {
            "id": clip_id, "clipPathUnits": "userSpaceOnUse"
        })
        clip_rect = ET.SubElement(clip, q("rect"), {
            "x": f"{x:g}", "y": f"{y - font_size * 1.20:g}",
            "width": "0", "height": f"{font_size * 1.65:g}"
        })
        ET.SubElement(clip_rect, q("animate"), {
            "attributeName": "width", "values": f"0;{target_width:.2f}",
            "begin": f"{start:.3f}s", "dur": f"{TEXT_DURATION:.3f}s", "fill": "freeze",
            "calcMode": "linear"
        })
        element.set("clip-path", f"url(#{clip_id})")

    for cursor in portrait_cursors:
        root.append(cursor)

    # The last shell prompt cursor starts blinking after the lines have appeared.
    for element in root.iter(q("rect")):
        try:
            x = float(element.attrib.get("x", "9999"))
            y = float(element.attrib.get("y", "-1"))
        except ValueError:
            continue
        if abs(x - 224.0) < 0.1 and abs(y - 551.0) < 0.1:
            element.set("opacity", "0")
            start = max(4.5, 0.22 + (len(baselines) - 1) * 0.13 + TEXT_DURATION + 0.15)
            ET.SubElement(element, q("animate"), {
                "attributeName": "opacity", "values": "0;1;0", "keyTimes": "0;0.5;1",
                "dur": "1s", "begin": f"{start:.2f}s", "repeatCount": "indefinite"
            })
            break

    tree.write(OUTPUT, encoding="utf-8", xml_declaration=True)
    ET.parse(OUTPUT)  # quick validity check
    print(f"Generated {OUTPUT}: {len(portrait_rows)} portrait rows and {len(baselines)} text lines.")

if __name__ == "__main__":
    main()
