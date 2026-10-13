"""
app.py — Buong lai van hanh cua Quy (Streamlit, chi doc).

Chay: chay_dashboard.bat  (hoac: .venv\\Scripts\\streamlit run dashboard/app.py)
Xem dashboard/README.md.
"""

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st  # noqa: E402

from dashboard import (chay, chi_tiet, danh_muc, nguon, tab_co_phieu, tab_danh_muc,  # noqa: E402
                       tab_kham_pha, tab_nganh, tab_thi_truong, tab_tong_quan, tab_vi_mo,
                       thi_truong, ui, vi_mo)

nguon.ve_goc()
st.set_page_config(page_title="Medici Terminal", page_icon="▣", layout="wide")
ui.nap_css()


# ------------------------------------------------------------------ du lieu (cache)
def chu_ky():
    """Chu ky file nguon: doi khi bat ky file pipeline nao doi -> cache tu xoa."""
    fs = [f for pat in ("scan_*.json", "candidates_*.json", "che_do_*.json", "ke_hoach_*.txt")
          for f in nguon.DATA.glob(pat)]
    fs += [nguon.DATA / "tham_dinh.json", nguon.DATA / "so_giao_dich.json", nguon.VI_MO_FILE,
           ROOT / "lt_config.py"]
    return tuple(sorted((f.name, f.stat().st_mtime) for f in fs if f.exists()))


@st.cache_data(show_spinner=False)
def _ds_phien(ck):
    return nguon.danh_sach_phien()


@st.cache_data(show_spinner="Đang đọc bản quét…")
def _ban_quet(ngay, ck):
    p = next(p for p in nguon.danh_sach_phien() if p.ngay == ngay)
    return nguon.doc_ban_quet(p)


@st.cache_data(show_spinner=False)
def _cands(ngay, ck):
    p = next((p for p in nguon.danh_sach_phien() if p.ngay == ngay), None)
    return nguon.doc_candidates(p) if p else None


@st.cache_data(show_spinner=False, ttl=900)
def _ngay_gd():
    return nguon.ngay_giao_dich_vnindex()


@st.cache_resource(show_spinner=False)
def _danh_ba_lan_dau():
    """Ten cong ty: tai mot lan neu chua co cache (mot request Vietcap); loi mang thi bo qua."""
    if not nguon.danh_ba_ma():
        try:
            nguon.tai_danh_ba_ma()
        except Exception:
            pass
    return True


@st.cache_data(show_spinner=False, ttl=3600)
def _vi_mo_tu_dong():
    """Chuoi Yahoo: tu tai neu chua co hoac cu hon 12 gio (ban cloud khong co cache dia)."""
    raw = vi_mo.doc_yahoo()
    try:
        cu = raw is None or (datetime.now() - datetime.strptime(raw["tai_luc"], "%Y-%m-%d %H:%M")
                             ).total_seconds() > 12 * 3600
        if cu:
            vi_mo.tai_yahoo()
    except Exception:
        pass
    return True


def la_may_local():
    """Nut quet / quet bu / day GitHub chi hien khi mo tu chinh may (localhost).

    Moi truy cap khac — Streamlit Cloud, nguoi duoc moi xem — la ban CHI DOC (chot 07/10/2026):
    o dia cloud bi xoa moi lan khoi dong lai nen ban quet tren do khong ve GitHub, va nguoi xem
    khong duoc kich mot lan quet 1.500 request. Khong doc duoc Host -> coi la chi doc.
    DASHBOARD_CHI_DOC=1 ep che do chi doc ngay tren may (xem truoc ban cloud).
    """
    if os.environ.get("DASHBOARD_CHI_DOC") == "1":
        return False
    try:
        host = (st.context.headers.get("Host") or "").rsplit(":", 1)[0].strip("[]").lower()
    except Exception:
        return False
    # medici-ptdttc: ten mien local trong file hosts -> 127.0.0.1 (xem chay_dashboard.bat)
    return host in ("localhost", "127.0.0.1", "::1", "medici-ptdttc") or host.endswith(".localhost")


@st.cache_data(show_spinner=False)
def _vn(ngay, ck):
    return thi_truong.chuoi_vnindex(_ban_quet(ngay, ck).phu)


@st.cache_data(show_spinner=False)
def _do_rong(ngay, ck):
    return thi_truong.do_rong(_ban_quet(ngay, ck).df, 1.0)


# ------------------------------------------------------------------ chay pipeline
def chay_lenh(args, nhan):
    with st.status(nhan, expanded=True) as s:
        o = st.empty()
        dong = []
        p = subprocess.Popen([sys.executable, "-m", "dashboard.chay", *args], cwd=ROOT,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                             encoding="utf-8", errors="replace", env=chay._env())
        for x in p.stdout:
            dong.append(x.rstrip())
            o.code("\n".join(dong[-25:]), language=None)
        p.wait()
        ok = p.returncode == 0
        s.update(label=f"{nhan} — {'xong' if ok else 'CÓ LỖI'}", state="complete" if ok else "error")
    st.session_state["nhat_ky"] = (datetime.now().strftime("%H:%M:%S"), nhan, ok, "\n".join(dong))
    st.cache_data.clear()
    if ok:
        st.session_state.pop("phien", None)     # ve phien moi nhat vua quet
        st.rerun()


def thanh_ben(ds, ngay_gd, local):
    sb = st.sidebar
    sb.markdown("## MEDICI ▸ BUỒNG LÁI")
    if not ds:
        return None, []
    nhan = {p.ngay: f"{ui.ngay_vn(p.ngay)}" for p in ds}
    chon = sb.selectbox("Phiên dữ liệu", [p.ngay for p in reversed(ds)], format_func=nhan.get,
                        key="phien")
    phien = next(p for p in ds if p.ngay == chon)
    sb.caption(f"`{phien.scan.name}` · quét lúc {phien.chay_luc}")

    thieu = nguon.phien_thieu(ds, ngay_gd)
    moi_nhat = ngay_gd[-1] if ngay_gd else None
    sb.divider()
    if not local:
        sb.info("Bản cloud — **chỉ đọc**. Số liệu cập nhật khi máy của Quỹ quét rồi bấm "
                "**Đẩy lên GitHub**.")
        if sb.button("↻ Tải lại vĩ mô", width="stretch"):
            chay_lenh(["vi_mo"], "Tải lại vĩ mô")
        _tra_ma(sb)
        return phien, thieu
    dang = chay.dang_chay()
    if dang:
        sb.warning("Đang có một lần quét chạy (khoá data/cache_dashboard/dang_chay.lock).")
    if datetime.now().hour < 15:
        sb.caption("Trước 15:00: phiên đang chạy sẽ bị bỏ — bản quét chỉ tới phiên trước.")
    if sb.button("▶ Quét phiên hôm nay", type="primary", disabled=dang, width="stretch",
                 help="Quét toàn thị trường (Vietcap) → screener → allocator nhịp hằng ngày → vĩ mô. ~2–3 phút."):
        chay_lenh(["hom_nay"], "Quét phiên hôm nay")
    # Phien moi nhat do nut "Quet phien hom nay" lo; phien co ten file bi chiem thi khong bu duoc.
    chiem = {d: chay.ten_bi_chiem(d) for d in thieu}
    khong_bu = {d: x for d, x in chiem.items() if x}
    bu = [d for d in thieu if d != moi_nhat and d not in khong_bu]
    if khong_bu:
        sb.caption("Không bù được: " + "; ".join(
            f"{ui.ngay_vn(d)} (scan_{d.replace('-', '')}.json đang chứa phiên {ui.ngay_vn(x)} — "
            "quy ước tên cũ theo ngày chạy)" for d, x in khong_bu.items()))
    if bu:
        sb.markdown(f"**Thiếu {len(bu)} phiên:** " + ", ".join(ui.ngay_vn(d) for d in bu))
        chon_bu = sb.multiselect("Quét bù", bu, default=bu, format_func=ui.ngay_vn, key="bu",
                                 label_visibility="collapsed")
        if sb.button(f"⟲ Quét bù {len(chon_bu)} phiên", disabled=dang or not chon_bu,
                     width="stretch",
                     help="lt_scan_vietcap.py --den + screener cho từng phiên. Không chạy allocator."):
            chay_lenh(["bu", *chon_bu], f"Quét bù {len(chon_bu)} phiên")
    elif ngay_gd is None:
        sb.caption("Không kiểm được lịch phiên (mất mạng?).")
    cho = chay.file_cho_day()
    if sb.button(f"⇪ Đẩy lên GitHub ({len(cho)} file)", disabled=dang or not cho,
                 width="stretch",
                 help=f"Commit {len(cho)} file pipeline mới trong data/ (scan_, candidates_, che_do_, "
                      f"ke_hoach_, bao_cao_dau_tu_) rồi push lên {chay.NHANH_DAY} — Streamlit Cloud tự "
                      "cập nhật. Không đụng sổ giao dịch, tham_dinh, lt_config."):
        chay_lenh(["day"], "Đẩy lên GitHub")
    if sb.button("↻ Tải lại vĩ mô", width="stretch"):
        chay_lenh(["vi_mo"], "Tải lại vĩ mô")
    if "nhat_ky" in st.session_state:
        gio, nhan_, ok, txt = st.session_state["nhat_ky"]
        with sb.expander(f"Nhật ký {gio}: {nhan_} — {'xong' if ok else 'LỖI'}", expanded=not ok):
            st.code(txt[-6000:], language=None)

    _tra_ma(sb)
    return phien, thieu


def _tra_ma(sb):
    sb.divider()
    with sb.form("tra_ma", clear_on_submit=True, border=False):
        ma = st.text_input("Tra mã", placeholder="vd. DHC").strip().upper()
        if st.form_submit_button("Xem chi tiết", width="stretch") and ma:
            st.session_state["_tra_ma"] = ma


def canh_bao_dau_trang(ctx):
    if ctx.ngay_gd and ctx.ngay_gd[-1] > ctx.phien.ngay:
        thieu = [d for d in ctx.ngay_gd if d > ctx.phien.ngay]
        if ctx.la_moi_nhat:
            cach = ("Bấm quét ở thanh bên." if ctx.local else
                    "Bản cloud cập nhật khi máy của Quỹ quét và đẩy lên GitHub.")
            ui.canh_bao(f"Dữ liệu đến phiên <b>{ui.ngay_vn(ctx.phien.ngay)}</b> — cũ <b>{len(thieu)} phiên</b> "
                        f"so với VN-Index ({ui.ngay_vn(ctx.ngay_gd[-1])}). {cach}", nang=True)
        else:
            st.info(f"Đang xem lại phiên cũ {ui.ngay_vn(ctx.phien.ngay)}.")
    if ctx.che_do is None:
        ui.canh_bao("Chế độ thị trường <b>không xác định</b> cho phiên này (bản quét thiếu chuỗi VN-Index): "
                    "allocator không mua, không bán ép.", nang=True)
    for w in nguon.hang_rao(ctx.phien):
        w = w.replace(str(ROOT) + "\\", "").replace(str(ROOT) + "/", "")
        ui.canh_bao(f"[HÀNG RÀO] {w} <span style='opacity:.7'>(screener so thời gian sửa file — sau khi "
                    "checkout git mốc này có thể không phản ánh lần sửa thật)</span>")
    if not ctx.ro.get("ngay_chot"):
        ui.canh_bao("Rổ cơ bản <b>chưa chốt</b> → không mã nào mua được; quy tắc 4 chưa xét được.")
    if ctx.ke_hoach and ctx.ke_hoach["lenh"]["cham_tay"]:
        ui.canh_bao(f"<b>PHẢI CHẤM TAY</b> {len(ctx.ke_hoach['lenh']['cham_tay'])} vị thế — xem tab Danh mục & lệnh.")
    het = [ma for ma, v in ctx.tham_dinh.items() if not ma.startswith("_")
           and (v.get("buoc3_chi_tiet") or {}).get("het_han", "9999") < ctx.phien.ngay]
    if het:
        ui.canh_bao(f"Phiếu thẩm định hết hạn: {', '.join(het)} → coi như chưa thẩm định.")


@st.cache_data(show_spinner=False, ttl=3600)
def _chi_so_phu(ma, den):
    try:
        return thi_truong.chi_so(ma, den)
    except Exception:
        return None


def dai_bao_gia(ctx):
    """Dai bao gia: chi so trong nuoc tai ngay du lieu + vi mo toan cau (cache Yahoo, khong goi mang)."""
    v = ctx.bq.vnindex
    out = [("VNINDEX", ui.so(v["c"], 2), v.get("r1"))]
    for ma in ("VN30", "HNX30", "E1VFVN30"):
        x = _chi_so_phu(ma, ctx.phien.ngay)
        if x:
            out.append((ma, ui.so(x["Đóng cửa"], 2 if ma != "E1VFVN30" else 0), x["1 phiên"]))
    raw = vi_mo.doc_yahoo()
    for ma, ten, d in (("BZ=F", "BRENT", 2), ("USDVND=X", "USD/VND", 0), ("DX-Y.NYB", "DXY", 2),
                       ("GC=F", "VÀNG", 0), ("^TNX", "UST10Y", 2), ("^GSPC", "S&P500", 0)):
        tt = vi_mo.tom_tat(vi_mo.chuoi(raw, ma)) if raw else None
        if tt:
            out.append((ten, ui.so(tt["gia_tri"], d), tt["r1"]))
    return out


def main():
    ck = chu_ky()
    _danh_ba_lan_dau()
    _vi_mo_tu_dong()
    local = la_may_local()
    ds = _ds_phien(ck)
    ngay_gd = _ngay_gd()
    phien, thieu = thanh_ben(ds, ngay_gd, local)
    if phien is None:
        st.error("Chưa có bản quét Vietcap nào trong data/. Bấm **Quét phiên hôm nay**.")
        return
    bq = _ban_quet(phien.ngay, ck)
    truoc = nguon.phien_truoc(ds, phien)
    kh = nguon.danh_sach_ke_hoach().get(phien.ngay)
    ctx = SimpleNamespace(
        ds=ds, phien=phien, phien_truoc=truoc, la_moi_nhat=phien.ngay == ds[-1].ngay, bq=bq,
        cands=_cands(phien.ngay, ck), cands_truoc=_cands(truoc.ngay, ck) if truoc else None,
        che_do=nguon.doc_che_do(phien, bq.phu), tham_dinh=nguon.doc_tham_dinh(), ro=nguon.nap_ro(),
        ngay_gd=ngay_gd, thieu=thieu, vn=_vn(phien.ngay, ck), do_rong=_do_rong(phien.ngay, ck),
        chu_ky=ck, local=local,
        ke_hoach=None if kh is None else {"path": kh[0], "ngay_chay": kh[1], "nhip": kh[2],
                                          "lenh": danh_muc.doc_bang_lenh(kh[0])},
    )
    cd = ctx.che_do
    st_cd = cd["che_do"] if cd else None
    ui.thanh_lenh(f"PHIÊN {ui.ngay_vn(phien.ngay)} │ VNINDEX INDEX │ CHẾ ĐỘ {ui.CHE_DO_TEN[st_cd]}",
                  f"{ui.the_che_do(st_cd)}<span>QUÉT {phien.chay_luc[11:16]} "
                  f"{ui.ngay_vn(phien.chay_luc[:10])[:5]}</span>")
    ui.bang_gia(dai_bao_gia(ctx))
    canh_bao_dau_trang(ctx)
    if st.session_state.get("_tra_ma"):
        chi_tiet.mo(st.session_state.pop("_tra_ma"), ctx)

    tabs = st.tabs(["F1 Tổng quan", "F2 Thị trường", "F3 Vĩ mô", "F4 Ngành", "F5 Cổ phiếu",
                    "F6 Khám phá", "F7 Danh mục & lệnh"])
    for t, mod in zip(tabs, (tab_tong_quan, tab_thi_truong, tab_vi_mo, tab_nganh, tab_co_phieu,
                             tab_kham_pha, tab_danh_muc)):
        with t:
            try:
                mod.ve(ctx)
            except Exception as e:      # mot tab hong khong duoc keo sap ca buong lai
                st.error(f"Lỗi khi dựng tab: {e}")
                st.exception(e)


main()
