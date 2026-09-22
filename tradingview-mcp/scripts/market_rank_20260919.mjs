// Rank VN stocks (HOSE/HNX/UPCOM) for a new buy on the next session.
// Replicates the user's chart indicators: Two-Pole Oscillator [BigBeluga] (len 15)
// and an approximation of Volumatic Fair Value Gaps [BigBeluga], plus classic TA + fundamentals.
import fs from 'node:fs';
const root = 'analysis-20260919';
const LAST = '2026-09-18';
const coverage = JSON.parse(fs.readFileSync(`${root}/coverage.json`));
const tv = new Map(JSON.parse(fs.readFileSync(`${root}/universe.json`)).rows.map(x => [x.name, x]));

const mean = a => a.reduce((s, x) => s + x, 0) / a.length;
const last = a => a.at(-1);
const r2 = (x, d = 2) => (Number.isFinite(x) ? (d < 0 ? Math.round(x / 10 ** -d) * 10 ** -d : Number(x.toFixed(d))) : null);
const sma = (a, n) => a.map((_, i) => (i < n - 1 ? null : mean(a.slice(i - n + 1, i + 1))));
const stdev = (a, n) => a.map((_, i) => { if (i < n - 1) return null; const w = a.slice(i - n + 1, i + 1), m = mean(w); return Math.sqrt(mean(w.map(x => (x - m) ** 2))); });
const ema = (a, n) => { const k = 2 / (n + 1); return a.reduce((o, x, i) => (o.push(i ? x * k + last(o) * (1 - k) : x), o), []); };
const rma = (a, n) => { const o = []; let m = mean(a.slice(0, n)); for (let i = 0; i < a.length; i++) { if (i < n - 1) o.push(null); else if (i === n - 1) o.push(m); else { m = (m * (n - 1) + a[i]) / n; o.push(m); } } return o; };

function twoPole(c, len = 15) {
  const s1 = sma(c, 25), d = c.map((x, i) => (s1[i] == null ? null : x - s1[i]));
  const valid = d.map(x => x != null), first = valid.indexOf(true), dd = d.slice(first);
  const m = sma(dd, 25), sd = stdev(dd, 25);
  const n1 = dd.map((x, i) => (m[i] == null || !sd[i] ? null : (x - m[i]) / sd[i]));
  const alpha = 2 / (len + 1); let a = null, b = null; const out = Array(first).fill(null);
  for (const x of n1) { if (x == null) { out.push(null); continue; } a = a == null ? x : (1 - alpha) * a + alpha * x; b = b == null ? a : (1 - alpha) * b + alpha * a; out.push(b); }
  return out;
}

// Bullish/bearish FVGs over the last 60 bars; a zone is mitigated once a close crosses through it.
function fvgs(o, h, l, c, v, atr) {
  const n = c.length, bull = [], bear = [];
  for (let i = Math.max(2, n - 60); i < n; i++) {
    const thr = 0.1 * (atr[i] ?? 0);
    if (l[i] > h[i - 2] && c[i - 1] > h[i - 2] && l[i] - h[i - 2] > thr) {
      let alive = true; for (let j = i + 1; j < n; j++) if (c[j] < h[i - 2]) { alive = false; break; }
      const bv = [i - 2, i - 1, i].reduce((s, j) => s + (c[j] >= o[j] ? v[j] : 0), 0), tv3 = v[i - 2] + v[i - 1] + v[i];
      if (alive) bull.push({ top: l[i], bot: h[i - 2], age: n - 1 - i, buyPct: tv3 ? (bv / tv3) * 100 : 50 });
    }
    if (h[i] < l[i - 2] && c[i - 1] < l[i - 2] && l[i - 2] - h[i] > thr) {
      let alive = true; for (let j = i + 1; j < n; j++) if (c[j] > l[i - 2]) { alive = false; break; }
      if (alive) bear.push({ top: l[i - 2], bot: h[i], age: n - 1 - i });
    }
  }
  return { bull, bear };
}

const rows = [];
for (const s of coverage.items) {
  const p = `${root}/history/${s.name}.json`;
  if (!fs.existsSync(p)) continue;
  const b = JSON.parse(fs.readFileSync(p));
  if (!b.t?.length || b.t.length < 130) continue;
  const date = new Date(last(b.t) * 1000).toISOString().slice(0, 10);
  if (date !== LAST) continue;
  const K = 1000, o = b.o.map(x => x * K), h = b.h.map(x => x * K), l = b.l.map(x => x * K), c = b.c.map(x => x * K), v = b.v, n = c.length, price = last(c);
  if (![o, h, l, c, v].every(a => a.length === n && a.every(Number.isFinite))) continue;
  const tr = c.map((_, i) => (i ? Math.max(h[i] - l[i], Math.abs(h[i] - c[i - 1]), Math.abs(l[i] - c[i - 1])) : h[i] - l[i]));
  const atrA = rma(tr, 14), atr = last(atrA), atrpct = (atr / price) * 100;
  const ma = k => mean(c.slice(-Math.min(k, n))), ma20 = ma(20), ma50 = ma(50), ma200 = ma(200), ma50prev = mean(c.slice(-60, -10));
  const ret = k => (price / c[n - 1 - k] - 1) * 100;
  const diff = c.slice(1).map((x, i) => x - c[i]), g = rma(diff.map(x => Math.max(x, 0)), 14), ls = rma(diff.map(x => Math.max(-x, 0)), 14);
  const rsiAt = i => (ls[i] === 0 ? 100 : 100 - 100 / (1 + g[i] / ls[i])), rsi = rsiAt(g.length - 1), rsiPrev = rsiAt(g.length - 4);
  const e12 = ema(c, 12), e26 = ema(c, 26), mac = e12.map((x, i) => x - e26[i]), sig = ema(mac, 9), hist = mac.map((x, i) => x - sig[i]);
  const plus = h.map((x, i) => (i && x - h[i - 1] > l[i - 1] - l[i] ? Math.max(x - h[i - 1], 0) : 0)), minus = l.map((x, i) => (i && l[i - 1] - x > h[i] - h[i - 1] ? Math.max(l[i - 1] - x, 0) : 0));
  const ar = rma(tr.slice(1), 14), pr = rma(plus.slice(1), 14), mr = rma(minus.slice(1), 14), dx = []; let pdi = 0, mdi = 0;
  for (let i = 13; i < ar.length; i++) { pdi = ar[i] ? (100 * pr[i]) / ar[i] : 0; mdi = ar[i] ? (100 * mr[i]) / ar[i] : 0; dx.push(pdi + mdi ? (100 * Math.abs(pdi - mdi)) / (pdi + mdi) : 0); }
  const adx = last(rma(dx, 14));
  const turnover20 = mean(c.slice(-20).map((x, i) => x * v[n - 20 + i])) / 1e9, vol20 = mean(v.slice(-20)), rv = last(v) / mean(v.slice(-21, -1));
  const cmf = c.slice(-20).reduce((a, x, i) => { const j = n - 20 + i; return a + (h[j] === l[j] ? 0 : ((2 * x - h[j] - l[j]) / (h[j] - l[j])) * v[j]); }, 0) / v.slice(-20).reduce((a, x) => a + x, 0);
  // Up-volume vs down-volume over 10 sessions (accumulation)
  const upv = v.slice(-10).reduce((a, x, i) => a + (c[n - 10 + i] > c[n - 11 + i] ? x : 0), 0), dnv = v.slice(-10).reduce((a, x, i) => a + (c[n - 10 + i] < c[n - 11 + i] ? x : 0), 0);
  const tp = twoPole(c), tpv = last(tp), tp4 = tp.at(-5), tpPrev = tp.at(-2), tpPrev4 = tp.at(-6);
  let tpBuyAgo = null; for (let k = 0; k < 10; k++) { const i = n - 1 - k; if (tp[i] != null && tp[i - 4] != null && tp[i - 1] != null && tp[i - 5] != null && tp[i] > tp[i - 4] && tp[i - 1] <= tp[i - 5] && tp[i] < 0) { tpBuyAgo = k; break; } }
  const tpUp = tpv > tp4;
  const { bull, bear } = fvgs(o, h, l, c, v, atrA);
  const supp = bull.filter(z => z.bot <= price).sort((a, b) => b.top - a.top)[0] || null;
  const res = bear.filter(z => z.bot >= price).sort((a, b) => a.bot - b.bot)[0] || null;
  const inBullZone = supp && price <= supp.top * 1.03;
  const high63 = Math.max(...h.slice(-63)), high250 = Math.max(...h.slice(-250)), low20 = Math.min(...l.slice(-20)), low10 = Math.min(...l.slice(-10));
  const dist20 = (price / ma20 - 1) * 100, dist50 = (price / ma50 - 1) * 100, fromHigh63 = (price / high63 - 1) * 100;
  const chgLast = (price / c[n - 2] - 1) * 100;
  const limit = s.exchange === 'HOSE' ? 7 : s.exchange === 'HNX' ? 10 : 15;
  const t = tv.get(s.name) || {}, pe = t.price_earnings_ttm ?? null, pb = t.price_book_fq ?? null, roe = t.return_on_equity ?? null, eps = t.earnings_per_share_diluted_ttm ?? null, epsG = t.earnings_per_share_growth_ttm ?? null, mcap = t.market_cap_basic ?? null;

  const minTurn = s.exchange === 'HOSE' ? 10 : 1.5;
  const fail = [];
  if (turnover20 < minTurn) fail.push('liquidity');
  if (vol20 < 100000) fail.push('volume');
  if (price < 5000) fail.push('penny');
  if (!(price > ma50 && ma20 > ma50)) fail.push('trend');
  if (n >= 200 && price < ma200) fail.push('below_ma200');
  if (rsi < 48 || rsi > 72) fail.push('rsi');
  if (atrpct > 5.5) fail.push('volatile');
  if (dist20 > 8 || dist50 > 18) fail.push('extended');
  if (chgLast >= limit - 0.6) fail.push('limit_up_friday');
  if (eps != null && eps <= 0) fail.push('loss');
  if (!(tpUp || tpBuyAgo != null)) fail.push('twopole_down');
  if (tpv > 1.2) fail.push('twopole_overbought');

  // Scores
  const sTrend = (price > ma20 ? 4 : 0) + (ma20 > ma50 ? 4 : 0) + (n >= 200 && ma50 > ma200 ? 4 : 0) + (ma50 > ma50prev ? 4 : 0) + (adx >= 20 && pdi > mdi ? 4 : pdi > mdi ? 2 : 0);
  const sMom = Math.min(8, Math.max(0, ret(63) / 3)) + (rsi >= 52 && rsi <= 66 ? 6 : 3) + (rsi > rsiPrev ? 2 : 0) + (last(hist) > 0 ? 3 : 0) + (last(hist) > hist.at(-2) ? 3 : 0);
  // Two-Pole: best when turning up from low/neutral territory
  const sTP = (tpBuyAgo != null ? 8 : 0) + (tpUp ? 5 : 0) + (tpv < 0 ? 4 : tpv < 0.5 ? 3 : tpv < 0.9 ? 1 : 0) + (tpv > tpPrev ? 3 : 0);
  // FVG: holding above a fresh bullish FVG, with no bearish FVG just overhead
  const sFVG = (supp ? 4 : 0) + (inBullZone ? 4 : 0) + (supp && supp.buyPct >= 60 ? 2 : 0) + (res && (res.bot / price - 1) * 100 < 5 ? -4 : 0);
  const sVol = (cmf > 0.05 ? 5 : cmf > 0 ? 3 : 0) + (upv > dnv * 1.2 ? 4 : upv > dnv ? 2 : 0) + (rv >= 1.1 && rv <= 3 ? 3 : 0) + Math.min(6, Math.max(0, Math.log10(Math.max(turnover20, 0.01)) * 3));
  const sRisk = Math.max(0, 8 - atrpct * 1.5) + (dist20 >= -1 && dist20 <= 4 ? 4 : dist20 <= 6 ? 2 : 0) + (fromHigh63 > -8 ? 3 : 0);
  const sFund = (eps > 0 ? 3 : 0) + (pe > 0 && pe < 12 ? 5 : pe > 0 && pe < 20 ? 3 : 0) + (roe >= 15 ? 5 : roe >= 10 ? 3 : 0) + (epsG > 0 ? 3 : 0) + (pb > 0 && pb < 2.5 ? 2 : 0);
  const score = sTrend + sMom + sTP + sFVG + sVol + sRisk + sFund;

  // Trade plan
  const stopBase = Math.max(supp ? supp.bot : 0, low10, ma20 * 0.97);
  const stop = Math.min(stopBase, price - 1.2 * atr) > price * 0.9 ? Math.min(stopBase, price - 1.2 * atr) : price * 0.93;
  const target = Math.max(price + 2.5 * (price - stop), high63 > price * 1.03 ? high63 : 0);
  rows.push({
    name: s.name, exchange: s.exchange, desc: t.description || s.description, n, price, chgLast: r2(chgLast), ma20: r2(ma20, 0), ma50: r2(ma50, 0), ma200: n >= 200 ? r2(ma200, 0) : null,
    rsi: r2(rsi, 1), macdHist: r2(last(hist), 1), adx: r2(adx, 1), pdi: r2(pdi, 1), mdi: r2(mdi, 1), atrpct: r2(atrpct), ret21: r2(ret(21)), ret63: r2(ret(63)), dist20: r2(dist20), fromHigh63: r2(fromHigh63),
    turnover20: r2(turnover20), rv: r2(rv), cmf: r2(cmf, 3), upDn: r2(dnv ? upv / dnv : 9),
    tp: r2(tpv, 3), tp4: r2(tp4, 3), tpUp, tpBuyAgo, fvgSupp: supp && { top: r2(supp.top, 0), bot: r2(supp.bot, 0), age: supp.age, buyPct: r2(supp.buyPct, 0) }, fvgRes: res && { bot: r2(res.bot, 0), top: r2(res.top, 0) },
    pe: r2(pe, 1), pb: r2(pb, 2), roe: r2(roe, 1), epsG: r2(epsG, 1), mcapBn: mcap ? r2(mcap / 1e9, 0) : null,
    scores: { trend: r2(sTrend, 1), mom: r2(sMom, 1), tp: sTP, fvg: sFVG, vol: r2(sVol, 1), risk: r2(sRisk, 1), fund: sFund }, score: r2(score, 1),
    plan: { buy: `${r2(Math.max(price - 0.5 * atr, ma20), -1)}-${r2(price * 1.01, -1)}`, stop: r2(stop, -1), target: r2(target, -1) }, fail,
  });
}
fs.writeFileSync(`${root}/ranked.json`, JSON.stringify(rows, null, 1));
const stats = { total: rows.length, pass: rows.filter(r => !r.fail.length).length, byEx: {} };
for (const ex of ['HOSE', 'HNX', 'UPCOM']) stats.byEx[ex] = { total: rows.filter(r => r.exchange === ex).length, pass: rows.filter(r => r.exchange === ex && !r.fail.length).length };
console.log(JSON.stringify(stats));
for (const ex of ['HOSE', 'HNX', 'UPCOM']) {
  console.log(`\n== ${ex}`);
  for (const r of rows.filter(r => r.exchange === ex && !r.fail.length).sort((a, b) => b.score - a.score).slice(0, 12))
    console.log(JSON.stringify({ n: r.name, p: r.price, sc: r.score, s: r.scores, rsi: r.rsi, tp: r.tp, tpB: r.tpBuyAgo, adx: r.adx, atr: r.atrpct, d20: r.dist20, r63: r.ret63, t20: r.turnover20, cmf: r.cmf, fvg: r.fvgSupp, res: r.fvgRes, pe: r.pe, roe: r.roe }));
}
