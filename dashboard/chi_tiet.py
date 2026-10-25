"""
chi_tiet.py — Hop thoai chi tiet mot ma: bieu do gia + MA + muc dinh gia, chi so
quet, checklist mua/ban (tu candidates), phieu tham dinh, vi the.

Mo tu bat ky bang nao co cot "Mã" (chon mot dong) hoac o tra ma o thanh ben.
"""

import json

import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

import lt_config
from dashboard import nguon, pheu, ui
from dashboard.nganh import ten_nganh
from dashboard.thi_truong import SAN_TEN

TEN_CHECK = {
    "liquidity": "Thanh khoản ≥ 10 tỷ/phiên", "close_above_ma200": "Giá > MA200",
    "ma50_above_ma200": "MA50 > MA200", "rs_12m_positive": "RS 12 tháng > 0 (đã tắt)",
    "atr_max": "ATR ≤ trần (đã tắt)", "close_below_97pct_ma200": "Giá < 0,97 × MA200 (kỳ soát)",
    "ngoai_ro_co_ban": "Bị loại khỏi rổ (quy tắc 4)", "cham_co_so": "Giá ≥ Cơ sở",
}


@st.cache_data(show_spinner=False, ttl=3600)
def _gia(ma, den):
    return nguon.lich_su_gia(ma, den)


def bang_chon(df, key, sty=None, cao=None, cot_ma="Mã", ctx=None, **kw):
    """st.dataframe chon mot dong -> mo hop chi tiet ma (mot lan cho moi lua chon)."""
    if cao is not None:
        kw["height"] = int(cao)
    ev = st.dataframe(sty if sty is not None else df, key=key, on_select="rerun",
                      selection_mode="single-row", hide_index=True,
                      width="stretch", **kw)
    rows = ev.selection.rows if ev is not None else []
    mo_key = f"_da_mo_{key}"
    if not rows:
        st.session_state.pop(mo_key, None)
        return
    ma = df.iloc[rows[0]][cot_ma]
    if st.session_state.get(mo_key) != ma and ctx is not None:
        st.session_state[mo_key] = ma
        mo(ma, ctx)


def _bieu_do(ma, ctx, td, cand):
    try:
        g = _gia(ma, ctx.phien.ngay)
    except Exception as e:          # cloud o nuoc ngoai co the khong goi duoc Vietcap
        g = None
        st.caption(f"Lỗi tải giá Vietcap: {str(e)[:120]}")
    if g is None or len(g) == 0:
        st.info("Không tải được lịch sử giá từ Vietcap — các phần còn lại vẫn đúng theo bản quét.")
        return
    m = ui.mau()
    g = g.copy()
    g["ngay"] = g["ngay"].astype("datetime64[ns]")
    g["ma50"] = g["c"].rolling(50).mean()
    g["ma200"] = g["c"].rolling(200).mean()
    g = g.tail(500)
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.78, 0.22],
                        vertical_spacing=0.03)
    fig.add_trace(ui.go_line(g["ngay"], g["c"], "Giá đóng cửa", m["s1"]), 1, 1)
    fig.add_trace(ui.go_line(g["ngay"], g["ma50"], "MA50", m["s2"], 1.5), 1, 1)
    fig.add_trace(ui.go_line(g["ngay"], g["ma200"], "MA200", m["s3"], 1.5), 1, 1)
    fig.add_trace(go.Scatter(x=g["ngay"], y=0.97 * g["ma200"], name="0,97 × MA200",
                             mode="lines", line=dict(color=m["chu_3"], width=1, dash="dot")), 1, 1)
    dg = (td or {}).get("dinh_gia") or {}
    muc = []
    if dg.get("than_trong"):
        muc += [(0.85 * dg["than_trong"] * 1000, "Mua khi ≤ 0,85 × Thận trọng"),
                (dg["than_trong"] * 1000, "Thận trọng")]
    if dg.get("co_so"):
        muc.append((dg["co_so"] * 1000, "Cơ sở — bán khi chạm"))
    for y, nhan in muc:
        fig.add_hline(y=y, line=dict(color=m["chu_2"], width=1, dash="dash"), row=1, col=1,
                      annotation_text=f"{nhan} {ui.so(y)}", annotation_position="top left",
                      annotation_font=dict(size=11, color=m["chu_2"]))
    for ma_, kl, gv in lt_config.HOLDINGS.get("DM2", []) + lt_config.HOLDINGS.get("DM1", []):
        if ma_ == ma and gv:
            fig.add_hline(y=gv, line=dict(color=m["chu_3"], width=1), row=1, col=1,
                          annotation_text=f"Giá vốn {ui.so(gv)} · chặn −25% {ui.so(gv * .75)}",
                          annotation_position="bottom left",
                          annotation_font=dict(size=11, color=m["chu_3"]))
    fig.add_trace(go.Bar(x=g["ngay"], y=g["v"], name="Khối lượng", marker_color=m["chu_3"],
                         showlegend=False), 2, 1)
    ui.khung(fig, cao=440)
    fig.update_yaxes(tickformat=",.0f", side="right")
    ui.ve(fig, key=f"ct_{ma}")
    st.caption("Giá Vietcap đã điều chỉnh cổ tức — có thể lệch giá thô vài phần trăm trước ngày GDKHQ.")


def _phieu(ma, td):
    if not td:
        st.info("Chưa có bản ghi thẩm định trong data/tham_dinh.json → chưa thẩm định = không được mua.")
        return
    ct = td.get("buoc3_chi_tiet") or {}
    d = pheu.diem(td)
    cols = st.columns(4)
    cols[0].metric("Bước 3", td.get("buoc3_tham_dinh", "chua"))
    cols[1].metric("Bước 4", td.get("buoc4_dinh_gia", "chua"))
    cols[2].metric("Khuyến nghị", td.get("khuyen_nghi") or "—")
    cols[3].metric("Phiếu", ct.get("ket_qua") or "chưa có",
                   help=f"Lập {ui.ngay_vn(ct.get('ngay_lap'))} · hết hạn {ui.ngay_vn(ct.get('het_han'))}"
                   if ct else None)
    if ct:
        st.caption(f"Phiếu lập {ui.ngay_vn(ct.get('ngay_lap'))} bởi {ct.get('nguoi_lap', '?')} — "
                   f"hết hạn {ui.ngay_vn(ct.get('het_han'))}")
    if d:
        st.markdown(f"**Ba trục:** A kinh tế DN **{d.get('A_kinh_te_doanh_nghiep', '?')}** · "
                    f"B độ bền lợi thế **{d.get('B_do_ben_loi_the', '?')}** · "
                    f"C quản trị **{d.get('C_quan_tri_phan_bo_von', '?')}** → tổng **{d.get('tong', '?')}**/6")
    cg = pheu.cong(td)
    if cg:
        import pandas as pd
        df = pd.DataFrame([{"Cổng": k.replace("_", " "), "Trạng thái":
                            {"BAT": "⛔ BẬT", "KHONG BAT": "✓ không bật"}.get(t, "?"),
                            "Ghi chú": v[:220] + ("…" if len(v) > 220 else "")}
                           for k, t, v in cg])
        st.dataframe(df, hide_index=True, width="stretch")
    dg = td.get("dinh_gia") or {}
    st.markdown(
        f"**Định giá (nghìn đ/CP):** Thận trọng {ui.so(dg.get('than_trong'), 1)} · "
        f"Cơ sở {ui.so(dg.get('co_so'), 1)} · Upside {ui.so(dg.get('upside'), 1)}"
        + (" · ⚠️ cần dựng lại" if dg.get("can_dung_lai") else ""))
    if td.get("luan_diem"):
        with st.expander("Luận điểm (ghi lúc mua)"):
            st.write(td["luan_diem"])
    db = pheu.day_bay(td)
    if db:
        import pandas as pd
        st.markdown("**Dây bẫy luận điểm** — chạm ngưỡng nghĩa là luận điểm gãy:")
        st.dataframe(pd.DataFrame(db), hide_index=True, width="stretch")
    with st.expander("Toàn bộ bản ghi thẩm định (JSON)"):
        st.code(json.dumps(td, ensure_ascii=False, indent=1), language="json")


@st.dialog("Chi tiết mã", width="large")
def mo(ma, ctx):
    df = ctx.bq.df
    r = df.loc[ma] if ma in df.index else None
    td = ctx.tham_dinh.get(ma)
    cand = next((c for c in ctx.cands or [] if c["ma"] == ma), None)
    db = nguon.danh_ba_ma().get(ma, {})
    san = r["san"] if r is not None else db.get("san")
    icb = r["icb"] if r is not None else db.get("icb")
    st.markdown(f"### {ma} — {db.get('ten', '')}")
    st.caption(f"{SAN_TEN.get(san, san or '?')} · {ten_nganh(icb)} (ICB {icb or '?'})"
               + (f" · ngành rổ: {td.get('nganh')}" if td and td.get("nganh") else "")
               + f" · dữ liệu phiên {ui.ngay_vn(ctx.phien.ngay)}")
    if r is None:
        st.warning("Mã không có trong bản quét của phiên này (dừng giao dịch hoặc chưa niêm yết).")
    else:
        ui.o_so([
            ("Giá", ui.so(r["c"]), "phiên: " + ui.pt(r["r1"], 2), ui.mau_delta(r["r1"])),
            ("21 phiên", ui.pt(r["r21"]), None, None),
            ("63 phiên", ui.pt(r["r63"]), None, None),
            ("252 phiên", ui.pt(r["r252"]), None, None),
            ("MA50 / MA200", f"{ui.so(r['ma50'])} / {ui.so(r['ma200'])}",
             "giá " + ("trên" if r["ma200"] and r["c"] > r["ma200"] else "dưới") + " MA200", None),
            ("ATR 14", ui.pt(r["atr"], 2, dau=False), None, None),
            ("GTGD TB20", ui.so(r["tov_ty"], 1) + " tỷ", None, None),
        ])
    _bieu_do(ma, ctx, td, cand)
    if cand:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Checklist mua** (screener)")
            for k, ok in cand.get("buy_checklist", []):
                st.markdown(f"{'✅' if ok else '❌'} {TEN_CHECK.get(k, k)}")
            st.markdown(f"{'✅' if cand.get('trong_ro_co_ban') is True else '❌'} Trong rổ cơ bản"
                        + (f" — {cand.get('ly_do_ro')}" if cand.get("ly_do_ro") else ""))
            st.markdown(f"{'✅' if cand.get('phieu_ok') else '❌'} Phiếu qua (Đạt/Chờ) còn hạn"
                        + (f" — {cand.get('ly_do_phieu')}" if cand.get("ly_do_phieu") else ""))
            st.markdown(f"{'✅' if cand.get('bien_an_toan_ok') else '❌'} Biên an toàn ≥ "
                        f"{lt_config.BIEN_AN_TOAN_MIN:.0%}"
                        + (f" — {cand.get('ly_do_bien')}" if cand.get("ly_do_bien") else ""))
        with c2:
            st.markdown("**Checklist bán** (screener; chế độ và −25% xét ở allocator)")
            for k, ok in cand.get("sell_checklist", []):
                st.markdown(f"{'🔴' if ok else '⚪'} {TEN_CHECK.get(k, k)}")
    for pk, ds in lt_config.HOLDINGS.items():
        for ma_, kl, gv in ds:
            if ma_ == ma:
                gia = r["c"] if r is not None else None
                st.info(f"**Đang giữ ({pk}):** {ui.so(kl)} CP, giá vốn {ui.so(gv)}"
                        + (f", lãi/lỗ {ui.pt(gia / gv - 1)}" if gia and gv else ""))
    st.markdown("#### Thẩm định")
    _phieu(ma, td)
