"""
lt_che_do.py — Tru 1: che do thi truong (chot 04/10/2026, CHIEN_LUOC_DAI_HAN.md muc 14).

Mot nguon duy nhat cho luat che do: lt_screener.py (ky soat), kiem nhanh hang
ngay (chay file nay) va phep do tren VNINDEX (kiem_dinh_che_do_vnindex.py) cung
goi chuoi_che_do() — de con so bao cao do DUNG luat dang chay.

Luat (CHE_DO trong lt_config.py):
  * GIAM khi dong cua < 0,97 x MA200 (tinh lai moi phien). Chi RA khi dong cua
    > MA200 (do tre). Trong luc GIAM: ban toan bo, khoa mua moi.
  * Ngoai GIAM, tren MA200: TANG neu MA50 > MA200 va phien phan phoi < 5, nguoc
    lai DIEU_CHINH. Vung 0,97-1,00 x MA200: giu trang thai truoc, chi duoc xau di.
  * Tran ty trong co phieu: TANG 100%, DIEU_CHINH 60%, GIAM 0%.

Chay (kiem nhanh moi phien, du lieu song tu Vietcap):
  PYTHONIOENCODING=utf-8 python lt_che_do.py
"""

import json
import os
import sys
from datetime import datetime

from lt_config import CHE_DO, HOLDINGS, EXIT, THAM_DINH_FILE

TRANG_THAI = ("TANG", "DIEU_CHINH", "GIAM")


def _tong_tich_luy(c):
    cs = [0.0]
    for x in c:
        cs.append(cs[-1] + x)
    return cs


def phien_phan_phoi(c, v, i, cfg=CHE_DO):
    """Chi so cac phien phan phoi trong cua so ket thuc o i (ke ca i).

    Phien phan phoi (O'Neil): dong cua giam >= giam_toi_thieu so voi phien truoc
    VA khoi luong cao hon phien truoc.
    """
    p = cfg["phan_phoi"]
    out = []
    for j in range(max(1, i - p["cua_so"] + 1), i + 1):
        if c[j] <= c[j - 1] * (1 - p["giam_toi_thieu"]) and v[j] > v[j - 1]:
            out.append(j)
    return out


def chuoi_che_do(c, v, cfg=CHE_DO):
    """Trang thai tung phien (None khi chua du 200 phien de tinh MA200).

    Phat lai tu dau chuoi: do tre lam trang thai hom nay phu thuoc duong di, nen
    khong tinh duoc tu mot ngay don le.
    """
    n = len(c)
    cs = _tong_tich_luy(c)
    vao, ra = cfg["nguong_vao_giam"], cfg["nguong_ra_giam"]
    nguong_pp = cfg["phan_phoi"]["nguong_dieu_chinh"]
    out, prev = [None] * n, None
    for i in range(199, n):
        m200 = (cs[i + 1] - cs[i - 199]) / 200
        m50 = (cs[i + 1] - cs[i - 49]) / 50
        xau = m50 < m200 or len(phien_phan_phoi(c, v, i, cfg)) >= nguong_pp
        if prev == "GIAM":
            st = "GIAM" if not c[i] > ra * m200 else ("DIEU_CHINH" if xau else "TANG")
        elif c[i] < vao * m200:
            st = "GIAM"
        elif c[i] > ra * m200:
            st = "DIEU_CHINH" if xau else "TANG"
        else:                                    # vung 0,97-1,00 x MA200
            st = "TANG" if prev == "TANG" and not xau else "DIEU_CHINH"
        out[i] = st
        prev = st
    return out


def tinh_che_do(ngay, c, v, cfg=CHE_DO):
    """Che do cua phien cuoi chuoi, kem so lieu de in va de ghi so.

    Tra ve None neu chuoi chua du 200 phien.
    """
    n = len(c)
    if n < 200:
        return None
    st = chuoi_che_do(c, v, cfg)
    cs = _tong_tich_luy(c)
    m200 = (cs[n] - cs[n - 200]) / 200
    m50 = (cs[n] - cs[n - 50]) / 50
    pp = phien_phan_phoi(c, v, n - 1, cfg)
    doi = [(ngay[i], st[i - 1], st[i]) for i in range(200, n) if st[i] != st[i - 1]]
    tu = next((i for i in range(n - 1, 199, -1) if st[i - 1] != st[i]), 199)
    return {
        "ngay": ngay[-1], "che_do": st[-1],
        "dong_cua": round(c[-1], 2), "ma50": round(m50, 2), "ma200": round(m200, 2),
        "nguong_vao_giam": round(cfg["nguong_vao_giam"] * m200, 2),
        "nguong_ra_giam": round(cfg["nguong_ra_giam"] * m200, 2),
        "phien_phan_phoi": len(pp), "ngay_phan_phoi": [ngay[j] for j in pp],
        "tran_co_phieu": cfg["tran_co_phieu"][st[-1]],
        "tu_ngay": ngay[tu], "so_phien": n - tu,
        "doi_gan_nhat": doi[-8:],
    }


def tu_ban_quet(phu, cfg=CHE_DO):
    """Che do tu khoi `_vnindex` cua ban quet (lt_scan_vietcap.py tu 04/10/2026).

    Ban quet cu khong co khoi nay -> None = KHONG XAC DINH: allocator khong mua,
    khong ban ep — phai quet lai.
    """
    x = phu.get("_vnindex")
    if not x:
        return None
    return tinh_che_do(x["t"], x["c"], x["v"], cfg)


def in_che_do(cd):
    if cd is None:
        print("CHE DO THI TRUONG: KHONG XAC DINH — ban quet thieu chuoi VNINDEX "
              "(_vnindex). Quet lai bang lt_scan_vietcap.py. Allocator: khong mua, "
              "khong ban ep.")
        return
    print(f"CHE DO THI TRUONG ({cd['ngay']}): {cd['che_do']}  — tran co phieu "
          f"{cd['tran_co_phieu']:.0%}  (tu {cd['tu_ngay']}, {cd['so_phien']} phien)")
    print(f"  VNINDEX {cd['dong_cua']:,.2f} | MA50 {cd['ma50']:,.2f} | MA200 "
          f"{cd['ma200']:,.2f} | vao GIAM < {cd['nguong_vao_giam']:,.2f} | ra GIAM > "
          f"{cd['nguong_ra_giam']:,.2f} | phien phan phoi {cd['phien_phan_phoi']}/"
          f"{CHE_DO['phan_phoi']['cua_so']}")
    if cd["che_do"] == "GIAM":
        print(f"  => BAN TOAN BO, KHOA MUA MOI. Ra khi VNINDEX dong cua > "
              f"{cd['nguong_ra_giam']:,.2f} (+{cd['nguong_ra_giam']/cd['dong_cua']-1:.1%}).")


def _co_so(ma):
    """Gia tri co so (dong/CP) cua ma trong THAM_DINH_FILE, None neu chua co."""
    if not os.path.exists(THAM_DINH_FILE):
        return None
    v = json.load(open(THAM_DINH_FILE, encoding="utf-8")).get(ma) or {}
    cs = (v.get("dinh_gia") or {}).get("co_so")
    return None if cs is None else cs * 1000


def main():
    """Kiem nhanh MOI PHIEN: che do + ba luat ban xet hang ngay cho ma dang giu.

    Chi BAO, khong sinh bang lenh. Co tin hieu -> ghi PHIEU_LENH roi dat lenh
    phien sau (hoac quet lai + LOAI_KY=hang_ngay python lt_allocator.py).
    """
    from lt_scan_vietcap import tai_bar, cat_phien_dang_chay
    import time

    b = cat_phien_dang_chay(tai_bar("VNINDEX", int(time.time())), None)
    cd = tinh_che_do([x[0] for x in b], [x[4] for x in b], [x[5] for x in b])
    in_che_do(cd)
    print("\nVI THE DANG GIU — luat xet moi phien "
          f"({', '.join(EXIT['xet_hang_ngay'])}; quy tac 4 do nguoi danh):")
    for pk, ds in HOLDINGS.items():
        for ma, kl, gv in ds:
            bb = cat_phien_dang_chay(tai_bar(ma, int(time.time())), None)
            g, ngay = bb[-1][4], bb[-1][0]
            cs = _co_so(ma)
            co = []
            if cd and cd["che_do"] == "GIAM":
                co.append("CHE DO GIAM")
            if gv and g <= gv * (1 - EXIT["stop_tham_hoa"]):
                co.append("CHAN CUNG -25%")
            if cs is not None and g >= cs:
                co.append(f"CHAM CO SO {cs:,.0f}")
            print(f"  {pk} {ma:<5} {kl:>6,} CP  gia {g:>9,.0f} ({ngay})  von {gv:>8,.0f}  "
                  f"co so {'?' if cs is None else f'{cs:,.0f}':>8}  -> "
                  + ("BAN: " + ", ".join(co) if co else "giu"))
    print("\nCo tin hieu BAN -> ghi PHIEU_LENH trong lt_config.py TRUOC gio dat.")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
