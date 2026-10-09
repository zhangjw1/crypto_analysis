# -*- coding: utf-8 -*-
"""Build the Pendle Finance research memorandum."""

from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
CHARTS = ROOT / "charts"
CHARTS.mkdir(exist_ok=True)
OUT = ROOT / "Pendle_Finance_分析报告_20261009.docx"

NAVY = "1F3A5F"
TEAL = "0F6E6B"
GOLD = "8A6A2F"
RED = "8C3A3A"
INK = "243042"
MUTED = "5E6A7D"
LINE = "D5DCE6"
PALE = "F4F7FB"
WHITE = "FFFFFF"


def font_path():
    candidates = [
        r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\msyh.ttf",
        r"C:\Windows\Fonts\simhei.ttf",
    ]
    for item in candidates:
        if Path(item).exists():
            return item
    return None


FONT_FILE = font_path()


def pil_font(size, bold=False):
    if FONT_FILE:
        return ImageFont.truetype(FONT_FILE, size=size, index=1 if bold and FONT_FILE.endswith(".ttc") else 0)
    return ImageFont.load_default()


def draw_bars(path, title, subtitle, rows, unit, source):
    width, height = 1680, 760
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, width, 10), fill="#1F3A5F")
    draw.text((56, 36), title, font=pil_font(36, True), fill="#1F3A5F")
    draw.text((56, 88), subtitle, font=pil_font(20), fill="#5E6A7D")

    left, right, top, bottom = 110, 1540, 180, 620
    max_value = max(value for _, value, _ in rows) * 1.18
    gap = 36
    bar_w = int((right - left - gap * (len(rows) - 1)) / len(rows))
    for index, (label, value, note) in enumerate(rows):
        x = left + index * (bar_w + gap)
        bar_h = int((bottom - top) * value / max_value)
        y = bottom - bar_h
        draw.rounded_rectangle((x, y, x + bar_w, bottom), radius=8, fill="#1F3A5F")
        value_text = f"{value:.2f}" if value < 10 else f"{value:.1f}"
        draw.text((x + 8, y - 38), value_text, font=pil_font(24, True), fill="#1F3A5F")
        draw.text((x + 8, bottom + 18), label, font=pil_font(22, True), fill="#243042")
        draw.text((x + 8, bottom + 52), note, font=pil_font(17), fill="#5E6A7D")

    draw.line((left - 20, bottom, right + 20, bottom), fill="#D5DCE6", width=2)
    draw.text((56, 700), f"单位：{unit}。{source}", font=pil_font(16), fill="#5E6A7D")
    image.save(path)


def set_run_font(run, name="Microsoft YaHei", size=10.5, bold=False, color=INK, italic=False):
    run.font.name = name
    run.bold = bold
    run.italic = italic
    run.font.size = Pt(size)
    run.font.color.rgb = RGBColor.from_string(color)
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rfonts.set(qn(attr), name)


def shade(cell, color):
    tcpr = cell._tc.get_or_add_tcPr()
    shd = tcpr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tcpr.append(shd)
    shd.set(qn("w:fill"), color)
    shd.set(qn("w:val"), "clear")


def set_cell_border(cell):
    tcpr = cell._tc.get_or_add_tcPr()
    borders = tcpr.find(qn("w:tcBorders"))
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        tcpr.append(borders)
    for edge in ("top", "left", "bottom", "right"):
        element = borders.find(qn(f"w:{edge}"))
        if element is None:
            element = OxmlElement(f"w:{edge}")
            borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), "4")
        element.set(qn("w:color"), LINE)


def set_cell_text(cell, text, bold=False, size=8.5, color=INK, align="left", fill=None):
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = {
        "left": WD_ALIGN_PARAGRAPH.LEFT,
        "center": WD_ALIGN_PARAGRAPH.CENTER,
        "right": WD_ALIGN_PARAGRAPH.RIGHT,
    }[align]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.05
    run = p.add_run(text)
    set_run_font(run, size=size, bold=bold, color=color)
    if fill:
        shade(cell, fill)
    set_cell_border(cell)
    cell.vertical_alignment = 1


def add_table(document, headers, rows, widths, font_size=8.5):
    table = document.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    tbl = table._tbl
    tblpr = tbl.tblPr if tbl.tblPr is not None else OxmlElement("w:tblPr")
    layout = tblpr.find(qn("w:tblLayout"))
    if layout is None:
        layout = OxmlElement("w:tblLayout")
        tblpr.append(layout)
    layout.set(qn("w:type"), "fixed")
    for index, (header, width) in enumerate(zip(headers, widths)):
        cell = table.rows[0].cells[index]
        cell.width = Cm(width)
        set_cell_text(cell, header, bold=True, size=font_size, color=WHITE, align="center", fill=NAVY)
    for row_index, row in enumerate(rows):
        cells = table.add_row().cells
        fill = PALE if row_index % 2 == 0 else WHITE
        for index, (value, width) in enumerate(zip(row, widths)):
            cells[index].width = Cm(width)
            align = "left" if index == 0 else "right"
            if len(headers) <= 3 and index == 0:
                align = "left"
            set_cell_text(cells[index], value, size=font_size, align=align, fill=fill)
    document.add_paragraph()
    return table


def paragraph(document, text, size=10.5, bold=False, color=INK, space_before=0, space_after=8, align="left", italic=False):
    p = document.add_paragraph()
    p.alignment = {
        "left": WD_ALIGN_PARAGRAPH.LEFT,
        "center": WD_ALIGN_PARAGRAPH.CENTER,
        "justify": WD_ALIGN_PARAGRAPH.JUSTIFY,
    }[align]
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    run = p.add_run(text)
    set_run_font(run, size=size, bold=bold, color=color, italic=italic)
    return p


def heading(document, text, level):
    p = document.add_heading(text, level=level)
    p.paragraph_format.space_before = Pt(14 if level == 1 else 10)
    p.paragraph_format.space_after = Pt(6)
    for run in p.runs:
        set_run_font(run, size={1: 16, 2: 13, 3: 11.5}[level], bold=True, color=NAVY if level == 1 else TEAL)
    return p


def bullet(document, text):
    p = document.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.08
    if p.runs:
        p.runs[0].text = text
        set_run_font(p.runs[0], size=10.5)
    else:
        run = p.add_run(text)
        set_run_font(run, size=10.5)
    return p


def add_page_number(paragraph_obj):
    run = paragraph_obj.add_run()
    set_run_font(run, size=8, color=MUTED)
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_begin)
    run._r.append(instr)
    run._r.append(fld_end)


def configure(document):
    section = document.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.left_margin = Cm(1.7)
    section.right_margin = Cm(1.7)
    section.top_margin = Cm(1.6)
    section.bottom_margin = Cm(1.5)
    section.header_distance = Cm(0.5)
    section.footer_distance = Cm(0.4)
    section.different_first_page_header_footer = True

    normal = document.styles["Normal"]
    normal.font.name = "Microsoft YaHei"
    normal.font.size = Pt(10.5)
    normal.font.color.rgb = RGBColor.from_string(INK)
    rpr = normal.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rfonts.set(qn(attr), "Microsoft YaHei")

    header = section.header
    header_p = header.paragraphs[0]
    header_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = header_p.add_run("PENDLE RESEARCH MEMO  ·  数据截止 2026-10-09")
    set_run_font(run, size=8, color=MUTED)

    footer = section.footer
    footer_p = footer.paragraphs[0]
    footer_p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = footer_p.add_run("独立研究备忘录，不构成投资建议    ")
    set_run_font(run, size=8, color=MUTED)
    add_page_number(footer_p)

    first_footer = section.first_page_footer
    fp = first_footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = fp.add_run("独立研究备忘录，不构成投资建议    ")
    set_run_font(run, size=8, color=MUTED)
    add_page_number(fp)


def build_charts():
    draw_bars(
        CHARTS / "pendle_tvl.png",
        "Pendle 核心 TVL：2025 年冲顶，2026 年回落",
        "柱值为各年日均 TVL；注释给出当年峰值。2026 年仅统计至 10 月 9 日。",
        [
            ("2023", 0.11, "峰值 2.7 亿"),
            ("2024", 3.21, "峰值 67.2 亿"),
            ("2025", 5.67, "峰值 133.9 亿"),
            ("2026 YTD", 1.78, "当前 12.2 亿"),
        ],
        "十亿美元",
        "来源：DefiLlama protocol/pendle 日频 TVL，已剔除 staking 与 pool2。",
    )
    draw_bars(
        CHARTS / "pendle_fees.png",
        "协议费用先放大，再快速收缩",
        "2023 年仅有 7 月以后的记录；2026 年为截至 10 月 9 日的累计值，不可直接与全年比较。",
        [
            ("2023*", 0.19, "178 个记录日"),
            ("2024", 19.10, "完整年度"),
            ("2025", 39.55, "完整年度"),
            ("2026 YTD", 8.88, "281 个记录日"),
        ],
        "百万美元",
        "来源：DefiLlama summary/fees/pendle，dailyFees。单日峰值会显著影响年度总额。",
    )


def build():
    build_charts()
    document = Document()
    configure(document)

    paragraph(document, "加密货币协议研究备忘录", size=11, bold=True, color=TEAL, space_after=4)
    paragraph(document, "Pendle Finance：机制、百倍行情与代币价值捕获", size=22, bold=True, color=NAVY, space_after=4)
    paragraph(
        document,
        "一份面向投资判断的独立分析。结论先行，所有关键数字均标明口径与日期。",
        size=11,
        color=MUTED,
        space_after=8,
    )

    meta = document.add_table(rows=2, cols=4)
    meta.autofit = False
    meta_values = [
        ("研究对象", "Pendle / PENDLE"),
        ("数据截止", "2026-10-09"),
        ("当前价格", "2.09 美元"),
        ("当前市值", "3.62 亿美元"),
        ("研究问题", "业务、涨幅、价值捕获"),
        ("核心 TVL", "12.2 亿美元"),
        ("距历史高点", "-72%"),
        ("距 TVL 峰值", "-91%"),
    ]
    for index, (label, value) in enumerate(meta_values):
        cell = meta.rows[index // 4].cells[index % 4]
        cell.text = ""
        p1 = cell.paragraphs[0]
        r1 = p1.add_run(label)
        set_run_font(r1, size=8, color=MUTED)
        p2 = cell.add_paragraph()
        r2 = p2.add_run(value)
        set_run_font(r2, size=10.5, bold=True, color=NAVY)
        shade(cell, PALE)
        set_cell_border(cell)
    document.add_paragraph()

    paragraph(
        document,
        "结论：Pendle 是加密市场里少见的、已经证明产品契合度的利率基础设施；但它过去的百倍涨幅不能外推。当前代币已经把“类别龙头”的溢价计入价格，而费用和 TVL 仍处于明显的下行周期。",
        size=11,
        bold=True,
        space_after=10,
    )

    heading(document, "1. 先回答三个问题", 1)
    heading(document, "1.1 它是做什么的", 2)
    paragraph(
        document,
        "Pendle 不直接创造收益，而是把已经存在的收益变成可以定价、拆分、对冲和转让的金融资产。官网现在将自己定义为“全球最大的加密收益交易平台”，产品分成两条线：V2 做现货收益，Boros 做保证金化的资金费率交易。",
        align="justify",
    )
    paragraph(
        document,
        "V2 的核心动作是收益代币化。用户把 stETH、sUSDe、借贷凭证或其他生息资产包装成标准化的 SY，再拆成 PT 与 YT。PT 类似零息债券，到期按约定的会计资产赎回，因此买入折价 PT 等于锁定固定收益率；YT 代表到期前的全部浮动收益和积分，价格只占底层资产的一小部分，所以天然带有收益杠杆。两者通过专门为收益率设计的 AMM 和限价订单簿交易。",
        align="justify",
    )
    paragraph(
        document,
        "Boros 解决的是另一类问题。ETH 质押或资金费率长期围绕一个均值小幅波动，不用杠杆时，利率变化很难形成有意义的盈亏。Boros 用 Yield Unit 表示一单位底层资产的资金费率现金流，允许交易者以较少保证金做多或做空未来资金费率，也可把永续合约的浮动资金费变成固定成本。",
        align="justify",
    )

    heading(document, "1.2 百倍从哪里来，前景是否成立", 2)
    paragraph(
        document,
        "“前两年上涨百倍”这个说法，按极端价格衡量是成立的，但口径必须说清。CoinGecko 记录的美元最低价为 0.0338 美元，时间是 2022 年 11 月 14 日；最高价为 7.50 美元，时间是 2024 年 4 月 11 日。两者相差约 222 倍，间隔大约 17 个月。到 2026 年 10 月 9 日，价格约为 2.09 美元，较高点回撤 72%，但仍比最低点高约 62 倍。",
        align="justify",
    )
    paragraph(
        document,
        "这不是一条由利润连续复利推动的曲线。2023 年协议费用只有约 19 万美元，价格却已经开始脱离底部；真正的费用放量发生在 2024 年和 2025 年。涨幅主要来自四件事叠加：熊市底部的极低估值、LST/LRT/积分活动带来的需求冲击、V2 机制确实能服务这些需求，以及 Binance Labs 等机构关注改善了流动性和风险偏好。它证明 Pendle 抓住了一轮结构性行情，不能证明每两三年都可以再来一次百倍。",
        align="justify",
    )
    paragraph(
        document,
        "前景判断是：产品前景真实，代币的高增长前景未被当前数据证明。Pendle 有条件成为加密固定收益和利率交易的长期基础设施，但 Boros、RWA 和比特币收益都还是期权，不是已实现的收入引擎。合理的基准情形是一个有真实费用、强周期属性的利基龙头，而不是一个已经锁定巨大市场的成长垄断者。",
        align="justify",
    )

    heading(document, "1.3 经营数据与代币捕获了什么", 2)
    paragraph(
        document,
        "经营层面，Pendle 已经跨过“只有叙事”的阶段。DefiLlama 显示，核心 TVL 在 2025 年 9 月 19 日达到 133.9 亿美元，2025 年日均 56.7 亿美元；协议费用从 2024 年的 1,910 万美元增至 2025 年的 3,955 万美元。项目方 2025 年回顾还披露全年交易量 478 亿美元、新增用户 155,553 人、资产结构中稳定币占 85%。",
        align="justify",
    )
    paragraph(
        document,
        "但周期已经反转。2026 年 10 月 9 日核心 TVL 为 12.2 亿美元，较高峰下降 91%；2026 年 1 月至 9 月费用约 877 万美元，较 2025 年同期下降约 71%。近 30 日费用只有 43.3 万美元，年化约 527 万美元。",
        align="justify",
    )
    paragraph(
        document,
        "代币捕获机制是明确的：V2 收取 YT 收益的 5%，并对交易收取随到期时间缩放的手续费；扣除流动性提供者份额后，协议收入的 80% 用于回购 PENDLE，再分配给活跃的 sPENDLE 持有人，10% 进金库，10% 用于运营。它捕获的是持有人收益，不是供给销毁。按近 12 个月收入估算，质押收益大致在中个位数；按近 30 日跑速，只剩约 2%。若协议按文件中的每年 2% 终端通胀全额发放激励，当前美元增发价值已高于近期回购。价值捕获的“管道”是通的，管道里的现金流不够粗。",
        align="justify",
    )

    heading(document, "2. 业务定位与竞争位置", 1)
    paragraph(
        document,
        "可以把 DeFi 分成三层。第一层生产收益，例如 Lido、Ethena、Aave 和各类 RWA 项目；第二层提供杠杆和交易，例如永续合约交易所；Pendle 位于中间，把第一层的收益率标准化，再让第二层的交易和借贷市场使用它。官方文档明确把它称为搭建在 LST、LRT、稳定币和 RWA 之上的二阶衍生层。",
        align="justify",
    )
    paragraph(document, "因此，Pendle 的需求不是独立存在的。底层收益高、积分活动多、稳定币扩张快时，拆分和交易收益的需求就上升；这些活动退潮时，Pendle 的 TVL 和费用会比底层协议下降得更快。这是理解其财务报表的第一原则。", align="justify")
    paragraph(document, "它相对竞争对手的差异不在品牌口号，而在三个已经落地的能力：", align="justify")
    bullet(document, "把本金和收益拆开，使用户可以同时存在固定收益买方、收益投机买方和流动性提供者。")
    bullet(document, "AMM 按隐含收益率而不是代币价格集中流动性，并随到期日动态收紧曲线，降低持有到期时的无常损失。")
    bullet(document, "PT 已被 Morpho、Silo、Euler 等货币市场接受为抵押品，使固定收益凭证进入更广泛的借贷乐高，而不只停留在 Pendle 自己的界面。")
    paragraph(
        document,
        "Spectra 等协议采用了相似的 PT/YT 架构，但尚未在流动性和集成深度上取代 Pendle。真正的竞争不一定来自克隆者，也可能来自钱包、交易所理财账户和货币市场直接提供“固定利率”产品，从而把 Pendle 的复杂性隐藏起来，甚至绕开 PENDLE 代币。",
        align="justify",
    )

    heading(document, "3. 机制：两套产品，一种利率业务", 1)
    heading(document, "3.1 V2 的三层结构", 2)
    paragraph(document, "一笔典型交易可以拆成三层。", align="justify")
    bullet(document, "标准化：stETH、sUSDe 或 aUSDC 被包装成 SY。SY 持有底层资产，也是收益和积分进入系统的入口。")
    bullet(document, "拆分：1 单位 SY 可以拆成 1 单位 PT 加 1 单位 YT，也可以反向合并。到期后 PT 按会计资产赎回，YT 价值归零。")
    bullet(document, "交易：池子实际存放的是 PT 和 SY。买入 YT 时，合约利用 PT 与 YT 的价格关系做闪电交换，因此一套流动性可以同时服务两类交易。")

    add_table(
        document,
        ["角色", "持有什么", "核心收益来源", "主要风险"],
        [
            ["固定收益用户", "折价买入 PT", "到期赎回价差", "底层资产、智能合约、流动性"],
            ["收益交易者", "买入 YT", "实际收益率高于隐含收益率", "YT 时间衰减、收益不及预期"],
            ["流动性提供者", "PT/SY LP", "固定收益、底层收益、手续费、激励", "收益率偏离、激励下降"],
            ["积分农户", "通常买入 YT", "以较少资金获得底层积分", "积分规则变化、空投不及预期"],
            ["借贷集成方", "接受 PT 抵押", "可预测到期价值", "预言机、折价和底层资产风险"],
        ],
        [3.4, 3.2, 5.4, 5.6],
    )
    paragraph(document, "表 1  V2 市场的主要参与者。PT 与 YT 的风险不是对称的：PT 更接近持有到期的固定收益工具，YT 更接近浪费时间价值的期权。", size=8.5, color=MUTED, space_before=0)

    heading(document, "3.2 为什么这个 AMM 不是普通交易所", 2)
    paragraph(
        document,
        "普通 AMM 要为价格的无限波动准备流动性。收益率却通常在可判断的区间内波动，例如质押 ETH 不会长期处于 50% 或 -20%。Pendle 因而把流动性集中在预设收益率区间，并让 PT 价格随时间自然向赎回价值靠拢。官方文档据此认为，持有到期时，LP 的经济结果接近直接持有底层资产，时间因素造成的无常损失被曲线移动抵消。",
        align="justify",
    )
    paragraph(
        document,
        "手续费也按“剩余收益”而不是名义本金收取。公式是：交易费 =（费率档位 / 365）× 距离到期天数。同一笔交易，离到期一年比离到期一个月更贵。这个设计使不同期限的池子可以比较，也解释了为什么 TVL 高并不自动等于手续费高：临近到期、低换手的资金产生的交易费很少。",
        align="justify",
    )
    paragraph(
        document,
        "这里有一个常被忽略的费用规则。PT 或 LP 到期后如果不赎回，底层资产仍会继续产生收益和积分，但这些收益会被重定向到 Pendle 的费用钱包。它鼓励用户滚动仓位，同时也使“费用”里包含一部分用户惰性造成的收入，不应全部理解成主动交易需求。",
        align="justify",
    )

    heading(document, "3.3 Boros：正确的方向，尚小的账本", 2)
    paragraph(
        document,
        "Boros 目前主要交易中心化和链上永续合约市场的资金费率。每个 YU 代表一单位抵押资产在对应市场中的资金费率现金流。做多 YU 是支付固定利率、接收浮动资金费率；做空则相反。资金费率交易者可以借此表达方向观点、对冲永续仓位，或锁定跨交易所的费率差。",
        align="justify",
    )
    paragraph(
        document,
        "创始人 TN Lee 在 PANews 访谈中把 V2 和 Boros 比作同一品牌下的两条产品线，并明确表示 Pendle 不打算做现货或普通永续合约，而是集中做利率。这个战略边界是加分项。问题在于他同时表示，在 Boros 找到产品契合点并产生健康收入之前，不宜提前承诺其价值累积方式。",
        align="justify",
    )
    paragraph(
        document,
        "数字支持这种谨慎。DefiLlama 记录 Boros 于 2025 年 8 月形成 TVL，2026 年 4 月 18 日抵押品峰值仅 1,235 万美元，10 月 9 日为 749 万美元。上线以来累计费用约 80 万美元，只占 Pendle 历史总费用的 1.2%，占 2026 年费用的 5.6%。项目方在 2025 年 12 月称 Boros 四个月交易量 55 亿美元、未平仓名义价值 8,000 万美元，渗透率仅 0.04%。交易量说明有人试用，费用和抵押品说明它还没有成为利润中心。",
        align="justify",
    )

    heading(document, "4. 百倍行情的分解", 1)
    heading(document, "4.1 价格事实", 2)
    add_table(
        document,
        ["价格节点", "日期", "价格", "相对前一节点"],
        [
            ["美元最低价", "2022-11-14", "0.0338 美元", "—"],
            ["历史最高价", "2024-04-11", "7.50 美元", "约 +22,100%"],
            ["本报告快照", "2026-10-09", "2.09 美元", "较高点 -72%"],
            ["最低价至当前", "2022-11 至 2026-10", "2.09 美元", "约 +6,090%"],
        ],
        [4.4, 5.0, 3.6, 4.6],
    )
    paragraph(document, "表 2  CoinGecko 美元价格极值。222 倍使用最低价至最高价，不是任意连续 24 个月的收盘价涨幅。", size=8.5, color=MUTED)

    paragraph(
        document,
        "仅有价格倍数仍然不够，因为低点发生在全市场流动性最差的阶段，流通供给、解锁预期和市场深度都与 2024 年不同。本报告没有取得可靠的低点流通市值序列，所以不把“价格 222 倍”改写成“股东价值 222 倍”。可以确定的是，量级足够大，不能用数据误差解释掉。",
        align="justify",
    )

    heading(document, "4.2 五个真正起作用的因素", 2)
    paragraph(document, "第一，起点极低。2021 年中主网上线后，产品复杂且正逢牛市注意力外溢，TVL 到 2021 年底只有约 3,400 万美元；2022 年日均 TVL 进一步降到约 1,050 万美元。价格在 2022 年 11 月进入以美分为单位的区间。任何后续基本面改善，都会在这个基数上表现为极大倍数。", align="justify")
    paragraph(document, "第二，团队把失败周期用在产品重构上。TN Lee 曾是 KyberSwap 早期成员，2020 年 DeFi Summer 形成锁定超高收益率的想法。2021 年的早期产品没有获得持续关注，2022 年团队转向现在的 V2 架构。官方代币文档显示，团队和投资者代币到 2024 年 9 月已全部归属。至少从公开资料看，这不是一个在第一轮热度中放弃产品、只留下代币的项目。", align="justify")
    paragraph(document, "第三，2023 年至 2024 年的叙事恰好需要 Pendle 的结构。LST 需要固定利率买家，LRT 和 Ethena 积分活动需要能够加杠杆的 YT 买家。Pendle 不是在空泛地“受益于叙事”，而是提供了别人难以迅速复制的头寸：用较少资金买入未来收益和积分，或在不确定收益中锁定固定利率。TVL 于 2024 年 2 月首次越过 10 亿美元，4 月越过 50 亿美元，与价格高点处于同一窗口。", align="justify")
    paragraph(document, "第四，费用终于出现。DefiLlama 的日费用在 2024 年 4 月经常达到数万美元到十万美元，5 月出现 61 万美元的单日峰值。市场可以开始用费用而不是纯故事为代币定价。随后 Binance Labs 于 2023 年 8 月领投、Spartan Group 于 2023 年 11 月进行 OTC，提高了可投资性；这两轮金额未在 DefiLlama 披露，不能反过来当成估值锚。", align="justify")
    paragraph(document, "第五，流通与注意力的弹性。2024 年 4 月距离团队和投资者完全归属还有数月，市场交易的不一定是完全稀释后的供给。高换手、低流通和强叙事会放大价格。这是上涨的原因之一，也是后来回撤的原因之一。", align="justify")

    heading(document, "4.3 哪些解释应该降权", 2)
    bullet(document, "“传统利率衍生品名义规模超过 400 万亿美元，所以 Pendle 有巨大空间。”官方引用的是 BIS 的名义本金统计。名义本金不是收入，绝大部分也不是加密市场可迁移的零售或链上机构需求。它适合说明利率市场很大，不适合做收入预测。")
    bullet(document, "“TVL 曾经达到 134 亿美元，所以协议曾经值数百亿美元。”TVL 是托管或记账中的底层资产，不是 Pendle 的收入资产。Pendle 只抽取其中很小一部分收益和交易费。")
    bullet(document, "“机构标志出现在官网，所以需求和资金已经机构化。”Amber、Galaxy、Binance、OKX、Bybit、Fasanara 和 Republic 的展示说明有专业用户接触过产品，但不能替代持仓、留存和收入披露。")

    heading(document, "5. 经营数据：增长是真实的，持续性尚未证明", 1)
    paragraph(document, "以下经营数据以 DefiLlama 的可复核时间序列为主。项目方 2025 年回顾使用不同统计口径，只在能互相印证时引用。", align="justify")

    document.add_picture(str(CHARTS / "pendle_tvl.png"), width=Cm(17.4))
    paragraph(document, "图 1  日均 TVL 显示 2024 年完成跃迁，2025 年继续提高，2026 年均值已回落到接近 2024 年以前的趋势之外。", size=8.5, color=MUTED)

    add_table(
        document,
        ["年份", "日均 TVL", "年内峰值", "年末或当前", "记录日"],
        [
            ["2021", "0.27 亿", "0.38 亿", "0.34 亿", "199"],
            ["2022", "0.10 亿", "0.36 亿", "0.15 亿", "365"],
            ["2023", "1.14 亿", "2.73 亿", "2.34 亿", "365"],
            ["2024", "32.1 亿", "67.2 亿", "44.2 亿", "366"],
            ["2025", "56.7 亿", "133.9 亿", "37.4 亿", "365"],
            ["2026 YTD", "17.8 亿", "38.9 亿", "12.2 亿", "283"],
        ],
        [3.0, 3.2, 3.4, 4.0, 3.0],
    )
    paragraph(document, "表 3  DefiLlama 父协议 TVL，单位为美元；2026 年当前值取 10 月 9 日。该序列包含协议定义下的流动性价值，已与 staking、pool2 分列。", size=8.5, color=MUTED)

    paragraph(
        document,
        "TVL 的内部结构比总额更重要。2025 年 9 月以太坊峰值约 113 亿美元，说明高峰并不是分散在十几条链上的稳固网络，而是高度集中的阶段性存款。2026 年 10 月，以太坊仍占核心 TVL 的 62%，Arbitrum 占 15%，Monad 占 12%，X Layer 占 5%，Plasma 占 4%。Plasma 曾在 2026 年 1 月达到 14.2 亿美元，Hyperliquid 曾在 2025 年 9 月达到 14.1 亿美元，Sonic 曾达到 2.7 亿美元；三者当前分别只剩 0.43 亿、0.09 亿和 0.005 亿美元。多链扩展带来过 TVL，但留存很弱。",
        align="justify",
    )

    document.add_picture(str(CHARTS / "pendle_fees.png"), width=Cm(17.4))
    paragraph(document, "图 2  费用在 2025 年达到峰值，但 2026 年尚未表现出新的增长斜率。", size=8.5, color=MUTED)

    add_table(
        document,
        ["期间", "协议费用", "协议收入", "收入/费用", "备注"],
        [
            ["2023*", "19.1 万", "16.7 万", "87%", "序列自 7 月开始"],
            ["2024", "1,910 万", "1,771 万", "93%", "完整年度"],
            ["2025", "3,955 万", "3,837 万", "97%", "完整年度"],
            ["2026 YTD", "888 万", "875 万", "99%", "截至 10 月 9 日"],
            ["近 12 个月", "1,702 万", "1,667 万", "98%", "滚动窗口"],
            ["近 30 日年化", "527 万", "518 万", "98%", "短期跑速"],
            ["历史累计", "6,772 万", "6,500 万", "96%", "含异常峰值日"],
        ],
        [3.2, 3.2, 3.2, 2.8, 4.2],
    )
    paragraph(document, "表 4  DefiLlama 费用与收入，单位为美元。收入口径是归协议及其代币持有人的部分，不等于全部用户支付。", size=8.5, color=MUTED)

    paragraph(document, "费用质量有三个折扣：", align="justify")
    bullet(document, "极端集中。历史单日费用峰值是 2025 年 1 月 8 日的 608 万美元；最大的 10 个费用日占历史累计费用约 26%。这类峰值常与积分、空投或到期结算有关，不能按 365 天复制。")
    bullet(document, "同比已经转负。2026 年 1 月至 9 月费用约 877 万美元，2025 年同期约 3,070 万美元，下降约 71%。9 月单月仅 56 万美元。")
    bullet(document, "费用率很低。近 12 个月费用除以当前 TVL 约 1.4%，近 30 日跑速对应的费用率只有约 0.43%。Pendle 是高资金占用、低抽成的市场，不是高利润的交易平台。")

    paragraph(
        document,
        "交易量口径需要分开。DefiLlama 的现货交易量序列从 2024 年 6 月才开始，2025 年记录 406 亿美元；项目方回顾给出的 2025 年交易量是 478 亿美元。差异来自起始日期、YT 名义价值和统计边界，不改变“数百亿美元成交、但 2026 年显著放缓”的结论。DefiLlama 2026 年前 281 个记录日的成交量约为 60 亿美元。",
        align="justify",
    )
    paragraph(
        document,
        "项目方回顾中最有信息量的不是峰值，而是资产结构：2025 年投资分布为稳定币 85%、比特币 3%、以太坊 5%、其他 7%，并称提供了 580 亿美元固定收益、同比增长 161%。如果这个结构持续，Pendle 就从“积分杠杆赌场”转向“稳定币固定收益市场”，需求质量会更好，但单用户产生的投机费用也会更低。当前费用下滑说明，这种转型尚未补上积分退潮留下的收入缺口。",
        align="justify",
    )

    heading(document, "6. 代币：供给、权利与捕获能力", 1)
    heading(document, "6.1 供给没有隐藏的悬崖，但没有硬顶", 2)
    add_table(
        document,
        ["指标", "数值", "解释"],
        [
            ["快照价格", "2.09 美元", "CoinGecko，2026-10-09 前后"],
            ["流通供给", "1.738 亿枚", "CoinGecko 口径"],
            ["总供给", "2.815 亿枚", "无最大供给上限"],
            ["流通比例", "61.7%", "两种口径并不完全等同"],
            ["流通市值", "3.623 亿美元", "排名约第 130 位"],
            ["完全稀释价值", "5.869 亿美元", "按当前总供给，不含未来通胀"],
            ["历史最高价", "7.50 美元", "2024-04-11"],
            ["历史最低价", "0.0338 美元", "2022-11-14"],
        ],
        [4.0, 4.2, 9.4],
    )
    paragraph(document, "表 5  代币快照。FDV 没有包含 2% 终端通胀的永续稀释，因此仍是保守的静态口径。", size=8.5, color=MUTED)

    paragraph(
        document,
        "官方流通供给定义比交易所聚合器更严格。文档把 sPENDLE 合约、尚未退出的 vePENDLE、生态基金、治理多签和团队多签中的 PENDLE 都排除在自由流通之外。CoinGecko 的 1.738 亿枚不一定遵守这五个扣减项，所以不应把 61.7% 直接解释成自由流通比例。由于本报告没有逐一读取五个地址余额，不另报一个未验证的流通量。",
        align="justify",
    )
    paragraph(
        document,
        "供给端的好消息是大额历史包袱已经释放。官方文档写明，截至 2024 年 9 月，团队和投资者代币全部归属；此后新增供给来自激励和生态建设。2021 年种子轮在 DefiLlama 中记录为 370 万美元，后续 Binance Labs 与 Spartan 轮次金额未披露。至少不存在一个即将集中到期、但尚未公开的早期投资者悬崖。",
        align="justify",
    )
    paragraph(
        document,
        "坏消息是供给没有上限。旧规则是 2024 年 9 月每周排放 216,076 枚，每周降低 1.1%，直到 2026 年 4 月，其后转入每年 2% 的终端通胀。今天已经经过这个切换日期，但本报告没有直接读取排放合约，因此 2% 应视为文件中的上限和基准，而不是链上实测值。新的算法激励模型按池子自己的流动性和费用计算奖励，并设有每池美元上限；当 PENDLE 低于 1.25 美元时，按 1.25 美元折算排放数量，避免低价时无限制增发。这比旧的纯粹争夺排放份额更健康。",
        align="justify",
    )

    heading(document, "6.2 费用如何进入代币", 2)
    paragraph(document, "当前 V2 规则可以精确描述：", align="justify")
    bullet(document, "YT 费用：所有存续 YT 产生的收益和积分收取 5%；到期后未赎回 PT 对应的收益也归入这一逻辑。")
    bullet(document, "交易费：按费率档位和剩余天数计算，由池子部署者设定。目前文档称实际部署者仍是 Pendle 团队。")
    bullet(document, "分配：全部交易费的 20% 先给 LP。剩余交易费加全部 YT 费用中，80% 进入回购，10% 给协议金库，10% 给运营。")
    bullet(document, "回购执行：费用每两周归集到以太坊回购合约 0x9e08C5499f953C6297A7755BcBcEd383b606896b，随后按一小时 TWAP 买入。")
    bullet(document, "持有人分配：回购所得 PENDLE 最多 100% 分给活跃 sPENDLE 持有人。积分类费用按原代币空投，不强制换成 PENDLE。")

    paragraph(
        document,
        "2026 年 1 月 20 日上线的 sPENDLE 改变了参与方式。PENDLE 可以 1:1 立刻换成 sPENDLE；sPENDLE 本身不会复利增值。常规退出等待 14 天，即时退出收费 5%。有治理提案可投时，不投票的钱包会被视为不活跃，从而失去当期奖励；没有提案的周期则全部视为活跃。部署在合格 DeFi 集成中的 sPENDLE 持续视为活跃。旧 vePENDLE 在 1 月 29 日快照后停止新锁仓，并按剩余锁定期获得最高 4 倍、逐步衰减的虚拟 sPENDLE。",
        align="justify",
    )
    paragraph(
        document,
        "这是一次实质性改进。旧的多年锁仓把大量持有人挡在费用分配之外；可转让的 sPENDLE 降低了参与门槛，也让质押凭证有机会进入其他 DeFi。但它没有把代币变成股权。奖励是代币本身，收到后可以在 14 天后卖出，所以回购创造的是阶段性买盘和持有人收益，不是永久性供给收缩。",
        align="justify",
    )

    heading(document, "6.3 捕获能力的数量边界", 2)
    paragraph(document, "用 DefiLlama 的以太坊 staking TVL 作为质押基数，可以得到一个粗略但有方向性的收益率。该值在 10 月 9 日为 1.988 亿美元。若它主要代表质押的 PENDLE，按 2.09 美元计算约等于 9,510 万枚，占总供给 34%。这是估算，不是链上代币余额审计。", align="justify")
    add_table(
        document,
        ["测算", "收入基础", "80% 回购", "相对 1.99 亿美元质押价值"],
        [
            ["近 12 个月", "1,667 万美元", "1,334 万美元", "约 6.7%"],
            ["2026 年化 YTD", "约 1,137 万美元", "约 909 万美元", "约 4.6%"],
            ["近 30 日年化", "518 万美元", "415 万美元", "约 2.1%"],
            ["2% 增发压力测试", "—", "增发价值约 1,177 万美元", "回购尚未覆盖"],
        ],
        [3.6, 3.8, 4.4, 5.8],
    )
    paragraph(document, "表 6  持有人收益只是机械测算。它假设 staking TVL 全部是 PENDLE、80% 规则持续适用，并忽略奖励的代币价格波动、活跃度过滤和积分空投。", size=8.5, color=MUTED)

    paragraph(document, "这张表给出三个投资上重要的结论：", align="justify")
    bullet(document, "按过去 12 个月看，回购大体能抵消 2% 全额增发的美元价值，持有人还有正收益。")
    bullet(document, "按最近 30 日看，回购只有约 415 万美元，而 2% 全额增发价值约 1,177 万美元。当前跑速下，代币经济从“费用覆盖稀释”变成“稀释超过费用”。")
    bullet(document, "由于新激励模型可能不会发满 2%，实际稀释可能更低。但在读取排放合约之前，不能把这种可能性当成事实。")
    paragraph(
        document,
        "Boros 的费用目前不应自动算进上述回购。官方 sPENDLE 页面写的是 Pendle V2 的收益费和交易费，没有写明 Boros 的全部费用都进入同一回购池。创始人也明确把 Boros 的价值累积机制留到产品契合之后。DefiLlama 已记录 Boros 的协议收入，但这只说明费用被协议收取，不能证明 100% 或 80% 归 PENDLE 持有人。",
        align="justify",
    )

    heading(document, "7. 当前估值已经不便宜", 1)
    add_table(
        document,
        ["估值口径", "年化费用或收入", "流通市值倍数", "含义"],
        [
            ["近 12 个月费用", "1,702 万美元", "21.3 倍", "包含 2025 年尾部高收入"],
            ["近 12 个月收入", "1,667 万美元", "21.7 倍", "更接近可分配基础"],
            ["2026 YTD 年化费用", "1,153 万美元", "31.4 倍", "仍混有上半年峰值"],
            ["近 30 日年化收入", "518 万美元", "69.9 倍", "当前需求的严格口径"],
            ["静态 FDV / 近 12 个月收入", "1,667 万美元", "35.2 倍", "不含未来通胀"],
        ],
        [5.0, 3.8, 3.4, 4.4],
    )
    paragraph(document, "表 7  倍数使用 3.623 亿美元流通市值或 5.869 亿美元 FDV。加密项目的费用倍数不能直接与股票市盈率比较，但足以判断价格是否已反映复苏。", size=8.5, color=MUTED)

    paragraph(
        document,
        "价格较高点下跌 72%，容易造成“已经很便宜”的错觉。便宜与否要看分母。若未来费用稳定在 2,000 万至 2,500 万美元，并以 15 至 20 倍费用定价，对应流通市值约为 3.0 亿至 5.0 亿美元，当前价格大体位于这个区间内。也就是说，现价已经提前反映了费用从当前低点明显恢复，并没有把协议当成失败项目定价。",
        align="justify",
    )
    paragraph(
        document,
        "再涨 10 倍意味着约 36 亿美元流通市值。即便市场愿意给 30 倍费用，也需要每年约 1.2 亿美元的可持续费用，较近 30 日跑速增长 20 倍以上，较 2025 年峰值年份仍需增长约 3 倍并长期维持。Boros 或 RWA 并非数学上不可能实现它，但今天没有任何经营数据支持把这当作基准情形。",
        align="justify",
    )

    heading(document, "8. 情景、催化剂与证伪条件", 1)
    add_table(
        document,
        ["情景", "需要看到的证据", "代币含义"],
        [
            ["基准", "TVL 稳定在 10 亿至 30 亿美元，年费用恢复到 1,500 万至 3,000 万美元", "有持有价值，但难以重复历史倍数"],
            ["乐观", "Boros 费用连续多个季度跃升，或 RWA/BTC 收益形成可留存市场", "可以支持新一轮重估，仍需看分配规则"],
            ["悲观", "TVL 跌破 10 亿美元且月费用长期低于 50 万美元", "回购无法覆盖稀释，代币更依赖叙事"],
        ],
        [2.4, 9.2, 6.0],
    )
    paragraph(document, "表 8  情景用于跟踪，不是目标价。乐观情景必须同时满足“收入增长”和“收入归代币”两个条件。", size=8.5, color=MUTED)

    paragraph(document, "未来 12 个月真正重要的催化剂只有四类：", align="justify")
    bullet(document, "稳定币固定收益市场的留存，而不是新链上线当天的 TVL。")
    bullet(document, "Boros 从交易量转向费用、抵押品和重复用户，并公布明确的 PENDLE 分配比例。")
    bullet(document, "PT 抵押在外部货币市场中的使用规模。这代表 Pendle 是否成为其他协议的默认组件。")
    bullet(document, "实际周排放低于 2% 上限，且回购合约保持透明执行。")
    paragraph(document, "以下观察会削弱本报告的正面判断：", align="justify")
    bullet(document, "核心月费用连续低于 50 万美元，同时质押奖励继续完全依赖代币增发。")
    bullet(document, "新链 TVL 继续呈现“上线即峰值、数月后回落”的模式。")
    bullet(document, "Boros 扩大名义未平仓，但费用长期停留在每月数万美元。")
    bullet(document, "治理把回购比例下调，或把新增产品的收入留在团队控制的实体。")
    bullet(document, "底层稳定币、RWA 或 LST 出现重大损失，导致 PT 的“到期确定价值”失效。")

    heading(document, "9. 风险地图", 1)
    bullet(document, "需求风险：积分、空投和激励存款曾是增长核心。稳定币转型是正确方向，但目前没有证明它能产生同等费用。")
    bullet(document, "底层资产风险：官方 FAQ 明确声明，第三方协议被利用造成的损失不由 Pendle 负责。Pendle 的 TVL 越大，嵌入的外部信用风险越大。")
    bullet(document, "智能合约与预言机风险：V2 和 Boros 均有 ChainSecurity、Spearbit 等审计，DefiLlama 黑客库没有 Pendle 核心协议被盗记录。审计不能消除风险，Boros 的保证金、清算和跨市场预言机增加了新的失败面。")
    bullet(document, "用户安全风险：公开报道中的损失更多与钓鱼、授权和钱包操作有关，团队曾澄清相关事件不是核心协议被攻击。对协议估值不是直接资金缺口，但会影响分发和品牌。")
    bullet(document, "治理与费用风险：池子费率目前实际上由团队部署决定；回购比例和 Boros 分配都可由治理改变。代币权利是政策，不是不可更改的链上股息。")
    bullet(document, "流动性与解锁风险：历史投资者悬崖已过，但生态基金、团队多签和激励库存仍可能进入市场。sPENDLE 的 14 天退出队列在恐慌时也会集中解锁。")
    bullet(document, "数据风险：费用峰值、交易名义价值和 TVL 都可能被积分计价、一次性结算或跨链重复叙事放大。本报告优先使用时间序列，不用单一宣传峰值做估值。")

    heading(document, "10. 最终判断", 1)
    paragraph(
        document,
        "Pendle 值得被当作真正的金融协议研究，而不是普通的激励型 DeFi 项目。它找到了一个清晰的工作：给链上收益提供期限结构和交易场所。V2 的 PT/YT 设计、收益率 AMM、PT 抵押集成和后来的回购机制，共同构成了其他项目不容易用一次分叉复制的经营系统。2024 年至 2025 年的 TVL、交易量和费用证明这套系统有市场需求。",
        align="justify",
    )
    paragraph(
        document,
        "但“与众不同”不等于“仍有百倍空间”。222 倍发生在从周期底部到叙事极致的特殊区间；今天的起点是 3.6 亿美元市值、12 亿美元 TVL，近 30 日费用只有 43 万美元。类别地位仍在，增长斜率不在。Boros 是最合理的第二曲线，可是抵押品不到 800 万美元、历史费用不到 100 万美元，且代币分配尚未完全承诺。",
        align="justify",
    )
    paragraph(
        document,
        "因此，对项目本身给予正面评价，对当前价格下的高增长预期保持否定。若只问 Pendle 是否有前景，答案是有，它是加密利率层最可信的候选者之一。若问 PENDLE 是否因为曾经上涨百倍、现在仍有明确的价值捕获，就应该再涨一个数量级，答案是否定的。它现在更像一个需要用费用复苏和 Boros 真实收入来证明自己的优质周期资产。",
        align="justify",
    )

    heading(document, "11. 方法、局限与资料", 1)
    paragraph(document, "本报告没有使用未标明的市场传闻填补空缺。主要处理规则如下：", align="justify")
    bullet(document, "机制和代币规则优先采用 Pendle 官方文档；访谈只用于说明战略意图。")
    bullet(document, "TVL、费用、收入和交易量优先采用 DefiLlama API 的日频数据，并在 2026 年 10 月 9 日下载。")
    bullet(document, "价格、供给和市值采用 CoinGecko 与 CoinPaprika 的公开接口。两者的 24 小时成交额差异较大，故不把它作为核心论据。")
    bullet(document, "项目方 2025 年回顾未能直接打开原始长文，只通过 BlockBeats 2025 年 12 月 5 日对官方数据的转述引用，并与 DefiLlama 交叉验证。")
    bullet(document, "未直接审计回购合约余额、五个非流通地址和当前排放合约。涉及这些地址的结论都表述为规则或估算。")
    paragraph(document, "主要来源：", align="justify")
    bullet(document, "Pendle 官网：https://www.pendle.finance/")
    bullet(document, "V2 文档：https://docs.pendle.finance/pendle-v2/Introduction")
    bullet(document, "费用规则：https://docs.pendle.finance/pendle-v2/ProtocolMechanics/Mechanisms/Fees")
    bullet(document, "代币与 sPENDLE：https://docs.pendle.finance/pendle-v2/ProtocolMechanics/Mechanisms/Tokenomics")
    bullet(document, "Boros 文档：https://docs.pendle.finance/boros-docs/Introduction")
    bullet(document, "DefiLlama Pendle：https://defillama.com/protocol/pendle")
    bullet(document, "CoinGecko Pendle：https://www.coingecko.com/en/coins/pendle")
    bullet(document, "BlockBeats 对 2025 年官方回顾的报道：https://en.theblockbeats.news/flash/323178")
    bullet(document, "PANews 对 TN Lee 的访谈：https://www.panewslab.com/")
    paragraph(
        document,
        "免责声明：本文件是基于公开资料的研究备忘录，不是购买、出售或持有任何代币的建议，也不构成对未来价格、收益率或协议安全性的承诺。加密资产可能损失全部本金；智能合约、预言机、稳定币和治理规则均可能变化。",
        size=9,
        color=MUTED,
        align="justify",
    )
    paragraph(
        document,
        "跟踪清单：每月核对核心 TVL、协议费用、回购执行、实际排放、Boros 抵押品与费用，以及 PT 在外部借贷市场的使用规模。只有费用恢复和分配规则同时改善，才应上调代币结论。",
        size=10.5,
        align="justify",
    )

    document.save(OUT)
    print(OUT)


if __name__ == "__main__":
    build()
