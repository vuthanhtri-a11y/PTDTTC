"""
vi_mo.py — Hai nguon vi mo:
  * Chuoi gia toan cau tu Yahoo (khong can khoa, da kiem 30/09/2026), tai khi bam
    quet hoac nut "Tai lai vi mo", cache o data/cache_dashboard/vi_mo_yahoo.json.
  * So lieu Viet Nam NHAP TAY trong data/vi_mo.json (CPI, PMI, tin dung...). App
    chi doc; dong nao nhap qua NGAY_CU ngay thi to vang.
"""

import json
from datetime import date, datetime

import pandas as pd

from dashboard.nguon import CACHE, VI_MO_FILE

NGAY_CU = 45
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"}
YAHOO = [
    ("BZ=F", "Dầu Brent", "USD/thùng", 2),
    ("CL=F", "Dầu WTI", "USD/thùng", 2),
    ("DX-Y.NYB", "Chỉ số USD (DXY)", "điểm", 2),
    ("USDVND=X", "USD/VND", "đồng", 0),
    ("GC=F", "Vàng", "USD/oz", 0),
    ("^TNX", "Lợi suất TPCP Mỹ 10 năm", "%", 2),
    ("^GSPC", "S&P 500", "điểm", 0),
]
CACHE_FILE = CACHE / "vi_mo_yahoo.json"


def tai_yahoo(range_="3y"):
    """Tai moi chuoi; loi chuoi nao ghi loi chuoi do, khong lam hong ca file."""
    import requests
    out = {"tai_luc": datetime.now().strftime("%Y-%m-%d %H:%M"), "chuoi": {}, "loi": {}}
    for ma, *_ in YAHOO:
        try:
            r = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{ma}",
                             params={"range": range_, "interval": "1d"}, headers=UA, timeout=30)
            r.raise_for_status()
            res = r.json()["chart"]["result"][0]
            t = res["timestamp"]
            c = res["indicators"]["quote"][0]["close"]
            pts = [(datetime.fromtimestamp(a).strftime("%Y-%m-%d"), b)
                   for a, b in zip(t, c) if b is not None]
            out["chuoi"][ma] = pts
        except Exception as e:      # mang loi / doi dinh dang -> giu chuoi khac
            out["loi"][ma] = str(e)[:160]
    if out["chuoi"]:
        CACHE.mkdir(parents=True, exist_ok=True)
        CACHE_FILE.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    return out


def doc_yahoo():
    if not CACHE_FILE.exists():
        return None
    return json.loads(CACHE_FILE.read_text(encoding="utf-8"))


def chuoi(raw, ma):
    pts = (raw or {}).get("chuoi", {}).get(ma)
    if not pts:
        return None
    s = pd.Series([p[1] for p in pts], index=pd.to_datetime([p[0] for p in pts]), name=ma)
    return s[~s.index.duplicated(keep="last")]


def tom_tat(s):
    """Gia tri cuoi + thay doi 1 phien / 1 thang / tu dau nam."""
    if s is None or len(s) < 2:
        return None
    cuoi, ngay = s.iloc[-1], s.index[-1]

    def tu(moc):
        truoc = s[s.index <= moc]
        return cuoi / truoc.iloc[-1] - 1 if len(truoc) else None
    return {"gia_tri": cuoi, "ngay": ngay, "r1": cuoi / s.iloc[-2] - 1,
            "r1m": tu(ngay - pd.DateOffset(months=1)),
            "ytd": tu(pd.Timestamp(ngay.year - 1, 12, 31))}


def la_ngay_cuoi_thang(ngay):
    """Ngay lam viec cuoi thang: hop dong Brent ky gan dao han/cuon (memory 30/09)."""
    ke = pd.Timestamp(ngay) + pd.offsets.BDay(1)
    return ke.month != pd.Timestamp(ngay).month


# ------------------------------------------------------------------ nhap tay
def doc_vi_mo_vn():
    if not VI_MO_FILE.exists():
        return None
    return json.loads(VI_MO_FILE.read_text(encoding="utf-8"))


def bang_vi_mo_vn(raw, hom_nay=None):
    """Mot dong moi chi so: ky gan nhat, gia tri, ky truoc, nguon, ngay nhap, so ngay tu khi nhap."""
    hom_nay = hom_nay or date.today()
    rows = []
    for khoa, v in (raw or {}).get("chi_so", {}).items():
        ds = sorted(v.get("chuoi") or [], key=lambda x: x.get("ky", ""))
        cuoi = ds[-1] if ds else {}
        truoc = ds[-2] if len(ds) > 1 else {}
        nhap = cuoi.get("ngay_nhap")
        tuoi = (hom_nay - date.fromisoformat(nhap)).days if nhap else None
        rows.append({
            "khoa": khoa, "Chỉ số": v.get("ten", khoa), "Đơn vị": v.get("don_vi", ""),
            "Kỳ": cuoi.get("ky"), "Giá trị": cuoi.get("gia_tri"),
            "Kỳ trước": truoc.get("gia_tri"), "Nguồn": cuoi.get("nguon") or v.get("nguon", ""),
            "Ngày nhập": nhap, "Số ngày từ khi nhập": tuoi,
            "Cũ": tuoi is None or tuoi > NGAY_CU,
        })
    return pd.DataFrame(rows)


def chuoi_vi_mo_vn(raw, khoa):
    v = (raw or {}).get("chi_so", {}).get(khoa) or {}
    ds = sorted(v.get("chuoi") or [], key=lambda x: x.get("ky", ""))
    if not ds:
        return None
    return pd.Series([x.get("gia_tri") for x in ds], index=[x.get("ky") for x in ds])
