"""tab_vi_mo.py — Ket luan vi mo cua ro, chuoi toan cau (Yahoo), so lieu VN nhap tay."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from dashboard import ui, vi_mo

KHUNG = {"3 tháng": 3, "1 năm": 12, "3 năm": 36}


def _the(ten, don_vi, s, d, key, thang):
    m = ui.mau()
    tt = vi_mo.tom_tat(s)
    if tt is None:
        st.markdown(f"**{ten}** — chưa có dữ liệu")
        return
    st.markdown(f"**{ten}** <span style='opacity:.65;font-size:12px'>{don_vi}</span>",
                unsafe_allow_html=True)
    st.markdown(
        f"<div style='font-size:22px;font-weight:600'>{ui.so(tt['gia_tri'], d)}</div>"
        f"<div style='font-size:12px'>"
        f"<span style='color:{ui.mau_delta(tt['r1'])}'>{ui.pt(tt['r1'], 2)} phiên</span> · "
        f"<span style='color:{ui.mau_delta(tt['r1m'])}'>{ui.pt(tt['r1m'])} 1 tháng</span> · "
        f"<span style='color:{ui.mau_delta(tt['ytd'])}'>{ui.pt(tt['ytd'])} từ đầu năm</span>"
        f"</div><div style='font-size:11px;opacity:.6'>{ui.ngay_vn(tt['ngay'].date())}</div>",
        unsafe_allow_html=True)
    tu = s.index[-1] - pd.DateOffset(months=thang)
    v = s[s.index >= tu]
    fig = go.Figure(ui.go_line(v.index, v.values, ten, m["s1"]))
    ui.khung(fig, cao=170, legend=False)
    fig.update_layout(margin=dict(l=4, r=4, t=4, b=4))
    fig.update_yaxes(tickformat=f",.{d}f")
    ui.ve(fig, key=key)


def ve(ctx):
    vm = ctx.ro.get("vi_mo") or {}
    st.markdown("##### Kết luận vĩ mô của rổ cơ bản (tầng vĩ mô, nhánh người)")
    if (vm.get("ket_luan") or "").strip():
        st.info(f"**{ui.ngay_vn(vm.get('ngay'))}** — {vm['ket_luan']}")
    else:
        ui.canh_bao("Tầng vĩ mô <b>chưa có kết luận</b> (`_ro_co_ban.vi_mo.ket_luan` trong "
                    "data/tham_dinh.json). Rổ cơ bản chưa chốt được khi thiếu tầng này.")

    st.markdown("##### Thị trường toàn cầu")
    raw = vi_mo.doc_yahoo()
    if raw is None:
        st.warning("Chưa tải chuỗi vĩ mô. Bấm **Tải lại vĩ mô** ở thanh bên.")
    else:
        kh = st.segmented_control("Khung", list(KHUNG), default="1 năm", key="vm_khung",
                                  label_visibility="collapsed") or "1 năm"
        st.caption(f"Nguồn Yahoo Finance, tải lúc {raw.get('tai_luc')}."
                   + (f" Lỗi: {', '.join(raw['loi'])}." if raw.get("loi") else ""))
        cols = st.columns(4)
        for i, (ma, ten, dv, d) in enumerate(vi_mo.YAHOO):
            with cols[i % 4]:
                _the(ten, dv, vi_mo.chuoi(raw, ma), d, f"vm_{ma}", KHUNG[kh])
        brent = vi_mo.chuoi(raw, "BZ=F")
        if brent is not None and len(brent) > 1:
            cuoi = brent.index[-1]
            bd = brent.iloc[-1] / brent.iloc[-2] - 1
            if vi_mo.la_ngay_cuoi_thang(cuoi) and abs(bd) >= 0.03:
                ui.canh_bao(f"Brent {ui.pt(bd)} ngày {ui.ngay_vn(cuoi.date())} là ngày làm việc cuối "
                            "tháng: hợp đồng kỳ gần đáo hạn/cuộn, bước nhảy có thể không phải biến động "
                            "giá thật — đối chiếu WTI.")
        st.caption("BZ=F là hợp đồng Brent kỳ gần nhất: ngày làm việc cuối tháng có thể nhảy ≥ 5% vì cuộn "
                   "hợp đồng. Đối chiếu với WTI trước khi đọc thành tin.")

    st.markdown("##### Số liệu Việt Nam (nhập tay)")
    raw_vn = vi_mo.doc_vi_mo_vn()
    if raw_vn is None:
        st.warning("Chưa có data/vi_mo.json.")
        return
    b = vi_mo.bang_vi_mo_vn(raw_vn)
    hien = b.drop(columns=["khoa", "Cũ"]).copy()

    def to_cu(row):
        cu = b.loc[row.name, "Cũ"]
        return ["background-color: rgba(250,178,25,.18)" if cu else "" for _ in row]
    sty = ui.bang(hien, so_cot={"Giá trị": 2, "Kỳ trước": 2, "Số ngày từ khi nhập": 0},
                  ngay_cot=["Ngày nhập"]).apply(to_cu, axis=1)
    st.dataframe(sty, hide_index=True, use_container_width=True)
    st.caption(f"Tô vàng: chưa nhập hoặc nhập cách đây hơn {vi_mo.NGAY_CU} ngày. Dashboard chỉ đọc — "
               "thêm kỳ mới vào cuối `chuoi` trong data/vi_mo.json (hướng dẫn ở `_huong_dan`).")
    co_chuoi = [k for k in b["khoa"] if (s := vi_mo.chuoi_vi_mo_vn(raw_vn, k)) is not None and len(s) > 1]
    if co_chuoi:
        m = ui.mau()
        cols = st.columns(3)
        for i, k in enumerate(co_chuoi):
            s = vi_mo.chuoi_vi_mo_vn(raw_vn, k)
            fig = go.Figure(ui.go_line(list(s.index), list(s.values), k, m["s1"], mode="lines+markers"))
            ui.khung(fig, cao=200, chu_y=raw_vn["chi_so"][k].get("ten", k), legend=False)
            with cols[i % 3]:
                ui.ve(fig, key=f"vmvn_{k}")
