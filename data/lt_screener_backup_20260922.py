"""
lt_screener.py — Tim co phieu MANH HON THI TRUONG de nam giu dai han.

Dau vao : data/scan_YYYYMMDD.json  (quet tu TradingView, xem lt_scan_howto.md)
Dau ra  : bang xep hang ung vien, ghi data/candidates_YYYYMMDD.json cho
          lt_allocator.py doc.

Triet ly:
  * Suc manh tuong doi (RS) so voi VNINDEX la yeu to co bang chung thuc nghiem
    manh nhat o thi truong co phieu — dung no lam truc xep hang.
  * Bo loc xu huong (MA200) khong de DU BAO thi truong, ma de dam bao ta chi
    nam giu nhung ma dang o pha tang. Neu it ma qua duoc loc thi tien mat tang
    len MOT CACH TU DONG — day la cach duy nhat he thong nay "canh thi truong".
    (Da kiem chung 17/08/2026: loc VNINDEX theo MA50 KHONG du bao duoc huong
    chi so — nen tuyet doi khong dung bo loc chi so de quyet dinh cam tien.)
  * Khong dung p (xac suat thang) nua: da kiem chung p khong co suc phan biet
    (kiem dinh hoan vi p-value 0,689). Khong dung P(ve nhat) nua: da bo khung
    cuoc thi ngan han.

Chay: PYTHONIOENCODING=utf-8 python lt_screener.py
"""

import json
import math
import os
import sys

from ranking import pct_rank
from lt_config import (LOC, RS_WEIGHTS, NGANH, EXIT,
                       THAM_DINH_FILE, THAM_DINH_TRANG_THAI, QUY_TAC_5)

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


def nap_tham_dinh():
    """Ket luan Buoc 3 + Buoc 4 do NGUOI nhap. Thieu ban ghi = 'chua'.

    Hai buoc nay co quyen phu quyet va khong duoc suy ra tu du lieu gia
    (Triet_ly_dau_tu_FF5, Bang CL.2). Mac dinh phai la 'chua' chu khong phai
    'dat' — neu mac dinh la dat thi lop phu quyet khong ton tai.
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
        out[ma] = {"buoc3": b3, "buoc4": b4,
                   "ly_do": v.get("ly_do", ""), "luan_diem": v.get("luan_diem", ""),
                   "ngay": v.get("ngay", ""),
                   "luan_diem_con_nguyen": v.get("luan_diem_con_nguyen", None)}
    return out


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
        sys.exit(f"Khong tim thay {DATA_DIR}/{prefix}*.json — chay quet TradingView truoc.")
    return os.path.join(DATA_DIR, fs[-1])


def load(path):
    """Doc ban quet. Cot thieu (ban quet cu) duoc bu None, KHONG bu gia tri mac
    dinh — cot nao khong do duoc phai hien la khong do duoc. Thieu cot goc thi
    dung han vi moi thu con lai deu sai theo.
    """
    raw = json.load(open(path, encoding="utf-8"))
    out = {}
    for k, v in raw.items():
        if k.startswith("_"):
            continue
        if len(v) < FIELDS_GOC:
            sys.exit(f"{path}: {k} chi co {len(v)}/{FIELDS_GOC} cot goc — quet lai.")
        d = dict(zip(FIELDS, v))
        for f in FIELDS[len(v):]:
            d[f] = None
        out[k] = d
    return out


def trend_r2(ds):
    """Chat luong xu huong: R^2 cua log(gia) theo thoi gian tren ~6 thang cuoi.

    Momentum 'muot' (tang deu) ben hon momentum 'giat cuc' (nhay mot phat roi di
    ngang). Dau cua he so goc duoc gan vao ket qua nen xu huong giam -> diem am.
    """
    y = [math.log(v) for v in ds[-13:] if v and v > 0]
    n = len(y)
    if n < 6:
        return 0.0
    xm, ym = (n - 1) / 2, sum(y) / n
    sxy = sum((i - xm) * (y[i] - ym) for i in range(n))
    sxx = sum((i - xm) ** 2 for i in range(n))
    syy = sum((v - ym) ** 2 for v in y)
    if sxx <= 0 or syy <= 0:
        return 0.0
    r2 = (sxy * sxy) / (sxx * syy)
    return r2 if sxy > 0 else -r2


def hard_filter_checks(r):
    """Single source for Step 1 eligibility and its rejection reasons."""
    return [
        ("liquidity", r["tov"] >= LOC["thanh_khoan_min"],
         f"thanh khoan {r['tov']/1e9:.1f} ty"),
        ("close_above_ma200", not LOC["gia_tren_ma200"] or r["gia"] > r["ma200"],
         "duoi MA200"),
        ("ma50_above_ma200", not LOC["ma50_tren_ma200"] or r["ma50"] > r["ma200"],
         "MA50<MA200"),
        ("rs_12m_positive", not LOC["rs_252_duong"] or r["rs_252_skip21"] > 0,
         "thua VNINDEX 12T"),
        ("atr_max", r["atr"] <= LOC["atr_max"], f"ATR {r['atr']*100:.1f}%"),
    ]


def build_rows(scan, bench):
    """Tinh chi so RS + diem cho tung ma. Tra ve (qua_loc, bi_loai)."""
    rows, loai = [], []
    for ma, d in scan.items():
        def rs(k):
            a, b = d.get(k), bench.get(k)
            return None if a is None or b is None else a - b

        # 12 thang BO QUA 21 phien gan nhat (skip-month): dao chieu ngan han
        # lam nhieu tin hieu momentum, day la chuan trong hoc thuat.
        a = (1 + d["r252"]) / (1 + d["r21"]) - 1
        b = (1 + bench["r252"]) / (1 + bench["r21"]) - 1
        rs252_skip = a - b

        r = {
            "ma": ma, "gia": d["c"], "atr": d["atr"], "tov": d["tov_ty"] * 1e9,
            "ma50": d["ma50"], "ma200": d["ma200"], "r252": d["r252"],
            "rs_252_skip21": rs252_skip, "rs_126": rs("r126"),
            "rs_63": rs("r63"), "rs_21": rs("r21"),
            "trend_r2": trend_r2(d["ds"]), "nganh": NGANH.get(ma, "Khac"),
        }

        why = [reason for _, ok, reason in hard_filter_checks(r) if not ok]

        (loai if why else rows).append((ma, ", ".join(why)) if why else r)
    return rows, loai


def score(rows):
    """Buoc 2 — xep hang trong RO DA QUA BO LOC.

    Pham vi tinh phan vi la co y va da duoc chot: "Toan bo thang diem tinh theo
    phan vi trong ro DA QUA BO LOC, khong dung gia tri tuyet doi"
    (Triet_ly_dau_tu_FF5, Buoc 2). Khong doi sang toan ro.

    Ngoai `diem` (gia tri thang diem), ham gan them `thu_hang` = THU HANG VI TRI
    trong ro da loc, 0 = dau bang. Quy tac thoat so 3 hoi "con nam trong nhom
    dan dau bang xep hang?" — do la cau hoi ve THU HANG, khong phai ve gia tri
    diem, nen phai so bang `thu_hang` chu khong phai `diem`.
    """
    for key in RS_WEIGHTS:
        pr = pct_rank([r[key] for r in rows])
        for r, v in zip(rows, pr):
            r["pr_" + key] = v
    for r in rows:
        r["diem"] = sum(RS_WEIGHTS[k] * r["pr_" + k] for k in RS_WEIGHTS)
    rows.sort(key=lambda r: (-r["diem"], r["ma"]))
    n = len(rows)
    group_rank = 0
    for i, r in enumerate(rows):
        if i == 0 or r["diem"] != rows[i - 1]["diem"]:
            group_rank = i
        r["thu"] = i + 1
        # Equal scores share the best position in their group. Symbol order is
        # only a deterministic display/order tie-break, never an exit signal.
        r["thu_hang"] = group_rank / max(1, n - 1)
    return rows


def cua_tham_dinh(r, td):
    """Buoc 3 + Buoc 4 — hai cua do NGUOI quyet, co quyen phu quyet.

    Khong tinh diem tu du lieu gia o day. Ham `investment_score` cu da bi bo:
    no cong diem cho "quality" va "valuation" bang thanh khoan, MA50/MA200,
    R^2 va RS — toan bo la du lieu gia deo nhan co ban. Tai lieu goi dung ten
    cua loi do: day la cach mot quy tu khen minh vi thu von chi la phoi nhiem
    rui ro.
    """
    v = td.get(r["ma"], {})
    r["buoc3_tham_dinh"] = v.get("buoc3", "chua")
    r["buoc4_dinh_gia"] = v.get("buoc4", "chua")
    r["tham_dinh_ly_do"] = v.get("ly_do", "")
    r["luan_diem"] = v.get("luan_diem", "")
    r["tham_dinh_ngay"] = v.get("ngay", "")
    r["luan_diem_con_nguyen"] = v.get("luan_diem_con_nguyen", None)
    r["bi_phu_quyet"] = r["buoc3_tham_dinh"] == "loai"
    r["trong_danh_sach_cho"] = (r["buoc3_tham_dinh"] == "dat"
                                and r["buoc4_dinh_gia"] == "cho")
    return r


def buy_checklist(r):
    """Buoc 1 — bo loc cung. DUNG 5 dieu kien cua Bang CL.1, khong hon.

    Da bo `trend_quality_r2` va `rs_6m_positive` khoi bo loc: R^2 la thanh phan
    XEP HANG o Buoc 2 (trong so 10%), con RS 6 thang la thanh phan xep hang
    (trong so 30%). Dung chung lam cua loc la bien mot tieu chi "de xep truoc
    sau" thanh mot tieu chi "duoc phep hay khong" — sai voi thiet ke "bo loc
    theo phep hoi, khong phai bang diem".
    """
    checks = [(name, ok) for name, ok, _ in hard_filter_checks(r)]
    r["buy_checklist"] = checks
    r["qua_loc_cung"] = all(ok for _, ok in checks)
    # Duoc mua = qua ca bon buoc. Thieu ket luan tham dinh -> KHONG duoc mua.
    r["buy_ready"] = (r["qua_loc_cung"]
                      and r["buoc3_tham_dinh"] == "dat"
                      and r["buoc4_dinh_gia"] == "dat")
    return r


def sell_checklist(r):
    """Bang CL.3 — bon quy tac thoat. Mot cau phu dinh la ban toan bo vi the."""
    nguong = EXIT["giu_khi"]["thu_hang_rs"]
    checks = [
        ("close_below_97pct_ma200", r["gia"] < 0.97 * r["ma200"]),
        ("rs_12m_below_minus_5pct",
         r["rs_252_skip21"] < EXIT["giu_khi"]["rs_12t_toi_thieu"]),
        # Quy tac 3 hoi ve THU HANG trong ro da loc, khong phai ve gia tri diem.
        # Ban cu so `r["diem"] < 0.60` sai hai lan: so gia tri thay vi thu hang,
        # va lay nguong 0,60 von khong lien quan gi toi con so 40%.
        ("rank_below_40pct", r.get("thu_hang", 1.0) > nguong),
        # Quy tac 4 — quy tac duy nhat khong doc du lieu gia. None = chua ra
        # soat: khong tu dong ban, nhung phai bao cao la con thieu.
        ("luan_diem_gay", r.get("luan_diem_con_nguyen") is False),
    ]
    r["sell_checklist"] = checks
    r["sell_ready"] = any(ok for _, ok in checks)
    r["thieu_ra_soat_luan_diem"] = r.get("luan_diem_con_nguyen") is None
    return r


def main():
    path = newest("scan_")
    scan = load(path)
    bench = scan.pop("VNINDEX", None)
    if bench is None:
        sys.exit("Thieu VNINDEX — khong tinh duoc suc manh tuong doi.")
    td = nap_tham_dinh()

    rows, loai = build_rows(scan, bench)          # Buoc 1
    score(rows)                                   # Buoc 2 (phan vi trong ro da loc)
    for r in rows:
        cua_tham_dinh(r, td)                      # Buoc 3 + 4 (nguoi)
        buy_checklist(r)
        sell_checklist(r)

    print(f"Nguon: {path}   |   {len(rows)} ma qua bo loc cung / {len(rows)+len(loai)} ma quet")
    print(f"Tham dinh: {THAM_DINH_FILE} — {len(td)} ban ghi")
    print(f"VNINDEX: 12T {bench['r252']*100:+.1f}%  6T {bench['r126']*100:+.1f}%  "
          f"3T {bench['r63']*100:+.1f}%  1T {bench['r21']*100:+.1f}%\n")
    print("QUY TRINH 4 BUOC (Triet_ly_dau_tu_FF5) — khong co diem bu tru giua cac buoc:")
    print("  B1 bo loc cung : thanh khoan>=10 ty, gia>MA200, MA50>MA200, RS12T(bo 1T)>0, ATR<=6%")
    print("  B2 xep hang    : 0,40*RS12T + 0,30*RS6T + 0,20*RS3T + 0,10*R2, phan vi TRONG RO DA LOC")
    print("  B3 tham dinh   : doanh nghiep -> nganh -> vi mo (NGUOI, co quyen phu quyet)")
    print("  B4 dinh gia    : gia hop ly + diem mua (NGUOI)")

    hdr = (f"{'#':>3} {'Ma':<5} {'Gia':>8} {'Diem':>5} {'Hang':>5} {'RS12T':>7} {'RS6T':>7} "
           f"{'RS3T':>7} {'R2':>5} {'ATR%':>5} {'Ty/ph':>6} {'B3':>5} {'B4':>5} {'Mua':>4}  Nganh")
    print("\n" + hdr)
    print("-" * len(hdr))
    for r in rows:
        print(f"{r['thu']:>3} {r['ma']:<5} {r['gia']:>8.0f} {r['diem']:>5.2f} "
              f"{r['thu_hang']:>5.2f} "
              f"{r['rs_252_skip21']*100:>+6.1f}% {r['rs_126']*100:>+6.1f}% "
              f"{r['rs_63']*100:>+6.1f}% {r['trend_r2']:>5.2f} {r['atr']*100:>5.2f} "
              f"{r['tov']/1e9:>6.1f} {r['buoc3_tham_dinh']:>5} {r['buoc4_dinh_gia']:>5} "
              f"{'Y' if r['buy_ready'] else 'N':>4}  {r['nganh']}")

    cho_td = [r for r in rows if r["buoc3_tham_dinh"] == "chua"]
    bi_loai_b3 = [r for r in rows if r["bi_phu_quyet"]]
    ds_cho = [r for r in rows if r["trong_danh_sach_cho"]]
    mua_duoc = [r for r in rows if r["buy_ready"]]

    print(f"\nMUA DUOC ngay: {len(mua_duoc)} ma "
          f"{[r['ma'] for r in mua_duoc] if mua_duoc else '(chua co)'}")
    if ds_cho:
        print(f"Danh sach cho (dat B3, gia chua hop ly): {[r['ma'] for r in ds_cho]}")
    if cho_td:
        print(f"CHUA THAM DINH — khong duoc mua cho toi khi co ket luan B3/B4: "
              f"{[r['ma'] for r in cho_td]}")
        print(f"  -> nhap ket luan vao {THAM_DINH_FILE}")

    # "Tu kiem tra bat buoc": mot lop phu quyet khong bao gio phu quyet thi tren
    # thuc te khong ton tai (Triet_ly_dau_tu_FF5, Buoc 3).
    if td and not bi_loai_b3:
        print("\n[CANH BAO] Ky ra soat nay lop tham dinh khong loai duoc ma nao. "
              "Ghi nhan lai — mot lop phu quyet khong bao gio phu quyet thi khong ton tai.")

    print("\nBON QUY TAC THOAT (Bang CL.3) — mot cau phu dinh la ban toan bo:")
    print("  1. gia < 0,97*MA200   2. RS12T < -5%   "
          f"3. thu hang > {EXIT['giu_khi']['thu_hang_rs']:.0%} ro da loc   "
          "4. luan diem doanh nghiep da gay")
    for r in rows:
        sells = [name for name, ok in r["sell_checklist"] if ok]
        ghi = ", ".join(sells) if sells else "giu"
        if r["thieu_ra_soat_luan_diem"]:
            ghi += "  [quy tac 4 chua ra soat]"
        print(f"  {r['thu']:>2}. {r['ma']:<5} {ghi}")

    # ---------------------------------------------------------- Quy tac 5
    # 11/09/2026: quy tac 5 la quy tac TUY NGHI — screener khong sinh tin hieu
    # cho no. So lenh va kiem tra tran 50% nam o lt_allocator.py.
    print(f"\nQUY TAC THU NAM — {QUY_TAC_5['ten']} (tu {QUY_TAC_5['hieu_luc_tu']}):")
    print(f"  NGUOI quyet, he thong khong sinh tin hieu. Toi da "
          f"{QUY_TAC_5['ty_le_ban_toi_da']:.0%} moi vi the moi lan; hieu luc toi "
          f"{QUY_TAC_5['hieu_luc_toi']}. Ghi vao LENH_QUY_TAC_5 TRUOC khi dat lenh.")
    print(f"\nBi loai o Buoc 1 ({len(loai)}):")
    for ma, why in sorted(loai):
        print(f"  {ma:<5} {why}")

    out = os.path.join(DATA_DIR, os.path.basename(path).replace("scan_", "candidates_"))
    json.dump(rows, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"\n-> {out}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
