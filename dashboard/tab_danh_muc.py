"""tab_danh_muc.py — NAV, vi the, bang lenh, phieu lenh, so giao dich, lai/lo, chi phi, so ngoai luat."""

import pandas as pd
import streamlit as st

import lt_config
from dashboard import bieu_do, chi_tiet, danh_muc, nguon, ui


@st.cache_data(show_spinner="Đang dựng đường NAV từ sổ giao dịch…", ttl=3600)
def _nav(den, chu_ky):
    so = nguon.doc_so_giao_dich()
    vni = nguon.lich_su_gia("VNINDEX", den)
    ngay = [d for d in vni["ngay"] if danh_muc.NGAY_BAT_DAU_NAV <= d <= den]
    gia = {}
    for ma in danh_muc.ma_tung_giu(so):
        g = nguon.lich_su_gia(ma, den)
        # Ma khong khop lenh mot phien -> lay gia dong cua gan nhat truoc do.
        gia[ma] = pd.Series(g["c"].values, index=g["ngay"]).reindex(
            sorted(set(g["ngay"]) | set(ngay))).ffill()
    he_so = danh_muc.he_so_tu_gia_khop(gia, so)
    nav = danh_muc.chuoi_nav(gia, ngay, so, he_so).set_index("ngay")
    e1 = nguon.lich_su_gia("E1VFVN30", den)
    nav["VN-Index"] = pd.Series(vni["c"].values, index=vni["ngay"]).reindex(nav.index)
    nav["E1VFVN30"] = pd.Series(e1["c"].values, index=e1["ngay"]).reindex(nav.index).ffill()
    nav.attrs["he_so"] = he_so
    return nav


def _bieu_do_nav(ctx):
    try:
        nav = _nav(ctx.phien.ngay, ctx.chu_ky)
    except Exception as e:
        st.warning(f"Không dựng được đường NAV (cần mạng để tải giá Vietcap): {e}")
        return
    if nav.empty:
        st.info("Chưa đủ dữ liệu giá để dựng NAV.")
        return
    m = ui.mau()
    goc = nav.iloc[0]
    chi_so = pd.DataFrame({"NAV DM2": nav["nav"] / goc["nav"] * 100,
                           "VN-Index": nav["VN-Index"] / goc["VN-Index"] * 100,
                           "E1VFVN30": nav["E1VFVN30"] / goc["E1VFVN30"] * 100})
    chi_so.index = pd.to_datetime(chi_so.index)
    fig = bieu_do.duong(chi_so, [("NAV DM2", "NAV DM2", m["s1"]), ("VN-Index", "VN-Index", m["s2"]),
                                 ("E1VFVN30", "E1VFVN30", m["s3"])], cao=360,
                        dinh_dang=lambda x: ui.so(x, 1))
    fig.add_hline(y=100, line=dict(color=m["truc"], width=1))
    fig.update_traces(customdata=nav[["nav", "tien_mat", "co_phieu"]].to_numpy(),
                      selector=dict(name="NAV DM2"),
                      hovertemplate="NAV DM2 %{y:.1f} · %{customdata[0]:,.0f} đ "
                                    "(tiền %{customdata[1]:,.0f})<extra></extra>")
    ui.ve(fig, key="dm_nav")
    cuoi = chi_so.iloc[-1]
    st.caption(
        f"Gốc 100 = đóng cửa {ui.ngay_vn(nav.index[0])} (phiên đầu đủ vị thế khung dài hạn). Từ đó: "
        f"NAV {ui.pt(cuoi['NAV DM2'] / 100 - 1)}, VN-Index {ui.pt(cuoi['VN-Index'] / 100 - 1)}, "
        f"E1VFVN30 {ui.pt(cuoi['E1VFVN30'] / 100 - 1)}. Tái dựng từ sổ + giá Vietcap đã điều chỉnh: "
        "MSB quy đổi 1,2 trước 28/08"
        + "".join(f"; {ma} nhân lại ×{ui.so(k, 2)} tới {ui.ngay_vn(d)} (giá Vietcap đã chia lùi vì sự "
                  "kiện cổ phiếu sau khi Quỹ bán — tỷ lệ đo từ giá khớp trong sổ)"
                  for ma, (k, d) in nav.attrs.get("he_so", {}).items())
        + "; cổ tức tiền (DHC) làm giá trước ngày GDKHQ thấp hơn giá thô vài phần trăm. Tiền mặt theo "
        "sổ (không gồm lãi tiền gửi/phí lặt vặt, lệch sao kê 241 đ ngày 18/09).")


def _bang_lenh(ctx):
    kh = ctx.ke_hoach
    if not kh:
        st.info("Chưa có bảng lệnh allocator cho phiên này. Nút **Quét phiên hôm nay** chạy allocator "
                "nhịp hằng ngày và ghi data/ke_hoach_YYYYMMDD.txt.")
        return
    st.caption(f"`{kh['path'].name}` — chạy {ui.ngay_vn(kh['ngay_chay'])}, nhịp {ui.NHIP.get(kh['nhip'], kh['nhip'])}.")
    L = kh["lenh"]
    if L["lenh"]:
        df = pd.DataFrame(L["lenh"])
        chi_tiet.bang_chon(df, "dm_lenh", sty=ui.bang(df, so_cot={"KL": 0, "Giá": 0, "Giá trị": 0,
                                                                  "Phí": 0}), ctx=ctx)
    else:
        st.success("Không có lệnh.")
    for k in L["khong_mua"]:
        st.caption(f"[KHÔNG MUA] {k['DM']}: {k['Lý do']}")
    if L["cham_tay"]:
        st.markdown("**PHẢI CHẤM TAY** — không tự động bán, sửa dữ liệu rồi chạy lại:")
        st.dataframe(ui.bang(pd.DataFrame(L["cham_tay"]), so_cot={"KL": 0, "Giá vốn": 0}),
                     hide_index=True, use_container_width=True)
    with st.expander("Toàn văn bảng lệnh"):
        st.code(kh["path"].read_text(encoding="utf-8", errors="replace"), language=None)


def ve(ctx):
    so = nguon.doc_so_giao_dich()
    vt = danh_muc.vi_the_hien_tai({ma: r for ma, r in ctx.bq.df["c"].items()})
    d1, d2 = vt["DM1"], vt["DM2"]
    ui.o_so([
        ("NAV DM2 (giá phiên)", ui.so(d2["nav"]), f"{ui.pt(d2['nav'] / d2['von_ban_dau'] - 1)} so vốn gốc "
         f"{ui.so(d2['von_ban_dau'])}", ui.mau_delta(d2["nav"] - d2["von_ban_dau"])),
        ("Cổ phiếu DM2", ui.so(d2["co_phieu"]), ui.pt(d2["co_phieu"] / d2["nav"], 1, dau=False) + " NAV", None),
        ("Tiền mặt DM2", ui.so(d2["tien_mat"]), ui.pt(d2["tien_mat"] / d2["nav"], 1, dau=False) + " NAV", None),
        ("Lãi/lỗ đã thực hiện (sổ)", ui.so(so["tong_ket"]["lai_lo_da_thuc_hien_rong"]),
         "ròng sau phí và thuế", ui.mau_delta(so["tong_ket"]["lai_lo_da_thuc_hien_rong"])),
        ("Chi phí giao dịch", ui.so(so["tong_ket"]["tong_chi_phi_giao_dich"]),
         f"{ui.so(so['tong_ket']['chi_phi_tren_von_goc_pct'], 2)}% vốn gốc", None),
        ("DM1 — tiền thật", "chưa có vốn" if d1["nav"] <= 0 else ui.so(d1["nav"]),
         "HOLDINGS rỗng, TIEN_MAT = 0" if d1["nav"] <= 0 else None, None),
    ])

    st.markdown("##### NAV DM2 so với VN-Index và E1VFVN30 (gốc 100)")
    _bieu_do_nav(ctx)

    c1, c2 = st.columns([3, 2])
    with c1:
        st.markdown("##### Bảng lệnh của phiên")
        _bang_lenh(ctx)
    with c2:
        st.markdown("##### Vị thế đang giữ (lt_config.HOLDINGS)")
        for pk in ("DM2", "DM1"):
            rows = vt[pk]["vi_the"]
            if rows:
                df = pd.DataFrame(rows)
                sty = ui.them_mau_delta(ui.bang(df, so_cot={"KL": 0, "Giá vốn": 0, "Giá": 0, "Giá trị": 0},
                                                pt_cot={"Lãi/lỗ %": 1}), ["Lãi/lỗ %"])
                st.markdown(f"**{pk}**")
                chi_tiet.bang_chon(df, f"dm_vt_{pk}", sty=sty, ctx=ctx)
            else:
                st.caption(f"{pk}: không có vị thế.")
        for e in so.get("vi_the_dang_giu", []):
            if e.get("ghi_chu"):
                st.caption(f"{e['ma']}: {e['ghi_chu']}")

    st.markdown("##### Phiếu lệnh (ghi trước giờ đặt)")
    if lt_config.PHIEU_LENH:
        df = pd.DataFrame(lt_config.PHIEU_LENH)
        cot = [c for c in ["so", "ghi_luc", "ngay_dat", "dm", "chieu", "ma", "kl", "trang_thai", "khop",
                           "can_cu", "ghi_chu"] if c in df.columns]
        df = df[cot].rename(columns={"so": "Số", "ghi_luc": "Ghi lúc", "ngay_dat": "Ngày đặt", "dm": "DM",
                                     "chieu": "Chiều", "ma": "Mã", "kl": "KL", "trang_thai": "Trạng thái",
                                     "khop": "Khớp", "can_cu": "Căn cứ", "ghi_chu": "Ghi chú"})
        st.dataframe(df, hide_index=True, use_container_width=True)
    else:
        st.caption("Chưa có phiếu lệnh.")

    st.markdown("##### Lãi/lỗ đã thực hiện theo lệnh bán")
    ll = danh_muc.lai_lo_da_thuc_hien(so)
    sty = ui.them_mau_delta(ui.bang(ll, so_cot={"KL": 0, "Giá bán": 0, "Giá vốn BQ": 0, "Thu ròng": 0,
                                                "Lãi/lỗ": 0}, pt_cot={"% trên vốn": 1},
                                    ngay_cot=["Ngày"]), ["Lãi/lỗ", "% trên vốn"])
    chi_tiet.bang_chon(ll, "dm_ll", sty=sty, ctx=ctx)
    st.caption(f"Tổng {ui.so(ll['Lãi/lỗ'].sum())} đ theo giá vốn bình quân gồm phí mua; sổ ghi "
               f"{ui.so(so['tong_ket']['lai_lo_da_thuc_hien_rong'])} đ (chênh do làm tròn giá vốn).")

    with st.expander(f"Sổ giao dịch DM2 — {len(so['giao_dich'])} lệnh (data/so_giao_dich.json)"):
        df = pd.DataFrame(so["giao_dich"])
        cot = [c for c in ["ngay", "loai", "ma", "kl", "gia", "gia_tri", "phi_dich_vu", "thue",
                           "dong_tien", "du_tien_mat_sau", "can_cu", "ghi_chu"] if c in df.columns]
        st.dataframe(ui.bang(df[cot], so_cot={c: 0 for c in ["kl", "gia", "gia_tri", "phi_dich_vu", "thue",
                                                            "dong_tien", "du_tien_mat_sau"]}),
                     hide_index=True, use_container_width=True)
        tk = so["tong_ket"]
        st.caption(f"Phí dịch vụ {ui.so(tk['tong_phi_dich_vu'])} · thuế TNCN {ui.so(tk['tong_thue_tncn'])} · "
                   f"phí lưu ký ước tính {ui.so(so.get('phi_luu_ky', {}).get('cong'))} (chưa trừ khỏi sổ).")
    with st.expander(f"Sổ lệnh ngoài luật ({len(lt_config.LENH_NGOAI_LUAT)}) — người quyết, hệ thống không sinh"):
        for L in lt_config.LENH_NGOAI_LUAT:
            st.markdown(f"**#{L.get('so')} {ui.ngay_vn(L.get('ngay'))} {L.get('ma')}** [{L.get('trang_thai')}] — "
                        f"{L.get('ten')}  \n{L.get('viec')}  \n_Kết thúc:_ {L.get('ket_thuc') or '—'}")
    with st.expander(f"Sổ lệnh quy tắc 5 ({len(lt_config.LENH_QUY_TAC_5)}) — đã bỏ từ "
                     f"{ui.ngay_vn(lt_config.QUY_TAC_5.get('het_hieu_luc_tu'))}, chỉ còn là hồ sơ"):
        df = pd.DataFrame(lt_config.LENH_QUY_TAC_5)
        st.dataframe(df, hide_index=True, use_container_width=True)
