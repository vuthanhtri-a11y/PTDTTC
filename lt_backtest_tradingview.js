// lt_backtest_tradingview.js — BAN CU, GIU DE DOI CHIEU. DUNG lt_backtest_scope.js.
//
// ⚠️ 26/08/2026: file nay xep hang tren TOAN RO, trong khi ban chot
// Triet_ly_dau_tu_FF5.docx yeu cau phan vi trong RO DA QUA BO LOC. Ngoai ra no
// chi chay MOT pha luoi lay mau -> moi con so trong header duoi day la mot lan
// rut tham. Dich luoi mot tuan lam CAGR doi toi 5,2 diem phan tram.
// Ban thay the: lt_backtest_scope.js (3 pham vi x 4 pha luoi).
//
// lt_backtest_tradingview.js — Backtest chien luoc DAI HAN tren du lieu TUAN.
//
// Day la doan code DA CHAY ngay 17/08/2026 de ra cac con so trong
// CHIEN_LUOC_DAI_HAN.md. Chay lai: doi chart sang khung "1W", chay
// lt_scan_tradingview.js (bien the luu window.__W voi c = close moi 4 tuan),
// roi dan file nay vao ui_evaluate.
//
// Du lieu: window.__W.res[ma] = {c: [~75 diem gia, moi diem cach 4 tuan]}.
// Cac ma niem yet muon co it diem hon -> can chinh phai theo NGAY CUOI (deu la
// 2026-08-17), do la y nghia cua bien `off` trong px().
//
// Ket qua (52 thang, 2022-04 -> 2026-08, da tru phi 0,4% moi vong quay):
//   VNINDEX mua & giu                                7,51%/nam, sut giam -20,2%
//   Thang + giu lai top40% + bien 3% (CHIEN LUOC)   13,89%/nam, sut giam -21,3%
//   Thang, tai can bang toan bo moi thang            6,95%/nam, sut giam -34,5%
//   Boc tham 10 ma tu ro qua loc                     2,43%/nam
//   Top 10 diem RS nhung BO QUA bo loc xu huong      2,28%/nam
// t-stat cua alpha thang = 0,87 -> KHONG co y nghia thong ke. Xem muc "Canh bao".

(function () {
  var R = window.__W.res, G = 75,
      SYMS = Object.keys(R).filter(function (s) { return s !== "VNINDEX"; });

  function px(s, t) { var a = R[s].c, off = G - a.length, i = t - off; return (i >= 0 && i < a.length && a[i] > 0) ? a[i] : null; }
  function mom(s, t, k, sk) { var A = px(s, t - (sk || 0)), B = px(s, t - k); return (A && B) ? A / B - 1 : null; }
  function ma(s, t, k) { var v = 0, n = 0; for (var i = t - k + 1; i <= t; i++) { var p = px(s, i); if (p) { v += p; n++; } } return n === k ? v / n : null; }
  function vol(s, t, k) {
    var r = []; for (var i = t - k + 1; i <= t; i++) { var a = px(s, i), b = px(s, i - 1); if (a && b) r.push(a / b - 1); }
    if (r.length < 3) return null;
    var m = r.reduce(function (x, y) { return x + y; }, 0) / r.length;
    return Math.sqrt(r.reduce(function (x, y) { return x + (y - m) * (y - m); }, 0) / (r.length - 1));
  }
  function r2(s, t, k) {   // chat luong xu huong: R^2 cua log(gia) theo thoi gian
    var y = []; for (var i = t - k + 1; i <= t; i++) { var p = px(s, i); if (p) y.push(Math.log(p)); }
    var n = y.length; if (n < 5) return null;
    var xm = (n - 1) / 2, ym = y.reduce(function (a, b) { return a + b; }, 0) / n, sxy = 0, sxx = 0, syy = 0;
    for (var i = 0; i < n; i++) { sxy += (i - xm) * (y[i] - ym); sxx += (i - xm) * (i - xm); syy += (y[i] - ym) * (y[i] - ym); }
    if (sxx <= 0 || syy <= 0) return 0;
    var v = sxy * sxy / (sxx * syy); return sxy > 0 ? v : -v;
  }
  function prank(a) {
    var idx = a.map(function (v, i) { return i; }); idx.sort(function (x, y) { return a[x] - a[y]; });
    var o = a.map(function () { return 0; }); idx.forEach(function (i, r) { o[i] = r / Math.max(1, idx.length - 1); });
    return o;
  }

  var SNAP = {};
  function snapshot(t) {                       // anh chup toan ro tai thoi diem t
    if (SNAP[t]) return SNAP[t];
    var out = [], i12 = mom("VNINDEX", t, 13, 1), i6 = mom("VNINDEX", t, 6, 0), i3 = mom("VNINDEX", t, 3, 0);
    SYMS.forEach(function (s) {
      var c = px(s, t), m10 = ma(s, t, 10), m3 = ma(s, t, 3), v = vol(s, t, 6),
          a12 = mom(s, t, 13, 1), a6 = mom(s, t, 6, 0), a3 = mom(s, t, 3, 0), q = r2(s, t, 7);
      if (c == null || m10 == null || m3 == null || v == null || a12 == null || a6 == null || a3 == null) return;
      out.push({
        s: s,
        pass: (c > m10 && m3 > m10 && (a12 - i12) > 0),      // dieu kien MUA MOI
        soft: (c > m10 * 0.97 && (a12 - i12) > -0.05),       // dieu kien GIU TIEP
        rs12: a12 - i12, rs6: a6 - i6, rs3: a3 - i3, q: q || 0, v: Math.max(v, 0.01)
      });
    });
    var p12 = prank(out.map(function (o) { return o.rs12; })), p6 = prank(out.map(function (o) { return o.rs6; })),
        p3 = prank(out.map(function (o) { return o.rs3; })), pq = prank(out.map(function (o) { return o.q; }));
    out.forEach(function (o, i) { o.score = 0.4 * p12[i] + 0.3 * p6[i] + 0.2 * p3[i] + 0.1 * pq[i]; });
    out.sort(function (a, b) { return b.score - a.score; });
    out.forEach(function (o, i) { o.rank = i / Math.max(1, out.length - 1); });
    SNAP[t] = out; return out;
  }
  function fwd(s, t) { var a = px(s, t + 1), b = px(s, t); return (a && b) ? a / b - 1 : 0; }

  function weights(sel, N, cap) {              // 1/bien dong, tran ma, o trong = tien
    var w = {}, raw = {}, tot = (1 - 0.02) / N * sel.length, sum = 0;
    sel.forEach(function (o) { raw[o.s] = 1 / o.v; sum += raw[o.s]; });
    sel.forEach(function (o) { w[o.s] = raw[o.s] / sum * tot; });
    for (var it = 0; it < 20; it++) {
      var ex = 0, rest = [];
      for (var k in w) { if (w[k] > cap) { ex += w[k] - cap; w[k] = cap; } else rest.push(k); }
      if (ex < 1e-9 || !rest.length) break;
      var sr = 0; rest.forEach(function (k) { sr += w[k]; });
      rest.forEach(function (k) { w[k] += ex * (sr > 0 ? w[k] / sr : 1 / rest.length); });
    }
    return w;
  }

  // o = {N, cap, hyst (nguong thu hang giu lai), band (bien khong giao dich), cost}
  function run(o, t0, t1) {
    var cost = (o.cost == null ? 0.004 : o.cost);
    var nav = 1, prev = {}, held = [], curve = [], ms = [];
    for (var t = t0; t < t1; t++) {
      var snap = snapshot(t), by = {}; snap.forEach(function (x) { by[x.s] = x; });
      var keep = [];
      held.forEach(function (s) { var x = by[s]; if (x && x.soft && x.rank <= o.hyst) keep.push(x); });
      var have = {}; keep.forEach(function (x) { have[x.s] = 1; });
      var pool = snap.filter(function (x) { return x.pass && !have[x.s]; });
      var w = weights(keep.concat(pool.slice(0, Math.max(0, o.N - keep.length))), o.N, o.cap);
      if (o.band) {                            // khong dieu chinh neu lech qua nho
        var w2 = {}, ks = {};
        for (var k in w) ks[k] = 1; for (var k in prev) ks[k] = 1;
        for (var k in ks) { var a = prev[k] || 0, b = w[k] || 0; w2[k] = (Math.abs(b - a) < o.band && b > 0 && a > 0) ? a : b; if (w2[k] <= 0) delete w2[k]; }
        w = w2;
      }
      var to = 0, k2 = {}; for (var k in w) k2[k] = 1; for (var k in prev) k2[k] = 1;
      for (var k in k2) to += Math.abs((w[k] || 0) - (prev[k] || 0));
      var g = 0; for (var k in w) g += w[k] * fwd(k, t);
      var net = (1 + g) * (1 - to / 2 * cost) - 1;
      nav *= (1 + net); curve.push(nav); ms.push(net - fwd("VNINDEX", t));
      var np = {}, sc = 1 + g;                 // ty trong troi theo gia sang thang sau
      for (var k in w) np[k] = w[k] * (1 + fwd(k, t)) / sc;
      prev = np; held = Object.keys(np);
    }
    var pk = curve[0], m = 0; curve.forEach(function (v) { if (v > pk) pk = v; m = Math.min(m, v / pk - 1); });
    var mu = ms.reduce(function (a, b) { return a + b; }, 0) / ms.length,
        sd = Math.sqrt(ms.reduce(function (a, b) { return a + (b - mu) * (b - mu); }, 0) / (ms.length - 1));
    return {
      cagr: Math.pow(nav, 12 / (t1 - t0)) - 1, mdd: m,
      alpha_thang: mu, t: mu / (sd / Math.sqrt(ms.length))
    };
  }

  var out = { CHIEN_LUOC: run({ N: 10, cap: 0.15, hyst: 0.40, band: 0.03 }, 22, G - 1) };
  var iv = 1; for (var t = 22; t < G - 1; t++) iv *= (1 + fwd("VNINDEX", t));
  out.VNINDEX = { cagr: Math.pow(iv, 12 / (G - 1 - 22)) - 1 };
  // Do nhay: bo do nhay nao cung nen chay lai truoc khi tin mot con so.
  [0.25, 0.33, 0.40, 0.50, 0.60].forEach(function (h) {
    out["hyst_" + h] = run({ N: 10, cap: 0.15, hyst: h, band: 0.03 }, 22, G - 1).cagr;
  });
  [5, 6, 8, 10, 12, 15].forEach(function (n) {
    out["N_" + n] = run({ N: n, cap: Math.max(0.15, 1.4 / n), hyst: 0.40, band: 0.03 }, 22, G - 1).cagr;
  });
  return JSON.stringify(out);
})()
