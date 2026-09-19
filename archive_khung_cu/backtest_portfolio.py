"""
backtest_portfolio.py — Backtest CA chien luoc lan ENGINE PHAN BO tren cung du lieu.

Cau hoi: tang softmax(ER) co them gia tri that khong, hay chi la trang tri?

Thiet ke tranh nhin trom tuong lai (walk-forward):
  Voi moi cum ngay k, p cua tung loai setup CHI duoc uoc luong tu cac cum 1..k-1,
  co ve base rate bang Beta prior (chong nhieu mau nho). Cum dau tien khong co
  lich su nen roi hoan toan ve prior.

Phan ra hai hieu ung:
  EW-all   : can bang deu tren TOAN BO ung vien cua cum   (dung nhu backtest goc)
  EW-topN  : can bang deu tren dung N ma softmax da chon  (tach hieu ung CHON MA)
  Softmax  : trong so softmax(ER/tau) tren N ma do        (them hieu ung DANH TRONG SO)

  Softmax - EW-topN = gia tri cua viec DANH TRONG SO
  EW-topN - EW-all  = gia tri cua viec CHON MA
"""

import re
from collections import defaultdict

import numpy as np
import openpyxl

from allocator import softmax, effective_tau, cap_weights, MAX_WEIGHT
from exit_rules import load, evaluate, legs_trail, legs_A

XLSX = "Backtest_khuyen_nghi_30-07_den_10-08-2026.xlsx"
RNG = np.random.default_rng(3)

B_RULE   = 0.82     # b do duoc cua luat trailing 3% (exit_rules.py)
PRIOR_K  = 5.0      # Do manh cua Beta prior (so "lenh ao")
PRIOR_P  = 0.65     # Base rate khi chua co lich su
TOP_N    = 4        # So vi the — khop voi ket qua sau rang buoc ticket toi thieu


# ------------------------------------------------------------------ Phan loai
LIMIT_KW = ("vùng", "chỉnh về", "mua hồi", "không đuổi")
BREAK_KW = ("vượt", "breakout", "phá ", "đóng cửa >", "đỉnh", "kích hoạt khi")
OPEN_KW  = ("danh sách lọc", "giá mở cửa")


def classify(text):
    """Loai setup, chi dung thong tin co TRUOC khi vao lenh."""
    t = (text or "").lower()
    if any(k in t for k in OPEN_KW):
        return "MO_CUA"
    pos_l = min((t.find(k) for k in LIMIT_KW if k in t), default=10**6)
    pos_b = min((t.find(k) for k in BREAK_KW if k in t), default=10**6)
    if pos_l == pos_b == 10**6:
        return "KHAC"
    return "CHINH" if pos_l < pos_b else "BREAKOUT"


def attach_setup(trades):
    wb = openpyxl.load_workbook(XLSX, data_only=True)
    ws = wb["Backtest khuyến nghị"]
    texts = defaultdict(list)
    for row in ws.iter_rows(5, ws.max_row, values_only=True):
        if row[3] and row[4]:
            texts[(row[1], row[3], float(row[4]))].append(row[2])
    for t in trades:
        key = next((k for k in texts if k[0] == t["ma"] and abs(k[2] - t["entry"]) < 1), None)
        t["setup"] = classify(texts[key].pop(0)) if key and texts[key] else "KHAC"
    return trades


# ------------------------------------------------------------------ Backtest
def shrunk_p(hist):
    """p uoc luong voi Beta prior: (thang + k*prior) / (n + k)."""
    if not hist:
        return PRIOR_P
    w = sum(1 for a in hist if a > 0)
    return (w + PRIOR_K * PRIOR_P) / (len(hist) + PRIOR_K)


def run(trades, top_n=TOP_N, verbose=True):
    cohorts = defaultdict(list)
    for t in trades:
        cohorts[t["entry_i"]].append(t)
    keys = sorted(cohorts)

    hist = defaultdict(list)            # setup -> danh sach alpha da quan sat
    rows, sm, e_top, e_all = [], [], [], []

    for k in keys:
        cands = cohorts[k]
        ps = {c["ma"] + str(id(c)): shrunk_p(hist[c["setup"]]) for c in cands}
        ers = np.array([ps[c["ma"] + str(id(c))] * (B_RULE + 1) - 1 for c in cands])

        live = [(c, er) for c, er in zip(cands, ers) if er > 1e-9]
        live.sort(key=lambda x: -x[1])
        live = live[:top_n]

        if live:
            e = np.array([er for _, er in live])
            w = cap_weights(softmax(e, effective_tau(e)), MAX_WEIGHT)
            a_sm = float(sum(wi * c["alpha"] for (c, _), wi in zip(live, w)))
            a_et = float(np.mean([c["alpha"] for c, _ in live]))
        else:                            # Khong ma nao qua cong -> cam tien
            a_sm = a_et = 0.0
        a_ea = float(np.mean([c["alpha"] for c in cands]))

        sm.append(a_sm); e_top.append(a_et); e_all.append(a_ea)
        rows.append((k, len(cands), len(live), a_sm, a_et, a_ea))

        for c in cands:                  # Chi cap nhat lich su SAU khi da phan bo
            hist[c["setup"]].append(c["alpha"])

    if verbose:
        print(f"{'Cum':>6}{'Ung vien':>10}{'Chon':>6}{'Softmax':>10}"
              f"{'EW-topN':>10}{'EW-all':>10}")
        print("-" * 52)
        for k, nc, nl, a, b, c in rows:
            print(f"{DATES[k]:>6}{nc:>10}{nl:>6}{a:>10.2%}{b:>10.2%}{c:>10.2%}")
        print("-" * 52)
    return np.array(sm), np.array(e_top), np.array(e_all)


def compound(x):
    return float(np.prod(1 + x) - 1)


def boot_ci(a, b, n=20000):
    d = np.array(a) - np.array(b)
    idx = RNG.integers(0, len(d), size=(n, len(d)))
    m = d[idx].sum(axis=1)
    return d.sum(), np.percentile(m, 2.5), np.percentile(m, 97.5)


if __name__ == "__main__":
    DATES, prices, trades = load()
    vni = prices["VNINDEX"]["Đóng"]
    n = len(DATES)

    for rule_name, fn in [("C. Trailing stop 3%", lambda t: legs_trail(t, prices, n, 0.03)),
                          ("A. Chot tai Muc tieu 1", lambda t: legs_A(t, prices, n))]:
        for t in trades:
            t["alpha"] = evaluate(t, fn(t), vni)[2]
        attach_setup(trades)

        print(f"\n{'='*72}\nLUAT THOAT: {rule_name}\n{'='*72}")
        counts = defaultdict(lambda: [0, 0])
        for t in trades:
            counts[t["setup"]][0] += 1
            counts[t["setup"]][1] += t["alpha"] > 0
        print("Phan loai setup (toan mau, chi de tham khao — backtest dung walk-forward):")
        for s, (c, w) in sorted(counts.items(), key=lambda kv: -kv[1][0]):
            al = np.mean([t["alpha"] for t in trades if t["setup"] == s])
            print(f"   {s:<10}{c:>3} lenh   thang {w}/{c} = {w/c:>5.1%}   alpha TB {al:>+7.2%}")
        print()

        sm, et, ea = run(trades)
        print(f"{'Gop 6 cum':<22}{'Softmax':>10}{'EW-topN':>10}{'EW-all':>10}")
        print(f"{'':<22}{compound(sm):>10.2%}{compound(et):>10.2%}{compound(ea):>10.2%}")

        d1, lo1, hi1 = boot_ci(sm, et)
        d2, lo2, hi2 = boot_ci(et, ea)
        d3, lo3, hi3 = boot_ci(sm, ea)
        print(f"\n  Hieu ung DANH TRONG SO (Softmax - EW-topN): {d1:>+7.2%}  "
              f"[{lo1:>+6.2%}, {hi1:>+6.2%}]")
        print(f"  Hieu ung CHON MA      (EW-topN - EW-all) : {d2:>+7.2%}  "
              f"[{lo2:>+6.2%}, {hi2:>+6.2%}]")
        print(f"  TONG                  (Softmax - EW-all) : {d3:>+7.2%}  "
              f"[{lo3:>+6.2%}, {hi3:>+6.2%}]")

    print(f"\n{'='*72}\nDO NHAY THEO SO VI THE (luat C)\n{'='*72}")
    for t in trades:
        t["alpha"] = evaluate(t, legs_trail(t, prices, n, 0.03), vni)[2]
    attach_setup(trades)
    print(f"{'N vi the':<12}{'Softmax':>10}{'EW-topN':>10}{'EW-all':>10}")
    for N in (2, 3, 4, 5, 6):
        s, e, a = run(trades, top_n=N, verbose=False)
        print(f"{N:<12}{compound(s):>10.2%}{compound(e):>10.2%}{compound(a):>10.2%}")
