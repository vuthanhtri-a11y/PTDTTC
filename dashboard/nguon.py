"""
nguon.py — Lop doc du lieu cua dashboard. CHI DOC: khong ghi file nao ma
lt_screener.py / lt_allocator.py doc.

Moi thu khoa theo NGAY DU LIEU (_meta.ngay_du_lieu), khong theo ten file: ban
quet chay thuong dat ten theo ngay chay (scan_20261004.json chua phien 02/10),
ban quet bu `--den` dat ten theo ngay du lieu. Hai file cung mot ngay du lieu ->
lay ban chay sau cung.

Chi nhan ban quet Vietcap (co _meta). Ban quet TradingView cu (112 ma HOSE,
khong co _meta) khong co ngay du lieu chac chan nen bo qua.
"""

import json
import os
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import lt_che_do    # noqa: E402
import lt_config    # noqa: E402
import lt_screener  # noqa: E402

DATA = ROOT / "data"
CACHE = DATA / "cache_dashboard"
VI_MO_FILE = DATA / "vi_mo.json"
TEN_FILE = re.compile(r"^scan_(\d{8})\.json$")
KE_HOACH = re.compile(r"^ke_hoach_(\d{8})\.txt$")

H_VIETCAP = {"User-Agent": "Mozilla/5.0", "Referer": "https://trading.vietcap.com.vn/",
             "Origin": "https://trading.vietcap.com.vn/"}
LIST_URL = "https://trading.vietcap.com.vn/api/price/symbols/getAll"


def ve_goc():
    """lt_*.py dung duong dan tuong doi 'data/...' -> phai chay tu goc repo."""
    os.chdir(ROOT)


# ------------------------------------------------------------------ phien
@dataclass(frozen=True)
class Phien:
    ngay: str          # ngay du lieu, ISO
    hau_to: str        # YYYYMMDD trong ten file
    scan: Path
    chay_luc: str

    def _canh(self, tien_to):
        p = DATA / f"{tien_to}_{self.hau_to}.json"
        return p if p.exists() else None

    @property
    def candidates(self):
        return self._canh("candidates")

    @property
    def file_che_do(self):
        return self._canh("che_do")


_META_CACHE = {}


def doc_meta(path):
    """_meta cua ban quet ma khong nap ca file vao dict (file ~1 MB)."""
    path = Path(path)
    k = (str(path), path.stat().st_mtime)
    if k not in _META_CACHE:
        txt = path.read_text(encoding="utf-8")
        i = txt.find('"_meta":')
        meta = None
        if i >= 0:
            meta, _ = json.JSONDecoder().raw_decode(txt, i + len('"_meta":'))
        _META_CACHE[k] = meta
    return _META_CACHE[k]


def danh_sach_phien():
    """Moi phien co ban quet Vietcap, xep tang dan theo ngay du lieu."""
    tot = {}
    for f in DATA.glob("scan_*.json"):
        m = TEN_FILE.match(f.name)
        if not m:
            continue
        meta = doc_meta(f)
        if not meta or not meta.get("ngay_du_lieu"):
            continue
        p = Phien(meta["ngay_du_lieu"], m.group(1), f, meta.get("chay_luc", ""))
        cu = tot.get(p.ngay)
        if cu is None or (p.chay_luc, p.hau_to) > (cu.chay_luc, cu.hau_to):
            tot[p.ngay] = p
    return sorted(tot.values(), key=lambda p: p.ngay)


def phien_truoc(ds, phien):
    i = [p.ngay for p in ds].index(phien.ngay)
    return ds[i - 1] if i > 0 else None


def phien_thieu(ds, ngay_giao_dich):
    """Phien giao dich (theo VN-Index) tu ban quet Vietcap dau tien ma chua co ban quet."""
    if not ds or not ngay_giao_dich:
        return []
    co = {p.ngay for p in ds}
    return [d for d in ngay_giao_dich if d >= ds[0].ngay and d not in co]


# ------------------------------------------------------------------ ban quet
@dataclass
class BanQuet:
    phien: Phien
    df: pd.DataFrame      # index = ma; cot FIELDS + san, icb, lech_ngay
    vnindex: dict         # dong VNINDEX theo FIELDS
    phu: dict             # _meta, _san, _icb, _vnindex


def doc_ban_quet(phien):
    scan, phu = lt_screener.load(str(phien.scan))
    vni = scan.pop("VNINDEX", None)
    df = pd.DataFrame.from_dict(scan, orient="index")
    df.index.name = "ma"
    df["san"] = pd.Series(phu.get("_san", {}))
    df["icb"] = pd.Series(phu.get("_icb", {}))
    lech = set(phu.get("_meta", {}).get("bar_cuoi_lech_ngay", []))
    # Quet hai tang (tu 31/10/2026): ma it thanh khoan chua toi luot lam moi thi mang nguyen
    # dong cua ban quet truoc; ngay du lieu cua dong do nam o _mang_sang.
    ms = phu.get("_mang_sang", {}) or {}
    df["mang_sang"] = pd.Series(ms).reindex(df.index)
    # Ma khong khop lenh o phien cuoi (hoac dong mang sang): chuoi 60 phien cua no ket thuc o
    # ngay khac VN-Index -> loai khoi moi phep tinh theo chuoi thoi gian va dem tang/giam.
    df["lech_ngay"] = df.index.isin(lech) | df.index.isin(list(ms))
    df["tov_ty"] = df["tov_ty"].astype(float)
    return BanQuet(phien, df.sort_index(), vni, phu)


def doc_candidates(phien):
    p = phien.candidates
    if p is None:
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def doc_che_do(phien, phu=None):
    """Che do do screener ghi; thieu file thi phat lai bang ham cua lt_che_do."""
    p = phien.file_che_do
    if p is not None:
        cd = json.loads(p.read_text(encoding="utf-8"))
        return cd if cd.get("che_do") else None
    return lt_che_do.tu_ban_quet(phu) if phu else None


def doc_tham_dinh():
    p = ROOT / lt_config.THAM_DINH_FILE
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def nap_ro():
    return lt_screener.nap_ro()


def hang_rao(phien):
    return lt_screener.canh_bao_hang_rao(str(phien.scan), nap_ro())


def doc_so_giao_dich():
    return json.loads((DATA / "so_giao_dich.json").read_text(encoding="utf-8"))


# ------------------------------------------------------------------ bang lenh
_NGAY_CD = re.compile(r"CHE DO THI TRUONG \((\d{4}-\d{2}-\d{2})\)")
_NGAY_CHAY = re.compile(r"^NGAY CHAY (\d{4}-\d{2}-\d{2}) — nhip (HANG NGAY|KY SOAT)")


def ngay_du_lieu_ke_hoach(f):
    """Ngay du lieu bang lenh dang chua (dong "CHE DO THI TRUONG (YYYY-MM-DD)"); None neu khong co."""
    m = _NGAY_CD.search(f.read_text(encoding="utf-8", errors="replace"))
    return m.group(1) if m else None


def danh_sach_ke_hoach():
    """{ngay du lieu: (path, ngay chay, nhip)} — ban chay sau cung cho moi ngay du lieu.

    Bang lenh allocator dat ten theo ngay chay; ngay du lieu doc tu dong "CHE DO
    THI TRUONG (YYYY-MM-DD)". Bang lenh cu (truoc 05/10) khong co dong do -> bo qua.
    """
    out = {}
    for f in DATA.glob("ke_hoach_*.txt"):
        if not KE_HOACH.match(f.name):
            continue
        txt = f.read_text(encoding="utf-8", errors="replace")
        m = _NGAY_CD.search(txt)
        h = _NGAY_CHAY.search(txt.splitlines()[0] if txt else "")
        if not m:
            continue
        chay = h.group(1) if h else ""
        cu = out.get(m.group(1))
        if cu is None or (chay, f.name) > (cu[1], cu[0].name):
            out[m.group(1)] = (f, chay, h.group(2) if h else "")
    return out


# ------------------------------------------------------------------ Vietcap
def danh_ba_ma():
    """{ma: {ten, san, icb}} tu cache; rong neu chua tai."""
    p = CACHE / "danh_sach_ma.json"
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8")).get("ma", {})


def tai_danh_ba_ma():
    import requests
    d = requests.get(LIST_URL, headers=H_VIETCAP, timeout=60).json()
    ma = {x["symbol"]: {"ten": x.get("organShortName") or x.get("organName") or "",
                        "ten_day_du": x.get("organName") or "",
                        "san": x.get("board"), "icb": x.get("icbCode2")}
          for x in d if x.get("type") == "STOCK"}
    CACHE.mkdir(parents=True, exist_ok=True)
    (CACHE / "danh_sach_ma.json").write_text(
        json.dumps({"tai_luc": datetime.now().strftime("%Y-%m-%d %H:%M"), "ma": ma},
                   ensure_ascii=False), encoding="utf-8")
    return ma


def lich_su_gia(ma, den=None):
    """DataFrame ngay/o/h/l/c/v (~620 phien, gia DA DIEU CHINH co tuc) tu Vietcap.

    `den` = ngay du lieu ISO: chot nhu cuoi phien do va cache ra dia (bat bien
    trong ngay). None = du lieu song, bo phien dang chay truoc 15:00.
    """
    from lt_scan_vietcap import cat_phien_dang_chay, tai_bar
    cache = CACHE / "gia" / f"{ma}_{den}.json" if den else None
    if cache is not None and cache.exists():
        b = json.loads(cache.read_text(encoding="utf-8"))
    else:
        if den:
            to_ts = int(datetime.strptime(den, "%Y-%m-%d").timestamp()) + 23 * 3600
        else:
            to_ts = int(time.time())
        b = cat_phien_dang_chay(tai_bar(ma, to_ts), den) or []
        if den:
            b = [x for x in b if x[0] <= den]
        if cache is not None and b:
            cache.parent.mkdir(parents=True, exist_ok=True)
            cache.write_text(json.dumps(b), encoding="utf-8")
    df = pd.DataFrame(b, columns=["ngay", "o", "h", "l", "c", "v"])
    return df


def ngay_giao_dich_vnindex():
    """Ngay cac phien VN-Index da dong cua (du lieu song). None neu loi mang."""
    try:
        df = lich_su_gia("VNINDEX")
    except Exception:
        return None
    return list(df["ngay"]) if len(df) else None
