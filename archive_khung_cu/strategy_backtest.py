"""
strategy_backtest.py — Backtest chien luoc DE XUAT, do bang cung thuoc do.

Chien luoc de xuat (4 diem):
  1. Luat thoat: trailing stop 3%          (da kiem chung, +0,38% alpha/lenh)
  2. Bo xep hang theo ER                    (da kiem chung: te hon boc tham)
  3. Van tap trung 4 vi the                 (da kiem chung: tap trung mien phi)
  4. Chon 4 ma theo BIEN DONG CAO NHAT      <-- CHUA KIEM CHUNG, do o day

Logic diem 4: neu tap trung mien phi ve alpha va muc tieu la P(ve nhat) thi nen
chon theo tieu chi phuc vu truc tiep duoi phai — tuc bien dong — thay vi theo ER
(dang phuc vu nhieu). Do la GIA THUYET; file nay kiem tra no.

Bien dong do walk-forward: chi dung cac phien TRUOC ngay vao lenh.
Dung TB cua (Cao-Thap)/Dong thay vi do lech chuan loi nhuan — on dinh hon voi 3-5 bar.
"""

from collections import defaultdict

import numpy as np

from backtest_portfolio import attach_setup, compound
from exit_rules import load, evaluate, legs_trail, legs_A

RNG     = np.random.default_rng(17)
N_BOOT  = 100_000
CYCLES  = 8            # ~40 phien thi dau / ~5 phien moi vong
TOP_N   = 4


def vol_before(ma, prices, before_i):
    """Bien dong quan sat duoc TRUOC phien vao lenh."""
    h, l, c = prices[ma]["Cao"], prices[ma]["Thấp"], prices[ma]["Đóng"]
    v = [(h[i] - l[i]) / c[i] for i in range(before_i)
         if h[i] and l[i] and c[i]]
    return float(np.mean(v)) if v else np.nan


def by_cohort(trades):
    g = defaultdict(list)
    for t in trades:
        g[t["entry_i"]].append(t)
    return g


def run_selector(trades, prices, key, n=TOP_N, reverse=True):
    """Tra ve alpha va net cua tung cum, chon n ma theo ham key, can bang deu."""
    g, a_out, n_out = by_cohort(trades), [], []
    for k in sorted(g):
        c = sorted(g[k], key=lambda t: key(t, prices), reverse=reverse)[:n]
        a_out.append(float(np.mean([t["alpha"] for t in c])))
        n_out.append(float(np.mean([t["net"] for t in c])))
    return np.array(a_out), np.array(n_out)


def run_all(trades, prices):
    g, a, nt = by_cohort(trades), [], []
    for k in sorted(g):
        a.append(float(np.mean([t["alpha"] for t in g[k]])))
        nt.append(float(np.mean([t["net"] for t in g[k]])))
    return np.array(a), np.array(nt)


def random_dist(trades, n=TOP_N, n_draw=20000):
    g = by_cohort(trades)
    keys = sorted(g)
    out = np.empty(n_draw)
    for j in range(n_draw):
        tot = 1.0
        for k in keys:
            arr = np.array([t["alpha"] for t in g[k]])
            m = min(n, len(arr))
            tot *= 1 + arr[RNG.choice(len(arr), m, replace=False)].mean()
        out[j] = tot - 1
    return out


def p_win(cycle_alphas, field_sigma, n_rivals=7):
    """Block bootstrap {CYCLES} vong tu alpha cap danh muc, roi so voi 7 doi thu."""
    draws = RNG.integers(0, len(cycle_alphas), size=(N_BOOT, CYCLES))
    total = np.prod(1 + cycle_alphas[draws], axis=1) - 1
    rivals = RNG.normal(0.0, field_sigma, size=(N_BOOT, n_rivals))
    return total, float((total > rivals.max(axis=1)).mean())


if __name__ == "__main__":
    dates, prices, trades = load()
    n, vni = len(dates), prices["VNINDEX"]["Đóng"]

    # --- Bien dong walk-forward cua tung lenh ---
    for t in trades:
        t["vol"] = vol_before(t["ma"], prices, t["entry_i"])
    print(f"\nBien dong walk-forward: TB {np.nanmean([t['vol'] for t in trades]):.2%}"
          f"  |  dai {np.nanmin([t['vol'] for t in trades]):.2%}"
          f"–{np.nanmax([t['vol'] for t in trades]):.2%}")

    K_VOL = lambda t, p: (t["vol"] if not np.isnan(t["vol"]) else -1)
    K_ER  = lambda t, p: t["_er"]

    scenarios = []
    for exit_name, fn in [("A", lambda t: legs_A(t, prices, n)),
                          ("C", lambda t: legs_trail(t, prices, n, 0.03))]:
        for t in trades:
            g, nt_, al = evaluate(t, fn(t), vni)
            t["alpha"], t["net"] = al, nt_
        attach_setup(trades)

        a_all, n_all = run_all(trades, prices)
        a_hi, n_hi = run_selector(trades, prices, K_VOL, reverse=True)
        a_lo, n_lo = run_selector(trades, prices, K_VOL, reverse=False)
        scenarios += [
            (f"Thoat {exit_name} + EW toan bo ung vien", a_all, n_all),
            (f"Thoat {exit_name} + 4 ma BIEN DONG CAO", a_hi, n_hi),
            (f"Thoat {exit_name} + 4 ma bien dong THAP", a_lo, n_lo),
        ]
        if exit_name == "C":
            rand = random_dist(trades)

    print("\n" + "=" * 88)
    print("HIEU SUAT GOP 6 CUM")
    print("=" * 88)
    print(f"{'Chien luoc':<40}{'Alpha':>9}{'Net':>9}{'sd/cum':>9}{'Min cum':>10}{'Max cum':>10}")
    print("-" * 88)
    for label, a, nt_ in scenarios:
        print(f"{label:<40}{compound(a):>9.2%}{compound(nt_):>9.2%}"
              f"{a.std(ddof=1):>9.2%}{a.min():>10.2%}{a.max():>10.2%}")
    print("-" * 88)
    print(f"{'Thoat C + chon NGAU NHIEN 4 (moc so sanh)':<40}{rand.mean():>9.2%}"
          f"{'—':>9}{'—':>9}{np.percentile(rand,5):>10.2%}{np.percentile(rand,95):>10.2%}")

    hi = next(a for lb, a, _ in scenarios if lb == "Thoat C + 4 ma BIEN DONG CAO")
    lo = next(a for lb, a, _ in scenarios if lb == "Thoat C + 4 ma bien dong THAP")
    print(f"\n  Chon bien dong CAO nam o phan vi {(rand < compound(hi)).mean():.0%}"
          f" cua phan phoi ngau nhien")
    print(f"  Chon bien dong THAP nam o phan vi {(rand < compound(lo)).mean():.0%}")
    print(f"  Do lech chuan moi cum:  cao {hi.std(ddof=1):.2%}"
          f"  vs  thap {lo.std(ddof=1):.2%}"
          f"  -> tieu chi bien dong {'CO' if hi.std(ddof=1) > lo.std(ddof=1) else 'KHONG'} tang duoc phuong sai")

    print("\n" + "=" * 88)
    print(f"P(VE NHAT) — block bootstrap {CYCLES} vong tu alpha cap danh muc")
    print("=" * 88)
    cands = [(lb, a) for lb, a, _ in scenarios if lb.startswith("Thoat C")] + \
            [("Thoat A + EW toan bo (dang dung)",
              next(a for lb, a, _ in scenarios if lb == "Thoat A + EW toan bo ung vien"))]
    hdr = "".join(f"{s:>10.0%}" for s in (0.05, 0.08, 0.10, 0.12))
    print(f"{'Chien luoc':<40}{'Alpha TB':>10}{'sd':>8}   sigma nhom:{hdr}")
    print("-" * 88)
    for lb, a in cands:
        tot, _ = p_win(a, 0.10)
        ps = "".join(f"{p_win(a, s)[1]:>10.1%}" for s in (0.05, 0.08, 0.10, 0.12))
        print(f"{lb:<40}{tot.mean():>10.2%}{tot.std():>8.2%}{'':>12}{ps}")
    print("-" * 88)
    print("  Muc nen neu 8 nguoi ngang tai = 12.5%")
    print(f"\n  CANH BAO: bootstrap chi rut tu {len(scenarios[0][1])} cum quan sat duoc."
          f" Khoang tin cay thuc rong hon nhieu so ve day.")
