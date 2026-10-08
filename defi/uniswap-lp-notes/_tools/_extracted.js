
/* ============================================================
   1) 公式与图表引擎（原生 SVG，无外部依赖）
   ============================================================ */
(function () {
  const css = (v) => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
  const PAL = ["--c1","--c2","--c3","--c4","--c5","--c6","--c7"];
  const color = (i, tone) => css(tone || PAL[i % PAL.length]);
  const NS = "http://www.w3.org/2000/svg";
  const fmt = (v) => (Math.abs(v) >= 100 ? Math.round(v).toLocaleString("en-US")
                    : (Math.round(v * 100) / 100).toString());

  function niceRange(min, max) {
    min = Math.min(0, min); max = Math.max(0, max);
    if (max === min) max = min + 1;
    const span = max - min, raw = span / 5, mag = Math.pow(10, Math.floor(Math.log10(raw)));
    const step = [1, 2, 2.5, 5, 10].map((m) => m * mag).find((s) => span / s <= 6);
    return { lo: Math.floor(min / step) * step, hi: Math.ceil(max / step) * step, step };
  }
  function el(tag, attrs, parent, text) {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (text !== undefined) e.textContent = text;
    if (parent) parent.appendChild(e);
    return e;
  }
  function legend(host, series) {
    if (series.length < 2) return;
    const d = document.createElement("div"); d.className = "legend";
    series.forEach((s, i) => { d.insertAdjacentHTML("beforeend",
      `<span><i style="background:${color(i, s.tone)}"></i>${s.name}</span>`); });
    host.appendChild(d);
  }

  function lineChart(id, cats, series, opt = {}) {
    const host = document.getElementById(id); if (!host) return;
    host.innerHTML = "";
    const W = 640, H = opt.height || 260, L = 52, R = 14, T = 12, B = 34;
    const all = series.flatMap((s) => s.data).filter((v) => isFinite(v));
    const { lo, hi, step } = niceRange(Math.min(...all), Math.max(...all));
    const svg = el("svg", { viewBox: `0 0 ${W} ${H}` }, host);
    const x = (i) => L + (cats.length === 1 ? 0 : (i * (W - L - R)) / (cats.length - 1));
    const y = (v) => T + ((hi - v) * (H - T - B)) / (hi - lo);
    for (let v = lo; v <= hi + 1e-9; v += step) {
      el("line", { x1: L, x2: W - R, y1: y(v), y2: y(v), stroke: css("--line"),
                   "stroke-width": Math.abs(v) < 1e-9 ? 1.2 : 0.6 }, svg);
      el("text", { x: L - 6, y: y(v) + 4, "text-anchor": "end" }, svg, fmt(v) + (opt.suffix || ""));
    }
    const every = Math.max(1, Math.ceil(cats.length / 12));
    cats.forEach((c, i) => { if (i % every === 0)
      el("text", { x: x(i), y: H - 12, "text-anchor": "middle" }, svg, c); });
    if (opt.hlines) opt.hlines.forEach((h) => {
      el("line", { x1: L, x2: W - R, y1: y(h.v), y2: y(h.v), stroke: css(h.tone || "--c2"),
                   "stroke-width": 1.4, "stroke-dasharray": "6 4" }, svg);
      el("text", { x: W - R, y: y(h.v) - 4, "text-anchor": "end",
                   style: "font-size:10px" }, svg, h.name);
    });
    series.forEach((s, si) => {
      const col = color(si, s.tone);
      const pts = s.data.map((v, i) => (isFinite(v) ? `${x(i)},${y(v)}` : null))
                         .filter(Boolean).join(" ");
      el("polyline", { points: pts, fill: "none", stroke: col, "stroke-width": 2 }, svg);
      s.data.forEach((v, i) => {
        if (!isFinite(v)) return;
        const c = el("circle", { cx: x(i), cy: y(v), r: 3, fill: col }, svg);
        el("title", {}, c, `${s.name}｜${cats[i]}：${fmt(v)}${opt.suffix || ""}`);
      });
    });
    if (opt.marker !== undefined && isFinite(opt.marker.v)) {
      const mx = x(opt.marker.i), my = y(opt.marker.v);
      el("circle", { cx: mx, cy: my, r: 6, fill: css("--c2"), stroke: css("--bg"),
                     "stroke-width": 2 }, svg);
    }
    legend(host, series);
  }

  /* ---------- 惰性渲染：滚动到可见时才画 ---------- */
  const pending = new Map();
  function defer(key, fn) { pending.set(key, fn); }
  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (!e.isIntersecting) return;
      io.unobserve(e.target);
      const fn = pending.get(e.target.id);
      if (fn) { fn(); pending.delete(e.target.id); }
    });
  }, { rootMargin: "300px" });

  /* ============================================================
     2) 误区列表
     ============================================================ */
  const MYTHS = [
    ["根本误解", "red", "1. ETH 涨价，池子就「失衡」了",
     "x·(y/x) = y 是<b>代数恒等式</b>，不是需要维持的约束。价格就是这么定义的，所以池子<b>永远不可能失衡</b>。而且合约根本不知道美元是什么，它只有两个整数。"],
    ["根本误解", "red", "2. 加流动性要保持 K 不变",
     "<b>正好说反了。</b>按比例 s 加流动性，K 必然变成 K(1+s)²。真正需要保持不变的是<b>比例</b>，因为比例决定价格。"],
    ["几何", "orange", "3. 「V2 均匀分布」= 两种币数量相等",
     "指的是 <b>L = √K 在整条价格轴上处处相同</b>——每个价位能承接的交易深度一样。跟两种币的数量是否相等毫无关系。"],
    ["风险", "red", "4. 组 LP 能保住 ETH 本位的本金",
     "<b>完全不保证。</b>你的 ETH ∝ √P。MEME 跌到 1/10000，你的 ETH 数量变成 1/10，ETH 本位亏 99%。这不是「价值缩水」，是<b>数量真的少了</b>。"],
    ["几何", "", "5. 集中流动性改变了曲线形状",
     "<b>形状没变</b>，还是双曲线，L 扮演的角色和 √K 一样。变的是它<b>被平移了</b>，所以第一象限里只剩一段有限的弧。V2 只是 V3 在 p_a→0、p_b→∞ 时的特例。"],
    ["持仓", "orange", "6. V2 里 LP 两边永远各占 50%",
     "只对 <b>V2 全区间</b>成立。V3 里只有价格恰好在<b>几何均值 √(p_a·p_b)</b> 处才是 50/50；在边界上是 100/0 或 0/100。"],
    ["风险", "red", "7. 出区间只是少赚手续费",
     "出界后仓位<b>冻结</b>，但市场继续走。IL 会持续恶化：主例子 E 里从 −12.5% 一路到 <b>−85.3%</b>。出界不是结束，是痛苦的开始。"],
    ["收益", "orange", "8. 手续费收入 ≈ 费率 × 成交量",
     "在暴涨暴跌的池子里<b>严重高估</b>。手续费以池中两种币收取，其中一种正在贬值。主例子 C 里 1.8 ETH 的手续费崩回原点后只剩 <b>0.258 ETH</b>（−85.7%）。"],
    ["操作", "orange", "9. 出界了重新设个区间就行",
     "每次 rebalance 都是「撤出 + 重新存入」。撤出意味着<b>把浮动亏损变成已实现亏损</b>。价格如果回来了，你已经错过了。"],
    ["架构", "", "10. V4 的曲线设计和 V3 不同",
     "<b>几何完全没变。</b>曲线形状、价格定义、tick 精度、L 的关系、资本效率、IL 公式——七项不变量一模一样。V4 改的是架构和可编程性。"],
    ["安全", "red", "11. Hook 只是「插件」，不会动我的钱",
     "有 delta 权限（bit0–3）的 hook <b>可以参与资金结算</b>，等于池子的共同所有者。而一个在 <code>beforeRemoveLiquidity</code> 里 revert 的 hook <b>可以把你的本金永久锁死</b>。这是设计上允许的，不是漏洞。"],
  ];
  const mHost = document.getElementById("myths");
  if (mHost) mHost.innerHTML = MYTHS.map((r, i) =>
    `<div class="reason${i < 2 ? " top" : ""}"><span class="tag ${r[1]}">${r[0]}</span>` +
    `<b>❌ ${r[2]}</b><p>${r[3]}</p></div>`).join("");

  /* ============================================================
     3) 术语表
     ============================================================ */
  const TERMS = [
    ["AMM", "自动做市商。用公式代替订单簿来定价的交易所。"],
    ["恒定乘积", "x·y=K 的约束。V2 的核心机制。"],
    ["K", "两种币数量的乘积。衡量池子大小，与价格无关。"],
    ["P = y/x", "价格的定义。不是存储在合约里的变量。"],
    ["无常损失 IL", "做 LP 相对「拿住不动」的损失。价格回到原点则归零。"],
    ["滑点", "平均成交价与现货价的差额。"],
    ["价格冲击", "一笔交易完成后现货价的变动幅度。"],
    ["L", "V3 的流动性参数，等于虚拟储备的几何平均。"],
    ["虚拟储备", "V3 里「如果不受区间限制，池子看起来会有多少币」。"],
    ["实际储备", "虚拟储备减去边界处的虚拟储备，即真实锁在合约里的数量。"],
    ["tick", "价格的离散刻度，P(i) = 1.0001^i。"],
    ["tickSpacing", "区间边界允许的最小粒度，按费率档位固定。"],
    ["区间 / range", "V3 仓位提供流动性的价格范围 [p_a, p_b]。"],
    ["出界", "价格走出区间。仓位冻结，不再赚手续费但继续承受风险。"],
    ["资本效率 E", "同样资金相对 V2 提供的深度倍数。"],
    ["集中流动性", "把资金集中在某个价格区间提供流动性。V3 的核心创新。"],
    ["geometric mean", "区间的几何均值 √(p_a·p_b)。仓位在此处恰好 50/50。"],
    ["Singleton", "V4 的单一合约架构，所有池子存在一本合约里。"],
    ["PoolKey", "V4 里唯一标识一个池子的结构体。"],
    ["PoolId", "PoolKey 的哈希，用作 mapping 的键。"],
    ["Flash Accounting", "V4 的延迟结算机制，中间只记 delta。"],
    ["EIP-1153", "瞬态存储。delta 存在这里，交易结束自动清零。"],
    ["delta", "记账差额，表示某地址欠多少或多多少。"],
    ["settle / take", "把 delta 用真实代币结清的两个操作。"],
    ["Hook", "V4 允许在关键执行节点插入的自定义合约。"],
    ["权限位", "hook 地址最低 14 位，编码它有哪些回调权限。"],
    ["CREATE2 挖矿", "不断换盐部署，直到地址低位匹配所需权限。约 2^14 次。"],
    ["Selector", "函数选择器。hook 返回值必须原样回传它。"],
    ["ERC-6909", "V4 的认领凭证标准，允许跳过实际转账。"],
    ["Subscribers", "仓位变化订阅机制，不需要转让 ERC-721。"],
    ["donate", "直接向区间内 LP 捐赠，不改变价格。"],
    ["sync", "同步储备记录，处理直接转账的情况。"],
    ["协议费", "V4 中上限 0.1% 的协议层抽成，方向性、先于 LP 费率。"],
    ["动态费率", "建池时用 0x800000 标记，之后可修改的费率。"],
    ["TWAP", "时间加权平均价格，V3 内置的预言机。"],
    ["JIT 流动性", "在大单成交前后瞬时注入并撤走流动性。"],
    ["Rug Pull", "项目方撤走全部流动性，代币归零。"],
    ["联合曲线", "bonding curve。代币价格随供应量按公式变化，无需 LP。"],
    ["σ (sigma)", "波动率。这里指日对数收益率标准差。"],
    ["δ (delta)", "区间对数半宽。"],
    ["H", "预期持有期，单位天。"],
    ["δ* ≈ σ√H", "最优区间半宽公式。"],
  ];
  const gHost = document.getElementById("glossary");
  if (gHost) gHost.innerHTML = TERMS.map((t) =>
    `<div style="margin:2px 0"><b>${t[0]}</b> — <span class="muted">${t[1]}</span></div>`).join("");

  /* ============================================================
     4) 模拟器 1：AMM 池子
     ============================================================ */
  const S1 = { p0: 0.1, x0: 100, y0: 10, share: 10, r: 1 };
  const q = (id) => document.getElementById(id);

  function ilOf(r) { return (2 * Math.sqrt(r)) / (1 + r) - 1; }

  function updAMM() {
    const K = S1.x0 * S1.y0;
    const x = Math.sqrt(K / S1.p0), y = Math.sqrt(K * S1.p0);
    const P = S1.p0 * S1.r;
    const xNew = Math.sqrt(K / P), yNew = Math.sqrt(K * P);
    const s = S1.share / 100;
    const il = ilOf(S1.r);

    q("v-p0").textContent = S1.p0.toFixed(2);
    q("v-x0").textContent = S1.x0.toLocaleString("en-US") + " A";
    q("v-y0").textContent = S1.y0 + " ETH";
    q("v-share").textContent = S1.share.toFixed(1) + "%";
    q("v-r").textContent = "×" + S1.r.toFixed(2);

    q("amm-stats").innerHTML = [
      ["", "×" + S1.r.toFixed(2), "价格倍数"],
      [il < -0.001 ? "red" : "green", (il * 100).toFixed(2) + "%", "无常损失"],
      ["blue", (s * yNew).toFixed(4), "你的 ETH 数量"],
      ["", (s * xNew).toFixed(2), "你的 A 数量"],
    ].map((a) => `<div class="stat ${a[0]}"><b>${a[1]}</b><span>${a[2]}</span></div>`).join("");

    q("amm-table").innerHTML =
      `<tr><th>量</th><th class="r">初始</th><th class="r">现在</th><th class="r">变化</th></tr>` +
      [["价格 P", S1.p0, P, (S1.r - 1) * 100],
       ["池中 A", x, xNew, (xNew / x - 1) * 100],
       ["池中 ETH", y, yNew, (yNew / y - 1) * 100],
       ["你的 A", s * x, s * xNew, (xNew / x - 1) * 100],
       ["你的 ETH", s * y, s * yNew, (yNew / y - 1) * 100],
       ["持仓价值(ETH)", s * x * S1.p0 + s * y, s * xNew * P + s * yNew,
        ((s * xNew * P + s * yNew) / (s * x * S1.p0 + s * y) - 1) * 100],
      ].map((r) => {
        const d = r[3], cls = Math.abs(d) < 0.01 ? "" : (d > 0 ? "good" : "bad");
        return `<tr class="${cls}"><td>${r[0]}</td><td class="r">${fmt(r[1])}</td>` +
               `<td class="r">${fmt(r[2])}</td><td class="r">${d >= 0 ? "+" : ""}${d.toFixed(1)}%</td></tr>`;
      }).join("");

    // IL 曲线
    const rs = [], data = [];
    for (let i = 0; i <= 60; i++) {
      const e = -2 + (4 * i) / 60, rr = Math.pow(10, e);
      rs.push("×" + (rr < 1 ? rr.toFixed(2) : rr.toFixed(0)));
      data.push(ilOf(rr) * 100);
    }
    const mi = Math.round(((Math.log10(S1.r) + 2) / 4) * 60);
    lineChart("ch-il", rs, [{ name: "无常损失 IL(%)", data, tone: "--c2" }],
      { height: 240, suffix: "%", marker: { i: Math.max(0, Math.min(60, mi)), v: il * 100 } });
  }

  /* ============================================================
     5) 模拟器 2：V3 区间
     ============================================================ */
  const S2 = { delta: 0.1, sigma: 0.03, H: 30 };
  const ASSETS = [
    ["稳定币", { delta: 0.01, sigma: 0.001, H: 30 }],
    ["ETH 30天", { delta: 0.164, sigma: 0.03, H: 30 }],
    ["ETH 7天", { delta: 0.079, sigma: 0.03, H: 7 }],
    ["MEME 1天", { delta: 0.30, sigma: 0.30, H: 1 }],
    ["MEME 7天", { delta: 0.79, sigma: 0.30, H: 7 }],
  ];

  function effOf(d) {                    // d = 区间半宽(相对), 在几何均值处
    const w = (1 + d) / (1 - d);         // p_b/p_a
    const sw = Math.sqrt(w);
    return sw / (sw - 1);
  }

  function updV3() {
    const d = S2.delta, sg = S2.sigma, H = S2.H;
    const E = effOf(Math.min(d, 0.98));
    const life = (d * d) / (sg * sg);    // 天
    const dStar = sg * Math.sqrt(H);

    q("v-delta").textContent = (d * 100).toFixed(1) + "%";
    q("v-sigma").textContent = (sg * 100).toFixed(1) + "%";
    q("v-H").textContent = H + " 天";

    const ok = life >= H;
    q("v3-stats").innerHTML = [
      ["blue", E.toFixed(1) + "×", "资本效率（相对 V2）"],
      [ok ? "green" : "red", life >= 100 ? life.toFixed(0) : life.toFixed(1),
       "期望出界时间（天）"],
      [Math.abs(d - dStar) / dStar < 0.25 ? "green" : "orange",
       (dStar * 100).toFixed(1) + "%", "该持有期的最优半宽 δ*"],
      [ok ? "green" : "red", ok ? "✓ 撑得住" : "✗ 会出界", `${H} 天持有期`],
    ].map((a) => `<div class="stat ${a[0]}"><b>${a[1]}</b><span>${a[2]}</span></div>`).join("");

    const pb = 1 + d, pa = 1 - d;
    q("v3-table").innerHTML =
      `<tr><th>量</th><th class="r">数值</th></tr>` +
      [["价格区间", `[${pa.toFixed(3)}, ${pb.toFixed(3)}]`],
       ["上界相对现价", `+${(d * 100).toFixed(1)}%`],
       ["下界相对现价", `−${(d * 100).toFixed(1)}%`],
       ["最坏情况 IL（到边界）", (ilOf(pb) * 100).toFixed(2) + "%"],
       ["区间寿命 / 持有期", `${(life / H).toFixed(2)}×`],
       ["结论", ok ? "区间足够宽，能撑过持有期"
                   : `需把半宽加到 ${(dStar * 100).toFixed(1)}% 才能撑过 ${H} 天`],
      ].map((r) => `<tr><td>${r[0]}</td><td class="r">${r[1]}</td></tr>`).join("");

    // E 曲线
    const ds = [], ed = [];
    for (let i = 0; i <= 50; i++) {
      const dd = 0.005 + (0.5 * i) / 50;
      ds.push((dd * 100).toFixed(1) + "%");
      ed.push(effOf(dd));
    }
    lineChart("ch-eff", ds, [{ name: "资本效率 E（倍）", data: ed, tone: "--c1" }],
      { height: 220 });
  }

  document.getElementById("asset-presets").innerHTML =
    ASSETS.map((a, i) => `<button data-i="${i}">${a[0]}</button>`).join("");

  /* ============================================================
     6) 模拟器 3：区间寿命
     ============================================================ */
  const S3 = { sigma: 0.3, delta: 0.1, H: 7 };

  function updLife() {
    const sg = S3.sigma, d = S3.delta, H = S3.H;
    const life = (d * d) / (sg * sg);
    const dStar = sg * Math.sqrt(H);

    q("v-sig2").textContent = (sg * 100).toFixed(1) + "%";
    q("v-del2").textContent = (d * 100).toFixed(1) + "%";
    q("v-H2").textContent = H + " 天";

    const ok = life >= H;
    q("life-stats").innerHTML = [
      [ok ? "green" : "red", life >= 100 ? life.toFixed(0) + " 天" : life.toFixed(1) + " 小时",
       ok ? "期望出界时间" : "期望出界时间（小时）"],
      ["", dStar.toFixed(4), "该持有期最优半宽"],
      [ok ? "green" : "red", ok ? "✓ 可以" : "✗ 不行", "能否撑过持有期"],
    ].map((a) => `<div class="stat ${a[0]}"><b>${a[1]}</b><span>${a[2]}</span></div>`).join("");

    // 寿命 vs 半宽
    const ds = [], ld = [];
    for (let i = 0; i <= 50; i++) {
      const dd = 0.005 + (1.95 * i) / 50;
      ds.push((dd * 100).toFixed(0) + "%");
      ld.push(Math.max(0.05, (dd * dd) / (sg * sg)));
    }
    lineChart("ch-life", ds, [{ name: "期望出界时间（天）", data: ld, tone: "--c1" }],
      { height: 230, hlines: [{ v: H, name: `目标 ${H} 天`, tone: "--c2" }] });

    const advice = ok
      ? `<b class="t">✓ 这个组合可行</b>半宽 ${(d * 100).toFixed(1)}% 的区间期望能撑 ${life.toFixed(1)} 天，` +
        `超过你打算持有的 ${H} 天。<b>资本效率约 ${effOf(Math.min(d, 0.98)).toFixed(1)} 倍。</b>`
      : `<b class="t">✗ 这个组合撑不住</b>半宽 ${(d * 100).toFixed(1)}% 的区间期望只能活 ` +
        `${(life * 24).toFixed(1)} 小时，而你打算持有 ${H} 天。` +
        `<b>要把半宽加到 ${(dStar * 100).toFixed(1)}% 才行</b>——` +
        `代价是资本效率从 ${effOf(Math.min(d, 0.98)).toFixed(1)} 倍降到 ${effOf(Math.min(dStar, 0.98)).toFixed(1)} 倍。`;
    const aHost = q("life-advice");
    aHost.className = "callout " + (ok ? "good" : "bad");
    aHost.innerHTML = advice;
  }

  /* ============================================================
     7) 绑定
     ============================================================ */
  const BIND = [
    ["in-p0", "p0", "v-p0", updAMM], ["in-x0", "x0", "v-x0", updAMM],
    ["in-y0", "y0", "v-y0", updAMM], ["in-share", "share", "v-share", updAMM],
    ["in-delta", "delta", "v-delta", updV3], ["in-sigma", "sigma", "v-sigma", updV3],
    ["in-H", "H", "v-H", updV3],
    ["in-sig2", "sigma", "v-sig2", updLife], ["in-del2", "delta", "v-del2", updLife],
    ["in-H2", "H", "v-H2", updLife],
  ];
  BIND.forEach(([id, key, , fn]) => {
    const e = q(id); if (!e) return;
    e.addEventListener("input", () => {
      const v = Number(e.value);
      if (id === "in-r") { S1.r = Math.pow(10, v); updAMM(); return; }
      if (id === "in-sig2") S3.sigma = v;
      else if (id === "in-del2") S3.delta = v;
      else if (id === "in-H2") S3.H = v;
      else if (id === "in-delta") S2.delta = v;
      else if (id === "in-sigma") S2.sigma = v;
      else if (id === "in-H") S2.H = v;
      else S1[key] = v;
      fn();
    });
  });
  const rEl = q("in-r");
  if (rEl) rEl.addEventListener("input", () => { S1.r = Math.pow(10, Number(rEl.value)); updAMM(); });

  document.querySelectorAll("#asset-presets button").forEach((b) => {
    b.addEventListener("click", () => {
      const a = ASSETS[+b.dataset.i][1];
      S2.delta = a.delta; S2.sigma = a.sigma; S2.H = a.H;
      q("in-delta").value = a.delta; q("in-sigma").value = a.sigma; q("in-H").value = a.H;
      document.querySelectorAll("#asset-presets button").forEach((x) => x.classList.remove("on"));
      b.classList.add("on");
      updV3();
    });
  });

  /* 初次渲染 */
  updAMM(); updV3(); updLife();

  /* 图表容器变化时重绘（主题切换） */
  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => {
    updAMM(); updV3(); updLife();
  });
})();
