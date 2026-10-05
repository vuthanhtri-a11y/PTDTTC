"""
lt_scan_vietcap.py — Quet TOAN THI TRUONG (HOSE + HNX + UPCoM) tu API Vietcap.

Chot 01/10/2026 (CHIEN_LUOC_DAI_HAN.md muc 13, quyet dinh 6): nhanh MAY cua khung
top-down quet toan bo co phieu dang niem yet thay cho 112 ma HOSE. Thay the
lt_scan_tradingview.js lam nguon san xuat; file .js giu lai de doi chieu.

Vi sao khong mo rong file .js: 1.522 ma x 3-10 giay = 1,3-4,2 gio tren
TradingView Desktop, cong them bay "gan du lieu ma truoc cho ma sau" phai chan
bang signature. Vietcap tra ve moi ma mot request (~0,5 giay), gia DA DIEU
CHINH co tuc (hop ly hon cho MA/RS; lech ~1% voi gia tho TradingView o ma co co
tuc — do bang --den, xem duoi).

Dau ra: data/scan_YYYYMMDD.json, DUNG schema 15 truong cua lt_scan_tradingview.js
(xem FIELDS trong lt_screener.py) de screener doc khong phai sua. Them ba khoa
phu bat dau bang "_" (screener bo qua): _meta, _san, _icb.

Chay:
  PYTHONIOENCODING=utf-8 python lt_scan_vietcap.py              # toan thi truong
  PYTHONIOENCODING=utf-8 python lt_scan_vietcap.py --den 2026-09-21 --ma-tu data/scan_20260921.json
      # dung lai ban quet cua mot ngay cu tren dung ro ma cua file do -> doi
      # chieu voi ban TradingView (ghi ra data/scan_vietcap_doi_chieu_YYYYMMDD.json,
      # KHONG de len scan_*.json)
"""

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta

import requests

H = {"User-Agent": "Mozilla/5.0", "Referer": "https://trading.vietcap.com.vn/",
     "Origin": "https://trading.vietcap.com.vn/"}
PX_URL = "https://trading.vietcap.com.vn/api/chart/OHLCChart/gap-chart"
LIST_URL = "https://trading.vietcap.com.vn/api/price/symbols/getAll"
SAN = ("HSX", "HNX", "UPCOM")          # ma "DELISTED" bi bo: khong con giao dich

# --- Tham so PHAI KHOP lt_scan_tradingview.js (cung schema, cung cach tinh) ---
MA_LEN = 50
NEED_OBS = 500
NEED_BARS = NEED_OBS + MA_LEN + 10     # 560
VOL_WIN = 60
DS_KEEP = 30
COUNT_BACK = 620                        # du 560 bar + du tru ngay nghi

# Ma khong co phien khop nao trong ngan nay ngay (so voi VNINDEX) bi coi la
# DUNG GIAO DICH: khong ghi vao ban quet, liet ke o _meta.cu. Neu giu lai, r21..
# r252 cua no neo vao mot ngay khac VNINDEX va RS so sanh hai moc lech nhau.
CU_TOI_DA_NGAY = 10


def danh_sach_ma():
    """Toan bo co phieu (type STOCK) tren HOSE/HNX/UPCoM + san va ma ICB cap 2."""
    for lan in range(4):
        try:
            r = requests.get(LIST_URL, headers=H, timeout=60)
            r.raise_for_status()
            d = r.json()
            break
        except Exception:
            if lan == 3:
                raise
            time.sleep(2 * (lan + 1))
    out = {}
    for x in d:
        if x.get("type") == "STOCK" and x.get("board") in SAN:
            out[x["symbol"]] = {"san": x["board"], "icb": x.get("icbCode2")}
    return out


def tai_bar(ma, to_ts):
    body = {"timeFrame": "ONE_DAY", "symbols": [ma], "to": to_ts, "countBack": COUNT_BACK}
    for lan in range(4):
        try:
            r = requests.post(PX_URL, json=body, headers=H, timeout=60)
            r.raise_for_status()
            d = r.json()
            break
        except Exception:
            if lan == 3:
                raise
            time.sleep(2 * (lan + 1))
    if not d:
        return None
    x = d[0]
    # Moi bar: [ngay 'YYYY-MM-DD', O, H, L, C, V] — cung thu tu voi TradingView.
    return [[datetime.fromtimestamp(int(t)).strftime("%Y-%m-%d"), float(o), float(h),
             float(l), float(c), float(v or 0)]
            for t, o, h, l, c, v in zip(x["t"], x["o"], x["h"], x["l"], x["c"], x["v"])]


def cat_phien_dang_chay(b, den):
    """Bo bar cua phien chua dong cua. Vietcap tra ve phien dang chay nhu mot bar
    binh thuong; tinh MA/RS tren no la dung gia giua phien lam gia dong cua."""
    if not b:
        return b
    now = datetime.now()
    hom_nay = now.strftime("%Y-%m-%d")
    if den is None and b[-1][0] == hom_nay and now.hour < 15:
        return b[:-1]
    return b


def dist_ma50(c):
    """(a) cua quy tac 5 ban cu — giu trong schema, khong con duoc doc."""
    n = len(c)
    if n < MA_LEN + 20:
        return [None, None, 0]
    d, s = [], 0.0
    for i in range(n):
        s += c[i]
        if i >= MA_LEN:
            s -= c[i - MA_LEN]
        if i >= MA_LEN - 1:
            ma = s / MA_LEN
            d.append(c[i] / ma - 1 if ma > 0 else 0)
    d = d[-NEED_OBS:]
    now = d[-1]
    le = sum(1 for x in d if x <= now)
    return [round(now, 4), round(le / len(d), 3), len(d)]


def metrics(b):
    """Ban Python cua metrics() trong lt_scan_tradingview.js — tung dong mot."""
    c = [x[4] for x in b]
    h = [x[2] for x in b]
    l = [x[3] for x in b]
    v = [x[5] for x in b]
    n = len(c)

    def ret(k):
        return c[n - 1] / c[n - 1 - k] - 1 if n > k and c[n - 1 - k] > 0 else None

    def sma(k):
        return sum(c[n - k:]) / k if n >= k else None

    tr = [max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1])) / c[i]
          for i in range(max(1, n - 14), n)]
    atr = sum(tr) / len(tr)
    w20 = range(max(0, n - 20), n)
    to = sum(c[i] * v[i] for i in w20) / len(w20)
    ds = [round(c[i]) for i in range(n - 1, -1, -10)][::-1][-DS_KEEP:]
    w = min(VOL_WIN, n)
    vol60 = [round((v[i] or 0) / 1000) for i in range(n - w, n)]
    c60 = [round(c[i]) for i in range(n - w, n)]

    def rnd(x, d):
        return None if x is None else round(x, d)

    def rint(x):
        return None if x is None else round(x)

    return [rnd(c[-1], 2), rnd(ret(21), 4), rnd(ret(63), 4), rnd(ret(126), 4), rnd(ret(252), 4),
            rint(sma(50)), rint(sma(200)), rnd(atr, 4),
            round(to / 1e8) / 10, ds,
            rnd(ret(1), 4), rnd(ret(5), 4),
            dist_ma50(c), vol60, c60]


def quet(ds_ma, to_ts, den, luong=6):
    res, loi, bars = {}, [], {}

    def mot(ma):
        b = cat_phien_dang_chay(tai_bar(ma, to_ts), den)
        return ma, b

    with ThreadPoolExecutor(max_workers=luong) as ex:
        fut = [ex.submit(mot, ma) for ma in ds_ma]
        for i, f in enumerate(as_completed(fut), 1):
            try:
                ma, b = f.result()
            except Exception as e:
                loi.append(str(e)[:80])
                continue
            if not b or len(b) < 22:
                loi.append(f"{ma}: {len(b) if b else 0} bar")
                continue
            bars[ma] = b
            if i % 100 == 0:
                print(f"  {i}/{len(ds_ma)}", flush=True)
    return bars, loi


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--den", help="YYYY-MM-DD: quet nhu tai cuoi phien ngay nay")
    ap.add_argument("--ma-tu", help="lay ro ma tu mot file scan_*.json (de doi chieu)")
    ap.add_argument("--luong", type=int, default=6)
    ap.add_argument("--ra", help="ghi ra duong dan nay thay vi data/ (chay thu)")
    a = ap.parse_args()

    ds = danh_sach_ma()
    if a.ma_tu:
        ro = [k for k in json.load(open(a.ma_tu, encoding="utf-8")) if not k.startswith("_")]
    else:
        ro = sorted(ds)
    ro = sorted(set(ro) | {"VNINDEX"})
    if a.den:
        to_ts = int((datetime.strptime(a.den, "%Y-%m-%d") + timedelta(hours=23)).timestamp())
    else:
        to_ts = int(time.time())

    t0 = time.time()
    print(f"Quet {len(ro)} ma tu Vietcap ({a.luong} luong)...", flush=True)
    bars, loi = quet(ro, to_ts, a.den, a.luong)
    if "VNINDEX" not in bars:
        sys.exit("Khong tai duoc VNINDEX — khong tinh duoc RS. Dung.")
    ngay_du_lieu = bars["VNINDEX"][-1][0]

    # Ma dung giao dich: bar cuoi cach ngay du lieu cua VNINDEX qua CU_TOI_DA_NGAY.
    moc = (datetime.strptime(ngay_du_lieu, "%Y-%m-%d")
           - timedelta(days=CU_TOI_DA_NGAY)).strftime("%Y-%m-%d")
    cu = sorted(ma for ma, b in bars.items() if b[-1][0] < moc)
    lech_ngay = sorted(ma for ma, b in bars.items()
                       if moc <= b[-1][0] < ngay_du_lieu)

    out = {}
    for ma in sorted(bars):
        if ma in cu:
            continue
        out[ma] = metrics(bars[ma])
    n_bar = [len(b) for b in bars.values()]

    out["_meta"] = {
        "nguon": "Vietcap gap-chart ONE_DAY (gia da dieu chinh co tuc)",
        "script": "lt_scan_vietcap.py",
        "chay_luc": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "ngay_du_lieu": ngay_du_lieu,
        "so_ma_yeu_cau": len(ro),
        "so_ma_ghi": len(out),
        "cu_dung_giao_dich": cu,
        "bar_cuoi_lech_ngay": lech_ngay,
        "loi": loi,
        "bars_min_max": [min(n_bar), max(n_bar)],
        "fields": ["c", "r21", "r63", "r126", "r252", "ma50", "ma200", "atr", "tov_ty",
                   "ds", "r1", "r5", "dma50", "vol60", "c60"],
    }
    out["_san"] = {ma: ds.get(ma, {}).get("san") for ma in out if not ma.startswith("_")}
    out["_icb"] = {ma: ds.get(ma, {}).get("icb") for ma in out if not ma.startswith("_")}

    ngay_file = (a.den or os.environ.get("NGAY_CHAY")
                 or datetime.now().strftime("%Y-%m-%d")).replace("-", "")
    ten = (f"scan_vietcap_doi_chieu_{ngay_file}.json" if a.ma_tu
           else f"scan_{ngay_file}.json")
    path = a.ra or os.path.join("data", ten)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))

    so_ma = len(out) - 3
    print(f"\nXong {time.time()-t0:.0f}s. Du lieu den {ngay_du_lieu}. Ghi {so_ma} ma -> {path}")
    print(f"  bar/ma: {min(n_bar)}-{max(n_bar)} | loi: {len(loi)} | dung giao dich (> "
          f"{CU_TOI_DA_NGAY} ngay): {len(cu)} | bar cuoi lech ngay VNINDEX: {len(lech_ngay)}")
    thieu = [ma for ma, v in out.items() if not ma.startswith("_") and v[5] is None]
    if thieu:
        print(f"  {len(thieu)} ma chua du 200 phien (MA200 = None) -> screener loai o Buoc 1")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
