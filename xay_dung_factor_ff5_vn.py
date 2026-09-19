# -*- coding: utf-8 -*-
"""
================================================================================
 XÂY DỰNG 5 NHÂN TỐ FAMA–FRENCH CHO THỊ TRƯỜNG CHỨNG KHOÁN VIỆT NAM
 Giai đoạn 2010–2026 · Chạy trên máy có kết nối mạng (vnstock)
================================================================================

 Bản quyền: viết cho Quỹ Medici — PTĐTTC 2026.
 Bản chạy được, không phải mã giả. Cách dùng:

     pip install vnstock pandas numpy openpyxl
     python xay_dung_factor_ff5_vn.py --tu 2010 --den 2026 --out factor_vn.xlsx

 CẢNH BÁO QUAN TRỌNG VỀ THIÊN LỆCH NGƯỜI SỐNG SÓT
 -------------------------------------------------
 Nếu lấy danh sách mã bằng API "các mã đang niêm yết hôm nay" rồi chạy ngược về
 2010, mọi doanh nghiệp đã huỷ niêm yết (phá sản, bị mua lại, chuyển sàn) đều
 biến mất khỏi mẫu. Kết quả: phần bù nhân tố bị thổi phồng có hệ thống, đặc biệt
 là SMB — vì cổ phiếu nhỏ chết nhiều nhất. Muốn làm đúng, phải dựng danh sách
 niêm yết theo từng năm từ dữ liệu lịch sử của HOSE/HNX, hoặc ít nhất ghi rõ
 rằng bộ nhân tố có thiên lệch này và ước lượng cận trên của nó.

================================================================================
 ĐỊNH NGHĨA TỪNG NHÂN TỐ (Fama & French 2015, bản 2×3, áp cho Việt Nam)
================================================================================

 Quy ước ký hiệu:
   ME(i,t)   vốn hoá thị trường của mã i cuối tháng t   = giá × SLCP lưu hành
   BE(i,y)   vốn chủ sở hữu sổ sách của mã i, năm tài chính y (31/12)
   OP(i,y)   lợi nhuận hoạt động: doanh thu thuần − giá vốn − chi phí lãi vay
                                  − chi phí bán hàng & quản lý
   AT(i,y)   tổng tài sản cuối năm tài chính y
   R(i,t)    tỷ suất sinh lời tháng t, đã điều chỉnh cổ tức và chia tách

 ----------------------------------------------------------------------------
 (0) TSSL và lãi suất phi rủi ro
 ----------------------------------------------------------------------------
   R(i,t) = P_adj(i,t) / P_adj(i,t−1) − 1        P_adj = giá đã điều chỉnh
   Rf(t)  = lợi suất TPCP kỳ hạn 1 năm (hoặc lãi suất liên ngân hàng qua đêm
            bình quân tháng), quy về tháng:  Rf_thang = (1 + y_nam)^(1/12) − 1
   → LUÔN quy đổi bằng luỹ thừa, không chia 12. Chia 12 sai ~2% giá trị mỗi năm
     ở mức lãi suất Việt Nam.

 ----------------------------------------------------------------------------
 (1) MKT — nhân tố thị trường
 ----------------------------------------------------------------------------
   MKT(t) = Σ_i w(i,t−1)·R(i,t) − Rf(t)
   w(i,t−1) = ME(i,t−1) / Σ_j ME(j,t−1)          ← trọng số vốn hoá ĐẦU kỳ

   Không dùng VN-Index thay cho vế đầu: VN-Index bỏ HNX/UPCoM và có cách xử lý
   cổ phiếu mới niêm yết riêng. Nếu buộc phải dùng, ghi rõ đó là xấp xỉ.

 ----------------------------------------------------------------------------
 (2) Sáu rổ cho SMB & HML — phân loại vào cuối tháng 6 mỗi năm
 ----------------------------------------------------------------------------
   Trục quy mô  (2 nhóm): S / B, cắt tại TRUNG VỊ vốn hoá cuối tháng 6 năm y
   Trục giá trị (3 nhóm): H / M / L, cắt tại phân vị 30% và 70% của
        BM(i) = BE(i, y−1) / ME(i, cuối tháng 12 năm y−1)

   → 6 rổ: SH SM SL BH BM BL, mỗi rổ tính TSSL theo trọng số vốn hoá,
     giữ nguyên thành phần từ tháng 7 năm y đến tháng 6 năm y+1.

   SMB_BM = (SH + SM + SL)/3 − (BH + BM + BL)/3
   HML    = (SH + BH)/2 − (SL + BL)/2

   Vì sao trễ 6 tháng: BCTC năm y−1 công bố chậm nhất 31/3 năm y (thông tư
   96/2020/TT-BTC với DN phải kiểm toán). Phân loại vào 30/6 bảo đảm mọi nhà đầu
   tư đều đã có thông tin — nếu không, nhân tố chứa look-ahead bias.

 ----------------------------------------------------------------------------
 (3) Sáu rổ cho RMW
 ----------------------------------------------------------------------------
   OP_BE(i) = OP(i, y−1) / BE(i, y−1)
   Trục quy mô như trên; trục sinh lời cắt tại 30% / 70% → R / N / W
   SMB_OP = (SR + SN + SW)/3 − (BR + BN + BW)/3
   RMW    = (SR + BR)/2 − (SW + BW)/2

 ----------------------------------------------------------------------------
 (4) Sáu rổ cho CMA
 ----------------------------------------------------------------------------
   INV(i) = AT(i, y−1) / AT(i, y−2) − 1
   Trục quy mô như trên; trục đầu tư cắt tại 30% / 70% → C (thấp) / N / A (cao)
   SMB_INV = (SC + SN + SA)/3 − (BC + BN + BA)/3
   CMA     = (SC + BC)/2 − (SA + BA)/2

 ----------------------------------------------------------------------------
 (5) SMB cuối cùng
 ----------------------------------------------------------------------------
   SMB = (SMB_BM + SMB_OP + SMB_INV) / 3

   Đây là lý do cột `smb` (bản 3 nhân tố) và `smb_ave` (bản 5 nhân tố) trong
   dữ liệu công bố khác nhau. Dùng đúng cột `smb_ave` khi chạy hồi quy 5 nhân tố.

================================================================================
 SÁU QUYẾT ĐỊNH PHẢI GHI RÕ TRONG BÁO CÁO (mỗi cái đổi kết quả vài điểm %)
================================================================================
 1. Vũ trụ mẫu: HOSE, hay HOSE+HNX, hay cả UPCoM. UPCoM thanh khoản mỏng làm
    nhiễu rổ nhỏ rất mạnh → khuyến nghị HOSE+HNX, loại UPCoM, và nói rõ.
 2. Ngân hàng và bảo hiểm: Fama–French loại DN tài chính vì đòn bẩy sổ sách
    không so sánh được. Với Việt Nam, loại ngân hàng nghĩa là loại ~30% vốn hoá
    thị trường. Khuyến nghị: dựng HAI bộ nhân tố (có và không có DN tài chính),
    báo cáo bộ chính là bộ loại DN tài chính theo chuẩn gốc.
    → Danh mục Medici có 3/7 mã là ngân hàng, nên phải dùng bộ CÓ DN tài chính
      khi hồi quy các mã đó, và nói rõ vì sao lệch chuẩn gốc.
 3. BE âm: loại khỏi rổ B/M (tỷ số vô nghĩa), giữ trong MKT và SMB.
 4. Sàn thanh khoản: loại mã có dưới 15 phiên khớp lệnh trong tháng.
 5. Ngưỡng giá tối thiểu: loại cổ phiếu dưới 1.000 đ để TSSL không bị chi phối
    bởi bước giá.
 6. Winsorize TSSL tháng tại 1% và 99% — thị trường Việt Nam có biên độ và
    những phiên trần sàn liên tiếp tạo đuôi rất dày.

================================================================================
"""

from __future__ import annotations
import argparse
import warnings
import numpy as np
import pandas as pd

warnings.filterwarnings('ignore')

# =============================================================================
# PHẦN A — NẠP DỮ LIỆU
# =============================================================================
# Thay ba hàm dưới đây bằng nguồn dữ liệu bạn có. Bản mẫu dùng vnstock.
# Ba hàm phải trả về đúng khuôn dạng ghi trong docstring, phần còn lại chạy được
# mà không cần sửa gì thêm.
# =============================================================================

def nap_danh_sach_ma(san=('HOSE', 'HNX')) -> list[str]:
    """Trả về danh sách mã. XEM CẢNH BÁO THIÊN LỆCH NGƯỜI SỐNG SÓT ở đầu file."""
    from vnstock import Listing
    df = Listing().symbols_by_exchange()
    df = df[df['exchange'].isin(san) & (df['type'] == 'STOCK')]
    return sorted(df['symbol'].dropna().unique().tolist())


def nap_gia_thang(ma_list: list[str], tu: str, den: str) -> pd.DataFrame:
    """
    Trả về DataFrame khung dài, 3 cột:
        ma (str) | thang (Period[M]) | gia (float, đã điều chỉnh cổ tức/chia tách)
    """
    from vnstock import Quote
    out = []
    for i, ma in enumerate(ma_list, 1):
        try:
            d = Quote(symbol=ma, source='VCI').history(
                start=tu, end=den, interval='1D')
            if d is None or d.empty:
                continue
            d['time'] = pd.to_datetime(d['time'])
            d = d.set_index('time')
            # số phiên khớp lệnh trong tháng — dùng cho sàn thanh khoản
            phien = d['close'].resample('ME').count()
            gia = d['close'].resample('ME').last()
            t = pd.DataFrame({'gia': gia, 'so_phien': phien}).dropna()
            t['ma'] = ma
            t['thang'] = t.index.to_period('M')
            out.append(t.reset_index(drop=True))
        except Exception as e:
            print(f'  [bỏ qua] {ma}: {e}')
        if i % 50 == 0:
            print(f'  ... {i}/{len(ma_list)} mã')
    return pd.concat(out, ignore_index=True)


def nap_bao_cao_tai_chinh(ma_list: list[str]) -> pd.DataFrame:
    """
    Trả về DataFrame khung dài, các cột:
        ma | nam (int, năm tài chính) | BE | OP | AT | SLCP
    Trong đó:
        BE   = vốn chủ sở hữu cuối năm
        OP   = doanh thu thuần − giá vốn − chi phí lãi vay − chi phí BH&QLDN
        AT   = tổng tài sản cuối năm
        SLCP = số lượng cổ phiếu lưu hành cuối năm
    Với ngân hàng: OP = thu nhập lãi thuần + lãi thuần từ dịch vụ và hoạt động
        khác − chi phí hoạt động  (KHÔNG trừ chi phí dự phòng — dự phòng là
        khoản dồn tích, không phải chi phí vận hành; ghi rõ lựa chọn này).
    """
    from vnstock import Finance
    rows = []
    for i, ma in enumerate(ma_list, 1):
        try:
            bs = Finance(symbol=ma, period='year', source='VCI').balance_sheet()
            is_ = Finance(symbol=ma, period='year', source='VCI').income_statement()
            bs.columns = [str(c).strip() for c in bs.columns]
            is_.columns = [str(c).strip() for c in is_.columns]
            for _, r in bs.iterrows():
                nam = int(r.get('yearReport', r.get('year', 0)))
                ir = is_[is_.get('yearReport', is_.get('year')) == nam]
                if ir.empty:
                    continue
                ir = ir.iloc[0]
                rows.append(dict(
                    ma=ma, nam=nam,
                    BE=_lay(r, ['OWNER\'S EQUITY(Bau cao)', 'Owners Equity',
                                'VỐN CHỦ SỞ HỮU', 'equity']),
                    AT=_lay(r, ['TOTAL ASSETS (Bn. VND)', 'Total Assets',
                                'TỔNG CỘNG TÀI SẢN', 'asset']),
                    OP=_op(ir),
                    SLCP=_lay(r, ['shareOutstanding', 'outstanding_share']),
                ))
        except Exception as e:
            print(f'  [bỏ qua BCTC] {ma}: {e}')
        if i % 50 == 0:
            print(f'  ... {i}/{len(ma_list)} mã')
    return pd.DataFrame(rows)


def _lay(row, keys):
    for k in keys:
        for c in row.index:
            if k.lower() in str(c).lower():
                v = row[c]
                if pd.notna(v):
                    return float(v)
    return np.nan


def _op(ir):
    """Lợi nhuận hoạt động theo định nghĩa RMW của Fama–French 2015."""
    dt   = _lay(ir, ['Net Sales', 'Revenue', 'Doanh thu thuần'])
    gv   = _lay(ir, ['Cost of Sales', 'Giá vốn'])
    lai  = _lay(ir, ['Interest Expenses', 'Chi phí lãi vay'])
    bhql = _lay(ir, ['Selling Expenses', 'General & Admin', 'Chi phí bán hàng'])
    vals = [x for x in [gv, lai, bhql] if pd.notna(x)]
    if pd.isna(dt):
        return np.nan
    return dt - sum(abs(v) for v in vals)


# =============================================================================
# PHẦN B — DỰNG NHÂN TỐ (không cần sửa)
# =============================================================================

MIN_PHIEN = 15        # sàn thanh khoản: số phiên khớp lệnh tối thiểu trong tháng
GIA_TOI_THIEU = 1000  # đồng
WINSOR = (0.01, 0.99)


def _tssl(gia: pd.DataFrame) -> pd.DataFrame:
    g = gia.sort_values(['ma', 'thang']).copy()
    g['R'] = g.groupby('ma')['gia'].pct_change()
    g = g[(g['so_phien'] >= MIN_PHIEN) & (g['gia'] >= GIA_TOI_THIEU)]
    lo, hi = g['R'].quantile(WINSOR)
    g['R'] = g['R'].clip(lo, hi)
    return g.dropna(subset=['R'])


def _gan_nhom(x: pd.Series, q=(0.30, 0.70), nhan=('L', 'M', 'H')) -> pd.Series:
    a, b = x.quantile(q[0]), x.quantile(q[1])
    return pd.Series(np.where(x <= a, nhan[0], np.where(x >= b, nhan[2], nhan[1])),
                     index=x.index)


def _vw(df: pd.DataFrame) -> float:
    """TSSL bình quân gia quyền theo vốn hoá đầu kỳ."""
    if df.empty or df['ME_dau_ky'].sum() == 0:
        return np.nan
    return float(np.average(df['R'], weights=df['ME_dau_ky']))


def dung_nhan_to(gia: pd.DataFrame, bctc: pd.DataFrame, rf: pd.Series) -> pd.DataFrame:
    """
    gia  : ma | thang | gia | so_phien
    bctc : ma | nam | BE | OP | AT | SLCP
    rf   : Series index=Period[M], giá trị = lãi suất phi rủi ro THÁNG
    """
    g = _tssl(gia)
    b = bctc.copy()

    # vốn hoá cuối mỗi tháng
    slcp = b.set_index(['ma', 'nam'])['SLCP']
    g['nam'] = g['thang'].dt.year
    g = g.merge(slcp.rename('SLCP'), left_on=['ma', 'nam'], right_index=True, how='left')
    g['SLCP'] = g.groupby('ma')['SLCP'].ffill()
    g['ME'] = g['gia'] * g['SLCP']
    g['ME_dau_ky'] = g.groupby('ma')['ME'].shift(1)

    # ---- MKT -----------------------------------------------------------------
    mkt = (g.dropna(subset=['ME_dau_ky'])
             .groupby('thang')
             .apply(_vw)
             .rename('MKT_tho'))

    # ---- biến phân loại, chốt tại 30/6 mỗi năm --------------------------------
    b = b.sort_values(['ma', 'nam'])
    b['AT_truoc'] = b.groupby('ma')['AT'].shift(1)
    b['INV'] = b['AT'] / b['AT_truoc'] - 1
    b['OP_BE'] = b['OP'] / b['BE']

    # ME tháng 12 năm y−1 để tính B/M
    me_t12 = (g[g['thang'].dt.month == 12]
              .assign(nam=lambda d: d['thang'].dt.year)
              .set_index(['ma', 'nam'])['ME'])

    ket = []
    nam_min, nam_max = g['thang'].dt.year.min(), g['thang'].dt.year.max()
    for y in range(int(nam_min) + 1, int(nam_max) + 1):
        # đặc điểm lấy từ năm tài chính y−1, ME mẫu số lấy 31/12 năm y−1
        f = b[b['nam'] == y - 1].set_index('ma')
        if f.empty:
            continue
        try:
            me12 = (me_t12[me_t12.index.get_level_values('nam') == y - 1]
                    .droplevel('nam'))
        except Exception:
            continue
        if me12.empty:
            continue
        # ME tháng 6 năm y để cắt trục quy mô
        me6 = (g[(g['thang'].dt.year == y) & (g['thang'].dt.month == 6)]
               .set_index('ma')['ME'])
        idx = f.index.intersection(me12.index).intersection(me6.index)
        if len(idx) < 30:
            continue
        f = f.loc[idx]
        d = pd.DataFrame(index=idx)
        d['ME6'] = me6.loc[idx]
        d['BM'] = f['BE'] / me12.loc[idx]
        d.loc[f['BE'] <= 0, 'BM'] = np.nan          # loại BE âm khỏi trục B/M
        d['OP_BE'] = f['OP_BE']
        d['INV'] = f['INV']

        d['S'] = np.where(d['ME6'] <= d['ME6'].median(), 'S', 'B')
        d['g_bm']  = _gan_nhom(d['BM'],    nhan=('L', 'M', 'H'))
        d['g_op']  = _gan_nhom(d['OP_BE'], nhan=('W', 'N', 'R'))
        d['g_inv'] = _gan_nhom(d['INV'],   nhan=('C', 'N', 'A'))
        d['ma'] = d.index
        d['tu'] = pd.Period(f'{y}-07', 'M')
        d['den'] = pd.Period(f'{y+1}-06', 'M')
        ket.append(d.reset_index(drop=True))

    if not ket:
        raise RuntimeError('Không dựng được rổ nào — kiểm tra lại dữ liệu đầu vào.')
    phan_loai = pd.concat(ket, ignore_index=True)

    # ---- ghép nhãn rổ vào từng tháng, tính TSSL từng rổ -----------------------
    g2 = g.dropna(subset=['ME_dau_ky']).copy()
    g2 = g2.merge(phan_loai, on='ma', how='inner')
    g2 = g2[(g2['thang'] >= g2['tu']) & (g2['thang'] <= g2['den'])]

    def _rieng(cot, nhan_long, nhan_short, ten):
        p = (g2.groupby(['thang', 'S', cot]).apply(_vw).rename('r').reset_index())
        pv = p.pivot_table(index='thang', columns=['S', cot], values='r')
        L = pv[[('S', nhan_long), ('B', nhan_long)]].mean(axis=1)
        Sh = pv[[('S', nhan_short), ('B', nhan_short)]].mean(axis=1)
        smb = (pv['S'].mean(axis=1) - pv['B'].mean(axis=1))
        return (L - Sh).rename(ten), smb.rename('smb_' + ten)

    hml, smb_bm  = _rieng('g_bm',  'H', 'L', 'HML')
    rmw, smb_op  = _rieng('g_op',  'R', 'W', 'RMW')
    cma, smb_inv = _rieng('g_inv', 'C', 'A', 'CMA')

    out = pd.concat([mkt, hml, rmw, cma, smb_bm, smb_op, smb_inv], axis=1)
    out['SMB'] = out[['smb_HML', 'smb_RMW', 'smb_CMA']].mean(axis=1)
    out['RF'] = rf.reindex(out.index)
    out['MKT'] = out['MKT_tho'] - out['RF']
    return out[['MKT', 'SMB', 'HML', 'RMW', 'CMA', 'RF']].dropna(how='all')


# =============================================================================
# PHẦN C — KIỂM TRA CHẤT LƯỢNG BẮT BUỘC CHẠY TRƯỚC KHI DÙNG
# =============================================================================

def kiem_tra(f: pd.DataFrame, vnindex_thang: pd.Series | None = None) -> pd.DataFrame:
    """
    Bốn phép thử. Bộ nhân tố nào trượt phép thử 1 hoặc 2 thì KHÔNG được dùng.
    """
    kq = []
    sd_mkt = f['MKT'].std() * np.sqrt(12)
    kq.append(('1. Biến động MKT quy năm nằm trong 15–30%',
               f'{sd_mkt*100:.1f}%', 0.15 <= sd_mkt <= 0.30))

    if vnindex_thang is not None:
        r = f['MKT'].corr(vnindex_thang.reindex(f.index))
        kq.append(('2. Tương quan MKT với VN-Index ≥ 0,85',
                   f'{r:.3f}', r >= 0.85))

    kq.append(('3. Tương quan HML–RMW không quá âm (> −0,7)',
               f"{f['HML'].corr(f['RMW']):.3f}", f['HML'].corr(f['RMW']) > -0.7))
    kq.append(('4. RF luôn không âm',
               f"{f['RF'].min()*100:.3f}%", bool(f['RF'].min() >= 0)))
    return pd.DataFrame(kq, columns=['Phép thử', 'Giá trị', 'Đạt'])


# =============================================================================
# PHẦN D — HỒI QUY DANH MỤC / CỔ PHIẾU LÊN 5 NHÂN TỐ
# =============================================================================

def hoi_quy_ff5(R_thang: pd.Series, f: pd.DataFrame) -> dict:
    """
    R_thang: TSSL tháng của cổ phiếu hoặc danh mục (chưa trừ Rf), index Period[M]
    Trả về alpha, 5 hệ số tải, sai số chuẩn, t và R² hiệu chỉnh.
    """
    d = pd.concat([R_thang.rename('R'), f], axis=1).dropna()
    y = (d['R'] - d['RF']).values
    X = np.column_stack([np.ones(len(d)), d[['MKT', 'SMB', 'HML', 'RMW', 'CMA']].values])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    n_, k_ = X.shape
    s2 = resid @ resid / (n_ - k_)
    se = np.sqrt(np.diag(s2 * np.linalg.inv(X.T @ X)))
    r2 = 1 - (resid @ resid) / ((y - y.mean()) @ (y - y.mean()))
    ten = ['alpha', 'b_MKT', 'b_SMB', 'b_HML', 'b_RMW', 'b_CMA']
    return dict(n=n_,
                he_so=dict(zip(ten, beta.round(4))),
                t=dict(zip(ten, (beta / se).round(2))),
                R2_hieu_chinh=round(1 - (1 - r2) * (n_ - 1) / (n_ - k_), 4))


def tssl_doi_hoi(loadings: dict, rf_nam: float, phan_bu: dict) -> float:
    """
    Re = Rf + b_MKT·MRP + b_SMB·λ_SMB + b_HML·λ_HML + b_RMW·λ_RMW + b_CMA·λ_CMA
    Mọi tham số theo đơn vị %/năm dạng thập phân.
    """
    return rf_nam + sum(loadings[f'b_{k}'] * phan_bu[k]
                        for k in ['MKT', 'SMB', 'HML', 'RMW', 'CMA'])


# =============================================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tu', default='2010-01-01')
    ap.add_argument('--den', default='2026-08-31')
    ap.add_argument('--out', default='factor_vn.xlsx')
    ap.add_argument('--rf', type=float, default=0.0456,
                    help='Lợi suất phi rủi ro quy năm nếu không có chuỗi thật')
    a = ap.parse_args()

    print('1/4 · Lấy danh sách mã ...')
    ma = nap_danh_sach_ma()
    print(f'     {len(ma)} mã')

    print('2/4 · Lấy giá ...')
    gia = nap_gia_thang(ma, a.tu, a.den)

    print('3/4 · Lấy báo cáo tài chính ...')
    bctc = nap_bao_cao_tai_chinh(ma)

    print('4/4 · Dựng nhân tố ...')
    thang = pd.period_range(a.tu, a.den, freq='M')
    rf = pd.Series((1 + a.rf) ** (1 / 12) - 1, index=thang)   # thay bằng chuỗi thật
    f = dung_nhan_to(gia, bctc, rf)

    with pd.ExcelWriter(a.out, engine='openpyxl') as w:
        f.to_excel(w, sheet_name='factor_thang')
        kiem_tra(f).to_excel(w, sheet_name='kiem_tra', index=False)
        (f.agg(['mean', 'std', 'count']).T
           .assign(t=lambda d: d['mean'] / (d['std'] / np.sqrt(d['count'])),
                   quy_nam=lambda d: d['mean'] * 12)
           .to_excel(w, sheet_name='thong_ke'))
    print('Xong →', a.out)
    print(kiem_tra(f).to_string(index=False))


if __name__ == '__main__':
    main()
