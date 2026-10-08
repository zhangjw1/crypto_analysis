# -*- coding: utf-8 -*-
"""把 11 张 SVG 内联进 HTML，并注入 MathJax 与图注。"""
import os, re, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, "Uniswap流动性做市深度笔记.html")
FIGD = os.path.join(ROOT, "figures")

CAPTIONS = {
    "fig-01-state-space.svg":
        "状态空间：横轴是 A 的数量，纵轴是 ETH 的数量。双曲线 xy=K 是池子能到达的全部状态，"
        "每条从原点出发的射线是一个固定价格。池子状态点只能沿曲线滑动（交易）或沿射线移动（按比例加减流动性）。",
    "fig-02-v2-vs-v3-curve.svg":
        "左：V2 的曲线贯穿整个象限，永远碰不到坐标轴，所以价格范围是 (0,∞)、处处深度相同。"
        "右：V3 把同一条双曲线平移，第一象限里只剩一段有限的弧，两端精确落在坐标轴上。",
    "fig-03-price-space-liquidity.svg":
        "价格空间中的流动性分布：V2 是一条平坦的直线（每个价位深度相同），V3 是若干个区间方块，"
        "块的高度代表该价位堆了多少 L。",
    "fig-04-v3-sweep.svg":
        "V3 仓位随价格扫描的完整过程：价格从左到右移动，仓位构成从「全是 A」逐渐变成「全是 ETH」，"
        "出界后完全冻结。下方标注了关键价格点的持仓和 IL。",
    "fig-05-capital-efficiency.svg":
        "同样 10 万美元，放在不同宽度的区间能提供多少倍的深度。区间越窄，倍数越大，但出界也越快。",
    "fig-06-liquidity-ladder.svg":
        "多个 LP 各自选择不同区间，叠加后得到阶梯状的 L(P)。注意在 tick 边界上会突然跳变——"
        "这意味着价格穿过边界时市场深度会突变。",
    "fig-07-hook-lifecycle.svg":
        "一次 swap 的完整 Hook 调用链：beforeSwap 回调 → 真正的 swap 数学 → afterSwap 回调 → 结算。"
        "Hook 的 delta 由调用者承担，这就是「hook 手续费」的实现方式。",
    "fig-08-hook-flags.svg":
        "Hook 地址的最低 14 位编码了它的全部权限。橙色是官方源码注释里 0x2400 的例子，"
        "红色是 bit0–3（delta 权限，能动钱）。",
    "fig-09-sigma-sqrt-h.svg":
        "最优区间半宽 δ* = σ√H。四条彩色线是不同持有期 H 下的最优解，"
        "五个点是稳定币 / ETH / MEME 在不同持有期的实际位置。",
    "fig-10-bonding-vs-amm.svg":
        "Solana 的联合曲线（左）vs 以太坊的 AMM（右）。联合曲线的价格由公式决定，"
        "储备由买家注入，全程不需要 LP；AMM 则依赖有人自愿提供流动性。",
    "fig-11-v4-architecture.svg":
        "V4 架构：所有池子装在一本 PoolManager 合约里，通过 PoolKey 唯一标识。"
        "Flash Accounting 让多跳交易只需两次真实转账。",
}

html = open(HTML, encoding="utf-8").read()

# ---- 1) 内联 SVG ----
def inline(svg_path, fname):
    s = open(svg_path, encoding="utf-8").read()
    s = re.sub(r"<\?xml[^>]*\?>", "", s)
    s = re.sub(r"<!DOCTYPE[^>]*>", "", s)
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    m = re.search(r"<svg[^>]*viewBox=\"([^\"]+)\"", s)
    vb = m.group(1) if m else "0 0 960 560"
    s = s[s.index("<svg"):]
    # 统一成响应式、跟随主题
    s = re.sub(r"<svg[^>]*>",
               f'<svg viewBox="{vb}" xmlns="http://www.w3.org/2000/svg" '
               f'style="width:100%;height:auto;display:block">', s, count=1)
    return s

injected, missing = 0, []
for key in list(CAPTIONS.keys()):
    fid = "fig" + key.split("-")[1]          # fig-01-... -> fig01
    anchor = f'<figure id="{fid}"></figure>'
    # 兼容 fig02b / fig04b 这类重复引用
    for alt in [anchor] + ([f'<figure id="{fid}b"></figure>'] if fid in ("fig02", "fig04") else []):
        if alt not in html:
            continue
        p = os.path.join(FIGD, key)
        if not os.path.exists(p):
            missing.append(key); continue
        cap = CAPTIONS[key]
        rep = f'<figure>\n{inline(p, key)}\n<figcaption>{cap}</figcaption>\n</figure>'
        html = html.replace(alt, rep, 1)
        injected += 1

# ---- 2) 注入 MathJax ----
MJ = ('<script>\n'
      'window.MathJax = {\n'
      '  tex: { inlineMath: [["$","$"],["\\\\(","\\\\)"]], displayMath: [["$$","$$"],["\\\\[","\\\\]"]] },\n'
      '  options: { skipHtmlTags: ["script","noscript","style","textarea","pre","code"] },\n'
      '  svg: { fontCache: "global" }\n'
      '};\n'
      '</script>\n'
      '<script id="MathJax-script" async\n'
      '  src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>\n')

if "MathJax-script" not in html:
    html = html.replace("</head>", MJ + "</head>", 1)

open(HTML, "w", encoding="utf-8", newline="\n").write(html)

print(f"内联图片: {injected} 处")
if missing:
    print("缺失:", missing)
leftover = re.findall(r'<figure id="([^"]+)"></figure>', html)
print("未替换的占位:", leftover if leftover else "无")
print("MathJax 注入:", "MathJax-script" in html)
print("文件大小: %.1f KB" % (len(html.encode("utf-8")) / 1024))
