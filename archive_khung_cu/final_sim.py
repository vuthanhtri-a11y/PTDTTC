"""
final_sim.py — P(ve nhat) voi tham so DO DUOC tu 56.496 lenh mo phong 2018-2026.

Khac moi ban truoc: p, W, L khong con la so gia dinh. Chung do tu mo phong
8 nam tren 30 ma, tach theo che do thi truong, tinh tren ALPHA (vuot VNINDEX).

Uoc luong ky nang CHON DIEM VAO:
  35 lenh that cua user, luat thoat A, cua so tang gia  -> alpha +0,28%/lenh
  Vao lenh NGAU NHIEN,   luat thoat A, che do TANG      -> alpha -0,235%/lenh
  => ky nang chon diem vao dong gop ~ +0,52%/lenh.
Con so nay do tren 35 lenh nen rat nhieu — mo phong ca hai kich ban co/khong.
"""

import numpy as np
from scipy.stats import norm

RNG    = np.random.default_rng(2026)
N_SIM  = 200_000
CYCLES = 8                                     # ~40 phien / ~5 phien moi vong
W4     = np.array([0.25, 0.25, 0.25, 0.25])    # Can bang deu 4 vi the
RHO    = 0.50                                  # Tuong quan noi danh muc
P_UP   = 35172 / 56496                         # Ty le phien o che do TANG (62,3%)
ENTRY_SKILL = 0.0052                           # +0,52%/lenh, cong vao moi lenh

# Tham so ALPHA do duoc: (p, W, L)
PAR = {
    ("A", "UP"):   (0.575, 0.0245, 0.0386),
    ("A", "DOWN"): (0.518, 0.0247, 0.0410),
    ("C", "UP"):   (0.410, 0.0570, 0.0331),
    ("C", "DOWN"): (0.410, 0.0565, 0.0389),
}


def simulate(rule, skill=0.0):
    """Mo phong CYCLES vong; moi vong rut che do thi truong roi rut 4 ket qua
    tuong quan qua copula Gaussian mot yeu to."""
    n = len(W4)
    up = RNG.random((N_SIM, CYCLES)) < P_UP
    zm = RNG.standard_normal((N_SIM, CYCLES, 1))
    eps = RNG.standard_normal((N_SIM, CYCLES, n))
    z = np.sqrt(RHO) * zm + np.sqrt(1 - RHO) * eps

    ret = np.empty_like(z)
    for regime, mask in (("UP", up), ("DOWN", ~up)):
        p, W, L = PAR[(rule, regime)]
        r = np.where(z > norm.ppf(1 - p), W, -L) + skill
        ret[mask] = r[mask]

    cycle = ret @ W4
    return np.prod(1 + cycle, axis=1) - 1


def p_win(total, field_sigma, n_rivals=7):
    rivals = RNG.normal(0.0, field_sigma, size=(len(total), n_rivals))
    return float((total > rivals.max(axis=1)).mean())


if __name__ == "__main__":
    print("=" * 96)
    print(f"P(VE NHAT) — 8 nguoi, {CYCLES} vong x 4 vi the, tuong quan {RHO}, "
          f"{N_SIM:,} lan chay")
    print(f"Tham so do tu 56.496 lenh mo phong 2018-2026 ({P_UP:.0%} phien che do TANG)")
    print("=" * 96)

    rows = [
        ("A. Chot tai Muc tieu 1  (vao lenh ngau nhien)", "A", 0.0),
        ("A. Chot tai Muc tieu 1  + ky nang chon diem vao", "A", ENTRY_SKILL),
        ("C. Trailing stop 3%     (vao lenh ngau nhien)", "C", 0.0),
        ("C. Trailing stop 3%     + ky nang chon diem vao", "C", ENTRY_SKILL),
    ]

    sims = {}
    print(f"{'Chien luoc':<48}{'Alpha TB':>10}{'Do lech':>9}{'Skew':>7}"
          f"{'PV 95%':>9}{'PV 99%':>9}")
    print("-" * 96)
    for label, rule, skill in rows:
        t = simulate(rule, skill)
        sims[label] = t
        skew = float(((t - t.mean()) ** 3).mean() / t.std() ** 3)
        print(f"{label:<48}{t.mean():>+10.2%}{t.std():>9.2%}{skew:>+7.2f}"
              f"{np.percentile(t,95):>+9.2%}{np.percentile(t,99):>+9.2%}")

    print("\n" + "=" * 96)
    print("XAC SUAT VE NHAT theo do bien dong cua nhom thi")
    print("=" * 96)
    sig = (0.05, 0.08, 0.10, 0.12, 0.15)
    print(f"{'Chien luoc':<48}" + "".join(f"{s:>9.0%}" for s in sig))
    print("-" * 96)
    for label, t in sims.items():
        print(f"{label:<48}" + "".join(f"{p_win(t, s):>9.1%}" for s in sig))
    print("-" * 96)
    print("  Muc nen neu 8 nguoi ngang tai = 12.5%")

    a = sims["A. Chot tai Muc tieu 1  + ky nang chon diem vao"]
    c = sims["C. Trailing stop 3%     + ky nang chon diem vao"]
    print(f"\nDoi luat thoat A -> C (giu nguyen ky nang chon diem vao):")
    for s in sig:
        pa, pc = p_win(a, s), p_win(c, s)
        print(f"  sigma nhom {s:>4.0%}:  {pa:>5.1%}  ->  {pc:>5.1%}"
              f"   (x{pc/pa:.1f})")
