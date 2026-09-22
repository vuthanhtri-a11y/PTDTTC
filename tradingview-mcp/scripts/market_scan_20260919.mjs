import fs from 'node:fs';
const out = 'analysis-20260919';
fs.mkdirSync(out,{recursive:true});
if(process.argv.includes('--bench')) {
 for(const symbol of ['VNINDEX','HNXINDEX','UPCOMINDEX']){
  const url=`https://services.entrade.com.vn/chart-api/v2/ohlcs/index?from=${Math.floor(Date.parse('2025-01-01')/1000)}&to=${Math.floor(Date.parse('2026-09-19')/1000)}&symbol=${symbol}&resolution=1D`;
  try{const r=await fetch(url,{signal:AbortSignal.timeout(20000)});const d=await r.json();fs.writeFileSync(`${out}/${symbol}.json`,JSON.stringify(d));console.log(symbol,r.status,d.t?.length,d.c?.slice(-2));}catch(e){console.log(symbol,e.message);}
 }process.exit(0);
}
if(process.argv.includes('--history')) {
 const tv=JSON.parse(fs.readFileSync(`${out}/universe.json`)).rows;
 const vci=JSON.parse(fs.readFileSync(`${out}/vci-symbols.json`));
 const syms=new Map(vci.filter(x=>x.type==='STOCK'&&['HSX','HNX','UPCOM'].includes(x.board)).map(x=>[x.symbol,{name:x.symbol,exchange:x.board==='HSX'?'HOSE':x.board,description:x.organName}]));
 for(const r of tv)if(r.type==='stock'&&!syms.has(r.name))syms.set(r.name,{name:r.name,exchange:r.exchange,description:r.description});
 const items=[...syms.values()];fs.mkdirSync(`${out}/history`,{recursive:true});
 fs.writeFileSync(`${out}/coverage.json`,JSON.stringify({source:'Vietcap symbols/getAll + TradingView Vietnam scanner',total:items.length,counts:items.reduce((a,r)=>(a[r.exchange]=(a[r.exchange]||0)+1,a),{}),items},null,2));
 let index=0,ok=0,empty=0,failed=0;
 const from=Math.floor(Date.parse('2025-01-01')/1000),to=Math.floor(Date.parse('2026-09-19')/1000);
 async function worker(){while(index<items.length){const item=items[index++],p=`${out}/history/${item.name}.json`;if(fs.existsSync(p)){ok++;continue;}
  try{const url=`https://services.entrade.com.vn/chart-api/v2/ohlcs/stock?from=${from}&to=${to}&symbol=${encodeURIComponent(item.name)}&resolution=1D`;const r=await fetch(url,{signal:AbortSignal.timeout(20000)});if(!r.ok)throw new Error(`HTTP ${r.status}`);const d=await r.json();fs.writeFileSync(p,JSON.stringify(d));if(d.t?.length)ok++;else empty++;}catch(e){failed++;fs.appendFileSync(`${out}/history-errors.jsonl`,JSON.stringify({symbol:item.name,error:e.message})+'\n');}
  if((ok+empty+failed)%100===0)console.log(JSON.stringify({done:ok+empty+failed,total:items.length,ok,empty,failed}));await new Promise(r=>setTimeout(r,200));}}
 await Promise.all(Array.from({length:4},()=>worker()));console.log(JSON.stringify({done:items.length,ok,empty,failed}));process.exit(0);
}
if(process.argv.includes('--audit')) {
 for(const [name,url] of Object.entries({vci:'https://trading.vietcap.com.vn/api/price/symbols/getAll',dnse:'https://services.entrade.com.vn/chart-api/v2/symbols'})) {
  try{const r=await fetch(url,{signal:AbortSignal.timeout(30000)});const t=await r.text();fs.writeFileSync(`${out}/${name}-symbols.json`,t);console.log(name,r.status,t.slice(0,600));}catch(e){console.log(name,e.message);}
 }
 process.exit(0);
}
const columns=['name','description','exchange','type','close','open','high','low','volume','change','average_volume_10d_calc','average_volume_30d_calc','relative_volume_10d_calc','Value.Traded','market_cap_basic','price_earnings_ttm','price_book_fq','earnings_per_share_diluted_ttm','earnings_per_share_growth_ttm','return_on_equity','SMA20','SMA50','SMA200','EMA20','RSI','RSI[1]','MACD.macd','MACD.signal','ADX','ADX+DI','ADX-DI','ATR','Perf.W','Perf.1M','Perf.3M','Perf.6M','price_52_week_high','price_52_week_low','update_mode','time','last_bar_update'];
async function scan(cols) {
 const r=await fetch('https://scanner.tradingview.com/vietnam/scan',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({columns:cols,range:[0,5000] }),signal:AbortSignal.timeout(40000)});
 const txt=await r.text(); if(!r.ok) throw new Error(txt); return JSON.parse(txt);
}
let cols=[...columns], data;
for(let i=0;i<10;i++) {try{data=await scan(cols);break;}catch(e){const m=e.message.match(/Unknown field \"([^\"]+)\"/);if(!m)throw e;console.log('Unsupported',m[1]);cols=cols.filter(c=>c!==m[1]);}}
if(!data)throw new Error('No scan data');
const rows=data.data.map(r=>({symbol:r.s,...Object.fromEntries(cols.map((c,i)=>[c,r.d[i]]))}));
fs.writeFileSync(`${out}/universe.json`,JSON.stringify({retrieved_at:new Date().toISOString(),source:'https://scanner.tradingview.com/vietnam/scan',totalCount:data.totalCount,columns:cols,rows},null,2));
console.log(JSON.stringify({total:data.totalCount,counts:rows.reduce((a,r)=>(a[r.exchange]=(a[r.exchange]||0)+1,a),{}),sample:rows.slice(0,2)},null,2));
const from=Math.floor(Date.parse('2025-01-01')/1000),to=Math.floor(Date.parse('2026-09-19')/1000);
const url=`https://services.entrade.com.vn/chart-api/v2/ohlcs/stock?from=${from}&to=${to}&symbol=HPG&resolution=1D`;
try{const r=await fetch(url,{signal:AbortSignal.timeout(30000)});const text=await r.text();fs.writeFileSync(`${out}/history-probe.json`,text);console.log('History',r.status,text.slice(0,250),text.slice(-250));}catch(e){console.log('History error',e.message);}
