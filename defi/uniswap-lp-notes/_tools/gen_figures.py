# -*- coding: utf-8 -*-
"""
生成 uniswap-lp-notes 的全部 SVG 插图。
不依赖 matplotlib，直接输出 SVG。
"""
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "figures")
os.makedirs(OUT, exist_ok=True)

# ---------- 配色 ----------
C_AXIS = "#334155"
C_GRID = "#e8edf3"
C_V2 = "#2563eb"
C_V3 = "#dc2626"
C_RAY = "#b6c2d1"
C_ACC = "#f59e0b"
C_GOOD = "#16a34a"
C_BAD = "#dc2626"
C_TXT = "#0f172a"
C_MUTE = "#64748b"
C_PANEL = "#f8fafc"
C_BORDER = "#cbd5e1"

FONT = "Microsoft YaHei, PingFang SC, Hiragino Sans GB, Segoe UI, sans-serif"

ARROW_COLORS = {
    "axis": C_AXIS, "v2": C_V2, "v3": C_V3, "ray": C_RAY,
    "acc": C_ACC, "good": C_GOOD, "bad": C_BAD, "mute": C_MUTE,
}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Canvas:
    def __init__(self, w, h, title=None, subtitle=None):
        self.w, self.h = w, h
        self.body = []
        self.title = title
        self.subtitle = subtitle

    def raw(self, s):
        self.body.append(s)
        return self

    # ---- 基础图元 ----
    def rect(self, x, y, w, h, fill="none", stroke="none", sw=1, rx=0, opacity=None):
        o = f' opacity="{opacity}"' if opacity is not None else ''
        self.raw(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
                 f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}" rx="{rx}"{o}/>')
        return self

    def line(self, x1, y1, x2, y2, stroke=C_AXIS, sw=1.5, dash=None,
             arrow=None, cap="round", opacity=None):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        a = f' marker-end="url(#ar-{arrow})"' if arrow else ''
        o = f' opacity="{opacity}"' if opacity is not None else ''
        self.raw(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                 f'stroke="{stroke}" stroke-width="{sw}"{d}{a}{o} stroke-linecap="{cap}"/>')
        return self

    def path(self, d, stroke=C_AXIS, sw=2, fill="none", dash=None,
             arrow=None, opacity=None):
        ds = f' stroke-dasharray="{dash}"' if dash else ''
        a = f' marker-end="url(#ar-{arrow})"' if arrow else ''
        o = f' opacity="{opacity}"' if opacity is not None else ''
        self.raw(f'<path d="{d}" stroke="{stroke}" stroke-width="{sw}" fill="{fill}"'
                 f'{ds}{a}{o} stroke-linecap="round" stroke-linejoin="round"/>')
        return self

    def circle(self, cx, cy, r, fill=C_AXIS, stroke="none", sw=1, opacity=None):
        o = f' opacity="{opacity}"' if opacity is not None else ''
        self.raw(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
                 f'stroke="{stroke}" stroke-width="{sw}"{o}/>')
        return self

    def text(self, x, y, s, size=13, fill=C_TXT, anchor="start",
             weight="normal", op=None, rot=None):
        o = f' opacity="{op}"' if op is not None else ''
        r = f' transform="rotate({rot} {x:.1f} {y:.1f})"' if rot else ''
        self.raw(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
                 f'fill="{fill}" text-anchor="{anchor}" font-weight="{weight}"{o}{r}>{esc(s)}</text>')
        return self

    def mtext(self, x, y, lines, size=12, fill=C_MUTE, lh=None, anchor="start"):
        lh = lh or size + 5
        for i, ln in enumerate(lines):
            self.text(x, y + i * lh, ln, size=size, fill=fill, anchor=anchor)
        return self

    # ---- 复合 ----
    def panel(self, x, y, w, h, label=None, fill=C_PANEL):
        self.rect(x, y, w, h, fill=fill, stroke=C_BORDER, sw=1, rx=10)
        if label:
            self.text(x + 14, y + 24, label, size=14, weight="700", fill=C_AXIS)
        return self

    def note(self, x, y, w, lines, fill="#fffbeb", stroke="#fcd34d", accent="#92400e"):
        lh = 19
        h = len(lines) * lh + 20
        self.rect(x, y, w, h, fill=fill, stroke=stroke, sw=1, rx=8)
        self.rect(x, y, 4, h, fill=accent, rx=2)
        for i, ln in enumerate(lines):
            self.text(x + 14, y + 22 + i * lh, ln, size=12.5, fill=accent)
        return self

    def render(self):
        defs = ['<marker id="ar-axis" viewBox="0 0 10 10" refX="8.5" refY="5" '
                'markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
                f'<path d="M 0 1 L 9 5 L 0 9 z" fill="{C_AXIS}"/></marker>']
        for name, col in ARROW_COLORS.items():
            if name == "axis":
                continue
            defs.append(f'<marker id="ar-{name}" viewBox="0 0 10 10" refX="8.5" refY="5" '
                        f'markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
                        f'<path d="M 0 1 L 9 5 L 0 9 z" fill="{col}"/></marker>')

        head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
                f'viewBox="0 0 {self.w} {self.h}">'
                f'<defs>{"".join(defs)}</defs>'
                f'<rect width="{self.w}" height="{self.h}" fill="#ffffff"/>')
        t = ""
        if self.title:
            t += f'<text x="34" y="40" font-family="{FONT}" font-size="22" font-weight="700" ' \
                 f'fill="{C_TXT}">{esc(self.title)}</text>'
        if self.subtitle:
            t += f'<text x="34" y="64" font-family="{FONT}" font-size="13.5" ' \
                 f'fill="{C_MUTE}">{esc(self.subtitle)}</text>'
        return head + t + "".join(self.body) + "</svg>"


class Plot:
    """数据坐标 → 像素坐标"""
    def __init__(self, x0, y0, x1, y1, dx0, dy0, dx1, dy1):
        self.px0, self.py0, self.px1, self.py1 = x0, y0, x1, y1
        self.dx0, self.dy0, self.dx1, self.dy1 = dx0, dy0, dx1, dy1

    def X(self, dx):
        return self.px0 + (dx - self.dx0) / (self.dx1 - self.dx0) * (self.px1 - self.px0)

    def Y(self, dy):
        return self.py1 - (dy - self.dy0) / (self.dy1 - self.dy0) * (self.py1 - self.py0)

    def axes(self, c, xlabel, ylabel, xticks=None, yticks=None,
             xfmt="{:.2f}", yfmt="{:.2f}", grid=True, xlabel_pad=44, ylabel_pad=None):
        # 网格
        if grid:
            for t in (xticks or []):
                c.line(self.X(t), self.py0, self.X(t), self.py1, stroke=C_GRID, sw=1)
            for t in (yticks or []):
                c.line(self.px0, self.Y(t), self.px1, self.Y(t), stroke=C_GRID, sw=1)
        # 轴
        c.line(self.px0, self.py1, self.px1, self.py1, stroke=C_AXIS, sw=1.6, arrow="axis")
        c.line(self.px0, self.py1, self.px0, self.py0, stroke=C_AXIS, sw=1.6, arrow="axis")
        # 刻度
        for t in (xticks or []):
            c.line(self.X(t), self.py1, self.X(t), self.py1 + 5, stroke=C_AXIS, sw=1.2)
            c.text(self.X(t), self.py1 + 19, xfmt.format(t), size=11.5,
                   fill=C_MUTE, anchor="middle")
        for t in (yticks or []):
            c.line(self.px0 - 5, self.Y(t), self.px0, self.Y(t), stroke=C_AXIS, sw=1.2)
            c.text(self.px0 - 9, self.Y(t) + 4, yfmt.format(t), size=11.5,
                   fill=C_MUTE, anchor="end")
        # 轴标签
        c.text(self.px1 + 2, self.py1 + xlabel_pad, xlabel, size=13,
               fill=C_AXIS, anchor="end", weight="600")
        c.text(self.px0 - (ylabel_pad or 62), self.py0 - 12, ylabel, size=13,
               fill=C_AXIS, weight="600")
        return self


def save(name, c):
    p = os.path.join(OUT, name)
    with open(p, "w", encoding="utf-8") as f:
        f.write(c.render())
    print(f"  {name:38s} {os.path.getsize(p)/1024:7.1f} KB")


# =====================================================================
# fig-01  状态空间：双曲线与价格射线
# =====================================================================
def fig01():
    c = Canvas(940, 660, "状态空间：池子状态是一个点",
               "x 轴 = A 的数量，y 轴 = ETH 的数量；价格 = 从原点连到状态点的射线斜率")
    p = Plot(100, 112, 830, 500, 0, 0, 140, 14)

    p.axes(c, "x  (A 的数量) →", "y  (ETH 的数量) ↑",
           xticks=[0, 20, 40, 60, 80, 100, 120, 140],
           yticks=[0, 2, 4, 6, 8, 10, 12, 14], xfmt="{:.0f}", yfmt="{:.0f}")

    # 价格射线
    for slope, lbl in [(0.04, "P = 0.04"), (0.08, "P = 0.08"),
                       (0.14, "P = 0.14"), (0.25, "P = 0.25")]:
        xmax = min(140, 14 / slope)
        c.line(p.X(0), p.Y(0), p.X(xmax), p.Y(xmax * slope), stroke=C_RAY, sw=1.4, dash="5 5")
        lx = xmax * 0.60
        c.text(p.X(lx) + 7, p.Y(lx * slope) - 7, lbl, size=11.5, fill="#8fa0b3")

    # 双曲线 xy = 1000
    d = []
    x = 71.5
    while x <= 140.001:
        d.append(("M" if not d else "L") + f"{p.X(x):.1f} {p.Y(1000.0 / x):.1f}")
        x += 0.5
    c.path(" ".join(d), stroke=C_V2, sw=3)

    c.text(p.X(124), p.Y(9.0), "xy = K", size=16, fill=C_V2, weight="700")
    c.text(p.X(124), p.Y(8.1), "（恒定乘积曲线）", size=11.5, fill=C_V2)

    # 状态点
    sx, sy = 100, 10
    c.line(p.X(0), p.Y(0), p.X(sx), p.Y(sy), stroke=C_ACC, sw=2.4, arrow="acc")
    c.circle(p.X(sx), p.Y(sy), 7.5, fill=C_ACC, stroke="#ffffff", sw=2.5)
    c.text(p.X(sx) + 15, p.Y(sy) - 6, "池子状态 (100 A, 10 ETH)", size=13,
           fill="#b45309", weight="700")
    c.text(p.X(sx) + 15, p.Y(sy) + 14, "斜率 = 10/100 = 0.1 = 价格", size=12, fill="#b45309")

    c.note(40, 520, 860, [
        "读图方法：任意一条从原点出发的直线 = 一个固定价格。线上离原点越远的点，币的数量越多，但价格相同。",
        "状态点只能沿着双曲线滑动（swap），不能离开曲线；沿射线方向移动才是「按比例加/撤流动性」。",
        "价格不是一个被存起来的变量 —— 它只是「储备比 y/x」的另一个说法。所以没有预言机、没有 keeper，池子自己不会动。",
    ], fill="#f8fafc", stroke=C_BORDER, accent=C_MUTE)
    return c


# =====================================================================
# fig-02  V2 整条曲线 vs V3 有限弧
# =====================================================================
def fig02():
    c = Canvas(960, 560, "V2 与 V3 的几何差别：整条曲线 vs 一段弧",
               "两者用的是同一条双曲线；V3 只是把它平移后只保留一段")

    # ---- 左：V2 ----
    pl = Plot(80, 110, 430, 440, 0, 0, 28, 3.2)
    c.panel(52, 84, 410, 390, "V2：整条双曲线")
    pl.axes(c, "x  (A) →", "y  (ETH) ↑",
            xticks=[0, 7, 14, 21, 28], yticks=[0, 0.8, 1.6, 2.4, 3.2],
            xfmt="{:.0f}", yfmt="{:.1f}", ylabel_pad=44)
    d = []
    x = 20.0 / 3.2          # 曲线进入可视范围的起点 (K=20)
    while x <= 28.001:
        d.append(("M" if not d else "L") + f"{pl.X(x):.1f} {pl.Y(20.0/x):.1f}")
        x += 0.1
    c.path(" ".join(d), stroke=C_V2, sw=3)
    c.text(pl.X(17.5), pl.Y(1.9), "xy = K", size=14, fill=C_V2, weight="700")
    # 渐近提示
    c.text(pl.X(27.6), pl.Y(0.30), "永远逼近 x 轴，碰不到", size=10.5,
           fill=C_MUTE, anchor="end")
    c.text(pl.X(6.4), pl.Y(3.02), "永远逼近 y 轴，碰不到", size=10.5, fill=C_MUTE)
    c.text(pl.X(14), pl.Y(0.62), "价格范围 (0, ∞)", size=13.5,
           fill=C_V2, weight="700", anchor="middle")

    # ---- 右：V3 ----
    pr = Plot(560, 110, 910, 440, 0, 0, 26, 3.2)
    c.panel(532, 84, 410, 390, "V3：只剩一段有限弧")
    pr.axes(c, "x  (A) →", "y  (ETH) ↑",
            xticks=[0, 6.5, 13, 19.5, 26], yticks=[0, 0.8, 1.6, 2.4, 3.2],
            xfmt="{:.0f}", yfmt="{:.1f}", ylabel_pad=44)

    # V3 弧：L=10, pa=0.05, pb=0.2
    L, pa, pb = 10.0, 0.05, 0.20
    pts = []
    P = pa
    while P <= pb + 1e-9:
        xr = L * (1 / math.sqrt(P) - 1 / math.sqrt(pb))
        yr = L * (math.sqrt(P) - math.sqrt(pa))
        pts.append((xr, yr))
        P += (pb - pa) / 260
    d = " ".join(("M" if i == 0 else "L") + f"{pr.X(a):.1f} {pr.Y(b):.1f}"
                 for i, (a, b) in enumerate(pts))
    c.path(d, stroke=C_V3, sw=3.2)

    # 端点
    c.circle(pr.X(22.36), pr.Y(0), 7, fill=C_V3, stroke="#fff", sw=2.5)
    c.circle(pr.X(0), pr.Y(2.236), 7, fill=C_V3, stroke="#fff", sw=2.5)
    c.text(pr.X(21.5), pr.Y(0.30), "起点 (22.36, 0)", size=11.5, fill=C_BAD, anchor="end")
    c.text(pr.X(21.5), pr.Y(0.52), "100% A", size=11.5, fill=C_BAD, anchor="end", weight="700")
    c.text(pr.X(0.7), pr.Y(2.55), "终点 (0, 2.236)", size=11.5, fill=C_BAD)
    c.text(pr.X(0.7), pr.Y(2.80), "100% ETH", size=11.5, fill=C_BAD, weight="700")

    # 当前价格点
    cx = L * (1 / math.sqrt(0.1) - 1 / math.sqrt(pb))
    cy = L * (math.sqrt(0.1) - math.sqrt(pa))
    c.circle(pr.X(cx), pr.Y(cy), 6, fill=C_ACC, stroke="#fff", sw=2)
    c.text(pr.X(cx) + 12, pr.Y(cy) - 6, "P = 0.1", size=12, fill="#b45309", weight="700")

    c.text(pr.X(13), pr.Y(0.62), "价格范围 [0.05, 0.20]", size=13.5,
           fill=C_V3, weight="700", anchor="middle")

    c.note(52, 494, 890, [
        "关键：集中流动性没有改变曲线形状——还是那条 xy = K。它改变的是曲线【存在的范围】：从「贯穿整个象限」变成「一段落在坐标轴上的弧」。",
        "弧的两个端点精确落在坐标轴上，这正是「出区间 = 100% 单边」的几何含义。",
    ], fill="#fef2f2", stroke="#fecaca", accent="#b91c1c")
    return c


# =====================================================================
# fig-03  价格空间的流动性分布
# =====================================================================
def fig03():
    c = Canvas(940, 540, "价格空间：钱铺在哪里",
               "横轴 = 价格 P，纵轴 = 该价格上的流动性 L")

    # ---- 上：V2 ----
    p1 = Plot(110, 120, 880, 250, 0, 0, 1.0, 1.0)
    c.panel(80, 96, 830, 180, "V2：每个价格都铺满，高度一样（L = √K 是常数）")
    c.rect(110, 158, 760, 74, fill="#dbeafe", stroke="#93c5fd", sw=1.5, rx=4)
    c.text(490, 202, "L 处处相同", size=14, fill="#1d4ed8", weight="700", anchor="middle")
    c.line(110, 236, 875, 236, stroke=C_AXIS, sw=1.6, arrow="axis")
    c.text(872, 256, "P", size=13, fill=C_AXIS, anchor="end", weight="700")
    c.text(108, 256, "0", size=11.5, fill=C_MUTE, anchor="middle")
    c.text(875, 256, "∞", size=13, fill=C_MUTE, anchor="start")
    # 稳定币实际用到的范围
    c.rect(110 + 760 * 0.49, 150, 760 * 0.02, 90, fill="none",
           stroke=C_BAD, sw=2.5, rx=2)
    c.line(110 + 760 * 0.50, 300, 110 + 760 * 0.50, 250, stroke=C_BAD, sw=1.5)
    c.text(110 + 760 * 0.50, 318, "稳定币实际只在 0.99–1.01 交易", size=12,
           fill=C_BAD, anchor="middle", weight="700")
    c.text(110 + 760 * 0.50, 336, "→ 其余 99.5% 的资金全部闲置", size=12,
           fill=C_BAD, anchor="middle")

    # ---- 下：V3 ----
    c.panel(80, 366, 830, 130, "V3：只在 [p_a, p_b] 里有深度，区间外 L = 0")
    base = 476
    xa = 110 + 760 * 0.34
    xb = 110 + 760 * 0.62
    c.rect(xa, 418, xb - xa, base - 418, fill="#fee2e2", stroke="#fca5a5", sw=1.5, rx=4)
    c.text((xa + xb) / 2, 452, "L > 0", size=14, fill="#b91c1c", weight="700", anchor="middle")
    c.text((xa + xb) / 2, 471, "有人做市", size=11.5, fill="#b91c1c", anchor="middle")
    c.text(xa - 16, 452, "L = 0", size=12.5, fill=C_MUTE, anchor="end")
    c.text(xb + 16, 452, "L = 0", size=12.5, fill=C_MUTE)
    c.line(110, base, 875, base, stroke=C_AXIS, sw=1.6, arrow="axis")
    c.text(872, base + 20, "P", size=13, fill=C_AXIS, anchor="end", weight="700")
    for xx, lab in [(xa, "p_a"), (xb, "p_b")]:
        c.line(xx, base, xx, base + 6, stroke=C_AXIS, sw=1.2)
        c.text(xx, base + 22, lab, size=12, fill=C_AXIS, anchor="middle", weight="600")

    # 切换箭头
    c.text(490, 356, "同样的钱：从「平摊到所有价格」变成「堆在一小段上」→ 深度暴涨",
           size=12.5, fill=C_MUTE, anchor="middle")
    c.line(490, 344, 490, 366, stroke=C_MUTE, sw=1.6, arrow="mute")
    return c


# =====================================================================
# fig-04  价格扫过时的仓位形变
# =====================================================================
def fig04():
    c = Canvas(980, 620, "价格从左扫到右：你的仓位如何形变",
               "区间 [0.05, 0.20]，L = 10，入场价 P = 0.10")

    p = Plot(90, 120, 560, 500, 0, 0, 26, 3.2)
    p.axes(c, "x  (A 的数量) →", "y  (ETH 的数量) ↑",
           xticks=[0, 6.5, 13, 19.5, 26], yticks=[0, 0.8, 1.6, 2.4, 3.2],
           xfmt="{:.0f}", yfmt="{:.1f}", ylabel_pad=52)

    L, pa, pb = 10.0, 0.05, 0.20
    pts = []
    P = pa
    while P <= pb + 1e-9:
        pts.append((L * (1 / math.sqrt(P) - 1 / math.sqrt(pb)),
                    L * (math.sqrt(P) - math.sqrt(pa))))
        P += (pb - pa) / 300
    d = " ".join(("M" if i == 0 else "L") + f"{p.X(a):.1f} {p.Y(b):.1f}"
                 for i, (a, b) in enumerate(pts))
    c.path(d, stroke=C_V3, sw=3.4)

    marks = [
        (0.05, "22.36 A\n0 ETH", "100% A", C_MUTE),
        (0.07, "15.44 A\n0.410 ETH", "72.5% A", C_V3),
        (0.10, "9.262 A\n0.926 ETH", "50% A", C_ACC),
        (0.14, "4.365 A\n1.506 ETH", "28.9% A", C_V3),
        (0.20, "0 A\n2.236 ETH", "0% A", C_MUTE),
    ]
    for P, _lab, tag, col in marks:
        xr = L * (1 / math.sqrt(P) - 1 / math.sqrt(pb))
        yr = L * (math.sqrt(P) - math.sqrt(pa))
        c.circle(p.X(xr), p.Y(yr), 6.5, fill=col, stroke="#fff", sw=2.2)
        c.text(p.X(xr) + 12, p.Y(yr) + 4, f"P={P:.2f}", size=11.5, fill=col, weight="700")

    # 方向箭头
    c.path(f"M {p.X(23.5):.1f} {p.Y(0.35):.1f} Q {p.X(17):.1f} {p.Y(1.9):.1f} "
           f"{p.X(2.6):.1f} {p.Y(2.65):.1f}",
           stroke=C_GOOD, sw=2.6, arrow="good")
    c.text(p.X(15.5), p.Y(2.85), "价格上涨 →", size=12.5, fill=C_GOOD, weight="700")

    # 右侧：组成条形
    bx, bw = 640, 300
    c.text(bx, 128, "各价位时的仓位构成", size=14, weight="700", fill=C_AXIS)
    c.text(bx, 148, "（按价值计算 A 的占比）", size=11.5, fill=C_MUTE)

    rows = [(0.03, "100%", "全额单边 A", C_MUTE, "⛔ 出界 · 不赚手续费"),
            (0.05, "100%", "下界", C_V3, "⚠ 临界"),
            (0.07, "72.5%", "", C_V3, "✓ 活跃"),
            (0.10, "50.0%", "入场", C_ACC, "✓ 活跃"),
            (0.14, "28.9%", "", C_V3, "✓ 活跃"),
            (0.20, "0%", "上界", C_V3, "⚠ 临界"),
            (0.25, "0%", "全额单边 ETH", C_MUTE, "⛔ 出界 · 不赚手续费")]

    y = 178
    for P, pct, sub, col, status in rows:
        c.text(bx - 10, y + 4, f"{P:.2f}", size=11.5, fill=C_MUTE, anchor="end")
        c.rect(bx, y - 10, bw - 90, 20, fill="#f1f5f9", rx=4)
        w = (bw - 90) * float(pct.rstrip("%")) / 100
        if w > 0:
            c.rect(bx, y - 10, w, 20, fill=col, rx=4, opacity=0.85)
        c.text(bx + 8, y + 4, pct, size=11.5,
               fill="#ffffff" if w > 52 else C_TXT, weight="700")
        c.text(bx + bw - 84, y + 4, status, size=11, fill=col)
        if sub:
            c.text(bx + 52, y + 4, sub, size=11, fill="#ffffff", weight="600")
        y += 40

    c.note(90, 528, 850, [
        "① 弧往上走 = 价格涨 = A 变少、ETH 变多 → 被迫卖出上涨的 A",
        "② 弧往下走 = 价格跌 = A 变多、ETH 变少 → 被迫买入下跌的 A",
        "③ 走出弧的端点 = 仓位冻结、一种币清零、手续费归零",
    ], fill="#f8fafc", stroke=C_BORDER, accent=C_MUTE)
    return c


# =====================================================================
# fig-05  资本效率
# =====================================================================
def fig05():
    c = Canvas(940, 540, "区间越窄，同样资金堆出的深度越大",
               "固定 1.852 ETH 资金，价格 P = 0.1 时能提供的流动性 L")

    data = [("[0.050, 0.200]", "×2 / ÷2", 3.4, 10.0, "#93c5fd", "#1d4ed8"),
            ("[0.080, 0.125]", "±22%", 9.5, 27.7, "#60a5fa", "#1d4ed8"),
            ("[0.090, 0.110]", "±10%", 20.4, 59.9, "#3b82f6", "#1d4ed8"),
            ("[0.099, 0.101]", "±1%", 200.5, 587.1, "#dc2626", "#7f1d1d")]

    x0, x1 = 250, 830
    logmin, logmax = math.log10(1), math.log10(700)

    def bx(v):
        return x0 + (math.log10(v) - logmin) / (logmax - logmin) * (x1 - x0)

    c.text(x0, 120, "对数刻度 →", size=11.5, fill=C_MUTE)
    for gv in [1, 10, 100]:
        c.line(bx(gv), 132, bx(gv), 400, stroke=C_GRID, sw=1.2)
        c.text(bx(gv), 418, str(gv), size=11.5, fill=C_MUTE, anchor="middle")
    c.line(x0, 400, x1 + 40, 400, stroke=C_AXIS, sw=1.6)
    c.text(x1 + 40, 420, "L", size=13, fill=C_AXIS, anchor="end", weight="700")

    y = 160
    for label, width, E, L, bar, ink in data:
        c.text(x0 - 20, y + 5, label, size=12.5, fill=C_AXIS, anchor="end", weight="600")
        c.text(x0 - 20, y + 22, width, size=11, fill=C_MUTE, anchor="end")
        c.rect(x0, y - 14, bx(L) - x0, 30, fill=bar, rx=5, opacity=0.9)
        c.text(bx(L) + 12, y + 6, f"L = {L:g}", size=12.5, fill=ink, weight="700")
        c.text(bx(L) + 12, y + 24, f"{E}× 于 V2", size=11, fill=ink)
        y += 64

    c.note(60, 452, 820, [
        "公式：E = 1 / (1 − √(p_a / P))        —— 相对 V2 的深度倍数",
        "同样的钱，区间从「×2/÷2」收窄到「±1%」，深度提升 58 倍（3.4× → 199.5×）。",
        "代价：区间越窄，价格越容易走出去。深度和「出界风险」是同一枚硬币的两面。",
    ], fill="#eff6ff", stroke="#bfdbfe", accent="#1d4ed8")
    return c


# =====================================================================
# fig-06  L(P) 阶梯函数
# =====================================================================
def fig06():
    c = Canvas(960, 560, "L(P) 是一个阶梯函数：厚墙与薄区",
               "某个价格上的深度 = 所有覆盖该价格的 L 之和。深度薄的地方，价格会跳。")

    # 阶梯数据 (起点, 终点, L)
    steps = [(0.00, 0.08, 0), (0.08, 0.12, 520), (0.12, 0.16, 60),
             (0.16, 0.22, 0), (0.22, 0.30, 480), (0.30, 0.34, 40),
             (0.34, 0.42, 360), (0.42, 0.50, 0)]
    p = Plot(90, 110, 880, 400, 0, 0, 0.50, 600)

    # 网格
    for t in [0.1, 0.2, 0.3, 0.4, 0.5]:
        c.line(p.X(t), p.Y(0), p.X(t), p.Y(600), stroke=C_GRID, sw=1)
    for t in [0, 200, 400, 600]:
        c.line(p.X(0), p.Y(t), p.X(0.5), p.Y(t), stroke=C_GRID, sw=1)

    for a, b, h in steps:
        if h == 0:
            continue
        col = "#93c5fd" if h >= 300 else "#fca5a5"
        c.rect(p.X(a), p.Y(h), p.X(b) - p.X(a), p.Y(0) - p.Y(h),
               fill=col, stroke="none", rx=3)

    # 薄区高亮
    for a, b in [(0.12, 0.16), (0.30, 0.34)]:
        c.rect(p.X(a), p.Y(600), p.X(b) - p.X(a), p.Y(0) - p.Y(600),
               fill="#fee2e2", stroke="#f87171", sw=1.6, rx=3, opacity=0.55)

    p.axes(c, "价格 P →", "深度 L ↑",
           xticks=[0, 0.1, 0.2, 0.3, 0.4, 0.5], yticks=[0, 200, 400, 600],
           xfmt="{:.1f}", yfmt="{:.0f}", ylabel_pad=60)

    c.text(p.X(0.10), p.Y(560), "厚墙", size=12.5, fill="#1d4ed8",
           weight="700", anchor="middle")
    c.text(p.X(0.10), p.Y(500), "价格黏住", size=11, fill="#1d4ed8", anchor="middle")
    c.text(p.X(0.14), p.Y(150), "薄", size=12.5, fill="#b91c1c",
           weight="700", anchor="middle")
    c.text(p.X(0.14), p.Y(92), "价格跳", size=11, fill="#b91c1c", anchor="middle")
    c.text(p.X(0.26), p.Y(520), "厚墙", size=12.5, fill="#1d4ed8",
           weight="700", anchor="middle")
    c.text(p.X(0.32), p.Y(120), "薄", size=12.5, fill="#b91c1c",
           weight="700", anchor="middle")

    c.note(90, 428, 850, [
        "价格冲击公式：ΔP / P = 2·Δy / (L·√P)        —— 冲击与 L 成反比",
        "同样买 10 ETH：L = 1,000,000 处冲击 0.002%；L = 10,000 处冲击 0.2% —— 相差 100 倍。",
        "DEX 图表上的「断崖式拉升」，原因不是买盘巨大，而是那里没人做市。",
    ], fill="#fef2f2", stroke="#fecaca", accent="#b91c1c")

    c.note(90, 508, 850, [
        "自我强化：价格涨进薄区 → 同样买单推动更大 → 加速 → 更多 LP 的区间被甩在身后 → 该价格上的 L 更小 → 回到第一步。",
    ], fill="#f8fafc", stroke=C_BORDER, accent=C_MUTE)
    return c


# =====================================================================
# fig-07  Hook 调用链
# =====================================================================
def fig07():
    c = Canvas(980, 660, "一次 swap 的完整 Hook 调用链",
               "Hook 的两次回调夹着真正的 swap 数学，并且都能影响结果")

    def box(x, y, w, h, title, lines, fill, stroke, ink):
        c.rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.8, rx=9)
        c.text(x + w / 2, y + 24, title, size=13.5, fill=ink,
               weight="700", anchor="middle")
        for i, ln in enumerate(lines):
            c.text(x + w / 2, y + 45 + i * 17, ln, size=11, fill=ink, anchor="middle")

    box(360, 92, 240, 58, "用户 / 路由", ["调用 PoolManager.swap()"],
        "#f1f5f9", C_BORDER, C_AXIS)
    c.line(480, 150, 480, 176, stroke=C_AXIS, sw=1.8, arrow="axis")

    box(290, 176, 380, 100, "① Hooks.beforeSwap()",
        ["检查 bit7 → 决定是否回调",
         "回调 hook.beforeSwap(...)",
         "校验 返回 96 字节 + selector 一致"],
        "#fef3c7", "#fbbf24", "#92400e")

    c.line(480, 276, 480, 316, stroke=C_ACC, sw=1.8, arrow="acc")
    c.text(504, 292, "可改 swap 数量", size=10.5, fill="#b45309")
    c.text(504, 308, "可覆盖费率 · 可返回 delta", size=10.5, fill="#b45309")

    box(290, 320, 380, 60, "② 真正的 swap 数学",
        ["用可能已被修改的 amount 和 fee 执行"],
        "#dbeafe", "#93c5fd", "#1d4ed8")

    c.line(480, 380, 480, 406, stroke=C_AXIS, sw=1.8, arrow="axis")

    box(290, 406, 380, 100, "③ Hooks.afterSwap()",
        ["检查 bit6 → 决定是否回调",
         "回调 hook.afterSwap(...)",
         "校验 返回 64 字节 + selector 一致"],
        "#fee2e2", "#fca5a5", "#b91c1c")

    c.line(480, 506, 480, 532, stroke=C_AXIS, sw=1.8, arrow="axis")

    box(290, 532, 380, 58, "④ 结算",
        ["swapDelta = swapDelta − hookDelta"],
        "#dcfce7", "#86efac", "#15803d")

    c.note(40, 176, 226, [
        "Hook delta 的正负约定",
        "（源码注释原文）",
        "",
        "Positive：hook 应收 / 已收",
        "Negative：hook 应付 / 已付",
    ], fill="#f8fafc", stroke=C_BORDER, accent=C_AXIS)

    c.note(702, 176, 238, [
        "四道内置护栏",
        "",
        "① selector 必须原样回传",
        "② 返回长度必须精确",
        "③ noSelfCall 防递归",
        "④ 权限与地址必须一致",
    ], fill="#eff6ff", stroke="#bfdbfe", accent="#1d4ed8")

    c.note(702, 406, 238, [
        "第 ④ 步的含义",
        "",
        "用户承担 hook 的收支",
        "→ 这就是「hook 手续费」",
        "  的实现方式",
    ], fill="#fffbeb", stroke="#fcd34d", accent="#92400e")
    return c


# =====================================================================
# fig-08  Hook 权限位
# =====================================================================
def fig08():
    c = Canvas(1060, 500, "Hook 地址的 14 个权限位",
               "PoolManager 不查询 hook 实现了什么，而是直接看它部署在哪个地址")

    bits = [
        (13, "BEFORE_INITIALIZE", "beforeInitialize", "0x2000", "hook"),
        (12, "AFTER_INITIALIZE", "afterInitialize", "0x1000", "hook"),
        (11, "BEFORE_ADD_LIQUIDITY", "beforeAddLiquidity", "0x0800", "hook"),
        (10, "AFTER_ADD_LIQUIDITY", "afterAddLiquidity", "0x0400", "hook"),
        (9, "BEFORE_REMOVE_LIQUIDITY", "beforeRemoveLiquidity", "0x0200", "hook"),
        (8, "AFTER_REMOVE_LIQUIDITY", "afterRemoveLiquidity", "0x0100", "hook"),
        (7, "BEFORE_SWAP", "beforeSwap", "0x0080", "hook"),
        (6, "AFTER_SWAP", "afterSwap", "0x0040", "hook"),
        (5, "BEFORE_DONATE", "beforeDonate", "0x0020", "hook"),
        (4, "AFTER_DONATE", "afterDonate", "0x0010", "hook"),
        (3, "BEFORE_SWAP_RETURNS_DELTA", "↑ 可返回 delta", "0x0008", "delta"),
        (2, "AFTER_SWAP_RETURNS_DELTA", "↑ 可返回 delta", "0x0004", "delta"),
        (1, "AFTER_ADD_LIQ_RETURNS_DELTA", "↑ 可返回 delta", "0x0002", "delta"),
        (0, "AFTER_REMOVE_LIQ_RETURNS_DELTA", "↑ 可返回 delta", "0x0001", "delta"),
    ]

    # ---- 位条 ----
    x0, cw, gap = 30, 66, 6
    ytop = 112
    for i, (b, name, fn, hexv, kind) in enumerate(bits):
        x = x0 + i * (cw + gap)
        is_acc = hexv in ("0x2000", "0x0400")
        fill = "#fecaca" if kind == "delta" else ("#fbbf24" if is_acc else "#dbeafe")
        stroke = "#dc2626" if kind == "delta" else ("#d97706" if is_acc else "#93c5fd")
        ink = "#7f1d1d" if kind == "delta" else ("#78350f" if is_acc else "#1d4ed8")
        c.rect(x, ytop, cw, 60, fill=fill, stroke=stroke, sw=2, rx=7)
        c.text(x + cw / 2, ytop + 31, str(b), size=20, fill=ink,
               weight="700", anchor="middle")
        c.text(x + cw / 2, ytop + 51, hexv[2:], size=10.5, fill=ink,
               weight="600", anchor="middle")
        c.text(x + cw / 2, ytop - 9, f"bit {b}", size=9.5, fill=C_MUTE, anchor="middle")

    c.line(x0, ytop + 88, x0 + 14 * (cw + gap) - gap, ytop + 88, stroke=C_BORDER, sw=1.2)

    # ---- 对照表（两栏）----
    def row(col_x, y, b, name, fn, hexv, kind):
        col = "#b91c1c" if kind == "delta" else C_AXIS
        c.text(col_x, y, f"bit {b:2d}", size=11, fill=C_MUTE, weight="600")
        c.text(col_x + 62, y, hexv, size=11, fill=col, weight="700")
        c.text(col_x + 128, y, name, size=11, fill=col)
        c.text(col_x + 350, y, fn, size=11, fill=C_MUTE)

    ytab = 224
    for i in range(7):
        row(52, ytab + i * 20.5, *bits[i])
    for i in range(7):
        row(560, ytab + i * 20.5, *bits[i + 7])

    c.note(30, 380, 1000, [
        "官方源码注释里的例子：地址 0x0000…2400  →  0x2400 = 0010 0100 0000 0000  →  bit13 + bit10（图中橙色两格）→ 只启用 beforeInitialize 和 afterAddLiquidity",
        "为什么这么设计：权限检查退化成一次纯位运算，零存储读取、零外部调用。代价是必须用 CREATE2 挖地址（期望约 2^14 = 16,384 次尝试）。",
        "注意 bit 0–3（红色）：它们不是独立回调点，而是「给已有回调加权限」。想启用 afterSwap 返回 delta，必须同时设 bit6 和 bit2。",
        "判断捷径：把 hook 地址与 0x3FFF 做按位与，得到的 14 位就是它全部的能力清单。",
    ], fill="#fffbeb", stroke="#fcd34d", accent="#92400e")
    return c


# =====================================================================
# fig-09  sigma-sqrt-H 决策图
# =====================================================================
def fig09():
    c = Canvas(960, 620, "区间宽度怎么定：δ* ≈ σ√H",
               "纵轴是建议的对数半宽 δ*，横轴是波动率 σ（对数刻度）")

    x0, y0, x1, y1 = 120, 120, 800, 470
    lx0, lx1 = math.log10(0.0005), math.log10(1.0)      # sigma
    ly0, ly1 = math.log10(0.001), math.log10(3.0)       # delta*

    def X(v):
        return x0 + (math.log10(v) - lx0) / (lx1 - lx0) * (x1 - x0)

    def Y(v):
        return y1 - (math.log10(v) - ly0) / (ly1 - ly0) * (y1 - y0)

    # 网格
    for gv in [0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0]:
        c.line(X(gv), y0, X(gv), y1, stroke=C_GRID, sw=1)
        lab = f"{gv*100:.1f}%" if gv < 0.01 else f"{gv*100:.0f}%"
        c.text(X(gv), y1 + 20, lab, size=11, fill=C_MUTE, anchor="middle")
    for gv in [0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0, 3.0]:
        c.line(x0, Y(gv), x1, Y(gv), stroke=C_GRID, sw=1)
        lab = f"{gv*100:.1f}%" if gv < 0.01 else f"{gv*100:.0f}%"
        c.text(x0 - 10, Y(gv) + 4, lab, size=11, fill=C_MUTE, anchor="end")

    c.line(x0, y1, x1, y1, stroke=C_AXIS, sw=1.6, arrow="axis")
    c.line(x0, y1, x0, y0, stroke=C_AXIS, sw=1.6, arrow="axis")
    c.text(x1, y1 + 46, "日波动率 σ →", size=12.5, fill=C_AXIS, anchor="end", weight="600")
    c.text(x0 - 62, y0 - 12, "最优半宽 δ* ↑", size=12.5, fill=C_AXIS, weight="600")

    # 等 H 线：delta = sigma*sqrt(H)
    import math as _m
    HSPEC = [(1, "H = 1 天", "#60a5fa", None),
             (7, "H = 7 天", "#3b82f6", None),
             (30, "H = 30 天", "#1d4ed8", None),
             (90, "H = 90 天", "#1e3a8a", "7 5")]
    for H, lbl, col, dash in HSPEC:
        pts = []
        v = 0.0005
        while v <= 1.0001:
            dv = v * _m.sqrt(H)
            if ly0 <= dv <= ly1:
                pts.append((X(v), Y(dv)))
            v *= 1.03
        for i in range(len(pts) - 1):
            c.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1],
                   stroke=col, sw=2.4, dash=dash)

    # 图例（替代原先贴在线尾的标签，避免与资产标注打架）
    lgx, lgy = 152, 146
    c.rect(lgx - 14, lgy - 22, 196, 122, fill="#ffffff", stroke=C_BORDER,
           sw=1.2, rx=8, opacity=0.96)
    c.text(lgx, lgy - 6, "持有期 H", size=11, fill=C_MUTE, weight="600")
    for i, (H, lbl, col, dash) in enumerate(HSPEC):
        yy = lgy + 16 + i * 24
        c.line(lgx, yy, lgx + 32, yy, stroke=col, sw=2.6, dash=dash)
        c.text(lgx + 42, yy + 4, lbl, size=11.5, fill=col, weight="600")

    # 资产标记点
    marks = [
        (0.001, math.sqrt(30), "稳定币", "σ=0.1%, H=30天", C_GOOD, -16, 24, "end"),
        (0.03, math.sqrt(30), "ETH", "σ=3%, H=30天", "#7c3aed", -16, 24, "end"),
        (0.03, math.sqrt(7), "ETH", "H=7天", "#7c3aed", 18, -26, "start"),
        (0.30, math.sqrt(1), "MEME", "σ=30%, H=1天", C_BAD, 18, -26, "start"),
        (0.30, math.sqrt(7), "MEME", "H=7天", C_BAD, -18, 24, "end"),
    ]
    for sig, sq, t1, t2, col, dx, dy, anc in marks:
        dv = sig * sq
        if not (ly0 <= dv <= ly1):
            continue
        c.circle(X(sig), Y(dv), 7, fill=col, stroke="#fff", sw=2.4)
        c.text(X(sig) + dx, Y(dv) + dy, t1, size=11.5, fill=col,
               anchor=anc, weight="700")
        c.text(X(sig) + dx, Y(dv) + dy + 15, t2, size=10.5, fill=col, anchor=anc)

    # 不可行区
    c.rect(x0, y0, x1 - x0, Y(1.0) - y0, fill="#fef2f2", opacity=0.75)
    c.text(x1 - 12, y0 + 24, "δ* > 100%：区域宽到几乎退化成 V2", size=12,
           fill="#b91c1c", anchor="end", weight="700")
    c.text(x1 - 12, y0 + 43, "→ 资本效率优势消失，不如直接持有或不做 LP", size=11,
           fill="#b91c1c", anchor="end")

    c.note(60, 512, 840, [
        "读法：先估资产日波动率 σ，再定你打算持有多少天 H，在图上找到交点，读出建议的对数半宽 δ*。",
        "建议区间 = [P₀·e^(−δ*), P₀·e^(+δ*)]。  例：ETH σ=3%、H=30 天 → δ*=16.4% → 区间约 [0.85, 1.18]。",
        "⚠ 这是规则而非精确解：忽略了趋势（drift）、肥尾、费率档位竞争和 rebalance 成本。真实市场里 MEME 有强烈的单边趋势，实际需要的区间还要更宽。",
    ], fill="#f8fafc", stroke=C_BORDER, accent=C_MUTE)
    return c


# =====================================================================
# fig-10  联合曲线 vs AMM 池
# =====================================================================
def fig10():
    c = Canvas(980, 560, "联合曲线（单边） vs AMM 池（双边）",
               "两者都能画成「曲线 + 价格射线」，但一个是公式，一个需要真人当对手方")

    # ---- 左 ----
    pl = Plot(90, 130, 430, 420, 0, 0, 10, 10)
    c.panel(62, 104, 400, 350, "pump.fun 联合曲线：不需要 LP")
    pl.axes(c, "代币流通量 →", "SOL 储备 ↑",
            xticks=[0, 2, 4, 6, 8, 10], yticks=[0, 2, 4, 6, 8, 10],
            xfmt="{:.0f}", yfmt="{:.0f}", ylabel_pad=54)
    d = []
    x = 3.3
    while x <= 10.001:
        d.append(("M" if not d else "L") + f"{pl.X(x):.1f} {pl.Y(33.0/x):.1f}")
        x += 0.15
    c.path(" ".join(d), stroke=C_V2, sw=3)
    # 虚拟起点
    c.circle(pl.X(9.0), pl.Y(3.667), 6, fill=C_MUTE, stroke="#fff", sw=2)
    c.circle(pl.X(3.6), pl.Y(9.167), 6, fill=C_ACC, stroke="#fff", sw=2)
    c.line(pl.X(0), pl.Y(0), pl.X(3.6), pl.Y(9.167), stroke=C_ACC, sw=1.6,
           dash="5 5", arrow="acc")
    c.text(pl.X(3.9), pl.Y(9.4), "价格沿曲线移动", size=11.5, fill="#b45309", weight="600")
    c.text(pl.X(9.2), pl.Y(3.0), "起点（虚拟储备）", size=11, fill=C_MUTE)

    c.text(pl.X(5), pl.Y(0.9), "对手方 = 曲线本身", size=13,
           fill=C_V2, weight="700", anchor="middle")
    c.text(pl.X(5), pl.Y(0.45), "最波动的阶段没有任何 LP 承担风险", size=11,
           fill=C_V2, anchor="middle")

    # ---- 右 ----
    pr = Plot(560, 130, 900, 420, 0, 0, 10, 10)
    c.panel(532, 104, 400, 350, "Uniswap 池：必须有人当 LP")
    pr.axes(c, "代币储备 →", "ETH 储备 ↑",
            xticks=[0, 2, 4, 6, 8, 10], yticks=[0, 2, 4, 6, 8, 10],
            xfmt="{:.0f}", yfmt="{:.0f}", ylabel_pad=54)
    d = []
    x = 3.3
    while x <= 10.001:
        d.append(("M" if not d else "L") + f"{pr.X(x):.1f} {pr.Y(33.0/x):.1f}")
        x += 0.15
    c.path(" ".join(d), stroke=C_V3, sw=3)

    # LP 存入箭头
    for (ax, ay, tx, ty, lab) in [(6.4, 9.7, 5.2, 6.2, "存入 A"),
                                  (2.0, 4.4, 3.6, 5.4, "存入 ETH")]:
        c.line(pr.X(ax), pr.Y(ay), pr.X(tx), pr.Y(ty), stroke=C_GOOD, sw=2.2, arrow="good")
    c.text(pr.X(6.6), pr.Y(9.9), "LP 存入 A", size=11, fill=C_GOOD, weight="600")
    c.text(pr.X(0.3), pr.Y(4.2), "LP 存入 ETH", size=11, fill=C_GOOD, weight="600")

    c.text(pr.X(5), pr.Y(0.9), "对手方 = 真人 LP", size=13,
           fill=C_V3, weight="700", anchor="middle")
    c.text(pr.X(5), pr.Y(0.45), "最波动的阶段 LP 承担全部风险", size=11,
           fill=C_V3, anchor="middle")

    c.note(62, 468, 870, [
        "Solana 的 MEME 栈（联合曲线 → 毕业后注入全区间 AMM）全程不使用集中流动性。它用的是「V2 模式」，而全区间恰恰是对波动资产更友好的模式。",
        "更关键的是：联合曲线在最疯狂的阶段根本不需要 LP —— 价格是公式算出来的，储备金是买家自己放进去的。以太坊的模型则依赖「有人愿意当 LP」。",
    ], fill="#f0fdf4", stroke="#86efac", accent="#15803d")
    return c


# =====================================================================
# fig-11  V4 架构
# =====================================================================
def fig11():
    c = Canvas(1000, 600, "V3 与 V4 的架构差别",
               "几何完全没变，变的是「池子住在哪里」和「多跳要不要真的转账」")

    # ---- 左：V3 ----
    c.panel(50, 100, 400, 400, "V3：每个池子一个独立合约")
    pools = [("池 A/ETH", 150), ("池 B/ETH", 235), ("池 C/ETH", 320)]
    for name, y in pools:
        c.rect(90, y, 200, 56, fill="#dbeafe", stroke="#93c5fd", sw=1.8, rx=8)
        c.text(190, y + 26, name, size=12.5, fill="#1d4ed8", weight="700", anchor="middle")
        c.text(190, y + 44, "独立合约 · 独立储备", size=10.5, fill="#3b82f6", anchor="middle")
    # 转账箭头
    for i in range(len(pools) - 1):
        y1 = pools[i][1] + 56
        y2 = pools[i + 1][1]
        c.line(190, y1, 190, y2, stroke=C_BAD, sw=2, arrow="bad")
        c.text(200, (y1 + y2) / 2 + 4, "真实代币转账", size=10.5, fill=C_BAD)
    c.text(250, 140, "用户", size=12, fill=C_AXIS, weight="700", anchor="middle")
    c.line(250, 148, 250, 178, stroke=C_AXIS, sw=1.6, arrow="axis")
    c.text(190, 470, "多跳 = 多次跨合约调用 + 多次真实转账",
           size=11.5, fill=C_BAD, anchor="middle", weight="600")

    # ---- 右：V4 ----
    c.panel(540, 100, 410, 400, "V4：所有池子住在一个 PoolManager 里")
    c.rect(590, 150, 310, 180, fill="#fef3c7", stroke="#fbbf24", sw=2.2, rx=10)
    c.text(745, 176, "PoolManager（单例合约）", size=13.5,
           fill="#92400e", weight="700", anchor="middle")
    for i, name in enumerate(["mapping(PoolId ⇒ Pool.State)", "池 A/ETH", "池 B/ETH", "池 C/ETH"]):
        c.rect(615, 192 + i * 33, 260, 27, fill="#ffffff",
               stroke="#fcd34d", sw=1.4, rx=6)
        c.text(745, 210 + i * 33, name, size=11.5,
               fill="#92400e", anchor="middle",
               weight="700" if i == 0 else "normal")

    c.rect(590, 372, 310, 74, fill="#dcfce7", stroke="#86efac", sw=2, rx=9)
    c.text(745, 396, "Flash Accounting", size=13, fill="#15803d",
           weight="700", anchor="middle")
    c.text(745, 416, "所有余额变动记为 delta", size=11, fill="#15803d", anchor="middle")
    c.text(745, 433, "存在 EIP-1153 瞬态存储里", size=11, fill="#15803d", anchor="middle")

    c.text(745, 470, "任意多跳 → 只需两次真实转账",
           size=11.5, fill=C_GOOD, anchor="middle", weight="700")

    # 对比
    c.note(50, 520, 900, [
        "V3：建池 = 部署一个新合约；A→B→C 多跳 = 3 次跨合约调用 + 3 次代币转账",
        "V4：建池 = 往 mapping 里写一条记录；A→B→C 多跳 = 内部记账，开头转进一次、结尾转出一次，共 2 次转账",
    ], fill="#eff6ff", stroke="#bfdbfe", accent="#1d4ed8")
    return c


# =====================================================================
NAMES = {
    fig01: "fig-01-state-space.svg",
    fig02: "fig-02-v2-vs-v3-curve.svg",
    fig03: "fig-03-price-space-liquidity.svg",
    fig04: "fig-04-v3-sweep.svg",
    fig05: "fig-05-capital-efficiency.svg",
    fig06: "fig-06-liquidity-ladder.svg",
    fig07: "fig-07-hook-lifecycle.svg",
    fig08: "fig-08-hook-flags.svg",
    fig09: "fig-09-sigma-sqrt-h.svg",
    fig10: "fig-10-bonding-vs-amm.svg",
    fig11: "fig-11-v4-architecture.svg",
}

if __name__ == "__main__":
    print("生成 SVG 插图 →", OUT)
    for fn, name in NAMES.items():
        save(name, fn())
    print("完成：%d 张" % len(NAMES))
