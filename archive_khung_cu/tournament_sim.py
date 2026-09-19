"""
tournament_sim.py — P(ve nhat) trong cuoc thi 2 thang, 8 nguoi, cham theo return.

Khac ban dau: KHONG dung mo hinh nhi phan (p, b) voi tham so bia ra nua.
Thay bang BLOCK BOOTSTRAP tren 40 alpha THUC DO duoc tu backtest.

Vi sao block bootstrap: lay mau theo NGAY KHUYEN NGHI, tuc lay ca cum lenh cung
mo trong mot phien. Cau truc phu thuoc duoc giu nguyen vi ta TAI SU DUNG no chu
khong uoc luong no — khong can copula, khong can ma tran hiep phuong sai.

So sanh tren co so ALPHA (vuot VNINDEX). Ly do: ca 8 thi sinh cung an mot beta
thi truong, nen thu hang chi phu thuoc phan vuot chi so.
"""

import numpy as np
from collections import defaultdict

from exit_rules import (load, evaluate, legs_A, legs_trail, legs_half, Leg)

RNG     = np.random.default_rng(2026)
N_SIM   = 100_000
CYCLES  = 8                                      # ~40 phien / ~5 phien moi vong
WEIGHTS = np.array([0.40, 0.30, 0.17, 0.13])     # Ty trong softmax da ap tran


def cohorts(trades, alphas):
    """Gom alpha theo ngay vao lenh -> giu tuong quan cheo trong cung phien."""
    g = defaultdict(list)
    for t, a in zip(trades, alphas):
        g[t["entry_i"]].append(a)
    return [np.array(v) for v in g.values() if len(v) >= 2]


def bootstrap(blocks, label):
    """8 vong; moi vong rut mot cum ngay roi rut 4 lenh trong cum do."""
    n_pos = len(WEIGHTS)
    pick_block = RNG.integers(0, len(blocks), size=(N_SIM, CYCLES))
    cycle = np.empty((N_SIM, CYCLES))
    for bi, blk in enumerate(blocks):
        m = pick_block == bi
        if not m.any():
            continue
        draws = RNG.integers(0, len(blk), size=(m.sum(), n_pos))
        cycle[m] = (blk[draws] * WEIGHTS).sum(axis=1)

    total = np.prod(1 + cycle, axis=1) - 1
    sd = total.std()
    skew = float(((total - total.mean()) ** 3).mean() / sd ** 3)
    print(f"{label:<34}{total.mean():>9.2%}{sd:>8.2%}{skew:>8.2f}"
          f"{np.percentile(total,5):>9.2%}{np.percentile(total,95):>9.2%}"
          f"{np.percentile(total,99):>9.2%}")
    return total


def p_win(mine, field_sigma, n_rivals=7):
    """Doi thu co alpha 2 thang ~ N(0, field_sigma). Beta triet tieu hai ben."""
    rivals = RNG.normal(0.0, field_sigma, size=(len(mine), n_rivals))
    return float((mine > rivals.max(axis=1)).mean())


if __name__ == "__main__":
    dates, prices, trades = load()
    n = len(dates)
    vni = prices["VNINDEX"]["Đóng"]

    rules = {
        "A. Chot tai Muc tieu 1 (hien tai)": lambda t: legs_A(t, prices, n),
        "C. Trailing stop 3%":               lambda t: legs_trail(t, prices, n, 0.03),
        "D. Nua T1 + nua trail 3%":          lambda t: legs_half(t, prices, n, 0.03),
    }

    print("=" * 92)
    print(f"MO PHONG {CYCLES} vong x {len(WEIGHTS)} vi the, block bootstrap tu "
          f"{len(trades)} alpha thuc do, {N_SIM:,} lan chay")
    print("=" * 92)
    print(f"{'Luat thoat':<34}{'Alpha TB':>9}{'Do lech':>8}{'Skew':>8}"
          f"{'PV 5%':>9}{'PV 95%':>9}{'PV 99%':>9}")
    print("-" * 92)

    sims = {}
    for label, fn in rules.items():
        alphas = [evaluate(t, fn(t), vni)[2] for t in trades]
        sims[label] = bootstrap(cohorts(trades, alphas), label)

    # Kich ban gia dinh: van chua co du lieu de kiem chung
    hypo = None
    print("\n" + "=" * 92)
    print("XAC SUAT VE NHAT (7 doi thu, alpha ~ N(0, sigma_nhom))")
    print("=" * 92)
    hdr = "".join(f"{k.split('.')[0]:>14}" for k in sims)
    print(f"{'sigma nhom (alpha 2 thang)':<30}{hdr}")
    print("-" * 92)
    for fs in (0.03, 0.05, 0.08, 0.10, 0.12):
        row = "".join(f"{p_win(v, fs):>14.1%}" for v in sims.values())
        print(f"  {fs:>4.0%}{'':<24}{row}")
    print("-" * 92)
    print("  Muc nen neu 8 nguoi ngang tai = 12.5%")

    best = max(sims.values(), key=lambda v: v.mean())
    print(f"\nNguong can vuot de ve nhat (ky vong cua max 7 doi thu):")
    for fs in (0.05, 0.08, 0.10, 0.12):
        bar = fs * 1.35
        print(f"  sigma nhom {fs:>4.0%}  ->  can alpha ~{bar:>5.1%}"
              f"   |  P(luat tot nhat vuot) = {(best > bar).mean():>5.1%}")
