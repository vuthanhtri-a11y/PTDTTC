"""
lt_config.py — Tham so CHIEN LUOC DAI HAN (long-term), dung chung cho ca 2 danh muc.

Thay the hoan toan khung "P(ve nhat)" cu:
  - Ham muc tieu cu: P(ve nhat) trong cuoc thi 2 thang -> khuyen khich tap trung,
    bo qua rui ro, chon ma bien dong cao. DA BO.
  - Ham muc tieu moi: toi da hoa E[log NAV] dai han (toc do gop von), tuc la
    uu tien (a) chon ma manh hon thi truong ben vung, (b) khong de mot ma lam
    hong danh muc, (c) chi phi giao dich thap vi vong quay cham.

Tu 01/10/2026 — KHUNG TOP-DOWN, HAI NHANH SONG SONG (CHIEN_LUOC_DAI_HAN.md muc 13):
  1. NHANH MAY  — LOC (hard filter) tren TOAN THI TRUONG (HOSE+HNX+UPCoM,
                  lt_scan_vietcap.py) -> "ro xu huong".
  2. NHANH NGUOI — RO CO BAN top-down: vi mo -> nganh -> doanh nghiep (V1-V5),
                  nhap tay trong THAM_DINH_FILE.
  3. GIAO DIEM hai ro + Buoc 4 dinh gia = lua chon cua Quy. Thu tu mua theo
     `uu_tien` nguoi gan, pha hoa bang ATR thap truoc.
  4. PHAN BO (risk parity) — ty trong ~ 1/bien dong, co tran ma va tran nganh.
Buoc 2 (xep hang RS) DA BO 01/10/2026 — ban cu: data/lt_config_backup_20261001.py

Tu 05/10/2026 — KHUNG GIAI DOAN 2 (CHIEN_LUOC_DAI_HAN.md muc 14), dung khung da
cong bo o Muc 9 bao cao giai doan 1 (tr.69-73):
  "Doanh nghiep tot la dieu kien (Fisher), gia hop ly la nguyen tac (Graham),
   xu huong xac nhan la ky luat (Medici)."
  * TRU 1 — CHE_DO thi truong (lt_che_do.py): VNINDEX so voi MA50/MA200 + phien
    phan phoi -> TANG / DIEU_CHINH / GIAM; dat TRAN ty trong co phieu. GIAM =
    ban toan bo, khoa mua moi.
  * TRU 2 — nam cong V1-V5 + ba truc (phieu Dat) + bien an toan kep: mua khi
    gia <= (1 - BIEN_AN_TOAN_MIN) x than_trong; ban khi gia cham co_so.
  * Xac nhan xu huong o dau vao: gia > MA200, MA50 > MA200 (RS va ATR da bo).
  * Quy tac 5 (ban theo cam quan) BO tu 05/10; moi lenh can PHIEU_LENH ghi truoc.
Ban truoc 04/10/2026: data/lt_config_backup_20261004b.py

Chay: PYTHONIOENCODING=utf-8 python lt_screener.py
"""

# ----------------------------------------------------------------- Danh muc
PORTFOLIOS = {
    "DM1": {
        "ten": "Danh muc 1 — tien that",
        "von_ban_dau": 200_000_000,
        "so_vi_the": 10,          # con so DA CHOT (khong con duoc backtest ung ho)
        "tran_ma": 0.15,          # 15% NAV toi da 1 ma
        "tran_nganh": 0.30,       # 30% NAV toi da 1 nganh
        "ticket_toi_thieu": 8_000_000,
    },
    "DM2": {
        "ten": "Danh muc 2 — tai khoan du thi",
        "von_ban_dau": 60_000_000,
        "so_vi_the": 8,           # con so DA CHOT (xem canh bao do nhay ben duoi)
        "tran_ma": 0.20,
        "tran_nganh": 0.40,
        "ticket_toi_thieu": 5_000_000,
    },
}
# ⚠️ 26/08/2026 — bang do nhay cu DA BI DAO NGUOC khi do lai. Bang cu (1 pha
# luoi, pham vi xep hang toan ro): 5 o 8,6% | 6 o 10,5% | 8 o 13,1% | 10 o 13,9%
# | 12 o 9,4% | 15 o 8,6%, ket luan "vung 8-10 tot nhat".
# Do lai (TB 4 pha luoi, pham vi ro da loc theo ban chot FF5):
#   5 o 10,66% | 6 o 10,50% | 8 o 9,08% | 10 o 9,05% | 12 o 8,04% | 15 o 8,05%
# tuc 5 o TOT HON 10 o o ca 4/4 pha — nguoc han ket luan cu.
# Hai phep do cho hai ket luan nguoc nhau => dieu doc duoc chac chan nhat la
# SO O KHONG DO DUOC o co mau nay. Giu 10/8 vi do la con so DA CHOT, khong phai
# vi du lieu ung ho. Chi tiet: data/backtest_pha_luoi_20260826.json, muc 8 cua
# CHIEN_LUOC_DAI_HAN.md.

# ------------------------------------------------------- Vi the dang nam giu
# (ma, khoi luong, gia von VND). Cap nhat khi mua/ban.
HOLDINGS = {
    # 25/08/2026 — user yeu cau TAM XOA du lieu DM1, se tu cap nhat lai sau.
    # Ban ghi cu (17/08 -> 24/08) giu tai data/lt_config_backup_20260825.py:
    #     "DM1": [("PVT", 1000, 19_900), ("TCB", 500, 31_300)]
    #     TIEN_MAT["DM1"] = 164_396_675
    # Trong luc DM1 rong, lt_allocator chi con sinh bang lenh cho DM2; phan DM1
    # chuyen thanh danh sach ung vien mua moi (khong co so tien -> khong chia lo).
    "DM1": [],
    # DM2 cap nhat sau phien 19/08/2026: da BAN 200 VNM @62.000 va 100 BAF @31.500
    # (ca hai khong dat chuan khung dai han). Con 6 ma.
    # 25/08/2026: user xac nhan lenh mua 100 VPI (ke hoach 20-21/08) KHONG KHOP.
    # Nhanh bat buoc "qua 21/08 chua khop -> mua gia thi truong" da khong duoc
    # thuc hien -> ghi nhan la LECH so voi ke hoach da chot, khong phai lenh cho.
    # 28/08/2026 — MSB GIAO DICH KHONG HUONG QUYEN co tuc bang CO PHIEU 100:20.
    #   Truoc:  700 CP, gia von 16.000  (tong von 11.200.000)
    #   Sau:    840 CP, gia von 13.333  (700 x 1,2 = 840; 16.000 / 1,2 = 13.333)
    #   Tong von KHONG doi (lam tron xuong lech 280d, bo qua).
    # Xac nhan tu du lieu: TradingView da hoi to chia 1,2 toan bo lich su MSB —
    # chot 26/08 doc ra 12.791,67 (= 15.350 / 1,2), chot 27/08 doc ra 13.083,33
    # (= 15.700 / 1,2). Bar 28/08 la so nguyen (O 13.200) => ngay GDKHQ dung la
    # hom nay. Gia tham chieu 28/08 = 15.700 / 1,2 = 13.083.
    # ⚠️ 140 CP thuong duoc VE TAI KHOAN SAU ~4-6 TUAN. Tinh NAV thi da co quyen
    # tu hom nay, nhung nếu can BAN truoc ngay ve thi chi ban duoc 700 CP.
    # 03/09/2026 (phien sang) — DA MUA 200 DHC @36.600 theo bang lenh ky soat
    # thang 9 (ke hoach ghi 36.900 = chot 28/08; khop thap hon 300d/CP).
    # Chi 7.320.000 + phi 10.980 = 7.330.980.
    # 03/09/2026 (chieu) — HAI LENH BAN CUA KY SOAT DA KHOP: 100 GMD @78.100 va
    # 100 LPB @49.050. Da go khoi HOLDINGS ngay 04/09/2026 (sao luu truoc khi sua:
    # data/lt_config_backup_20260904.py). Lo thuc hien: GMD -70.000, LPB -175.000.
    # Thu ve rong 7.790.475 + 4.892.738 = 12.683.213 (phi ban+thue 0,25%).
    # 07/09/2026 — LENH NGOAI LUAT #1 (xem LENH_NGOAI_LUAT ben duoi):
    #   "Lenh chot lai mot phan theo yeu cau nguoi gop von" — ban 50/100 VHM
    #   @77.700, kem ke hoach mua lai o 75.200 (han 16/10).
    #   KHONG phai quy tac 5 va khong phai bat ky quy tac nao trong bon. Ban ghi
    #   dau tien cua phien nay goi no la "vien dan quy tac 5" — da sua sau khi
    #   user lam ro ban chat ngay trong ngay.
    # 🔴 Doi chieu bang chung cua chinh quy: "ban de bao ve thanh qua ngan han"
    #    CHINH LA luat A (chot lai tai muc tieu) — 56.496 lenh mo phong 2018-2026
    #    do duoc alpha AM o CA HAI che do: -0,235%/lenh khi thi truong tang,
    #    -0,692%/lenh khi giam. Do la ly do EXIT co "khong_co_muc_tieu_chot_lai".
    #    Ghi lai o day de ky sau doi chieu, khong phai de bao chua hay trach moc.
    # Thu ve: 50 x 77.700 = 3.885.000 - phi/thue 0,25% (9.713) = 3.875.287.
    # Lai da thuc hien: (77.700 - 69.000) x 50 = +435.000 gop / +425.287 rong.
    # Con lai 50 CP VHM = LO LE (phai ban qua bang lo le neu muon thoat not).
    # 14/09/2026 — BAN TOAN BO 100 STB @76.900 theo QUY TAC THOAT SO 4 (luan
    #   diem doanh nghiep da gay). DAY LA LENH TRONG LUAT: khong ghi vao
    #   LENH_NGOAI_LUAT, khong ghi vao LENH_QUY_TAC_5.
    #   Chuoi nhan qua, ghi lai de ky sau doi chieu:
    #     - Luan diem luc mua (17-19/08): dua tren thong tin so bo tu bao cao
    #       phan tich cua cac CTCK, quy CHUA tu tham dinh doc lap.
    #     - Khi viet bao cao giua ky, quy tu thu thap va phat hien thong tin
    #       PHU QUYET luan diem ban dau -> phieu tham dinh Buoc 3 (13/09) cham
    #       1/6 diem, truc A = 0 va truc C = 0 -> PHU QUYET.
    #     - 14/09 dat luan_diem_con_nguyen = false trong data/tham_dinh.json
    #       -> quy tac 4 kich hoat -> ban TOAN BO, khong phai mot nua.
    #   Chi tiet phu quyet: STB.buoc3_chi_tiet trong data/tham_dinh.json.
    #   Thu ve: 100 x 76.900 = 7.690.000 - phi/thue 0,25% (19.225) = 7.670.775.
    #   Lai da thuc hien: (76.900 - 74.200) x 100 = +270.000 gop / +250.775 rong
    #   (+3,38% tren von 7.420.000).
    #   Sao luu truoc khi sua: data/lt_config_backup_20260914.py
    # 16/09/2026 — BAN 100/200 BSR @31.300 theo QUY TAC THU NAM (cam quan thi
    #   truong cua quy — lo ngai chung ve thi truong/nhom nganh, khong rieng ve
    #   ban than BSR). Dung TRAN 50% vi the. Ghi vao LENH_QUY_TAC_5 ben duoi —
    #   nhung GHI SAU KHI DA KHOP, khong dung thu tu quy tac doi hoi (phai ghi
    #   TRUOC lenh) - le sai quy trinh, ghi lai trung thuc de ky sau doi chieu.
    #   Hieu luc toi ky soat 01/10: neu BSR con qua 4 quy tac, allocator duoc
    #   mua lai 100 CP da ban (tru khi quy ghi gia_han_den truoc ngay soat).
    #   ⚠️ CAU TREN VIET KHI KY SOAT KE TIEP CON LA 01/10. Cung ngay 16/09, lich
    #   ra soat them ky bo sung 21/09 (LICH_SOAT) -> "ky soat ke tiep" thanh
    #   21/09, tuc BSR se bi mua lai sau 4 phien. Quy da GHI GIA HAN den
    #   2026-09-30 ngay trong ngay 16/09 (hop le vi truoc ngay soat), nen loi
    #   hua o cau tren duoc giu nguyen: ky 01/10 moi lay lai quyen.
    #   Thu ve: 100 x 31.300 = 3.130.000 - phi/thue 0,18% (5.634) = 3.124.366.
    #   Lai chua thuc hien tren 100 CP con lai: (31.300-27.000) x 100 = +430.000
    #   gop / +427.840 rong (tru phi mua con lai 2.160). Sao luu truoc khi sua:
    #   data/lt_config_backup_20260916.py
    # 22/09/2026 — BAN TOAN BO 50 VHM @69.000 do PHU_QUYET (Buoc 3 ngay 13/09,
    #   truc A=0 va C=0) -> quy tac thoat 4 (luan diem gay). Da het vi the.
    #   ⚠️ LECH KE HOACH: BAO_LUU_TIN_HIEU (ben duoi) ghi tin hieu nay phat sinh
    #   13/09 (TRUOC moc 16/09) nen le ra giu lich thuc thi CU, ban o ky 01/10.
    #   Nhung lenh da khop SOM hon, tai 22/09 — theo trinh tu ky soat bo sung
    #   21/09 (LICH_SOAT: "lenh BAN van dat 22/09, khong can tham dinh"). User
    #   xac nhan day la lenh khop som theo trinh tu do, khong phai quyet dinh
    #   khac. Ghi nhan lech trung thuc, khong sua lai BAO_LUU_TIN_HIEU cho khop.
    #   Gia ban = dung gia von 69.000 -> lai gop = 0, lai rong = -8.970 (phi+thue).
    #   Thu ve: 50 x 69.000 = 3.450.000 - phi/thue 0,18% (6.210) = 3.443.790.
    #   Da them vao KHOA_WHIPSAW.ban_ky_bo_sung (mot trong bon quy tac thoat).
    # 22/09/2026 — BAN 300 + 50 MSB @13.450 va @13.500 theo QUY TAC THU NAM
    #   (cam quan: lo ngai chung ve nganh ngan hang/thi truong, khong rieng ve
    #   ban than MSB). Hai lenh khop rieng, ghi thanh LENH_QUY_TAC_5 so 2 va
    #   so 3 ben duoi — GHI SAU KHI DA KHOP (le sai quy trinh nhu BSR 16/09),
    #   ghi lai trung thuc. Tong 350/840 CP (41,7% vi the goc), moi lenh rieng
    #   deu duoi tran 50%. Con lai 490 CP, gia von khong doi 13.333.
    #   Thu ve: 300 x 13.450 = 4.035.000 - phi/thue (7.263) = 4.027.737;
    #           50 x 13.500 = 675.000 - phi/thue (1.215) = 673.785.
    #   Sao luu truoc khi sua: data/lt_config_backup_20260922.py
    # 01/10/2026 — BAN 50 MSB @14.200 theo QUY TAC THU NAM (LENH_QUY_TAC_5 so 4).
    #   cam_quan (loi user): co cau danh muc an toan truoc bien dong thi truong,
    #   can lai so CP dang nam thanh lo chan. 50/490 = 10,2% vi the, duoi tran.
    #   Khop ngay ky soat 01/10, GHI SO NGAY 04/10 — sau khi khop (le sai quy
    #   trinh nhu so 1-3). Con 440 CP, gia von khong doi 13.333.
    #   Thu ve: 710.000 - phi/thue (1.278) = 708.722.
    #   Sao luu truoc khi sua: data/lt_config_backup_20261004.py
    # 05/10/2026 — DA KHOP theo che do GIAM (PHIEU_LENH so 1-3, ghi 04/10 18:57):
    #   BAN 100 BSR @30.350, 200 DHC @38.100 (het hai vi the), 300/440 MSB @14.050.
    #   140 MSB con lai = CP thuong GDKHQ 28/08, suy ra chua ve TK (chi ban duoc
    #   300) — ban ngay khi ve. Gia von khong doi 13.333.
    #   Sao luu truoc khi sua: data/lt_config_backup_20261005.py
    "DM2": [("MSB", 140, 13_333)],
}
# DM2: 15.826.732 - 7.330.980 (mua DHC 03/09) = 8.495.752
#      8.495.752 + 12.683.213 (ban GMD+LPB 03/09) = 21.178.965
#      21.178.965 + 3.875.287 (ban 50 VHM 07/09) = 25.054.252
#      25.054.252 + 7.670.775 (ban 100 STB 14/09, quy tac 4) = 32.725.027
# 15/09/2026 — TINH LAI theo bieu phi dung (0,08% / 0,08%+0,1%). Con so cu
# 32.725.027 duoc tinh bang 0,15%/0,25% nen thap hon thuc te 74.729 d. Toan bo
# chuoi so du ghi trong cac ban sao luu truoc day (315.607 / 15.826.732 /
# 8.495.752 / 21.178.965 / 25.054.252) deu mang cung loi nay — chung khop voi
# nhau vi cung sai mot kieu, khong phai vi chung dung.
# Chuoi so du tinh lai: 357.324 / 15.879.334 / 8.553.478 / 21.245.591 /
# 25.123.598 / 32.799.756. Chi tiet tung lenh: data/so_giao_dich.json
# Con lech 271 d so voi NAV sao ke (0,00045%) — chua truy duoc, nhieu kha nang
# la lai tien gui tren so du hoac lam tron cua cong ty chung khoan.
# 16/09/2026 — 32.799.756 + 3.124.366 (ban 100 BSR, quy tac 5) = 35.924.122.
# NAV tu day mang GIA MIXED NGAY (BSR 16/09, MSB/VHM/DHC van 15/09) nen chua
# doi chieu duoc voi sao ke moi — can mot dong sao ke ke tiep de dong lai.
# 18/09/2026 — DOI CHIEU SAO KE TIEN: 35.924.363 (lech +241 so voi 35.924.122: lai 638, luu ky -169, TTLK -225, lam tron -3). Xem so_giao_dich.json.
# 22/09/2026 — 35.924.363 + 3.443.790 (ban 50 VHM, phu_quyet) = 39.368.153
#              39.368.153 + 4.027.737 (ban 300 MSB, quy tac 5) = 43.395.890
#              43.395.890 + 673.785 (ban 50 MSB, quy tac 5) = 44.069.675
# 01/10/2026 — 44.069.675 + 708.722 (ban 50 MSB, quy tac 5 so 4) = 44.778.397
# 05/10/2026 — 44.778.397 + 3.029.537 (ban 100 BSR) = 47.807.934
#              47.807.934 + 7.606.284 (ban 200 DHC) = 55.414.218
#              55.414.218 + 4.207.413 (ban 300 MSB) = 59.621.631
#              59.621.631 + 190.000 (co tuc tien DHC) = 59.811.631
#   Che do GIAM. Phi TTLK ban tu 22/09 (~315d) + luu ky 09 (~387d) chua tru.
TIEN_MAT = {"DM1": 0, "DM2": 59_811_631}

# ------------------------------------------------- Lenh ngoai luat (co y thuc)
# Quy dinh: nhung quyet dinh KHONG sinh ra tu bon quy tac thoat / bang xep hang
# deu phai nam o day, ghi truoc khi biet ket qua. Muc dich khong phai de cam —
# quy co quyen lam ngoai luat — ma de bao cao cuoi ky doc duoc: cai gi la he
# thong, cai gi la nguoi. Khong co so nay thi moi lenh tuy nghi deu se duoc nho
# lai nhu "da co ly do tu dau".
#
# lt_allocator.py IN ra danh sach nay moi lan chay va KHONG tu dong thuc hien.
LENH_NGOAI_LUAT = [
    {
        "so": 1,
        "ngay": "2026-09-07",
        "ma": "VHM",
        # TEN CHINH THUC (chot 07/09/2026). Ba phep thu ma ten nay phai qua:
        #   1. dung co che  — chot lai mot phan, khong phai cat lo/giam rui ro/
        #      tai can bang (tai can bang la keo VE ty trong muc tieu; lenh nay
        #      day LECH KHOI ty trong muc tieu).
        #   2. dung nguyen nhan — nguon goc la yeu cau nguoi gop von, khong phai
        #      mot tin hieu. Nguoi doc bao cao truy duoc lenh nay tu dau ma ra.
        #   3. khong muon tham quyen he thong — trong ten KHONG co so hieu quy tac
        #      nao. Chi can chu "quy tac 5" nam trong ten la sau nay ca quy se nho
        #      lai nhu la he thong da bao lam.
        # Ten nay TRUNG TINH ve dung/sai. Phan quyet chi co ~17/10 khi biet lenh
        # mua lai co khop khong va VHM di dau — do duoc chinh vi hom nay da ghi ten.
        "ten": "Lenh chot lai mot phan theo yeu cau nguoi gop von",
        "viec": "BAN 50/100 VHM @77.700 (+12,6% tren gia von 69.000)",
        "trang_thai": "da khop",
        "ke_hoach_dao_nguoc": "MUA LAI 50 CP khi gia <= 75.200",
        "han_chot": "2026-10-16",   # phien cuoi truoc khi cuoc thi ket thuc ~17/10
        "neu_khong_khop": "HET HIEU LUC sau han chot; KHONG duoc nang gia mua lai. "
                          "Nang gia = doi luat sau khi biet ket qua.",
        "so_hoc_da_do": "Khop -> +109.648 d (+0,18% NAV). Khong khop ma VHM len "
                        "80.000/85.000 -> -124.712/-374.712 d (-0,21%/-0,62% NAV). "
                        "Xac suat khop phai dat 53,2%/77,4% moi hoa von.",
        "bang_chung_nguoc": "Luat A (chot lai tai muc tieu) co alpha AM tren "
                            "56.496 lenh mo phong — xem memory luat-thoat-va-cuoc-thi-dau-tu.",
        # 04/10/2026 — he qua cua luat da chot, khong phai quyet dinh moi: VHM
        # bi phu quyet Buoc 3 (13/09; chi phieu Dat duoc mua — quyet dinh 9) va
        # che do GIAM khoa moi lenh mua (quyet dinh 1). Ke hoach mua lai khong
        # con duong nao de thuc hien. Giu cac truong tren lam ho so.
        "ket_thuc": "04/10/2026: ke hoach mua lai HET CAN CU — VHM phu quyet Buoc 3 "
                    "va che do GIAM khoa mua moi (CHIEN_LUOC_DAI_HAN.md muc 14). "
                    "Khong mua lai.",
    },
]

# ------------------------------------------------------- Tran trung lap: DA BO
# 02/09/2026 — user quyet dinh XOA HAN quy tac "mot ma <= 10% TONG tai san hai
# danh muc". Truoc do: TRAN_TRUNG_LAP = 0.10, ap o vong 3 cua lt_allocator SAU
# khi lam tron lo.
#
# Ly do bo (bang chung do duoc ngay 02/09, NAV DM2 60.155.732, DM1 rong):
#   * DM1 dang rong nen "10% tong tai san hai tai khoan" = 6.015.573 d, tuc
#     10% cua RIENG DM2 — chat gap doi tran ma 20% cua DM2 (12.031.146 d).
#     Tran ma 20% da chot cho DM2 do do khong bao gio co hieu luc: chu chet.
#   * Cong voi ticket_toi_thieu 5.000.000, no tao ra mot CUA SO HOP LE chi rong
#     1.015.573 d (5.000.000 .. 6.015.573). Ma nao co gia tri 1 lo khong roi
#     vao cua so do thi bi ep ve 0, du qua ca 4 buoc va xep hang cao.
#     Do duoc 02/09: VHM (hang 3, qua ca 4 cua) 1 lo 7,30tr -> 0;
#                    DHC 1 lo 3,69tr duoi ticket / 2 lo 7,38tr vuot tran -> 0.
#     Toan bo dai thi gia > 60.200 d va 30.100-49.950 d bi chan sach.
#   * Hieu ung that cua no la THUONG CHO MA THI GIA THAP, tuc mot tran dat bang
#     SO TIEN TUYET DOI dang thay bang xep hang quyet dinh thu tu uu tien.
#     Do la dung loai lech chuan ma he thong nay von dung de tranh.
#
# ⚠️ Ghi nhan trung thuc: so 26/08 va 29/08 deu da ghi "phai chot TRAN_TRUNG_LAP
# TRUOC 01/09, khong duoc chot sau khi nhin bang lenh". Quyet dinh nay tren thuc
# te duoc dua SAU khi da nhin bang lenh 02/09. Do la mot sai lech quy trinh da
# biet, ghi lai de ky sau doi chieu — khong phai de bao chua.
#
# Con lai chan tap trung: tran ma (15% DM1 / 20% DM2) + tran nganh (30%/40%).
# Ban ghi cu: data/lt_config_backup_20260902.py

# ------------------------------------------------------------- Bo loc cung
LOC = {
    "thanh_khoan_min": 10e9,   # Gia tri khop lenh TB 20 phien >= 10 ty/phien
    "gia_tren_ma200": True,    # Close > MA200
    "ma50_tren_ma200": True,   # MA50 > MA200 (cau truc tang dai han)
    # 04/10/2026 — BO (muc 14, quyet dinh 5). RS la da tang TUONG DOI: no loai
    # dung nhom ma Tru 2 can tim (gia tang deu nhung cham hon chi so — ban quet
    # 01/10: AAA, NTP, QNS, SBT, VEA, VTZ). Chu L (RS 12T) trong phep do dang ky
    # truoc cua Quy co DAU NGUOC (-2,0%, t -1,42; muc 12.2). Doi xung voi viec bo
    # luat ban RS (quyet dinh 4). Ban cu: True.
    "rs_252_duong": False,
    # 04/10/2026 — BO (cam ket #2 tr.70 bao cao giai doan 1: ATR chua loai ma nao
    # trong 9 ky quet; ban quet 01/10 cung vay). None = tat. Ma dong manh van
    # bi thu nho o khau PHAN BO (1/ATR) va phai qua Tru 2. Ban cu: 0.060.
    "atr_max": None,
}

# ------------------------------------- Tru 1: che do thi truong (chot 04/10/2026)
# Quyet dinh 1-3 (muc 14). Bang 9.2 bao cao giai doan 1 + hai cho lam ro:
#   * GIAM khi VNINDEX dong cua < nguong_vao_giam x MA200 (tinh lai MOI PHIEN).
#     Chi RA khoi GIAM khi dong cua > nguong_ra_giam x MA200 (do tre: dung khoang
#     lech 3% Quy dung cho tung ma). Do tren VNINDEX 10/2014-10/2026: doi xung
#     cho 35 lan vao Giam, 24 lan ngan < 10 phien; do tre con 15 lan, 5 lan ngan.
#   * Ngoai GIAM: TANG khi dong cua > MA200 va MA50 > MA200 va phien phan phoi
#     < nguong; DIEU_CHINH khi MA50 < MA200 hoac phien phan phoi >= nguong. Vung
#     giua (0,97-1,00 x MA200) GIU trang thai truoc do, chi duoc XAU DI (sang
#     DIEU_CHINH), khong duoc tot len.
#   * Dai ty trong la TRAN, khong phai muc tieu (quyet dinh 3 — cuoc thi chi cho
#     mua co phieu, nen khong co ETF de lap san). Thieu ma dat Tru 2 -> nam tien.
#   * Phien phan phoi (O'Neil): VNINDEX giam >= giam_toi_thieu VA khoi luong cao
#     hon phien truoc; dem trong cua_so phien gan nhat.
CHE_DO = {
    "hieu_luc_tu": "2026-10-04",          # ngay chot; lenh dau tien dat 05/10
    "nguong_vao_giam": 0.97,
    "nguong_ra_giam": 1.00,
    "tran_co_phieu": {"TANG": 1.00, "DIEU_CHINH": 0.60, "GIAM": 0.00},
    "phan_phoi": {"giam_toi_thieu": 0.002, "cua_so": 25, "nguong_dieu_chinh": 5},
}

# ------------------------------------- Tru 2: bien an toan kep (chot 04/10/2026)
# Quyet dinh 6-7 (muc 14). Moi ma trong THAM_DINH_FILE co dinh_gia.than_trong va
# dinh_gia.co_so (nghin dong/CP). Mua khi gia <= (1 - BIEN_AN_TOAN_MIN) x
# than_trong; thieu mot trong hai, than_trong > co_so, hoac dinh_gia.can_dung_lai
# = true -> KHONG mua. Ban toan bo khi gia dong cua >= co_so.
BIEN_AN_TOAN_MIN = 0.15

# ------------------------------------------------ Quy trinh 4 buoc (Triet_ly_dau_tu_FF5)
# 25/08/2026 — dong bo voi Triet_ly_dau_tu_FF5.docx, ban da chot. Ba thay doi:
#
#  1) BUY_CHECKLIST cu them "trend_quality_r2_min" va "min_relative_strength_6m"
#     vao bo loc cung. Bang CL.1 cua tai lieu chi co DUNG 5 dieu kien, va R^2 la
#     THANH PHAN XEP HANG o Buoc 2 (trong so 10%), khong phai dieu kien loc.
#     Bien mot thanh phan xep hang thanh cua ai cung phai qua la sai thiet ke —
#     no loai mat nhung ma chi thua o dung cai tieu chi le ra chi de xep truoc sau.
#     -> Bo loc cung = dung LOC o tren, khong hon.
#
#  2) Buoc 3 (tham dinh doanh nghiep/nganh/vi mo) va Buoc 4 (dinh gia + diem mua)
#     la CON NGUOI lam, co quyen phu quyet. Khong duoc suy ra tu du lieu gia.
#     Ket luan nap tu THAM_DINH_FILE. Thieu ket luan = CHUA duoc mua (khong phai
#     mac dinh dat) — "mot ma dung dau bang xep hang van bi loai neu khong qua
#     duoc lop nay".
#
#  3) investment_score cu (thang 10) da bi bo. No goi momentum gia la "quality"
#     va "valuation", tuc dan nhan co ban cho du lieu gia — dung loai nham lan
#     ma chinh tai lieu canh bao ("Quy se tu khen minh vi nhung thu von chi la
#     phoi nhiem rui ro").
THAM_DINH_FILE = "data/tham_dinh.json"

# ------------------------------------------ Ro co ban top-down (chot 01/10/2026)
# Nhanh NGUOI cua khung moi. Nam trong THAM_DINH_FILE:
#   "_ro_co_ban": {
#       "ngay_chot": "YYYY-MM-DD",   # ro chi co hieu luc khi da chot
#       "vi_mo":  {"ket_luan": "...", "ngay": "..."},
#       "nganh":  {"<ten nganh>": {"trong_ro": true|false, "ly_do": "...", "ngay": "..."}}
#   }
#   va o tung ma: "trong_ro", "nganh", "uu_tien", "ngay_vao_ro", "ly_do_ro".
#
# Mot ma NAM TRONG RO khi va chi khi: ro da chot, vi mo co ket luan, nganh cua ma
# co trong ro nganh voi trong_ro = true, ma co trong_ro = true, buoc3 = "dat"
# (V1-V5 o tang doanh nghiep) va luan_diem_con_nguyen khong phai false.
# Ba trang thai, KHONG PHAI HAI:
#   True  — trong ro: duoc mua (neu qua Tang 1 va Buoc 4 dat)
#   False — bi loai o tang nao do: quy tac thoat 4 -> BAN toan bo
#   None  — thieu ket luan hoac nhap sai (vd nganh khong co trong ro nganh):
#           KHONG mua, KHONG tu dong ban, in PHAI CHAM TAY. Quy ve False thi mot
#           loi go nham se ban vi the; quy ve True thi thieu phieu van duoc mua.
# Hang rao thoi diem (quyet dinh 4): moi thay doi ro phai chot TRUOC ban quet
# cua ky do. lt_screener.py canh bao neu THAM_DINH_FILE sua sau file quet.
RO_CO_BAN_KHOA = "_ro_co_ban"

# Hieu luc luat moi va han chot lenh mua cua ky dau tien (quyet dinh 9, 11).
# Ky 01/10 la lan doi luat thu tu giua cuoc thi, do Quy chon. Qua han chot ma
# phieu V1-V5 + Buoc 4 chua xong -> phan von do nam tien toi ky 01/11.
TOP_DOWN = {
    "hieu_luc_tu": "2026-10-01",
    "han_chot_lenh_mua": {"2026-10-01": "2026-10-05"},   # ky soat -> han chot
}

# Gia tri hop le cho ket luan tham dinh thu cong.
THAM_DINH_TRANG_THAI = ("dat", "loai", "cho", "chua")
#   dat  — qua duoc lop nay
#   loai — bi phu quyet, ghi kem ly do
#   cho  — dat ve doanh nghiep nhung gia chua hop ly -> danh sach cho (Buoc 4)
#   chua — chua tham dinh (mac dinh khi thieu ban ghi)

# ------------------------------------------------ Buoc 3a CANSLIM (chot 22/09/2026)
# Buoc 3 moi = 3a CANSLIM (MAY cham) + 3b nam cong phu quyet V1-V5 (NGUOI, phieu
# trong THAM_DINH_FILE). Ba truc A/B/C cua phieu cu bo. Ma phai qua CA HAI.
# Xem CHIEN_LUOC_DAI_HAN.md muc 12.
#
# NGUONG DANG KY TRUOC — chot TRUOC khi chay canslim_backtest.py. Khong duoc sua
# sau khi da xem ket qua; muon doi thi ghi thanh mot phep do moi, co ngay moi.
#   C : LNST co dong me quy gan nhat so cung ky >= +25% (quy truoc phai > 0)
#       VA doanh thu thuan quy >= +15% (ngan hang: thu nhap lai thuan)
#       Dung LNST co dong me thay EPS: co tuc co phieu lam meo EPS lich su.
#   A : LNST TTM tang >= 20%/nam binh quan 3 nam, KHONG nam nao giam, VA ROE TTM >= 15%
#   N : gia cach dinh 252 phien <= 15%  (phan "cai moi" khong do bang may)
#   S : KL TB phien tang / KL TB phien giam, 50 phien >= 1,0
#   L : phan vi RS 12T (bo 1T) trong TOAN RO >= 0,70
#   I : BO khoi luat may — Viet Nam khong co du lieu tuong duong 13F
#   M : VNINDEX > MA200 VA MA50 > MA200; sai -> khong mua moi ma nao
# Ket luan: nhanh chinh  = M, C, A cong cung + (N + S + L) >= 2
#           doi chung    = ca sau chu (M, C, A, N, S, L) deu qua
CANSLIM = {
    "c_lnst_yoy_min": 0.25,
    "c_doanh_thu_yoy_min": 0.15,
    "a_cagr_3n_min": 0.20,
    "a_roe_min": 0.15,
    "n_cach_dinh_max": 0.15,
    "s_ty_le_kl_min": 1.0,
    "s_so_phien": 50,
    "l_phan_vi_min": 0.70,
    "diem_nsl_min": 2,
    # Co canh bao cho Buoc 3b (KHONG chan mua): dong tien HDKD 3 nam / LNST 3 nam
    "v3_nguong": 0.50,
}

# Cong tac theo ket qua kiem dinh dang ky truoc (muc 12):
#   dat nguong (>=3/4 pha duong, t>=2, sut giam khong te hon qua 3 diem %) -> True
#   chua ket luan (1 <= t < 2) -> False: van cham va ghi so, KHONG chan lenh
#   bac bo (t < 1)            -> go khoi bao cao
# V1-V5 (Buoc 3b, phieu nguoi) VAN CHAN trong moi truong hop.
CANSLIM_CHAN_MUA = False

# Ket qua kiem dinh dang ky truoc, chay 22/09/2026 (data/canslim_backtest_20260922.json):
# 0/4 pha duong, t TB = -1,00 -> BAC BO (ca doi chung, nhanh V3 va nhanh chi-M cung bac bo).
# Theo luat da chot: go 3a khoi bao cao screener, chi luu ho so. canslim.py van chay
# duoc de ghi so tien ve truoc neu quy muon dang ky mot phep do MOI (muc 12).
# Gia tri: "chua_do" | "chap_nhan" | "chua_ket_luan" | "bac_bo"
CANSLIM_KET_QUA = "bac_bo"

# Bang CL.4 — quy tac thoat, ra soat dau moi thang. Chi can MOT cau tra loi
# phu dinh la ban toan bo vi the.
# 01/10/2026: BO quy tac 3 (thu hang <= 40% ro da loc) cung voi Buoc 2. Muc 8 da
# do: tac dong cua no la nhieu (+2,44/-2,71/-2,52/+3,06 diem %, TB +0,07).
# Quy tac 4 doi nghia: "ma khong con trong ro co ban" (loai o tang nao cung vay).
# 04/10/2026 (muc 14): BO quy tac 2 (RS 12T < -5%) — quyet dinh 4. THEM ban khi
# gia cham gia tri co so (quyet dinh 6) va che do GIAM (quyet dinh 1). So hieu
# cu giu de doi chieu.
SELL_CHECKLIST = {
    "close_below_97pct_ma200": True,   # 1. Gia con tren MA200 sau khi tru dem 3%?
    "ngoai_ro_co_ban": True,           # 4. Con nam trong ro co ban top-down?
    "cham_co_so": True,                # 6. Gia dong cua da cham gia tri co so?
    "che_do_giam": True,               # Tru 1: thi truong sang che do GIAM?
    "stop_loss_25pct": True,           # chan cung -25% so voi gia von
}

# --------------------------------- Quy tac thu nam — ban theo cam quan cua quy
# 11/09/2026 — user quyet dinh DOI quy tac 5. Ban cu "ban bot khi gia qua nong"
# (ba dau hieu do duoc: gia-MA50 / dinh gia / KL can dan) bi thay bang:
#     "Ban theo cam quan thi truong cua quy" — dung de tang tinh chu dong ung
#     pho voi bien dong thi truong.
# Ly do bo ban cu: chua tung chay duoc tren du lieu that. Dau hieu (a) can 500
# quan sat nhung TradingView Desktop 3.4.1 bao `setVisibleRange: Not implemented`
# -> moi ma chi co 300 bar (251 quan sat). Ban cu luu o
# data/lt_config_backup_20260911.py (khoi QUA_NONG).
#
# Hai tham so do USER CHOT ngay 11/09/2026 (truoc khi co lenh nao theo luat moi):
#   * ban toi da 50% moi vi the moi lan — KHONG dong han. Thoat toan phan van
#     chi do bon quy tac da kiem chung quyet dinh.
#   * KY SOAT LAY LAI QUYEN — lenh cam quan chi co hieu luc toi ky soat dau
#     thang ke tiep. Toi ngay soat, allocator duoc mua lai phan da ban neu ma
#     con qua bon quy tac. Muon giu tien lau hon thi quy ghi `gia_han_den` va
#     `ngay_ghi_gia_han` TRUOC ngay soat; khi do allocator khong mua lai phan
#     da ban toi het ngay gia han.
#
# Day la quy tac TUY NGHI: NGUOI quyet, he thong khong sinh tin hieu va khong
# co backtest nao dung sau no. Vi vay moi lenh phai ghi vao LENH_QUY_TAC_5 TRUOC
# KHI DAT LENH — de bao cao cuoi ky tach duoc phan dong gop cua he thong va cua
# cam quan, va de do duoc cam quan cua quy dung/sai bao nhieu lan.
#
# KHONG AP DUNG HOI TO: lenh ban 50 VHM ngay 07/09/2026 van la LENH NGOAI LUAT #1
# (luat moi chua ton tai luc do). Doi nhan no thanh "quy tac 5" bay gio la dan
# nhan luat len mot quyet dinh da co san.
QUY_TAC_5 = {
    "ten": "Ban theo cam quan thi truong cua quy",
    "hieu_luc_tu": "2026-09-11",
    "loai": "tuy nghi",                 # nguoi quyet, khong co tin hieu may
    "ty_le_ban_toi_da": 0.50,           # moi lan, tren KL dang giu truoc lenh
    "hieu_luc_toi": "ky soat ke tiep",  # roi he thong lay lai quyen
    # Truong bat buoc cua moi ban ghi trong LENH_QUY_TAC_5. Thieu -> allocator
    # in [THIEU] ben canh lenh do.
    "truong_bat_buoc": ("so", "ngay", "ma", "kl_truoc", "kl_ban", "gia",
                        "cam_quan", "trang_thai"),
}

# So lenh quy tac 5. Mau mot ban ghi:
#   {
#     "so": 1, "ngay": "2026-09-20", "dm": "DM2", "ma": "STB",
#     "kl_truoc": 100, "kl_ban": 50, "gia": 80_000,
#     "cam_quan": "vi sao quy thay thi truong xau — ghi bang loi, TRUOC khi dat lenh",
#     "sai_khi": "dieu gi xay ra thi quy thua nhan cam quan nay sai (tuy chon)",
#     "trang_thai": "da khop",          # "cho khop" | "da khop" | "huy"
#     "gia_han_den": None,              # "YYYY-MM-DD" neu muon qua ky soat
#     "ngay_ghi_gia_han": None,         # phai TRUOC ngay soat moi co hieu luc
#   }
LENH_QUY_TAC_5 = [
    {
        "so": 1,
        "ngay": "2026-09-16",
        "dm": "DM2",
        "ma": "BSR",
        "kl_truoc": 200,
        "kl_ban": 100,
        "gia": 31_300,
        "cam_quan": "Lo ngai chung ve thi truong/nhom nganh dau khi noi rieng, "
                    "khong phai vi tin xau rieng cua BSR. BSR da tang 27.000 -> "
                    "31.300 (+15,9%) tu gia von.",
        "sai_khi": None,
        "trang_thai": "da khop",
        # 16/09/2026 — GIA HAN. Ly do: cung ngay, lich ra soat them ky bo sung
        # 21/09 (xem LICH_SOAT). Khong gia han thi ky 21/09 lay lai quyen va
        # allocator mua lai 100 BSR vao 22/09 — DUNG 4 PHIEN sau khi ban, tuc
        # he thong huy cam quan cua quy truoc khi cam quan do kip dung hay sai.
        # Gia han toi 30/09 giu dung loi da viet o tren ("hieu luc toi ky soat
        # 01/10"), khong dai hon. Dung co che gia han DA CO SAN trong luat chot
        # 11/09 — khong phai doi luat lan nua.
        # Hop le: ngay_ghi_gia_han 16/09 < ngay soat 21/09 (va < 01/10).
        "gia_han_den": "2026-09-30",
        "ngay_ghi_gia_han": "2026-09-16",
        # ⚠️ Ghi nhan trung thuc: ban ghi nay duoc lap SAU KHI lenh da khop
        # (nguoi bao "da ban" roi moi ghi cam_quan), khong dung thu tu QUY_TAC_5
        # doi hoi ("ghi TRUOC khi dat lenh"). Day la mot le sai quy trinh da
        # biet, ghi lai de ky sau doi chieu — khong phai de bao chua.
    },
    {
        "so": 2,
        "ngay": "2026-09-22",
        "dm": "DM2",
        "ma": "MSB",
        "kl_truoc": 840,
        "kl_ban": 300,
        "gia": 13_450,
        "cam_quan": "Lo ngai chung ve nganh ngan hang/thi truong, khong phai vi "
                    "tin xau rieng cua MSB.",
        "sai_khi": None,
        "trang_thai": "da khop",
        # 23/09/2026 — GIA HAN toi het cuoc thi (user quyet). Khong gia han thi
        # ky soat 01/10 lay lai quyen va allocator mua lai 350 MSB (so 2 + so 3)
        # — chi con ~11 phien toi 17/10, chiu phi khu hoi. 17/10 la ngay
        # het_hieu_luc_sau cua LICH_SOAT (thu Bay; phien cuoi 16/10).
        # Hop le: ngay_ghi_gia_han 23/09 < ngay soat 01/10.
        # ⚠️ Ghi nhan trung thuc: quyet dinh gia han dua ra SAU KHI da thay MSB
        # tang 13.050 (21/09) -> 13.500 (22/09) -> 14.100 (trua 23/09, +8,0%)
        # trong khi VNINDEX chi +1,1%. Tuc la gia han sau khi da biet cam quan
        # dang bat loi ~225.000 d (~0,37% NAV DM2) — ghi lai de bao cao cuoi ky
        # doc duoc, khong phai de bao chua.
        "gia_han_den": "2026-10-17",
        "ngay_ghi_gia_han": "2026-09-23",
        # ⚠️ Ghi nhan trung thuc: ban ghi nay duoc lap SAU KHI lenh da khop,
        # cung mot le sai quy trinh nhu ban ghi so 1 (BSR 16/09).
    },
    {
        "so": 3,
        "ngay": "2026-09-22",
        "dm": "DM2",
        "ma": "MSB",
        "kl_truoc": 540,
        "kl_ban": 50,
        "gia": 13_500,
        "cam_quan": "Lo ngai chung ve nganh ngan hang/thi truong, khong phai vi "
                    "tin xau rieng cua MSB — cung ly do voi lenh so 2, khop rieng "
                    "gia trong cung phien.",
        "sai_khi": None,
        "trang_thai": "da khop",
        # 23/09/2026 — GIA HAN cung quyet dinh voi lenh so 2 (xem ghi chu o do).
        "gia_han_den": "2026-10-17",
        "ngay_ghi_gia_han": "2026-09-23",
        # ⚠️ Ghi nhan trung thuc: ban ghi nay duoc lap SAU KHI lenh da khop,
        # cung mot le sai quy trinh nhu ban ghi so 1 va so 2.
    },
    {
        "so": 4,
        "ngay": "2026-10-01",
        "dm": "DM2",
        "ma": "MSB",
        "kl_truoc": 490,
        "kl_ban": 50,
        "gia": 14_200,
        "cam_quan": "Co cau danh muc an toan truoc bien dong cua thi truong, can "
                    "lai so co phieu dang nam thanh lo chan.",
        "sai_khi": None,
        "trang_thai": "da khop",
        # Khong gia han: hieu luc toi ky soat ke tiep 01/11. MSB van bi so 2-3
        # khoa mua lai toi 17/10 va Buoc 4 dang "cho" nen allocator khong mua.
        "gia_han_den": None,
        "ngay_ghi_gia_han": None,
        # ⚠️ Ghi nhan trung thuc: khop 01/10 (chinh ngay ky soat, TRUOC khi ro
        # co ban chot), ban ghi lap ngay 04/10 — SAU KHI khop, le sai quy trinh
        # thu tu (so 1-4 deu vay). Phan "lo chan" la ly do van hanh, khong phai
        # cam quan; ghi nguyen loi user.
    },
]
# 04/10/2026 — QUY TAC 5 BI BO HAN tu 05/10/2026 (CHIEN_LUOC_DAI_HAN.md muc 14,
# quyet dinh 11; dung cam ket #5 tr.70 bao cao giai doan 1: "bo han quy tac ban
# theo cam quan"). So tren giu lai lam ho so; khong ghi them lenh nao. Hai gia
# han so 2-3 (MSB, toi 17/10) van het hieu luc dung ngay da ghi.
QUY_TAC_5["het_hieu_luc_tu"] = "2026-10-05"

# ------------------------------------------- Phieu lenh (chot 04/10/2026)
# Cam ket #5 tr.70 bao cao giai doan 1: "lenh nao thieu ly do ghi truoc gio dat
# thi nguoi phe duyet tu choi". Moi lenh — trong luat hay khong — phai co mot
# phieu o day, ghi_luc TRUOC gio dat. lt_allocator.py in phieu cua ngay chay va
# gan co [CHUA CO PHIEU] cho moi lenh no sinh ra ma chua co phieu.
# Sau khi khop: doi trang_thai, ghi gia khop vao data/so_giao_dich.json va sua
# HOLDINGS / TIEN_MAT. Mau:
#   {"so": 1, "ghi_luc": "YYYY-MM-DD HH:MM", "ngay_dat": "YYYY-MM-DD",
#    "dm": "DM2", "chieu": "BAN" | "MUA", "ma": "XYZ", "kl": 100,
#    "loai_lenh": "...", "can_cu": "luat nao, so lieu nao",
#    "trang_thai": "cho dat" | "da khop" | "khop mot phan" | "huy", "ghi_chu": ""}
_CAN_CU_GIAM_0510 = ("CHE DO GIAM (muc 14, quyet dinh 1): VNINDEX dong cua 02/10/2026 "
                     "1.737,71 < 0,97 x MA200 1.795,65 = 1.741,78, va < nguong "
                     "1.738,84 da cong bo tr.72 bao cao giai doan 1 ('Quy chuyen "
                     "toan bo sang tien mat'). Ban toan bo vi the, khoa mua moi.")
PHIEU_LENH = [
    {"so": 1, "ghi_luc": "2026-10-04 18:57", "ngay_dat": "2026-10-05", "dm": "DM2",
     "chieu": "BAN", "ma": "MSB", "kl": 440,
     "loai_lenh": "phien sang 05/10; nguoi dat chon ATO/LO, ghi gia khop vao so",
     "can_cu": _CAN_CU_GIAM_0510,
     "trang_thai": "khop mot phan",
     "khop": "300 @14.050 ngay 05/10; con 140 CP thuong chua ve TK",
     "ghi_chu": "KIEM TRUOC KHI DAT: 140 CP thuong (GDKHQ 28/08) da ve tai khoan "
                "chua — so_giao_dich chua xac nhan. Chua ve thi chi ban duoc 300; "
                "140 CP con lai ban ngay khi ve. 40 CP la lo le (bang lo le)."},
    {"so": 2, "ghi_luc": "2026-10-04 18:57", "ngay_dat": "2026-10-05", "dm": "DM2",
     "chieu": "BAN", "ma": "BSR", "kl": 100,
     "loai_lenh": "phien sang 05/10; nguoi dat chon ATO/LO, ghi gia khop vao so",
     "can_cu": _CAN_CU_GIAM_0510,
     "trang_thai": "da khop", "khop": "100 @30.350 ngay 05/10", "ghi_chu": ""},
    {"so": 3, "ghi_luc": "2026-10-04 18:57", "ngay_dat": "2026-10-05", "dm": "DM2",
     "chieu": "BAN", "ma": "DHC", "kl": 200,
     "loai_lenh": "phien sang 05/10; nguoi dat chon ATO/LO, ghi gia khop vao so",
     "can_cu": _CAN_CU_GIAM_0510,
     "trang_thai": "da khop", "khop": "200 @38.100 ngay 05/10 (+ co tuc tien 190.000d)",
     "ghi_chu": "DHC la ma duy nhat phieu Dat (5/6) — van ban: che do Giam ban "
                "toan bo, khong mien tru theo ma (tr.72)."},
]

# ------------------------------------------------- Lich ra soat (chot 16/09/2026)
# Nguyen tac nen KHONG DOI: ra soat dau moi thang; trong thang khong lam gi tru
# chan cung -25%. Mua ban chi dien ra SAU mot ky soat.
#
# NGOAI LE MOT LAN, CHI CHO DM2 — ban to chuc cuoc thi chia lam 2 giai doan,
# giai doan 2 bat dau 21/09/2026. Do la moc BAO CAO: khong reset diem (return
# tinh lien tuc 17/08 -> ~17/10), khong doi luat dau tu, khong doi von. Vi cuoc
# thi khong bat dau vao dau thang nen lich soat dau thang lech pha voi lich cuoc
# thi; them mot ky soat tai 21/09 de danh muc nop bao cao giai doan 2 la danh
# muc da duoc soat. Ky 01/10 VAN GIU.
#
# Ly do moc nay KHONG phai "doi luat de hop thuc hoa mot quyet dinh da co san"
# (loi da ghi hai lan trong so): moc 21/09 do BTC dat, khong phai quy chon, va
# duoc chot HOM NAY 16/09 — truoc khi nhin bat ky bang lenh nao cua ky do.
# Bao cao cuoi ky phai ghi lai dung cau nay.
#
# Trinh tu ky 21/09: quet sau dong cua 21/09 -> lt_screener.py ra BANG XEP HANG
# -> lam phieu Buoc 3/4 vao data/tham_dinh.json -> lt_allocator.py ra BANG LENH
# -> dat lenh 22/09. Tham dinh sau bang xep hang nhung TRUOC bang lenh: dung
# hang rao da chot o CHIEN_LUOC_DAI_HAN.md muc 166. Neu tham dinh khong kip dem
# 21/09 thi lenh BAN van dat 22/09 (khong can tham dinh), lenh MUA cho phieu day
# du, han chot 25/09; qua han thi phan mua doi ky 01/10.
LICH_SOAT = {
    "chu_ky": "thang",                      # dau moi thang, nhu cu
    "ngay_bo_sung": ("2026-09-21",),         # ky soat them, chi DM2
    "dm_bo_sung": ("DM2",),
    "het_hieu_luc_sau": "2026-10-17",        # cuoc thi ket thuc -> ve nhip dau thang
    "han_chot_lenh_mua_ky_bo_sung": "2026-09-25",
}

# ------------------------------------------- Khoa chong whipsaw (chot 16/09/2026)
# Ma bi BON QUY TAC THOAT ban o ky bo sung 21/09 KHONG duoc allocator mua lai o
# ky 01/10; khoa toi 01/11.
#
# Ly do: quy tac 3 so THU HANG VI TRI trong ro DA LOC (~12 ma) nen top 40% chi
# la 5 ma — day la rang buoc chinh va rat nhay. Da do duoc: them DUNG 1 bar lam
# r252 cua VNINDEX tut 4,3 diem phan tram, day HCM khoi bo loc va MSB khoi top
# 40% du gia khong doi. Soat lai sau 7 phien la lay mau lai dung chi bao nhay
# nhat -> rui ro ban mot ma tot vi nhieu 1 bar roi mua lai ngay ky sau.
#
# Phi KHONG phai ly do: khu hoi 0,26% tren mot o ~3,5tr chi ~9.100 d (0,015%
# NAV). Ly do la tranh thoat mot vi the dung luc no hoi.
#
# Allocator TU GHI vao day sau khi in bang lenh ky bo sung? KHONG — ghi tay, vi
# moi thu trong duong ong nay deu phai co dau vet nguoi. Mau ban ghi:
#   {"ngay": "2026-09-21", "dm": "DM2", "ma": "BSR", "kl": 100,
#    "ly_do_ban": "quy tac 3 — thu hang 0,55 > 0,40"}
KHOA_WHIPSAW = {
    "khoa_den": "2026-11-01",       # allocator khong mua lai truoc ngay nay
    "ban_ky_bo_sung": [
        {"ngay": "2026-09-22", "dm": "DM2", "ma": "VHM", "kl": 50,
         "ly_do_ban": "quy tac thoat 4 — phu quyet Buoc 3 13/09 (truc A=0, C=0), "
                      "luan diem gay. Ban het vi the."},
    ],
}

# ------------------------------------------ Dieu khoan bao luu (chot 16/09/2026)
# LUAT MOI KHONG HOI TO — cung nguyen tac da dung ngay 11/09/2026 voi quy tac 5.
#
# Moi TIN HIEU BAN da phat sinh TRUOC 16/09/2026 giu nguyen lich thuc thi CU
# (ky soat 01/10). Moc 21/09 chi ap cho tin hieu MOI sinh tu chinh dot quet
# 21/09.
#
# Vi sao can dieu khoan nay: neu khong co no thi viec them moc 21/09 se tu dong
# day som mot lenh ban da nam cho san 7 phien — tuc doi lich de thay doi so phan
# cua mot quyet dinh da co truoc khi lich doi. Viet thanh dieu khoan CHUNG chu
# khong mien tru theo ma, vi mien tru dich danh mot ma la dung thu ma lop phu
# quyet sinh ra de chong.
BAO_LUU_TIN_HIEU = {
    "moc": "2026-09-16",            # tin hieu phat sinh TRUOC ngay nay thi bao luu
    "thuc_thi_tai": "2026-10-01",   # lich cu, khong doi
    "ma": {
        "VHM": "Phu quyet Buoc 3 ngay 13/09/2026 (cong V3+V4, truc C = 0) -> quy "
               "tac 4 hong. Tin hieu phat sinh 13/09, TRUOC moc 16/09 -> giu "
               "lich thuc thi cu: ban o ky 01/10, KHONG bi ky 21/09 day som.\n"
               "        ⚠️ 22/09/2026 — THUC TE KHONG DUNG NHU TREN: ban TOAN BO "
               "50 CP da khop 22/09 (theo trinh tu ky soat bo sung 21/09, "
               "LICH_SOAT: 'lenh BAN van dat 22/09'), SOM hon lich thuc thi da "
               "chot o day (01/10). User xac nhan day la lenh khop som theo "
               "trinh tu 21/09, khong phai quyet dinh khac. Dieu khoan bao luu "
               "o day KHONG duoc tuan thu dung nhu viet — ghi lai trung thuc de "
               "ky sau doi chieu, khong sua lai cho khop voi thuc te.",
    },
}

# --------------------------------------------------------- Diem suc manh RS: DA BO
# 01/10/2026 — Buoc 2 (xep hang RS) bi xoa theo quyet dinh cua user. Ban cu:
#   RS_WEIGHTS = {"rs_252_skip21": 0.40, "rs_126": 0.30, "rs_63": 0.20, "trend_r2": 0.10}
# Viec chon ma nao truoc chuyen sang `uu_tien` cua ro co ban (nguoi), pha hoa
# bang ATR. 04/10/2026: RS 12T (bo 1T) cung bi bo o Tang 1 va o quy tac thoat 2
# (muc 14, quyet dinh 4-5) — chi con in ra de doi chieu.

# ------------------------------------------------------------- Luat thoat
# Thay cho trailing 3% / toi da 20 phien cua khung cuoc thi.
# Ra soat HANG THANG nhung chi BAN khi luat kich hoat (khong tai co cau toan bo).
#
# ⚠️ 26/08/2026 — phat bieu cu "ra soat hang quy lam CAGR tut 13,9% -> 7,1%, toc
# do THOAT quan trong hon toc do vao" DA BI DAO NGUOC khi do lai. TB 4 pha luoi,
# pham vi ro da loc: hang thang 9,05% / sut giam -29,5%; hang QUY 11,67% /
# sut giam -24,1%, tot hon o 3/4 pha. Nhung bien do nhanh hang quy rat rong
# (4,84-18,99%) nen do cung khong phai bang chung cho chieu nguoc lai.
# Giu ra soat hang thang vi do la con so DA CHOT trong Triet_ly_dau_tu_FF5.docx
# ("Quy ra soat toan bo danh muc vao dau moi thang"), khong phai vi du lieu
# ung ho. Chi tiet: data/backtest_pha_luoi_20260826.json.
# 04/10/2026 (muc 14, quyet dinh 12) — NHIP XET thay "chi ra soat dau thang":
#   * MOI PHIEN (gia dong cua, dat lenh phien sau): che do GIAM, chan cung -25%,
#     cham gia tri co so, va quy tac 4 (nguoi danh luan_diem_con_nguyen = false
#     khi day bay cham — "xet ngay khi co so lieu"). Chay:
#     LOAI_KY=hang_ngay python lt_allocator.py, hoac kiem nhanh python lt_che_do.py
#   * KY SOAT dau thang: them luat MA200, cat ve tran che do, va moi lenh MUA.
#     Lenh mua van chi dien ra sau mot ky soat (giu nguyen giai doan 1).
EXIT = {
    "chu_ky_ra_soat": "thang",   # Ky soat dau thang; xem nhip xet o tren
    "giu_khi": {                 # Con du TAT CA thi giu tiep, khong dong vao
        "gia_tren": "0,97 x MA200",       # dem 3% duoi MA200, tranh bi quet nhieu
        # "rs_12t_toi_thieu": -0.05 — DA BO 04/10/2026 (quyet dinh 4)
        "trong_ro_co_ban": True,          # quy tac 4 moi (01/10/2026)
        "duoi_gia_tri_co_so": True,       # quyet dinh 6 (04/10/2026)
        "che_do_khac_giam": True,         # quyet dinh 1 (04/10/2026)
        # "thu_hang_rs": 0.40 — DA BO 01/10/2026 cung Buoc 2
    },
    # 04/10/2026 — DOI True -> False (quyet dinh 6). Bao cao giai doan 1 da cong
    # bo "Quy ban khi gia cham gia tri kich ban co so" (tr.72). Bang chung cu cua
    # "khong chot loi" (56.496 lenh, luat A) do muc tieu +3% trong <= 20 phien —
    # mot phep do NGAN HAN, khong phai ban khi cham gia tri noi tai; no khong ap
    # thang vao day. Cai gia da biet: cat som doanh nghiep tang truong (dieu
    # Fisher se khong lam). Chong doi cot gon: co_so chi duoc NANG bang phieu moi
    # dua tren BCTC moi, ghi TRUOC khi gia cham.
    "khong_co_muc_tieu_chot_lai": False,
    "ban_khi_cham_co_so": True,
    "xet_hang_ngay": ("che_do_giam", "stop_loss_25pct", "cham_co_so", "ngoai_ro_co_ban"),
    "xet_ky_soat": ("close_below_97pct_ma200",),
    "bien_khong_giao_dich": 0.03,         # lech ty trong < 3% NAV thi khong dieu chinh
    "stop_tham_hoa": 0.25,                # Chan cung mot chieu: -25% so voi gia von
}
# (lich su) Do nhay nguong "thu_hang_rs" (CAGR, khong co bien khong giao dich):
#   0,25 -> 11,9% | 0,33 -> 12,6% | 0,40 -> 15,4% | 0,50 -> 10,3% | 0,60 -> 8,1%
# Quy tac nay da bo 01/10/2026.

# --------------------------------------------------------------- Chi phi
# 15/09/2026 — SUA BIEU PHI theo bang phi that cua cong ty chung khoan.
# Truoc do ca he thong chay tren 0,15% mua / 0,25% ban. Con so 0,15% khong lay
# tu dau ca — no la mot gia dinh duoc go vao tu dau va chua bao gio duoc doi
# chieu voi sao ke.
#
# HAU QUA DA DO DUOC: tinh tren 15 lenh da khop (gia tri mua+ban 106.755.000 d),
# bieu phi cu tinh ra tong chi phi 199.973 d trong khi so that la 125.244 d
# -> he thong da bao cao THUA 74.729 d chi phi, tuc bao cao THIEU dung so tien
# do o tien mat suot bon tuan. Day chinh la khoang chenh 75.000 d giua NAV he
# thong (60.369.027) va NAV sao ke (60.444.027) ma ban ghi 15/09 ban dau da
# doan nham la "truot gia trong phien".
#
# KIEM CHUNG NGUOC: giai nguoc tu NAV sao ke 60.444.027 ra muc thue an trong do
# duoc 0,0993% — tuc dung 0,10%. Bieu phi moi vi the duoc xac nhan bang mot so
# lieu ben ngoai, khong phai bang gia dinh.
FEE_BUY = 0.0008               # phi dich vu theo gia tri giao dich
FEE_SELL = 0.0008 + 0.0010     # phi dich vu + thue TNCN chuyen nhuong 0,1%

# Phi luu ky VSD — 0,3 d / co phieu / thang, tinh tren so du chung khoan.
# KHONG phai phi giao dich: no chay theo THOI GIAN NAM GIU chu khong theo lenh,
# nen khong duoc cong vao FEE_BUY/FEE_SELL. Voi quy mo DM2 (~1.300 CP) no vao
# khoang 390 d/thang — khong du lam doi bat ky quyet dinh nao, nhung phai co
# trong so de bao cao cuoi ky khong bo sot khoan nao.
PHI_LUU_KY_CP_THANG = 0.3

LOT = 100

# --------------------------------------------------------------- Nganh: DA BO
# 01/10/2026 (quyet dinh 8): tran nganh dung NGANH NGUOI GAN trong ro co ban
# (truong "nganh" cua tung ma, phai trung mot khoa trong _ro_co_ban.nganh).
# Bang viet tay cu chi phu 112 ma HOSE; ma ICB cap 2 tu Vietcap chi in ra de
# doi chieu. Ma o giao diem ma thieu nganh -> KHONG mua, in canh bao.
# Ban cu: data/lt_config_backup_20261001.py
