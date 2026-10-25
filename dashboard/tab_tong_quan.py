"""tab_tong_quan.py — Mot man hinh: che do, nguong, do rong, ro xu huong, NAV, viec phai lam."""

from datetime import date, timedelta

import pandas as pd
import streamlit as st

import lt_config
from dashboard import bieu_do, chay, chi_tiet, danh_muc, nguon, pheu, ui, vi_mo
from lt_config import CHE_DO


def viec_phai_lam(ctx):
    """[(muc do, noi dung)] — muc do: 'nang' | 'vua' | 'nhe'."""
    out = []
    giu = danh_muc.vi_the_dang_giu()
    chua = danh_muc.lenh_chua_thuc_hien(ctx.ke_hoach, ctx.phien.ngay)
    for l in chua["lenh"]:
        out.append(("nang", f"**{l['Chiều']} {ui.so(l['KL'])} {l['Mã']}** × {ui.so(l['Giá'])} "
                            f"({l['DM']}) — {l['Lý do']}"
                            + (f" · {l['Phiếu']}" if l["Phiếu"] else "")))
    for c in chua["cham_tay"]:
        out.append(("vua", f"PHẢI CHẤM TAY: {ui.so(c['KL'])} {c['Mã']} ({c['DM']}) — {c['Vì sao']}"))
    for p in lt_config.PHIEU_LENH:
        tt = str(p.get("trang_thai", "")).lower()
        if tt in ("da khop", "huy", "da huy"):
            continue
        if p.get("chieu") == "BAN" and giu.get((p.get("dm"), p.get("ma")), 0) == 0:
            continue
        out.append(("vua", f"Phiếu lệnh số {p.get('so')} ({p.get('chieu')} {p.get('kl')} "
                           f"{p.get('ma')}) đang **{p.get('trang_thai')}**"
                           + (f": {p.get('khop')}" if p.get("khop") else "")))
    bu_duoc = [d for d in ctx.thieu if not chay.ten_bi_chiem(d)]
    if bu_duoc:
        out.append(("vua", f"Thiếu bản quét {len(bu_duoc)} phiên: "
                           + ", ".join(ui.ngay_vn(d) for d in bu_duoc)
                           + (" — dùng nút ở thanh bên." if ctx.local else " — chờ máy local quét bù.")))
    if not ctx.ro.get("ngay_chot"):
        out.append(("vua", "Rổ cơ bản **chưa chốt** (`_ro_co_ban.ngay_chot`) → không mã nào mua được; "
                           "chốt trước bản quét của kỳ soát đầu tiên ngoài chế độ Giảm."))
    han = date.fromisoformat(ctx.phien.ngay) + timedelta(days=30)
    for ma, v in ctx.tham_dinh.items():
        if ma.startswith("_"):
            continue
        hh = (v.get("buoc3_chi_tiet") or {}).get("het_han")
        if hh and hh <= han.isoformat():
            het = hh < ctx.phien.ngay
            out.append(("vua" if het else "nhe",
                        f"Phiếu thẩm định {ma} {'**đã hết hạn**' if het else 'sắp hết hạn'} "
                        f"{ui.ngay_vn(hh)}"))
    vn = vi_mo.bang_vi_mo_vn(vi_mo.doc_vi_mo_vn())
    if len(vn) and vn["Cũ"].any():
        out.append(("nhe", f"Vĩ mô VN: {int(vn['Cũ'].sum())}/{len(vn)} chỉ số chưa nhập hoặc cũ "
                           f"quá {vi_mo.NGAY_CU} ngày (data/vi_mo.json)."))
    return out


def ve(ctx):
    cd = ctx.che_do
    m = ui.mau()
    st_ = cd["che_do"] if cd else None
    vni = ctx.bq.vnindex
    cac_o = [("Chế độ thị trường", ui.the_che_do(st_),
              (f"từ {ui.ngay_vn(cd['tu_ngay'])} · {cd['so_phien']} phiên · trần CP "
               f"{ui.pt(cd['tran_co_phieu'], 0, dau=False)}") if cd else "bản quét thiếu chuỗi VN-Index",
              None)]
    cac_o.append(("VN-Index", ui.so(vni["c"], 2), ui.pt(vni.get("r1"), 2) + " phiên",
                  ui.mau_delta(vni.get("r1"))))
    if cd:
        if st_ == "GIAM":
            cac_o.append(("Ra khỏi Giảm khi đóng cửa >", ui.so(cd["nguong_ra_giam"], 2),
                          f"cách {ui.pt(cd['nguong_ra_giam'] / cd['dong_cua'] - 1)}", None))
        else:
            cac_o.append(("Vào Giảm khi đóng cửa <", ui.so(cd["nguong_vao_giam"], 2),
                          f"cách {ui.pt(cd['nguong_vao_giam'] / cd['dong_cua'] - 1)}", None))
        cac_o.append(("Phiên phân phối / 25", str(cd["phien_phan_phoi"]),
                      f"≥ {CHE_DO['phan_phoi']['nguong_dieu_chinh']} kéo về Điều chỉnh", None))
    dr = ctx.do_rong.loc["Toàn thị trường"]
    cac_o.append(("Mã trên MA200", ui.pt(dr["Trên MA200"], 0, dau=False),
                  f"{int(dr['Số mã'])} mã thanh khoản ≥ 1 tỷ", None))
    t = pheu.cac_tang(ctx.cands, ctx.bq, cd)
    vao, ra = pheu.thay_doi(ctx.cands, ctx.cands_truoc)
    cac_o.append(("Rổ xu hướng (qua lọc cứng)", str(len(t[1][1])),
                  (f"+{len(vao)} vào · −{len(ra)} rời so với {ui.ngay_vn(ctx.phien_truoc.ngay)}"
                   if ctx.phien_truoc else "chưa có phiên trước"), None))
    cac_o.append(("Giao điểm → được mua", f"{len(t[2][1])} → {len(t[5][1])}",
                  "giao điểm rổ xu hướng × rổ cơ bản", None))
    vt = danh_muc.vi_the_hien_tai({ma: r["c"] for ma, r in ctx.bq.df[["c"]].iterrows()})
    d2 = vt["DM2"]
    cac_o.append(("NAV DM2 (giá phiên)", ui.so(d2["nav"]),
                  f"{ui.pt(d2['nav'] / d2['von_ban_dau'] - 1)} so vốn gốc · CP "
                  f"{ui.pt(d2['co_phieu'] / d2['nav'], 0, dau=False)}",
                  ui.mau_delta(d2["nav"] - d2["von_ban_dau"])))
    ui.o_so(cac_o)

    trai, phai = st.columns([3, 2])
    with trai:
        st.markdown("##### VN-Index 6 tháng và chế độ")
        if ctx.vn is not None:
            ui.ve(bieu_do.vnindex(ctx.vn, so_phien=125, khoi_luong=False, cao=380), key="tq_vni")
        else:
            st.info("Bản quét phiên này chưa có chuỗi VN-Index (`_vnindex`) — quét lại để có chế độ.")
    with phai:
        st.markdown("##### Việc phải làm")
        viec = viec_phai_lam(ctx)
        if not viec:
            st.success("Không có việc nào tồn đọng.")
        for muc, txt in viec:
            icon = {"nang": "🔴", "vua": "🟠", "nhe": "⚪"}[muc]
            st.markdown(f"{icon} {txt}")
        if ctx.ke_hoach:
            st.caption(f"Bảng lệnh: `{ctx.ke_hoach['path'].name}` — allocator chạy "
                       f"{ui.ngay_vn(ctx.ke_hoach['ngay_chay'])} nhịp {ui.NHIP.get(ctx.ke_hoach['nhip'], ctx.ke_hoach['nhip'])}.")
        else:
            st.caption("Chưa có bảng lệnh allocator cho phiên này.")

    st.markdown("##### Rổ xu hướng: thay đổi so với phiên trước")
    if ctx.phien_truoc is None:
        st.caption("Chưa có phiên trước để so.")
    else:
        lydo = pheu.ly_do_loc_cung(ctx.bq) if ra else {}
        # Ma "moi vao" ma O PHIEN TRUOC cung da qua luat hien hanh -> khac biet do luat doi
        # (vd 04/10 bo RS/ATR), khong do gia. Chay lai ham screener tren ban quet phien truoc.
        truoc = pheu.ly_do_loc_cung(nguon.doc_ban_quet(ctx.phien_truoc)) if vao else {}
        rows = [{"Mã": x, "Thay đổi": "▲ mới vào",
                 "Ghi chú": ("luật đổi giữa hai phiên — phiên trước đã qua lọc theo luật hiện hành"
                             if truoc.get(x) == "" else "")} for x in vao]
        rows += [{"Mã": x, "Thay đổi": "▼ rời rổ", "Ghi chú": lydo.get(x, "không còn trong bản quét")}
                 for x in ra]
        if rows:
            df = pd.DataFrame(rows)
            chi_tiet.bang_chon(df, "tq_thaydoi", ctx=ctx)
        else:
            st.caption(f"Không đổi so với phiên {ui.ngay_vn(ctx.phien_truoc.ngay)}.")
