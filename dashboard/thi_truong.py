"""
thi_truong.py — So lieu thi truong tinh tu MOT ban quet (va chuoi VN-Index trong
khoi _vnindex cua no). Che do va phien phan phoi goi lai ham cua lt_che_do.py.
"""

import numpy as np
import pandas as pd

from dashboard.nguon import lich_su_gia   # dat ROOT vao sys.path truoc lt_*

import lt_che_do                          # noqa: E402
from lt_config import CHE_DO              # noqa: E402

SAN_TEN = {"HSX": "HOSE", "HNX": "HNX", "UPCOM": "UPCoM"}


def chuoi_vnindex(phu):
    """DataFrame VN-Index: c, v, MA50, MA200, nguong vao/ra Giam, che do, phien phan phoi.

    None neu ban quet khong co khoi _vnindex (ban quet truoc 04/10/2026).
    """
    x = phu.get("_vnindex")
    if not x:
        return None
    c, v = x["c"], x["v"]
    df = pd.DataFrame({"ngay": pd.to_datetime(x["t"]), "c": c, "v": v})
    df["ma50"] = df["c"].rolling(50).mean()
    df["ma200"] = df["c"].rolling(200).mean()
    df["nguong_vao_giam"] = CHE_DO["nguong_vao_giam"] * df["ma200"]
    df["nguong_ra_giam"] = CHE_DO["nguong_ra_giam"] * df["ma200"]
    df["che_do"] = lt_che_do.chuoi_che_do(c, v)
    pp = set()
    for i in range(1, len(c)):
        pp.update(lt_che_do.phien_phan_phoi(c, v, i))
    df["phan_phoi"] = df.index.isin(pp)
    # Chi cac phien phan phoi trong cua so 25 phien dang tinh cho che do hom nay.
    df["phan_phoi_cua_so"] = df.index.isin(lt_che_do.phien_phan_phoi(c, v, len(c) - 1))
    return df


def doan_che_do(vn):
    """[(tu, den, che_do)] — cac doan lien tuc cung che do, de to nen bieu do."""
    out, cu, tu = [], None, None
    for ngay, st in zip(vn["ngay"], vn["che_do"]):
        if st != cu:
            if cu is not None:
                out.append((tu, ngay, cu))
            cu, tu = st, ngay
    if cu is not None:
        out.append((tu, vn["ngay"].iloc[-1], cu))
    return [d for d in out if d[2] is not None]


def bo_mang_sang(df):
    """Bo dong mang sang tu ban quet truoc (quet hai tang): so lieu cua chung la cua phien cu."""
    return df[df["mang_sang"].isna()] if "mang_sang" in df else df


def do_rong(df, tov_min=0.0):
    """Do rong theo san + toan thi truong. Ty le tinh tren ma du 200 phien, bo dong mang sang."""
    d = bo_mang_sang(df[df["tov_ty"] >= tov_min])
    rows = []
    for ten, g in [("Toàn thị trường", d)] + [(SAN_TEN[s], d[d["san"] == s])
                                               for s in ("HSX", "HNX", "UPCOM")]:
        co_ma = g[g["ma200"].notna() & g["ma50"].notna()]
        gd = g[~g["lech_ngay"]]
        n = max(len(co_ma), 1)
        rows.append({
            "Nhóm": ten, "Số mã": len(g),
            "Trên MA50": (co_ma["c"] > co_ma["ma50"]).sum() / n,
            "Trên MA200": (co_ma["c"] > co_ma["ma200"]).sum() / n,
            "MA50 > MA200": (co_ma["ma50"] > co_ma["ma200"]).sum() / n,
            "Tăng": int((gd["r1"] > 0).sum()), "Giảm": int((gd["r1"] < 0).sum()),
            "Đứng": int((gd["r1"] == 0).sum()), "Không khớp": int(g["lech_ngay"].sum()),
            "GTGD TB20 (tỷ)": g["tov_ty"].sum(),
        })
    return pd.DataFrame(rows).set_index("Nhóm")


def ngay_60(phu):
    x = phu.get("_vnindex")
    return list(pd.to_datetime(x["t"][-60:])) if x else None


def ma_tran(df, cot, ngay):
    """Ma tran ma x ngay tu cot chuoi (c60 / vol60), canh theo phien cuoi.

    Bo ma lech ngay (khong khop lenh phien cuoi): chuoi cua chung ket thuc o ngay khac.
    """
    d = df[~df["lech_ngay"]]
    n = len(ngay)
    M = np.full((len(d), n), np.nan)
    for i, a in enumerate(d[cot]):
        if isinstance(a, list) and a:
            a = a[-n:]
            M[i, n - len(a):] = a
    return pd.DataFrame(M, index=d.index, columns=ngay)


def gia_tri_giao_dich(df, ngay):
    """GTGD khop lenh tung ma tung phien (ty dong) = gia dong cua x KL (vol60 tinh nghin CP)."""
    return ma_tran(df, "c60", ngay) * ma_tran(df, "vol60", ngay) * 1000 / 1e9


def thanh_khoan_theo_san(df, ngay):
    gt = gia_tri_giao_dich(df, ngay)
    san = df.loc[gt.index, "san"].map(SAN_TEN)
    out = gt.groupby(san).sum().T
    return out[[c for c in ("HOSE", "HNX", "UPCoM") if c in out.columns]]


def tang_giam_theo_phien(df, ngay):
    """So ma tang / giam moi phien + duong A/D tich luy (bo phien dau, khong co phien truoc)."""
    c = ma_tran(df, "c60", ngay)
    d = c.diff(axis=1).iloc[:, 1:]
    out = pd.DataFrame({"Tăng": (d > 0).sum(), "Giảm": (d < 0).sum()})
    out["Ròng"] = out["Tăng"] - out["Giảm"]
    out["A/D tích lũy"] = out["Ròng"].cumsum()
    return out


def top_bien_dong(df, cot, n=10, tov_min=10.0, tang=True):
    d = df[(~df["lech_ngay"]) & (df["tov_ty"] >= tov_min) & df[cot].notna()]
    return d.sort_values(cot, ascending=not tang).head(n)


def chi_so(ma, den):
    """Tom tat mot chi so (VN30, HNX30, E1VFVN30...) tai ngay du lieu `den`."""
    g = lich_su_gia(ma, den)
    if len(g) < 2:
        return None
    c = g["c"].to_numpy()

    def r(k):
        return c[-1] / c[-1 - k] - 1 if len(c) > k else None

    ma200 = c[-200:].mean() if len(c) >= 200 else None
    return {"Mã": ma, "Đóng cửa": c[-1], "1 phiên": r(1), "5 phiên": r(5),
            "21 phiên": r(21), "63 phiên": r(63),
            "So MA200": None if ma200 is None else c[-1] / ma200 - 1,
            "Ngày": g["ngay"].iloc[-1]}
