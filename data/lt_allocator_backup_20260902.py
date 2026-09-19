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

from lt_config import (PORTFOLIOS, HOLDINGS, TIEN_MAT, TRAN_TRUNG_LAP,
                       FEE_BUY, FEE_SELL, LOT, EXIT)
from lt_screener import newest

DEM_PHI = 0.02          # chua 2% cho phi + lam tron lo


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
    tran_tl = TRAN_TRUNG_LAP * tong_ts
    print(f"Tong tai san 2 danh muc: {tong_ts:,.0f} d   "
          f"(tran trung lap {TRAN_TRUNG_LAP:.0%} = {tran_tl:,.0f} d/ma)\n")

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

    # --- Vong 3: tran trung lap ap SAU khi da lam tron lo, cat tung lo mot tu
    #     danh muc dang giu nhieu tien nhat o ma do. Ap truoc khi lam tron se
    #     lam mot danh muc mat trang vi thieu vai tram nghin so voi 1 lo.
    for ma, g in gia.items():
        def gt(pk):
            return plan[pk]["kl"].get(ma, 0) * g
        while sum(gt(pk) for pk in plan) > tran_tl:
            pk = max(plan, key=gt)
            if plan[pk]["kl"].get(ma, 0) <= 0:
                break
            plan[pk]["kl"][ma] -= LOT
            if plan[pk]["kl"][ma] * g < plan[pk]["cfg"]["ticket_toi_thieu"]:
                plan[pk]["kl"][ma] = 0

    # --- Vong 4: in bang + lenh
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
            note = "" if kl else "1 lo vuot tran/ticket -> bo qua, o nay nam tien"
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
        print("\nLENH BAN (bon quy tac thoat):")
        ban_kl, lenh, phi = {}, 0, 0
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
                ly_do = ""
                print(f"  [?]  {kl:>7,} {ma:<5} — roi khoi bo loc cung, khong co "
                      f"trong bang xep hang. Cham tay theo 4 quy tac truoc khi quyet.")
            else:
                vi_pham = [n for n, ok in c.get("sell_checklist", []) if ok]
                ly_do = ", ".join(vi_pham)
            # chan cung -25% so voi gia von: ngoai le duy nhat giua hai ky ra soat
            gv = von.get(ma, 0)
            if gv and g <= gv * (1 - EXIT["stop_tham_hoa"]):
                ly_do = (ly_do + ", " if ly_do else "") + "cham chan cung -25%"
            if not ly_do:
                continue
            ban_kl[ma] = kl
            lenh += 1
            phi += kl * g * FEE_SELL
            print(f"  BAN  {kl:>7,} {ma:<5} x {g:>8,.0f} = {kl*g:>13,.0f}  "
                  f"phi {kl*g*FEE_SELL:>9,.0f}  — {ly_do}")
        if not lenh:
            print("  (khong co — moi vi the con tra loi CO cho ca bon cau hoi)")

        print("\nLENH MUA (o trong sau khi ban, theo thu hang Buoc 2):")
        for c in P["chosen"]:
            ma = c["ma"]
            cur = dang_giu.get(ma, 0) - ban_kl.get(ma, 0)
            d = P["kl"].get(ma, 0) - cur
            if d <= 0:
                continue
            g = c["gia"]
            lenh += 1
            phi += d * g * FEE_BUY
            print(f"  MUA  {d:>7,} {ma:<5} x {g:>8,.0f} = {d*g:>13,.0f}  "
                  f"phi {d*g*FEE_BUY:>9,.0f}")
        if not P["chosen"]:
            print("  (khong co ma nao qua du 4 buoc — phan von nay nam tien "
                  "cho toi ky ra soat sau)")
        print("  (khong co lenh)" if lenh == 0 else
              f"  => {lenh} lenh, tong phi {phi:,.0f} d ({phi/NAV*100:.2f}% NAV)")

        con_lai = {ma: kl - ban_kl.get(ma, 0) for ma, kl in dang_giu.items()
                   if kl - ban_kl.get(ma, 0) > 0}
        gt_cp = sum(kl * (gia.get(ma) or von.get(ma, 0)) for ma, kl in con_lai.items())
        tien = NAV - gt_cp
        print(f"\nSAU KHI DAT LENH: {len(con_lai)} ma "
              f"({', '.join(sorted(con_lai)) if con_lai else 'khong con ma nao'})")
        print(f"  co phieu {gt_cp:>13,.0f} ({gt_cp/NAV:>5.1%})   "
              f"tien mat {tien:>13,.0f} ({tien/NAV:>5.1%})")
        print()


if __name__ == "__main__":
    if not os.path.isdir("data"):
        sys.exit("Thieu thu muc data/")
    main()
