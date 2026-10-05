"""
kiem_dinh_che_do_vnindex.py — Do lop che do thi truong (Tru 1) tren CHINH VNINDEX.

Lap 04/10/2026 (CHIEN_LUOC_DAI_HAN.md muc 14.4) de THAY dong "chay lai trong hon
12 nam, lop nay cat sut giam toi da cua he thong tu 54% xuong 37%; CAGR 6,3% ->
5,7%" o tr.72 bao cao giai doan 1 — dong do khong co file, script hay du lieu
nao dung sau (muc 12.1, quyet dinh 1).

Pham vi — doc dung:
  * Do tren VNINDEX (chi so gia, KHONG gom co tuc), KHONG phai he thong chon ma
    cua Quy. Tra loi: neu nam chi so theo tran ty trong cua tung che do thi sut
    giam va tang truong doi the nao.
  * Goi lt_che_do.chuoi_che_do() — dung ham dang chay — nen con so do DUNG luat
    da chot, khong phai mot ban viet lai.
  * Tin hieu o gia dong cua phien s, dat lenh phien s+1, huong loi tu dong cua
    s+1. Phi 0,2% moi lan doi ty trong (tren phan doi). Tien mat lai 0%.
  * Mot duong gia, mot thi truong, KHONG dang ky truoc: la bang chung tham khao.

Chay:
  PYTHONIOENCODING=utf-8 python kiem_dinh_che_do_vnindex.py            # dung du lieu da luu
  PYTHONIOENCODING=utf-8 python kiem_dinh_che_do_vnindex.py --tai-lai  # tai lai tu Vietcap
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from statistics import median

from lt_config import CHE_DO
from lt_che_do import chuoi_che_do

DU_LIEU = "data/vnindex_vietcap_20261002.json"
KET_QUA = "data/kiem_dinh_che_do_vnindex_20261004.json"
PHI_DOI = 0.002
CUA_SO = {"12 nam (10/2014-10/2026)": "2014-10-01", "toan bo (tu khi co MA200)": None}


def tai_vnindex():
    import requests
    H = {"Referer": "https://trading.vietcap.com.vn/", "Origin": "https://trading.vietcap.com.vn",
         "User-Agent": "Mozilla/5.0"}
    x = requests.post("https://trading.vietcap.com.vn/api/chart/OHLCChart/gap-chart", headers=H,
                      json={"timeFrame": "ONE_DAY", "symbols": ["VNINDEX"],
                            "to": int(time.time()), "countBack": 6000}, timeout=60).json()[0]
    t = [datetime.fromtimestamp(int(a)).strftime("%Y-%m-%d") for a in x["t"]]
    return {"nguon": "Vietcap gap-chart ONE_DAY VNINDEX", "tai_luc": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "t": t, "c": [float(a) for a in x["c"]], "v": [float(a or 0) for a in x["v"]]}


def bien_the():
    """Cac bien the: ten -> (cfg che do, ham ty trong theo trang thai)."""
    doi_xung = dict(CHE_DO, nguong_ra_giam=CHE_DO["nguong_vao_giam"])
    tran = CHE_DO["tran_co_phieu"]
    return {
        "Mua va giu VNINDEX": (None, lambda s: 1.0),
        "Luat dang chay: tran 100/60/0, do tre": (CHE_DO, lambda s: tran[s]),
        "Chi lop GIAM (100/0), do tre": (CHE_DO, lambda s: 0.0 if s == "GIAM" else 1.0),
        "Chi lop GIAM (100/0), doi xung": (doi_xung, lambda s: 0.0 if s == "GIAM" else 1.0),
    }


def do(t, c, st, w_of, tu):
    """CAGR, sut giam toi da, ty trong TB, so lan doi trang thai GIAM trong cua so."""
    i0 = next(i for i in range(len(t)) if st[i] is not None and (tu is None or t[i] >= tu))
    w = [w_of(s) if s is not None else 1.0 for s in st]
    eq, dinh, mdd, prev, tong_w = 1.0, 1.0, 0.0, w[i0 - 1], 0.0
    for i in range(i0 + 1, len(c)):
        wi = w[i - 2]                    # tin hieu s = i-2, khop s+1 = i-1, huong tu i-1 -> i
        eq *= 1 + wi * (c[i] / c[i - 1] - 1)
        if wi != prev:
            eq *= 1 - PHI_DOI * abs(wi - prev)
            prev = wi
        tong_w += wi
        dinh = max(dinh, eq)
        mdd = min(mdd, eq / dinh - 1)
    nam = (datetime.strptime(t[-1], "%Y-%m-%d") - datetime.strptime(t[i0], "%Y-%m-%d")).days / 365.25
    dot, s0 = [], None
    for i in range(i0, len(st)):
        if st[i] == "GIAM" and s0 is None:
            s0 = i
        if st[i] != "GIAM" and s0 is not None:
            dot.append(i - s0)
            s0 = None
    if s0 is not None:
        dot.append(len(st) - s0)
    return {"tu": t[i0], "den": t[-1], "cagr": round(eq ** (1 / nam) - 1, 4),
            "sut_giam_toi_da": round(mdd, 4), "ty_trong_tb": round(tong_w / (len(c) - i0 - 1), 3),
            "so_lan_vao_giam": len(dot), "giam_ngan_duoi_10_phien": sum(1 for d in dot if d < 10),
            "trung_vi_phien_giam": median(dot) if dot else 0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tai-lai", action="store_true")
    a = ap.parse_args()
    if a.tai_lai or not os.path.exists(DU_LIEU):
        d = tai_vnindex()
        json.dump(d, open(DU_LIEU, "w", encoding="utf-8"), separators=(",", ":"))
    d = json.load(open(DU_LIEU, encoding="utf-8"))
    t, c, v = d["t"], d["c"], d["v"]
    print(f"VNINDEX {t[0]} -> {t[-1]} ({len(c)} phien), nguon {d['nguon']}, tai {d['tai_luc']}")
    print(f"Tin hieu dong cua s, khop s+1; phi {PHI_DOI:.1%}/lan doi; tien mat lai 0%; "
          "chi so gia (khong co tuc)\n")
    out = {"_ghi_chu": __doc__.strip().splitlines()[0], "du_lieu": DU_LIEU,
           "luat": CHE_DO, "phi_doi": PHI_DOI, "ket_qua": {}}
    for ten_cs, tu in CUA_SO.items():
        print(f"== {ten_cs}")
        print(f"  {'Bien the':<40} {'CAGR':>7} {'Sut giam':>9} {'TT TB':>6} "
              f"{'Vao GIAM':>9} {'<10 phien':>10} {'Trung vi':>9}")
        out["ket_qua"][ten_cs] = {}
        for ten, (cfg, w_of) in bien_the().items():
            st = chuoi_che_do(c, v, cfg or CHE_DO)
            r = do(t, c, st, w_of, tu)
            if cfg is None:
                r.update(so_lan_vao_giam=None, giam_ngan_duoi_10_phien=None, trung_vi_phien_giam=None)
            out["ket_qua"][ten_cs][ten] = r
            f = (lambda x: "-" if x is None else str(x))
            print(f"  {ten:<40} {r['cagr']*100:>6.1f}% {r['sut_giam_toi_da']*100:>8.1f}% "
                  f"{r['ty_trong_tb']:>6.2f} {f(r['so_lan_vao_giam']):>9} "
                  f"{f(r['giam_ngan_duoi_10_phien']):>10} {f(r['trung_vi_phien_giam']):>9}")
        print()
    json.dump(out, open(KET_QUA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"-> {KET_QUA}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
