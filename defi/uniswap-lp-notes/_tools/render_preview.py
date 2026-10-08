# -*- coding: utf-8 -*-
"""
把生成的 SVG 光栅化成 PNG，用于视觉校验。
只支持本项目中实际用到的 SVG 子集：
  rect(rx/opacity) line(dash/marker) path(M,L,Q; stroke/dash/marker)
  circle text(anchor/weight/rotate) marker
"""
import os
import re
import math
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SVGDIR = os.path.join(ROOT, "figures")
OUTDIR = os.path.join(ROOT, "figures", "preview")
os.makedirs(OUTDIR, exist_ok=True)

FONT_REG = r"C:\Windows\Fonts\msyh.ttc"
FONT_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
_fontcache = {}


def font(size, weight):
    key = (int(size), weight)
    if key not in _fontcache:
        path = FONT_BOLD if str(weight) in ("700", "bold", "800", "900") else FONT_REG
        try:
            _fontcache[key] = ImageFont.truetype(path, int(round(size)))
        except Exception:
            _fontcache[key] = ImageFont.load_default()
    return _fontcache[key]


def strip_ns(tag):
    return tag.split("}", 1)[1] if "}" in tag else tag


def hex2rgba(col, opacity=1.0):
    if col is None or col in ("none", ""):
        return None
    col = col.strip()
    if col.startswith("#"):
        h = col[1:]
        if len(h) == 3:
            h = "".join(ch * 2 for ch in h)
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    elif col.startswith("rgb"):
        nums = re.findall(r"[\d.]+", col)
        r, g, b = int(float(nums[0])), int(float(nums[1])), int(float(nums[2]))
    else:
        named = {"white": (255, 255, 255), "black": (0, 0, 0)}
        r, g, b = named.get(col.lower(), (0, 0, 0))
    a = int(round(255 * max(0.0, min(1.0, opacity))))
    return (r, g, b, a)


def parse_dash(s):
    if not s:
        return None
    return [float(x) for x in re.split(r"[,\s]+", s.strip()) if x]


def dashed_points(p0, p1, pattern):
    """把直线按 dash 模式切成若干段"""
    if not pattern:
        return [(p0, p1)]
    total = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    if total <= 0:
        return []
    ux, uy = (p1[0] - p0[0]) / total, (p1[1] - p0[1]) / total
    segs, pos, i, on = [], 0.0, 0, True
    while pos < total:
        step = pattern[i % len(pattern)]
        nxt = min(pos + step, total)
        if on:
            segs.append(((p0[0] + ux * pos, p0[1] + uy * pos),
                         (p0[0] + ux * nxt, p0[1] + uy * nxt)))
        pos, i, on = nxt, i + 1, not on
    return segs


def flatten_path(d):
    """支持 M / L / Q / Z 的最小实现，返回 (子路径列表, 闭合标记)"""
    tokens = re.findall(r"[MLQZmlqz]|-?\d*\.?\d+(?:e-?\d+)?", d)
    subs, cur, start = [], [], None
    i = 0
    cmd = None
    while i < len(tokens):
        t = tokens[i]
        if t.upper() in "MLQZ":
            cmd = t.upper()
            i += 1
            if cmd == "Z":
                if cur:
                    cur.append(start)
                    subs.append(cur)
                    cur = []
                continue
        if cmd == "M" or cmd == "L":
            x, y = float(tokens[i]), float(tokens[i + 1])
            i += 2
            if cmd == "M":
                if cur:
                    subs.append(cur)
                cur = [(x, y)]
                start = (x, y)
                cmd = "L"
            else:
                cur.append((x, y))
        elif cmd == "Q":
            cx, cy, x, y = (float(tokens[i]), float(tokens[i + 1]),
                            float(tokens[i + 2]), float(tokens[i + 3]))
            i += 4
            p0 = cur[-1] if cur else (cx, cy)
            for k in range(1, 25):
                u = k / 24.0
                bx = (1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * cx + u * u * x
                by = (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * cy + u * u * y
                cur.append((bx, by))
        else:
            i += 1
    if cur:
        subs.append(cur)
    return subs


def draw_arrow(dr, tip, direction, color, size=9.0):
    ux, uy = direction
    n = math.hypot(ux, uy)
    if n == 0:
        return
    ux, uy = ux / n, uy / n
    px, py = -uy, ux
    back = (tip[0] - ux * size, tip[1] - uy * size)
    a = (back[0] + px * size * 0.55, back[1] + py * size * 0.55)
    b = (back[0] - px * size * 0.55, back[1] - py * size * 0.55)
    dr.polygon([tip, a, b], fill=color)


def render(svg_path, png_path, scale=1.0):
    tree = ET.parse(svg_path)
    root = tree.getroot()

    W = float(root.get("width"))
    H = float(root.get("height"))
    SS = 2  # 超采样，抗锯齿
    img = Image.new("RGBA", (int(W * SS), int(H * SS)), (255, 255, 255, 255))
    dr = ImageDraw.Draw(img, "RGBA")

    def S(v):
        return float(v) * SS

    # 收集 marker 颜色
    markers = {}
    for el in root.iter():
        if strip_ns(el.tag) == "marker":
            mid = el.get("id")
            for ch in el:
                fc = ch.get("fill")
                if fc:
                    markers[mid] = fc

    def marker_color(ref):
        if not ref:
            return None
        m = re.search(r"#([\w-]+)", ref)
        return markers.get(m.group(1)) if m else None

    def walk(parent):
        for el in parent:
            tag = strip_ns(el.tag)
            a = el.attrib
            if tag in ("defs", "marker"):
                continue
            op = float(a.get("opacity", 1.0))

            if tag == "rect":
                x, y = S(a.get("x", 0)), S(a.get("y", 0))
                w, h = S(a.get("width", 0)), S(a.get("height", 0))
                rx = S(a.get("rx", 0))
                fill = hex2rgba(a.get("fill"), op)
                stroke = hex2rgba(a.get("stroke"), op)
                sw = S(a.get("stroke-width", 1))
                box = [x, y, x + w, y + h]
                if rx > 0:
                    dr.rounded_rectangle(box, radius=rx, fill=fill,
                                         outline=stroke, width=max(1, int(round(sw))))
                else:
                    dr.rectangle(box, fill=fill, outline=stroke,
                                 width=max(1, int(round(sw))))

            elif tag == "line":
                p0 = (S(a["x1"]), S(a["y1"]))
                p1 = (S(a["x2"]), S(a["y2"]))
                col = hex2rgba(a.get("stroke"), op)
                sw = max(1, int(round(S(a.get("stroke-width", 1)))))
                dash = parse_dash(a.get("stroke-dasharray"))
                if col:
                    for (q0, q1) in dashed_points(p0, p1, [d * SS for d in dash] if dash else None):
                        dr.line([q0, q1], fill=col, width=sw)
                mc = marker_color(a.get("marker-end"))
                if mc:
                    draw_arrow(dr, p1, (p1[0] - p0[0], p1[1] - p0[1]),
                               hex2rgba(mc, op), size=S(9))

            elif tag == "circle":
                cx, cy, r = S(a["cx"]), S(a["cy"]), S(a["r"])
                fill = hex2rgba(a.get("fill"), op)
                stroke = hex2rgba(a.get("stroke"), op)
                sw = max(1, int(round(S(a.get("stroke-width", 1)))))
                dr.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill,
                           outline=stroke, width=sw)

            elif tag == "path":
                d = a.get("d", "")
                col = hex2rgba(a.get("stroke"), op)
                sw = max(1, int(round(S(a.get("stroke-width", 1)))))
                dash = parse_dash(a.get("stroke-dasharray"))
                subs = flatten_path(d)
                if col:
                    for sub in subs:
                        pts = [(S(px), S(py)) for px, py in sub]
                        if dash:
                            for i in range(len(pts) - 1):
                                for (q0, q1) in dashed_points(
                                        pts[i], pts[i + 1], [x * SS for x in dash]):
                                    dr.line([q0, q1], fill=col, width=sw)
                        else:
                            if len(pts) > 1:
                                dr.line(pts, fill=col, width=sw, joint="curve")
                mc = marker_color(a.get("marker-end"))
                if mc and subs and len(subs[-1]) >= 2:
                    tip = (S(subs[-1][-1][0]), S(subs[-1][-1][1]))
                    prv = (S(subs[-1][-2][0]), S(subs[-1][-2][1]))
                    draw_arrow(dr, tip, (tip[0] - prv[0], tip[1] - prv[1]),
                               hex2rgba(mc, op), size=S(9))

            elif tag == "text":
                txt = "".join(el.itertext())
                if not txt.strip():
                    continue
                size = S(a.get("font-size", 12))
                f = font(size, a.get("font-weight", "normal"))
                col = hex2rgba(a.get("fill"), op) or (0, 0, 0, 255)
                x, y = S(a["x"]), S(a["y"])
                anchor = a.get("text-anchor", "start")
                bb = dr.textbbox((0, 0), txt, font=f)
                tw = bb[2] - bb[0]
                if anchor == "middle":
                    x -= tw / 2
                elif anchor == "end":
                    x -= tw
                rot = a.get("transform")
                if rot:
                    m = re.search(r"rotate\(([-\d.]+)", rot)
                    if m:
                        ang = float(m.group(1))
                        tmp = Image.new("RGBA", (int(tw + size * 2), int(size * 2)),
                                        (0, 0, 0, 0))
                        td = ImageDraw.Draw(tmp)
                        td.text((size, size * 0.5), txt, font=f, fill=col)
                        tmp = tmp.rotate(-ang, expand=True, resample=Image.BICUBIC)
                        img.alpha_composite(tmp, (int(x - size), int(y - size * 1.3)))
                        continue
                dr.text((x, y - size * 0.78), txt, font=f, fill=col)

    walk(root)

    img = img.convert("RGB").resize((int(W * scale), int(H * scale)), Image.LANCZOS)
    img.save(png_path, "PNG")
    return png_path


if __name__ == "__main__":
    files = sorted(f for f in os.listdir(SVGDIR) if f.endswith(".svg"))
    for f in files:
        out = os.path.join(OUTDIR, f[:-4] + ".png")
        try:
            render(os.path.join(SVGDIR, f), out)
            print(f"  OK  {f:38s} -> {os.path.getsize(out)/1024:7.1f} KB")
        except Exception as e:
            print(f"  ERR {f}: {type(e).__name__}: {e}")
