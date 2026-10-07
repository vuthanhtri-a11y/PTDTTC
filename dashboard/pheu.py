"""
pheu.py — Pheu chon ma CHINH THUC cua Quy, doc tu candidates_*.json do
lt_screener.py ghi (khong tinh lai). Rieng tang 0 -> 1 (ly do rot loc cung cua
moi ma) goi lai lt_screener.build_rows tren cung ban quet — cung mot ham screener
dung, nen ly do khop.

Tang:
  0 Toan thi truong         moi ma trong ban quet
  1 Qua loc cung            thanh khoan, gia > MA200, MA50 > MA200 (nhanh MAY)
  2 Giao diem voi ro        trong_ro_co_ban = True (nhanh NGUOI)
  3 Phieu Dat con han       V1-V5 + ba truc ket luan DAT, chua het han
  4 Buoc 4 + bien an toan   buy_ready: buoc4 'dat', gia <= 0,85 x Than trong
  5 Che do cho mua          che do khac GIAM va xac dinh duoc
"""

import pandas as pd

from dashboard import nguon  # noqa: F401  dat ROOT vao sys.path truoc lt_*

import lt_screener          # noqa: E402

TANG = ["Toàn thị trường", "Qua lọc cứng", "Giao điểm với rổ cơ bản",
        "Phiếu Đạt còn hạn", "Bước 4 + biên an toàn", "Chế độ cho mua"]


def ly_do_loc_cung(bq):
    """{ma: ly do rot Tang 1} tren toan ban quet — goi dung ham cua screener."""
    rows = lt_screener.build_rows(bq.df.to_dict("index"), bq.vnindex, bq.phu)
    return {r["ma"]: r["ly_do_loai_b1"] for r in rows}


def cac_tang(cands, bq, che_do):
    """[(ten tang, [ban ghi candidates]), ...] — tang 0 la danh sach ma cua ban quet."""
    cands = cands or []
    t1 = [c for c in cands if c.get("qua_loc_cung")]
    t2 = [c for c in t1 if c.get("trong_ro_co_ban") is True]
    t3 = [c for c in t2 if c.get("phieu_ok") is True]
    t4 = [c for c in t3 if c.get("buy_ready") is True]
    cho_mua = bool(che_do) and che_do.get("che_do") not in (None, "GIAM")
    t5 = t4 if cho_mua else []
    return [(TANG[0], list(bq.df.index)), (TANG[1], t1), (TANG[2], t2),
            (TANG[3], t3), (TANG[4], t4), (TANG[5], t5)]


def ly_do_rot(c, tang_tiep, che_do=None):
    """Vi sao ma `c` (o tang truoc) khong vao `tang_tiep`."""
    if tang_tiep == 2:
        return c.get("ly_do_ro") or "chưa có kết luận rổ"
    if tang_tiep == 3:
        return c.get("ly_do_phieu") or "chưa có phiếu"
    if tang_tiep == 4:
        lst = []
        if c.get("buoc4_dinh_gia") != "dat":
            lst.append(f"Bước 4 = {c.get('buoc4_dinh_gia')}")
        if not c.get("bien_an_toan_ok"):
            lst.append(c.get("ly_do_bien") or "biên an toàn chưa đạt")
        return "; ".join(lst)
    if tang_tiep == 5:
        return ("chế độ GIẢM — khoá mua mới" if che_do and che_do.get("che_do") == "GIAM"
                else "chế độ không xác định")
    return ""


def bang_ma(cands_list, cot_them=None):
    """DataFrame gon cho danh sach ban ghi candidates."""
    rows = []
    for c in cands_list:
        r = {"Mã": c["ma"], "Sàn": c.get("san"), "Giá": c.get("gia"),
             "MA50": c.get("ma50"), "MA200": c.get("ma200"),
             "Thanh khoản (tỷ)": (c.get("tov") or 0) / 1e9, "ATR": c.get("atr"),
             "RS 12T": c.get("rs_252_skip21"), "Rổ": c.get("trong_ro_co_ban"),
             "Phiếu": c.get("phieu_ok"), "B4": c.get("buoc4_dinh_gia"),
             "Biên an toàn": c.get("bien_an_toan"), "Ưu tiên": c.get("uu_tien")}
        if cot_them:
            r.update(cot_them(c))
        rows.append(r)
    return pd.DataFrame(rows)


def thay_doi(cands_nay, cands_truoc):
    """(moi vao, roi ra) ro xu huong (qua loc cung) so voi phien truoc."""
    nay = {c["ma"] for c in cands_nay or [] if c.get("qua_loc_cung")}
    truoc = {c["ma"] for c in cands_truoc or [] if c.get("qua_loc_cung")}
    return sorted(nay - truoc), sorted(truoc - nay)


def ro_co_ban(cands):
    """Ma trong ro co ban (nhanh nguoi) theo ket luan screener."""
    return [c for c in cands or [] if c.get("trong_ro_co_ban") is True]


# ------------------------------------------------------------------ phieu tham dinh
def cong(v):
    """[(cong, 'BAT' | 'KHONG BAT' | '?', van ban)] tu nam_cong_phu_quyet."""
    out = []
    for k, t in ((v.get("buoc3_chi_tiet") or {}).get("nam_cong_phu_quyet") or {}).items():
        s = str(t).strip().upper()
        tt = "KHONG BAT" if s.startswith("KHONG BAT") else ("BAT" if s.startswith("BAT") else "?")
        out.append((k, tt, str(t)))
    return out


def diem(v):
    d = (v.get("buoc3_chi_tiet") or {}).get("diem")
    return d if isinstance(d, dict) else None


def day_bay(v):
    db = (v.get("buoc3_chi_tiet") or {}).get("day_bay_nhip_D")
    return db if isinstance(db, list) else []
