import fs from 'node:fs';
import vm from 'node:vm';

const dir = 'exports/run_20260919';
const iso = t => new Date(t * 1000).toISOString().slice(0, 10);
const daily = JSON.parse(fs.readFileSync(`${dir}/daily.json`, 'utf8'));
const dates = Object.fromEntries(Object.entries(daily.raw).map(([s, b]) => [s, iso(b.at(-1)[0])]));
const latest = dates.VNINDEX;
const stale = Object.entries(dates).filter(([, d]) => d !== latest);
const short = Object.entries(daily.raw).filter(([, b]) => b.length < 253).map(([s, b]) => [s, b.length]);
if (daily.errs.length || stale.length || short.length) throw new Error(JSON.stringify({ errors: daily.errs, stale, short }));
for (const [s, bars] of Object.entries(daily.raw)) {
  if (bars.some(b => b.length < 6 || !b.slice(0, 6).every(Number.isFinite) || b[4] <= 0)) throw new Error(`Invalid bars: ${s}`);
  if (bars.some((b, i) => i && b[0] <= bars[i-1][0])) throw new Error(`Unordered dates: ${s}`);
}
const scan = { _meta: { source: 'TradingView Desktop HOSE_DLY', fetched_on: '2026-09-19', market_date: latest, count: Object.keys(daily.res).length - 1, warning: daily.warn }, ...daily.res };
const scanPath = `data/scan_${latest.replaceAll('-', '')}.json`;
if (fs.existsSync(scanPath) && fs.readFileSync(scanPath, 'utf8') !== JSON.stringify(scan)) throw new Error(`Refusing overwrite: ${scanPath}`);
if (!fs.existsSync(scanPath)) fs.writeFileSync(scanPath, JSON.stringify(scan));
fs.writeFileSync(`${dir}/validation.json`, JSON.stringify({ latest, stale, short, dates, bars_min:daily.bars_min,bars_max:daily.bars_max }, null, 2));
console.log(JSON.stringify({ scanPath, latest, count: scan._meta.count, bars_min:daily.bars_min,bars_max:daily.bars_max }));

if (!fs.existsSync(`${dir}/weekly.json`)) { console.log('Weekly scan still pending'); process.exit(0); }
const weekly = JSON.parse(fs.readFileSync(`${dir}/weekly.json`, 'utf8'));
const source = fs.readFileSync('lt_backtest_scope.js', 'utf8');
const output = { _meta: { run_date:'2026-09-19', daily_market_date:latest, source:'lt_backtest_scope.js', note:'Technical proxy only; fixed current universe, weekly closes sampled every four weeks, no historical fundamental/valuation vetoes or discretionary rule 5. Original engine annualizes at 12 periods/year; date-adjusted CAGR is added separately.' }, phases:[] };
for (let phase = 0; phase < 4; phase++) {
  const b = weekly.raw.VNINDEX.slice(-300);
  const indices = [];
  for (let i = b.length - 1 - phase; i >= 0; i -= 4) indices.unshift(i);
  const timeline = indices.map(i => b[i][0]);
  if (timeline.length <= 23) throw new Error('Insufficient weekly history');
  const res = {}, warmupFills = [];
  for (const [symbol, bars] of Object.entries(weekly.raw)) {
    const prices = new Map(bars.map(row => [row[0], row[4]]));
    res[symbol] = { c: timeline.map((t, i) => {
      if (prices.has(t)) return prices.get(t);
      const prior = bars.findLast(row => row[0] < t);
      if (!prior) return null; // Not yet listed: never invent pre-listing history.
      if (i >= 22) throw new Error(`Missing trading-period weekly point: ${symbol} ${iso(t)}`);
      warmupFills.push({ symbol, week:iso(t), prior_week:iso(prior[0]), close:prior[4] });
      return prior[4]; // Warm-up only, past observed price; no future information.
    }) };
  }
  const results = JSON.parse(vm.runInNewContext(source, { window: { __W: { res, G:timeline.length } } }));
  const t0 = results._meta.t0, t1 = results._meta.t1;
  const years = (timeline[t1] - timeline[t0]) / (365.25*86400);
  for (const value of Object.values(results)) {
    if (value && typeof value === 'object' && typeof value.cagr === 'number') {
      value.cagr_calendar = (1 + value.cagr) ** ((t1-t0)/12/years) - 1;
    }
  }
  const prices = res.VNINDEX.c.slice(t0,t1+1);
  let peak = prices[0], dd = 0;
  for (const p of prices) { peak = Math.max(peak,p); dd = Math.min(dd,p/peak-1); }
  results.VNINDEX.mdd = dd;
  output.phases.push({ phase, start:iso(timeline[t0]), end_week:iso(timeline[t1]), years, warmupFills, results });
}
fs.writeFileSync(`${dir}/backtest.json`, JSON.stringify(output,null,2));
console.log(JSON.stringify(output.phases.map(p=>({phase:p.phase,start:p.start,end_week:p.end_week,B2:p.results.CL_B2,VNINDEX:p.results.VNINDEX}))));
