"""
nganh.py — Nganh theo ICB cap 2 (19 nhom, Vietcap icbCode2), tinh tu ban quet.

Day la phan nganh cua MAY de quan sat. Tran nganh cua Quy dung nganh NGUOI gan
trong _ro_co_ban.nganh (quyet dinh 8, muc 13) — hien canh nhau, khong tron.
"""

import numpy as np
import pandas as pd

from dashboard.thi_truong import bo_mang_sang, gia_tri_giao_dich, ma_tran

TEN_ICB = {
    "0500": "Dầu khí", "1300": "Hóa chất", "1700": "Tài nguyên cơ bản",
    "2300": "Xây dựng & vật liệu", "2700": "Hàng & dịch vụ công nghiệp",
    "3300": "Ô tô & phụ tùng", "3500": "Thực phẩm & đồ uống",
    "3700": "Hàng cá nhân & gia dụng", "4500": "Y tế", "5300": "Bán lẻ",
    "5500": "Truyền thông", "5700": "Du lịch & giải trí", "6500": "Viễn thông",
    "7500": "Điện, nước & khí đốt", "8300": "Ngân hàng", "8500": "Bảo hiểm",
    "8600": "Bất động sản", "8700": "Dịch vụ tài chính", "9500": "Công nghệ thông tin",
}


def ten_nganh(icb):
    return TEN_ICB.get(icb, "Chưa phân ngành")


def bang_nganh(df, qua_loc=frozenset(), tov_min=1.0):
    """Mot dong moi nganh: do rong, loi suat trung vi, thanh khoan, so ma qua loc cung.

    `tov_min` (ty/phien, TB 20 phien) gioi han vu tru tinh trung vi va do rong —
    toan UPCoM khong thanh khoan se keo trung vi ve 0. So ma qua loc cung dem tren
    toan bo (loc cung da doi >= 10 ty).
    """
    d = bo_mang_sang(df[df["tov_ty"] >= tov_min]).copy()
    d["nganh"] = d["icb"].map(ten_nganh)
    gd = d[~d["lech_ngay"]]
    co_ma = d[d["ma200"].notna() & d["ma50"].notna()]
    tong_gt = d["tov_ty"].sum() or 1.0
    ql = df[df.index.isin(qua_loc)].assign(nganh=lambda x: x["icb"].map(ten_nganh))
    out = pd.DataFrame({
        "Số mã": d.groupby("nganh").size(),
        "Qua lọc cứng": ql.groupby("nganh").size(),
        "Trên MA200": co_ma.assign(x=co_ma["c"] > co_ma["ma200"]).groupby("nganh")["x"].mean(),
        "MA50 > MA200": co_ma.assign(x=co_ma["ma50"] > co_ma["ma200"]).groupby("nganh")["x"].mean(),
        "1 phiên": gd.groupby("nganh")["r1"].median(),
        "5 phiên": gd.groupby("nganh")["r5"].median(),
        "21 phiên": d.groupby("nganh")["r21"].median(),
        "63 phiên": d.groupby("nganh")["r63"].median(),
        "GTGD TB20 (tỷ)": d.groupby("nganh")["tov_ty"].sum(),
    })
    out["Tỷ trọng GTGD"] = out["GTGD TB20 (tỷ)"] / tong_gt
    out["Qua lọc cứng"] = out["Qua lọc cứng"].fillna(0).astype(int)
    out = out[out["Số mã"].fillna(0) > 0]
    out.index.name = "Ngành"
    return out.sort_values("21 phiên", ascending=False)


def loi_suat_lan(df, ngay, k=21, tov_min=1.0):
    """Trung vi loi suat k phien cua tung nganh, tinh lui tung phien tu chuoi c60."""
    d = df[df["tov_ty"] >= tov_min]
    c = ma_tran(d, "c60", ngay)
    r = c / c.shift(k, axis=1) - 1
    nganh = d.loc[r.index, "icb"].map(ten_nganh)
    out = r.groupby(nganh).median().T
    return out.dropna(how="all")


def ty_trong_dong_tien(df, ngay):
    """Ty trong GTGD khop lenh cua tung nganh trong tong thi truong, tung phien."""
    gt = gia_tri_giao_dich(df, ngay)
    nganh = df.loc[gt.index, "icb"].map(ten_nganh)
    s = gt.groupby(nganh).sum()
    return (s / s.sum()).T


def thu_hang(loi_suat, lui=5):
    """Thu hang nganh theo loi suat 21 phien: phien cuoi so voi `lui` phien truoc."""
    if len(loi_suat) <= lui:
        return None
    nay = loi_suat.iloc[-1].rank(ascending=False)
    truoc = loi_suat.iloc[-1 - lui].rank(ascending=False)
    out = pd.DataFrame({"Hạng nay": nay, f"Hạng {lui} phiên trước": truoc})
    out["Thay đổi"] = out[f"Hạng {lui} phiên trước"] - out["Hạng nay"]
    out = out.dropna().astype(int).sort_values("Hạng nay")
    out.index.name = "Ngành"
    return out


def nhan_heatmap(bang):
    """Ma tran nganh x khung (1/5/21/63 phien) cho heatmap."""
    cot = ["1 phiên", "5 phiên", "21 phiên", "63 phiên"]
    return bang[cot].astype(float).replace([np.inf, -np.inf], np.nan)
