"""
exit_rules.py — Phan thuc nghiem: giu nguyen 40 tin hieu vao lenh, doi luat thoat.

Cau hoi 1: luat "thoat toan bo khi cham Muc tieu 1" co cat cut duoi phai khong?
Cau hoi 2: phan cai thien la ALPHA that hay chi la BETA do giu lau hon trong
           mot thi truong dang tang?

Cau hoi 2 moi la cau quyet dinh. Cua so 30/07-10/08 co VNINDEX tang +0,194%/phien,
nen bat ky luat nao keo dai nam giu deu duoc cong beta mien phi. So sanh tho se
danh lua. Moi luat vi vay deu duoc do bang alpha = ty suat gop - VNINDEX cung ky.

Rang buoc: T+2. Phi: mua 0,15% — ban 0,25% (gom thue).
Alpha tinh tren TY SUAT GOP de dong nhat voi cot 17 cua file goc.
"""

import numpy as np
import openpyxl

XLSX = "Backtest_khuyen_nghi_30-07_den_10-08-2026.xlsx"
FEE_BUY, FEE_SELL = 0.0015, 0.0025
T_PLUS = 2
RNG = np.random.default_rng(7)


def load():
    wb = openpyxl.load_workbook(XLSX, data_only=True)

    ws = wb["Dữ liệu giá gốc"]
    dates = [c for c in next(ws.iter_rows(4, 4, values_only=True))[2:] if c]
    prices, cur = {}, None
    for row in ws.iter_rows(5, ws.max_row, values_only=True):
        if row[0]:
            cur = row[0]
            prices[cur] = {}
        if cur and row[1]:
            prices[cur][row[1]] = [float(v) if v is not None else None
                                   for v in row[2:2 + len(dates)]]

    ws = wb["Backtest khuyến nghị"]
    trades, dropped = [], 0
    for row in ws.iter_rows(5, ws.max_row, values_only=True):
        ngay_mua, ma, gia_mua = row[3], row[1], row[4]
        if not ngay_mua or not gia_mua or ma not in prices:
            continue
        # Lenh vao dung phien cuoi cua du lieu co thoi gian nam giu = 0 phien:
        # VNINDEX cung ky = 0 nen "alpha" cua chung chi la bien dong trong phien
        # khong duoc tru chi so. Loai bo, neu khong bootstrap bi thoi phong.
        if dates.index(ngay_mua) >= len(dates) - 1:
            dropped += 1
            continue
        ngay_ban = row[5]
        trades.append({
            "ma": ma,
            "entry_i": dates.index(ngay_mua),
            "exit_i_A": dates.index(ngay_ban) if ngay_ban in dates else len(dates) - 1,
            "entry": float(gia_mua),
            "ket_qua": row[7] or "",
            "gross_A": float(row[8]) if row[8] is not None else None,
        })
    if dropped:
        print(f"[loc] Loai {dropped} lenh vao phien cuoi ({dates[-1]}) — nam giu 0 phien.")
    return dates, prices, trades


class Leg:
    """Mot lan thoat: ty trong w, thoat tai chi so ngay exit_i, gia exit_px."""

    def __init__(self, w, exit_i, exit_px):
        self.w, self.exit_i, self.exit_px = w, exit_i, exit_px


def evaluate(t, legs, vni):
    """Tra ve (gross, net, alpha) tong hop tu cac leg."""
    gross = net = alpha = 0.0
    for lg in legs:
        g = lg.exit_px / t["entry"] - 1
        n = (lg.exit_px * (1 - FEE_SELL)) / (t["entry"] * (1 + FEE_BUY)) - 1
        m = vni[lg.exit_i] / vni[t["entry_i"]] - 1        # VNINDEX cung ky
        gross += lg.w * g
        net   += lg.w * n
        alpha += lg.w * (g - m)
    return gross, net, alpha


def legs_A(t, prices, n):
    """Luat hien tai: thoat toan bo tai Muc tieu 1 / cat lo, dung ket qua that."""
    px = t["entry"] * (1 + t["gross_A"]) if t["gross_A"] is not None \
        else prices[t["ma"]]["Đóng"][t["exit_i_A"]]
    return [Leg(1.0, t["exit_i_A"], px)]


def _trail_exit(t, prices, n, trail, start_i):
    """Chi so ngay thoat theo trailing stop tren gia dong cua."""
    c = prices[t["ma"]]["Đóng"]
    peak = c[start_i]
    for i in range(start_i + 1, n):
        peak = max(peak, c[i])
        if i >= t["entry_i"] + T_PLUS and c[i] < peak * (1 - trail):
            return i
    return n - 1


def legs_trail(t, prices, n, trail):
    i = _trail_exit(t, prices, n, trail, t["entry_i"])
    return [Leg(1.0, i, prices[t["ma"]]["Đóng"][i])]


def legs_hold(t, prices, n):
    return [Leg(1.0, n - 1, prices[t["ma"]]["Đóng"][n - 1])]


def legs_half(t, prices, n, trail):
    """Ban 1/2 tai Muc tieu 1, 1/2 con lai chay trailing tu ngay do."""
    if "mục tiêu" not in t["ket_qua"].lower() or t["gross_A"] is None:
        return legs_trail(t, prices, n, trail)
    t1_px = t["entry"] * (1 + t["gross_A"])
    hit = next((i for i in range(t["entry_i"] + T_PLUS, n)
                if prices[t["ma"]]["Cao"][i] >= t1_px), n - 1)
    j = _trail_exit(t, prices, n, trail, hit)
    return [Leg(0.5, hit, t1_px), Leg(0.5, j, prices[t["ma"]]["Đóng"][j])]


def stats(rows, label):
    net = np.array([r[1] for r in rows])
    alpha = np.array([r[2] for r in rows])
    wins, losses = net[net > 0], net[net <= 0]
    p = len(wins) / len(net)
    W = wins.mean() if len(wins) else 0.0
    L = -losses.mean() if len(losses) else 1e-9
    b = W / L
    print(f"{label:<32}{p:>7.1%}{b:>6.2f}{p*b-(1-p):>7.2f}"
          f"{net.mean():>10.2%}{alpha.mean():>10.2%}"
          f"{(alpha>0).mean():>9.1%}{net.max():>8.2%}")
    return net, alpha


def paired_ci(a, b, n_boot=20000):
    d = np.array(b) - np.array(a)
    idx = RNG.integers(0, len(d), size=(n_boot, len(d)))
    m = d[idx].mean(axis=1)
    return d.mean(), np.percentile(m, 2.5), np.percentile(m, 97.5)


if __name__ == "__main__":
    dates, prices, trades = load()
    n = len(dates)
    vni = prices["VNINDEX"]["Đóng"]
    drift = (vni[-1] / vni[0]) ** (1 / (n - 1)) - 1
    print(f"Du lieu: {n} phien ({dates[0]}–{dates[-1]}), {len(trades)} lenh khop")
    print(f"VNINDEX cua so nay: {vni[-1]/vni[0]-1:+.2%} tong = {drift:+.3%}/phien "
          f"— THI TRUONG TANG MANH\n")

    rules = [("A. Chot tai Muc tieu 1 (hien tai)", lambda t: legs_A(t, prices, n)),
             ("B. Giu den 10/08 (khong chot)",     lambda t: legs_hold(t, prices, n))]
    for tr in (0.03, 0.05, 0.07):
        rules.append((f"C. Trailing stop {tr:.0%}",
                      lambda t, tr=tr: legs_trail(t, prices, n, tr)))
    for tr in (0.03, 0.05):
        rules.append((f"D. Nua tai T1 + nua trail {tr:.0%}",
                      lambda t, tr=tr: legs_half(t, prices, n, tr)))

    print(f"{'Luat thoat':<32}{'p':>7}{'b':>6}{'ER':>7}"
          f"{'Net TB':>10}{'ALPHA TB':>10}{'% co a':>9}{'Max':>8}")
    print("-" * 89)
    out = {}
    for label, fn in rules:
        out[label] = stats([evaluate(t, fn(t), vni) for t in trades], label)

    base_net, base_alpha = out["A. Chot tai Muc tieu 1 (hien tai)"]
    print("\n" + "=" * 89)
    print("CHENH LECH SO VOI LUAT A — ghep cap tren cung 40 entry, bootstrap 95%")
    print("=" * 89)
    print(f"{'Luat':<32}{'d Net':>9}{'KTC 95%':>22}{'d ALPHA':>10}{'KTC 95%':>22}")
    print("-" * 89)
    for label, (nt, al) in out.items():
        if label.startswith("A."):
            continue
        dn, lo_n, hi_n = paired_ci(base_net, nt)
        da, lo_a, hi_a = paired_ci(base_alpha, al)
        star = " *" if (lo_a > 0 or hi_a < 0) else ""
        print(f"{label:<32}{dn:>+9.2%}  [{lo_n:>+6.2%},{hi_n:>+6.2%}]"
              f"{da:>+10.2%}  [{lo_a:>+6.2%},{hi_a:>+6.2%}]{star}")
    print("-" * 89)
    print("  * = chenh lech alpha co y nghia thong ke (khoang tin cay khong chua 0)")

    still_open = sum(1 for t in trades
                     if _trail_exit(t, prices, n, 0.05, t["entry_i"]) == n - 1)
    print(f"\nCANH BAO: {still_open}/{len(trades)} lenh cua trailing 5% van con mo o 10/08.")
    print("  Trailing stop gan nhu KHONG BAO GIO kich hoat trong cua so 10 phien")
    print("  -> 'C' va 'B' thuc chat la cung mot luat. Can du lieu dai hon de tach.")
