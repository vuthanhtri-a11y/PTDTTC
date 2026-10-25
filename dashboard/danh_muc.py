"""
danh_muc.py — Danh muc va lenh: vi the, NAV theo thoi gian, lai/lo, bang lenh.

Nguon: data/so_giao_dich.json (so goc), HOLDINGS/TIEN_MAT/PHIEU_LENH trong
lt_config.py, bang lenh allocator data/ke_hoach_*.txt. Chi doc.

Tien mat theo SO (du_tien_mat_sau cua lenh gan nhat + co tuc tien cua su kien co
ma), dung quy uoc cua TIEN_MAT trong lt_config.py. Lai tien gui / phi luu ky / phi
TTLK nho le KHONG nam trong so (xem doi_chieu_sao_ke_18_09: lech 241 d) nen cung
khong nam trong NAV o day.
"""

import re
from datetime import date, timedelta

import pandas as pd

from dashboard.nguon import doc_so_giao_dich   # dat ROOT vao sys.path truoc lt_*

import lt_config                              # noqa: E402

NAM = 2026
NGAY_BAT_DAU_NAV = "2026-08-19"   # phien dau tien du vi the khung dai han (17-19/08)


def chuan_ngay(s):
    """Ngay trong so -> ISO. 'truoc 17/08' -> 16/08; '17-19/08' -> 19/08."""
    s = str(s).strip()
    if re.match(r"^\d{4}-\d{2}-\d{2}$", s):
        return s
    m = re.search(r"(\d{1,2})/(\d{1,2})\s*$", s)
    if not m:
        raise ValueError(f"khong doc duoc ngay {s!r}")
    d = date(NAM, int(m.group(2)), int(m.group(1)))
    if s.lower().startswith("truoc"):
        d -= timedelta(days=1)
    return d.isoformat()


def su_kien_theo_ngay(so=None):
    """[(ngay, thu_tu, loai, ban ghi)] — lenh va su kien doanh nghiep (co ma), xep theo ngay."""
    so = so or doc_so_giao_dich()
    out = [(chuan_ngay(g["ngay"]), 0, "lenh", g) for g in so["giao_dich"]]
    for e in so.get("su_kien_phi_tien_mat", []):
        if e.get("ma") and re.match(r"^\d{4}-\d{2}-\d{2}$", str(e.get("ngay", ""))):
            out.append((e["ngay"], 1, "su_kien", e))
    return sorted(out, key=lambda x: (x[0], x[1]))   # sorted on dinh: giu thu tu so


def trang_thai(ngay, so=None):
    """(vi the {ma: kl}, tien mat) cuoi ngay `ngay` theo so."""
    so = so or doc_so_giao_dich()
    vt, tien, co_tuc = {}, so["von_goc"], 0
    for d, _, loai, e in su_kien_theo_ngay(so):
        if d > ngay:
            break
        if loai == "lenh":
            dau = 1 if e["loai"] == "MUA" else -1
            vt[e["ma"]] = vt.get(e["ma"], 0) + dau * e["kl"]
            tien = e["du_tien_mat_sau"]
        else:
            if e.get("sau", {}).get("kl") is not None:
                vt[e["ma"]] = e["sau"]["kl"]
            co_tuc += e.get("dong_tien", 0) or 0
    return {m: k for m, k in vt.items() if k}, tien + co_tuc


def he_so_chia_tach(so=None):
    """{ma: [(ngay GDKHQ, he so)]} — de quy doi KL truoc ngay chia khi dung gia da dieu chinh."""
    so = so or doc_so_giao_dich()
    out = {}
    for e in so.get("su_kien_phi_tien_mat", []):
        t, s = e.get("truoc", {}).get("kl"), e.get("sau", {}).get("kl")
        if e.get("ma") and t and s:
            out.setdefault(e["ma"], []).append((e["ngay"], s / t))
    return out


NGUONG_LECH_GIA = 0.10   # gia khop / gia dieu chinh lech >= 10% -> su kien co phieu ngoai so


def he_so_tu_gia_khop(gia_dc, so=None):
    """{ma: (he so, ngay lenh cuoi)} cho ma co su kien chia/thuong co phieu NGOAI so.

    Vietcap chia lui toan bo lich su khi co su kien, ke ca sau khi Quy da ban (GMD:
    gia khop 78.800 / 78.100 so voi gia dieu chinh ~52.000 -> 1,50). Lay trung vi ty
    le gia khop / gia dong cua dieu chinh cung ngay tren moi lenh cua ma; lech duoi
    nguong la nhieu trong phien hoac co tuc tien -> bo qua (ghi chu tren bieu do).
    """
    so = so or doc_so_giao_dich()
    tl, cuoi = {}, {}
    for g in so["giao_dich"]:
        d, s = chuan_ngay(g["ngay"]), gia_dc.get(g["ma"])
        if s is None or d not in s.index or not s[d]:
            continue
        tl.setdefault(g["ma"], []).append(g["gia"] / s[d])
        cuoi[g["ma"]] = max(cuoi.get(g["ma"], d), d)
    out = {}
    for ma, xs in tl.items():
        k = float(pd.Series(xs).median())
        if abs(k - 1) >= NGUONG_LECH_GIA:
            out[ma] = (k, cuoi[ma])
    return out


def nav_tai(ngay, gia, so=None):
    """NAV cuoi ngay voi bang gia THO {ma: gia} (khong quy doi chia tach)."""
    vt, tien = trang_thai(ngay, so)
    thieu = [m for m in vt if m not in gia]
    if thieu:
        raise KeyError(f"thieu gia {thieu} ngay {ngay}")
    return tien + sum(k * gia[m] for m, k in vt.items())


def chuoi_nav(gia_dc, ngay_list, so=None, he_so_gia=None):
    """NAV DM2 tung phien voi gia DA DIEU CHINH Vietcap.

    gia_dc: {ma: Series(index ngay ISO -> gia dong cua)}. Truoc ngay chia co phieu
    CO TRONG SO, KL nhan he so (MSB 700 -> 840 truoc 28/08) vi gia Vietcap da chia
    lui. Su kien NGOAI so (he_so_gia, xem he_so_tu_gia_khop): nhan gia voi he so toi
    ngay lenh cuoi cua ma. Co tuc TIEN khong quy doi -> gia truoc ngay GDKHQ thap hon
    gia tho mot chut.
    """
    so = so or doc_so_giao_dich()
    hs = he_so_chia_tach(so)
    he_so_gia = he_so_gia or {}
    rows = []
    for d in ngay_list:
        vt, tien = trang_thai(d, so)
        cp = 0.0
        for m, k in vt.items():
            s = gia_dc.get(m)
            if s is None or d not in s.index:
                cp = None
                break
            f = 1.0
            for ngay_ck, h in hs.get(m, []):
                if d < ngay_ck:
                    f *= h
            if m in he_so_gia and d <= he_so_gia[m][1]:
                f *= he_so_gia[m][0]
            cp += k * f * s[d]
        if cp is None:
            continue
        rows.append({"ngay": d, "tien_mat": tien, "co_phieu": cp, "nav": tien + cp})
    return pd.DataFrame(rows)


def ma_tung_giu(so=None):
    so = so or doc_so_giao_dich()
    return sorted({g["ma"] for g in so["giao_dich"]})


def lai_lo_da_thuc_hien(so=None):
    """Lai/lo da thuc hien theo gia von binh quan (gom phi mua); ban tru phi + thue.

    Chia co phieu giu tong von, doi KL (MSB 700@16.000 -> 840@13.333).
    """
    so = so or doc_so_giao_dich()
    kl, von = {}, {}
    rows = []
    for d, _, loai, e in su_kien_theo_ngay(so):
        m = e["ma"]
        if loai == "su_kien":
            if e.get("sau", {}).get("kl") is not None:
                kl[m] = e["sau"]["kl"]
            continue
        if e["loai"] == "MUA":
            kl[m] = kl.get(m, 0) + e["kl"]
            von[m] = von.get(m, 0) + e["gia_tri"] + e["phi_dich_vu"]
            continue
        gv_bq = von[m] / kl[m]
        thu = e["gia_tri"] - e["phi_dich_vu"] - e.get("thue", 0)
        lai = thu - gv_bq * e["kl"]
        rows.append({"Ngày": d, "Mã": m, "KL": e["kl"], "Giá bán": e["gia"],
                     "Giá vốn BQ": gv_bq, "Thu ròng": thu, "Lãi/lỗ": lai,
                     "% trên vốn": lai / (gv_bq * e["kl"]), "Căn cứ": e.get("can_cu", "")})
        von[m] -= gv_bq * e["kl"]
        kl[m] -= e["kl"]
    return pd.DataFrame(rows)


def vi_the_hien_tai(gia):
    """Vi the theo HOLDINGS/TIEN_MAT trong lt_config.py, danh gia bang `gia` {ma: gia}."""
    out = {}
    for pk, cfg in lt_config.PORTFOLIOS.items():
        rows = []
        for ma, kl, gv in lt_config.HOLDINGS[pk]:
            g = gia.get(ma)
            rows.append({"Mã": ma, "KL": kl, "Giá vốn": gv, "Giá": g,
                         "Giá trị": None if g is None else kl * g,
                         "Lãi/lỗ %": None if g is None or not gv else g / gv - 1})
        cp = sum(r["Giá trị"] or 0 for r in rows)
        tien = lt_config.TIEN_MAT[pk]
        out[pk] = {"ten": cfg["ten"], "von_ban_dau": cfg["von_ban_dau"], "vi_the": rows,
                   "co_phieu": cp, "tien_mat": tien, "nav": cp + tien}
    return out


# ------------------------------------------------------------------ bang lenh
_LENH = re.compile(r"^\s+(BAN|MUA)\s+([\d,]+)\s+(\S+)\s+x\s+([\d,]+)\s+=\s+([\d,]+)\s+"
                   r"phi\s+([\d,]+)(?:\s+—\s+(.*?))?(?:\s+(\[[^\]]*\]))?\s*$")
_CHAM_TAY = re.compile(r"^\s+\[\?\]\s+([\d,]+)\s+(\S+)\s+gia von\s+([\d,]+)\s+—\s+(.*)$")
_DM = re.compile(r"^(DM\d) — ")
_KHONG_MUA = re.compile(r"^\s+\[KHONG MUA\]\s+(.*)$")


def doc_bang_lenh(path):
    """Tach lenh BAN/MUA, PHAI CHAM TAY va ly do khong mua tu bang lenh allocator."""
    lenh, cham_tay, khong_mua = [], [], []
    dm = None

    def n(x):
        return int(x.replace(",", ""))
    for dong in path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = _DM.match(dong)
        if m:
            dm = m.group(1)
            continue
        m = _LENH.match(dong)
        if m:
            lenh.append({"DM": dm, "Chiều": m.group(1), "KL": n(m.group(2)), "Mã": m.group(3),
                         "Giá": n(m.group(4)), "Giá trị": n(m.group(5)), "Phí": n(m.group(6)),
                         "Lý do": m.group(7) or "", "Phiếu": (m.group(8) or "").strip("[]")})
            continue
        m = _CHAM_TAY.match(dong)
        if m:
            cham_tay.append({"DM": dm, "KL": n(m.group(1)), "Mã": m.group(2),
                             "Giá vốn": n(m.group(3)), "Vì sao": m.group(4)})
            continue
        m = _KHONG_MUA.match(dong)
        if m:
            khong_mua.append({"DM": dm, "Lý do": m.group(1)})
    return {"lenh": lenh, "cham_tay": cham_tay, "khong_mua": khong_mua}


def vi_the_dang_giu():
    """{(dm, ma): kl} tu lt_config.HOLDINGS cho cac vi the con kl > 0."""
    return {(dm, ma): kl for dm, rows in lt_config.HOLDINGS.items() for ma, kl, _ in rows if kl > 0}


def lenh_chua_thuc_hien(ke_hoach, ngay_phien=None):
    """Loc bang lenh allocator: bo lenh/vi the da khop trong PHIEU_LENH hoac da ban het khoi HOLDINGS."""
    if not ke_hoach or "lenh" not in ke_hoach:
        return {"lenh": [], "cham_tay": []}
    giu = vi_the_dang_giu()
    da_khop = {
        (p.get("dm"), p.get("chieu"), p.get("ma"))
        for p in lt_config.PHIEU_LENH
        if str(p.get("trang_thai", "")).lower() == "da khop"
        and (not ngay_phien or str(p.get("ngay_dat", "")) >= ngay_phien)
    }
    lenh = [
        l for l in ke_hoach["lenh"].get("lenh", [])
        if (l["DM"], l["Chiều"], l["Mã"]) not in da_khop
        and not (l["Chiều"] == "BAN" and giu.get((l["DM"], l["Mã"]), 0) == 0)
    ]
    cham_tay = [
        c for c in ke_hoach["lenh"].get("cham_tay", [])
        if giu.get((c["DM"], c["Mã"]), 0) > 0
        and (c["DM"], "BAN", c["Mã"]) not in da_khop
    ]
    return {"lenh": lenh, "cham_tay": cham_tay}
