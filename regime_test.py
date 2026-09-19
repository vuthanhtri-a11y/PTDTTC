"""
regime_test.py — Kiem dinh luat thoat tren 56.496 lenh mo phong, 8 nam, 30 ma.

Nguon: mo phong chay trong trinh duyet TradingView (2018-2026). Vao lenh tai gia
mo cua MOI phien (khong loc setup) nen day la phep do THUAN TUY ve luat thoat,
khong lan voi chat luong diem vao.

  Luat A: chot tai +3% / cat lo -4%   (mo phong "thoat toan bo khi cham Muc tieu 1")
  Luat C: trailing stop 3% tu dinh gia dong cua
  Ca hai: T+2, toi da 20 phien, phi mua 0,15% ban 0,25%.

Che do thi truong xac dinh TAI THOI DIEM VAO LENH: VNINDEX tren/duoi MA50.

Suy dien: cac lenh chong lan nhau rat nhieu (vao moi phien, giu ~9 phien) nen sai
so chuan tho se thoi phong y nghia. Dung bootstrap GOP CUM THEO MA — lay mau lai
30 ma, moi ma dong gop trung binh cua rieng no.
"""

import numpy as np

RNG = np.random.default_rng(23)

# [ma, n_UP, n_DOWN, alphaA_UP, alphaC_UP, alphaA_DOWN, alphaC_DOWN]  (don vi %)
DATA = [
    ["BAF",710,438,-0.054,0.422,0.073,2.321],   ["BID",1257,773,-0.058,0.016,-0.507,0.215],
    ["BSR",1257,765,-0.221,0.902,-1.518,-0.792],["BVH",1257,773,-0.693,-0.863,-0.475,0.077],
    ["CTD",1257,773,-0.61,-0.545,-1.215,0.43],  ["CTG",1257,773,0.074,-0.12,-0.479,-0.086],
    ["CTR",1250,773,-0.198,2.601,-0.704,0.939], ["DGC",1255,769,-0.003,1.296,-0.8,1.489],
    ["DGW",1257,773,-0.13,0.738,-0.912,0.03],   ["FPT",1257,773,0.174,0.287,-0.144,0.048],
    ["GAS",1257,773,-0.528,-0.515,-1.072,-0.909],["GMD",1257,773,-0.43,-0.423,-0.146,0.408],
    ["HCM",1257,773,-0.044,0.483,-0.899,-0.465],["HDB",1257,773,-0.214,0.467,-0.262,-0.123],
    ["HPG",1257,773,0.059,0.862,-1.007,-0.93],  ["HVN",1156,643,-0.762,-0.231,-1.123,-0.079],
    ["KDC",1257,773,-0.461,0.103,-0.635,0.509], ["MSB",914,470,0.177,1.092,-0.488,-0.112],
    ["MWG",1257,773,0.208,0.59,-0.733,0.061],   ["NVL",1257,773,-0.488,0.241,-0.533,0.191],
    ["PET",1257,773,-0.167,1.517,-0.892,0.537], ["PHP",616,339,-0.237,0.066,-0.218,0.365],
    ["SSI",1257,773,-0.061,1.234,-1.063,-1.152],["STB",1257,773,0.236,1.17,-0.527,-0.305],
    ["VCB",1257,773,0.003,0.398,-0.405,-0.28],  ["VGI",1223,725,-0.492,0.915,-0.956,0.557],
    ["VHM",1257,773,-0.604,0.095,-0.888,0.043], ["VNM",1257,773,-1.146,-1.383,-1.027,-1.244],
    ["VPI",1257,752,0.265,0.077,0.103,-0.368],  ["VTP",394,190,-1.114,-0.48,-0.751,1.218],
]

# Tong hop tu mo phong (toan mau)
AGG = {
    "A_UP":   dict(n=35172, p=62.2, alpha=-0.235, net=-0.495, W=2.56, L=5.51, b=0.46, ER=-0.09, hold=6.1),
    "C_UP":   dict(n=35172, p=38.9, alpha=+0.386, net=+0.382, W=6.87, L=3.75, b=1.83, ER=+0.102, hold=9.3),
    "A_DOWN": dict(n=21324, p=60.8, alpha=-0.692, net=-0.861, W=2.56, L=6.15, b=0.42, ER=-0.14, hold=5.6),
    "C_DOWN": dict(n=21324, p=40.7, alpha=+0.018, net=+0.203, W=6.99, L=4.46, b=1.57, ER=+0.046, hold=9.1),
}


def cluster_boot(vals, weights, n_boot=50000):
    """Bootstrap gop cum theo ma: lay mau lai 30 ma, tinh trung binh co trong so."""
    v, w = np.asarray(vals, float), np.asarray(weights, float)
    idx = RNG.integers(0, len(v), size=(n_boot, len(v)))
    m = (v[idx] * w[idx]).sum(axis=1) / w[idx].sum(axis=1)
    point = (v * w).sum() / w.sum()
    return point, np.percentile(m, 2.5), np.percentile(m, 97.5)


if __name__ == "__main__":
    syms = [d[0] for d in DATA]
    nU = [d[1] for d in DATA]
    nD = [d[2] for d in DATA]
    aU, cU = [d[3] for d in DATA], [d[4] for d in DATA]
    aD, cD = [d[5] for d in DATA], [d[6] for d in DATA]

    print("=" * 84)
    print("LUAT THOAT TREN 56.496 LENH MO PHONG — 30 ma, 2018-2026, vao lenh MOI phien")
    print("=" * 84)
    print(f"{'':<26}{'n':>8}{'p':>7}{'W':>7}{'L':>7}{'b':>6}{'ER':>7}"
          f"{'Alpha':>9}{'Net':>8}{'Giu':>6}")
    print("-" * 84)
    for lbl, key in [("A. Chot +3%/cat -4%  [TANG]", "A_UP"),
                     ("C. Trailing 3%       [TANG]", "C_UP"),
                     ("A. Chot +3%/cat -4%  [GIAM]", "A_DOWN"),
                     ("C. Trailing 3%       [GIAM]", "C_DOWN")]:
        a = AGG[key]
        print(f"{lbl:<26}{a['n']:>8,}{a['p']:>6.1f}%{a['W']:>6.2f}%{a['L']:>6.2f}%"
              f"{a['b']:>6.2f}{a['ER']:>+7.2f}{a['alpha']:>+8.3f}%{a['net']:>+7.3f}%"
              f"{a['hold']:>6.1f}")

    print("\n" + "=" * 84)
    print("CHENH LECH C − A  (bootstrap gop cum theo ma, 30 cum, KTC 95%)")
    print("=" * 84)
    for name, a, c, w in [("Thi truong TANG (VNINDEX > MA50)", aU, cU, nU),
                          ("Thi truong GIAM (VNINDEX < MA50)", aD, cD, nD)]:
        d = [ci - ai for ai, ci in zip(a, c)]
        pt, lo, hi = cluster_boot(d, w)
        sig = "co y nghia" if lo > 0 or hi < 0 else "KHONG co y nghia"
        nwin = sum(1 for x in d if x > 0)
        print(f"  {name}")
        print(f"    C − A = {pt:>+6.3f}%/lenh   KTC [{lo:>+6.3f}%, {hi:>+6.3f}%]   {sig}")
        print(f"    C thang A o {nwin}/{len(d)} ma\n")

    print("=" * 84)
    print("KIEM DINH MOC: alpha cua tung luat co khac 0 khong?")
    print("=" * 84)
    for name, vals, w in [("A [TANG]", aU, nU), ("C [TANG]", cU, nU),
                          ("A [GIAM]", aD, nD), ("C [GIAM]", cD, nD)]:
        pt, lo, hi = cluster_boot(vals, w)
        v = "duong" if lo > 0 else ("am" if hi < 0 else "khong khac 0")
        print(f"  {name:<10}{pt:>+7.3f}%   KTC [{lo:>+6.3f}%, {hi:>+6.3f}%]   -> {v}")
