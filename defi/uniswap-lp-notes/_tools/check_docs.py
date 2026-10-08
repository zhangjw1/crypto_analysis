# -*- coding: utf-8 -*-
"""交叉引用 / 图片引用 / 标题风格 / 数值一致性检查"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

md_files = sorted(f for f in os.listdir(ROOT) if f.endswith(".md"))
fig_dir = os.path.join(ROOT, "figures")
fig_files = set(os.listdir(fig_dir)) if os.path.isdir(fig_dir) else set()

link_re = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
img_re = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")

bad_links, bad_imgs, ok_links = [], [], 0
img_usage = {}
style_rows = []
stale = []

STALE_PATTERNS = [
    (r"199\.5\s*[×x]", "旧口径 E=199.5（已统一为 200.5）"),
    (r"19\.5\s*[×x]，.*\[0\.09", "旧口径 E=19.5"),
    (r"05-Hook机制\.md", "旧文件名 05-Hook机制.md"),
]

for f in md_files:
    p = os.path.join(ROOT, f)
    txt = open(p, encoding="utf-8").read()
    lines = txt.splitlines()

    # 标题风格
    h2 = [l for l in lines if l.startswith("## ")]
    has_q = any("本章回答什么问题" in l for l in lines)
    has_sum = any("本章要点" in l for l in lines)
    style_rows.append((f, len(lines), len(h2), has_q, has_sum))

    # 图片
    for alt, target in img_re.findall(txt):
        if target.startswith("figures/"):
            name = target.split("/", 1)[1]
            img_usage.setdefault(name, []).append(f)
            if name not in fig_files:
                bad_imgs.append((f, target))

    # 本地 md 链接
    for text, target in link_re.findall(txt):
        if target.startswith(("http://", "https://", "#")):
            continue
        tgt = target.split("#")[0]
        if not tgt:
            continue
        if os.path.exists(os.path.join(ROOT, tgt)):
            ok_links += 1
        else:
            bad_links.append((f, target))

    # 陈旧数值
    for pat, why in STALE_PATTERNS:
        for m in re.finditer(pat, txt):
            ln = txt[:m.start()].count("\n") + 1
            line = txt.splitlines()[ln - 1]
            # 明确在讲解"另一种口径"的行不算陈旧
            if any(k in line for k in ("若改用", "口径", "对照", "旧口径")):
                continue
            stale.append((f, ln, why, m.group(0)[:40]))

print("=" * 92)
print("文档校核")
print("=" * 92)

print("\n【1】章节结构")
print(f"{'文件':<38} {'行数':>6} {'H2':>4}  {'答什么问题':^10} {'本章要点':^10}")
for f, n, h2, q, s in style_rows:
    print(f"{f:<38} {n:>6} {h2:>4}  {'有' if q else '—':^10} {'有' if s else '—':^10}")

print(f"\n【2】图片引用（共 {len(fig_files)} 张图）")
for name in sorted(fig_files):
    users = img_usage.get(name, [])
    tag = "OK " if users else "!! 未被引用"
    print(f"  {tag} {name:<36} 被 {len(users)} 章引用")

print(f"\n【3】链接检查：{ok_links} 条有效")
if bad_links:
    print(f"  !! 死链 {len(bad_links)} 条：")
    for f, t in bad_links:
        print(f"     {f}  ->  {t}")
else:
    print("  无死链")
if bad_imgs:
    print(f"  !! 缺失图片 {len(bad_imgs)} 条：")
    for f, t in bad_imgs:
        print(f"     {f}  ->  {t}")
else:
    print("  图片引用全部有效")

print(f"\n【4】陈旧数值")
if stale:
    for f, ln, why, frag in stale:
        print(f"  !! {f}:{ln}  {why}   片段: {frag}")
else:
    print("  未发现陈旧数值")

print("\n【5】不确定性标注口径")
MARK = {}
for f in md_files:
    txt = open(os.path.join(ROOT, f), encoding="utf-8").read()
    marks = {
        "⚠️ 未验证": len(re.findall(r"⚠️\s*\*\*未验证\*\*", txt)),
        "[未验证]方括号": len(re.findall(r"\[⚠️?\s*未验证\]", txt)),
        "[推导]": len(re.findall(r"\[推导\]", txt)),
        "[事实]": len(re.findall(r"\[事实\]", txt)),
        "[推理]": len(re.findall(r"\[推理\]", txt)),
    }
    MARK[f] = marks
    active = {k: v for k, v in marks.items() if v}
    print(f"  {f:<38} {active if active else '（无标注）'}")
