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
(xem FIELDS trong lt_screener.py) de screener doc khong phai sua. Them cac khoa
phu bat dau bang "_" (screener tach rieng): _meta, _san, _icb, va tu 04/10/2026
_vnindex = {t, c, v} — toan bo chuoi phien cua VNINDEX de lt_che_do.py phat lai
che do thi truong (co do tre nen can ca duong di, khong chi MA ngay cuoi).

QUET HAI TANG (tu 31/10/2026). Tu 26/10 CDN Vietcap chan IP khi quet du 1.520 ma, nen moi
phien chi tai lai:
  * Tang 1 — moi phien: ma co GTGD TB20 >= TANG1_TOV_TY o ban quet goc (ban moi nhat co ngay
    du lieu <= phien can quet), moi ma trong tham_dinh.json (ro + phieu) va moi ma dang giu.
  * Phan con lai chia SO_NHOM_XOAY nhom co dinh (crc32 cua ma); moi phien lam moi mot nhom
    (theo ngay lich % 5 -> Thu 2..Thu 6 phu du 5 nhom). Ma chua toi luot thi MANG SANG nguyen
    dong cua ban goc va ghi ngay du lieu cua dong do vao khoa phu _mang_sang = {ma: ngay}.
    Dong mang sang cu hon MANG_SANG_TOI_DA ngay lich thi bat buoc tai lai.
  Dong mang sang chi la ma GTGD < 1 ty (khong qua duoc loc 10 ty cua screener); dashboard
  loai chung khoi do rong va chuoi thoi gian. --toan-bo quet nhu cu.

NGUON DU PHONG VNDirect (tu 31/10/2026): ma nao Vietcap chan/loi mang thi tai tu VNDirect
dchart; Vietcap chan NGAT_SAU lan lien tiep thi NGAT Vietcap cho het lan chay (khong goi
tiep vao mot CDN dang chan). Ma lay tu VNDirect liet ke o _meta.nguon_vnd. VNINDEX chi lay
tu Vietcap (xem VND_URL). --khong-du-phong: chi Vietcap nhu cu.

Chay:
  PYTHONIOENCODING=utf-8 python lt_scan_vietcap.py              # phien moi nhat, hai tang
  PYTHONIOENCODING=utf-8 python lt_scan_vietcap.py --toan-bo    # moi ma (de bi Vietcap chan)
  PYTHONIOENCODING=utf-8 python lt_scan_vietcap.py --cac-ngay 2026-10-23,2026-10-26 --ra-thu-muc data
      # quet bu NHIEU phien trong MOT lan tai: moi ma tai mot lan den phien cuoi, cat chuoi
      # theo tung phien (Vietcap dieu chinh co tuc ca chuoi theo hom nay nen giong het --den)
  PYTHONIOENCODING=utf-8 python lt_scan_vietcap.py --den 2026-09-21 --ma-tu data/scan_20260921.json
      # dung lai ban quet cua mot ngay cu tren dung ro ma cua file do -> doi
      # chieu voi ban TradingView (ghi ra data/scan_vietcap_doi_chieu_YYYYMMDD.json,
      # KHONG de len scan_*.json)
"""

import argparse
import glob
import json
import os
import sys
import threading
import time
import zlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta

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

# Ti le ma toi da duoc phep mat vi loi mang (sau vong vet) ma van ghi ban quet.
MAT_MANG_TOI_DA = 0.01


# --- Mang (sua 26/10/2026) ---
# CDN cua Vietcap (veloceed) chan theo IP khi gui nhieu: request bi GIU ~30 giay roi tra 418
# (body rong). Ban cu mo ket noi moi cho moi request, cho toi 60 giay, nghi 2 giay roi thu lai
# -> moi lan bi chan mat ~33 giay; 6 luong cung bi chan thi ban quet 1.500 ma keo hang gio.
# Cach chua, chi o tang mang (khong doi cach tinh):
#   1. Moi luong giu mot Session (keep-alive): do 26/10 thi it bi chan hon han ket noi moi.
#   2. Cat request sau DOC_TOI_DA giay (tra loi binh thuong < 1 giay) thay vi ngoi cho 30 giay.
#   3. PHANH chung cho moi luong: bi chan -> gian khoang cach giua hai request va nghi chung;
#      thong -> rut dan ve khoang toi thieu.
KET_NOI_TOI_DA = 5
DOC_TOI_DA = 8
LAN_THU = 6
LAN_THU_QUET = 3          # moi ma thu Vietcap bay nhieu lan roi chuyen VNDirect
MA_CHAN = {418, 429, 500, 502, 503, 504}
NGAT_SAU = 3              # Vietcap chan lien tiep >= NGAT_SAU lan -> ngat Vietcap den het lan chay

# --- Nguon du phong VNDirect (them 31/10/2026) ---
# Doi chieu 31/10/2026 tren 148 ma (chuoi 60 phien den 22/10): gia da dieu chinh va KL khop lenh
# cua co phieu TRUNG Vietcap o 119 ma. Lech con lai: (a) su kien chia/thuong sau 22/10 (TCB,
# NT2...) — Vietcap hien tai cung da dieu chinh y het; (b) KL lech 1-3% vai phien o mot so ma;
# (c) ma cuc it thanh khoan (VGR, POM) lech mot phien vi VNDirect ghi ca phien KL = 0 -> bo cac
# bar do. VNDirect tinh gia theo NGHIN dong -> nhan 1.000.
# KHONG dung cho VNINDEX: KL chi so cua VNDirect thap hon Vietcap ~14% (26/10: 519 trieu so voi
# 605 trieu) ma luat phien phan phoi doc KL chi so.
VND_URL = "https://dchart-api.vndirect.com.vn/dchart/history"
H_VND = {"User-Agent": "Mozilla/5.0"}
VND_NGAY = 950            # ngay lich lui lai: ~640 phien, du COUNT_BACK

# --- Quet hai tang (them 31/10/2026) ---
TANG1_TOV_TY = 1.0        # GTGD TB20 (ty) o ban goc tu muc nay tro len -> quet moi phien
SO_NHOM_XOAY = 5
MANG_SANG_TOI_DA = 14     # ngay lich
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


class _Phanh:
    """Nhip gui chung cho moi luong (AIMD): chan thi gap doi khoang cach + nghi, thong thi rut dan."""

    def __init__(self, khoang_min=0.3, khoang_max=3.0):
        self.khoa = threading.Lock()
        self.khoang_min, self.khoang_max = khoang_min, khoang_max
        self.khoang = khoang_min
        self.luot_toi = 0.0        # thoi diem (monotonic) som nhat cho request ke tiep
        self.chan_lien = 0
        self.so_chan = 0

    def cho(self):
        with self.khoa:
            bay_gio = time.monotonic()
            t = max(bay_gio, self.luot_toi)
            self.luot_toi = t + self.khoang
        if t > bay_gio:
            time.sleep(t - bay_gio)

    def bi_chan(self):
        with self.khoa:
            self.so_chan += 1
            self.chan_lien += 1
            self.khoang = min(self.khoang * 2, self.khoang_max)
            nghi = min(5 * 2 ** (self.chan_lien - 1), 60)
            self.luot_toi = max(self.luot_toi, time.monotonic() + nghi)

    def thong(self):
        with self.khoa:
            self.chan_lien = 0
            self.khoang = max(self.khoang * 0.9, self.khoang_min)


PHANH = _Phanh()
PHANH_VND = _Phanh(khoang_min=0.35, khoang_max=5.0)
VIETCAP_NGAT = threading.Event()
_LUONG = threading.local()


def _session():
    s = getattr(_LUONG, "s", None)
    if s is None:
        s = requests.Session()
        s.headers.update(H)
        _LUONG.s = s
    return s


def _session_vnd():
    s = getattr(_LUONG, "s_vnd", None)
    if s is None:
        s = requests.Session()
        s.headers.update(H_VND)
        _LUONG.s_vnd = s
    return s


def _goi(method, url, nguon="vietcap", lan_thu=LAN_THU, **kw):
    """Mot request qua PHANH cua nguon do; tra ve JSON. Het `lan_thu` lan van bi chan -> raise."""
    vc = nguon == "vietcap"
    phanh = PHANH if vc else PHANH_VND
    loi = None
    for _ in range(lan_thu):
        phanh.cho()
        try:
            s = _session() if vc else _session_vnd()
            r = s.request(method, url, timeout=(KET_NOI_TOI_DA, DOC_TOI_DA), **kw)
        except requests.exceptions.RequestException as e:
            loi = e
            if vc:                     # bo ket noi hong, lan sau mo moi
                _LUONG.s = None
            else:
                _LUONG.s_vnd = None
            phanh.bi_chan()
            continue
        if r.status_code in MA_CHAN:
            loi = requests.HTTPError(f"HTTP {r.status_code}")
            phanh.bi_chan()
            continue
        r.raise_for_status()
        phanh.thong()
        return r.json()
    raise loi


def danh_sach_ma():
    """Toan bo co phieu (type STOCK) tren HOSE/HNX/UPCoM + san va ma ICB cap 2."""
    d = _goi("GET", LIST_URL)
    out = {}
    for x in d:
        if x.get("type") == "STOCK" and x.get("board") in SAN:
            out[x["symbol"]] = {"san": x["board"], "icb": x.get("icbCode2")}
    return out


def tai_bar(ma, to_ts, lan_thu=LAN_THU_QUET):
    body = {"timeFrame": "ONE_DAY", "symbols": [ma], "to": to_ts, "countBack": COUNT_BACK}
    d = _goi("POST", PX_URL, json=body, lan_thu=lan_thu)
    if not d:
        return None
    x = d[0]
    # Moi bar: [ngay 'YYYY-MM-DD', O, H, L, C, V] — cung thu tu voi TradingView.
    return [[datetime.fromtimestamp(int(t)).strftime("%Y-%m-%d"), float(o), float(h),
             float(l), float(c), float(v or 0)]
            for t, o, h, l, c, v in zip(x["t"], x["o"], x["h"], x["l"], x["c"], x["v"])]


def doc_vnd(d):
    """JSON dchart cua VNDirect -> bar cung dang tai_bar (dong, bo phien KL = 0)."""
    if not isinstance(d, dict) or d.get("s") != "ok" or not d.get("t"):
        return None
    out = [[datetime.fromtimestamp(int(t)).strftime("%Y-%m-%d"), round(o * 1000, 2),
            round(h * 1000, 2), round(l * 1000, 2), round(c * 1000, 2), float(v)]
           for t, o, h, l, c, v in zip(d["t"], d["o"], d["h"], d["l"], d["c"], d["v"]) if v]
    return out[-COUNT_BACK:]


def tai_bar_vnd(ma, to_ts):
    if ma == "VNINDEX":
        raise ValueError("VNINDEX chi lay tu Vietcap (KL chi so VNDirect khac)")
    p = {"resolution": "D", "symbol": ma, "from": to_ts - VND_NGAY * 86400, "to": to_ts}
    return doc_vnd(_goi("GET", VND_URL, nguon="vnd", params=p))


def tai_mot(ma, to_ts, du_phong=True):
    """(bars, nguon). Vietcap truoc; bi chan / loi mang -> VNDirect (neu du_phong).

    Vietcap chan NGAT_SAU lan lien tiep thi dat VIETCAP_NGAT: moi ma sau do di thang VNDirect.
    """
    if not (du_phong and VIETCAP_NGAT.is_set()):
        try:
            return tai_bar(ma, to_ts), "vietcap"
        except requests.RequestException:
            if not du_phong:
                raise
            if PHANH.chan_lien >= NGAT_SAU and not VIETCAP_NGAT.is_set():
                VIETCAP_NGAT.set()
                print(f"  Vietcap chan {PHANH.chan_lien} lan lien tiep -> ngat Vietcap, cac ma con "
                      "lai lay tu VNDirect", flush=True)
    return tai_bar_vnd(ma, to_ts), "vnd"


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


def quet(ds_ma, to_ts, den, luong=6, du_phong=True):
    """Tai bar cho ds_ma -> (bars, loi, mat_mang, nguon). nguon = {ma: 'vietcap' | 'vnd'}."""
    loi, bars, nguon = [], {}, {}

    def mot(ma):
        b, ng = tai_mot(ma, to_ts, du_phong)
        return ma, cat_phien_dang_chay(b, den), ng

    def vong(ds, luong):
        hong = []
        t0 = time.time()
        with ThreadPoolExecutor(max_workers=luong) as ex:
            fut = {ex.submit(mot, ma): ma for ma in ds}
            for i, f in enumerate(as_completed(fut), 1):
                try:
                    ma, b, ng = f.result()
                except Exception as e:
                    hong.append((fut[f], str(e)[:80]))
                    continue
                if not b or len(b) < 22:
                    loi.append(f"{ma}: {len(b) if b else 0} bar")
                    continue
                bars[ma], nguon[ma] = b, ng
                if i % 100 == 0:
                    n_vnd = sum(1 for x in nguon.values() if x == "vnd")
                    print(f"  {i}/{len(ds)} — {time.time() - t0:.0f}s, Vietcap chan {PHANH.so_chan} lan,"
                          f" VNDirect {n_vnd} ma", flush=True)
        return hong

    hong = vong(ds_ma, luong)
    if hong:
        # Vong vet: mot luong, de PHANH nghi du lau cho IP duoc tha.
        print(f"  Quet vet {len(hong)} ma loi mang...", flush=True)
        hong = vong([ma for ma, _ in hong], 1)
    loi += [f"{ma}: {e}" for ma, e in hong]
    return bars, loi, [ma for ma, _ in hong], nguon


# ------------------------------------------------------------------ quet hai tang
def tim_ban_goc(ngay_max, thu_muc=None):
    """Ban quet Vietcap moi nhat co ngay du lieu <= ngay_max -> (path, scan) | (None, None)."""
    tep = sorted(glob.glob(os.path.join(thu_muc or DATA_DIR, "scan_" + "[0-9]" * 8 + ".json")),
                 reverse=True)
    for f in tep:
        try:
            with open(f, encoding="utf-8") as fh:
                s = json.load(fh)
        except (OSError, ValueError):
            continue
        d = (s.get("_meta") or {}).get("ngay_du_lieu")
        if d and d <= ngay_max:
            return f, s
    return None, None


def dong_goc(goc):
    """{ma: dong} cua ban goc (bo khoa phu va VNINDEX)."""
    return {k: v for k, v in goc.items() if not k.startswith("_") and k != "VNINDEX"}


def ngay_dong(goc):
    """{ma: ngay du lieu cua dong} — dong mang sang giu ngay cu, con lai = ngay cua ban goc."""
    d0 = goc.get("_meta", {}).get("ngay_du_lieu")
    ms = goc.get("_mang_sang", {})
    return {k: ms.get(k, d0) for k in dong_goc(goc)}


def nhom_xoay(ma):
    return zlib.crc32(ma.encode("utf-8")) % SO_NHOM_XOAY


def nhom_cua_ngay(ngay):
    return date.fromisoformat(ngay).toordinal() % SO_NHOM_XOAY


def ma_uu_tien():
    """Ma luon quet moi phien: moi ma co ban ghi trong tham_dinh.json (ro + phieu) va ma dang giu."""
    from lt_config import HOLDINGS, THAM_DINH_FILE
    out = set()
    try:
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), THAM_DINH_FILE)
        with open(p, encoding="utf-8") as f:
            out |= {k for k in json.load(f) if not k.startswith("_")}
    except (OSError, ValueError):
        pass
    for ds in HOLDINGS.values():
        for x in ds:
            ma = x[0] if isinstance(x, (list, tuple)) else (x.get("ma") if isinstance(x, dict) else x)
            if ma:
                out.add(ma)
    return out


def chon_ma(tat_ca, goc, uu_tien, ngay_max):
    """Chia ro ma (moi ma dang niem yet, tru VNINDEX) thanh ma phai TAI va ma MANG SANG.

    Tra ve (tai: set, mang_sang: {ma: ngay}, tang1: set, info: dict).
    """
    dg, nd = dong_goc(goc), ngay_dong(goc)
    moc = (date.fromisoformat(ngay_max) - timedelta(days=MANG_SANG_TOI_DA)).isoformat()
    tang1 = {m for m in tat_ca if m in uu_tien or (m in dg and (dg[m][8] or 0) >= TANG1_TOV_TY)}
    nhom = nhom_cua_ngay(ngay_max)
    xoay = {m for m in tat_ca - tang1 if nhom_xoay(m) == nhom}
    qua_han = {m for m in tat_ca - tang1 - xoay if m in nd and nd[m] < moc}
    tai = tang1 | xoay | qua_han
    mang_sang = {m: nd[m] for m in tat_ca - tai if m in nd}
    info = {"tang1": len(tang1), "xoay": len(xoay), "nhom_xoay": nhom, "qua_han": len(qua_han),
            "bo_qua_chua_co_dong": len(tat_ca - tai - set(mang_sang))}
    return tai, mang_sang, tang1, info


def dung_ban_quet(bars, phien, san_icb, goc, mang_sang, nguon, meta_them):
    """Ban quet cua `phien` tu bar da tai (cat chuoi den `phien`) + dong mang sang tu ban goc."""
    vb = [x for x in bars["VNINDEX"] if x[0] <= phien]
    ngay_du_lieu = vb[-1][0]
    loi, b_p = [], {}
    for ma, b in bars.items():
        bb = [x for x in b if x[0] <= phien]
        if len(bb) < 22:
            loi.append(f"{ma}: {len(bb)} bar den {phien}")
            continue
        b_p[ma] = bb

    # Ma dung giao dich: bar cuoi cach ngay du lieu cua VNINDEX qua CU_TOI_DA_NGAY.
    moc = (datetime.strptime(ngay_du_lieu, "%Y-%m-%d")
           - timedelta(days=CU_TOI_DA_NGAY)).strftime("%Y-%m-%d")
    cu = sorted(ma for ma, b in b_p.items() if b[-1][0] < moc)
    lech_ngay = sorted(ma for ma, b in b_p.items() if moc <= b[-1][0] < ngay_du_lieu)

    out = {ma: metrics(b_p[ma]) for ma in sorted(b_p) if ma not in cu}
    ms = {}
    if goc is not None:
        for ma, nd in sorted(mang_sang.items()):
            if ma not in out and ma in goc and nd <= ngay_du_lieu:
                out[ma] = goc[ma]
                ms[ma] = nd
    n_bar = [len(b) for b in b_p.values()]
    vnd = sorted(ma for ma in b_p if nguon.get(ma) == "vnd" and ma in out)

    out["_meta"] = {
        "nguon": ("Vietcap gap-chart ONE_DAY (gia da dieu chinh co tuc); ma trong nguon_vnd lay tu "
                  "VNDirect dchart (du phong khi Vietcap chan)"),
        "script": "lt_scan_vietcap.py",
        "chay_luc": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "ngay_du_lieu": ngay_du_lieu,
        **meta_them,
        "so_ma_ghi": len(out),
        "so_ma_mang_sang": len(ms),
        "cu_dung_giao_dich": cu,
        "bar_cuoi_lech_ngay": lech_ngay,
        "loi": meta_them.get("loi", []) + loi,
        "nguon_vnd": vnd,
        "vietcap_chan": PHANH.so_chan,
        "vietcap_ngat": VIETCAP_NGAT.is_set(),
        "bars_min_max": [min(n_bar), max(n_bar)],
        "fields": ["c", "r21", "r63", "r126", "r252", "ma50", "ma200", "atr", "tov_ty",
                   "ds", "r1", "r5", "dma50", "vol60", "c60"],
    }
    goc = goc or {}
    hang = [ma for ma in out if not ma.startswith("_")]
    out["_san"] = {ma: (san_icb.get(ma) or {}).get("san") or goc.get("_san", {}).get(ma) for ma in hang}
    out["_icb"] = {ma: (san_icb.get(ma) or {}).get("icb") or goc.get("_icb", {}).get(ma) for ma in hang}
    out["_mang_sang"] = ms
    out["_vnindex"] = {"t": [x[0] for x in vb], "c": [round(x[4], 2) for x in vb],
                       "v": [round(x[5]) for x in vb]}
    return out


def _ghi(out, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    m = out["_meta"]
    so_ma = sum(1 for k in out if not k.startswith("_"))
    print(f"\nDu lieu den {m['ngay_du_lieu']}. Ghi {so_ma} ma -> {path}")
    print(f"  bar/ma: {m['bars_min_max'][0]}-{m['bars_min_max'][1]} | loi: {len(m['loi'])} | dung giao "
          f"dich (> {CU_TOI_DA_NGAY} ngay): {len(m['cu_dung_giao_dich'])} | bar cuoi lech ngay "
          f"VNINDEX: {len(m['bar_cuoi_lech_ngay'])} | mang sang: {m['so_ma_mang_sang']} | VNDirect: "
          f"{len(m['nguon_vnd'])} ma | Vietcap chan: {m['vietcap_chan']} lan"
          + (" (da ngat)" if m["vietcap_ngat"] else ""))
    thieu = [ma for ma, v in out.items() if not ma.startswith("_") and v[5] is None]
    if thieu:
        print(f"  {len(thieu)} ma chua du 200 phien (MA200 = None) -> screener loai o Buoc 1")


def _ts_cuoi_ngay(ngay):
    return int((datetime.strptime(ngay, "%Y-%m-%d") + timedelta(hours=23)).timestamp())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--den", help="YYYY-MM-DD: quet nhu tai cuoi phien ngay nay")
    ap.add_argument("--cac-ngay", help="D1,D2,...: quet bu nhieu phien trong MOT lan tai, ghi "
                                       "scan_<D>.json vao --ra-thu-muc")
    ap.add_argument("--ra-thu-muc", default=DATA_DIR)
    ap.add_argument("--ma-tu", help="lay ro ma tu mot file scan_*.json (de doi chieu)")
    ap.add_argument("--toan-bo", action="store_true", help="quet moi ma, bo hai tang")
    ap.add_argument("--khong-du-phong", action="store_true", help="chi Vietcap, khong dung VNDirect")
    ap.add_argument("--luong", type=int, default=3)
    ap.add_argument("--ra", help="ghi ra duong dan nay thay vi data/ (chay thu)")
    a = ap.parse_args()
    if a.cac_ngay and (a.den or a.ra or a.ma_tu):
        ap.error("--cac-ngay khong di cung --den / --ra / --ma-tu")
    cac_ngay = sorted({x.strip() for x in a.cac_ngay.split(",") if x.strip()}) if a.cac_ngay else None
    den = cac_ngay[-1] if cac_ngay else a.den
    to_ts = _ts_cuoi_ngay(den) if den else int(time.time())
    t0 = time.time()

    # 1. VNINDEX truoc tien, luc IP con nghi; chi Vietcap, kien nhan du LAN_THU lan.
    try:
        vb = cat_phien_dang_chay(tai_bar("VNINDEX", to_ts, lan_thu=LAN_THU), den)
    except requests.RequestException as e:
        sys.exit(f"Khong tai duoc VNINDEX tu Vietcap ({e}) — Vietcap dang chan IP. Doi ~1 gio roi "
                 "quet lai. (VNINDEX khong lay tu VNDirect: KL chi so khac, lech phien phan phoi.)")
    if not vb:
        sys.exit("Khong tai duoc VNINDEX — khong tinh duoc RS. Dung.")
    ngay_max = vb[-1][0]

    # 2. Ban goc (cho hai tang va du phong danh sach ma): ngay du lieu <= phien SOM nhat can ghi.
    goc_path, goc = tim_ban_goc(cac_ngay[0] if cac_ngay else ngay_max)

    # 3. Danh sach ma.
    try:
        ds = danh_sach_ma()
        ds_tu = "vietcap getAll"
    except requests.RequestException as e:
        if goc is None:
            sys.exit(f"Khong tai duoc danh sach ma ({e}) va khong co ban goc. Dung.")
        ds = {m: {"san": goc.get("_san", {}).get(m), "icb": goc.get("_icb", {}).get(m)}
              for m in dong_goc(goc)}
        ds_tu = f"ban goc {os.path.basename(goc_path)} (Vietcap getAll loi: {str(e)[:60]})"
        print(f"  Danh sach ma lay tu {ds_tu} — ma moi niem yet / vua giao dich lai se thieu.", flush=True)
    tat_ca = set(ds) - {"VNINDEX"}

    tang1, mang_sang = set(), {}
    if a.ma_tu:
        with open(a.ma_tu, encoding="utf-8") as f:
            ro = {k for k in json.load(f) if not k.startswith("_")} - {"VNINDEX"}
        goc, info = None, {"che_do_quet": "doi_chieu"}
    elif a.toan_bo or goc is None:
        if goc is None:
            print("  Khong co ban goc -> quet toan bo.", flush=True)
        ro, goc, info = tat_ca, None, {"che_do_quet": "toan_bo"}
    else:
        ro, mang_sang, tang1, info = chon_ma(tat_ca, goc, ma_uu_tien(), ngay_max)
        info = {"che_do_quet": "hai_tang", "ban_goc": os.path.basename(goc_path), **info}
        print(f"  Hai tang: tang 1 {info['tang1']} ma, nhom xoay {info['nhom_xoay']} {info['xoay']} ma, "
              f"qua han {info['qua_han']}, mang sang {len(mang_sang)} ma (ban goc "
              f"{info['ban_goc']})", flush=True)

    print(f"Quet {len(ro)} ma ({a.luong} luong, du phong VNDirect "
          f"{'TAT' if a.khong_du_phong else 'BAT'})...", flush=True)
    bars, loi, mat_mang, nguon = quet(sorted(ro), to_ts, den, a.luong, du_phong=not a.khong_du_phong)
    bars["VNINDEX"], nguon["VNINDEX"] = vb, "vietcap"
    # Mat ma vi mang thi screener tuong ma do khong ton tai (ke ca ma dang giu) -> khong ghi
    # ban quet thieu qua MAT_MANG_TOI_DA; ban cu ghi luon, im lang.
    if len(mat_mang) > MAT_MANG_TOI_DA * max(len(ro), 1):
        sys.exit(f"{len(mat_mang)}/{len(ro)} ma khong tai duoc (Vietcap chan {PHANH.so_chan} lan) — "
                 "khong ghi ban quet thieu. Doi vai phut roi quet lai.")
    if goc is not None:
        # Ma ngoai tang 1 tai hong (loi mang, hoac VNDirect bo phien KL 0 nen con < 22 bar) thi
        # mang sang dong cu, trong han MANG_SANG_TOI_DA (qua han -> bo, de ma huy niem yet khong
        # bi mang mai). Ma tang 1 hong thi bo: khong dua gia cu cua ma thanh khoan vao screener.
        nd = ngay_dong(goc)
        moc = (date.fromisoformat(ngay_max) - timedelta(days=MANG_SANG_TOI_DA)).isoformat()
        for m in ro - set(bars) - tang1:
            if m in nd and nd[m] >= moc:
                mang_sang[m] = nd[m]
    meta_them = {**info, "danh_sach_ma": ds_tu, "so_ma_yeu_cau": len(ro) + 1, "loi": loi,
                 "mat_mang": mat_mang}

    if cac_ngay:
        phien_co = {x[0] for x in vb}
        for p in cac_ngay:
            if p not in phien_co:
                print(f"\n!! {p} khong phai phien giao dich cua VNINDEX — bo qua.", flush=True)
                continue
            _ghi(dung_ban_quet(bars, p, ds, goc, mang_sang, nguon, meta_them),
                 os.path.join(a.ra_thu_muc, f"scan_{p.replace('-', '')}.json"))
    else:
        out = dung_ban_quet(bars, ngay_max, ds, goc, mang_sang, nguon, meta_them)
        ngay_file = (a.den or os.environ.get("NGAY_CHAY")
                     or datetime.now().strftime("%Y-%m-%d")).replace("-", "")
        ten = (f"scan_vietcap_doi_chieu_{ngay_file}.json" if a.ma_tu
               else f"scan_{ngay_file}.json")
        _ghi(out, a.ra or os.path.join(DATA_DIR, ten))
    print(f"Xong {time.time() - t0:.0f}s.")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
