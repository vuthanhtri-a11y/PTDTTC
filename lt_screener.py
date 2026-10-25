"""
lt_screener.py — Khung TOP-DOWN, hai nhanh song song (chot 01/10/2026).

Dau vao : data/scan_YYYYMMDD.json  (lt_scan_vietcap.py — toan thi truong)
          data/tham_dinh.json      (ro co ban top-down + phieu V1-V5 + Buoc 4, NGUOI)
Dau ra  : bang giao diem, ghi data/candidates_YYYYMMDD.json cho lt_allocator.py.

Cau truc (CHIEN_LUOC_DAI_HAN.md muc 13):
  * NHANH MAY  — Tang 1 (5 dieu kien cua Bang CL.1) tren toan HOSE+HNX+UPCoM
                 -> "ro xu huong". Khong xep hang: Buoc 2 da bo 01/10/2026.
  * NHANH NGUOI — ro co ban: vi mo -> nganh -> doanh nghiep (V1-V5).
  * GIAO DIEM + Buoc 4 (dinh gia) = duoc mua. Thu tu: `uu_tien` nguoi gan, roi
    ATR thap truoc.
  * (toi 04/10/2026) Bo loc xu huong khong de DU BAO thi truong: it ma qua loc
    thi tien mat tu tang. Tu 05/10/2026 them Tru 1 — che do thi truong dat tran
    ty trong co phieu (lt_che_do.py, muc 14).

Tu 05/10/2026 — KHUNG GIAI DOAN 2 (muc 14):
  * Tang 1 chi con: thanh khoan, gia > MA200, MA50 > MA200 (RS va ATR da bo).
  * Duoc mua = giao diem + Buoc 4 + PHIEU QUA con han (ket_qua "DAT" hoac "CHO";
    tu 18/10/2026, muc 15.8) + BIEN AN TOAN: gia <= (1 - BIEN_AN_TOAN_MIN) x than_trong.
  * Luat ban: gia < 0,97 x MA200 (ky soat), ngoai ro (quy tac 4), gia >= co_so.
    Che do GIAM va chan cung -25% xu ly o lt_allocator.py.
  * Che do thi truong tinh tu khoi _vnindex cua ban quet (lt_che_do.py), ghi ra
    data/che_do_YYYYMMDD.json cho allocator.

Chay: PYTHONIOENCODING=utf-8 python lt_screener.py
Ban truoc 01/10/2026 (co xep hang RS): data/lt_screener_backup_20261001.py
Ban truoc 04/10/2026 (co RS/ATR o Tang 1): data/lt_screener_backup_20261004.py
"""

import json
import os
import sys
from datetime import datetime

from lt_config import (LOC, EXIT, HOLDINGS, THAM_DINH_FILE, THAM_DINH_TRANG_THAI,
                       RO_CO_BAN_KHOA, QUY_TAC_5, CANSLIM_CHAN_MUA, CANSLIM_KET_QUA,
                       BIEN_AN_TOAN_MIN)
from lt_che_do import tu_ban_quet, in_che_do

DATA_DIR = "data"
# Vi tri cot trong scan_YYYYMMDD.json. CHI DUOC NOI THEM VAO CUOI — cac ban
# quet cu ngan hon se duoc bu None trong load(), nen doi thu tu la hong het.
#   0-9   : ban goc
#   10-11 : r1, r5 — da xuat hien tu ban quet 04/09 nhung chua tung khai o day
#   12-14 : dma50, vol60, c60 — sinh cho quy tac 5 ban cu (07/09/2026). Tu
#           11/09/2026 quy tac 5 la ban theo cam quan nen KHONG con doc toi,
#           nhung giu trong schema vi chi duoc noi them vao cuoi.
FIELDS = ["c", "r21", "r63", "r126", "r252", "ma50", "ma200", "atr", "tov_ty", "ds",
          "r1", "r5", "dma50", "vol60", "c60"]
FIELDS_GOC = 10        # so cot bat buoc; thieu -> file quet hong
KHONG_UU_TIEN = 10**6  # ma trong ro chua duoc gan uu_tien -> xep sau cung, pha hoa bang ATR


def nap_tham_dinh():
    """Ket luan Buoc 3 + Buoc 4 + truong ro co ban do NGUOI nhap.

    Thieu ban ghi = 'chua'. Mac dinh phai la 'chua' chu khong phai 'dat' — neu
    mac dinh la dat thi lop phu quyet khong ton tai.
    """
    if not os.path.exists(THAM_DINH_FILE):
        return {}
    raw = json.load(open(THAM_DINH_FILE, encoding="utf-8"))
    out = {}
    for ma, v in raw.items():
        if ma.startswith("_"):
            continue
        b3 = v.get("buoc3_tham_dinh", "chua")
        b4 = v.get("buoc4_dinh_gia", "chua")
        for nhan, gt in (("buoc3_tham_dinh", b3), ("buoc4_dinh_gia", b4)):
            if gt not in THAM_DINH_TRANG_THAI:
                sys.exit(f"{THAM_DINH_FILE}: {ma}.{nhan} = {gt!r} khong hop le "
                         f"(chi nhan {THAM_DINH_TRANG_THAI})")
        tr = v.get("trong_ro")
        if tr not in (True, False, None):
            sys.exit(f"{THAM_DINH_FILE}: {ma}.trong_ro = {tr!r} — chi nhan true/false/null")
        ut = v.get("uu_tien")
        if ut is not None and not isinstance(ut, int):
            sys.exit(f"{THAM_DINH_FILE}: {ma}.uu_tien = {ut!r} — phai la so nguyen (1 = cao nhat)")
        dg = v.get("dinh_gia") or {}
        ct = v.get("buoc3_chi_tiet") or {}
        out[ma] = {"buoc3": b3, "buoc4": b4,
                   "ly_do": v.get("ly_do", ""), "luan_diem": v.get("luan_diem", ""),
                   "ngay": v.get("ngay", ""),
                   "luan_diem_con_nguyen": v.get("luan_diem_con_nguyen", None),
                   "trong_ro": tr, "nganh": v.get("nganh") or None, "uu_tien": ut,
                   "ngay_vao_ro": v.get("ngay_vao_ro", ""),
                   "ly_do_ro": v.get("ly_do_ro", ""),
                   # Giai doan 2 (04/10/2026): dinh gia NGHIN DONG/CP; phieu V1-V5 +
                   # ba truc la ban ghi buoc3_chi_tiet (ket_qua, het_han).
                   "co_so": dg.get("co_so"), "than_trong": dg.get("than_trong"),
                   "can_dung_lai": dg.get("can_dung_lai") is True,
                   "phieu_ket_qua": ct.get("ket_qua"), "phieu_het_han": ct.get("het_han")}
    return out


def hom_nay():
    """Ngay chay (ISO). Ghi de bang NGAY_CHAY de chay gia lap, nhu lt_allocator."""
    return os.environ.get("NGAY_CHAY") or datetime.now().strftime("%Y-%m-%d")


PHIEU_QUA = ("DAT", "CHO")   # 18/10/2026 (muc 15.8): khong bi phu quyet la qua


def trang_thai_phieu(v, ngay):
    """(True/False, ly do): ma co phieu V1-V5 + ba truc KHONG phu quyet, con han?

    Tu 18/10/2026 (muc 15.8, sua quyet dinh 9): phieu Dat HOAC Cho deu qua —
    qua phieu = doanh nghiep co tiem nang dau tu; cua chan mua con lai la dinh
    gia + bien an toan. Truoc do: "Chi ma Dat duoc mua" (tr.72 bao cao giai
    doan 1) — sai lech nay phai cong bo (14.6). Nhan buoc3 = "dat" ma khong co
    phieu (vd ban dich tu khuyen_nghi 01/09) KHONG du. Phieu Phu quyet hoac qua
    han = khong qua. Chi chan MUA; vi the dang giu khong bi ban vi ly do nay.
    """
    kq, han = v.get("phieu_ket_qua"), v.get("phieu_het_han")
    if not kq:
        return False, "chua co phieu V1-V5 + ba truc"
    if str(kq).upper() not in PHIEU_QUA:
        return False, f"phieu ket luan {kq} (chi DAT/CHO duoc mua)"
    if not han or han < ngay:
        return False, f"phieu het han {han or '?'}"
    return True, ""


def trang_thai_bien(gia, v):
    """(True/False, bien an toan, ly do) — Buoc 4 bien an toan kep (quyet dinh 7).

    Mua khi gia <= (1 - BIEN_AN_TOAN_MIN) x than_trong. Thieu than_trong hoac
    co_so, than_trong > co_so, hay dinh gia danh dau can_dung_lai -> khong mua.
    """
    tt, cs = v.get("than_trong"), v.get("co_so")
    if tt is None or cs is None:
        return False, None, "thieu than_trong/co_so"
    if tt > cs:
        return False, None, f"[MAU THUAN] than_trong {tt} > co_so {cs}"
    bien = 1 - gia / (tt * 1000)
    if v.get("can_dung_lai"):
        return False, bien, "dinh gia danh dau can_dung_lai"
    if bien < BIEN_AN_TOAN_MIN:
        return False, bien, (f"bien {bien:+.1%} < {BIEN_AN_TOAN_MIN:.0%} "
                             f"(mua khi <= {(1 - BIEN_AN_TOAN_MIN) * tt * 1000:,.0f})")
    return True, bien, ""


def nap_ro():
    """Khoi `_ro_co_ban` cua THAM_DINH_FILE: ngay chot, vi mo, ro nganh."""
    if not os.path.exists(THAM_DINH_FILE):
        return {"ngay_chot": None, "vi_mo": {}, "nganh": {}}
    raw = json.load(open(THAM_DINH_FILE, encoding="utf-8")).get(RO_CO_BAN_KHOA) or {}
    return {"ngay_chot": raw.get("ngay_chot") or None,
            "vi_mo": raw.get("vi_mo") or {},
            "nganh": raw.get("nganh") or {}}


def trang_thai_ro(ma, td, ro):
    """(True/False/None, ly do). Xem khoi "Ro co ban top-down" trong lt_config.py.

    False chi khi NGUOI da noi ro "khong" o mot tang nao do. Moi cho thieu hay
    nhap sai deu la None: khong mua, khong tu ban, phai cham tay.
    """
    if not ro["ngay_chot"]:
        return None, "ro co ban chua chot"
    v = td.get(ma)
    if v is None or v["trong_ro"] is None:
        return None, "chua co ket luan trong_ro"
    if v["trong_ro"] is False:
        return False, "nguoi loai khoi ro" + (f": {v['ly_do_ro']}" if v["ly_do_ro"] else "")
    if v["luan_diem_con_nguyen"] is False:
        return False, "luan diem doanh nghiep da gay"
    if v["buoc3"] == "loai":
        return False, "phu quyet V1-V5"
    ng = v["nganh"]
    if not ng or ng not in ro["nganh"]:
        return None, f"nganh {ng!r} khong co trong _ro_co_ban.nganh"
    if ro["nganh"][ng].get("trong_ro") is False:
        return False, f"nganh {ng} bi loai khoi ro"
    if ro["nganh"][ng].get("trong_ro") is not True:
        return None, f"nganh {ng} chua co ket luan"
    if not (ro["vi_mo"].get("ket_luan") or "").strip():
        return None, "tang vi mo chua co ket luan"
    if v["buoc3"] != "dat":
        return None, "chua co phieu V1-V5 (buoc3 = chua)"
    return True, ""


def nap_canslim():
    """Buoc 3a — ket qua MAY cham CANSLIM, file data/canslim_YYYYMMDD.json moi nhat
    (sinh bang `python canslim.py`). Thieu file / thieu ma = None = khong qua.

    Chi CHAN mua khi CANSLIM_CHAN_MUA = True (cong tac theo ket qua kiem dinh
    dang ky truoc, CHIEN_LUOC_DAI_HAN.md muc 12). Mac dinh chi cham va in ra.
    """
    fs = sorted(f for f in os.listdir(DATA_DIR)
                if f.startswith("canslim_") and f.endswith(".json")
                and f[8:-5].isdigit() and len(f[8:-5]) == 8)
    if not fs:
        return {}, None
    raw = json.load(open(os.path.join(DATA_DIR, fs[-1]), encoding="utf-8"))
    return raw.get("toan_ro", {}), raw["_meta"]["ngay_du_lieu"]


def cua_canslim(r, cs):
    v = cs.get(r["ma"], {})
    r["canslim_3a"] = v.get("qua_3a")
    r["canslim_co_v3"] = v.get("co_v3", False)
    return r


def newest(prefix):
    """File moi nhat khop `prefix`, dang scan_YYYYMMDD.json.

    26/08/2026 — them bo loc ngay thang. `weekly_rank.py` ghi ra
    data/scan_weekly_*.json voi dinh dang HOAN TOAN KHAC (khong co truong `ds`),
    ma ten file do cung bat dau bang "scan_" nen ban cu luon chon nham no lam
    du lieu dau vao va chet o KeyError: 'ds'. Chi nhan hau to la 8 chu so.
    """
    def dung_dang(f):
        than = f[len(prefix):-len(".json")]
        return len(than) == 8 and than.isdigit()

    fs = sorted(f for f in os.listdir(DATA_DIR)
                if f.startswith(prefix) and f.endswith(".json") and dung_dang(f))
    if not fs:
        sys.exit(f"Khong tim thay {DATA_DIR}/{prefix}*.json — chay lt_scan_vietcap.py truoc.")
    return os.path.join(DATA_DIR, fs[-1])


def load(path):
    """Doc ban quet. Cot thieu (ban quet cu) duoc bu None, KHONG bu gia tri mac
    dinh — cot nao khong do duoc phai hien la khong do duoc. Thieu cot goc thi
    dung han vi moi thu con lai deu sai theo. Khoa bat dau bang "_" (_meta,
    _san, _icb cua lt_scan_vietcap.py) tra ve rieng.
    """
    raw = json.load(open(path, encoding="utf-8"))
    out, phu = {}, {}
    for k, v in raw.items():
        if k.startswith("_"):
            phu[k] = v
            continue
        if len(v) < FIELDS_GOC:
            sys.exit(f"{path}: {k} chi co {len(v)}/{FIELDS_GOC} cot goc — quet lai.")
        d = dict(zip(FIELDS, v))
        for f in FIELDS[len(v):]:
            d[f] = None
        out[k] = d
    return out, phu


def hard_filter_checks(r):
    """Single source for Step 1 eligibility and its rejection reasons.

    04/10/2026: RS (rs_252_duong = False) va ATR (atr_max = None) da tat — khi tat,
    dieu kien do luon dat va khong con doi du 252 phien lich su cho RS.
    """
    if r["ma200"] is None or (LOC["rs_252_duong"] and r["rs_252_skip21"] is None):
        return [("du_lich_su", False, "chua du lich su (MA200/RS)")]
    return [
        ("liquidity", r["tov"] >= LOC["thanh_khoan_min"],
         f"thanh khoan {r['tov']/1e9:.1f} ty"),
        ("close_above_ma200", not LOC["gia_tren_ma200"] or r["gia"] > r["ma200"],
         "duoi MA200"),
        ("ma50_above_ma200", not LOC["ma50_tren_ma200"] or r["ma50"] > r["ma200"],
         "MA50<MA200"),
        ("rs_12m_positive", not LOC["rs_252_duong"] or r["rs_252_skip21"] > 0,
         "thua VNINDEX 12T"),
        ("atr_max", LOC["atr_max"] is None or r["atr"] <= LOC["atr_max"],
         f"ATR {r['atr']*100:.1f}%"),
    ]


def build_rows(scan, bench, phu=None):
    """Tinh chi so cho TUNG ma quet duoc (qua loc hay khong) — Tang 1."""
    phu = phu or {}
    san, icb = phu.get("_san", {}), phu.get("_icb", {})
    rows = []
    for ma, d in scan.items():
        def rs(k):
            a, b = d.get(k), bench.get(k)
            return None if a is None or b is None else a - b

        # 12 thang BO QUA 21 phien gan nhat (skip-month): dao chieu ngan han
        # lam nhieu tin hieu momentum, day la chuan trong hoc thuat.
        if d["r252"] is None or d["r21"] is None:
            rs252_skip = None
        else:
            a = (1 + d["r252"]) / (1 + d["r21"]) - 1
            b = (1 + bench["r252"]) / (1 + bench["r21"]) - 1
            rs252_skip = a - b

        r = {
            "ma": ma, "gia": d["c"], "atr": d["atr"], "tov": d["tov_ty"] * 1e9,
            "ma50": d["ma50"], "ma200": d["ma200"], "r252": d["r252"],
            "rs_252_skip21": rs252_skip, "rs_126": rs("r126"),
            "rs_63": rs("r63"), "rs_21": rs("r21"),
            "san": san.get(ma), "icb": icb.get(ma),
        }
        why = [reason for _, ok, reason in hard_filter_checks(r) if not ok]
        r["ly_do_loai_b1"] = ", ".join(why)
        rows.append(r)
    return rows


def cua_ro(r, td, ro):
    """Nhanh NGUOI: ro co ban top-down + Buoc 4.

    Khong tinh diem tu du lieu gia o day. Ham `investment_score` cu da bi bo:
    no cong diem cho "quality" va "valuation" bang du lieu gia deo nhan co ban.
    """
    v = td.get(r["ma"], {})
    r["buoc3_tham_dinh"] = v.get("buoc3", "chua")
    r["buoc4_dinh_gia"] = v.get("buoc4", "chua")
    r["tham_dinh_ly_do"] = v.get("ly_do", "")
    r["luan_diem"] = v.get("luan_diem", "")
    r["tham_dinh_ngay"] = v.get("ngay", "")
    r["luan_diem_con_nguyen"] = v.get("luan_diem_con_nguyen", None)
    r["trong_ro_co_ban"], r["ly_do_ro"] = trang_thai_ro(r["ma"], td, ro)
    # Tran nganh dung nganh NGUOI gan (quyet dinh 8). Khong co -> "Khac" chi de
    # hien thi; ma do khong the co trong_ro_co_ban = True nen khong duoc mua.
    r["nganh"] = v.get("nganh") or "Khac"
    r["uu_tien"] = v.get("uu_tien")
    r["bi_phu_quyet"] = r["buoc3_tham_dinh"] == "loai"
    r["trong_danh_sach_cho"] = (r["trong_ro_co_ban"] is True
                                and r["buoc4_dinh_gia"] == "cho")
    # Giai doan 2 (04/10/2026): phieu qua (Dat/Cho) con han + bien an toan kep. Gia tri
    # dinh gia doi ra DONG/CP de so thang voi gia.
    r["phieu_ok"], r["ly_do_phieu"] = trang_thai_phieu(v, hom_nay())
    r["co_so"] = None if v.get("co_so") is None else v["co_so"] * 1000
    r["than_trong"] = None if v.get("than_trong") is None else v["than_trong"] * 1000
    r["bien_an_toan_ok"], r["bien_an_toan"], r["ly_do_bien"] = trang_thai_bien(r["gia"], v)
    return r


def buy_checklist(r):
    """Tang 1 + giao diem ro co ban + Buoc 4 + phieu qua + bien an toan kep.

    Che do thi truong (Tru 1) la rang buoc CAP DANH MUC — lt_allocator.py ap.
    """
    checks = [(name, ok) for name, ok, _ in hard_filter_checks(r)]
    r["buy_checklist"] = checks
    r["qua_loc_cung"] = all(ok for _, ok in checks)
    r["giao_diem"] = r["qua_loc_cung"] and r.get("trong_ro_co_ban") is True
    r["buy_ready"] = (r["giao_diem"]
                      and r["buoc4_dinh_gia"] == "dat"
                      and r.get("phieu_ok") is True
                      and r.get("bien_an_toan_ok") is True
                      and (not CANSLIM_CHAN_MUA or r.get("canslim_3a") is True))
    return r


def sell_checklist(r):
    """Quy tac thoat (sua 04/10/2026, muc 14). Mot cau phu dinh la ban toan bo.

    Quy tac 2 (RS) va 3 (thu hang) DA BO. Quy tac 4 = khong con trong ro co
    ban. Trang thai ro None (thieu ket luan) KHONG tu dong ban — bao cham tay.
    Them: gia dong cua >= gia tri co so -> ban (quyet dinh 6). Thieu co_so thi
    luat nay KHONG xet duoc -> co thieu_co_so, khong tu ban.
    Che do GIAM va chan cung -25% la luat cap danh muc/gia von -> lt_allocator.py.
    """
    thieu_ls = r["ma200"] is None
    co_so = r.get("co_so")
    checks = [
        ("close_below_97pct_ma200", not thieu_ls and r["gia"] < 0.97 * r["ma200"]),
        ("ngoai_ro_co_ban", r.get("trong_ro_co_ban") is False),
        ("cham_co_so", co_so is not None and r["gia"] >= co_so),
    ]
    r["sell_checklist"] = checks
    r["sell_ready"] = any(ok for _, ok in checks)
    r["thieu_ra_soat_ro"] = r.get("trong_ro_co_ban") is None
    r["thieu_lich_su"] = thieu_ls
    r["thieu_co_so"] = co_so is None
    return r


def thu_tu_mua(r):
    """Thu tu uu tien giao diem (quyet dinh 5): uu_tien nguoi gan, roi ATR thap."""
    ut = r.get("uu_tien")
    return (ut if isinstance(ut, int) else KHONG_UU_TIEN, r["atr"], r["ma"])


def canh_bao_hang_rao(scan_path, ro):
    """Hang rao thoi diem (quyet dinh 4): ro phai chot TRUOC ban quet."""
    ngay_quet = os.path.basename(scan_path)[5:13]
    out = []
    if ro["ngay_chot"] and ro["ngay_chot"].replace("-", "") > ngay_quet:
        out.append(f"ngay_chot ro {ro['ngay_chot']} SAU ngay ban quet {ngay_quet}")
    if (os.path.exists(THAM_DINH_FILE)
            and os.path.getmtime(THAM_DINH_FILE) > os.path.getmtime(scan_path)):
        out.append(f"{THAM_DINH_FILE} duoc sua SAU khi ghi {scan_path} — neu la sua "
                   "ro co ban thi phai ghi nhan: ro da doi sau khi nhin ban quet")
    return out


def ghi_che_do(scan_path, cd):
    """Ghi che do thi truong canh candidates_*.json cho lt_allocator.py doc.

    Thieu chuoi VNINDEX -> ghi {"che_do": null}: allocator hieu la KHONG XAC
    DINH (khong mua, khong ban ep), khong lui ve mot che do mac dinh nao.
    """
    out = os.path.join(DATA_DIR, os.path.basename(scan_path).replace("scan_", "che_do_"))
    json.dump(cd or {"che_do": None}, open(out, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return out


def main():
    path = newest("scan_")
    scan, phu = load(path)
    bench = scan.pop("VNINDEX", None)
    if bench is None:
        sys.exit("Thieu VNINDEX — khong tinh duoc suc manh tuong doi.")
    cd = tu_ban_quet(phu)
    td = nap_tham_dinh()
    ro = nap_ro()
    cs, _ = nap_canslim()
    dang_giu = {ma for pk in HOLDINGS for ma, _, _ in HOLDINGS[pk]}

    rows = build_rows(scan, bench, phu)
    for r in rows:
        cua_canslim(r, cs)
        cua_ro(r, td, ro)
        buy_checklist(r)
        sell_checklist(r)

    xu_huong = [r for r in rows if r["qua_loc_cung"]]
    giao = sorted((r for r in rows if r["giao_diem"]), key=thu_tu_mua)
    meta = phu.get("_meta", {})
    print(f"Nguon: {path}  ({meta.get('nguon', 'TradingView')}, du lieu den "
          f"{meta.get('ngay_du_lieu', '?')})")
    theo_san = {}
    for r in rows:
        theo_san.setdefault(r["san"] or "?", [0, 0])
        theo_san[r["san"] or "?"][0] += 1
        theo_san[r["san"] or "?"][1] += r["qua_loc_cung"]
    print("Ro quet: " + " | ".join(f"{s} {q}/{n}" for s, (n, q) in sorted(theo_san.items()))
          + f"  (qua Tang 1 / quet)  => RO XU HUONG {len(xu_huong)} ma")
    print(f"VNINDEX: 12T {bench['r252']*100:+.1f}%  6T {bench['r126']*100:+.1f}%  "
          f"3T {bench['r63']*100:+.1f}%  1T {bench['r21']*100:+.1f}%\n")
    in_che_do(cd)
    print()

    print("KHUNG GIAI DOAN 2 (chot 04/10/2026, muc 14) tren khung top-down 01/10:")
    print("  TRU 1 che do : VNINDEX vs MA50/MA200 + phien phan phoi -> tran co phieu "
          "(GIAM = ban het, khoa mua)")
    print("  MAY   Tang 1 : thanh khoan>=10 ty, gia>MA200, MA50>MA200 — toan "
          "HOSE+HNX+UPCoM  [RS, ATR: DA BO]")
    print("  NGUOI ro     : vi mo -> nganh -> doanh nghiep (V1-V5 + ba truc), trong "
          f"{THAM_DINH_FILE}:{RO_CO_BAN_KHOA}")
    print(f"  GIAO DIEM + B4 + phieu DAT con han + bien an toan >= {BIEN_AN_TOAN_MIN:.0%} "
          "duoi than_trong = duoc mua; thu tu = uu_tien, roi ATR thap")
    if CANSLIM_KET_QUA != "bac_bo":
        print(f"  B3a CANSLIM    : {'CHAN mua' if CANSLIM_CHAN_MUA else 'chi cham'} (muc 12)")

    # ------------------------------------------------------------ Ro co ban
    print(f"\nRO CO BAN — ngay chot: {ro['ngay_chot'] or 'CHUA CHOT'}")
    if ro["vi_mo"].get("ket_luan"):
        print(f"  vi mo ({ro['vi_mo'].get('ngay', '?')}): {ro['vi_mo']['ket_luan']}")
    else:
        print("  vi mo: CHUA CO KET LUAN")
    for ng, v in sorted(ro["nganh"].items()):
        tt = {True: "trong ro", False: "LOAI", None: "chua ket luan"}[v.get("trong_ro")]
        print(f"  nganh {ng:<22} {tt}" + (f" — {v['ly_do']}" if v.get("ly_do") else ""))
    trong_ro = sorted((ma for ma in td if trang_thai_ro(ma, td, ro)[0] is True))
    print(f"  => {len(trong_ro)} ma trong ro: {trong_ro if trong_ro else '(chua co)'}")
    for w in canh_bao_hang_rao(path, ro):
        print(f"  [HANG RAO] {w}")

    # ------------------------------------------------------------ Giao diem
    hdr = (f"{'#':>3} {'Ma':<5} {'San':<5} {'UT':>3} {'Gia':>9} {'ThanTrong':>9} "
           f"{'Bien':>6} {'ATR%':>5} {'Ty/ph':>7} {'B4':>5} {'Mua':>4}  Nganh / vi sao chua mua")
    print(f"\nGIAO DIEM ({len(giao)} ma) — ro xu huong x ro co ban, theo thu tu mua:")
    print(hdr)
    print("-" * len(hdr))
    for i, r in enumerate(giao, 1):
        tt = "?" if r.get("than_trong") is None else f"{r['than_trong']:,.0f}"
        bien = "?" if r.get("bien_an_toan") is None else f"{r['bien_an_toan']*100:+.0f}%"
        vi_sao = "; ".join(x for x in (
            "" if r.get("phieu_ok") else r.get("ly_do_phieu", ""),
            "" if r.get("bien_an_toan_ok") else r.get("ly_do_bien", ""),
            "" if r["buoc4_dinh_gia"] == "dat" else f"B4 {r['buoc4_dinh_gia']}") if x)
        print(f"{i:>3} {r['ma']:<5} {r['san'] or '?':<5} "
              f"{r['uu_tien'] if r['uu_tien'] is not None else '-':>3} {r['gia']:>9,.0f} "
              f"{tt:>9} {bien:>6} {r['atr']*100:>5.2f} {r['tov']/1e9:>7.1f} "
              f"{r['buoc4_dinh_gia']:>5} {'Y' if r['buy_ready'] else 'N':>4}  {r['nganh']}"
              + (f" — {vi_sao}" if vi_sao and not r["buy_ready"] else ""))
    if not giao:
        print("  (khong co ma nao — moi o se nam tien)")
    ds_cho = [r["ma"] for r in giao if r["trong_danh_sach_cho"]]
    if ds_cho:
        print(f"Danh sach cho (trong ro, gia chua hop ly): {ds_cho}")
    chua_b4 = [r["ma"] for r in giao if r["buoc4_dinh_gia"] == "chua"]
    if chua_b4:
        print(f"CHUA DINH GIA (Buoc 4) — chua duoc mua: {chua_b4}")

    by_ma = {r["ma"]: r for r in rows}
    ro_ngoai_xh = [(ma, by_ma[ma]["ly_do_loai_b1"] if ma in by_ma else "khong co trong ban quet")
                   for ma in trong_ro if not (ma in by_ma and by_ma[ma]["qua_loc_cung"])]
    if ro_ngoai_xh:
        print(f"\nTrong ro co ban nhung KHONG qua Tang 1 ({len(ro_ngoai_xh)}):")
        for ma, why in ro_ngoai_xh:
            print(f"  {ma:<5} {why}")
    loi_ro = [(ma, trang_thai_ro(ma, td, ro)[1]) for ma in td
              if td[ma]["trong_ro"] is True and trang_thai_ro(ma, td, ro)[0] is None]
    if loi_ro and ro["ngay_chot"]:
        print("\n[RO THIEU/SAI] nguoi ghi trong_ro = true nhung chua du dieu kien — "
              "KHONG duoc mua:")
        for ma, why in loi_ro:
            print(f"  {ma:<5} {why}")

    # "Tu kiem tra bat buoc": mot lop phu quyet khong bao gio phu quyet thi tren
    # thuc te khong ton tai (Triet_ly_dau_tu_FF5, Buoc 3).
    if ro["ngay_chot"] and not any(trang_thai_ro(ma, td, ro)[0] is False for ma in td):
        print("\n[CANH BAO] Ro co ban khong loai ma nao. Ghi nhan lai — mot lop phu "
              "quyet khong bao gio phu quyet thi khong ton tai.")

    # ------------------------------------------------------------ Quy tac thoat
    print("\nQUY TAC THOAT (sua 04/10/2026, muc 14) — mot cau phu dinh la ban toan bo:")
    print("  moi phien: che do GIAM | chan cung -25% | gia >= co so | 4. khong con "
          "trong ro (nguoi danh)")
    print("  ky soat  : 1. gia < 0,97*MA200        [2. RS, 3. thu hang, 5. cam quan: DA BO]")
    if cd and cd["che_do"] == "GIAM":
        print(f"  ** CHE DO GIAM: moi vi the dang giu deu BAN (lt_allocator.py) **")
    for ma in sorted(dang_giu):
        r = by_ma.get(ma)
        if r is None:
            print(f"  {ma:<5} KHONG CO TRONG BAN QUET — cham tay")
            continue
        sells = [name for name, ok in r["sell_checklist"] if ok]
        ghi = ", ".join(sells) if sells else "giu"
        if r["thieu_ra_soat_ro"]:
            ghi += f"  [quy tac 4 CHUA RO: {r['ly_do_ro']}]"
        elif r["trong_ro_co_ban"] is False:
            ghi += f"  ({r['ly_do_ro']})"
        if r["thieu_co_so"]:
            ghi += "  [THIEU co_so — luat gia tri co so chua xet duoc]"
        else:
            ghi += f"  (co so {r['co_so']:,.0f}, gia {r['gia']:,.0f})"
        if not r["phieu_ok"]:
            ghi += f"  [phieu: {r['ly_do_phieu']} — khong mua them]"
        print(f"  {ma:<5} {ghi}")

    # ---------------------------------------------------------- Quy tac 5
    print(f"\nQUY TAC THU NAM — {QUY_TAC_5['ten']}: DA BO tu "
          f"{QUY_TAC_5.get('het_hieu_luc_tu', '?')} (cam ket #5 tr.70; muc 14). "
          "Moi lenh can PHIEU_LENH ghi truoc gio dat.")

    # Ghi: ro xu huong + moi ma co ban ghi ro + moi ma dang giu. Ma dang giu da
    # roi Tang 1 van co ban ghi -> allocator kiem duoc chan cung -25% bang gia
    # that (sua lo hong muc 10.3: truoc day chi ghi ma qua loc).
    giu_lai = [r for r in rows if r["qua_loc_cung"] or r["ma"] in td or r["ma"] in dang_giu]
    giu_lai.sort(key=lambda r: (not r["giao_diem"], thu_tu_mua(r)))
    out = os.path.join(DATA_DIR, os.path.basename(path).replace("scan_", "candidates_"))
    json.dump(giu_lai, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"\n-> {out}  ({len(giu_lai)} ban ghi)")
    print(f"-> {ghi_che_do(path, cd)}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
