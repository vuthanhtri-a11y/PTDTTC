# -*- coding: utf-8 -*-
"""
BO NHAN TO PROXY — thay cho chuoi nhan to khong quan sat duoc sau 07/2021.

Y tuong: khong dung uoc luong theo giai doan lam so cong bo (no truot kiem dinh
ngoai mau), ma dung no voi DUNG trong so ma du lieu cho phep. Trong so do uoc
luong bang chinh phep kiem dinh ngoai mau, khong dat tay.
"""
import numpy as np, pandas as pd
from regime import M, HT, VARS, Z, zh, F, FAC, nam_tb, nam_n
np.random.seed(20260824)
pd.set_option('display.width', 230)

d = np.sqrt(((Z[VARS] - zh[VARS])**2).sum(axis=1) / len(VARS)).sort_values()
TOP5 = list(d.index[:5])

# ---------------------------------------------------------------------------
# 1. TRONG SO THU HEP TOI UU — uoc luong ngoai mau, khong dat tay
#    Voi tung nam y: bo y ra, du bao nhan to cua y bang trung binh k nam giong
#    nhat trong 11 nam con lai (P), va bang trung binh 11 nam do (B).
#    Tim w toi thieu hoa || w*P + (1-w)*B - A ||^2  ->  w* = <P-B, A-B>/||P-B||^2
# ---------------------------------------------------------------------------
def cv_frames(k):
    P, B, A = [], [], []
    for y in Z.index:
        khac = Z.drop(index=y)
        dz = np.sqrt(((khac[VARS] - Z.loc[y, VARS])**2).sum(axis=1) / len(VARS))
        lg = dz.nsmallest(k).index
        P.append(nam_tb.loc[lg].mean())
        B.append(nam_tb.drop(index=y).mean())
        A.append(nam_tb.loc[y])
    return (pd.DataFrame(P, index=Z.index), pd.DataFrame(B, index=Z.index),
            pd.DataFrame(A, index=Z.index))

def trong_so_toi_uu(k):
    P, B, A = cv_frames(k)
    out = {}
    for c in FAC:
        p, b, a = P[c].values, B[c].values, A[c].values
        num, den = np.dot(p - b, a - b), np.dot(p - b, p - b)
        w = num / den if den > 0 else 0.0
        w_clip = float(np.clip(w, 0.0, 1.0))
        rmse = lambda v: np.sqrt(((v - a)**2).mean())
        out[c] = dict(w_tho=w, w_dung=w_clip,
                      RMSE_w0=rmse(b), RMSE_w1=rmse(p),
                      RMSE_wtoiuu=rmse(w_clip*p + (1-w_clip)*b))
    T = pd.DataFrame(out).T
    T['cai_thien_%'] = (1 - T.RMSE_wtoiuu / T.RMSE_w0) * 100
    return T

W = {k: trong_so_toi_uu(k) for k in (1, 3, 5)}

# ---------------------------------------------------------------------------
# 2. BO PROXY
# ---------------------------------------------------------------------------
K = 5
w_star = W[K]['w_dung']
lam_regime = F[F.nam.isin(TOP5)][FAC].mean() * 12 * 100
lam_uncond = F[FAC].mean() * 12 * 100
lam_proxy  = w_star * lam_regime + (1 - w_star) * lam_uncond

PROXY = pd.DataFrame({
    'Giai đoạn tương đồng (Top-5)': lam_regime,
    'Toàn mẫu 2010–2021': lam_uncond,
    'Trọng số w* (ngoài mẫu)': w_star,
    'PROXY = w*·GĐ + (1−w*)·toàn mẫu': lam_proxy,
})

# ---------------------------------------------------------------------------
# 3. PHAN PHOI PROXY CHO CUA SO 10 TUAN  (10/52 nam ~ 2,31 thang)
#    Bootstrap khoi 3 thang tu chinh 60 quan sat cua 5 nam tuong dong,
#    tron voi 133 quan sat toan mau theo dung ty le w*.
# ---------------------------------------------------------------------------
TUAN, THANG_KY = 10, 10 * 12 / 52          # 2,3077 thang
def bootstrap_10tuan(n=300000):
    """Hon hop theo TUNG nhan to: voi xac suat w*_c lay khoi tu 5 nam tuong dong,
    con lai lay tu toan mau. Lay khoi 3 thang lien tiep de giu tuong quan chuoi,
    va giu CUNG chi so khoi cho ca bon nhan to de giu tuong quan giua cac nhan to."""
    reg_idx = np.where(F.nam.isin(TOP5).values)[0]
    reg_idx = reg_idx[reg_idx < len(F) - 2]
    all_idx = np.arange(0, len(F) - 2)
    Fv = F[FAC].values
    # chon nguon rieng cho tung nhan to, nhung dung chung mot boc chi so
    i_reg = np.random.choice(reg_idx, size=n)
    i_all = np.random.choice(all_idx, size=n)
    out, keo = {}, {}
    for j, c in enumerate(FAC):
        w = float(w_star[c])
        lay_reg = np.random.random(n) < w
        idx = np.where(lay_reg, i_reg, i_all)
        blk = np.stack([Fv[idx, j], Fv[idx+1, j], Fv[idx+2, j]], axis=1)
        tich = np.prod(1 + blk, axis=1) - 1
        out[c] = np.sign(1+tich) * np.abs(1+tich) ** (THANG_KY/3) - 1
        keo[c] = idx
    return out

BS = bootstrap_10tuan()
PHANPHOI = pd.DataFrame({c: {
    'trung bình': v.mean()*100, 'độ lệch chuẩn': v.std()*100,
    'P5': np.percentile(v, 5)*100, 'P25': np.percentile(v, 25)*100,
    'P50': np.percentile(v, 50)*100, 'P75': np.percentile(v, 75)*100,
    'P95': np.percentile(v, 95)*100} for c, v in BS.items()}).T

# ---------------------------------------------------------------------------
# 4. ANH HUONG LEN ALPHA 5 NHAN TO
# ---------------------------------------------------------------------------
B_ = dict(MKT=0.6821, SMB=-0.1307, HML=-0.1164, RMW=0.1178, CMA=-0.1696)
dieu_chinh = pd.Series({c: B_[c] * PHANPHOI.loc[c, 'trung bình'] for c in FAC})

# phan phoi cua TONG dieu chinh — bootstrap chung, giu tuong quan giua cac nhan to
tong_bs = sum(B_[c] * BS[c] * 100 for c in FAC)
xau_nhat = np.percentile(tong_bs, 5)
tot_nhat = np.percentile(tong_bs, 95)
sd_tong = tong_bs.std()
dc_tong = tong_bs.mean()

# ---------------------------------------------------------------------------
# 5. TSSL DOI HOI NEU DUNG PROXY (de doi chieu — KHONG thay so cong bo)
# ---------------------------------------------------------------------------
RF, ERP = 0.0456, 0.0813
def Re(lam):
    return (RF + B_['MKT']*ERP + sum(B_[c]*lam[c]/100 for c in FAC)) * 100
RE = {'A · Hiện hành (công bố)': Re(pd.Series(dict(SMB=1.71, HML=3.49, RMW=3.47, CMA=1.26))),
      'Toàn mẫu 2010–2021': Re(lam_uncond),
      'Giai đoạn tương đồng Top-5': Re(lam_regime),
      'PROXY (w* ngoài mẫu)': Re(lam_proxy),
      'CAPM': (RF + B_['MKT']*ERP) * 100}

if __name__ == '__main__':
    print('=== 1. TRONG SO THU HEP TOI UU (uoc luong ngoai mau) ===')
    for k, T in W.items():
        print(f'\n  k = {k} lang gieng:')
        print(T.round(3).to_string())
    print('\n=== 2. BO NHAN TO PROXY (%/nam) ===')
    print(PROXY.round(2).to_string())
    print('\n=== 3. PHAN PHOI PROXY CHO CUA SO 10 TUAN (%) ===')
    print(PHANPHOI.round(2).to_string())
    print('\n=== 4. DIEU CHINH ALPHA 5 NHAN TO (diem % tren 10 tuan) ===')
    print(dieu_chinh.round(3).to_string())
    print(f'  Tong dieu chinh   : {dc_tong:+.3f} diem %')
    print(f'  Do lech chuan     : {sd_tong:.3f} diem %')
    print(f'  P5 / P95 cua tong : {xau_nhat:+.3f} / {tot_nhat:+.3f}')
    print(f'  Doi chieu lam_proxy x 10/52: ' + str({c: round(lam_proxy[c]*10/52,3) for c in FAC}))
    print('\n=== 5. TSSL DOI HOI DOI CHIEU (%/nam) ===')
    for k, v in RE.items(): print(f'  {k:<32} {v:.2f}')
