"""
canslim_backtest.py — Phep do dang ky truoc cho Buoc 3a CANSLIM (chot 22/09/2026).

P1 (phep so sanh chinh): he thong dang chay (B1 cua muc 8: bo loc cung -> xep hang
trong ro da loc -> bon luat thoat, 1/ATR, bien khong giao dich 3%, phi 0,4%/vong)
  CO   Buoc 3a: chi MUA MOI ma qua 3a (M sai -> khong mua moi)
  KHONG Buoc 3a: = B1
Chi so chinh: chenh lech loi suat thang (co 3a - khong 3a), t Newey-West, 4 pha luoi.
Nguong: CHAP NHAN khi >= 3/4 pha duong VA t >= 2 VA sut giam khong te hon qua 3 diem %;
        CHUA KET LUAN khi 1 <= t < 2; BAC BO khi t < 1.

Nhanh phu: doi chung (ca 6 chu), 3a + co V3, tung chu rieng le (loi suat 3 thang ke tiep).
Buoc 3b (V1-V5, phieu nguoi) KHONG backtest duoc -> ca hai phien ban deu bo qua.

Khac biet da biet so voi lt_backtest_scope.js (ghi trong bao cao):
  - buoc ngay (21 phien) thay vi 4 tuan; MA200/MA50 phien thay MA10/MA3 thang
  - co them loc thanh khoan >= 10 ty va ATR <= 6% (dung Tang 1 dang chay)
  - ATR14 true range; khong co tran nganh, khong co chan -25%
  - tin hieu dong cua phien a, khop lenh dong cua phien a+1; sut giam do theo ngay
  - "chi MUA MOI phai qua 3a": ma dang giu van duoc tang ty trong ma khong hoi 3a
Thien lech song sot: ro = ma dang niem yet hom nay -> ket qua lac quan hon thuc te.
BCTC la ban moi nhat (co the da dieu chinh hoi to) — khong co ban cong bo lan dau.
Phan xet doi khang (Codex, 22/09/2026): 15 diem; da sua #2 #3 #4 #7 #8 #9 #11-#14.

Chay: python canslim_backtest.py  -> data/canslim_backtest_20260922.json + in bang
"""

import datetime as dt
import json
import os

import numpy as np
import pandas as pd

import canslim as cs
import canslim_data as cd
from lt_config import LOC
from ranking import pct_rank

BUOC = 21                     # phien giua hai ky ra soat (~1 thang)
PHA = (0, 5, 10, 15)          # 4 pha luoi, lech nhau 1 tuan (nhu muc 8)
N_O, TRAN = 8, 0.20           # DM2 — cau hinh chinh da chot o cau hoi 6
PHI = 0.004
TRE, BIEN = 0.40, 0.03
W = {"rs12": 0.4, "rs6": 0.3, "rs3": 0.2, "q": 0.1}


def nw_t(x, lag=None):
    """t-stat cua trung binh voi sai so chuan Newey-West (Bartlett)."""
    x = np.asarray([v for v in x if v is not None and np.isfinite(v)], float)
    n = len(x)
    if n < 6:
        return None, n
    lag = lag if lag is not None else int(np.floor(4 * (n / 100) ** (2 / 9)))
    e = x - x.mean()
    s = e @ e / n
    for k in range(1, lag + 1):
        s += 2 * (1 - k / (lag + 1)) * (e[k:] @ e[:-k]) / n
    se = np.sqrt(s / n)
    return (float(x.mean() / se) if se > 0 else None), n


class DuLieu:
    def __init__(self):
        self.ro = [m for m in cd.ro_ma() if m != "VNINDEX"]
        self.C, self.H, self.Lo, self.V = cs.khung_gia(self.ro)
        self.ro = [m for m in self.ro if m in self.C]
        self.Cf = self.C.ffill()
        self.K = cs.chi_bao(self.C, self.H, self.Lo, self.V)
        self.fund = {m: cd.nap_bctc(m) for m in self.ro}
        self._snap = {}

    def snap(self, i):
        """Mot anh chup day du tai phien i: bo loc cung, diem, CANSLIM."""
        if i in self._snap:
            return self._snap[i]
        C, K, b = self.C, self.K, "VNINDEX"
        can = cs.cham_ngay(i, self.ro, C, K, self.fund)
        rows = {}
        for m in self.ro:
            c = C[m].iat[i]
            if pd.isna(c) or m not in can:
                continue
            g = lambda k: K[k][m].iat[i]
            gb = lambda k: K[k][b].iat[i]
            vals = dict(ma200=g("ma200"), ma50=g("ma50"), rs12=g("r252s") - gb("r252s"),
                        rs6=g("r126") - gb("r126"), rs3=g("r63") - gb("r63"),
                        tov=g("tov20"), atr=g("atr"))
            if any(pd.isna(v) for v in vals.values()):
                continue
            q = cs.trend_r2(C[m].iloc[max(0, i - 125):i + 1].dropna().values) or 0.0
            r = dict(ma=m, c=c, q=q, **{k: float(v) for k, v in vals.items()})
            r["pass"] = (r["tov"] >= LOC["thanh_khoan_min"] and c > r["ma200"]
                         and r["ma50"] > r["ma200"] and r["rs12"] > 0
                         and r["atr"] <= LOC["atr_max"])
            r["soft"] = c > 0.97 * r["ma200"] and r["rs12"] > -0.05
            cr = can[m]
            r.update({k: cr[k] for k in ("C", "A", "N", "S", "L", "M", "qua_3a",
                                         "qua_3a_doi_chung", "co_v3", "v3")})
            rows[m] = r
        pas = [r for r in rows.values() if r["pass"]]
        for r in rows.values():
            r["score"] = 0.0
        for k, w in W.items():
            for r, p in zip(pas, pct_rank([r[k] for r in pas])):
                r["score"] += w * p
        pas.sort(key=lambda r: (-r["score"], r["ma"]))
        n = len(pas)
        grp = 0
        for j, r in enumerate(pas):
            if j == 0 or r["score"] != pas[j - 1]["score"]:
                grp = j
            r["rank"] = grp / (n - 1) if n > 1 else 0.0
        for r in rows.values():                    # B1: chen ma rot loc vao ro co dinh
            if r["pass"]:
                continue
            sc = 0.0
            for k, w in W.items():
                less = sum(p[k] < r[k] for p in pas)
                eq = sum(p[k] == r[k] for p in pas)
                if n > 1:
                    rr = min(1, max(0, (less + ((eq - 1) / 2 if eq else 0)) / (n - 1)))
                elif n == 1:
                    rr = 0.5 if r[k] == pas[0][k] else float(r[k] > pas[0][k])
                else:
                    rr = 0.0
                sc += w * rr
            r["score"] = sc
            k = sum(p["score"] > sc for p in pas)
            r["rank"] = min(1, k / (n - 1)) if n > 1 else 1.0
        out = dict(rows=rows, pas=pas, M=can["_M"])
        self._snap[i] = out
        return out


def ty_trong(sel):
    if not sel:
        return {}
    raw = {r["ma"]: 1 / max(r["atr"], 0.005) for r in sel}
    s = sum(raw.values())
    tot = (1 - 0.02) / N_O * len(sel)
    w = {k: v / s * tot for k, v in raw.items()}
    for _ in range(20):
        ex, rest = 0.0, []
        for k in list(w):
            if w[k] > TRAN:
                ex += w[k] - TRAN
                w[k] = TRAN
            else:
                rest.append(k)
        if ex < 1e-9 or not rest:
            break
        sr = sum(w[k] for k in rest)
        for k in rest:
            w[k] += ex * (w[k] / sr if sr > 0 else 1 / len(rest))
    return w


def gioi_han(w):
    """Ap lai tran/ma va tong giai ngan SAU bien khong giao dich (phan xet Codex #2)."""
    w = {k: min(v, TRAN) for k, v in w.items()}
    tong = sum(w.values())
    if tong > 1 - 0.02:
        w = {k: v * (1 - 0.02) / tong for k, v in w.items()}
    return w


def chay(D, idx, cua=None):
    """cua(r) -> True neu ma duoc phep MUA MOI (Buoc 3a). None = khong co 3a (B1).

    Tin hieu doc o dong cua phien a; lenh KHOP o dong cua phien a+1 (phan xet Codex #4).
    Ma dang giu ma thieu du lieu tai phien a -> giu nguyen, khong tu ban (Codex #8).
    NAV theo ngay de do sut giam (Codex #9).
    """
    Cf = D.Cf
    last = len(Cf.index) - 1
    nav, prev, ex, gross, so_ma, rong = 1.0, {}, [], [], [], 0
    giai_ngan, ls_von, daily = [], [], [1.0]
    for a, b in zip(idx[:-1], idx[1:]):
        e, e2 = min(a + 1, last), min(b + 1, last)
        s = D.snap(a)
        rows = s["rows"]
        mat_du_lieu = {m: prev[m] for m in prev if m not in rows}
        keep = [rows[m] for m in prev if m in rows and rows[m]["soft"]
                and rows[m]["rank"] <= TRE]
        have = {r["ma"] for r in keep} | set(mat_du_lieu)
        pool = [r for r in s["pas"] if r["ma"] not in have]
        if cua is not None:
            pool = [r for r in pool if cua(r)]
            if not pool and len(keep) + len(mat_du_lieu) < N_O:
                rong += 1
        w = ty_trong(keep + pool[:max(0, N_O - len(keep) - len(mat_du_lieu))])
        w.update(mat_du_lieu)
        w2 = {}
        for k in set(w) | set(prev):
            x, y = prev.get(k, 0), w.get(k, 0)
            v = x if (abs(y - x) < BIEN and x > 0 and y > 0) else y
            if v > 0:
                w2[k] = v
        w = gioi_han(w2)
        to = sum(abs(w.get(k, 0) - prev.get(k, 0)) for k in set(w) | set(prev))
        chi_phi = to / 2 * PHI
        # Duong NAV theo ngay trong ky giu [e, e2]
        p0 = {k: Cf[k].iat[e] for k in w}
        tien = 1 - sum(w.values())
        base = nav * (1 - chi_phi)
        for t in range(e + 1, e2 + 1):
            val = tien + sum(w[k] * (Cf[k].iat[t] / p0[k] if p0[k] and np.isfinite(Cf[k].iat[t] / p0[k]) else 1)
                             for k in w)
            daily.append(base * val)
        fwd = {k: Cf[k].iat[e2] / p0[k] - 1 for k in w}
        fwd = {k: (0.0 if not np.isfinite(v) else v) for k, v in fwd.items()}
        g = sum(w[k] * fwd[k] for k in w)
        net = (1 + g) * (1 - chi_phi) - 1
        ib = Cf["VNINDEX"].iat[e2] / Cf["VNINDEX"].iat[e] - 1
        nav *= 1 + net
        gross.append(net)
        ex.append(net - ib)
        so_ma.append(len(w))
        gn = sum(w.values())
        giai_ngan.append(gn)
        if gn > 0.05:
            ls_von.append(g / gn)              # loi suat tren phan von DA giai ngan (hau kiem)
        sc = 1 + g
        prev = {k: w[k] * (1 + fwd[k]) / sc for k in w}
    pk, mdd = daily[0], 0.0
    for v in daily:
        pk = max(pk, v)
        mdd = min(mdd, v / pk - 1)
    n = len(gross)
    nam = (min(idx[-1] + 1, last) - min(idx[0] + 1, last)) / 252
    t, _ = nw_t(ex)
    return dict(cagr=nav ** (1 / nam) - 1, mdd=mdd, alpha_ky=float(np.mean(ex)), t_alpha=t,
                so_ma_tb=float(np.mean(so_ma)), ky_khong_co_ma_3a=rong, so_ky=n,
                giai_ngan_tb=float(np.mean(giai_ngan)),
                ls_tren_von_giai_ngan_ky=float(np.mean(ls_von)) if ls_von else None,
                so_ky_co_giai_ngan=len(ls_von), _ret=gross)


def luoi(D, bat_dau, pha):
    """Chi so phien ra soat: neo tu phien cuoi, lui tung BUOC phien, lech `pha` phien."""
    end = len(D.C.index) - 1 - pha
    i0 = cs.vi_tri_ngay(D.C.index, bat_dau, method="bfill")
    return list(range(end, i0 - 1, -BUOC))[::-1]


def kiem_tung_chu(D, idx, h=63, pham_vi="thanh_khoan"):
    """Moi ky: TB loi suat vuot VNINDEX h phien toi (nhom qua chu X) - (nhom khong qua).

    Vao o dong cua phien a+1. Ma KHONG DO DUOC chu X (None) bi loai khoi ca hai nhom.
    pham_vi: "thanh_khoan" (dang ky truoc: moi ma >= 10 ty/phien)
             "tang1"       (hau kiem, phan xet Codex #5: chi ma qua Tang 1 — dung tap
                            ma B1 that su co the mua)
    """
    Cf = D.Cf
    chu = ("C", "A", "N", "S", "L", "qua_3a_ko_M", "qua_3a_doi_chung_ko_M", "co_v3")
    kq = {k: [] for k in chu}
    m_rows = []
    for a0 in idx:
        a, b = a0 + 1, a0 + 1 + h
        if b >= len(Cf.index):
            break
        s = D.snap(a0)
        ib = Cf["VNINDEX"].iat[b] / Cf["VNINDEX"].iat[a] - 1
        m_rows.append((s["M"], ib))
        rows = [r for r in s["rows"].values()
                if (r["pass"] if pham_vi == "tang1" else r["tov"] >= LOC["thanh_khoan_min"])]
        for r in rows:
            f = Cf[r["ma"]].iat[b] / Cf[r["ma"]].iat[a] - 1
            r["_fx"] = f - ib if np.isfinite(f) else None
            nsl = sum(r[k] is True for k in ("N", "S", "L"))
            r["qua_3a_ko_M"] = r["C"] is True and r["A"] is True and nsl >= 2
            r["qua_3a_doi_chung_ko_M"] = r["qua_3a_ko_M"] and nsl == 3
            r["co_v3"] = r["co_v3"] if r["v3"] is not None else None
        for k in chu:
            yes = [r["_fx"] for r in rows if r[k] is True and r["_fx"] is not None]
            no = [r["_fx"] for r in rows if r[k] is False and r["_fx"] is not None]
            kq[k].append((np.mean(yes) - np.mean(no), len(yes), len(no))
                         if len(yes) >= 3 and len(no) >= 3 else None)
    lag = int(np.ceil(h / BUOC)) + 1
    out = {}
    for k, v in kq.items():
        d = [x[0] for x in v if x]
        t, n = nw_t(d, lag)
        out[k] = dict(chenh_3t=float(np.mean(d)) if d else None, t_nw=t, so_ky=n,
                      tb_so_ma_qua=float(np.mean([x[1] for x in v if x])) if d else None)
    # M: loi suat VNINDEX h phien toi khi M dung vs sai (chuoi thoi gian, NW)
    on = np.array([m is True for m, _ in m_rows])
    rr = np.array([r for _, r in m_rows])
    if on.any() and (~on).any():
        X = np.column_stack([np.ones(len(rr)), on.astype(float)])
        beta = np.linalg.lstsq(X, rr, rcond=None)[0]
        e = rr - X @ beta
        n = len(rr)
        S = (X * e[:, None]).T @ (X * e[:, None]) / n
        for k in range(1, lag + 1):
            G = (X[k:] * e[k:, None]).T @ (X[:-k] * e[:-k, None]) / n
            S += (1 - k / (lag + 1)) * (G + G.T)
        Q = np.linalg.inv(X.T @ X / n)
        V = Q @ S @ Q / n
        out["M"] = dict(chenh_3t=float(beta[1]), t_nw=float(beta[1] / np.sqrt(V[1, 1])),
                        so_ky=n, ty_le_M_dung=float(on.mean()),
                        tb_khi_dung=float(rr[on].mean()), tb_khi_sai=float(rr[~on].mean()))
    return out


def phan_xu(pha_kq, ten):
    d = [p[ten]["diff_ky"] for p in pha_kq]
    ts = [p[ten]["t_diff"] for p in pha_kq]
    dd = [p[ten]["mdd"] - p["B1"]["mdd"] for p in pha_kq]
    duong = sum(x > 0 for x in d)
    t_tb = float(np.mean([t for t in ts if t is not None])) if any(t is not None for t in ts) else None
    if t_tb is None:
        v = "KHONG DO DUOC"
    elif duong >= 3 and t_tb >= 2 and min(dd) >= -0.03:
        v = "CHAP NHAN"
    elif t_tb >= 1:
        v = "CHUA KET LUAN"
    else:
        v = "BAC BO"
    return dict(pha_duong=duong, t_tb=t_tb, chenh_ky_tb=float(np.mean(d)),
                mdd_te_hon_toi_da=float(min(dd)), phan_xu=v)


def main():
    D = DuLieu()
    # Cua so: tu thang dau tien ma A do duoc cho >= 50% ro (can 16 quy LNST lien tuc).
    ngay_ra = D.C.index
    bat_dau = None
    for i in range(260, len(ngay_ra), BUOC):
        nd = ngay_ra[i]
        co = sum(cs.co_ban(*D.fund[m], nd)["A"] is not None for m in D.ro)
        if co >= 0.5 * len(D.ro):
            bat_dau = nd
            break
    print(f"Ro: {len(D.ro)} ma | cua so tu {bat_dau} (A do duoc cho >=50% ro) "
          f"den {ngay_ra[-1]}")
    bien_the = {
        "B1": None,
        "CANSLIM_chinh": lambda r: r["qua_3a"],
        "CANSLIM_doi_chung": lambda r: r["qua_3a_doi_chung"],
        "CANSLIM_chinh_V3": lambda r: r["qua_3a"] and not r["co_v3"],
        "chi_M": lambda r: r["M"] is True,
    }
    pha_kq = []
    for p in PHA:
        idx = luoi(D, bat_dau, p)
        res = {k: chay(D, idx, f) for k, f in bien_the.items()}
        base = res["B1"]["_ret"]
        for k, r in res.items():
            diff = [x - y for x, y in zip(r["_ret"], base)]
            r["diff_ky"] = float(np.mean(diff))
            r["t_diff"] = nw_t(diff)[0] if k != "B1" else None
        iv = D.Cf["VNINDEX"]
        nam = (len(idx) - 1) * BUOC / 252
        res["VNINDEX"] = dict(cagr=(iv.iat[idx[-1]] / iv.iat[idx[0]]) ** (1 / nam) - 1)
        res["_ky"] = [str(ngay_ra[idx[0]]), str(ngay_ra[idx[-1]]), len(idx) - 1]
        pha_kq.append(res)

    sach = lambda r: {k: v for k, v in r.items() if not k.startswith("_")}
    out = {"_meta": dict(sinh_luc=str(dt.date.today()), ro=len(D.ro), bat_dau=str(bat_dau),
                         ket_thuc=str(ngay_ra[-1]), buoc_phien=BUOC, pha=PHA, so_o=N_O,
                         tran=TRAN, phi=PHI,
                         canh_bao=["Thien lech song sot: ro la ma dang niem yet hom nay",
                                   "BCTC la ban moi nhat (co the da dieu chinh hoi to)",
                                   "Buoc 3b (V1-V5) khong backtest duoc",
                                   "I bo khoi luat may"])}
    out["pha"] = [{k: (sach(v) if isinstance(v, dict) else v) for k, v in p.items()}
                  for p in pha_kq]
    out["phan_xu"] = {k: phan_xu(pha_kq, k) for k in bien_the if k != "B1"}
    out["tung_chu"] = kiem_tung_chu(D, luoi(D, bat_dau, 0))
    out["tung_chu_tang1_hau_kiem"] = kiem_tung_chu(D, luoi(D, bat_dau, 0), pham_vi="tang1")

    print(f"\n{'Bien the':<20}" + "".join(f"  pha{p:<2} CAGR / MDD / chenh-ky / t " for p in PHA))
    for k in list(bien_the) + ["VNINDEX"]:
        line = f"{k:<20}"
        for p in pha_kq:
            r = p[k]
            if k == "VNINDEX":
                line += f"  {r['cagr']*100:6.2f}%{'':>28}"
            else:
                t = r.get("t_diff")
                line += (f"  {r['cagr']*100:6.2f}% {r['mdd']*100:6.1f}% "
                         f"{r['diff_ky']*100:+6.2f}% {'' if t is None else f'{t:+5.2f}':>6}")
        print(line)
    print("\nPHAN XU (nguong dang ky truoc):")
    for k, v in out["phan_xu"].items():
        print(f"  {k:<20} {v}")
    print("\nTUNG CHU (vuot VNINDEX 3 thang toi, qua - khong qua):")
    for k, v in out["tung_chu"].items():
        print(f"  {k:<24} {v}")
    print("\nTUNG CHU — HAU KIEM, chi ma qua Tang 1:")
    for k, v in out["tung_chu_tang1_hau_kiem"].items():
        print(f"  {k:<24} {v}")
    for p in pha_kq:
        print("  ky", p["_ky"], {k: dict(so_ma=round(p[k]['so_ma_tb'], 1),
                                          giai_ngan=round(p[k]['giai_ngan_tb'], 2),
                                          ls_von=None if p[k]['ls_tren_von_giai_ngan_ky'] is None
                                          else round(p[k]['ls_tren_von_giai_ngan_ky'] * 100, 2),
                                          ky_rong=p[k]['ky_khong_co_ma_3a'])
                                 for k in bien_the})
    pj = os.path.join("data", f"canslim_backtest_{dt.date.today():%Y%m%d}.json")
    with open(pj, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1, default=str)
    print(f"\n-> {pj}")


if __name__ == "__main__":
    main()
