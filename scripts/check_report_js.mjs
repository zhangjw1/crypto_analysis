import { readFileSync } from "node:fs";

const file = process.argv[2];
const html = readFileSync(file, "utf8");
const js = html.slice(html.lastIndexOf("<script>") + 8, html.lastIndexOf("</script>"));
const ids = [...html.matchAll(/id="([^"]+)"/g)].map((m) => m[1]);

let nodes = 0;
function mk(tag) {
  nodes++;
  return { tag, children: [], attrs: {}, _html: "", setAttribute(k, v) { if (typeof v === "number" && !Number.isFinite(v)) throw new Error(`non-finite ${k} on ${tag}`); this.attrs[k] = v; }, appendChild(c) { this.children.push(c); return c; }, insertAdjacentHTML() {}, addEventListener() {}, set innerHTML(v) { this._html = v; }, get innerHTML() { return this._html; }, set textContent(v) { this._t = v; }, set className(v) {}, dataset: {} };
}
const els = {};
global.document = {
  documentElement: {},
  getElementById(id) { if (!ids.includes(id) && !/^(in|v)-/.test(id)) throw new Error("missing id " + id); return (els[id] ||= mk("div")); },
  createElementNS: (_, t) => mk(t),
  createElement: (t) => mk(t),
  querySelectorAll: () => [],
};
global.getComputedStyle = () => ({ getPropertyValue: () => "#000" });
new Function(js)();
const nan = Object.entries(els).filter(([, e]) => /NaN|undefined|Infinity/.test(e._html));
console.log("OK, svg nodes:", nodes, "elements touched:", Object.keys(els).length, nan.length ? "BAD html in " + nan.map((x) => x[0]) : "no NaN in innerHTML");
console.log("simstats:", els.simstats._html.replace(/<[^>]+>/g, " ").replace(/\s+/g, " "));
