# Crypto Analysis · 加密资产研究笔记

个人加密资产研究资料库：DeFi 协议深度报告、Uniswap 做市机制笔记、以太坊隐私赛道总结。

所有报告都是**自包含的单文件 HTML**——CSS、JavaScript、图表数据全部内联，下载后双击即可离线阅读，交互式图表和估值模拟器都能正常工作，不依赖任何外部 CDN。

> ⚠️ **免责声明**：全部内容仅为机制研究与个人分析，**不构成投资建议**。文中大量数字是为说明机制而构造的算例，不是任何真实池子的数据。数据口径与截止日期在各报告开头注明。

---

## 目录结构

```
.
├── defi/                            # DeFi 协议深度报告
│   ├── AAVE/                        # Aave 项目研究报告
│   ├── Ethena研究报告/               # Ethena（ENA）协议深度报告
│   ├── Hyperliquid研究报告/          # Hyperliquid（HYPE）协议深度报告
│   ├── Lido研究报告/                 # Lido 协议深度报告（HTML + Markdown）
│   ├── Maple研究报告/                # Maple Finance 协议深度报告
│   ├── Pendle研究报告/               # Pendle（PENDLE）协议深度报告
│   └── uniswap-lp-notes/            # Uniswap 流动性做市深度笔记（10 章 + 插图）
├── Quant研究报告/                    # Quant（QNT）协议深度报告
├── Pendle_Finance_分析报告.html       # Pendle 分析报告（网页版）
├── Pendle_Finance_分析报告_20261009.docx  # Pendle 分析报告（Word 版，12 页）
├── 隐私/                             # 以太坊 / EVM 隐私赛道
├── scripts/                         # 报告构建脚本（抓数 / 汇总 / 生成图表与 DOCX）
├── charts/                          # 脚本生成的图表
├── data/                            # DefiLlama / Hyperliquid / CoinGecko 原始数据转储
├── preview-v2/ · preview-v3/        # DOCX 渲染出的页面预览图（排版校验用）
└── README.md
```

---

## 🔹 defi/ — DeFi 协议研究

| 报告 | 内容 | 日期 |
|---|---|---|
| **[Hyperliquid（HYPE）协议深度报告](<defi/Hyperliquid研究报告/Hyperliquid协议深度报告.html>)** | 永续 DEX 三代演进（dYdX → GMX → Hyperliquid）与 Hyperliquid 胜出的原因：自建 L1 全链上订单簿、零风投 + 31% 空投、约 81% 手续费进入援助基金自动回购；HYPE 近 12 个月 $7.1 亿收入（全加密第 3）与同业估值对比、从 $3.8 到 $98 的五阶段行情复盘（2026 年翻倍主要来自估值倍数扩张）、HIP-3 美股 / 大宗商品永续与 ETF / 上市公司买盘，以及团队解锁的供需账（累计只领 4%，但领出后基本卖出，2026-10 一次场外出售 375 万枚，近半年月均领取已与回购持平）。含估值与供需模拟器。 | 2026-10-09 |
| **[Pendle（PENDLE）协议深度报告](<defi/Pendle研究报告/Pendle协议深度报告.html>)** | PT / YT 收益拆分与时间衰减 AMM 的机制、2022–2024 年约 180 倍行情的六个驱动（费用同步增长约 100 倍）、Ethena × Aave 循环贷如何把 TVL 推到 $133.9 亿又在两天内蒸发一半、「收入 ≈ TVL × 收益率 × 5%」的双重顺周期，以及 sPENDLE 改革后 80% 回购、近零通胀的价值捕获能力。含 PT / YT 收益计算器与估值模拟器。 | 2026-10-09 |
| **[Aave 项目研究报告](<defi/AAVE/aave研究报告.html>)** | Aave 与 Compound 的分野、Aave 的收入结构与估值定位、Kelp / rsETH 跨链桥事件复盘，以及「存款人」与「代币持有人」两种身份下完全不同的结论。含收入 / 回购情景模拟器。 | 2026-10-08 |
| **[Ethena（ENA）协议深度报告](<defi/Ethena研究报告/Ethena协议深度报告.html>)** | USDe「现货多头 + 永续空头」的 Delta 中性机制与资金费率收益引擎、2026 年从基差交易切换到稳定币理财组合的转型、USDe 从 $148 亿缩水到 $49 亿的经营数据、毛收入如何几乎全部分给 sUSDe / 交易所合作方 / Aave 激励，以及费用开关「$75 亿才启动、首档回购远小于团队解锁」的价值捕获分析。含回购 vs 解锁模拟器。 | 2026-10-08 |
| **[Lido 协议深度报告](<defi/Lido研究报告/Lido协议深度报告.html>)** | 最大的以太坊流动性质押协议为什么撑不起 LDO 的价格：收「收益」而非本金的收费模式、DAO「以 ETH 收钱、以美元花钱」的三重挤压、协议成功与代币价值之间的传导断链、金库如何填补亏损，以及 EIP-8363 增发提案的尾部风险。同时提供 [Markdown 版](<defi/Lido研究报告/Lido协议深度报告.md>)。 | 2026-10-07 |
| **[Maple Finance 协议深度报告](<defi/Maple研究报告/Maple协议深度报告.html>)** | Maple 把存款人的 USDC / USDT / USDG 以超额抵押贷款的形式借给加密做市商、交易公司等机构，借款利息扣除管理费后作为收益分给存款人。报告拆解了这种「链上资金池 + 链下尽调清算」的混合架构：资金池、份额、费用与违约记账在智能合约里，而借款人准入、条款谈判、抵押品托管、盯市与清算由 Maple 在链下执行并以法律合同兜底；并以 syrupUSDC 为例梳理存款人与借款人两条链路如何在资金池汇合。 | 2026-10-07 |
| **[Quant（QNT）协议深度报告](<Quant研究报告/Quant协议深度报告.html>)** | Quant 作为银行间「中间件层」的真实定位、2026-09 那轮行情的逐步拆解、QNT 的价值捕获管道为何在官方文档里被放开成「可选的」，以及与 CFG 之间三种不同资产类型 / 不同定价锚的对比。含估值翻译器。 | 2026-10-05 |
| **[Uniswap 流动性做市深度笔记](<defi/uniswap-lp-notes/README.md>)** | 从 `x · y = K` 到 V4 Hook 源码的一整套推导，共 10 章 + 11 张矢量插图。见下方单独说明。 | — |

### Uniswap 流动性做市笔记

一句话：**把 Uniswap 的池子看成一个几何对象——一条曲线、一条从原点出发的射线、以及 LP 自己选的那段弧。** 一旦有了这张图，V2 / V3 / V4 的行为都能自己推出来，不用背。

- 📖 [**笔记总目录 / 一页速查卡**](<defi/uniswap-lp-notes/README.md>) ← 建议从这里进入
- 🖥️ [单文件 HTML 全本](<defi/uniswap-lp-notes/Uniswap流动性做市深度笔记.html>)（约 400 KB，含全部交互图表）
- 📐 插图在 [`figures/`](<defi/uniswap-lp-notes/figures/>)，SVG 矢量版 + `preview/` 里的 PNG 版
- 🛠️ 所有插图由 [`_tools/gen_figures.py`](<defi/uniswap-lp-notes/_tools/gen_figures.py>) 脚本生成，不是手绘，可改参数重新生成

覆盖内容：坐标系统与价格、V2 恒定乘积与无常损失、V3 集中流动性、V4 架构与机制、V4 Hook 机制（源码级）、MEME 做市与区间决策、以太坊与 Solana 生态对比、11 条常见误区与安全检查清单、公式速查与源码索引。

---

## 🔹 隐私/ — 以太坊 / EVM 隐私赛道

| 报告 | 内容 | 日期 |
|---|---|---|
| **[以太坊 / EVM 隐私赛道深度报告](<隐私/以太坊-EVM隐私赛道项目总结-2026-10.html>)** | RAILGUN、Zama、Aztec、Fhenix 四家横向对比。核心观察：「隐私」在这四个项目里指的不是同一件事——RAILGUN 隐藏的是「谁和谁交易」，Zama 与 Fhenix 隐藏的是「余额和金额是多少」，Aztec 让开发者自己决定哪些状态私有。客户、监管压力和估值逻辑因此完全不同。含 RAIL 的收入倍数估值模拟器。 | 2026-10-05 |

---

## 🔹 其他交付物

| 交付物 | 说明 | 日期 |
|---|---|---|
| **[Pendle Finance 分析报告（网页版）](<Pendle_Finance_分析报告.html>)** | 与 `defi/Pendle研究报告/` 同主题的分析报告网页版，可离线打开。 | 2026-10-09 |
| **`Pendle_Finance_分析报告_20261009.docx`** | 同一份 Pendle 分析的 Word 备忘录版本，共 12 页，结论先行、关键数字标注口径与日期。 | 2026-10-09 |

> 根目录的 `Quant研究报告/` 与 `defi/` 下的各协议报告是同类产物，只是尚未归入 `defi/` 目录。

### 构建材料（非阅读内容）

这几项是生成报告时的中间产物与工具，保留在这里是为了可复现：

| 目录 | 内容 |
|---|---|
| [`scripts/`](<scripts/>) | 抓数与构建脚本：`fetch_*.py` / `fetch_*.mjs` 抓取 DefiLlama、Hyperliquid、CoinGecko 数据；`summarize_*.py` / `*.mjs` 汇总关键指标；[`build_pendle_report.py`](<scripts/build_pendle_report.py>) 生成图表与 Pendle 的 DOCX 备忘录。 |
| `charts/` | `build_pendle_report.py` 生成的图表 PNG。 |
| `data/` | 原始 API 转储（DefiLlama / Hyperliquid / CoinGecko），约 38 MB。 |
| `preview-v2/` · `preview-v3/` | DOCX 渲染出的页面预览图，用于排版校验。 |

> 脚本中的路径均基于脚本自身位置解析，克隆到任何目录都能直接运行。

---

## 关于可靠性

这套资料对**每一条结论**都区分了性质，不混为一谈：

- **纯粹数学推导** —— 可以自己验算，中间步骤都给出。
- **协议实现细节** —— 尽量对照源码（如 v3-core / v4-core）逐条核实，并给出文件链接。
- **市场判断** —— 显式标注是**结构性推理**还是**已验证事实**。

未经核实的内容都会显式标注 ⚠️ **未验证**。

## 阅读方式

克隆后直接用浏览器打开任意 `.html` 文件即可，无需构建、无需联网：

```bash
git clone https://github.com/zhangjw1/crypto_analysis.git
```

---

**本仓库全部内容不构成投资建议。**
