import fs from 'node:fs';
const root='analysis-20260919';
const coverage=JSON.parse(fs.readFileSync(`${root}/coverage.json`));
const tv=new Map(JSON.parse(fs.readFileSync(`${root}/universe.json`)).rows.map(x=>[x.name,x]));
const mean=a=>a.reduce((s,x)=>s+x,0)/a.length;
const last=a=>a.at(-1);
const round=(x,d=2)=>Number.isFinite(x)?Number(x.toFixed(d)):null;
const ema=(a,n)=>{const k=2/(n+1);return a.reduce((out,x,i)=>(out.push(i?x*k+last(out)*(1-k):x),out),[]);};
const rma=(a,n)=>{const out=[];let m=mean(a.slice(0,n));for(let i=0;i<a.length;i++){if(i<n-1)out.push(null);else if(i===n-1)out.push(m);else{m=(m*(n-1)+a[i])/n;out.push(m);}}return out;};
const rows=[];
for(const s of coverage.items){const p=`${root}/history/${s.name}.json`;if(!fs.existsSync(p)){rows.push({...s,error:'fetch_failed'});continue;}const b=JSON.parse(fs.readFileSync(p));
 if(!b.t?.length){rows.push({...s,error:'empty_history'});continue;}
 const v=b.v,c=b.c.map(x=>x*1000),h=b.h.map(x=>x*1000),l=b.l.map(x=>x*1000),n=c.length,price=last(c),date=new Date(last(b.t)*1000).toISOString().slice(0,10);
 if(n<201){rows.push({...s,n,date,price,error:'history_lt_201'});continue;}
 if(![c,h,l,v].every(a=>a.length===n&&a.every(Number.isFinite))||c.some(x=>x<=0)||h.some((x,i)=>x<l[i])){rows.push({...s,error:'bad_ohlcv'});continue;}
 const ma=k=>mean(c.slice(-k)),ret=k=>(price/c[n-1-k]-1)*100;
 const diff=c.slice(1).map((x,i)=>x-c[i]),g=rma(diff.map(x=>Math.max(x,0)),14),loss=rma(diff.map(x=>Math.max(-x,0)),14);
 const rsi=last(loss)===0?100:100-100/(1+last(g)/last(loss));
 const tr=c.map((_,i)=>i?Math.max(h[i]-l[i],Math.abs(h[i]-c[i-1]),Math.abs(l[i]-c[i-1])):h[i]-l[i]);
 const atr=last(rma(tr,14)),e12=ema(c,12),e26=ema(c,26),mac=e12.map((x,i)=>x-e26[i]),sig=ema(mac,9);
 const plus=h.map((x,i)=>i&&x-h[i-1]>l[i-1]-l[i]?Math.max(x-h[i-1],0):0),minus=l.map((x,i)=>i&&l[i-1]-x>h[i]-h[i-1]?Math.max(l[i-1]-x,0):0);
 const ar=rma(tr.slice(1),14),pr=rma(plus.slice(1),14),mr=rma(minus.slice(1),14),dx=[];let pdi=0,mdi=0;
 for(let i=13;i<ar.length;i++){pdi=ar[i]?100*pr[i]/ar[i]:0;mdi=ar[i]?100*mr[i]/ar[i]:0;dx.push(pdi+mdi?100*Math.abs(pdi-mdi)/(pdi+mdi):0);}
 const adx=last(rma(dx,14));
 const turnover20=mean(c.slice(-20).map((x,i)=>x*v[n-20+i]))/1e9,vol20=mean(v.slice(-20)),rv=last(v)/mean(v.slice(-21,-1));
 const cmf= c.slice(-20).reduce((a,x,i)=>{const j=n-20+i;return a+(h[j]===l[j]?0:(2*x-h[j]-l[j])/(h[j]-l[j]))*v[j];},0)/v.slice(-20).reduce((a,x)=>a+x,0);
 const t=tv.get(s.name)||{},ma20=ma(20),ma50=ma(50),ma200=ma(200),atrpct=atr/price*100,dist50=(price/ma50-1)*100;
 const eps=t.earnings_per_share_diluted_ttm,pe=t.price_earnings_ttm,roe=t.return_on_equity;
 const recentHigh=Math.max(...h.slice(-63)),low20=Math.min(...l.slice(-20)),low10=Math.min(...l.slice(-10));
 const eligible=date==='2026-09-18'&&turnover20>=(s.exchange==='HOSE'?5:s.exchange==='HNX'?1:2)&&vol20>=50000&&price>ma50&&price>ma200&&ret(63)>0&&rsi>=45&&rsi<=75&&atrpct<=5&&dist50<=18&&(eps==null||eps>0);
 const trend=(price>ma20?4:0)+(price>ma50?6:0)+(price>ma200?6:0)+(ma50>mean(c.slice(-70,-20))?4:0);
 const momentum=Math.min(10,Math.max(0,ret(63)/2))+(rsi>=50&&rsi<=68?5: rsi>45&&rsi<75?2:0)+(last(mac)>last(sig)?5:0);
 const liquidity=Math.min(15,Math.max(0,Math.log10(Math.max(turnover20,0.01))*6));
 const risk=Math.max(0,15-atrpct*2)+(dist50>=0&&dist50<=8?5:dist50<=15&&dist50>=0?2:0);
 const fundamental=(eps>0?4:0)+(pe>0&&pe<18?5:pe>0&&pe<30?2:0)+(roe>=12?4:roe>=8?2:0)+(t.earnings_per_share_growth_ttm>0?2:0);
 const entry=(cmf>0?4:0)+(price>=ma20&&price/ma20<1.06?4:0)+(rv>=1&&rv<3?2:0);
 rows.push({...s,n,date,price,ma20,ma50,ma200,rsi,macd:last(mac),signal:last(sig),hist:last(mac)-last(sig),histPrev:mac.at(-2)-sig.at(-2),adx,pdi,mdi,atr,atrpct,ret21:ret(21),ret63:ret(63),ret126:n>126?ret(126):null,dist50,turnover20,vol20,rv,cmf,high63:recentHigh,high20:Math.max(...h.slice(-20)),low20,low10,pe:pe??null,eps:eps??null,roe:roe??null,epsGrowth:t.earnings_per_share_growth_ttm??null,tvPrice:t.close??null,tvRsi:t.RSI??null,eligible,score:trend+momentum+liquidity+risk+fundamental+entry});
}
const bench=JSON.parse(fs.readFileSync(`${root}/VNINDEX.json`));
const bm=new Map(bench.t.map((t,i)=>[new Date(t*1000).toISOString().slice(0,10),bench.c[i]]));
for(const r of rows.filter(x=>!x.error)){
 const bars=JSON.parse(fs.readFileSync(`${root}/history/${r.name}.json`));
 const startDate=new Date(bars.t.at(-64)*1000).toISOString().slice(0,10);
 r.rs63=bm.has(startDate)&&bm.has(r.date)?r.ret63-(bm.get(r.date)/bm.get(startDate)-1)*100:null;
 r.priceMismatch=r.tvPrice!=null&&Math.abs(r.price/r.tvPrice-1)>0.001;
 if(r.priceMismatch)r.eligible=false;
}
fs.writeFileSync(`${root}/metrics.json`,JSON.stringify(rows,null,2));
console.log(JSON.stringify({total:rows.length,valid:rows.filter(r=>!r.error).length,errors:rows.filter(r=>r.error).reduce((a,r)=>(a[r.error]=(a[r.error]||0)+1,a),{}),dates:rows.filter(r=>!r.error).reduce((a,r)=>(a[r.date]=(a[r.date]||0)+1,a),{})}));
for(const ex of ['HOSE','HNX','UPCOM']){console.log(ex,JSON.stringify(rows.filter(r=>r.exchange===ex&&r.eligible).sort((a,b)=>b.score-a.score).slice(0,16).map(r=>Object.fromEntries(['name','price','score','rsi','ma50','ma200','ret63','atrpct','turnover20','rv','cmf','high63','pe','roe'].map(k=>[k,typeof r[k]==='number'?round(r[k]):r[k]])))));}
