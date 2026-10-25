# -*- coding: utf-8 -*-
"""
medici_regime.py — Nhận diện chế độ thị trường (market regime) cho VN-Index
Quỹ Medici · PTĐTTC 2026

Bốn trụ của khung chế độ thị trường:
  1. Xu hướng      : giá so với MA50 / MA200, độ dốc MA200
  2. Cổng momentum : dấu lợi suất 36 tháng (Cooper–Gutierrez–Hameed 2004;
                     kiểm định tại VN: Hoàng Văn Hải và cộng sự 2022)
  3. Biến động     : GARCH(1,1) Student-t, phân vị biến động có điều kiện
  4. Markov switching (Hamilton 1989) 2 và 3 trạng thái, chuyển cả trung bình
     lẫn phương sai (giống Trần Thị Tuấn Anh 2018; Võ Văn Hảo 2020)

Kèm theo:
  - Kiểm định walk-forward NGOÀI MẪU, không nhìn trước (dùng xác suất LỌC,
    không dùng xác suất LÀM TRƠN), có chi phí giao dịch và độ trễ xác nhận.
  - Bootstrap khối (circular block) cho chênh lệch Sharpe so với mua-và-giữ.
  - Kịch bản có xác suất: mô phỏng Monte Carlo từ mô hình Markov đã ước lượng,
    xuất phát từ xác suất trạng thái hiện tại.

CÁCH CHẠY
  pip install pandas numpy statsmodels arch matplotlib openpyxl
  # 1) Dữ liệu CSV xuất từ TradingView (HOSE:VNINDEX, khung 1D):
  python medici_regime.py --csv VNINDEX_1D.csv
  # 2) Lấy trực tiếp bằng vnstock (đã cài trên máy):
  python medici_regime.py --vnstock
  # 3) Chạy thử trên dữ liệu giả lập có tham số đã biết (kiểm tra mô hình):
  python medici_regime.py --demo

Kết quả nằm trong thư mục ket_qua_regime/ :
  tom_tat.json, tom_tat.md, regime_ket_qua.xlsx, 6 biểu đồ PNG.
"""
import argparse
import json
import os
import sys
import time
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

TD_YEAR = 250  # số phiên giao dịch/năm của HOSE (xấp xỉ)
MAXITER = 1000     # số vòng lặp tối đa của bộ tối ưu (statsmodels mặc định chỉ 100)
GTOL = 1e-8        # ngưỡng gradient để BFGS dừng ở bước đánh bóng
TOL_GRAD = 1e-3    # max|gradient| (không gian không ràng buộc) chấp nhận là đã hội tụ


# ----------------------------------------------------------------------------
# 0. DỮ LIỆU
# ----------------------------------------------------------------------------
def doc_csv(path):
    """Đọc CSV linh hoạt: TradingView (time,open,high,low,close,...),
    Investing (Date,Price,...), vnstock (time,open,...,close)."""
    df = pd.read_csv(path)
    cols = {c.lower().strip(): c for c in df.columns}
    c_date = next((cols[k] for k in ("time", "date", "ngày", "ngay", "tradingdate") if k in cols), None)
    c_close = next((cols[k] for k in ("close", "price", "đóng cửa", "dong cua", "closeprice", "adj close") if k in cols), None)
    if c_date is None or c_close is None:
        sys.exit(f"Không nhận ra cột ngày/giá đóng cửa trong {path}. Các cột: {list(df.columns)}")
    s = df[[c_date, c_close]].copy()
    s.columns = ["date", "close"]
    # TradingView có thể xuất unix time (giây)
    if pd.api.types.is_numeric_dtype(s["date"]):
        unit = "ms" if s["date"].abs().max() > 1e11 else "s"   # TradingView: giây; vài nguồn: mili-giây
        s["date"] = pd.to_datetime(s["date"], unit=unit) + pd.Timedelta(hours=7)  # UTC → giờ VN
    else:
        s["date"] = pd.to_datetime(s["date"], dayfirst=False, errors="coerce")
    if not pd.api.types.is_numeric_dtype(s["close"]):
        s["close"] = s["close"].astype(str).str.replace(",", "").astype(float)
    s = s.dropna().drop_duplicates("date").sort_values("date").set_index("date")["close"]
    s.index = s.index.tz_localize(None) if s.index.tz is not None else s.index
    s.index = s.index.normalize()
    return s.astype(float)


def lay_vnstock(start):
    """Lấy VN-Index bằng vnstock; thử cả API mới (v3+) và cũ."""
    end = pd.Timestamp.today().strftime("%Y-%m-%d")
    try:
        from vnstock import Vnstock
        for src in ("VCI", "TCBS"):
            try:
                q = Vnstock().stock(symbol="VNINDEX", source=src).quote
                df = q.history(start=start, end=end, interval="1D")
                if df is not None and len(df) > 100:
                    break
            except Exception:
                df = None
    except ImportError:
        df = None
    if df is None or len(df) < 100:
        try:
            from vnstock import stock_historical_data
            df = stock_historical_data("VNINDEX", start, end, "1D", type="index")
        except Exception as e:
            sys.exit(f"vnstock không lấy được dữ liệu ({e}). Hãy xuất CSV từ TradingView và chạy --csv.")
    df = df.rename(columns={c: c.lower() for c in df.columns})
    c_date = "time" if "time" in df.columns else "tradingdate"
    s = pd.Series(df["close"].values, index=pd.to_datetime(df[c_date]))
    s.index = s.index.normalize()
    return s.sort_index().astype(float)


def gia_lap(seed=7):
    """Chuỗi giả lập 2 trạng thái với tham số ĐÃ BIẾT, để kiểm tra mô hình
    có tìm lại đúng tham số hay không. Không phải dữ liệu thị trường."""
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2010-01-04", "2026-10-14")
    n = len(idx)
    p11, p22 = 0.9793, 0.9229          # duy trì Tăng / Giảm (Võ Văn Hảo 2020)
    mu = np.array([0.09, -0.20])        # %/phiên
    sd = np.array([0.95, 2.10])         # %/phiên
    st = np.zeros(n, dtype=int)
    for t in range(1, n):
        stay = p11 if st[t - 1] == 0 else p22
        st[t] = st[t - 1] if rng.random() < stay else 1 - st[t - 1]
    r = mu[st] + sd[st] * rng.standard_t(6, n) / np.sqrt(6 / 4)
    lvl = 500 * np.exp(np.cumsum(r) / 100)
    lvl = lvl * (1704.87 / lvl[-1])
    truth = dict(p_tang=p11, p_giam=p22, mu=mu.tolist(), sd=sd.tolist(),
                 ty_le_giam=float(st.mean()))
    return pd.Series(lvl, index=idx), pd.Series(st, index=idx), truth


# ----------------------------------------------------------------------------
# 1. CHỈ BÁO XU HƯỚNG & CỔNG MOMENTUM
# ----------------------------------------------------------------------------
def chi_bao_xu_huong(close):
    df = pd.DataFrame({"close": close})
    df["ma20"] = close.rolling(20).mean()
    df["ma50"] = close.rolling(50).mean()
    df["ma200"] = close.rolling(200).mean()
    df["doc_ma200_20p"] = df["ma200"].pct_change(20) * 100      # % thay đổi MA200 trong 20 phiên
    df["ret_12t"] = close.pct_change(TD_YEAR) * 100
    df["ret_36t"] = close.pct_change(3 * TD_YEAR) * 100
    df["dd_tu_dinh"] = (close / close.cummax() - 1) * 100
    # RSI(14) kiểu Wilder
    d = close.diff()
    up = d.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
    df["rsi14"] = 100 - 100 / (1 + up / dn.replace(0, np.nan))
    return df


# ----------------------------------------------------------------------------
# 2. GARCH(1,1)
# ----------------------------------------------------------------------------
def garch(ret, maxiter=MAXITER):
    from arch import arch_model
    am = arch_model(ret, mean="Constant", vol="GARCH", p=1, q=1, dist="t")
    res = am.fit(disp="off", tol=1e-10, options={"maxiter": maxiter})
    cv = res.conditional_volatility * np.sqrt(TD_YEAR)          # %/năm
    pr = res.params
    out = dict(
        omega=float(pr["omega"]), alpha=float(pr["alpha[1]"]), beta=float(pr["beta[1]"]),
        nu=float(pr["nu"]), persistence=float(pr["alpha[1]"] + pr["beta[1]"]),
        vol_hien_tai_nam=float(cv.iloc[-1]),
        vol_trung_vi_nam=float(cv.median()),
        phan_vi_vol_hien_tai=float((cv <= cv.iloc[-1]).mean() * 100),
    )
    out["half_life_phien"] = float(np.log(0.5) / np.log(out["persistence"])) if out["persistence"] < 1 else None
    out["hoi_tu"] = bool(res.convergence_flag == 0)
    out["so_vong_lap"] = int(res.optimization_result.nit)
    return cv, out


# ----------------------------------------------------------------------------
# 3. MARKOV SWITCHING
# ----------------------------------------------------------------------------
def grad_khong_rang_buoc(mod, params):
    """Gradient log-likelihood theo tham số KHÔNG ràng buộc (sai phân trung tâm).
    Gradient theo tham số gốc bị thổi phồng khi xác suất chuyển gần 1 (thấy ~1e2 dù đã
    ở cực đại), nên chỉ dùng gradient này để xét hội tụ."""
    u = mod.untransform_params(params)
    g = np.zeros_like(u)
    for i in range(len(u)):
        h = 1e-5 * max(1.0, abs(u[i]))
        e = np.zeros_like(u); e[i] = h
        g[i] = (mod.loglike(u + e, transformed=False) - mod.loglike(u - e, transformed=False)) / (2 * h)
    return g


def fit_ms(ret, k, reps=20, seed=1, maxiter=MAXITER, n_luot=3):
    """Ước lượng MS(k) hai bước rồi tự kiểm tra hội tụ:
      1) n_luot lượt độc lập, mỗi lượt random search (reps điểm khởi đầu) + EM 200 vòng
         + BFGS tối đa maxiter vòng; giữ lượt có log-likelihood cao nhất. Một lượt đơn lẻ
         có thể kẹt ở cực đại địa phương suy biến (trạng thái σ ≈ 0, kéo dài 1–2 phiên);
      2) đánh bóng từ nghiệm bước 1 bằng BFGS gtol=GTOL; chưa đạt thì thử L-BFGS, rồi Nelder–Mead.
    Hội tụ = cờ của bộ tối ưu bật VÀ max|gradient không ràng buộc| < TOL_GRAD.
    statsmodels ≥ 0.15 dùng `rng` riêng cho random search (np.random.seed không có tác dụng),
    nên truyền rng có seed để kết quả tái lập được.
    Trả về (mod, res, info) với info = solver dùng, cờ hội tụ, gradient, llf."""
    import statsmodels.api as sm
    mod = sm.tsa.MarkovRegression(ret.values, k_regimes=k, trend="c", switching_variance=True)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")    # statsmodels tự bật lại ConvergenceWarning; ta tự kiểm tra
        best, llf_luot = None, []
        for luot in range(n_luot):
            try:
                res = mod.fit(search_reps=reps, em_iter=200, maxiter=maxiter, disp=False,
                              rng=np.random.default_rng([seed, luot]))
            except Exception:
                continue
            llf_luot.append(float(res.llf))
            if best is None or res.llf > best.llf:
                best = res
        if best is None:
            raise RuntimeError(f"MS({k}) không ước lượng được")
        g, solver = np.abs(grad_khong_rang_buoc(mod, best.params)).max(), "bfgs"
        for method, kw in (("bfgs", dict(gtol=GTOL)),
                           ("lbfgs", dict(pgtol=GTOL, factr=10)),
                           ("nm", dict(xtol=1e-10, ftol=1e-10))):
            if best.mle_retvals.get("converged") and g < TOL_GRAD:
                break
            try:
                cand = mod.fit(start_params=best.params, method=method, maxiter=maxiter,
                               em_iter=0, disp=False, **kw)
                gc = np.abs(grad_khong_rang_buoc(mod, cand.params)).max()
            except Exception:
                continue
            if cand.llf >= best.llf - 1e-6:
                best, g, solver = cand, gc, method
    info = dict(solver=solver, hoi_tu=bool(best.mle_retvals.get("converged") and g < TOL_GRAD),
                grad_max=float(g), llf=float(best.llf), llf_cac_luot=llf_luot)
    return mod, best, info


def tom_tat_ms(res, k, index):
    """Trích tham số, sắp xếp trạng thái theo trung bình giảm dần (0 = tốt nhất)."""
    p = res.params
    names = res.model.param_names
    mu = np.array([p[names.index(f"const[{i}]")] for i in range(k)])
    var = np.array([p[names.index(f"sigma2[{i}]")] for i in range(k)])
    P = res.regime_transition[:, :, 0].T if res.regime_transition.ndim == 3 else res.regime_transition.T
    # statsmodels: regime_transition[i, j] = P(S_t = i | S_{t-1} = j) -> chuyển vị để P[j, i]
    order = np.argsort(-mu)                                     # trạng thái tốt nhất trước
    mu, var = mu[order], var[order]
    P = P[np.ix_(order, order)]
    sm_p = np.asarray(res.smoothed_marginal_probabilities)[:, order]
    fl_p = np.asarray(res.filtered_marginal_probabilities)[:, order]
    dur = 1 / (1 - np.diag(P))
    erg = ergodic(P)
    mu_nam = mu * TD_YEAR
    sd_nam = np.sqrt(var * TD_YEAR)
    names_k = nhan_ms(mu_nam, sd_nam, k)
    rows = []
    for i in range(k):
        rows.append(dict(
            trang_thai=i, ten=names_k[i],
            mu_phien_pct=float(mu[i]), sd_phien_pct=float(np.sqrt(var[i])),
            mu_nam_pct=float(mu_nam[i]), sd_nam_pct=float(sd_nam[i]),
            p_duy_tri=float(P[i, i]), thoi_gian_ky_vong_phien=float(dur[i]),
            ty_trong_dai_han=float(erg[i]),
            ty_le_ngay_lam_tron=float((sm_p.argmax(1) == i).mean()),
        ))
    return dict(k=k, llf=float(res.llf), aic=float(res.aic), bic=float(res.bic),
                trang_thai=rows, P=P.tolist(),
                p_loc_hien_tai=fl_p[-1].tolist(), p_tron_hien_tai=sm_p[-1].tolist()), \
        pd.DataFrame(sm_p, index=index), pd.DataFrame(fl_p, index=index), order, mu, var, P


def ergodic(P):
    k = P.shape[0]
    A = np.vstack([P.T - np.eye(k), np.ones(k)])
    b = np.zeros(k + 1); b[-1] = 1
    return np.linalg.lstsq(A, b, rcond=None)[0]


def nhan_ms(mu_pct_nam, sd_pct_nam, k):
    """Đặt nhãn chế độ Markov chuyển phương sai theo cả kỳ vọng lẫn biến động."""
    if k == 2:
        return ["Tăng / Biến động thấp", "Giảm / Biến động cao"]
    if mu_pct_nam is not None and sd_pct_nam is not None and len(mu_pct_nam) == 3:
        if mu_pct_nam[1] > 10 and sd_pct_nam[1] < sd_pct_nam[0]:
            return ["Tăng – sôi động", "Tăng – êm (biến động thấp)", "Giảm/Hoảng loạn"]
    return ["Tăng", "Đi ngang", "Giảm/Hoảng loạn"]


# ----------------------------------------------------------------------------
# 4. CHẾ ĐỘ TỔNG HỢP (4 trạng thái) — quy tắc, không ước lượng
# ----------------------------------------------------------------------------
def che_do_tong_hop(df, cv):
    vol_med = cv.expanding(TD_YEAR).median()                   # trung vị mở rộng: không nhìn trước
    xu_huong_tang = (df["close"] > df["ma200"]) & (df["ma50"] > df["ma200"])
    xu_huong_giam = (df["close"] < df["ma200"]) & (df["ma50"] < df["ma200"])
    nhieu = cv > vol_med
    lab = pd.Series("Chuyển tiếp", index=df.index)
    lab[xu_huong_tang & ~nhieu] = "Tăng – êm"
    lab[xu_huong_tang & nhieu] = "Tăng – nhiễu"
    lab[xu_huong_giam & ~nhieu] = "Giảm – êm"
    lab[xu_huong_giam & nhieu] = "Giảm – nhiễu"
    lab[df["ma200"].isna() | vol_med.isna()] = np.nan
    return xac_nhan_nhan(lab, 5), vol_med


def xac_nhan_nhan(lab, k_days):
    """Bản phân loại của độ trễ xác nhận: nhãn mới chỉ được nhận khi giữ k phiên liên tiếp
    (chỉ dùng dữ liệu quá khứ, tránh nhãn nhấp nháy quanh ngưỡng)."""
    out = lab.copy()
    cur, cand, run = None, None, 0
    for i, v in enumerate(lab.values):
        if not isinstance(v, str):
            out.iloc[i] = np.nan
            continue
        if cur is None:
            cur = v
        if v == cur:
            cand, run = None, 0
        else:
            if v == cand:
                run += 1
            else:
                cand, run = v, 1
            if run >= k_days:
                cur, cand, run = v, None, 0
        out.iloc[i] = cur
    return out


# ----------------------------------------------------------------------------
# 5. WALK-FORWARD NGOÀI MẪU
# ----------------------------------------------------------------------------
def walk_forward_ms(ret, k=2, min_train=3 * TD_YEAR, refit_every=63, reps=8, maxiter=MAXITER):
    """P(trạng thái tốt nhất) LỌC tại t, chỉ dùng dữ liệu ≤ t và tham số ước
    lượng trên dữ liệu ≤ lần tái ước lượng gần nhất. Trả kèm chẩn đoán hội tụ từng lần."""
    import statsmodels.api as sm
    n = len(ret)
    p_good = pd.Series(np.nan, index=ret.index)
    starts = list(range(min_train, n, refit_every))
    chan_doan = []
    t0 = time.time()
    for j, s in enumerate(starts):
        e = min(s + refit_every, n)
        try:
            mod_tr, res_tr, info = fit_ms(ret.iloc[:s], k, reps=reps, seed=j, maxiter=maxiter)
        except Exception:
            chan_doan.append(dict(ngay=str(ret.index[s].date()), solver=None, hoi_tu=False))
            continue
        chan_doan.append(dict(ngay=str(ret.index[s].date()), **info))
        good = int(np.argmax([res_tr.params[res_tr.model.param_names.index(f"const[{i}]")] for i in range(k)]))
        mod_ext = sm.tsa.MarkovRegression(ret.iloc[:e].values, k_regimes=k, trend="c", switching_variance=True)
        fl = np.asarray(mod_ext.filter(res_tr.params).filtered_marginal_probabilities)
        p_good.iloc[s:e] = fl[s:e, good]
        if j % 8 == 0:
            print(f"   walk-forward {j + 1}/{len(starts)}  ({time.time() - t0:.0f}s)")
    return p_good, chan_doan


def tre_xac_nhan(sig, k_days):
    """Chỉ đổi vị thế khi tín hiệu mới giữ nguyên k phiên liên tiếp."""
    if k_days <= 1:
        return sig
    out = sig.copy()
    cur = sig.iloc[0]
    run = 0
    for i in range(len(sig)):
        v = sig.iloc[i]
        if np.isnan(v):
            out.iloc[i] = np.nan
            continue
        if np.isnan(cur):
            cur = v
        if v != cur:
            run += 1
            if run >= k_days:
                cur, run = v, 0
        else:
            run = 0
        out.iloc[i] = cur
    return out


def chay_chien_luoc(ret_pct, exposure, rf_nam, cost_bps):
    """exposure tại t áp cho lợi suất t+1. Tiền mặt hưởng rf.
    ret_pct là lợi suất LOG (%), phải đổi sang lợi suất đơn để tính lãi/lỗ."""
    r = np.expm1(ret_pct / 100)
    rf = (1 + rf_nam) ** (1 / TD_YEAR) - 1
    w = exposure.shift(1)
    turn = w.diff().abs().fillna(0)
    strat = w * r + (1 - w) * rf - turn * cost_bps / 1e4
    return strat.dropna(), w.dropna()


def chi_so_hieu_qua(r, rf_nam, w=None):
    rf = (1 + rf_nam) ** (1 / TD_YEAR) - 1
    eq = (1 + r).cumprod()
    yrs = len(r) / TD_YEAR
    cagr = eq.iloc[-1] ** (1 / yrs) - 1
    sd = r.std()
    vol = sd * np.sqrt(TD_YEAR)
    sharpe = (r - rf).mean() / sd * np.sqrt(TD_YEAR) if sd > 1e-12 else np.nan
    dd = (eq / eq.cummax() - 1).min()
    out = dict(CAGR_pct=cagr * 100, Vol_pct=vol * 100, Sharpe=sharpe,
               MaxDD_pct=dd * 100, Calmar=cagr / abs(dd) if dd < 0 else np.nan)
    if w is not None:
        out["Thoi_gian_trong_TT_pct"] = float((w > 0.5).mean() * 100)
        out["So_lan_doi_vi_the"] = int((w.diff().abs() > 0.5).sum())
    return out


def bootstrap_sharpe(r_s, r_b, rf_nam, n_boot=2000, block=20, seed=0):
    """Circular block bootstrap: H0 Sharpe(chiến lược) ≤ Sharpe(mua-và-giữ)."""
    rng = np.random.default_rng(seed)
    rf = (1 + rf_nam) ** (1 / TD_YEAR) - 1
    a = (r_s - rf).values
    b = (r_b - rf).values
    n = len(a)

    def sh(x):
        sd = x.std()
        return x.mean() / sd * np.sqrt(TD_YEAR) if sd > 1e-12 else 0.0

    obs = sh(a) - sh(b)
    nb = int(np.ceil(n / block))
    diffs = np.empty(n_boot)
    for i in range(n_boot):
        st = rng.integers(0, n, nb)
        ix = (st[:, None] + np.arange(block)[None, :]).ravel()[:n] % n
        diffs[i] = sh(a[ix]) - sh(b[ix])
    # p-value một phía: tỷ lệ bootstrap mà chênh lệch (đã dời tâm) vượt quan sát
    p = float(((diffs - diffs.mean()) >= obs).mean())
    lo, hi = np.percentile(diffs, [5, 95])
    return dict(chenh_sharpe=float(obs), ci90_thap=float(lo), ci90_cao=float(hi), p_mot_phia=p)


# ----------------------------------------------------------------------------
# 6. KỊCH BẢN CÓ XÁC SUẤT
# ----------------------------------------------------------------------------
def mo_phong_kich_ban(last_close, p_now, mu, var, P, horizons, n_sim=20000, seed=11, nu=6.0):
    """Mô phỏng Monte Carlo từ trạng thái hiện tại với nhiễu Student-t chuẩn hóa phương sai 1."""
    rng = np.random.default_rng(seed)
    k = len(mu)
    sd = np.sqrt(var)
    H = max(horizons)
    s = rng.choice(k, size=n_sim, p=np.asarray(p_now) / np.sum(p_now))
    cum = np.zeros(n_sim)
    out = {}
    cdf = np.cumsum(P, axis=1)
    nu_eff = max(float(nu), 4.0) if nu is not None and nu > 2.5 else None
    scale_t = np.sqrt(nu_eff / (nu_eff - 2.0)) if nu_eff is not None else 1.0
    for h in range(1, H + 1):
        u = rng.random(n_sim)
        s = (u[:, None] > cdf[s]).sum(1)
        s = np.minimum(s, k - 1)
        z = rng.standard_t(nu_eff, n_sim) / scale_t if nu_eff is not None else rng.standard_normal(n_sim)
        cum += mu[s] + sd[s] * z
        if h in horizons:
            lvl = last_close * np.exp(cum / 100)
            q = np.percentile(lvl, [5, 25, 50, 75, 95])
            dist_state = np.bincount(s, minlength=k) / n_sim
            out[h] = dict(
                p5=q[0], p25=q[1], p50=q[2], p75=q[3], p95=q[4],
                xs_duoi_1600=float((lvl < 1600).mean()), xs_tren_1800=float((lvl > 1800).mean()),
                xs_tren_hien_tai=float((lvl > last_close).mean()),
                pmf_trang_thai=dist_state.tolist(),
            )
    # Phân phối trạng thái giải tích (để đối chiếu mô phỏng)
    giai_tich = {h: (np.asarray(p_now) @ np.linalg.matrix_power(P, h)).tolist() for h in horizons}
    return out, giai_tich


# ----------------------------------------------------------------------------
# 7. BIỂU ĐỒ
# ----------------------------------------------------------------------------
C = dict(blue="#2a78d6", orange="#eb6834", aqua="#1baf7a", yellow="#eda100",
         violet="#6250d6", red="#e34948", ink="#0b0b0b", ink2="#52514e", grid="#e6e5e0")
REGIME_COLORS = {"Tăng – êm": "#2a78d6", "Tăng – nhiễu": "#1baf7a",
                 "Chuyển tiếp": "#bdbcb6", "Giảm – êm": "#eda100", "Giảm – nhiễu": "#eb6834"}


def _style(ax):
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    for sp in ("left", "bottom"):
        ax.spines[sp].set_color(C["grid"])
    ax.tick_params(colors=C["ink2"], labelsize=9)
    ax.grid(axis="y", color=C["grid"], lw=0.6)
    ax.set_axisbelow(True)


def ve_bieu_do(out_dir, df, lab, cv, sm2, sm3, k3_names, eq, scen, last_close, demo):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    plt.rcParams.update({"font.family": "DejaVu Sans", "figure.dpi": 150})
    tag = " (DỮ LIỆU GIẢ LẬP)" if demo else ""
    files = []

    # 1. Giá + chế độ tổng hợp
    fig, ax = plt.subplots(figsize=(11, 4.6))
    _style(ax)
    lv = lab.dropna()
    blocks = (lv != lv.shift()).cumsum()
    grp = [g for _, g in lv.groupby(blocks)]
    for i, g in enumerate(grp):
        end = grp[i + 1].index[0] if i + 1 < len(grp) else g.index[-1]
        ax.axvspan(g.index[0], end, color=REGIME_COLORS[g.iloc[0]], alpha=0.22, lw=0)
    ax.plot(df.index, df["close"], color=C["ink"], lw=1.1)
    ax.plot(df.index, df["ma200"], color=C["violet"], lw=1, ls="--")
    ax.set_yscale("log")
    from matplotlib.ticker import FuncFormatter, NullFormatter
    from matplotlib.ticker import LogLocator
    ax.yaxis.set_major_locator(LogLocator(base=10, subs=(1, 2, 5)))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax.yaxis.set_minor_formatter(NullFormatter())
    ax.set_title(f"VN-Index và chế độ thị trường tổng hợp (xu hướng × biến động){tag}",
                 loc="left", fontsize=11, color=C["ink"])
    hs = [Patch(color=v, alpha=0.4, label=k) for k, v in REGIME_COLORS.items()]
    hs += [plt.Line2D([], [], color=C["violet"], ls="--", label="MA200")]
    ax.legend(handles=hs, ncol=6, fontsize=8, frameon=False, loc="upper left")
    f = os.path.join(out_dir, "1_gia_va_che_do.png"); fig.tight_layout(); fig.savefig(f); plt.close(fig); files.append(f)

    # 2. Xác suất làm trơn MS(2)
    fig, ax = plt.subplots(figsize=(11, 3.2))
    _style(ax)
    ax.fill_between(sm2.index, sm2.iloc[:, 1], color=C["orange"], alpha=0.55, lw=0)
    ax.set_ylim(0, 1)
    ax.set_title(f"Xác suất (làm trơn) ở trạng thái Giảm — Markov 2 trạng thái{tag}",
                 loc="left", fontsize=11, color=C["ink"])
    f = os.path.join(out_dir, "2_xac_suat_ms2.png"); fig.tight_layout(); fig.savefig(f); plt.close(fig); files.append(f)

    # 3. MS(3) xếp chồng
    if sm3 is not None:
        fig, ax = plt.subplots(figsize=(11, 3.2))
        _style(ax)
        ax.stackplot(sm3.index, *[sm3.iloc[:, i] for i in range(sm3.shape[1])],
                     colors=[C["blue"], C["yellow"], C["orange"]][: sm3.shape[1]],
                     labels=k3_names, alpha=0.8, lw=0)
        ax.set_ylim(0, 1)
        ax.legend(ncol=3, fontsize=8, frameon=False, loc="upper left")
        ax.set_title(f"Xác suất (làm trơn) — Markov 3 trạng thái{tag}", loc="left", fontsize=11, color=C["ink"])
        f = os.path.join(out_dir, "3_xac_suat_ms3.png"); fig.tight_layout(); fig.savefig(f); plt.close(fig); files.append(f)

    # 4. GARCH vol
    fig, ax = plt.subplots(figsize=(11, 3.2))
    _style(ax)
    ax.plot(cv.index, cv, color=C["blue"], lw=1)
    ax.axhline(cv.median(), color=C["ink2"], lw=0.8, ls=":")
    ax.text(cv.index[5], cv.median() * 1.05, f"trung vị {cv.median():.0f}%", fontsize=8, color=C["ink2"])
    ax.set_title(f"Biến động có điều kiện GARCH(1,1), %/năm{tag}", loc="left", fontsize=11, color=C["ink"])
    f = os.path.join(out_dir, "4_garch_vol.png"); fig.tight_layout(); fig.savefig(f); plt.close(fig); files.append(f)

    # 5. Đường vốn walk-forward
    fig, ax = plt.subplots(figsize=(11, 4))
    _style(ax)
    cols = [C["ink"], C["violet"], C["blue"], C["aqua"]]
    for (name, s), c in zip(eq.items(), cols):
        ax.plot(s.index, s, lw=1.4 if name == "Mua và giữ" else 1.2, color=c, label=name)
    ax.set_yscale("log")
    from matplotlib.ticker import FuncFormatter, NullFormatter
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.1f}"))
    ax.yaxis.set_minor_formatter(NullFormatter())
    ax.legend(fontsize=8, frameon=False, loc="upper left")
    ax.set_title(f"Kiểm định ngoài mẫu (walk-forward): giá trị 1 đồng đầu tư{tag}",
                 loc="left", fontsize=11, color=C["ink"])
    f = os.path.join(out_dir, "5_walk_forward.png"); fig.tight_layout(); fig.savefig(f); plt.close(fig); files.append(f)

    # 6. Biểu đồ quạt kịch bản
    hs_ = sorted(scen.keys())
    fig, ax = plt.subplots(figsize=(8, 4))
    _style(ax)
    x = [0] + hs_
    for lo, hi, a in (("p5", "p95", 0.18), ("p25", "p75", 0.35)):
        ax.fill_between(x, [last_close] + [scen[h][lo] for h in hs_],
                        [last_close] + [scen[h][hi] for h in hs_], color=C["blue"], alpha=a, lw=0)
    ax.plot(x, [last_close] + [scen[h]["p50"] for h in hs_], color=C["blue"], lw=2, marker="o", ms=5)
    for h in hs_:
        ax.text(h, scen[h]["p95"], f"{scen[h]['p95']:,.0f}", fontsize=8, color=C["ink2"], ha="center", va="bottom")
        ax.text(h, scen[h]["p5"], f"{scen[h]['p5']:,.0f}", fontsize=8, color=C["ink2"], ha="center", va="top")
    ax.set_xlabel("Số phiên tới", fontsize=9, color=C["ink2"])
    ax.set_title(f"Kịch bản VN-Index từ mô phỏng Markov (dải 50% và 90%){tag}", loc="left",
                 fontsize=11, color=C["ink"])
    f = os.path.join(out_dir, "6_kich_ban.png"); fig.tight_layout(); fig.savefig(f); plt.close(fig); files.append(f)
    return files


# ----------------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------------
def main():
    try:  # Windows console (cp1252) không in được tiếng Việt
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--csv")
    g.add_argument("--vnstock", action="store_true")
    g.add_argument("--demo", action="store_true")
    ap.add_argument("--start", default="2010-01-01", help="ngày bắt đầu mẫu (mặc định 2010-01-01)")
    ap.add_argument("--rf", type=float, default=0.05, help="lãi suất tiền mặt/năm cho phần không đầu tư (mặc định 5%)")
    ap.add_argument("--cost_bps", type=float, default=15, help="chi phí mỗi lần đổi 100%% tỷ trọng, bps (mặc định 15)")
    ap.add_argument("--confirm", type=int, default=3, help="số phiên xác nhận trước khi đổi vị thế (mặc định 3)")
    ap.add_argument("--refit", type=int, default=63, help="tái ước lượng Markov mỗi N phiên (mặc định 63 ≈ 1 quý)")
    ap.add_argument("--maxiter", type=int, default=MAXITER, help=f"số vòng lặp tối đa của bộ tối ưu (mặc định {MAXITER})")
    ap.add_argument("--no_wf", action="store_true", help="bỏ qua walk-forward (chạy nhanh)")
    ap.add_argument("--out", default="ket_qua_regime")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    t_all = time.time()

    truth = None
    if a.demo:
        close, true_state, truth = gia_lap()
        nguon = "Giả lập 2 trạng thái (tham số đã biết)"
    elif a.csv:
        close = doc_csv(a.csv); nguon = f"CSV: {os.path.basename(a.csv)}"
    else:
        close = lay_vnstock(a.start); nguon = "vnstock (VNINDEX)"
    close = close[close.index >= pd.Timestamp(a.start) - pd.Timedelta(days=1200)]  # dư 3 năm cho MA/36T
    print(f"[1/7] Dữ liệu: {nguon} | {close.index[0].date()} → {close.index[-1].date()} | {len(close)} phiên")

    df = chi_bao_xu_huong(close)
    ret_all = np.log(close).diff() * 100
    est = ret_all[ret_all.index >= pd.Timestamp(a.start)].dropna()
    # Cắt biên ngày cực trị lỗi dữ liệu (|r| > 15% không thể có với biên độ HOSE 7%)
    bad = est.abs() > 15
    if bad.any():
        print(f"   Cảnh báo: {bad.sum()} phiên |lợi suất| > 15% — kiểm tra dữ liệu; đã loại khỏi ước lượng.")
        est = est[~bad]

    print("[2/7] GARCH(1,1)-t ...")
    cv, g_out = garch(est, a.maxiter)
    print(f"   hội tụ: {'có' if g_out['hoi_tu'] else 'KHÔNG'} sau {g_out['so_vong_lap']} vòng")

    print("[3/7] Markov switching 2 và 3 trạng thái ...")
    _, r2, hoi_tu2 = fit_ms(est, 2, maxiter=a.maxiter)
    ms2, sm2, fl2, _, mu2, var2, P2 = tom_tat_ms(r2, 2, est.index)
    ms2["hoi_tu"] = hoi_tu2
    try:
        _, r3, hoi_tu3 = fit_ms(est, 3, reps=40, maxiter=a.maxiter)
        ms3, sm3, fl3, _, mu3, var3, P3 = tom_tat_ms(r3, 3, est.index)
        ms3["hoi_tu"] = hoi_tu3
    except Exception as e:
        print(f"   MS(3) lỗi: {e}"); ms3 = sm3 = None
    for ms in (ms2, ms3):
        if ms:
            h = ms["hoi_tu"]
            print(f"   MS({ms['k']}): hội tụ {'có' if h['hoi_tu'] else 'KHÔNG'} · solver {h['solver']} · "
                  f"max|gradient| {h['grad_max']:.1e} · llf {h['llf']:.4f}")
    k3_names = [r["ten"] for r in ms3["trang_thai"]] if ms3 else nhan_ms(None, None, 3)
    # Quy tắc chọn: chỉ nhận MS(3) khi BIC tốt hơn rõ rệt (> 10 điểm) VÀ mọi trạng thái
    # kéo dài ≥ 5 phiên. Lý do: lợi suất đuôi dày khiến MS(3) hay "bắt" vài phiên
    # cực trị thành một trạng thái riêng chỉ kéo dài 1–2 phiên (đã thấy khi chạy giả lập).
    ok3 = (ms3 is not None and ms3["bic"] < ms2["bic"] - 10
           and min(r["thoi_gian_ky_vong_phien"] for r in ms3["trang_thai"]) >= 5)
    chon = ms3 if ok3 else ms2
    print(f"   BIC: MS2={ms2['bic']:.1f}" + (f"  MS3={ms3['bic']:.1f}" if ms3 else "") + f" → chọn MS({chon['k']})")

    print("[4/7] Chế độ tổng hợp (xu hướng × biến động) ...")
    df = df.loc[est.index]
    lab, vol_med = che_do_tong_hop(df, cv)
    phan_bo = lab.value_counts(normalize=True).mul(100).round(1).to_dict()
    # Lợi suất 20 phiên kế tiếp theo từng chế độ (mô tả, trong mẫu)
    fwd20 = (np.log(close).shift(-20) - np.log(close)).reindex(est.index) * 100
    theo_che_do = pd.DataFrame({"che_do": lab, "fwd20": fwd20, "r1": est.shift(-1)}).dropna()
    bang_che_do = theo_che_do.groupby("che_do").agg(
        so_phien=("fwd20", "size"),
        loi_suat_20p_tb_pct=("fwd20", "mean"),
        xs_20p_duong_pct=("fwd20", lambda x: (x > 0).mean() * 100),
        vol_nam_pct=("r1", lambda x: x.std() * np.sqrt(TD_YEAR)),
    ).round(2)

    print("[5/7] Walk-forward ngoài mẫu ...")
    wf = {}
    if not a.no_wf:
        p_good, wf_chan_doan = walk_forward_ms(est, 2, refit_every=a.refit, maxiter=a.maxiter)
        so_hoi_tu = sum(d["hoi_tu"] for d in wf_chan_doan)
        print(f"   hội tụ {so_hoi_tu}/{len(wf_chan_doan)} lần tái ước lượng")
        start_oos = p_good.first_valid_index()
        r_oos = est.loc[start_oos:]
        bh = pd.Series(1.0, index=r_oos.index)
        trend = ((df["close"] > df["ma200"]).astype(float)).loc[start_oos:]
        msig = (p_good.loc[start_oos:] > 0.5).astype(float)
        comp = ((df["close"] > df["ma200"]) & (p_good > 0.5)).astype(float).loc[start_oos:]
        sigs = {"Mua và giữ": bh,
                "Lọc MA200": tre_xac_nhan(trend, a.confirm),
                "Lọc Markov (P tăng > 50%)": tre_xac_nhan(msig, a.confirm),
                "Tổng hợp (MA200 và Markov)": tre_xac_nhan(comp, a.confirm)}
        rows, eq = {}, {}
        r_bh, _ = chay_chien_luoc(r_oos, bh, a.rf, 0)
        for name, sgl in sigs.items():
            rs, w = chay_chien_luoc(r_oos, sgl, a.rf, 0 if name == "Mua và giữ" else a.cost_bps)
            m = chi_so_hieu_qua(rs, a.rf, None if name == "Mua và giữ" else w)
            if name != "Mua và giữ":
                m.update(bootstrap_sharpe(rs, r_bh.loc[rs.index], a.rf))
            rows[name] = m
            eq[name] = (1 + rs).cumprod()
        wf = dict(bat_dau_ngoai_mau=str(start_oos.date()), ket_qua=rows,
                  p_tang_loc_ngoai_mau_hien_tai=float(p_good.iloc[-1]),
                  so_lan_uoc_luong=len(wf_chan_doan), so_lan_hoi_tu=so_hoi_tu,
                  chan_doan_hoi_tu=wf_chan_doan)
    else:
        eq = {"Mua và giữ": (1 + np.expm1(est / 100)).cumprod()}

    print("[6/7] Kịch bản Monte Carlo ...")
    last = float(close.iloc[-1])
    horizons = [7, 21, 63]
    base = ms2 if chon["k"] == 2 else ms3
    mu_b, var_b, P_b = (mu2, var2, P2) if chon["k"] == 2 else (mu3, var3, P3)
    scen, scen_giai_tich = mo_phong_kich_ban(
        last, base["p_loc_hien_tai"], mu_b, var_b, P_b, horizons, nu=g_out.get("nu", 6.0)
    )

    print("[7/7] Ghi kết quả ...")
    files = ve_bieu_do(a.out, df, lab, cv, sm2, sm3, k3_names, eq, scen, last, a.demo)

    hien_tai = df.iloc[-1]
    snap = dict(
        ngay=str(df.index[-1].date()), close=last,
        ma20=float(hien_tai["ma20"]), ma50=float(hien_tai["ma50"]), ma200=float(hien_tai["ma200"]),
        doc_ma200_20p_pct=float(hien_tai["doc_ma200_20p"]), rsi14=float(hien_tai["rsi14"]),
        ret_12t_pct=float(hien_tai["ret_12t"]), ret_36t_pct=float(hien_tai["ret_36t"]),
        dd_tu_dinh_pct=float(hien_tai["dd_tu_dinh"]),
        cong_momentum_36t="Up" if hien_tai["ret_36t"] > 0 else "Down",
        che_do_tong_hop=str(lab.iloc[-1]),
        vol_garch_nam=g_out["vol_hien_tai_nam"], vol_trung_vi_mo_rong=float(vol_med.iloc[-1]),
    )
    summary = dict(nguon=nguon, mau=[str(est.index[0].date()), str(est.index[-1].date())], so_phien=len(est),
                   tham_so=dict(rf=a.rf, cost_bps=a.cost_bps, confirm=a.confirm, refit=a.refit,
                                maxiter=a.maxiter, gtol=GTOL, tol_grad=TOL_GRAD),
                   hien_tai=snap, garch=g_out, ms2=ms2, ms3=ms3, bic_chon=chon["k"],
                   phan_bo_che_do_pct=phan_bo, bang_che_do=bang_che_do.reset_index().to_dict("records"),
                   walk_forward=wf, kich_ban={str(h): v for h, v in scen.items()},
                   kich_ban_trang_thai_giai_tich={str(h): v for h, v in scen_giai_tich.items()},
                   gia_lap_tham_so_that=truth)

    def _clean(o):
        if isinstance(o, dict):
            return {str(k): _clean(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [_clean(v) for v in o]
        if isinstance(o, (np.floating, float)):
            if np.isnan(o):
                return None
            val = float(o)
            return float(f"{val:.6g}") if 0 < abs(val) < 1e-4 else round(val, 6)
        if isinstance(o, np.integer):
            return int(o)
        return o

    with open(os.path.join(a.out, "tom_tat.json"), "w", encoding="utf-8") as f:
        json.dump(_clean(summary), f, ensure_ascii=False, indent=2)

    # Excel
    with pd.ExcelWriter(os.path.join(a.out, "regime_ket_qua.xlsx")) as xw:
        pd.DataFrame([snap]).T.rename(columns={0: "giá trị"}).to_excel(xw, sheet_name="Hien_tai")
        for nm, ms in (("MS2", ms2), ("MS3", ms3)):
            if ms:
                pd.DataFrame(ms["trang_thai"]).to_excel(xw, sheet_name=nm, index=False)
                pd.DataFrame(ms["P"]).to_excel(xw, sheet_name=nm + "_ma_tran_P")
        pd.DataFrame([g_out]).T.to_excel(xw, sheet_name="GARCH")
        bang_che_do.to_excel(xw, sheet_name="Theo_che_do")
        if wf:
            pd.DataFrame(wf["ket_qua"]).T.to_excel(xw, sheet_name="Walk_forward")
        pd.DataFrame(scen).T.drop(columns="pmf_trang_thai").to_excel(xw, sheet_name="Kich_ban")
        daily = pd.DataFrame({"close": df["close"], "ma50": df["ma50"], "ma200": df["ma200"],
                              "vol_garch": cv, "che_do": lab, "p_giam_ms2_tron": sm2.iloc[:, 1],
                              "p_giam_ms2_loc": fl2.iloc[:, 1]})
        daily.to_excel(xw, sheet_name="Chuoi_ngay")

    # Markdown tóm tắt
    L = [f"# Tóm tắt chế độ thị trường — {snap['ngay']}", f"Nguồn: {nguon} · mẫu {est.index[0].date()} → {est.index[-1].date()} ({len(est)} phiên)", ""]
    L += [f"- Đóng cửa {last:,.2f} · MA50 {snap['ma50']:,.1f} · MA200 {snap['ma200']:,.1f} · RSI14 {snap['rsi14']:.0f}",
          f"- Chế độ tổng hợp: **{snap['che_do_tong_hop']}** · cổng 36 tháng: **{snap['cong_momentum_36t']}** ({snap['ret_36t_pct']:+.1f}%)",
          f"- GARCH: vol hiện tại {g_out['vol_hien_tai_nam']:.1f}%/năm, phân vị {g_out['phan_vi_vol_hien_tai']:.0f}, α+β = {g_out['persistence']:.3f}",
          ""]
    for ms in (ms2, ms3):
        if not ms:
            continue
        L.append(f"## Markov {ms['k']} trạng thái (BIC {ms['bic']:.1f})")
        L.append("| Trạng thái | μ %/năm | σ %/năm | p duy trì | thời gian kỳ vọng (phiên) | P lọc hiện tại |")
        L.append("|---|---|---|---|---|---|")
        for i, row in enumerate(ms["trang_thai"]):
            ten_tt = row.get("ten") or nhan_ms(None, None, ms["k"])[i]
            L.append(f"| {ten_tt} | {row['mu_nam_pct']:+.1f} | {row['sd_nam_pct']:.1f} | {row['p_duy_tri']:.4f} | {row['thoi_gian_ky_vong_phien']:.1f} | {ms['p_loc_hien_tai'][i]:.0%} |")
        L.append("")
    if snap["close"] < snap["ma200"]:
        L.append("> **Lưu ý diễn giải:** Mô hình Markov chuyển phương sai trên lợi suất ngày phân tách chủ yếu theo "
                 "**chế độ biến động** (σ thấp vs σ cao). Khi thị trường điều chỉnh/giảm chậm với biên độ ngày nhỏ "
                 f"(**{snap['che_do_tong_hop']}**, vol GARCH ở phân vị {g_out['phan_vi_vol_hien_tai']:.0f}), xác suất lọc "
                 "vẫn nghiêng về trạng thái biến động thấp dù xu hướng giá đang dưới MA200. Do đó quy tắc vận hành "
                 "kết hợp cả bộ lọc xu hướng MA200 lẫn Markov.")
        L.append("")
    if wf:
        L.append(f"## Walk-forward ngoài mẫu (từ {wf['bat_dau_ngoai_mau']}, chi phí {a.cost_bps:.0f} bps, xác nhận {a.confirm} phiên)")
        L.append("| Chiến lược | CAGR % | Vol % | Sharpe | MaxDD % | Δ Sharpe vs B&H | p |")
        L.append("|---|---|---|---|---|---|---|")
        for nm, m in wf["ket_qua"].items():
            L.append(f"| {nm} | {m['CAGR_pct']:.1f} | {m['Vol_pct']:.1f} | {m['Sharpe']:.2f} | {m['MaxDD_pct']:.1f} | "
                     f"{m.get('chenh_sharpe', 0):+.2f} | {m.get('p_mot_phia', float('nan')):.2f} |")
        L.append("")
    L.append("## Kịch bản (Monte Carlo từ mô hình Markov được chọn)")
    L.append("| Phiên tới | P5 | P25 | Trung vị | P75 | P95 | P(< 1.600) | P(> 1.800) |")
    L.append("|---|---|---|---|---|---|---|---|")
    for h, v in scen.items():
        L.append(f"| {h} | {v['p5']:,.0f} | {v['p25']:,.0f} | {v['p50']:,.0f} | {v['p75']:,.0f} | {v['p95']:,.0f} | {v['xs_duoi_1600']:.0%} | {v['xs_tren_1800']:.0%} |")
    L += ["", f"## Kiểm tra hội tụ (tối đa {a.maxiter} vòng lặp, đạt khi max|gradient không ràng buộc| < {TOL_GRAD:g})",
          "| Mô hình | Hội tụ | Solver | max\\|gradient\\| | log-likelihood |", "|---|---|---|---|---|",
          f"| GARCH(1,1)-t | {'có' if g_out['hoi_tu'] else 'KHÔNG'} | SLSQP ({g_out['so_vong_lap']} vòng) | – | – |"]
    for ms in (ms2, ms3):
        if ms:
            h = ms["hoi_tu"]
            L.append(f"| Markov {ms['k']} trạng thái | {'có' if h['hoi_tu'] else 'KHÔNG'} | {h['solver']} | "
                     f"{h['grad_max']:.1e} | {h['llf']:.4f} |")
    if wf:
        L.append(f"| Walk-forward MS(2) | {wf['so_lan_hoi_tu']}/{wf['so_lan_uoc_luong']} lần | – | – | – |")
    if truth:
        L += ["", "## Kiểm tra trên dữ liệu giả lập",
              f"Tham số thật: p_tăng={truth['p_tang']}, p_giảm={truth['p_giam']}, μ={truth['mu']} %/phiên, σ={truth['sd']} %/phiên"]
    with open(os.path.join(a.out, "tom_tat.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    print(f"Xong sau {time.time() - t_all:.0f}s → {os.path.abspath(a.out)}")
    print("\n".join(L))


if __name__ == "__main__":
    main()
