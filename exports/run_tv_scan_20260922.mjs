import fs from 'node:fs';
import { evaluate, getClient } from '../tradingview-mcp/src/connection.js';
import { setTimeframe } from '../tradingview-mcp/src/core/chart.js';

const out = 'exports/run_20260922';
fs.mkdirSync(out, { recursive: true });
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
const original = await evaluate('({symbol:TradingViewApi.activeChart().symbol(), resolution:TradingViewApi.activeChart().resolution()})');
fs.writeFileSync(`${out}/chart_original.json`, JSON.stringify(original, null, 2));
let source = fs.readFileSync('lt_scan_tradingview.js', 'utf8');
// Preserve the production scanner's calculations and record dated raw bars for audit.
source = source.replace('window.__S.res[U[i]] = metrics(b);',
  'window.__S.res[U[i]] = metrics(b); window.__S.raw[U[i]] = b;');
source = source.replace('syms: U, warn:', 'raw: {}, syms: U, warn:');

try {
  for (const [name, timeframe] of [['daily', '1D']]) {
    await setTimeframe({ timeframe });
    await sleep(2000);
    console.log(name, await evaluate(source));
    for (let poll = 0; poll < 160; poll++) {
      await sleep(10000);
      const state = await evaluate('({i:window.__S.i,n:window.__S.n,cur:window.__S.cur,done:window.__S.done,ok:Object.keys(window.__S.res).length,errs:window.__S.errs,warn:window.__S.warn})');
      console.log(JSON.stringify({ phase: name, ...state }));
      if (state.done) {
        const result = await evaluate('window.__S');
        fs.writeFileSync(`${out}/${name}.json`, JSON.stringify(result));
        if (!result.res.VNINDEX || result.errs.length) {
          throw new Error(`${name}: incomplete scan; inspect saved results`);
        }
        break;
      }
      if (poll === 159) throw new Error(`${name}: scan timeout`);
    }
  }
} finally {
  await evaluate(`TradingViewApi.activeChart().setSymbol(${JSON.stringify(original.symbol)})`);
  await setTimeframe({ timeframe: original.resolution });
  await (await getClient()).close();
}
