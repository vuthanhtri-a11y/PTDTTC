"""Buong lai van hanh cua Quy — dashboard Streamlit chi doc (chot 07/10/2026).

Doc dau ra cua chuoi lt_scan_vietcap.py -> lt_screener.py -> lt_allocator.py
trong data/. Khong viet lai luat: che do, pheu va lenh lay tu file pipeline ghi
ra, hoac goi lai ham co san cua lt_*.py.
"""

import os
import time

# Gio Viet Nam cho moi datetime.now(): container / Streamlit Cloud chay UTC nen luat "truoc 15:00 bo
# phien dang chay" (lt_scan_vietcap.cat_phien_dang_chay), ngay chay va canh bao 15:00 lech 7 gio.
# Chuoi POSIX (UTC+7, khong DST) khong can tzdata; tien trinh con (dashboard.chay, lt_*.py) thua huong
# qua os.environ. Windows bo qua: may cua Quy o gio VN, va CRT khong doc chuoi nay.
if os.name != "nt":
    os.environ["TZ"] = "<+07>-7"
    time.tzset()
