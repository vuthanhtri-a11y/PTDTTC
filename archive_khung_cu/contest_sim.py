"""
contest_sim.py — P(ve nhat) cho DANH MUC 2 (60 trieu, thi 2 thang, bat dau 17/08/2026).

Mo rong final_sim.py theo hai truc ma bai toan thuc te bat phai tra loi:
  1. SO VI THE 4 hay 5 (user muon 5 ma; final_sim.py chi chay 4).
  2. CHE DO THI TRUONG. final_sim.py dung P_UP = 62,3% (tan suat lich su 2018-2026).
     Do luc 14/08/2026: VNINDEX 1729,08 < MA50 1792,85 -> dang o che do GIAM.
     Nen chay them kich ban P_UP = 0,35 (thi truong yeu suot cuoc thi).

Tham so p/W/L giu nguyen tu 56.496 lenh mo phong — xem regime_test.py.
Chay: PYTHONIOENCODING=utf-8 python contest_sim.py
"""

import numpy as np
from scipy.stats import norm

RNG = np.random.default_rng(2026)
N_SIM = 200_000
CYCLES = 8
RHO = 0.50
ENTRY_SKILL = 0.0052

PAR = {
    ("A", "UP"):   (0.575, 0.0245, 0.0386),
    ("A", "DOWN"): (0.518, 0.0247, 0.0410),
    ("C", "UP"):   (0.410, 0.0570, 0.0331),
    ("C", "DOWN"): (0.410, 0.0565, 0.0389),
}

SCENARIOS = {"Lich su (62% TANG)": 35172 / 56496, "Thi truong yeu (35% TANG)": 0.35}


def simulate(rule, n_pos, p_up, skill=ENTRY_SKILL):
    w = np.full(n_pos, 1.0 / n_pos)
    up = RNG.random((N_SIM, CYCLES)) < p_up
    zm = RNG.standard_normal((N_SIM, CYCLES, 1))
    eps = RNG.standard_normal((N_SIM, CYCLES, n_pos))
    z = np.sqrt(RHO) * zm + np.sqrt(1 - RHO) * eps

    ret = np.empty_like(z)
    for regime, mask in (("UP", up), ("DOWN", ~up)):
        p, W, L = PAR[(rule, regime)]
        r = np.where(z > norm.ppf(1 - p), W, -L) + skill
        ret[mask] = r[mask]

    return np.prod(1 + ret @ w, axis=1) - 1


def p_win(total, field_sigma, n_rivals=7):
    rivals = RNG.normal(0.0, field_sigma, size=(len(total), n_rivals))
    return float((total > rivals.max(axis=1)).mean())


if __name__ == "__main__":
    sig = (0.08, 0.10, 0.12)
    print("=" * 104)
    print("DANH MUC 2 — P(VE NHAT), 8 nguoi, 8 vong, tuong quan 0,50, 200.000 lan chay")
    print("=" * 104)
    hdr = f"{'Kich ban':<28}{'Luat':<6}{'N':>3}{'Alpha TB':>11}{'Do lech':>9}{'Skew':>7}{'PV 95%':>9}"
    hdr += "".join(f"{'P|sg=' + f'{s:.0%}':>10}" for s in sig)
    print(hdr)
    print("-" * 104)

    for sc_name, p_up in SCENARIOS.items():
        for rule in ("A", "C"):
            for n_pos in (4, 5):
                t = simulate(rule, n_pos, p_up)
                skew = float(((t - t.mean()) ** 3).mean() / t.std() ** 3)
                line = f"{sc_name:<28}{rule:<6}{n_pos:>3}{t.mean():>+11.2%}{t.std():>9.2%}"
                line += f"{skew:>+7.2f}{np.percentile(t, 95):>+9.2%}"
                line += "".join(f"{p_win(t, s):>10.1%}" for s in sig)
                print(line)
        print("-" * 104)

    print("  Muc nen neu 8 nguoi ngang tai = 12,5%")

    print("\n" + "=" * 104)
    print("QUY RA TIEN — NAV 60 trieu, alpha cong doi voi loi suat VNINDEX")
    print("=" * 104)
    for sc_name, p_up in SCENARIOS.items():
        for rule in ("A", "C"):
            t = simulate(rule, 5, p_up)
            print(f"{sc_name:<28}{'Luat ' + rule:<8}"
                  f"trung vi {60 * (1 + np.median(t)):>6.1f}tr   "
                  f"PV5 {60 * (1 + np.percentile(t, 5)):>6.1f}tr   "
                  f"PV95 {60 * (1 + np.percentile(t, 95)):>6.1f}tr")
