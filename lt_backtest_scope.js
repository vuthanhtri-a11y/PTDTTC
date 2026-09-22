// lt_backtest_scope.js — Do lai chien luoc DAI HAN voi PHAM VI XEP HANG moi.
//
// Ly do ton tai: Triet_ly_dau_tu_FF5.docx (ban da chot) noi thang diem tinh
// "phan vi trong ro DA QUA BO LOC". Ban backtest cu (lt_backtest_tradingview.js)
// xep hang tren TOAN RO. Voi nguong 40%, hai cach khac nhau rat xa:
//   toan ro ~112 ma -> top 40% la ~45 ma  -> quy tac 3 gan nhu khong rang buoc
//   ro da loc ~N ma -> top 40% la 0,4N ma -> quy tac 3 thanh rang buoc chinh
// => con so 13,89%/nam khong con do dung he thong dang chay. File nay do lai.
//
// Ba pham vi duoc chay canh nhau:
//   A  — toan ro (ban cu, de doi chung: phai ra lai ~13,89%)
//   B1 — ro da loc; ma DANG GIU ma roi khoi bo loc van duoc gan thu hang bang
//        cach chen diem cua no vao bang xep hang cua nhom qua loc
//   B2 — ro da loc; ma DANG GIU ma roi khoi bo loc coi nhu hong quy tac 3 -> ban
//        (day la hanh vi cua lt_allocator.py sau ban sua 25/08/2026)
//
// Du lieu: window.__W.res[ma] = {c: [<=75 diem gia tuan, moi diem cach 4 tuan]}
// Chay lt_scan_weekly truoc (chart o khung 1W).

(function () {
  var R = window.__W.res, G = window.__W.G || 75,
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
  function r2(s, t, k) {
    var y = []; for (var i = t - k + 1; i <= t; i++) { var p = px(s, i); if (p) y.push(Math.log(p)); }
    var n = y.length; if (n < 5) return null;
    var xm = (n - 1) / 2, ym = y.reduce(function (a, b) { return a + b; }, 0) / n, sxy = 0, sxx = 0, syy = 0;
    for (var i = 0; i < n; i++) { sxy += (i - xm) * (y[i] - ym); sxx += (i - xm) * (i - xm); syy += (y[i] - ym) * (y[i] - ym); }
    if (sxx <= 0 || syy <= 0) return 0;
    var v = sxy * sxy / (sxx * syy); return sxy > 0 ? v : -v;
  }
  function prank(a) {
    var idx = a.map(function (v, i) { return i; }); idx.sort(function (x, y) { return a[x] - a[y]; });
    var o = a.map(function () { return 0; });
    for (var start = 0; start < idx.length;) {
      var end = start + 1;
      while (end < idx.length && a[idx[end]] === a[idx[start]]) end++;
      var rank = idx.length > 1 ? (start + end - 1) / 2 / (idx.length - 1) : 0.5;
      for (var j = start; j < end; j++) o[idx[j]] = rank;
      start = end;
    }
    return o;
  }

  function scoreRows(rows, field) {
    rows.forEach(function (o) { o[field] = 0; });
    [["rs12", 0.4], ["rs6", 0.3], ["rs3", 0.2], ["q", 0.1]].forEach(function (item) {
      var ranks = prank(rows.map(function (o) { return o[item[0]]; }));
      rows.forEach(function (o, i) { o[field] += item[1] * ranks[i]; });
    });
  }

  var SNAP = {}, POOL = [];
  function snapshot(t) {
    if (SNAP[t]) return SNAP[t];
    var out = [], i12 = mom("VNINDEX", t, 13, 1), i6 = mom("VNINDEX", t, 6, 0), i3 = mom("VNINDEX", t, 3, 0);
    SYMS.forEach(function (s) {
      var c = px(s, t), m10 = ma(s, t, 10), m3 = ma(s, t, 3), v = vol(s, t, 6),
          a12 = mom(s, t, 13, 1), a6 = mom(s, t, 6, 0), a3 = mom(s, t, 3, 0), q = r2(s, t, 7);
      if (c == null || m10 == null || m3 == null || v == null || a12 == null || a6 == null || a3 == null) return;
      out.push({
        s: s,
        pass: (c > m10 && m3 > m10 && (a12 - i12) > 0),
        soft: (c > m10 * 0.97 && (a12 - i12) > -0.05),
        rs12: a12 - i12, rs6: a6 - i6, rs3: a3 - i3, q: q || 0, v: Math.max(v, 0.01)
      });
    });
    scoreRows(out, "score");
    out.sort(function (a, b) { return b.score - a.score || a.s.localeCompare(b.s); });

    // --- A: thu hang tren TOAN RO (ban cu)
    out.forEach(function (o, i) { o.rankA = i / Math.max(1, out.length - 1); });

    // --- B: thu hang trong RO DA QUA BO LOC
    var pas = out.filter(function (o) { return o.pass; });
    // Filter BEFORE computing component percentiles, as in lt_screener.py.
    // Merely filtering the globally scored table leaves rejected stocks able
    // to change the relative weights of the four ranking components.
    scoreRows(pas, "scoreB");
    pas.sort(function (a, b) { return b.scoreB - a.scoreB || a.s.localeCompare(b.s); });
    var np = pas.length;
    POOL.push(np);
    var groupRank = 0;
    pas.forEach(function (o, i) {
      if (i === 0 || o.scoreB !== pas[i - 1].scoreB) groupRank = i;
      o.rankB1 = np > 1 ? groupRank / (np - 1) : 0; o.rankB2 = o.rankB1;
    });
    out.forEach(function (o) {
      if (o.pass) return;
      // B1: evaluate a held, rejected stock against the FIXED passing universe;
      // inserting it must not change the scores of the eligible stocks.
      o.scoreB = 0;
      [["rs12", 0.4], ["rs6", 0.3], ["rs3", 0.2], ["q", 0.1]].forEach(function (item) {
        var less = 0, equal = 0;
        pas.forEach(function (p) {
          if (p[item[0]] < o[item[0]]) less++;
          if (p[item[0]] === o[item[0]]) equal++;
        });
        var r = np > 1 ? Math.max(0, Math.min(1, (less + (equal ? (equal - 1) / 2 : 0)) / (np - 1)))
          : np === 1 ? (o[item[0]] === pas[0][item[0]] ? 0.5 : +(o[item[0]] > pas[0][item[0]])) : 0;
        o.scoreB += item[1] * r;
      });
      var k = 0; while (k < np && pas[k].scoreB > o.scoreB) k++;
      o.rankB1 = np > 1 ? Math.min(1, k / (np - 1)) : 1;
      // B2: roi khoi bo loc = hong quy tac 3
      o.rankB2 = 1.0;
    });
    SNAP[t] = out; return out;
  }
  function fwd(s, t) { var a = px(s, t + 1), b = px(s, t); return (a && b) ? a / b - 1 : 0; }

  function weights(sel, N, cap) {
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

  // o = {N, cap, hyst, band, cost, scope: "A"|"B1"|"B2", noTrend, rand}
  function run(o, t0, t1) {
    var cost = (o.cost == null ? 0.004 : o.cost), key = "rank" + (o.scope || "A");
    var nav = 1, prev = {}, held = [], curve = [1], ms = [], seed = 12345;
    function rnd() { seed = (seed * 1103515245 + 12345) & 0x7fffffff; return seed / 0x7fffffff; }
    for (var t = t0; t < t1; t++) {
      var scoreKey = o.scope === "B1" || o.scope === "B2" ? "scoreB" : "score";
      var snap = snapshot(t).slice().sort(function (a, b) {
        return b[scoreKey] - a[scoreKey] || a.s.localeCompare(b.s);
      }), by = {}; snap.forEach(function (x) { by[x.s] = x; });
      var keep = [];
      if (!o.rand) {
        held.forEach(function (s) { var x = by[s]; if (x && x.soft && x[key] <= o.hyst) keep.push(x); });
      }
      var have = {}; keep.forEach(function (x) { have[x.s] = 1; });
      var pool = snap.filter(function (x) { return (o.noTrend ? true : x.pass) && !have[x.s]; });
      if (o.rand) { pool = pool.slice(); for (var i = pool.length - 1; i > 0; i--) { var j = Math.floor(rnd() * (i + 1)), tmp = pool[i]; pool[i] = pool[j]; pool[j] = tmp; } }
      var w = weights(keep.concat(pool.slice(0, Math.max(0, o.N - keep.length))), o.N, o.cap);
      if (o.band) {
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
      var np2 = {}, sc = 1 + g;
      for (var k in w) np2[k] = w[k] * (1 + fwd(k, t)) / sc;
      prev = np2; held = Object.keys(np2);
    }
    var pk = curve[0], m = 0; curve.forEach(function (v) { if (v > pk) pk = v; m = Math.min(m, v / pk - 1); });
    var mu = ms.reduce(function (a, b) { return a + b; }, 0) / ms.length,
        sd = Math.sqrt(ms.reduce(function (a, b) { return a + (b - mu) * (b - mu); }, 0) / (ms.length - 1));
    return {
      cagr: +(Math.pow(nav, 12 / (t1 - t0)) - 1).toFixed(4), mdd: +m.toFixed(4),
      alpha_thang: +mu.toFixed(5), t: +(mu / (sd / Math.sqrt(ms.length))).toFixed(2)
    };
  }

  var T0 = 22, T1 = G - 1, out = {};
  out._meta = { G: G, syms: SYMS.length, t0: T0, t1: T1, thang: T1 - T0 };

  ["A", "B1", "B2"].forEach(function (sc) {
    out["CL_" + sc] = run({ N: 10, cap: 0.15, hyst: 0.40, band: 0.03, scope: sc }, T0, T1);
  });

  var iv = 1; for (var t = T0; t < T1; t++) iv *= (1 + fwd("VNINDEX", t));
  out.VNINDEX = { cagr: +(Math.pow(iv, 12 / (T1 - T0)) - 1).toFixed(4) };

  // Do nhay nguong thu hang, chay rieng cho tung pham vi
  ["A", "B1", "B2"].forEach(function (sc) {
    var h = {};
    [0.20, 0.25, 0.33, 0.40, 0.50, 0.60, 0.80, 1.00].forEach(function (x) {
      h[x] = run({ N: 10, cap: 0.15, hyst: x, band: 0.03, scope: sc }, T0, T1).cagr;
    });
    out["hyst_" + sc] = h;
  });

  // Doi chung
  out.tai_can_bang_moi_thang = run({ N: 10, cap: 0.15, hyst: -1, band: 0, scope: "B1" }, T0, T1);
  out.boc_tham_10 = run({ N: 10, cap: 0.15, hyst: 0.40, band: 0.03, scope: "B1", rand: 1 }, T0, T1);
  out.bo_loc_xu_huong = run({ N: 10, cap: 0.15, hyst: 0.40, band: 0.03, scope: "B1", noTrend: 1 }, T0, T1);

  // Kich thuoc ro da loc theo thoi gian — quyet dinh quy tac 3 co rang buoc khong
  var ps = POOL.slice(0, T1 - T0).sort(function (a, b) { return a - b; });
  out.pool = { min: ps[0], p25: ps[Math.floor(ps.length * 0.25)], median: ps[Math.floor(ps.length / 2)],
               p75: ps[Math.floor(ps.length * 0.75)], max: ps[ps.length - 1],
               tb: +(ps.reduce(function (a, b) { return a + b; }, 0) / ps.length).toFixed(1) };
  return JSON.stringify(out);
})()
