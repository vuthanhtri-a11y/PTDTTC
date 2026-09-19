// lt_scan_tradingview.js — Quet toan bo ro co phieu tu TradingView Desktop.
//
// Dan nguyen file nay vao mcp__tradingview__ui_evaluate. Ham chay NEN, ghi ket
// qua vao window.__S; poll bang mot lenh ui_evaluate ngan de biet da xong chua:
//     (function(){var S=window.__S;return JSON.stringify(
//       {i:S.i,n:S.n,done:S.done,ok:Object.keys(S.res).length,errs:S.errs,
//        warn:S.warn,bars:S.bars_min+"-"+S.bars_max});})()
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
// 07/09/2026 — MO RONG LICH SU LEN >=560 BAR (truoc day ~300 bar ~ 1,2 nam).
//   Ly do: quy tac thu nam (ban bot khi gia qua nong) can phan phoi khoang cach
//   gia-MA50 trong HAI NAM = 500 quan sat, cong 49 bar khoi dong MA50 = 549.
//   Cach lam: dat visible range lui 1.200 ngay lich MOT LAN truoc vong lap;
//   TradingView tu nap lich su theo khung nay cho tung ma khi doi symbol.
//   Neu API setVisibleRange khong ton tai -> ghi window.__S.warn va chay tiep
//   voi so bar mac dinh; truong `dma50` khi do bao nobs < 500 va lt_screener
//   danh dau dau hieu (a) la "khong du du lieu" thay vi tinh bua tren cua so ngan.
//   Toan bo truong CU deu neo vao bar CUOI (r21..r252, sma, atr, tov, ds) nen
//   nap them lich su KHONG lam doi gia tri cua chung — da giu ds dung 30 diem
//   de ban quet moi so sanh duoc voi cac ban truoc.
//
// 07/09/2026 — DONG BO SCHEMA: ban quet 04/09 tren thuc te da ghi 12 truong
//   (them r1, r5 o chi so 10, 11) nhung file .js nay van la ban 10 truong.
//   Nay da dua r1/r5 vao code de file khop voi du lieu that.
//
// Toc do ~3-10s/ma (cham hon ban 300 bar). 113 ma ~ 6-20 phut.
// Doi "1D" -> "1W" o chart truoc khi chay de lay du lieu tuan (300 bar ~ 5,8 nam).
// LUU Y: ban san xuat chay tren 1D. Chay 1W chi de backtest, va khi do truong
// `dma50` mang y nghia khac (500 TUAN chu khong phai 500 phien) — dung dem sang.

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

  // --- Tham so quy tac thu nam — PHAI KHOP QUA_NONG trong lt_config.py ---
  var MA_LEN = 50;                          // MA trung han cho dau hieu (a)
  var NEED_OBS = 500;                       // 2 nam quan sat khoang cach gia-MA50
  var NEED_BARS = NEED_OBS + MA_LEN + 10;   // 560 = 500 quan sat + khoi dong MA + du tru
  var VOL_WIN = 60;                         // cua so dau hieu (c): ~3 thang
  var DS_KEEP = 30;                         // giu dung 30 diem nhu cac ban quet cu

  window.__S = { i: 0, n: U.length, res: {}, errs: [], done: false, cur: null,
                 syms: U, warn: null, bars_min: null, bars_max: null,
                 need_bars: NEED_BARS };
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

  // Mo rong khung nhin lui ve qua khu MOT LAN truoc vong lap. Moi lan setSymbol
  // sau do, TradingView nap thang lich su cho khung nay -> khong phai keo tung ma.
  async function moRongLichSu() {
    if (typeof chart.setVisibleRange !== "function") {
      window.__S.warn = "setVisibleRange khong co -> chay voi so bar mac dinh; " +
                        "dau hieu (a) cua quy tac 5 se KHONG du du lieu";
      return;
    }
    var now = Math.floor(Date.now() / 1000);
    try {
      await chart.setVisibleRange({ from: now - 1200 * 86400, to: now });
      await sleep(1500);
    } catch (e) {
      window.__S.warn = "setVisibleRange loi: " + e.message;
    }
  }

  // Cho tin hieu on dinh: sig phai KHAC ma truoc VA lap lai giong nhau hai lan.
  // sig chua so luong bar, nen trong luc lich su con dang nap thi sig con doi ->
  // vong lap tu dong doi nap xong. Timeout dai gap doi ban 300 bar (80 x 250ms).
  async function grab(sym, prev) {
    chart.setSymbol(sym);
    var last = null;
    for (var t = 0; t < 80; t++) {
      await sleep(250);
      var b = bars(), s = sig(b);
      if (s !== "0" && s !== prev) { if (s === last) return b; last = s; }
    }
    return null;
  }

  // (a) Khoang cach gia-MA50 hom nay nam o phan vi nao trong phan phoi 2 nam
  //     cua CHINH ma do. Tra ve [d_hom_nay, phan_vi, so_quan_sat].
  //     so_quan_sat < NEED_OBS => chua du 2 nam; lt_screener phai coi la KHONG
  //     danh gia duoc, chu khong phai "khong qua nong".
  function distMa50(c) {
    var n = c.length;
    if (n < MA_LEN + 20) return [null, null, 0];
    var d = [], s = 0;
    for (var i = 0; i < n; i++) {
      s += c[i];
      if (i >= MA_LEN) s -= c[i - MA_LEN];
      if (i >= MA_LEN - 1) {
        var ma = s / MA_LEN;
        d.push(ma > 0 ? c[i] / ma - 1 : 0);
      }
    }
    if (d.length > NEED_OBS) d = d.slice(d.length - NEED_OBS);
    var now = d[d.length - 1], le = 0;
    for (var j = 0; j < d.length; j++) if (d[j] <= now) le++;
    return [Math.round(now * 1e4) / 1e4,
            Math.round(le / d.length * 1e3) / 1e3,
            d.length];
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
    if (ds.length > DS_KEEP) ds = ds.slice(ds.length - DS_KEEP);   // dung 30 diem nhu ban cu

    // Chuoi 60 phien gan nhat cho dau hieu (c). Can CA HAI chuoi vi luat doi
    // "khoi luong dot bien roi CAN DAN trong khi GIA VAN LEN" — thieu gia thi
    // khong phan biet duoc phan phoi dinh voi tich luy can KL lanh manh.
    var w = Math.min(VOL_WIN, n);
    var vol60 = [], c60 = [];
    for (var i = n - w; i < n; i++) {
      vol60.push(Math.round((v[i] || 0) / 1000));   // don vi 1.000 CP
      c60.push(Math.round(c[i]));
    }
    function rnd(x, d) { return x == null ? null : Math.round(x * Math.pow(10, d)) / Math.pow(10, d); }
    return [rnd(c[n - 1], 2), rnd(ret(21), 4), rnd(ret(63), 4), rnd(ret(126), 4), rnd(ret(252), 4),
            Math.round(sma(50)), Math.round(sma(200)), rnd(atr, 4),
            Math.round(to / k / 1e8) / 10, ds,
            rnd(ret(1), 4), rnd(ret(5), 4),          // 10, 11 — nhip phien / tuan
            distMa50(c), vol60, c60];                // 12, 13, 14 — quy tac thu nam
  }

  (async function () {
    await moRongLichSu();
    var prev = null;
    for (var i = 0; i < U.length; i++) {
      window.__S.cur = U[i]; window.__S.i = i;
      try {
        var b = await grab("HOSE_DLY:" + U[i], prev);
        if (!b) { window.__S.errs.push(U[i]); continue; }
        prev = sig(b);
        window.__S.res[U[i]] = metrics(b);
        if (window.__S.bars_min === null || b.length < window.__S.bars_min) window.__S.bars_min = b.length;
        if (window.__S.bars_max === null || b.length > window.__S.bars_max) window.__S.bars_max = b.length;
      } catch (e) { window.__S.errs.push(U[i] + ":" + e.message); }
    }
    window.__S.done = true;
  })();
  return "started " + U.length + " (can >=" + NEED_BARS + " bar/ma)";
})()

// SAU KHI XONG — kiem tra trung du lieu (bat buoc, day la bay da tung dinh):
//   (function(){var R=window.__S.res,k=Object.keys(R),sg={},dup=[];
//    k.forEach(function(s){var g=R[s][0]+"|"+R[s][8];if(sg[g])dup.push(sg[g]+"="+s);sg[g]=s;});
//    return JSON.stringify({n:k.length,dup:dup});})()
//
// VA kiem tra do phu lich su (moi 07/09/2026 — thieu thi quy tac 5 khong chay):
//   (function(){var R=window.__S.res,k=Object.keys(R),thieu=[];
//    k.forEach(function(s){if(!R[s][12]||R[s][12][2]<500)thieu.push(s+":"+(R[s][12]?R[s][12][2]:0));});
//    return JSON.stringify({thieu_2nam:thieu.length,vd:thieu.slice(0,10)});})()
//
// Roi xuat tung khuc de dan vao data/scan_YYYYMMDD.json. Ban 15 truong nang
// dung luong len ~3 lan ban cu -> cat khuc 20 ma thay vi 38:
//   (function(){var R=window.__S.res,k=Object.keys(R).sort(),o=[];
//    k.slice(0,20).forEach(function(s){o.push('"'+s+'":'+JSON.stringify(R[s]));});
//    return "{"+o.join(",\n")+"}";})()
