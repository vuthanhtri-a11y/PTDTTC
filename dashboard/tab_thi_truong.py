"""tab_thi_truong.py — Chi so, VN-Index + che do, do rong, thanh khoan, tang/giam, top bien dong."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from dashboard import bieu_do, chi_tiet, thi_truong, ui
from dashboard.nganh import ten_nganh

VU_TRU = {"Tất cả": 0.0, "Thanh khoản ≥ 1 tỷ": 1.0, "Thanh khoản ≥ 10 tỷ": 10.0}
CHI_SO_PHU = ["VN30", "HNX30", "E1VFVN30"]


@st.cache_data(show_spinner=False, ttl=3600)
def _chi_so(ma, den):
    try:
        return thi_truong.chi_so(ma, den)
    except Exception:
        return None


def ve(ctx):
    bq, vni = ctx.bq, ctx.bq.vnindex
    rows = [{"Mã": "VNINDEX", "Đóng cửa": vni["c"], "1 phiên": vni.get("r1"),
             "5 phiên": vni.get("r5"), "21 phiên": vni["r21"], "63 phiên": vni["r63"],
             "So MA200": vni["c"] / vni["ma200"] - 1 if vni.get("ma200") else None,
             "Ngày": ctx.phien.ngay}]
    for ma in CHI_SO_PHU:
        x = _chi_so(ma, ctx.phien.ngay)
        if x:
            rows.append(x)
    cs = pd.DataFrame(rows)
    st.markdown("##### Chỉ số")
    sty = ui.bang(cs, so_cot={"Đóng cửa": 2},
                  pt_cot={"1 phiên": 2, "5 phiên": 1, "21 phiên": 1, "63 phiên": 1, "So MA200": 1},
                  ngay_cot=["Ngày"])
    st.dataframe(ui.them_mau_delta(sty, ["1 phiên", "5 phiên", "21 phiên", "63 phiên", "So MA200"]),
                 hide_index=True, width="stretch")
    st.caption("HNX-Index và UPCoM-Index: Vietcap không trả dữ liệu cho mã chỉ số này. "
               "E1VFVN30 là chứng chỉ quỹ dùng làm thước đo (quyết định 16).")

    st.markdown("##### VN-Index và chế độ thị trường")
    if ctx.vn is None:
        st.info("Bản quét phiên này không có chuỗi VN-Index (quét trước 04/10/2026).")
    else:
        kh = st.segmented_control("Khung", ["6 tháng", "1 năm", "2 năm"], default="1 năm",
                                  key="tt_khung", label_visibility="collapsed")
        n = {"6 tháng": 125, "1 năm": 250, "2 năm": 500}.get(kh or "1 năm", 250)
        ui.ve(bieu_do.vnindex(ctx.vn, so_phien=n), key="tt_vni")
        if ctx.che_do and ctx.che_do.get("doi_gan_nhat"):
            st.caption("Các lần đổi chế độ gần nhất: " + " · ".join(
                f"{ui.ngay_vn(d)} {ui.CHE_DO_TEN[a]}→{ui.CHE_DO_TEN[b]}"
                for d, a, b in ctx.che_do["doi_gan_nhat"][-5:]))

    st.markdown("##### Độ rộng thị trường")
    vu = st.segmented_control("Vũ trụ", list(VU_TRU), default="Thanh khoản ≥ 1 tỷ", key="tt_vu",
                              label_visibility="collapsed") or "Thanh khoản ≥ 1 tỷ"
    dr = thi_truong.do_rong(bq.df, VU_TRU[vu]).reset_index()
    st.dataframe(ui.bang(dr, so_cot={"GTGD TB20 (tỷ)": 0},
                         pt_khong_dau={"Trên MA50": 0, "Trên MA200": 0, "MA50 > MA200": 0}),
                 hide_index=True, width="stretch")
    st.caption("Tỷ lệ tính trên mã đủ 200 phiên. 'Không khớp' = không có khớp lệnh ở phiên cuối "
               "(bị loại khỏi đếm tăng/giảm và mọi chuỗi theo thời gian). Vietcap chỉ tính khớp lệnh, "
               "không gồm thoả thuận.")

    ngay = thi_truong.ngay_60(bq.phu)
    if ngay:
        m = ui.mau()
        c1, c2 = st.columns(2)
        with c1:
            tk = thi_truong.thanh_khoan_theo_san(bq.df, ngay)
            x = [d.strftime("%d/%m") for d in tk.index]     # truc danh muc: khong co khe cuoi tuan
            fig = go.Figure()
            for cot, mau_ in zip(tk.columns, (m["s1"], m["s2"], m["s3"])):
                fig.add_trace(go.Bar(x=x, y=tk[cot], name=cot, marker_color=mau_,
                                     marker_line=dict(color=m["be_mat"], width=1)))
            fig.update_layout(barmode="stack", bargap=0.15)
            ui.khung(fig, cao=340, chu_y="Giá trị khớp lệnh 60 phiên (tỷ đồng)")
            fig.update_yaxes(tickformat=",.0f")
            fig.update_xaxes(type="category", nticks=8)
            ui.ve(fig, key="tt_tk")
        with c2:
            tg = thi_truong.tang_giam_theo_phien(bq.df, ngay)
            fig = go.Figure()
            fig.add_trace(go.Bar(x=[d.strftime("%d/%m") for d in tg.index], y=tg["Ròng"],
                                 name="Tăng − giảm (ròng)",
                                 marker_color=[m["tang"] if v >= 0 else m["giam"] for v in tg["Ròng"]]))
            ui.khung(fig, cao=340, chu_y="Số mã tăng trừ số mã giảm mỗi phiên", legend=False)
            fig.update_xaxes(type="category", nticks=8)
            fig.update_traces(customdata=tg[["Tăng", "Giảm"]].to_numpy(),
                              hovertemplate="Tăng %{customdata[0]} · Giảm %{customdata[1]}"
                                            " · ròng %{y}<extra></extra>")
            ui.ve(fig, key="tt_tg")

    st.markdown("##### Biến động mạnh nhất")
    c1, c2, c3 = st.columns([1, 1, 2])
    cot = {"1 phiên": "r1", "5 phiên": "r5", "21 phiên": "r21"}[
        c1.selectbox("Khung", ["1 phiên", "5 phiên", "21 phiên"], key="tt_top_khung")]
    tov = c2.number_input("Thanh khoản tối thiểu (tỷ/phiên)", 0.0, 1000.0, 10.0, 5.0, key="tt_top_tov")
    c3.caption("Chọn một dòng để mở chi tiết mã.")
    a, b = st.columns(2)
    for khung_, tang, key in ((a, True, "tt_top_tang"), (b, False, "tt_top_giam")):
        d = thi_truong.top_bien_dong(bq.df, cot, 15, tov, tang).reset_index()
        d = pd.DataFrame({"Mã": d["ma"], "Sàn": d["san"].map(thi_truong.SAN_TEN),
                          "Ngành": d["icb"].map(ten_nganh), "Giá": d["c"], "Biến động": d[cot],
                          "GTGD TB20 (tỷ)": d["tov_ty"]})
        with khung_:
            st.markdown("**Tăng mạnh nhất**" if tang else "**Giảm mạnh nhất**")
            sty = ui.them_mau_delta(ui.bang(d, so_cot={"Giá": 0, "GTGD TB20 (tỷ)": 1},
                                            pt_cot={"Biến động": 1}), ["Biến động"])
            chi_tiet.bang_chon(d, key, sty=sty, ctx=ctx)
