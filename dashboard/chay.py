"""
chay.py — Chay chuoi quet cuoi ngay cho nut trong dashboard (hoac tay tu dong lenh).

  python -m dashboard.chay hom_nay            # quet -> screener -> allocator hang_ngay -> vi mo
  python -m dashboard.chay bu 2026-10-05 ...  # quet --den + screener tung phien thieu (KHONG allocator)
  python -m dashboard.chay vi_mo              # chi tai lai chuoi vi mo
  python -m dashboard.chay day                # commit file pipeline moi cua data/ va push len main

Khong sua lt_*.py: moi buoc goi dung script/ham co san.

TEN FILE THEO NGAY DU LIEU. Ban quet tu dashboard ghi ra data/scan_<ngay du lieu>.json
(lt_scan_vietcap.py --ra), khong theo ngay chay nhu quy uoc cu (scan_20261004.json chua
phien 02/10). Ly do: ban quet bu `--den D` cung ghi scan_<D>.json, nen dat theo ngay
chay se de len nhau. KHONG BAO GIO ghi de mot file dang chua phien khac — phien do
bao "khong bu duoc" (vd 01/10: scan_20261001.json dang chua phien 30/09).

Screener va allocator luon chon file MOI NHAT theo ten (newest), nen ca hai chay
trong tien trinh con co `newest` tro thang vao file cua phien can chay. NGAY_CHAY:
hom nay cho nhip hang ngay (han phieu, phieu lenh xet theo ngay chay), ngay du lieu
cho phien bu. Bang lenh allocator ghi data/ke_hoach_<ngay chay>.txt nhu quy uoc cu.

Bao luu: phien bu tinh pheu bang tham_dinh.json VA HOLDINGS HIEN TAI, khong phai
trang thai cua ngay do.

DAY LEN GITHUB (`day`): ban Streamlit Cloud chi doc, so lieu len cloud bang cach commit
DUNG cac file pipeline moi (scan_/candidates_/che_do_ .json, ke_hoach_ .txt,
bao_cao_dau_tu_ .xlsx — 8 chu so ngay) roi push len nhanh cloud theo doi (mac dinh
main, doi bang bien moi truong DASHBOARD_NHANH). So giao dich, tham_dinh, lt_config,
vi_mo.json KHONG bao gio duoc commit tu nut nay — nhung file do la quyet dinh cua nguoi.
Chi push khi la fast-forward: nhanh local phai chua origin/<nhanh>.
"""

import os
import re
import subprocess
import sys
import time
from datetime import datetime

from dashboard.nguon import CACHE, DATA, ROOT, doc_meta, lich_su_gia, tai_danh_ba_ma

KHOA = CACHE / "dang_chay.lock"
KHOA_HET_HAN = 30 * 60          # khoa cu hon 30 phut coi nhu tien trinh da chet
NHANH_DAY = os.environ.get("DASHBOARD_NHANH", "main")
FILE_PIPELINE = re.compile(r"^data/((scan|candidates|che_do)_\d{8}\.json|ke_hoach_\d{8}\.txt|"
                           r"bao_cao_dau_tu_\d{8}\.xlsx)$")


def _env(**kw):
    e = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUNBUFFERED="1")
    e.update({k: v for k, v in kw.items() if v is not None})
    return e


def _chay(cmd, env=None, ra=None):
    """Chay lenh, day tung dong ra stdout (dashboard doc truc tiep). Tra ve (ma loi, toan van)."""
    print(f"$ {' '.join(cmd)}", flush=True)
    p = subprocess.Popen(cmd, cwd=ROOT, env=env or _env(), stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, text=True, encoding="utf-8",
                         errors="replace")
    dong = []
    for x in p.stdout:
        dong.append(x)
        print(x, end="", flush=True)
    p.wait()
    txt = "".join(dong)
    if ra is not None:
        ra.write_text(txt, encoding="utf-8")
    if p.returncode:
        print(f"!! loi {p.returncode}: {' '.join(cmd)}", flush=True)
    return p.returncode, txt


def chay_screener(scan_path, ngay):
    """Screener tren DUNG mot ban quet (tien trinh con, de sys.exit khong giet cha)."""
    ma = ("import sys, lt_screener as s; sys.stdout.reconfigure(encoding='utf-8'); "
          f"s.newest = lambda p: {str(scan_path)!r}; s.main()")
    return _chay([sys.executable, "-c", ma], env=_env(NGAY_CHAY=ngay))


def chay_allocator(cand_path, ngay_chay):
    """Allocator nhip hang ngay tren DUNG file candidates; ghi bang lenh nhu quy uoc cu."""
    ma = ("import sys, lt_allocator as a; sys.stdout.reconfigure(encoding='utf-8'); "
          f"a.newest = lambda p: {str(cand_path)!r}; a.main(); a.in_lenh_ngoai_luat(); "
          "a.in_lenh_quy_tac_5()")
    return _chay([sys.executable, "-c", ma], env=_env(NGAY_CHAY=ngay_chay, LOAI_KY="hang_ngay"),
                 ra=DATA / f"ke_hoach_{ngay_chay.replace('-', '')}.txt")


def file_quet(ngay):
    return DATA / f"scan_{ngay.replace('-', '')}.json"


def ten_bi_chiem(ngay):
    """Ngay du lieu dang nam trong scan_<ngay>.json neu file do chua phien KHAC; None neu trong/khop."""
    f = file_quet(ngay)
    if not f.exists():
        return None
    try:
        d = (doc_meta(f) or {}).get("ngay_du_lieu")
    except Exception:
        d = "?"
    return None if d == ngay else (d or "?")


def phien_moi_nhat():
    """Ngay phien VN-Index moi nhat da dong cua (bo phien dang chay truoc 15:00)."""
    g = lich_su_gia("VNINDEX")
    return g["ngay"].iloc[-1] if len(g) else None


def hom_nay():
    ngay_chay = datetime.now().strftime("%Y-%m-%d")
    d = phien_moi_nhat()
    if not d:
        print("Khong lay duoc phien moi nhat cua VN-Index (mang?).", flush=True)
        return 1
    chiem = ten_bi_chiem(d)
    if chiem:
        print(f"!! {file_quet(d).name} dang chua phien {chiem} — khong ghi de. Dung.", flush=True)
        return 1
    scan = file_quet(d)
    print(f"Phien du lieu: {d} -> {scan.name}", flush=True)
    rc, _ = _chay([sys.executable, "lt_scan_vietcap.py", "--ra", str(scan)])
    if rc or not scan.exists():
        return rc or 1
    that = (doc_meta(scan) or {}).get("ngay_du_lieu")
    if that != d:      # phien vua dong cua trong luc quet -> dat lai ten theo du lieu that
        dich = file_quet(that)
        if ten_bi_chiem(that) or dich.exists():
            print(f"!! ban quet ra phien {that}, khac {d}; {dich.name} da co — giu {scan.name}.",
                  flush=True)
        else:
            scan.rename(dich)
            scan = dich
    rc, _ = chay_screener(scan, ngay_chay)
    if rc:
        return rc
    cand = DATA / scan.name.replace("scan_", "candidates_")
    rc, _ = chay_allocator(cand, ngay_chay)
    if rc:
        return rc
    vi_mo()
    try:
        tai_danh_ba_ma()
        print("Danh ba ma (ten cong ty) da cap nhat.", flush=True)
    except Exception as e:
        print(f"[bo qua] khong tai duoc danh ba ma: {e}", flush=True)
    return 0


def bu(cac_ngay):
    loi = 0
    for ngay in cac_ngay:
        print(f"\n===== Quet bu phien {ngay} =====", flush=True)
        chiem = ten_bi_chiem(ngay)
        if chiem:
            print(f"!! {file_quet(ngay).name} dang chua phien {chiem} (quy uoc ten cu theo ngay chay)"
                  " — khong ghi de, bo qua phien nay.", flush=True)
            loi = loi or 4
            continue
        scan = file_quet(ngay)
        rc, _ = _chay([sys.executable, "lt_scan_vietcap.py", "--den", ngay, "--ra", str(scan)])
        if rc or not scan.exists():
            loi = rc or 1
            continue
        rc, _ = chay_screener(scan, ngay)
        loi = loi or rc
    return loi


def vi_mo():
    from dashboard.vi_mo import YAHOO, tai_yahoo
    print("Tai chuoi vi mo (Yahoo)...", flush=True)
    out = tai_yahoo()
    print(f"  {len(out['chuoi'])}/{len(YAHOO)} chuoi"
          + (f"; loi: {', '.join(out['loi'])}" if out["loi"] else ""), flush=True)
    return 0


def loc_file_pipeline(porcelain):
    """Tu `git status --porcelain` lay ra file pipeline moi/sua trong data/ — khong gi khac."""
    out = []
    for dong in porcelain.splitlines():
        p = dong[3:].strip().strip('"')
        if " -> " in p:
            p = p.split(" -> ", 1)[1].strip('"')
        if FILE_PIPELINE.match(p):
            out.append(p)
    return sorted(set(out))


def file_cho_day():
    """File pipeline chua commit. Loi git (khong phai repo, khong co git) -> rong."""
    try:
        r = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all", "--", "data"],
                           cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=30)
    except Exception:
        return []
    return loc_file_pipeline(r.stdout) if r.returncode == 0 else []


def day_github(nhanh=NHANH_DAY):
    files = file_cho_day()
    if not files:
        print("Khong co file pipeline moi trong data/ — khong co gi de day.", flush=True)
        return 0
    print(f"{len(files)} file se commit:\n  " + "\n  ".join(files), flush=True)
    rc, _ = _chay(["git", "fetch", "origin", nhanh])
    if rc:
        return rc
    r = subprocess.run(["git", "merge-base", "--is-ancestor", f"origin/{nhanh}", "HEAD"], cwd=ROOT)
    if r.returncode != 0:
        print(f"!! GitHub ({nhanh}) co commit ma may nay chua co — chay `git pull` truoc roi bam lai."
              " Khong push de khong ghi de.", flush=True)
        return 5
    ngay = sorted({re.search(r"_(\d{8})\.", f).group(1) for f in files})
    nhan = ", ".join(f"{d[6:]}/{d[4:6]}" for d in ngay)
    rc, _ = _chay(["git", "add", "--", *files])
    if rc:
        return rc
    rc, _ = _chay(["git", "commit", "-m", f"Du lieu quet {nhan} (dashboard)", "--", *files])
    if rc:
        return rc
    rc, _ = _chay(["git", "push", "origin", f"HEAD:{nhanh}"])
    if rc == 0:
        print(f"Da day len {nhanh}. Streamlit Cloud tu cap nhat sau khoang mot phut.", flush=True)
    return rc


def dang_chay():
    return KHOA.exists() and time.time() - KHOA.stat().st_mtime < KHOA_HET_HAN


def main(argv):
    if not argv or argv[0] not in ("hom_nay", "bu", "vi_mo", "day"):
        print(__doc__)
        return 2
    os.chdir(ROOT)
    CACHE.mkdir(parents=True, exist_ok=True)
    if argv[0] != "vi_mo":
        if dang_chay():
            print("Dang co mot lan quet khac chay (data/cache_dashboard/dang_chay.lock).")
            return 3
        KHOA.write_text(f"{os.getpid()} {datetime.now():%Y-%m-%d %H:%M:%S}", encoding="utf-8")
    t0 = time.time()
    try:
        if argv[0] == "hom_nay":
            rc = hom_nay()
        elif argv[0] == "bu":
            rc = bu(argv[1:])
        elif argv[0] == "day":
            rc = day_github()
        else:
            rc = vi_mo()
    finally:
        if argv[0] != "vi_mo":
            KHOA.unlink(missing_ok=True)
    print(f"\n{'XONG' if rc == 0 else 'CO LOI'} sau {time.time() - t0:.0f} giay.", flush=True)
    return rc


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
