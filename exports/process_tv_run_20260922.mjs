import fs from 'node:fs';
import vm from 'node:vm';

const dir = 'exports/run_20260922';
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
const scan = { _meta: { source: 'TradingView Desktop HOSE_DLY', fetched_on: '2026-09-22', market_date: latest, count: Object.keys(daily.res).length - 1, warning: daily.warn }, ...daily.res };
const scanPath = `data/scan_${latest.replaceAll('-', '')}.json`;
if (fs.existsSync(scanPath) && fs.readFileSync(scanPath, 'utf8') !== JSON.stringify(scan)) throw new Error(`Refusing overwrite: ${scanPath}`);
if (!fs.existsSync(scanPath)) fs.writeFileSync(scanPath, JSON.stringify(scan));
fs.writeFileSync(`${dir}/validation.json`, JSON.stringify({ latest, stale, short, dates, bars_min:daily.bars_min,bars_max:daily.bars_max }, null, 2));
console.log(JSON.stringify({ scanPath, latest, count: scan._meta.count, bars_min:daily.bars_min,bars_max:daily.bars_max }));

if (!fs.existsSync(`${dir}/weekly.json`)) { console.log('Weekly scan still pending'); process.exit(0); }
const weekly = JSON.parse(fs.readFileSync(`${dir}/weekly.json`, 'utf8'));
