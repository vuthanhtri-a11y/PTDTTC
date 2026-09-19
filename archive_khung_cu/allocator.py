"""
allocator.py — Phan bo danh muc theo softmax(ER) cho cuoc thi dau tu 2 thang.

Thiet ke:
    ER_i = p_i * b_i - (1 - p_i)          # Risk chuan hoa = 1, b = Reward/Risk
    Loc ER <= 0                            # Khong duoc ban khong -> loai thang
    w_i  = softmax(ER_i / TAU)             # TAU = 0.3 (chot cho cuoc thi 2 thang)
    + tran 40%/ma, toi da 5 ma, ticket toi thieu 25tr

Hai che do quy ra tien:
    "capital" (mac dinh, cho cuoc thi): w LA ty trong von, giai ngan gan 100%.
    "risk"    (cho tien that): w la ty trong NGAN SACH RUI RO, chia cho stop distance.

Chay:  python allocator.py
"""

import numpy as np

# ---------------------------------------------------------------- Tham so
NAV          = 230_000_000    # Tong tai san
CASH         = 194_000_000    # Tien mat kha dung
TAU_MODE     = "scaled"       # "absolute": TAU co dinh | "scaled": TAU = K_TAU * std(ER)
TAU          = 0.30           # Dung khi TAU_MODE = "absolute"
K_TAU        = 2.1            # Dung khi TAU_MODE = "scaled" (bat bien voi thang do ER)
MAX_WEIGHT   = 0.40           # Tran ty trong 1 ma
MAX_POSITIONS = 5             # So vi the toi da
MIN_TICKET   = 25_000_000     # Ticket toi thieu (duoi muc nay phi an het)
LOT          = 100            # Lo giao dich HOSE
INVEST_RATIO = 0.98           # Chua 2% dem cho phi + lam tron lo
RISK_BUDGET  = 0.05           # Chi dung o che do "risk"

FEE_BUY  = 0.0015             # Phi mua
FEE_SELL = 0.0015 + 0.0010    # Phi ban + thue TNCN 0.1%


class Candidate:
    """Mot ung vien. price_k = gia theo NGHIN dong (nhu bang gia HOSE)."""

    def __init__(self, ticker, price_k, p, reward_R, stop_pct, sector, held=0):
        self.ticker   = ticker
        self.price    = price_k * 1000
        self.p        = p
        self.b        = reward_R
        self.stop_pct = stop_pct
        self.sector   = sector
        self.held     = held          # So co phieu dang nam giu

    @property
    def ER(self):
        return self.p * self.b - (1 - self.p)

    @property
    def breakeven_p(self):
        """p toi thieu de ER > 0."""
        return 1.0 / (1.0 + self.b)


def effective_tau(ers):
    """TAU thuc te. Che do 'scaled' neo vao do phan tan cua ER nen muc do
    tap trung khong doi khi thang do cua ER thay doi (vi du khi doi cach tinh p)."""
    if TAU_MODE == "absolute":
        return TAU
    sigma = float(np.std(ers))
    return max(K_TAU * sigma, 1e-6)


def softmax(x, tau):
    z = np.asarray(x, dtype=float) / tau
    z -= z.max()                       # On dinh so hoc
    e = np.exp(z)
    return e / e.sum()


def cap_weights(w, cap):
    """Ap tran ty trong, phan bo lai phan thua cho cac ma chua cham tran."""
    w = np.array(w, dtype=float)
    if cap * len(w) < 1.0:             # Tran qua chat, khong the thoa man
        return np.full(len(w), 1.0 / len(w))
    for _ in range(100):
        over = w > cap + 1e-12
        if not over.any():
            break
        excess    = (w[over] - cap).sum()
        w[over]   = cap
        room      = ~over
        if not room.any():
            break
        w[room] += excess * w[room] / w[room].sum()
    return w


def allocate(candidates, mode="capital"):
    """Tra ve list (candidate, weight, money) sau khi ap moi rang buoc."""
    live = [c for c in candidates if c.ER > 1e-9]
    if not live:
        return []

    live.sort(key=lambda c: c.ER, reverse=True)
    live = live[:MAX_POSITIONS]

    investable = min(CASH + sum(c.held * c.price for c in candidates),
                     NAV) * INVEST_RATIO

    while live:
        ers = [c.ER for c in live]
        w = cap_weights(softmax(ers, effective_tau(ers)), MAX_WEIGHT)

        if mode == "capital":
            money = w * investable
        else:                                    # mode == "risk"
            risk_vnd = NAV * RISK_BUDGET * w
            money    = risk_vnd / np.array([c.stop_pct for c in live])
            if money.sum() > investable:         # Khong vuot von kha dung
                money *= investable / money.sum()

        if money.min() >= MIN_TICKET or len(live) == 1:
            return list(zip(live, w, money))
        live.pop()                               # Bo ma nho nhat, chia lai

    return []


def report(alloc, mode):
    if not alloc:
        print("Khong co ma nao co ER > 0 — dung ngoai thi truong.")
        return

    tau_eff = effective_tau([c.ER for c, _, _ in alloc])
    print(f"\n{'='*74}")
    print(f"PHAN BO DANH MUC  |  tau={tau_eff:.3f} ({TAU_MODE})  |  che do = {mode}"
          f"  |  NAV = {NAV/1e6:,.0f} tr")
    print("=" * 74)
    print(f"{'Ma':<6}{'p':>6}{'b':>5}{'ER':>7}{'w':>8}{'Gia':>9}"
          f"{'CP':>8}{'Von(tr)':>10}{'Rui ro':>9}")
    print("-" * 74)

    total_money = total_risk = 0.0
    by_sector = {}

    for c, w, money in alloc:
        shares = int(money / c.price // LOT * LOT)
        actual = shares * c.price
        risk   = actual * c.stop_pct
        total_money += actual
        total_risk  += risk
        by_sector[c.sector] = by_sector.get(c.sector, 0.0) + actual

        print(f"{c.ticker:<6}{c.p:>6.2f}{c.b:>5.1f}{c.ER:>7.2f}{w:>7.1%}"
              f"{c.price/1000:>9.2f}{shares:>8,}{actual/1e6:>10.1f}"
              f"{risk/NAV:>8.2%}")

    print("-" * 74)
    print(f"{'TONG':<6}{'':>18}{total_money/NAV:>7.1%}{'':>17}"
          f"{total_money/1e6:>10.1f}{total_risk/NAV:>8.2%}")
    print(f"{'Tien mat':<24}{1-total_money/NAV:>7.1%}{'':>17}"
          f"{(NAV-total_money)/1e6:>10.1f}")

    print(f"\nTap trung nganh:")
    for s, v in sorted(by_sector.items(), key=lambda kv: -kv[1]):
        flag = "  <-- vuot 35%" if v / NAV > 0.35 else ""
        print(f"  {s:<22}{v/NAV:>7.1%}{flag}")

    print(f"\nNeu MOI vi the deu dinh stop: NAV -{total_risk/NAV:.2%}"
          f"  ({total_risk/1e6:.1f} tr)")

    # Lenh can dat de di tu danh muc hien tai sang danh muc muc tieu
    print(f"\n{'Lenh can dat':<74}")
    print("-" * 74)
    target = {c.ticker: int(m / c.price // LOT * LOT) for c, _, m in alloc}
    for c, _, m in alloc:
        diff = target[c.ticker] - c.held
        if diff:
            side = "MUA " if diff > 0 else "BAN "
            cost = abs(diff) * c.price * (FEE_BUY if diff > 0 else FEE_SELL)
            print(f"  {side}{abs(diff):>6,} {c.ticker:<6}"
                  f"@ {c.price/1000:>6.2f}   "
                  f"= {abs(diff)*c.price/1e6:>7.1f} tr"
                  f"   (phi {cost/1e3:>5.0f}k)")


if __name__ == "__main__":
    # ------------------------------------------------------------------
    # b = 0.82 la so DO DUOC tu exit_rules.py (luat trailing stop 3% tren
    # 35 lenh backtest). b la thuoc tinh cua LUAT THOAT, gan nhu khong doi
    # giua cac ma — nen dat chung mot gia tri.
    #   Suy ra: ER_i = p_i*(b+1) - 1  ->  softmax chi con phu thuoc p_i.
    #   Diem hoa von: p > 1/(1+b) = 54.9%. Duoi muc nay la loai.
    # p duoi day VAN LA SO GIA DINH — phai thay bang p(W) that truoc khi dat lenh.
    # ------------------------------------------------------------------
    B_RULE = 0.82
    candidates = [
        # ticker  gia    p     b     stop  nganh              dang giu
        Candidate("PVT",  19.90, 0.70, B_RULE, 0.06, "Dau khi/Van tai", held=1000),
        Candidate("TCB",  31.30, 0.66, B_RULE, 0.05, "Ngan hang",       held=500),
        Candidate("HPG",  27.50, 0.72, B_RULE, 0.07, "Thep"),
        Candidate("FPT",  92.00, 0.68, B_RULE, 0.06, "Cong nghe"),
        Candidate("VCB",  61.00, 0.62, B_RULE, 0.05, "Ngan hang"),
        Candidate("SSI",  28.40, 0.56, B_RULE, 0.08, "Chung khoan"),
        Candidate("GAS",  68.00, 0.52, B_RULE, 0.06, "Dau khi/Van tai"),
    ]

    print("\nSANG LOC ER")
    print("-" * 74)
    print(f"{'Ma':<6}{'p':>6}{'b':>5}{'p hoa von':>12}{'ER':>8}   Ket qua")
    print("-" * 74)
    for c in sorted(candidates, key=lambda c: -c.ER):
        verdict = "vao" if c.ER > 1e-9 else "LOAI (ER <= 0)"
        print(f"{c.ticker:<6}{c.p:>6.2f}{c.b:>5.1f}{c.breakeven_p:>12.2f}"
              f"{c.ER:>8.2f}   {verdict}")

    report(allocate(candidates, mode="capital"), "capital (cuoc thi)")
    report(allocate(candidates, mode="risk"), "risk (tien that)")
