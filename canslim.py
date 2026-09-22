"""
canslim.py — Buoc 3a: cham CANSLIM tai MOT ngay, chi dung du lieu da biet tai ngay do.

Dung chung cho cham hien tai (python canslim.py) va canslim_backtest.py — luat chay
that phai trung voi luat da kiem dinh (quyet dinh 22/09/2026).

Moi chu tra ve True / False / None. None = KHONG DO DUOC (thieu du lieu) va duoc
tinh la KHONG QUA — thieu du lieu khong bao gio tu dong thanh "dat".

Chay:  python canslim.py [YYYY-MM-DD]
  -> data/canslim_YYYYMMDD.json + data/canslim_YYYYMMDD.md
     cho cac ma trong tham_dinh.json + candidates moi nhat.
"""

import datetime as dt
import glob
import json
import os
import sys

import numpy as np
import pandas as pd

import canslim_data as cd
from lt_config import CANSLIM as CF, CANSLIM_CHAN_MUA
from ranking import pct_rank


# ------------------------------------------------------------------ Co ban (C, A, V3)
def _lnst(r):
    v = r.get("isa22")
    return v if v is not None else r.get("isa20")


def _doanh_thu(r):
    """Ngan hang: thu nhap lai thuan (isb27). Con lai: doanh thu thuan (isa3)."""
    b = r.get("isb27")
    return b if b not in (None, 0) else r.get("isa3")


def la_ngan_hang(quy):
    return any(r.get("isb27") not in (None, 0) for r in quy[-4:])


def _yoy(a, b):
    if a is None or b is None or b <= 0:
        return None
    return a / b - 1


def co_ban(quy, nam, ngay):
    """Chi so co ban da biet tai `ngay` (ngay_hieu_luc <= ngay)."""
    quy = [r for r in quy if r["hl"] <= ngay]      # chi nhung ky DA cong bo
    biet = {(r["nam"], r["quy"]): r for r in quy}
    out = dict(ky=None, lnst_yoy=None, dt_yoy=None, cagr3=None, khong_giam=None,
               roe=None, v3=None, C=None, A=None)
    if not biet:
        return out
    ky = max(biet)
    out["ky"] = f"Q{ky[1]}/{ky[0]}"

    def lui(k, n):                           # lui n quy
        y, q = k
        idx = y * 4 + (q - 1) - n
        return (idx // 4, idx % 4 + 1)

    cur, prev = biet.get(ky), biet.get(lui(ky, 4))
    if prev:
        out["lnst_yoy"] = _yoy(_lnst(cur), _lnst(prev))
        out["dt_yoy"] = _yoy(_doanh_thu(cur), _doanh_thu(prev))
    if out["lnst_yoy"] is not None and out["dt_yoy"] is not None:
        out["C"] = (out["lnst_yoy"] >= CF["c_lnst_yoy_min"]
                    and out["dt_yoy"] >= CF["c_doanh_thu_yoy_min"])
    elif prev is not None and _lnst(prev) is not None and _lnst(prev) <= 0:
        out["C"] = False                     # quy truoc lo: % tang khong co nghia

    def ttm(k):
        rs = [biet.get(lui(k, n)) for n in range(4)]
        vals = [_lnst(r) if r else None for r in rs]
        return None if any(v is None for v in vals) else sum(vals)

    t = [ttm(lui(ky, 4 * n)) for n in range(4)]          # t0 (nay) .. t3 (3 nam truoc)
    if all(v is not None for v in t):
        if all(v > 0 for v in t):
            out["khong_giam"] = t[0] >= t[1] >= t[2] >= t[3]   # "khong nam nao giam"
            out["cagr3"] = (t[0] / t[3]) ** (1 / 3) - 1
        else:
            out["khong_giam"] = False
            out["cagr3"] = None
        eq = [biet.get(ky, {}).get("bsa78"), (biet.get(lui(ky, 4)) or {}).get("bsa78")]
        if t[0] is not None and all(e not in (None, 0) for e in eq):
            out["roe"] = t[0] / (sum(eq) / 2)
        if out["khong_giam"] is False:
            out["A"] = False
        elif out["cagr3"] is not None and out["roe"] is not None:
            out["A"] = (out["khong_giam"] and out["cagr3"] >= CF["a_cagr_3n_min"]
                        and out["roe"] >= CF["a_roe_min"])

    # V3 (co canh bao Buoc 3b): 3 nam tai chinh gan nhat DA CONG BO, khong ap ngan hang
    if not la_ngan_hang(quy):
        ns = [r for r in nam if r["hl"] <= ngay][-3:]
        if len(ns) == 3 and all(r.get("cfa18") is not None and r.get("isa20") is not None
                                for r in ns):
            lnst3 = sum(r["isa20"] for r in ns)
            cfo3 = sum(r["cfa18"] for r in ns)
            out["v3"] = cfo3 / lnst3 if lnst3 > 0 else float("-inf") if cfo3 < 0 else None
    return out


# ------------------------------------------------------------------ Gia (N, S, L, M)
def khung_gia(ds_ma):
    """-> DataFrame c, h, v (index ngay, cot ma), theo lich phien cua VNINDEX."""
    bench = cd.nap_gia("VNINDEX")
    lich = pd.Index(bench["d"], name="ngay")
    c, h, lo, v = {}, {}, {}, {}
    for ma in ["VNINDEX"] + list(ds_ma):
        g = bench if ma == "VNINDEX" else cd.nap_gia(ma)
        if not g:
            continue
        idx = pd.Index(g["d"])
        c[ma] = pd.Series(g["c"], idx).groupby(level=0).last()
        h[ma] = pd.Series(g["h"], idx).groupby(level=0).last()
        lo[ma] = pd.Series(g["l"], idx).groupby(level=0).last()
        v[ma] = pd.Series(g["v"], idx).groupby(level=0).last()
    f = lambda d: pd.DataFrame(d).reindex(lich)
    return f(c), f(h), f(lo), f(v)


def vi_tri_ngay(lich, ngay, method="pad"):
    """Chi so phien cho `ngay` tren lich phien. KHONG BAO GIO tra -1: get_indexer tra -1
    khi ngay nam ngoai lich, va -1 lai la phien CUOI — tuc lang le dung du lieu tuong lai
    (phan xet Codex luc dung). Ngoai lich -> bao loi."""
    i = lich.get_indexer([ngay], method=method)[0]
    if i < 0:
        raise ValueError(f"{ngay} nam ngoai lich du lieu {lich[0]} .. {lich[-1]}")
    return int(i)


def chi_bao(C, H, Lo, V):
    """Chi bao ky thuat moi phien. Tra ve dict DataFrame cung shape voi C."""
    ret = C.pct_change(fill_method=None)
    up = (ret > 0).astype(float).where(ret.notna())
    dn = (ret < 0).astype(float).where(ret.notna())
    n = CF["s_so_phien"]
    # S: cua so 50 phien DAY DU; khong doi rieng so phien tang/giam (Codex #11)
    kl_up = (V * up).rolling(n, min_periods=n).sum() / up.rolling(n, min_periods=n).sum()
    kl_dn = (V * dn).rolling(n, min_periods=n).sum() / dn.rolling(n, min_periods=n).sum()
    pc = C.shift(1)
    tr = pd.concat([H - Lo, (H - pc).abs(), (Lo - pc).abs()]).groupby(level=0).max()
    tr = tr.reindex(C.index)
    return dict(
        ma50=C.rolling(50, min_periods=50).mean(),
        ma200=C.rolling(200, min_periods=200).mean(),
        dinh252=H.rolling(252, min_periods=200).max(),
        r252s=C.shift(21) / C.shift(252) - 1,
        r126=C / C.shift(126) - 1,
        r63=C / C.shift(63) - 1,
        s_ratio=kl_up / kl_dn,
        tov20=(C * V).rolling(20, min_periods=15).mean(),
        atr=tr.rolling(14, min_periods=14).mean() / C,        # ATR14 / gia, nhu ban quet
    )


def trend_r2(c, n=126):
    y = np.log(np.asarray(c[-n:], float))
    y = y[np.isfinite(y)]
    if len(y) < 20:
        return None
    x = np.arange(len(y))
    r = np.corrcoef(x, y)[0, 1]
    return float(np.sign(r) * r * r)


def cham_ngay(i, ds_ma, C, K, fund):
    """Cham CANSLIM toan ro tai phien thu i. fund[ma] = (quy, nam) da nap.

    Tra ve dict ma -> dong ket qua; kem '_M' cho trang thai thi truong.
    """
    ngay = C.index[i]
    b = "VNINDEX"
    M = bool(C[b].iat[i] > K["ma200"][b].iat[i] and K["ma50"][b].iat[i] > K["ma200"][b].iat[i]) \
        if pd.notna(K["ma200"][b].iat[i]) else None
    rs = {}
    for ma in ds_ma:
        if ma not in C:
            continue
        a, ib = K["r252s"][ma].iat[i], K["r252s"][b].iat[i]
        rs[ma] = float(a - ib) if pd.notna(a) and pd.notna(ib) else None
    ma_list = list(rs)
    pr = dict(zip(ma_list, pct_rank([rs[m] for m in ma_list])))
    out = {"_M": M}
    for ma in ma_list:
        c = C[ma].iat[i]
        if pd.isna(c):
            continue
        dinh, s = K["dinh252"][ma].iat[i], K["s_ratio"][ma].iat[i]
        N = bool(c >= (1 - CF["n_cach_dinh_max"]) * dinh) if pd.notna(dinh) else None
        S = bool(s >= CF["s_ty_le_kl_min"]) if pd.notna(s) else None
        L = bool(pr[ma] >= CF["l_phan_vi_min"]) if rs[ma] is not None else None
        fb = co_ban(*fund.get(ma, ([], [])), ngay)
        row = dict(ma=ma, M=M, C=fb["C"], A=fb["A"], N=N, S=S, L=L,
                   cach_dinh=float(1 - c / dinh) if pd.notna(dinh) else None,
                   s_ratio=float(s) if pd.notna(s) else None,
                   rs12=rs[ma], pv_rs12=pr[ma] if rs[ma] is not None else None,
                   **{k: fb[k] for k in ("ky", "lnst_yoy", "dt_yoy", "cagr3",
                                          "khong_giam", "roe", "v3")})
        row.update(ket_luan(row))
        out[ma] = row
    return out


def ket_luan(r):
    q = lambda k: r.get(k) is True
    nsl = sum(q(k) for k in ("N", "S", "L"))
    chinh = q("M") and q("C") and q("A") and nsl >= CF["diem_nsl_min"]
    doi_chung = all(q(k) for k in ("M", "C", "A", "N", "S", "L"))
    v3 = r.get("v3")
    return dict(diem_nsl=nsl, qua_3a=chinh, qua_3a_doi_chung=doi_chung,
                co_v3=(v3 is not None and v3 < CF["v3_nguong"]))


# ------------------------------------------------------------------ Cham hien tai
def _ky_hieu(v):
    return {True: "Y", False: "-", None: "?"}[v]


def _so(v):
    return "—" if v is None else f"{v:.2f}"


def _pct(v):
    return "—" if v is None else ("−∞" if v == float("-inf") else f"{v*100:+.0f}%")


def main():
    ngay = dt.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else None
    with open(os.path.join("data", "tham_dinh.json"), encoding="utf-8") as f:
        td = [k for k in json.load(f) if not k.startswith("_")]
    cand_f = sorted(glob.glob(os.path.join("data", "candidates_2*.json")))[-1]
    with open(cand_f, encoding="utf-8") as f:
        cand = [r["ma"] for r in json.load(f)]
    ro = cd.ro_ma()
    ro = [m for m in ro if m != "VNINDEX"]
    C, H, Lo, V = khung_gia(ro)
    K = chi_bao(C, H, Lo, V)
    i = len(C.index) - 1 if ngay is None else vi_tri_ngay(C.index, ngay)
    ngay = C.index[i]
    fund = {m: cd.nap_bctc(m) for m in ro}
    kq = cham_ngay(i, ro, C, K, fund)
    chon = [m for m in dict.fromkeys(td + cand) if m in kq]
    rows = [kq[m] for m in chon]
    for r in rows:
        r["nguon"] = ("tham_dinh" if r["ma"] in td else "") + \
                     ("+candidates" if r["ma"] in cand else "")
    tag = ngay.strftime("%Y%m%d")
    out = {"_meta": dict(ngay_du_lieu=str(ngay), sinh_luc=str(dt.date.today()),
                         M=kq["_M"], CANSLIM_CHAN_MUA=CANSLIM_CHAN_MUA, nguong=CF,
                         candidates=os.path.basename(cand_f),
                         ghi_chu="May cham, KHONG phai ket luan nguoi. I bo khoi luat may. "
                                 "co_v3 = canh bao cho phieu 3b, khong chan mua."),
           "ma": rows,
           # Toan ro, ban gon — lt_screener.py doc phan nay cho moi ma qua bo loc cung.
           "toan_ro": {m: {k: v[k] for k in ("C", "A", "N", "S", "L", "M", "qua_3a",
                                             "qua_3a_doi_chung", "co_v3")}
                       for m, v in kq.items() if not m.startswith("_")}}
    pj = os.path.join("data", f"canslim_{tag}.json")
    with open(pj, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1, default=str)

    md = [f"# Chấm CANSLIM (Bước 3a) — dữ liệu {ngay:%d/%m/%Y}", "",
          f"M (VNINDEX > MA200 và MA50 > MA200): **{_ky_hieu(kq['_M'])}** · "
          f"công tắc `CANSLIM_CHAN_MUA = {CANSLIM_CHAN_MUA}` "
          f"({'chặn lệnh' if CANSLIM_CHAN_MUA else 'chỉ chấm và ghi sổ, không chặn lệnh'})", "",
          "Y = qua · - = không qua · ? = không đo được (tính là không qua). "
          "I bỏ khỏi luật máy.", "",
          "| Mã | Kỳ BCTC | C | A | N | S | L | M | 3a chính | 3a đối chứng | LNST q/q-4 | DT q/q-4 | "
          "CAGR 3N | ROE | Cách đỉnh | RS12 pv | V3 | Nguồn |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        md.append(
            f"| {r['ma']} | {r['ky'] or '—'} | {_ky_hieu(r['C'])} | {_ky_hieu(r['A'])} | "
            f"{_ky_hieu(r['N'])} | {_ky_hieu(r['S'])} | {_ky_hieu(r['L'])} | {_ky_hieu(r['M'])} | "
            f"**{'QUA' if r['qua_3a'] else 'không'}** | {'QUA' if r['qua_3a_doi_chung'] else 'không'} | "
            f"{_pct(r['lnst_yoy'])} | {_pct(r['dt_yoy'])} | {_pct(r['cagr3'])} | {_pct(r['roe'])} | "
            f"{_pct(r['cach_dinh'])} | {_so(r['pv_rs12'])} | "
            f"{_pct(r['v3'])}{' ⚠' if r['co_v3'] else ''} | {r['nguon']} |")
    md += ["", "⚠ ở cột V3 = dòng tiền HĐKD 3 năm < 50% LNST 3 năm: cờ để người lập phiếu 3b "
           "ưu tiên xem, **không** phải kết luận V3 chính thức. Ngân hàng không áp V3 (—)."]
    pm = os.path.join("data", f"canslim_{tag}.md")
    with open(pm, "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    print("\n".join(md))
    print(f"\n-> {pj}\n-> {pm}")


if __name__ == "__main__":
    main()
