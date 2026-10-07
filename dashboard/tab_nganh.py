"""tab_nganh.py — 19 nganh ICB cap 2 + lop phu nganh cua ro co ban (nguoi gan)."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from dashboard import bieu_do, chi_tiet, nganh, thi_truong, ui

VU_TRU = {"Tất cả": 0.0, "Thanh khoản ≥ 1 tỷ": 1.0, "Thanh khoản ≥ 10 tỷ": 10.0}


def _ro_nganh(ctx):
    st.markdown("##### Ngành của rổ cơ bản (người gán)")
    ro = ctx.ro.get("nganh") or {}
    if not ro:
        ui.canh_bao("Rổ chưa có ngành nào (`_ro_co_ban.nganh` rỗng). Trần ngành của Quỹ dùng ngành "
                    "người gán ở đây — bảng ICB bên trên chỉ để quan sát.")
        return
    ma_theo_nganh = {}
    for ma, v in ctx.tham_dinh.items():
        if not ma.startswith("_") and v.get("nganh"):
            ma_theo_nganh.setdefault(v["nganh"], []).append(ma)
    rows = [{"Ngành rổ": ng, "Kết luận": {True: "✓ trong rổ", False: "✗ loại", None: "? chưa kết luận"}
             .get(v.get("trong_ro")), "Lý do": v.get("ly_do", ""),
             "Mã gán ngành này": ", ".join(sorted(ma_theo_nganh.get(ng, [])))}
            for ng, v in sorted(ro.items())]
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)


def ve(ctx):
    bq = ctx.bq
    vu = st.segmented_control("Vũ trụ", list(VU_TRU), default="Thanh khoản ≥ 1 tỷ", key="ng_vu",
                              label_visibility="collapsed") or "Thanh khoản ≥ 1 tỷ"
    tov = VU_TRU[vu]
    ql = {c["ma"] for c in ctx.cands or [] if c.get("qua_loc_cung")}
    b = nganh.bang_nganh(bq.df, ql, tov)
    st.markdown("##### Bảng ngành (ICB cấp 2) — xếp theo lợi suất trung vị 21 phiên")
    sty = ui.bang(b.reset_index(), so_cot={"Số mã": 0, "Qua lọc cứng": 0, "GTGD TB20 (tỷ)": 0},
                  pt_cot={"1 phiên": 2, "5 phiên": 1, "21 phiên": 1, "63 phiên": 1},
                  pt_khong_dau={"Trên MA200": 0, "MA50 > MA200": 0, "Tỷ trọng GTGD": 1})
    sty = ui.them_mau_delta(sty, ["1 phiên", "5 phiên", "21 phiên", "63 phiên"])
    st.dataframe(sty, hide_index=True, use_container_width=True, height=36 * len(b) + 40)
    st.caption("Lợi suất = trung vị các mã trong ngành (một mã một phiếu). 'Qua lọc cứng' đếm trên toàn "
               "bộ — lọc cứng đã đòi ≥ 10 tỷ/phiên. Phân ngành ICB của Vietcap khá thô: 8700 gộp mọi công "
               "ty chứng khoán, 1700 gộp thép với cao su.")

    c1, c2 = st.columns([2, 3])
    with c1:
        ui.ve(bieu_do.heatmap(nganh.nhan_heatmap(b), chu_y="Lợi suất trung vị theo khung"),
              key="ng_heat")
    ngay = thi_truong.ngay_60(bq.phu)
    with c2:
        if ngay:
            ls = nganh.loi_suat_lan(bq.df, ngay, 21, tov)
            m = ui.mau()
            mac_dinh = list(b.index[:2]) + list(b.index[-1:])
            chon = st.multiselect("Ngành trên biểu đồ (tối đa 3)", list(ls.columns), default=[
                x for x in mac_dinh if x in ls.columns], max_selections=3, key="ng_chon")
            mau_ = [m["s1"], m["s2"], m["s3"]]
            fig = bieu_do.duong(ls, [(c, c, mau_[i]) for i, c in enumerate(chon)], cao=360,
                                dinh_dang=lambda x: ui.pt(x),
                                chu_y="Lợi suất 21 phiên (trung vị) tính lùi từng phiên")
            fig.add_hline(y=0, line=dict(color=m["truc"], width=1))
            fig.update_yaxes(tickformat=".0%")
            ui.ve(fig, key="ng_line")
        else:
            st.info("Bản quét phiên này không có chuỗi VN-Index nên không dựng được chuỗi theo ngày.")

    if ngay:
        c1, c2 = st.columns([2, 3])
        with c1:
            th = nganh.thu_hang(nganh.loi_suat_lan(bq.df, ngay, 21, tov), 5)
            st.markdown("##### Thứ hạng ngành: nay so với 5 phiên trước")
            if th is not None:
                th = th.reset_index()
                th["Xu hướng"] = th["Thay đổi"].map(lambda x: f"▲ {x}" if x > 0 else (f"▼ {-x}" if x < 0 else "—"))
                st.dataframe(th[["Ngành", "Hạng nay", "Hạng 5 phiên trước", "Xu hướng"]],
                             hide_index=True, use_container_width=True, height=36 * len(th) + 40)
        with c2:
            tt = nganh.ty_trong_dong_tien(bq.df, ngay).T
            tt = tt.loc[tt.mean(axis=1).sort_values(ascending=False).index]
            tt.columns = [d.strftime("%d/%m") for d in tt.columns]
            ui.ve(bieu_do.heatmap(tt.iloc[:, -20:], chu_y="Tỷ trọng giá trị khớp lệnh theo ngành — 20 phiên",
                                  phan_ky=False, dinh_dang=lambda x: ui.so(x * 100, 0)), key="ng_dongtien")
            st.caption("Số trong ô: % tổng giá trị khớp lệnh toàn thị trường của phiên đó.")

    st.markdown("##### Mã trong một ngành")
    chon_ng = st.selectbox("Ngành", list(b.index), key="ng_ma")
    d = bq.df[(bq.df["icb"].map(nganh.ten_nganh) == chon_ng) & (bq.df["tov_ty"] >= tov)].reset_index()
    d = pd.DataFrame({"Mã": d["ma"], "Sàn": d["san"].map(thi_truong.SAN_TEN), "Giá": d["c"],
                      "1 phiên": d["r1"], "21 phiên": d["r21"], "63 phiên": d["r63"],
                      "Trên MA200": d["c"] > d["ma200"], "MA50 > MA200": d["ma50"] > d["ma200"],
                      "Qua lọc cứng": d["ma"].isin(ql), "GTGD TB20 (tỷ)": d["tov_ty"]}
                     ).sort_values("GTGD TB20 (tỷ)", ascending=False)
    sty = ui.them_mau_delta(ui.bang(d, so_cot={"Giá": 0, "GTGD TB20 (tỷ)": 1},
                                    pt_cot={"1 phiên": 2, "21 phiên": 1, "63 phiên": 1}),
                            ["1 phiên", "21 phiên", "63 phiên"])
    chi_tiet.bang_chon(d, "ng_bang_ma", sty=sty, ctx=ctx, cao=min(420, 36 * len(d) + 40))
    _ro_nganh(ctx)
