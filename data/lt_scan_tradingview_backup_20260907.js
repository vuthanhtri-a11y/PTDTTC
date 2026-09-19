// lt_scan_tradingview.js — Quet toan bo ro co phieu tu TradingView Desktop.
//
// Dan nguyen file nay vao mcp__tradingview__ui_evaluate. Ham chay NEN, ghi ket
// qua vao window.__S; poll bang mot lenh ui_evaluate ngan de biet da xong chua:
//     (function(){var S=window.__S;return JSON.stringify(
//       {i:S.i,n:S.n,done:S.done,ok:Object.keys(S.res).length,errs:S.errs});})()
//
// Bay da gap va da chan (xem memory tradingview-basic-plan-limits):
//   * chart.exportData() bi chan, fetch() toi scanner.tradingview.com bi CSP chan.
//     Duong duy nhat la doc thang bar tu series.
//   * Sau setSymbol(), chart.symbol() doi TRUOC khi bar moi ve -> vong lap ngay
//     tho se gan du lieu ma truoc cho ma sau MA KHONG BAO LOI. Chan bang cach
//     tinh chu ky (signature) va chi nhan khi sig KHAC ma truoc VA lap lai giong
//     nhau hai lan doc cach 250ms.
//   * ui_evaluate KHONG await promise -> phai luu vao window roi poll.
//
// Toc do ~1,5-6s/ma. 113 ma ~ 3-10 phut.
// Doi "1D" -> "1W" o chart truoc khi chay de lay du lieu tuan (300 bar ~ 5,8 nam).

(function () {
  var U = ("VNINDEX,ACB,BCM,BID,BMP,BSI,BSR,BVH,BWE,CII,CMG,CTD,CTG,CTR,DBC,DCM," +
    "DGC,DGW,DIG,DPM,DSE,DXG,EIB,EVF,FPT,FRT,FTS,GAS,GEE,GEX,GMD,GVR,HAG,HAH,HCM," +
    "HDB,HDC,HDG,HHV,HPG,HSG,HT1,HVN,IMP,KBC,KDC,KDH,KOS,LPB,MBB,MSB,MSN,MWG,NAB," +
    "NKG,NLG,NT2,NTL,NVL,OCB,PAN,PC1,PDR,PHR,PLX,PNJ,POW,PPC,PTB,PVD,PVT,REE,SAB," +
    "SBT,SCS,SHB,SIP,SJS,SSB,SSI,STB,SZC,TCB,TCH,TLG,TMS,TPB,VCB,VCG,VCI,VGC,VHC," +
    "VHM,VIB,VIC,VIX,VJC,VND,VNM,VPB,VPI,VRE,VSC,VTP,BAF,ANV,ASM,CSV,DHC,ELC,GIL," +
    "LSS,MSH").split(",");
  var seen = {};
  U = U.filter(function (s) { if (seen[s]) return false; seen[s] = 1; return true; });

  window.__S = { i: 0, n: U.length, res: {}, errs: [], done: false, cur: null, syms: U };
  var chart = TradingViewApi.activeChart();

  function bars() {
    var b = [];
    try {
      chart.getSeries().data().bars().each(function (i, v) { b.push(v.value || v); return false; });
    } catch (e) { }
    return b;                       // moi bar: [time, O, H, L, C, V]
  }
  function sig(b) {
    return b.length ? b.length + "|" + b[0][0] + "|" + b[b.length - 1][0] + "|" +
      b[b.length - 1][4] + "|" + b[b.length - 1][5] : "0";
  }
  function sleep(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }

  async function grab(sym, prev) {
    chart.setSymbol(sym);
    var last = null;
    for (var t = 0; t < 50; t++) {
      await sleep(250);
      var b = bars(), s = sig(b);
      if (s !== "0" && s !== prev) { if (s === last) return b; last = s; }
    }
    return null;
  }

  function metrics(b) {
    var c = b.map(function (x) { return x[4]; }), h = b.map(function (x) { return x[2]; }),
        l = b.map(function (x) { return x[3]; }), v = b.map(function (x) { return x[5]; });
    var n = c.length;
    function ret(k) { return (n > k && c[n - 1 - k] > 0) ? c[n - 1] / c[n - 1 - k] - 1 : null; }
    function sma(k) { if (n < k) return null; var s = 0; for (var i = n - k; i < n; i++) s += c[i]; return s / k; }
    var tr = [];
    for (var i = Math.max(1, n - 14); i < n; i++) {
      tr.push(Math.max(h[i] - l[i], Math.abs(h[i] - c[i - 1]), Math.abs(l[i] - c[i - 1])) / c[i]);
    }
    var atr = tr.reduce(function (a, x) { return a + x; }, 0) / tr.length;
    var to = 0, k = 0;
    for (var i = Math.max(0, n - 20); i < n; i++) { to += c[i] * v[i]; k++; }
    var ds = [];                    // lay thua ~2 tuan mot diem cho backtest
    for (var i = n - 1; i >= 0; i -= 10) ds.unshift(Math.round(c[i]));
    function rnd(x, d) { return x == null ? null : Math.round(x * Math.pow(10, d)) / Math.pow(10, d); }
    return [rnd(c[n - 1], 2), rnd(ret(21), 4), rnd(ret(63), 4), rnd(ret(126), 4), rnd(ret(252), 4),
            Math.round(sma(50)), Math.round(sma(200)), rnd(atr, 4),
            Math.round(to / k / 1e8) / 10, ds];
  }

  (async function () {
    var prev = null;
    for (var i = 0; i < U.length; i++) {
      window.__S.cur = U[i]; window.__S.i = i;
      try {
        var b = await grab("HOSE_DLY:" + U[i], prev);
        if (!b) { window.__S.errs.push(U[i]); continue; }
        prev = sig(b);
        window.__S.res[U[i]] = metrics(b);
      } catch (e) { window.__S.errs.push(U[i] + ":" + e.message); }
    }
    window.__S.done = true;
  })();
  return "started " + U.length;
})()

// SAU KHI XONG — kiem tra trung du lieu (bat buoc, day la bay da tung dinh):
//   (function(){var R=window.__S.res,k=Object.keys(R),sg={},dup=[];
//    k.forEach(function(s){var g=R[s][0]+"|"+R[s][8];if(sg[g])dup.push(sg[g]+"="+s);sg[g]=s;});
//    return JSON.stringify({n:k.length,dup:dup});})()
// Roi xuat tung khuc ~38 ma mot de dan vao data/scan_YYYYMMDD.json:
//   (function(){var R=window.__S.res,k=Object.keys(R).sort(),o=[];
//    k.slice(0,38).forEach(function(s){o.push('"'+s+'":'+JSON.stringify(R[s]));});
//    return "{"+o.join(",\n")+"}";})()
