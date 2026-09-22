"""
canslim_data.py — Tai va nap du lieu cho Buoc 3a CANSLIM (chot 22/09/2026).

Nguon: API cong khai cua Vietcap (cung nguon ma vnstock/VCI goi).
  - BCTC: iq.vietcap.com.vn .../financial-statement?section=...  -> 34 quy tu Q1/2018
  - Gia : trading.vietcap.com.vn/api/chart/OHLCChart/gap-chart   -> gia ngay DA DIEU CHINH

Ban cong dong cua vnstock tu cat con 4 ky o phia client (head(4)); server tra du.
File nay KHONG sua vnstock — goi thang endpoint.

Cache: data/canslim_cache/<MA>_fin.json va <MA>_px.json. Chay lai chi tai ma thieu,
tru khi dat CANSLIM_TAI_LAI=1.

CHONG NHIN TRUOC TUONG LAI: moi ky bao cao co `ngay_hieu_luc` = ngay som nhat duoc
phep dung so lieu do:
  max(publicDate, cuoi_quy + 20 ngay)        neu co publicDate
  cuoi_quy + 45 ngay (Q4 / nam: + 90 ngay)   neu thieu publicDate
Gioi han con lai (phai ghi trong bao cao): so lieu la ban MOI NHAT (da dieu chinh hoi
to neu co), khong phai ban cong bo lan dau.
"""

import datetime as dt
import json
import os
import sys
import time

import requests

CACHE = os.path.join("data", "canslim_cache")
H = {"User-Agent": "Mozilla/5.0", "Referer": "https://trading.vietcap.com.vn/",
     "Origin": "https://trading.vietcap.com.vn/"}
FIN_URL = "https://iq.vietcap.com.vn/api/iq-insight-service/v1/company/{}/financial-statement"
PX_URL = "https://trading.vietcap.com.vn/api/chart/OHLCChart/gap-chart"

# Truong can dung (ma truong Vietcap). Cac ma khac bi bo de cache gon.
TRUONG = {
    "INCOME_STATEMENT": ("isa3", "isb27", "isa20", "isa22"),
    "BALANCE_SHEET": ("bsa78",),
    "CASH_FLOW": ("cfa18",),
}
META = ("yearReport", "lengthReport", "publicDate")


def _get(url, **kw):
    for lan in range(4):
        try:
            r = requests.get(url, headers=H, timeout=60, **kw)
            r.raise_for_status()
            return r.json()
        except Exception:                           # mang chap chon -> thu lai
            if lan == 3:
                raise
            time.sleep(2 * (lan + 1))


def tai_bctc(ma):
    out = {"quarters": {}, "years": {}}
    for sec, fields in TRUONG.items():
        data = _get(FIN_URL.format(ma), params={"section": sec})["data"]
        for kind in ("quarters", "years"):
            for rec in data.get(kind) or []:
                key = f"{rec['yearReport']}-{rec['lengthReport']}"
                row = out[kind].setdefault(key, {m: rec.get(m) for m in META})
                # Moi phan BCTC giu ngay cong bo RIENG (phan xet Codex #3); ngay
                # hieu luc cua ky = ngay MUON NHAT trong cac phan.
                row["pd_" + sec] = rec.get("publicDate")
                for f in fields:
                    row[f] = rec.get(f)
    return out


def tai_gia(ma, bars=2500):
    body = {"timeFrame": "ONE_DAY", "symbols": [ma], "to": int(time.time()),
            "countBack": bars}
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
    return {k: x[k] for k in ("t", "o", "h", "l", "c", "v")}


def ro_ma():
    """112 ma cua ban quet moi nhat + cac ma trong tham_dinh.json + VNINDEX."""
    import glob
    scan = sorted(glob.glob(os.path.join("data", "scan_2*.json")))[-1]
    with open(scan, encoding="utf-8") as f:
        ma = [k for k in json.load(f) if not k.startswith("_")]
    with open(os.path.join("data", "tham_dinh.json"), encoding="utf-8") as f:
        ma += [k for k in json.load(f) if not k.startswith("_")]
    return sorted(set(ma) | {"VNINDEX"})


def tai_tat_ca(ds=None):
    os.makedirs(CACHE, exist_ok=True)
    tai_lai = os.environ.get("CANSLIM_TAI_LAI") == "1"
    loi = []
    for i, ma in enumerate(ds or ro_ma(), 1):
        for loai, ham in (("px", tai_gia), ("fin", tai_bctc)):
            if loai == "fin" and ma == "VNINDEX":
                continue
            p = os.path.join(CACHE, f"{ma}_{loai}.json")
            if os.path.exists(p) and not tai_lai:
                continue
            try:
                d = ham(ma)
                with open(p, "w", encoding="utf-8") as f:
                    json.dump(d, f)
            except Exception as e:
                loi.append((ma, loai, str(e)[:80]))
            time.sleep(0.3)
        print(f"{i:>3} {ma}", flush=True)
    if loi:
        print("LOI:", loi)
    return loi


# ------------------------------------------------------------------ Nap du lieu
def _cuoi_quy(nam, quy):
    thang = 3 * quy
    d = dt.date(nam + (thang == 12), 1 if thang == 12 else thang + 1, 1)
    return d - dt.timedelta(days=1)


def ngay_hieu_luc(nam, quy, public_date, la_nam=False):
    cq = _cuoi_quy(nam, 4 if la_nam else quy)
    if public_date:
        pd_ = dt.date.fromisoformat(public_date[:10])
        return max(pd_, cq + dt.timedelta(days=20))
    return cq + dt.timedelta(days=90 if (la_nam or quy == 4) else 45)


def nap_bctc(ma):
    """-> (quy, nam): list dict sap theo thoi gian, moi dict co 'hl' (ngay hieu luc)."""
    p = os.path.join(CACHE, f"{ma}_fin.json")
    if not os.path.exists(p):
        return [], []
    with open(p, encoding="utf-8") as f:
        d = json.load(f)
    quy, nam = [], []
    for kind, dst in (("quarters", quy), ("years", nam)):
        for r in d[kind].values():
            y, q = r["yearReport"], r["lengthReport"]
            if kind == "quarters" and q not in (1, 2, 3, 4):
                continue
            pds = [v for k, v in r.items() if k.startswith("pd_") and v]
            pub = max(pds) if pds else r.get("publicDate")
            r = dict(r, nam=y, quy=q if kind == "quarters" else 4,
                     hl=ngay_hieu_luc(y, q, pub, kind == "years"))
            dst.append(r)
        dst.sort(key=lambda r: (r["nam"], r["quy"]))
    return quy, nam


def nap_gia(ma):
    p = os.path.join(CACHE, f"{ma}_px.json")
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        d = json.load(f)
    if not d:
        return None
    d["d"] = [dt.datetime.fromtimestamp(int(t), dt.timezone.utc).date() for t in d["t"]]
    return d


if __name__ == "__main__":
    sys.exit(1 if tai_tat_ca(sys.argv[1:] or None) else 0)
