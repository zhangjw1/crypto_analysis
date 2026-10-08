# -*- coding: utf-8 -*-
"""
对生成的 SVG 做程序化校验：
  1. 所有图元是否越出画布
  2. 文字是否超出画布
  3. 文字块之间是否显著重叠（标签打架）
  4. 是否存在零尺寸/不可见图元
  5. 关键曲线端点是否符合预期数值
"""
import os
import re
import math
import xml.etree.ElementTree as ET

from PIL import ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SVGDIR = os.path.join(ROOT, "figures")

FONT_REG = r"C:\Windows\Fonts\msyh.ttc"
FONT_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
_fc = {}


def font(size, weight):
    k = (int(size), weight)
    if k not in _fc:
        p = FONT_BOLD if str(weight) in ("700", "bold") else FONT_REG
        _fc[k] = ImageFont.truetype(p, int(round(size)))
    return _fc[k]


def strip_ns(t):
    return t.split("}", 1)[1] if "}" in t else t


def tw(txt, size, weight):
    f = font(size, weight)
    try:
        b = f.getbbox(txt)
    except Exception:
        return len(txt) * size * 0.6
    return b[2] - b[0]


def flatten_path(d):
    toks = re.findall(r"[MLQZmlqz]|-?\d*\.?\d+", d)
    subs, cur = [], []
    cmd, i = None, 0
    while i < len(toks):
        t = toks[i]
        if t.upper() in "MLQZ":
            cmd = t.upper()
            i += 1
            if cmd == "Z":
                continue
        if cmd in ("M", "L"):
            x, y = float(toks[i]), float(toks[i + 1])
            i += 2
            if cmd == "M":
                if cur:
                    subs.append(cur)
                cur = [(x, y)]
                cmd = "L"
            else:
                cur.append((x, y))
        elif cmd == "Q":
            cx, cy, x, y = (float(toks[i]), float(toks[i + 1]),
                            float(toks[i + 2]), float(toks[i + 3]))
            i += 4
            p0 = cur[-1] if cur else (cx, cy)
            for k in range(1, 21):
                u = k / 20.0
                cur.append(((1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * cx + u * u * x,
                            (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * cy + u * u * y))
        else:
            i += 1
    if cur:
        subs.append(cur)
    return subs


def bbox_overlap(a, b):
    x0 = max(a[0], b[0]); y0 = max(a[1], b[1])
    x1 = min(a[2], b[2]); y1 = min(a[3], b[3])
    if x1 <= x0 or y1 <= y0:
        return 0.0
    inter = (x1 - x0) * (y1 - y0)
    amin = min((a[2] - a[0]) * (a[3] - a[1]), (b[2] - b[0]) * (b[3] - b[1]))
    return inter / amin if amin > 0 else 0.0


def check(path):
    issues = []
    root = ET.parse(path).getroot()
    W = float(root.get("width")); H = float(root.get("height"))
    name = os.path.basename(path)

    texts = []          # (bbox, content)
    pad = 6.0           # 容差

    for el in root.iter():
        tag = strip_ns(el.tag)
        a = el.attrib
        if tag in ("defs", "marker", "svg"):
            continue

        if tag == "rect":
            x, y = float(a.get("x", 0)), float(a.get("y", 0))
            w, h = float(a.get("width", 0)), float(a.get("height", 0))
            if w <= 0 or h <= 0:
                issues.append(f"[零尺寸 rect] x={x} y={y} w={w} h={h}")
            if x < -pad or y < -pad or x + w > W + pad or y + h > H + pad:
                issues.append(f"[越界 rect] ({x:.0f},{y:.0f}) {w:.0f}x{h:.0f}")

        elif tag == "line":
            for (px, py) in [(float(a["x1"]), float(a["y1"])),
                             (float(a["x2"]), float(a["y2"]))]:
                if px < -pad or py < -pad or px > W + pad or py > H + pad:
                    issues.append(f"[越界 line] ({px:.0f},{py:.0f})")

        elif tag == "circle":
            cx, cy, r = float(a["cx"]), float(a["cy"]), float(a["r"])
            if cx - r < -pad or cy - r < -pad or cx + r > W + pad or cy + r > H + pad:
                issues.append(f"[越界 circle] ({cx:.0f},{cy:.0f}) r={r}")

        elif tag == "path":
            for sub in flatten_path(a.get("d", "")):
                for (px, py) in sub:
                    if px < -pad or py < -pad or px > W + pad or py > H + pad:
                        issues.append(f"[越界 path] ({px:.0f},{py:.0f})")
                        break

        elif tag == "text":
            txt = "".join(el.itertext())
            if not txt.strip():
                continue
            size = float(a.get("font-size", 12))
            weight = a.get("font-weight", "normal")
            x, y = float(a["x"]), float(a["y"])
            rot = a.get("transform")
            w = tw(txt, size, weight)
            anchor = a.get("text-anchor", "start")
            if anchor == "middle":
                x0 = x - w / 2
            elif anchor == "end":
                x0 = x - w
            else:
                x0 = x
            if rot:   # 旋转文字不做重叠检测，只查越界（用近似包围盒）
                if x0 < -pad or y - w < -pad or x0 + w > W + pad or y + w > H + pad:
                    issues.append(f"[越界 text·旋转] '{txt[:18]}'")
                continue
            bb = (x0, y - size * 0.82, x0 + w, y + size * 0.24)
            if bb[0] < -pad or bb[1] < -pad or bb[2] > W + pad or bb[3] > H + pad:
                issues.append(f"[越界 text] '{txt[:24]}' x=[{bb[0]:.0f},{bb[2]:.0f}] y=[{bb[1]:.0f},{bb[3]:.0f}]")
            texts.append((bb, txt))

    # 文字重叠
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            ov = bbox_overlap(texts[i][0], texts[j][0])
            if ov > 0.35:
                issues.append(f"[文字重叠 {ov*100:.0f}%] '{texts[i][1][:20]}'  ×  '{texts[j][1][:20]}'")

    return name, W, H, len(texts), issues


# ---------- 语义抽查：关键曲线端点 ----------
def semantic_checks():
    out = []
    # fig-02 / fig-04 的 V3 弧：L=10, pa=0.05, pb=0.2 → 端点 (22.36,0) 与 (0,2.236)
    L, pa, pb = 10.0, 0.05, 0.20
    x_at_pa = L * (1 / math.sqrt(pa) - 1 / math.sqrt(pb))
    y_at_pb = L * (math.sqrt(pb) - math.sqrt(pa))
    out.append(("V3 弧左端点 x (应 ≈22.36)", round(x_at_pa, 2)))
    out.append(("V3 弧上端点 y (应 ≈2.236)", round(y_at_pb, 2)))
    x_at_P10 = L * (1 / math.sqrt(0.10) - 1 / math.sqrt(pb))
    y_at_P10 = L * (math.sqrt(0.10) - math.sqrt(pa))
    out.append(("P=0.10 处 (应 ≈9.262, 0.926)", (round(x_at_P10, 3), round(y_at_P10, 3))))
    # 主例子 E
    L2 = 10000 / (0.154846 + 0.051317)
    x_e = L2 * 0.154846
    y_e = L2 * 0.051317
    y_top = L2 * (math.sqrt(1.4) - math.sqrt(0.9))
    hold14 = x_e * 1.4 + y_e
    hold10 = x_e * 10 + y_e
    out.append(("例子E 初始持仓 (应 ≈7510.6, 2489.4)", (round(x_e, 1), round(y_e, 1))))
    out.append(("例子E P=1.4 时 IL (应 ≈−12.5%)", f"{(y_top/hold14-1)*100:.1f}%"))
    out.append(("例子E P=10 时 IL (应 ≈−85.3%)", f"{(y_top/hold10-1)*100:.1f}%"))
    # 资本效率
    for lo, hi in [(0.05, 0.2), (0.08, 0.125), (0.09, 0.11), (0.099, 0.101)]:
        P = math.sqrt(lo * hi)
        E = 1 / (1 - math.sqrt(lo / P))
        out.append((f"资本效率 [{lo},{hi}]", f"{E:.1f}×"))
    return out


if __name__ == "__main__":
    print("=" * 88)
    print("SVG 校验")
    print("=" * 88)
    total = 0
    for f in sorted(os.listdir(SVGDIR)):
        if not f.endswith(".svg"):
            continue
        name, W, H, nt, issues = check(os.path.join(SVGDIR, f))
        total += len(issues)
        flag = "OK " if not issues else "!! "
        print(f"\n{flag}{name}   {W:.0f}x{H:.0f}   文本块 {nt}")
        for s in issues[:40]:
            print("      -", s)
        if len(issues) > 40:
            print(f"      ... 另有 {len(issues)-40} 条")
    print("\n" + "=" * 88)
    print(f"合计问题：{total}")
    print("=" * 88)
    print("\n数值抽查：")
    for k, v in semantic_checks():
        print(f"  {k:38s} {v}")
