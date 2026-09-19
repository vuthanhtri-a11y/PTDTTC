"""
lt_allocator.py — Phan bo danh muc dai han theo RUI RO NGANG NHAU (risk parity tho).

Thay the hoan toan allocator.py cu (softmax(ER)). Ly do doi:
  * Backtest 14/08/2026 cho thay tang xep hang theo ER TE HON boc tham (phan vi
    4%) vi p khong co suc phan biet. Softmax khuech dai p theo ham mu -> khuech
    dai nhieu.
  * Vi vay diem RS chi dung de CHON (vao/khong vao), khong dung de chia ty trong.
    Chia ty trong theo 1/ATR — moi vi the dong gop rui ro nhu nhau. Day la cau
    tra loi cho phat hien 17/08: trailing % co dinh khong trung tinh voi bien dong.

Tien mat KHONG do canh thi truong ma sinh ra: moi "o" (slot) khong tim duoc ma
qua duoc bo loc thi o do nam tien mat. It ma manh = it giai ngan.

Chay: PYTHONIOENCODING=utf-8 python lt_allocator.py
"""

import json
import os
import sys
from datetime import datetime

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment

from lt_config import (PORTFOLIOS, HOLDINGS, TIEN_MAT,
                       FEE_BUY, FEE_SELL, LOT, EXIT, LENH_NGOAI_LUAT,
                       QUY_TAC_5, LENH_QUY_TAC_5,
                       LICH_SOAT, KHOA_WHIPSAW, BAO_LUU_TIN_HIEU)
from lt_screener import newest

DEM_PHI = 0.02          # chua 2% cho phi + lam tron lo

# Mot nguon duy nhat cho "hom nay". Truoc 16/09/2026 moi cho goi datetime.now()
# rieng le; gio lich soat co ngay bo sung nen ngay chay quyet dinh ca lenh ban
# lan lenh mua -> phai nhat quan trong mot lan chay. Ghi de bang bien moi truong
# de chay ca gia lap: NGAY_CHAY=2026-09-21 python lt_allocator.py
HOM_NAY = os.environ.get("NGAY_CHAY") or datetime.now().strftime("%Y-%m-%d")


def khoa_quy_tac_5(pk, hom_nay):
    """KL KHONG duoc mua lai theo tung ma, do lenh quy tac 5 da GIA HAN hop le.

    Mac dinh (user chot 11/09/2026) la KY SOAT LAY LAI QUYEN: lenh ban theo cam
    quan het hieu luc o ky soat ke tiep, allocator mua lai neu ma con qua bon
    quy tac — nen mac dinh ham nay tra ve rong. Chi khoa khi quy da ghi
    `gia_han_den` va `ngay_ghi_gia_han` TRUOC ngay chay (ngay soat). Gia han ghi
    trong/sau ngay soat la gia han sau khi nhin bang lenh -> khong co hieu luc.
    Ngay dang ISO "YYYY-MM-DD" nen so sanh chuoi la so sanh ngay.
    """
    khoa = {}
    for L in LENH_QUY_TAC_5:
        if L.get("dm", "DM2") != pk or L.get("trang_thai") != "da khop":
            continue
        han, ghi = L.get("gia_han_den"), L.get("ngay_ghi_gia_han")
        if han and ghi and ghi < hom_nay <= han:
            khoa[L["ma"]] = khoa.get(L["ma"], 0) + L.get("kl_ban", 0)
    return khoa


def la_ky_bo_sung(pk, hom_nay):
    """Hom nay co phai ky soat BO SUNG cua danh muc nay khong (chot 16/09/2026)?

    Ky bo sung = moc do ban to chuc cuoc thi dat, khong phai dau thang. Hien chi
    co 21/09/2026 cho DM2 (giai doan 2 cua cuoc thi). Ky dau thang van chay binh
    thuong va KHONG di qua ham nay.
    """
    return (pk in LICH_SOAT["dm_bo_sung"]
            and hom_nay in LICH_SOAT["ngay_bo_sung"])


def bao_luu_ma(pk, ma, hom_nay):
    """Ma nay co duoc DIEU KHOAN BAO LUU giu lai o ky bo sung khong?

    Tin hieu ban phat sinh TRUOC moc 16/09/2026 giu nguyen lich thuc thi cu
    (01/10). Chi co hieu luc trong ky BO SUNG — den ky dau thang thi bao luu het
    tac dung va lenh ban chay binh thuong.

    Tra ve chuoi ly do (truthy) neu bao luu, "" neu khong.
    """
    if not la_ky_bo_sung(pk, hom_nay):
        return ""
    if hom_nay >= BAO_LUU_TIN_HIEU["thuc_thi_tai"]:
        return ""
    return BAO_LUU_TIN_HIEU["ma"].get(ma, "")


def khoa_whipsaw(pk, hom_nay):
    """KL KHONG duoc mua lai vi da bi BON QUY TAC THOAT ban o ky bo sung.

    Khoa toi `khoa_den` (01/11/2026). Chan dung vong ban-roi-mua-lai do nhieu
    giua hai ky cach nhau 7 phien. Khac `khoa_quy_tac_5`: cai kia khoa lenh TUY
    NGHI da gia han, cai nay khoa lenh DUNG LUAT o ky bo sung.
    """
    khoa = {}
    if hom_nay >= KHOA_WHIPSAW["khoa_den"]:
        return khoa
    for L in KHOA_WHIPSAW["ban_ky_bo_sung"]:
        if L.get("dm", "DM2") != pk or L["ngay"] > hom_nay:
            continue
        khoa[L["ma"]] = khoa.get(L["ma"], 0) + L.get("kl", 0)
    return khoa


def eligible(cands):
    """Ma duoc phep giai ngan = qua ca 4 buoc, xep theo thu hang Buoc 2.

    25/08/2026: bo `score_ready`/`investment_score`. Thu tu uu tien bay gio do
    DUY NHAT bang xep hang Buoc 2 quyet dinh — dung nhu tai lieu: "Thu hang
    quyet dinh ma nao duoc chon truoc, khong quyet dinh mua bao nhieu."
    `buy_ready` da bao gom ket luan tham dinh B3/B4, nen ma chua tham dinh
    khong lot vao day.
    """
    ok = [dict(c) for c in cands if c.get("buy_ready")]
    ok.sort(key=lambda c: (c.get("thu", 10**6), c["ma"]))
    return ok


def top_picks(cands, limit=5):
    """Tra ve top N ma theo score, san sang mua va danh gia nang luc."""
    return eligible(cands)[:limit]


def chon(cands, cfg):
    """Chon toi da N ma theo diem, ton trong tran nganh."""
    N = cfg["so_vi_the"]
    # Khong co nhanh du phong "ha chuan cho du o": o nao khong tim duoc ma dat
    # chuan thi o do nam tien. Do la toan bo co che sinh ra tien mat.
    ranked = eligible(cands)
    # +1e-9: 0.30 / (1/10) ra 2,9999... trong dau phay dong -> int() cat con 2.
    tran_n = max(1, int(cfg["tran_nganh"] * N + 1e-9))  # so ma toi da / nganh
    ra, dem = [], {}
    for c in ranked:
        if len(ra) >= N:
            break
        ng = c["nganh"]
        if dem.get(ng, 0) >= tran_n:
            c["ghi_chu"] = f"bo qua — day tran nganh {ng}"
            continue
        dem[ng] = dem.get(ng, 0) + 1
        ra.append(c)
    return ra


def ty_trong(chosen, cfg):
    """1/ATR chuan hoa, ap tran ma, phan phoi lai phan bi cat."""
    N = cfg["so_vi_the"]
    base = (1 - DEM_PHI) / N
    tong = base * len(chosen)                # o trong = tien mat
    raw = {c["ma"]: 1.0 / max(c["atr"], 1e-6) for c in chosen}
    s = sum(raw.values())
    w = {k: v / s * tong for k, v in raw.items()}

    for _ in range(20):                      # ap tran, lap lai cho hoi tu
        thua = sum(max(0.0, v - cfg["tran_ma"]) for v in w.values())
        if thua < 1e-9:
            break
        con = [k for k, v in w.items() if v < cfg["tran_ma"] - 1e-9]
        for k in w:
            w[k] = min(w[k], cfg["tran_ma"])
        if not con:
            break
        sc = sum(w[k] for k in con)
        for k in con:
            w[k] += thua * (w[k] / sc if sc > 0 else 1.0 / len(con))
    return w


def nav(pk, gia):
    hold = sum(kl * gia.get(ma, gv) for ma, kl, gv in HOLDINGS[pk])
    return TIEN_MAT[pk] + hold


def khoi_luong(tien, gia, tran_tien, ticket_min):
    """Lam tron ve lo GAN NHAT (khong phai lam tron xuong) roi kiem tra tran.

    Lam tron xuong lam mat han nhung vi the ma 1 lo da gan bang ca ty trong muc
    tieu (vi du VIC gia 198k) — do la loi thiet ke, khong phai than trong.
    """
    if gia <= 0:
        return 0
    kl = int(round(tien / gia / LOT)) * LOT
    while kl > 0 and kl * gia > tran_tien:
        kl -= LOT
    if kl * gia < ticket_min:
        return 0
    return kl


def status_for_signal(c):
    """Map a candidate to a user-facing status for Excel formatting."""
    if c.get("sell_ready"):
        return "Bán"
    if c.get("buy_ready"):
        return "Mua"
    if c.get("qua_loc_cung") and c.get("buoc3_tham_dinh") == "chua":
        return "Chờ thẩm định"
    return "Cảnh báo"


def export_excel(cands, navs, out_path):
    """Xuat bang ung vien, top picks va danh muc dang giu sang file Excel."""
    wb = Workbook()
    thin = Side(style="thin", color="D9D9D9")
    header_fill = PatternFill("solid", fgColor="D9EAF7")
    header_font = Font(bold=True, color="000000")
    fill_map = {
        "Mua": PatternFill("solid", fgColor="C6EFCE"),
        "Cảnh báo": PatternFill("solid", fgColor="FFF2CC"),
        "Bán": PatternFill("solid", fgColor="F4CCCC"),
    }

    def style_header(ws):
        for cell in ws[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = Border(left=thin, right=thin, top=thin, bottom=thin)
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions

    top = eligible(cands)

    ws = wb.active
    ws.title = "Top picks"
    headers = ["Ma", "Nganh", "Gia", "ATR%", "RS12T", "RS6T", "RS3T", "RS1T", "R2", "B3/B4", "Buy", "Sell", "Diem", "Trang thai"]
    ws.append(headers)
    style_header(ws)
    for c in top:
        status = status_for_signal(c)
        row = [
            c["ma"], c["nganh"], c["gia"], f"{c['atr'] * 100:.2f}%",
            f"{c['rs_252_skip21'] * 100:+.1f}%", f"{c['rs_126'] * 100:+.1f}%",
            f"{c['rs_63'] * 100:+.1f}%", f"{c['rs_21'] * 100:+.1f}%",
            f"{c['trend_r2']:.2f}",
            f"{c.get('buoc3_tham_dinh', 'chua')}/{c.get('buoc4_dinh_gia', 'chua')}",
            "Y" if c.get("buy_ready") else "N",
            "Y" if c.get("sell_ready") else "N",
            f"{c['diem']:.2f}", status,
        ]
        ws.append(row)
        for cell in ws[ws.max_row]:
            cell.border = Border(left=thin, right=thin, top=thin, bottom=thin)
            cell.fill = fill_map.get(status, PatternFill("solid", fgColor="FFFFFF"))
            if cell.column in (3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14):
                cell.alignment = Alignment(horizontal="right")

    ws2 = wb.create_sheet("All candidates")
    headers2 = ["Ma", "Nganh", "Gia", "ATR%", "RS12T", "RS6T", "RS3T", "RS1T", "R2", "B3/B4", "Buy", "Sell", "Diem", "Trang thai"]
    ws2.append(headers2)
    style_header(ws2)
    for c in sorted(cands, key=lambda x: x["ma"]):
        status = status_for_signal(c)
        row = [
            c["ma"], c["nganh"], c["gia"], f"{c['atr'] * 100:.2f}%",
            f"{c['rs_252_skip21'] * 100:+.1f}%", f"{c['rs_126'] * 100:+.1f}%",
            f"{c['rs_63'] * 100:+.1f}%", f"{c['rs_21'] * 100:+.1f}%",
            f"{c['trend_r2']:.2f}",
            f"{c.get('buoc3_tham_dinh', 'chua')}/{c.get('buoc4_dinh_gia', 'chua')}",
            "Y" if c.get("buy_ready") else "N",
            "Y" if c.get("sell_ready") else "N",
            f"{c['diem']:.2f}", status,
        ]
        ws2.append(row)
        for cell in ws2[ws2.max_row]:
            cell.border = Border(left=thin, right=thin, top=thin, bottom=thin)
            cell.fill = fill_map.get(status, PatternFill("solid", fgColor="FFFFFF"))
            if cell.column in (3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14):
                cell.alignment = Alignment(horizontal="right")

    ws3 = wb.create_sheet("Danh mục đang giữ")
    headers3 = ["TaiKhoan", "Ma", "GiaHienTai", "GiaVon", "SoLuong", "GiaTri", "%NAV", "Trang thai", "Ghi chu"]
    ws3.append(headers3)
    style_header(ws3)
    for pk, cfg in PORTFOLIOS.items():
        na = navs.get(pk, 0)
        for ma, qty, cost in HOLDINGS.get(pk, []):
            match = next((c for c in cands if c["ma"] == ma), None)
            current_price = float(match["gia"]) if match else cost
            value = qty * current_price
            status = status_for_signal(match) if match else "Cảnh báo"
            row = [pk, ma, current_price, cost, qty, value, f"{(value / na) * 100:.1f}%" if na > 0 else "0.0%", status, "Giữ theo chiến lược" if not (match and match.get("sell_ready")) else "Cần xem xét bán"]
            ws3.append(row)
            for cell in ws3[ws3.max_row]:
                cell.border = Border(left=thin, right=thin, top=thin, bottom=thin)
                cell.fill = fill_map.get(status, PatternFill("solid", fgColor="FFFFFF"))
                if cell.column in (3, 4, 5, 6, 7):
                    cell.alignment = Alignment(horizontal="right")

    ws4 = wb.create_sheet("Quy trinh 4 buoc")
    headers4 = ["Ma", "B1 bo loc cung", "B2 thu hang", "B2 diem", "B3 tham dinh",
                "B4 dinh gia", "Ly do loai / luan diem", "Ngay tham dinh",
                "BuyReady", "SellReady", "Status", "Nganh"]
    ws4.append(headers4)
    style_header(ws4)
    for c in sorted(cands, key=lambda x: x.get("thu", 10**6)):
        status = status_for_signal(c)
        row = [
            c["ma"],
            "dat" if c.get("qua_loc_cung") else "loai",
            c.get("thu", ""), round(c.get("diem", 0), 3),
            c.get("buoc3_tham_dinh", "chua"), c.get("buoc4_dinh_gia", "chua"),
            c.get("tham_dinh_ly_do") or c.get("luan_diem", ""),
            c.get("tham_dinh_ngay", ""),
            "Y" if c.get("buy_ready") else "N", "Y" if c.get("sell_ready") else "N",
            status, c.get("nganh", "Khac"),
        ]
        ws4.append(row)
        for cell in ws4[ws4.max_row]:
            cell.border = Border(left=thin, right=thin, top=thin, bottom=thin)
            cell.fill = fill_map.get(status, PatternFill("solid", fgColor="FFFFFF"))
            if cell.column in (2, 3, 4, 5, 6, 9, 10, 11):
                cell.alignment = Alignment(horizontal="center")

    if os.path.exists(out_path):
        try:
            os.remove(out_path)
        except PermissionError:
            pass
    wb.save(out_path)
    return out_path


def main():
    cands = json.load(open(newest("candidates_"), encoding="utf-8"))
    gia = {c["ma"]: c["gia"] for c in cands}
    diem = {c["ma"]: c["diem"] for c in cands}

    top = top_picks(cands, limit=5)
    qua_b1 = [c for c in cands if c.get("qua_loc_cung")]
    cho_td = [c for c in qua_b1 if c.get("buoc3_tham_dinh") == "chua"]
    print("TOP 5 MA DUOC PHEP GIAI NGAN (qua ca 4 buoc), xep theo thu hang Buoc 2\n")
    print(f"{'Ma':<5} {'Hang':>5} {'Diem':>6} {'RS12T':>8} {'R2':>6} {'ATR%':>6} "
          f"{'Ty/ph':>8} {'B3':>5} {'B4':>5} {'Nganh':<12}")
    print("-" * 88)
    if not top:
        print("(khong co ma nao — xem ghi chu ben duoi)")
    for c in top:
        print(f"{c['ma']:<5} {c.get('thu', 0):>5} {c['diem']:>6.2f} "
              f"{c['rs_252_skip21']*100:>+7.1f}% {c['trend_r2']:>6.2f} {c['atr']*100:>6.2f} "
              f"{c['tov']/1e9:>8.1f} {c.get('buoc3_tham_dinh', 'chua'):>5} "
              f"{c.get('buoc4_dinh_gia', 'chua'):>5} {c['nganh']:<12}")
    if cho_td:
        print(f"\n{len(qua_b1)} ma qua Buoc 1, nhung {len(cho_td)} ma CHUA co ket luan "
              f"tham dinh Buoc 3/4 nen chua duoc phep mua:")
        print("  " + ", ".join(f"{c['ma']}(#{c.get('thu', '?')})" for c in cho_td))
        print("  -> nhap ket luan vao data/tham_dinh.json roi chay lai.")
    print()

    navs = {pk: nav(pk, gia) for pk in PORTFOLIOS}
    today = datetime.now().strftime("%Y%m%d")
    excel_path = os.path.join("data", f"bao_cao_dau_tu_{today}.xlsx")
    export_excel(cands, navs, excel_path)
    print(f"-> Excel: {excel_path}")

    tong_ts = sum(navs.values())
    print(f"Tong tai san 2 danh muc: {tong_ts:,.0f} d\n")

    # --- Vong 1: ty trong muc tieu cua tung danh muc (chi rang buoc tran ma)
    plan = {}
    for pk, cfg in PORTFOLIOS.items():
        chosen = chon([dict(c) for c in cands], cfg)
        w = ty_trong(chosen, cfg)
        plan[pk] = {"chosen": chosen, "w": w, "cfg": cfg,
                    "tien": {c["ma"]: w[c["ma"]] * navs[pk] for c in chosen}}

    # --- Vong 2: quy ra lo (chi ap tran ma cua tung danh muc)
    for pk, P in plan.items():
        P["kl"] = {c["ma"]: khoi_luong(P["tien"][c["ma"]], c["gia"],
                                       P["cfg"]["tran_ma"] * navs[pk],
                                       P["cfg"]["ticket_toi_thieu"])
                   for c in P["chosen"]}

    # --- Vong 3 (tran trung lap) DA BO ngay 02/09/2026 theo quyet dinh cua user.
    #     Xem khoi ghi chu "Tran trung lap: DA BO" trong lt_config.py de biet ly do
    #     va bang chung. Tu day chan tap trung chi con tran ma + tran nganh, ap
    #     ngay trong vong 1-2. Ban ghi cu: data/lt_allocator_backup_20260902.py

    # --- Vong 3: in bang + lenh
    for pk, cfg in PORTFOLIOS.items():
        NAV, P = navs[pk], plan[pk]
        if NAV <= 0:
            # Du lieu danh muc dang bi xoa tam (vi du DM1 tu 25/08/2026).
            # Khong sinh bang lenh cho danh muc khong biet von — chi bao trang thai.
            print("=" * 78)
            print(f"{pk} — {cfg['ten']}")
            print("KHONG CO DU LIEU VON (HOLDINGS rong va TIEN_MAT = 0).")
            print("Bo qua phan bo. Cap nhat lt_config.py roi chay lai; ban ghi cu "
                  "o data/lt_config_backup_20260825.py.")
            print("=" * 78 + "\n")
            continue
        print("=" * 78)
        print(f"{pk} — {cfg['ten']}")
        print(f"Von ban dau {cfg['von_ban_dau']:,.0f}  |  NAV hien tai {NAV:,.0f}  "
              f"|  {len(P['chosen'])}/{cfg['so_vi_the']} o co ung vien")
        print("=" * 78)
        print(f"{'Ma':<5} {'Diem':>5} {'ATR%':>5} {'w':>6} {'Gia':>8} "
              f"{'KL':>7} {'Gia tri':>13} {'%NAV':>6}  Ghi chu")
        print("-" * 78)
        tong_mua = 0
        for c in P["chosen"]:
            ma = c["ma"]          # phai gan truoc: ve phai cua phep gan bo doi
            kl = P["kl"][ma]      # duoc tinh TRUOC khi ma duoc gan lai
            tong_mua += kl * c["gia"]
            # Ghi chu phai noi dung rang buoc NAO chan, khong gop chung "tran/ticket":
            # ban cu in "1 lo vuot tran/ticket" ke ca khi 1 lo THAP hon ticket, tuc
            # nguoc han. 02/09/2026 phat hien khi truy vet DHC.
            if kl:
                note = ""
            elif LOT * c["gia"] > cfg["tran_ma"] * NAV:
                note = (f"1 lo {LOT*c['gia']:,.0f} > tran ma {cfg['tran_ma']:.0%} NAV "
                        f"({cfg['tran_ma']*NAV:,.0f}) -> o nay nam tien")
            else:
                note = (f"1 lo {LOT*c['gia']:,.0f} < ticket toi thieu "
                        f"{cfg['ticket_toi_thieu']:,.0f} -> o nay nam tien")
            print(f"{ma:<5} {diem[ma]:>5.2f} {c['atr']*100:>5.2f} {P['w'][ma]:>5.1%} "
                  f"{c['gia']:>8,.0f} {kl:>7,} {kl*c['gia']:>13,.0f} "
                  f"{kl*c['gia']/NAV:>6.1%}  {note}")
        print("-" * 78)
        print(f"{'MUC TIEU CP':<11} {'':>13} {'':>8} {'':>7} {tong_mua:>13,.0f} "
              f"{tong_mua/NAV:>6.1%}")
        print(f"{'MUC TIEU TM':<11} {'':>13} {'':>8} {'':>7} {NAV-tong_mua:>13,.0f} "
              f"{1-tong_mua/NAV:>6.1%}")
        print("  (danh muc MUC TIEU cua cac o DA co ma qua du 4 buoc — "
              "khong phai trang thai hien tai)")

        dang_giu = {ma: kl for ma, kl, _ in HOLDINGS[pk]}
        von = {ma: gv for ma, _, gv in HOLDINGS[pk]}
        by_ma = {c["ma"]: c for c in cands}

        # LENH BAN chi den tu BON QUY TAC THOAT (Bang CL.3), khong den tu viec
        # "ma nay khong nam trong danh muc muc tieu".
        #
        # Ban cu tinh d = tgt - cur roi ban phan chenh lech, tuc moi ky ra soat
        # la mot lan tai co cau ve muc tieu. Ba he qua sai:
        #   * ma khong lot top N bi ban du con dat ca bon quy tac thoat — trong
        #     khi tai lieu noi ro chi ban khi co MOT cau tra loi phu dinh;
        #   * ma chua tham dinh xong lam `chosen` rong -> ban sach danh muc;
        #   * backtest do la ban theo quy tac thoat, khong phai tai co cau toan
        #     bo. (Con so cu "13,89% vs 6,95%" da bi thay: do lai tren 4 pha luoi
        #     ngay 26/08/2026 cho 9,05% cho ban quy-tac-thoat. Chieu so sanh giu
        #     nguyen, do lon thi khong.)
        # --- Giai doan 1: TINH (chua in) lenh ban theo bon quy tac thoat.
        ban_kl, ly_do_ban, cham_tay, hoan_ban = {}, {}, [], []
        for ma, kl in sorted(dang_giu.items()):
            c = by_ma.get(ma)
            g = gia.get(ma) or von.get(ma, 0)
            if c is None:
                # 26/08/2026 — doi tu B2 sang B1. Ban cu ban ngay khi ma roi khoi
                # bo loc cung; do la mot quy tac thoat THU NAM khong co trong Bang
                # CL.3, ma tai lieu chi cho phep ban theo bon cau hoi. Backtest 4
                # pha luoi: B1 tot hon B2 o ca 4/4 pha (TB +0,33 diem pt/nam).
                # `lt_screener.py` chi ghi ra ma qua bo loc, nen ma roi khoi loc
                # khong co ban ghi -> khong du can cu de ban, phai ra soat tay.
                #
                # ⚠️ Gom lai in o giai doan 4 chu khong in ngay: giai doan 1 chay
                # TRUOC tieu de "LENH BAN" nen in tai cho se lac khoi bang lenh.
                ly_do = ""
                cham_tay.append((ma, kl))
            else:
                vi_pham = [n for n, ok in c.get("sell_checklist", []) if ok]
                ly_do = ", ".join(vi_pham)
            # chan cung -25% so voi gia von: ngoai le duy nhat giua hai ky ra soat
            gv = von.get(ma, 0)
            if gv and g <= gv * (1 - EXIT["stop_tham_hoa"]):
                ly_do = (ly_do + ", " if ly_do else "") + "cham chan cung -25%"
            if not ly_do:
                continue
            # Dieu khoan bao luu (16/09/2026): tin hieu ban phat sinh TRUOC moc
            # giu nguyen lich thuc thi cu -> khong dat lenh o ky bo sung.
            bl = bao_luu_ma(pk, ma, HOM_NAY)
            if bl:
                hoan_ban.append((ma, kl, ly_do, bl))
                continue
            ban_kl[ma] = kl
            ly_do_ban[ma] = ly_do

        # --- Giai doan 2: TINH lenh mua. `cur` la vi the TRUOC khi tru lenh ban;
        #     phan chong lan duoc bu tru o giai doan 3 chu khong o day.
        mua_kl = {}
        for c in P["chosen"]:
            ma = c["ma"]
            cur = dang_giu.get(ma, 0) - ban_kl.get(ma, 0)
            d = P["kl"].get(ma, 0) - cur
            if d > 0:
                mua_kl[ma] = d

        # --- Giai doan 2b: quy tac 5 da gia han hop le -> khong mua lai phan da
        #     ban. Khong gia han thi ky soat lay lai quyen, khong co gi de lam.
        da_khoa = {}
        for ma, n in khoa_quy_tac_5(pk, HOM_NAY).items():
            if mua_kl.get(ma, 0) > 0:
                da_khoa[ma] = min(n, mua_kl[ma])
                mua_kl[ma] -= da_khoa[ma]
                if mua_kl[ma] <= 0:
                    del mua_kl[ma]

        # --- Giai doan 2c: khoa chong whipsaw (chot 16/09/2026). Ma bi bon quy
        #     tac thoat ban o ky BO SUNG 21/09 khong duoc mua lai o ky 01/10.
        da_khoa_ws = {}
        for ma, n in khoa_whipsaw(pk, HOM_NAY).items():
            if mua_kl.get(ma, 0) > 0:
                da_khoa_ws[ma] = min(n, mua_kl[ma])
                mua_kl[ma] -= da_khoa_ws[ma]
                if mua_kl[ma] <= 0:
                    del mua_kl[ma]

        # --- Giai doan 3: BU TRU ban/mua cung mot ma (sua 02/09/2026).
        #
        # Ban cu in ca BAN 200 BSR lan MUA 200 BSR trong cung mot bang: quy tac
        # thoat 3 duoi BSR ra (hang 0,70 > 0,40) trong khi `chon()` lap toi 8 o
        # tu danh sach du dieu kien nen no quay lai ngay o duoi. Ket qua la mot
        # vong rua — vi the khong doi, chi mat phi hai chieu.
        #
        # Day KHONG phai hanh vi da backtest. Trong `lt_backtest_scope.js`, ma
        # roi khoi `keep` van nam trong `pool` va duoc chon lai, nhung harness
        # tinh vong quay bang `to += Math.abs(w[k] - prev[k])` (dong 123) nen
        # tyle giu nguyen => turnover 0, chi phi 0. Neu ban that roi mua lai that
        # thi ket qua thuc te se kem backtest dung bang phan phi do — mot khoan
        # lech co he thong, khong phai ngau nhien.
        #
        # Bu tru la sua cho KHOP HARNESS, khong phai doi luat: quy tac thoat van
        # kich hoat, bang xep hang van chon lai, chi khong dat lenh cho phan
        # chong lan. Phan du (neu ban nhieu hon mua, hoac nguoc lai) van thanh
        # lenh that.
        bu_tru = {}
        for ma in set(ban_kl) & set(mua_kl):
            n = min(ban_kl[ma], mua_kl[ma])
            if n <= 0:
                continue
            bu_tru[ma] = n
            ban_kl[ma] -= n
            mua_kl[ma] -= n
            if ban_kl[ma] <= 0:
                del ban_kl[ma]
            if mua_kl[ma] <= 0:
                del mua_kl[ma]

        # --- Giai doan 4: in bang lenh (da bu tru)
        lenh, phi = 0, 0
        if cham_tay:
            print("\nPHAI CHAM TAY (roi khoi bo loc cung -> khong co trong bang "
                  "xep hang, khong du can cu ap quy tac 3):")
            for ma, kl in cham_tay:
                gv = von.get(ma, 0)
                print(f"  [?]  {kl:>7,} {ma:<5} gia von {gv:>8,.0f} — ra soat tay "
                      f"theo 4 quy tac thoat truoc khi quyet.")
            print("       (chan cung -25% KHONG kiem duoc cho nhom nay: "
                  "candidates_*.json khong co gia cua ma da roi khoi bo loc)")
        if la_ky_bo_sung(pk, HOM_NAY):
            print(f"\n*** KY SOAT BO SUNG {HOM_NAY} (moc giai doan 2 "
                  f"cuoc thi, do BTC dat - chot 16/09/2026). Ky dau thang "
                  f"01/10 VAN GIU. Han chot lenh mua: "
                  f"{LICH_SOAT['han_chot_lenh_mua_ky_bo_sung']} ***")
        print("\nLENH BAN (bon quy tac thoat):")
        for ma in sorted(ban_kl):
            kl = ban_kl[ma]
            g = gia.get(ma) or von.get(ma, 0)
            lenh += 1
            phi += kl * g * FEE_SELL
            print(f"  BAN  {kl:>7,} {ma:<5} x {g:>8,.0f} = {kl*g:>13,.0f}  "
                  f"phi {kl*g*FEE_SELL:>9,.0f}  — {ly_do_ban[ma]}")
        if not ban_kl:
            print("  (khong co — moi vi the con tra loi CO cho ca bon cau hoi)")

        print("\nLENH MUA (o trong sau khi ban, theo thu hang Buoc 2):")
        for ma in sorted(mua_kl, key=lambda m: by_ma[m].get("thu", 10**6)):
            d = mua_kl[ma]
            g = gia[ma]
            lenh += 1
            phi += d * g * FEE_BUY
            print(f"  MUA  {d:>7,} {ma:<5} x {g:>8,.0f} = {d*g:>13,.0f}  "
                  f"phi {d*g*FEE_BUY:>9,.0f}")
        if not mua_kl:
            print("  (khong co lenh mua)" if P["chosen"] else
                  "  (khong co ma nao qua du 4 buoc — phan von nay nam tien "
                  "cho toi ky ra soat sau)")
        print("  (khong co lenh)" if lenh == 0 else
              f"  => {lenh} lenh, tong phi {phi:,.0f} d ({phi/NAV*100:.2f}% NAV)")

        if bu_tru:
            print("\nDA BU TRU (khong dat lenh — vi the khong doi):")
            for ma in sorted(bu_tru):
                g = gia.get(ma) or von.get(ma, 0)
                tiet_kiem = bu_tru[ma] * g * (FEE_SELL + FEE_BUY)
                print(f"  {bu_tru[ma]:>7,} {ma:<5} — quy tac thoat doi ban "
                      f"({ly_do_ban[ma]}), bang xep hang doi mua lai cung so luong. "
                      f"Tranh duoc {tiet_kiem:,.0f} d phi rua.")

        if da_khoa:
            print("\nKHOA BOI QUY TAC 5 (quy da gia han — khong mua lai phan da ban):")
            for ma in sorted(da_khoa):
                print(f"  {da_khoa[ma]:>7,} {ma:<5} — xem LENH_QUY_TAC_5")

        if da_khoa_ws:
            print(f"\n[KHOA MUA LAI] — ban o ky bo sung, khoa den "
                  f"{KHOA_WHIPSAW['khoa_den']}:")
            for ma in sorted(da_khoa_ws):
                print(f"  {da_khoa_ws[ma]:>7,} {ma:<5} — chong whipsaw giua "
                      f"hai ky cach 7 phien; xem KHOA_WHIPSAW")

        if hoan_ban:
            print(f"\n[BAO LUU {BAO_LUU_TIN_HIEU['thuc_thi_tai']}] — quy "
                  f"tac thoat DA kich hoat nhung KHONG dat lenh o ky bo sung nay:")
            for ma, kl, ly_do, bl in hoan_ban:
                print(f"  {kl:>7,} {ma:<5} — {ly_do}")
                print(f"          {bl}")
            print("       (tin hieu phat sinh truoc moc "
                  f"{BAO_LUU_TIN_HIEU['moc']} -> giu lich thuc thi cu. "
                  "Luat moi khong hoi to.)")

        # --- Giai doan 5: trang thai sau lenh.
        #
        # Ban cu chi tru lenh BAN, khong cong lenh MUA, nen bao "3 ma / 43,3% CP"
        # trong khi bang lenh ngay tren no van co lenh mua. Sua 02/09/2026.
        con_lai = {}
        for ma in set(dang_giu) | set(mua_kl):
            kl = dang_giu.get(ma, 0) - ban_kl.get(ma, 0) + mua_kl.get(ma, 0)
            if kl > 0:
                con_lai[ma] = kl
        gt_cp = sum(kl * (gia.get(ma) or von.get(ma, 0)) for ma, kl in con_lai.items())
        nav_sau = NAV - phi             # NAV sau lenh = NAV truoc - phi
        tien = nav_sau - gt_cp
        # Ty trong phai chia cho NAV SAU phi, khong phai NAV truoc — chia cho NAV
        # truoc thi hai ty trong cong lai ra 99,9% chu khong phai 100%.
        print(f"\nSAU KHI DAT LENH: {len(con_lai)} ma "
              f"({', '.join(sorted(con_lai)) if con_lai else 'khong con ma nao'})")
        print(f"  co phieu {gt_cp:>13,.0f} ({gt_cp/nav_sau:>5.1%})   "
              f"tien mat {tien:>13,.0f} ({tien/nav_sau:>5.1%})   "
              f"NAV {nav_sau:,.0f}")
        print()


def in_lenh_ngoai_luat():
    """In so lenh ngoai luat. CHI NHAC, khong tu dong thuc hien bat cu gi.

    De o cuoi bang lenh vi day la thu duy nhat trong ca duong ong KHONG do he
    thong sinh ra. Neu no khong duoc in ra moi lan chay thi den cuoi ky se
    khong ai nho la no ton tai, va bao cao se ke lai moi thu nhu the deu la luat.
    """
    if not LENH_NGOAI_LUAT:
        return
    print("\nSO LENH NGOAI LUAT — nguoi quyet, he thong KHONG sinh ra:")
    for L in LENH_NGOAI_LUAT:
        print(f"  #{L.get('so', '?')}  {L['ngay']}  {L['ma']}  [{L['trang_thai']}]")
        print(f"      ten      : {L['ten']}")
        print(f"      viec     : {L['viec']}")
        if L.get("ke_hoach_dao_nguoc"):
            print(f"      con treo : {L['ke_hoach_dao_nguoc']}  (han {L['han_chot']})")
            print(f"      het han  : {L['neu_khong_khop']}")
        if L.get("so_hoc_da_do"):
            print(f"      so hoc   : {L['so_hoc_da_do']}")
        if L.get("bang_chung_nguoc"):
            print(f"      [NGUOC]  : {L['bang_chung_nguoc']}")
    print()


def in_lenh_quy_tac_5():
    """In so lenh quy tac 5 (ban theo cam quan) + kiem tra hai rang buoc da chot.

    Khong tu dong thuc hien gi. Hai phep kiem la thu duy nhat may lam duoc voi
    mot quy tac tuy nghi: (1) moi lenh ban khong qua ty_le_ban_toi_da cua vi the,
    (2) ban ghi du truong — nhat la `cam_quan`, ly do bang loi ghi truoc lenh.
    """
    Q = QUY_TAC_5
    print(f"SO LENH QUY TAC 5 — {Q['ten']} (tuy nghi, tu {Q['hieu_luc_tu']}):")
    if not LENH_QUY_TAC_5:
        print("  (chua co lenh nao)\n")
        return
    hom_nay = datetime.now().strftime("%Y-%m-%d")
    for L in LENH_QUY_TAC_5:
        thieu = [f for f in Q["truong_bat_buoc"] if L.get(f) in (None, "")]
        print(f"  #{L.get('so', '?')}  {L.get('ngay', '?')}  {L.get('dm', 'DM2')}  "
              f"{L.get('ma', '?')}  [{L.get('trang_thai', '?')}]"
              + (f"  [THIEU: {', '.join(thieu)}]" if thieu else ""))
        kt, kb = L.get("kl_truoc") or 0, L.get("kl_ban") or 0
        tran = kt * Q["ty_le_ban_toi_da"]
        print(f"      ban      : {kb:,}/{kt:,} CP @{L.get('gia') or 0:,.0f}"
              + (f"  [VUOT TRAN {Q['ty_le_ban_toi_da']:.0%}: toi da {tran:,.0f} CP]"
                 if kt and kb > tran + 1e-9 else ""))
        print(f"      cam quan : {L.get('cam_quan') or '—'}")
        if L.get("sai_khi"):
            print(f"      sai khi  : {L['sai_khi']}")
        han, ghi = L.get("gia_han_den"), L.get("ngay_ghi_gia_han")
        if not han:
            print("      hieu luc : toi ky soat ke tiep — allocator duoc mua lai "
                  "neu ma con qua bon quy tac")
        elif not ghi or ghi >= hom_nay:
            print(f"      hieu luc : [GIA HAN KHONG HOP LE] den {han} nhung ngay ghi "
                  f"{ghi or '?'} khong truoc ngay chay {hom_nay} -> coi nhu khong gia han")
        else:
            print(f"      hieu luc : gia han den {han} (ghi ngay {ghi})")
    print()


if __name__ == "__main__":
    if not os.path.isdir("data"):
        sys.exit("Thieu thu muc data/")
    main()
    in_lenh_ngoai_luat()
    in_lenh_quy_tac_5()
