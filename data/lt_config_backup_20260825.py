"""
lt_config.py — Tham so CHIEN LUOC DAI HAN (long-term), dung chung cho ca 2 danh muc.

Thay the hoan toan khung "P(ve nhat)" cu:
  - Ham muc tieu cu: P(ve nhat) trong cuoc thi 2 thang -> khuyen khich tap trung,
    bo qua rui ro, chon ma bien dong cao. DA BO.
  - Ham muc tieu moi: toi da hoa E[log NAV] dai han (toc do gop von), tuc la
    uu tien (a) chon ma manh hon thi truong ben vung, (b) khong de mot ma lam
    hong danh muc, (c) chi phi giao dich thap vi vong quay cham.

Ba tru cot:
  1. LOC (hard filter)   — chi choi trong xu huong tang dai han + du thanh khoan.
  2. XEP HANG (RS score) — suc manh tuong doi so voi VNINDEX, nhieu khung thoi gian.
  3. PHAN BO (risk parity) — ty trong ~ 1/bien dong, co tran ma va tran nganh.

Chay: PYTHONIOENCODING=utf-8 python lt_screener.py
"""

# ----------------------------------------------------------------- Danh muc
PORTFOLIOS = {
    "DM1": {
        "ten": "Danh muc 1 — tien that",
        "von_ban_dau": 200_000_000,
        "so_vi_the": 10,          # DO DUOC: 10 o cho CAGR 13,9% / sut giam -21,3%
        "tran_ma": 0.15,          # 15% NAV toi da 1 ma
        "tran_nganh": 0.30,       # 30% NAV toi da 1 nganh
        "ticket_toi_thieu": 8_000_000,
    },
    "DM2": {
        "ten": "Danh muc 2 — tai khoan du thi",
        "von_ban_dau": 60_000_000,
        "so_vi_the": 8,           # DO DUOC: 8 o (13,1%) tot hon 5-6 o (8,6-10,5%)
        "tran_ma": 0.20,
        "tran_nganh": 0.40,
        "ticket_toi_thieu": 5_000_000,
    },
}
# Do nhay so o (backtest 2022-04 -> 2026-08, 52 thang, xem lt_backtest_tradingview.js):
#   5 o  8,6% | 6 o 10,5% | 8 o 13,1% | 10 o 13,9% | 12 o 9,4% | 15 o 8,6%  (CAGR)
# Qua it o -> phu thuoc may rui; qua nhieu o -> pha loang. Vung 8-10 la tot nhat.

# ------------------------------------------------------- Vi the dang nam giu
# (ma, khoi luong, gia von VND). Cap nhat khi mua/ban.
HOLDINGS = {
    "DM1": [("PVT", 1000, 19_900), ("TCB", 500, 31_300)],
    # DM2 cap nhat sau phien 19/08/2026: da BAN 200 VNM @62.000 va 100 BAF @31.500
    # (ca hai khong dat chuan khung dai han). Con 6 ma. O VPI van CHUA mua.
    "DM2": [("MSB", 700, 16_000), ("BSR", 200, 27_000), ("GMD", 100, 78_800),
            ("LPB", 100, 50_800), ("STB", 100, 74_200), ("VHM", 100, 69_000)],
}
TIEN_MAT = {"DM1": 164_396_675, "DM2": 15_826_732}   # DM2: 315.607 + 15.511.125 tien ban VNM/BAF

# Tran trung lap giua 2 tai khoan: mot ma khong qua X% TONG tai san 2 danh muc.
TRAN_TRUNG_LAP = 0.10

# ------------------------------------------------------------- Bo loc cung
LOC = {
    "thanh_khoan_min": 10e9,   # Gia tri khop lenh TB 20 phien >= 10 ty/phien
    "gia_tren_ma200": True,    # Close > MA200
    "ma50_tren_ma200": True,   # MA50 > MA200 (cau truc tang dai han)
    "rs_252_duong": True,      # Phai vuot VNINDEX 12 thang qua
    # ATR chi la CHAN AN TOAN (loai ma qua dau co), khong phai tieu chi chon.
    # Bien dong duoc xu ly o khau PHAN BO (ty trong ~ 1/ATR), khong o khau loc —
    # neu loc bang ATR ta se vut bo nhung ma manh nhat chi vi chung dong manh.
    "atr_max": 0.060,
}

# ------------------------------------------------ Checklist mua/ban theo triet ly
# Day la bang cam ket chuyen tu ly thuyet sang kiem chung thuc te. Chung dung
# cho duyet quet hang ngay/ hang thang va phu hop voi "Peter Lynch + ky thuat".
BUY_CHECKLIST = {
    "liquidity": 10e9,
    "close_above_ma200": True,
    "ma50_above_ma200": True,
    "rs_12m_positive": True,
    "trend_quality_r2_min": 0.20,
    "atr_max": 0.060,
    "min_relative_strength_6m": 0.00,
}

# Thang diem 10 cho danh gia nhanh: 70+ thi duoc coi la "dat mua".
INVESTMENT_SCORE = {
    "threshold": 7.0,
    "weights": {
        "quality": 3.0,
        "valuation": 2.0,
        "trend": 2.0,
        "relative_strength": 2.0,
        "risk": 1.0,
    },
}

SELL_CHECKLIST = {
    "close_below_97pct_ma200": True,
    "rs_12m_below_minus_5pct": True,
    "rank_below_40pct": True,
    "stop_loss_25pct": True,
}

# --------------------------------------------------------- Diem suc manh RS
# Trong so cho tung khung. Bo qua 21 phien gan nhat trong khung 12 thang
# (skip-month) vi dao chieu ngan han lam nhieu tin hieu momentum.
RS_WEIGHTS = {"rs_252_skip21": 0.40, "rs_126": 0.30, "rs_63": 0.20, "trend_r2": 0.10}

# ------------------------------------------------------------- Luat thoat
# Thay cho trailing 3% / toi da 20 phien cua khung cuoc thi.
# Ba dieu kien duoi day DA DUOC BACKTEST nguyen ven (52 thang): ra soat HANG
# THANG nhung chi BAN khi luat kich hoat. Ra soat hang quy thay vi hang thang
# lam CAGR tut 13,9% -> 7,1%: toc do THOAT moi la thu quan trong, khong phai
# toc do vao.
EXIT = {
    "chu_ky_ra_soat": "thang",   # Ra soat dau moi thang. KHONG theo doi theo phien.
    "giu_khi": {                 # Con du CA BA thi giu tiep, khong dong vao
        "gia_tren": "0,97 x MA200",       # dem 3% duoi MA200, tranh bi quet nhieu
        "rs_12t_toi_thieu": -0.05,        # duoc phep thua VNINDEX toi 5% moi bi ban
        "thu_hang_rs": 0.40,              # con trong top 40% bang xep hang
    },
    "khong_co_muc_tieu_chot_lai": True,   # Giu nguyen bai hoc cua luat C
    "bien_khong_giao_dich": 0.03,         # lech ty trong < 3% NAV thi khong dieu chinh
    "stop_tham_hoa": 0.25,                # Chan cung mot chieu: -25% so voi gia von
}
# Do nhay nguong "thu_hang_rs" (CAGR, khong co bien khong giao dich):
#   0,25 -> 11,9% | 0,33 -> 12,6% | 0,40 -> 15,4% | 0,50 -> 10,3% | 0,60 -> 8,1%
# 0,40 la DINH cua be mat nen phai coi la may; dieu dang tin la CA HO 0,25-0,60
# deu thang VNINDEX (7,5%). Dung 0,40 nhung khong duoc coi con so nay la thieng.

# --------------------------------------------------------------- Chi phi
FEE_BUY = 0.0015
FEE_SELL = 0.0015 + 0.0010     # phi ban + thue TNCN 0,1%
LOT = 100

# --------------------------------------------------------------- Nganh
# Phan nganh tho de ap tran nganh (khong can chuan ICB, chi can chan tap trung).
NGANH = {
    "ACB": "Ngan hang", "BID": "Ngan hang", "CTG": "Ngan hang", "EIB": "Ngan hang",
    "HDB": "Ngan hang", "LPB": "Ngan hang", "MBB": "Ngan hang", "MSB": "Ngan hang",
    "NAB": "Ngan hang", "OCB": "Ngan hang", "SHB": "Ngan hang", "SSB": "Ngan hang",
    "STB": "Ngan hang", "TCB": "Ngan hang", "TPB": "Ngan hang", "VCB": "Ngan hang",
    "VIB": "Ngan hang", "VPB": "Ngan hang", "EVF": "Ngan hang",
    "BSI": "Chung khoan", "FTS": "Chung khoan", "HCM": "Chung khoan",
    "SSI": "Chung khoan", "VCI": "Chung khoan", "VIX": "Chung khoan",
    "VND": "Chung khoan", "DSE": "Chung khoan",
    "BVH": "Bao hiem",
    "BCM": "Bat dong san", "DIG": "Bat dong san", "DXG": "Bat dong san",
    "HDC": "Bat dong san", "HDG": "Bat dong san", "KBC": "Bat dong san",
    "KDH": "Bat dong san", "KOS": "Bat dong san", "NLG": "Bat dong san",
    "NTL": "Bat dong san", "NVL": "Bat dong san", "PDR": "Bat dong san",
    "SIP": "Bat dong san", "SJS": "Bat dong san", "SZC": "Bat dong san",
    "VHM": "Bat dong san", "VIC": "Bat dong san", "VRE": "Bat dong san",
    "CII": "Ha tang", "CTD": "Ha tang", "CTR": "Ha tang", "HHV": "Ha tang",
    "PC1": "Ha tang", "VCG": "Ha tang", "GEE": "Ha tang", "GEX": "Ha tang",
    "HPG": "Thep", "HSG": "Thep", "NKG": "Thep",
    "BSR": "Dau khi", "GAS": "Dau khi", "PLX": "Dau khi", "PVD": "Dau khi",
    "PVT": "Dau khi", "PVS": "Dau khi", "DCM": "Hoa chat", "DGC": "Hoa chat",
    "DPM": "Hoa chat", "CSV": "Hoa chat", "PHR": "Cao su", "GVR": "Cao su",
    "NT2": "Dien", "POW": "Dien", "PPC": "Dien", "REE": "Dien", "BWE": "Nuoc",
    "GMD": "Cang bien", "HAH": "Cang bien", "VSC": "Cang bien", "TMS": "Cang bien",
    "SCS": "Hang khong", "HVN": "Hang khong", "VJC": "Hang khong", "VTP": "Chuyen phat",
    "MWG": "Ban le", "FRT": "Ban le", "DGW": "Ban le", "PNJ": "Ban le",
    "MSN": "Tieu dung", "SAB": "Tieu dung", "VNM": "Tieu dung", "PAN": "Tieu dung",
    "KDC": "Tieu dung", "SBT": "Tieu dung", "TLG": "Tieu dung", "MSH": "Det may",
    "GIL": "Det may", "BAF": "Chan nuoi", "DBC": "Chan nuoi", "HAG": "Nong nghiep",
    "ANV": "Thuy san", "VHC": "Thuy san", "ASM": "Thuy san", "LSS": "Nong nghiep",
    "FPT": "Cong nghe", "CMG": "Cong nghe", "ELC": "Cong nghe",
    "IMP": "Duoc", "DHC": "Giay", "HT1": "Xi mang", "BMP": "Vat lieu",
    "PTB": "Vat lieu", "VGC": "Vat lieu", "TCH": "Bat dong san", "VPI": "Bat dong san",
}
