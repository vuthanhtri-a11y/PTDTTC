"""tab_kham_pha.py — Loc tu do toan thi truong. KHONG phai tin hieu cua Quy, khong ghi file pipeline."""

import pandas as pd
import streamlit as st

from dashboard import chi_tiet, nguon, ui
from dashboard.nganh import TEN_ICB, ten_nganh
from dashboard.thi_truong import SAN_TEN


def ve(ctx):
    st.markdown('<div class="nhan-kp">🔍 <b>Khám phá — không phải tín hiệu của Quỹ.</b> Bộ lọc tự do '
                'để tìm ứng viên đưa vào thẩm định. Kết quả không ghi vào file nào mà screener/allocator '
                'đọc; muốn một mã vào phễu thì phải qua rổ cơ bản và phiếu V1–V5.</div>',
                unsafe_allow_html=True)
    df = ctx.bq.df
    ten = nguon.danh_ba_ma()
    c = st.columns([2, 3, 1.3, 1.3, 1.3, 1.3])
    san = c[0].multiselect("Sàn", ["HOSE", "HNX", "UPCoM"], key="kp_san")
    nganh_ = c[1].multiselect("Ngành", sorted(TEN_ICB.values()), key="kp_nganh")
    tov = c[2].number_input("GTGD TB20 ≥ (tỷ)", 0.0, 5000.0, 1.0, 1.0, key="kp_tov")
    r21 = c[3].number_input("21 phiên ≥ (%)", -100.0, 500.0, -100.0, 1.0, key="kp_r21")
    r63 = c[4].number_input("63 phiên ≥ (%)", -100.0, 500.0, -100.0, 1.0, key="kp_r63")
    atr = c[5].number_input("ATR ≤ (%)", 0.0, 50.0, 50.0, 0.5, key="kp_atr")
    c = st.columns([1.2, 1.2, 1.2, 3])
    tren200 = c[0].checkbox("Giá > MA200", key="kp_ma200")
    ma50 = c[1].checkbox("MA50 > MA200", key="kp_ma50")
    tren50 = c[2].checkbox("Giá > MA50", key="kp_tren50")
    tim = c[3].text_input("Tìm mã / tên công ty", key="kp_tim").strip().upper()

    d = df.copy()
    d["san_ten"] = d["san"].map(SAN_TEN)
    d["nganh"] = d["icb"].map(ten_nganh)
    loc = d["tov_ty"] >= tov
    if san:
        loc &= d["san_ten"].isin(san)
    if nganh_:
        loc &= d["nganh"].isin(nganh_)
    loc &= d["r21"].fillna(-9) >= r21 / 100
    loc &= d["r63"].fillna(-9) >= r63 / 100
    loc &= d["atr"] <= atr / 100
    if tren200:
        loc &= d["c"] > d["ma200"]
    if ma50:
        loc &= d["ma50"] > d["ma200"]
    if tren50:
        loc &= d["c"] > d["ma50"]
    if tim:
        ten_up = pd.Series({m: v.get("ten", "").upper() for m, v in ten.items()})
        loc &= d.index.str.contains(tim, regex=False) | d.index.map(
            lambda m: tim in ten_up.get(m, "")).astype(bool)
    d = d[loc].reset_index()
    out = pd.DataFrame({
        "Mã": d["ma"], "Tên": d["ma"].map(lambda m: ten.get(m, {}).get("ten", "")),
        "Sàn": d["san_ten"], "Ngành": d["nganh"], "Giá": d["c"], "1 phiên": d["r1"],
        "5 phiên": d["r5"], "21 phiên": d["r21"], "63 phiên": d["r63"], "252 phiên": d["r252"],
        "So MA50": d["c"] / d["ma50"] - 1, "So MA200": d["c"] / d["ma200"] - 1,
        "ATR": d["atr"], "GTGD TB20 (tỷ)": d["tov_ty"],
    }).sort_values("GTGD TB20 (tỷ)", ascending=False)
    st.caption(f"**{len(out)}** / {len(df)} mã khớp bộ lọc · dữ liệu phiên {ui.ngay_vn(ctx.phien.ngay)}"
               + ("" if ten else " · chưa có tên công ty (sẽ tải ở lần quét tới)"))
    cot_pt = ["1 phiên", "5 phiên", "21 phiên", "63 phiên", "252 phiên", "So MA50", "So MA200"]
    sty = ui.them_mau_delta(ui.bang(out, so_cot={"Giá": 0, "GTGD TB20 (tỷ)": 1},
                                    pt_cot={k: 1 for k in cot_pt}, pt_khong_dau={"ATR": 2}), cot_pt)
    chi_tiet.bang_chon(out, "kp_bang", sty=sty, ctx=ctx, cao=560)
    st.download_button("Tải CSV (về máy, không ghi vào data/)", out.to_csv(index=False).encode("utf-8-sig"),
                       file_name=f"kham_pha_{ctx.phien.ngay}.csv", mime="text/csv")
