"""tab_co_phieu.py — Pheu chinh thuc (chi doc), ro co ban, ma dang giu + checklist ban."""

import pandas as pd
import streamlit as st

import lt_config
from dashboard import chi_tiet, pheu, ui
from dashboard.nganh import ten_nganh


def _pheu(tang):
    """Dai o so theo tang. Khong ve pheu: 1.265 -> 27 -> 0 lam cac tang duoi vo hinh."""
    cac_o, truoc = [], None
    for i, (ten, ds) in enumerate(tang):
        n = len(ds)
        phu = None if truoc is None else (f"{ui.pt(n / truoc, 1, dau=False)} tầng trước"
                                         if truoc else "—")
        cac_o.append((f"{i}. {ten}", ui.so(n), phu, None))
        truoc = n
    ui.o_so(cac_o)


def _ro_co_ban(ctx):
    rows = []
    for ma, v in ctx.tham_dinh.items():
        if ma.startswith("_"):
            continue
        ct = v.get("buoc3_chi_tiet") or {}
        dg = v.get("dinh_gia") or {}
        c = next((x for x in ctx.cands or [] if x["ma"] == ma), {})
        d = pheu.diem(v) or {}
        rows.append({"Mã": ma, "Bước 3": v.get("buoc3_tham_dinh"), "Bước 4": v.get("buoc4_dinh_gia"),
                     "Khuyến nghị": v.get("khuyen_nghi"), "Phiếu": ct.get("ket_qua") or "—",
                     "Điểm": d.get("tong"), "Hết hạn": ct.get("het_han"),
                     "Thận trọng": dg.get("than_trong"), "Cơ sở": dg.get("co_so"),
                     "Giá": c.get("gia"), "Trong rổ": {True: "✓", False: "✗", None: "?"}.get(
                         c.get("trong_ro_co_ban")),
                     "Vì sao chưa": c.get("ly_do_ro", "")})
    df = pd.DataFrame(rows)
    sty = ui.bang(df, so_cot={"Thận trọng": 1, "Cơ sở": 1, "Giá": 0, "Điểm": 0}, ngay_cot=["Hết hạn"])
    chi_tiet.bang_chon(df, "cp_ro", sty=sty, ctx=ctx)
    st.caption("Định giá tính bằng nghìn đồng/CP. Chỉ phiếu **Đạt còn hạn** + Bước 4 `dat` + giá ≤ 0,85 × "
               "Thận trọng mới mua được (mục 14). Nhãn không có phiếu không đủ.")


def _dang_giu(ctx):
    cd = ctx.che_do
    by = {c["ma"]: c for c in ctx.cands or []}
    rows = []
    for pk, ds in lt_config.HOLDINGS.items():
        for ma, kl, gv in ds:
            c = by.get(ma, {})
            gia = c.get("gia") or (ctx.bq.df.loc[ma, "c"] if ma in ctx.bq.df.index else None)
            sc = dict(c.get("sell_checklist", []))
            rows.append({
                "DM": pk, "Mã": ma, "KL": kl, "Giá vốn": gv, "Giá": gia,
                "Lãi/lỗ": None if not gia or not gv else gia / gv - 1,
                "Chế độ Giảm": "🔴 bán" if cd and cd["che_do"] == "GIAM" else "—",
                "Chặn −25%": "🔴 bán" if gia and gv and gia <= gv * (1 - lt_config.EXIT["stop_tham_hoa"]) else "—",
                "Chạm Cơ sở": "🔴 bán" if sc.get("cham_co_so") else ("? thiếu Cơ sở" if c.get("thieu_co_so") else "—"),
                "Quy tắc 4": "🔴 bán" if sc.get("ngoai_ro_co_ban") else (
                    "? chấm tay" if c.get("thieu_ra_soat_ro") else "—"),
                "< 0,97×MA200 (kỳ soát)": "🔴" if sc.get("close_below_97pct_ma200") else "—",
            })
    if not rows:
        st.caption("Không có vị thế nào.")
        return
    df = pd.DataFrame(rows)
    sty = ui.them_mau_delta(ui.bang(df, so_cot={"KL": 0, "Giá vốn": 0, "Giá": 0},
                                    pt_cot={"Lãi/lỗ": 1}), ["Lãi/lỗ"])
    chi_tiet.bang_chon(df, "cp_giu", sty=sty, ctx=ctx)
    st.caption("Một ô 🔴 là bán toàn bộ. Chế độ, −25%, chạm Cơ sở, quy tắc 4 xét mỗi phiên; MA200 chỉ xét "
               "ở kỳ soát đầu tháng. Lệnh thật lấy từ bảng lệnh allocator ở tab Danh mục.")


def ve(ctx):
    cd = ctx.che_do
    tang = pheu.cac_tang(ctx.cands, ctx.bq, cd)
    if ctx.cands is None:
        st.warning("Phiên này chưa có candidates_*.json — chạy screener (nút quét) để có phễu.")
    st.markdown("##### Phễu chọn mã của Quỹ")
    _pheu(tang)
    ro = pheu.ro_co_ban(ctx.cands)
    st.caption(f"Nhánh người — rổ cơ bản: **{len(ro)} mã** "
               + ("(rổ chưa chốt)" if not ctx.ro.get("ngay_chot") else
                  f"(chốt {ui.ngay_vn(ctx.ro['ngay_chot'])})")
               + ". Phễu đọc nguyên kết quả screener của phiên, không tính lại.")
    st.markdown("##### Xem một tầng")
    ten = st.segmented_control("Tầng", [t for t, _ in tang[1:]], default=tang[1][0],
                               key="cp_tang", label_visibility="collapsed") or tang[1][0]
    i = [t for t, _ in tang].index(ten)
    ds = tang[i][1]
    if not ds:
        st.info(f"Tầng **{ten}** không có mã nào.")
    else:
        df = pheu.bang_ma(ds, lambda c: {"Ngành": ten_nganh(c.get("icb"))})
        sty = ui.bang(df, so_cot={"Giá": 0, "MA50": 0, "MA200": 0, "Thanh khoản (tỷ)": 1},
                      pt_cot={"RS 12T": 1, "Biên an toàn": 1}, pt_khong_dau={"ATR": 2})
        chi_tiet.bang_chon(df, f"cp_tang_{i}", sty=sty, ctx=ctx, cao=min(460, 36 * len(df) + 40))
    if i < len(tang) - 1 and ds:
        con = {c["ma"] for c in tang[i + 1][1]}
        rot = [c for c in ds if c["ma"] not in con]
        if rot:
            with st.expander(f"{len(rot)} mã dừng ở tầng này — vì sao chưa sang '{tang[i + 1][0]}'"):
                df = pd.DataFrame([{"Mã": c["ma"], "Vì sao": pheu.ly_do_rot(c, i + 1, cd)}
                                   for c in rot])
                st.dataframe(df, hide_index=True, width="stretch")

    with st.expander("Vì sao các mã rớt lọc cứng (toàn thị trường)"):
        lydo = pheu.ly_do_loc_cung(ctx.bq)
        dem = pd.Series([x for v in lydo.values() if v for x in v.split(", ")]).map(
            lambda s: "thanh khoản < 10 tỷ" if s.startswith("thanh khoan") else s).value_counts()
        st.dataframe(dem.rename("Số mã").rename_axis("Lý do").reset_index(), hide_index=True)
        st.caption("Một mã có thể rớt nhiều điều kiện cùng lúc.")

    st.markdown("##### Mã đang giữ — checklist bán mỗi phiên")
    _dang_giu(ctx)
    st.markdown("##### Rổ cơ bản và thẩm định (data/tham_dinh.json)")
    _ro_co_ban(ctx)
