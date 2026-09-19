"""
lt_config.py — Tham so CHIEN LUOC DAI HAN (long-term), dung chung cho ca 2 danh muc.

Thay the hoan toan khung "P(ve nhat)" cu:
  - Ham muc tieu cu: P(ve nhat) trong cuoc thi 2 thang -> khuyen khich tap trung,
    bo qua rui ro, chon ma bien dong cao. DA BO.
  - Ham muc tieu moi: toi da hoa E[log NAV] dai han (toc do gop von), tuc la
    uu tien (a) chon ma manh hon thi truong ben vung, (b) khong de mot ma lam
    hong danh muc, (c) chi phi giao dich thap vi vong quay cham.

Ba tru cot:
  1. LOC (hard filter)   — chi choi trong xu huong tang dai han + du thanh khoan.
  2. XEP HANG (RS score) — suc manh tuong doi so voi VNINDEX, nhieu khung thoi gian.
  3. PHAN BO (risk parity) — ty trong ~ 1/bien dong, co tran ma va tran nganh.

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
    #   Thu ve: 100 x 31.300 = 3.130.000 - phi/thue 0,18% (5.634) = 3.124.366.
    #   Lai chua thuc hien tren 100 CP con lai: (31.300-27.000) x 100 = +430.000
    #   gop / +427.840 rong (tru phi mua con lai 2.160). Sao luu truoc khi sua:
    #   data/lt_config_backup_20260916.py
    "DM2": [("MSB", 840, 13_333), ("BSR", 100, 27_000),
            ("VHM", 50, 69_000), ("DHC", 200, 36_600)],
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
TIEN_MAT = {"DM1": 0, "DM2": 35_924_122}

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
    "rs_252_duong": True,      # Phai vuot VNINDEX 12 thang qua
    # ATR chi la CHAN AN TOAN (loai ma qua dau co), khong phai tieu chi chon.
    # Bien dong duoc xu ly o khau PHAN BO (ty trong ~ 1/ATR), khong o khau loc —
    # neu loc bang ATR ta se vut bo nhung ma manh nhat chi vi chung dong manh.
    "atr_max": 0.060,
}

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

# Gia tri hop le cho ket luan tham dinh thu cong.
THAM_DINH_TRANG_THAI = ("dat", "loai", "cho", "chua")
#   dat  — qua duoc lop nay
#   loai — bi phu quyet, ghi kem ly do
#   cho  — dat ve doanh nghiep nhung gia chua hop ly -> danh sach cho (Buoc 4)
#   chua — chua tham dinh (mac dinh khi thieu ban ghi)

# Bang CL.4 — bon quy tac thoat, ra soat dau moi thang. Chi can MOT cau tra loi
# phu dinh la ban toan bo vi the.
SELL_CHECKLIST = {
    "close_below_97pct_ma200": True,   # 1. Gia con tren MA200 sau khi tru dem 3%?
    "rs_12m_below_minus_5pct": True,   # 2. Con manh hon VNINDEX khung 12 thang?
    "rank_below_40pct": True,          # 3. Con trong nhom dan dau bang xep hang?
    "luan_diem_gay": True,             # 4. Luan diem doanh nghiep con nguyen ven?
    "stop_loss_25pct": True,           # ngoai le duy nhat giua hai ky ra soat
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
        "gia_han_den": None,
        "ngay_ghi_gia_han": None,
        # ⚠️ Ghi nhan trung thuc: ban ghi nay duoc lap SAU KHI lenh da khop
        # (nguoi bao "da ban" roi moi ghi cam_quan), khong dung thu tu QUY_TAC_5
        # doi hoi ("ghi TRUOC khi dat lenh"). Day la mot le sai quy trinh da
        # biet, ghi lai de ky sau doi chieu — khong phai de bao chua.
    },
]

# --------------------------------------------------------- Diem suc manh RS
# Trong so cho tung khung. Bo qua 21 phien gan nhat trong khung 12 thang
# (skip-month) vi dao chieu ngan han lam nhieu tin hieu momentum.
RS_WEIGHTS = {"rs_252_skip21": 0.40, "rs_126": 0.30, "rs_63": 0.20, "trend_r2": 0.10}

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
EXIT = {
    "chu_ky_ra_soat": "thang",   # Ra soat dau moi thang. KHONG theo doi theo phien.
    "giu_khi": {                 # Con du CA BA thi giu tiep, khong dong vao
        "gia_tren": "0,97 x MA200",       # dem 3% duoi MA200, tranh bi quet nhieu
        "rs_12t_toi_thieu": -0.05,        # duoc phep thua VNINDEX toi 5% moi bi ban
        "thu_hang_rs": 0.40,              # con trong top 40% bang xep hang
    },
    "khong_co_muc_tieu_chot_lai": True,   # Giu nguyen bai hoc cua luat C
    "bien_khong_giao_dich": 0.03,         # lech ty trong < 3% NAV thi khong dieu chinh
    "stop_tham_hoa": 0.25,                # Chan cung mot chieu: -25% so voi gia von
}
# Do nhay nguong "thu_hang_rs" (CAGR, khong co bien khong giao dich):
#   0,25 -> 11,9% | 0,33 -> 12,6% | 0,40 -> 15,4% | 0,50 -> 10,3% | 0,60 -> 8,1%
# 0,40 la DINH cua be mat nen phai coi la may; dieu dang tin la CA HO 0,25-0,60
# deu thang VNINDEX (7,5%). Dung 0,40 nhung khong duoc coi con so nay la thieng.

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

# --------------------------------------------------------------- Nganh
# Phan nganh tho de ap tran nganh (khong can chuan ICB, chi can chan tap trung).
NGANH = {
    "ACB": "Ngan hang", "BID": "Ngan hang", "CTG": "Ngan hang", "EIB": "Ngan hang",
    "HDB": "Ngan hang", "LPB": "Ngan hang", "MBB": "Ngan hang", "MSB": "Ngan hang",
    "NAB": "Ngan hang", "OCB": "Ngan hang", "SHB": "Ngan hang", "SSB": "Ngan hang",
    "STB": "Ngan hang", "TCB": "Ngan hang", "TPB": "Ngan hang", "VCB": "Ngan hang",
    "VIB": "Ngan hang", "VPB": "Ngan hang", "EVF": "Ngan hang",
    "BSI": "Chung khoan", "FTS": "Chung khoan", "HCM": "Chung khoan",
    "SSI": "Chung khoan", "VCI": "Chung khoan", "VIX": "Chung khoan",
    "VND": "Chung khoan", "DSE": "Chung khoan",
    "BVH": "Bao hiem",
    "BCM": "Bat dong san", "DIG": "Bat dong san", "DXG": "Bat dong san",
    "HDC": "Bat dong san", "HDG": "Bat dong san", "KBC": "Bat dong san",
    "KDH": "Bat dong san", "KOS": "Bat dong san", "NLG": "Bat dong san",
    "NTL": "Bat dong san", "NVL": "Bat dong san", "PDR": "Bat dong san",
    "SIP": "Bat dong san", "SJS": "Bat dong san", "SZC": "Bat dong san",
    "VHM": "Bat dong san", "VIC": "Bat dong san", "VRE": "Bat dong san",
    "CII": "Ha tang", "CTD": "Ha tang", "CTR": "Ha tang", "HHV": "Ha tang",
    "PC1": "Ha tang", "VCG": "Ha tang", "GEE": "Ha tang", "GEX": "Ha tang",
    "HPG": "Thep", "HSG": "Thep", "NKG": "Thep",
    "BSR": "Dau khi", "GAS": "Dau khi", "PLX": "Dau khi", "PVD": "Dau khi",
    "PVT": "Dau khi", "PVS": "Dau khi", "DCM": "Hoa chat", "DGC": "Hoa chat",
    "DPM": "Hoa chat", "CSV": "Hoa chat", "PHR": "Cao su", "GVR": "Cao su",
    "NT2": "Dien", "POW": "Dien", "PPC": "Dien", "REE": "Dien", "BWE": "Nuoc",
    "GMD": "Cang bien", "HAH": "Cang bien", "VSC": "Cang bien", "TMS": "Cang bien",
    "SCS": "Hang khong", "HVN": "Hang khong", "VJC": "Hang khong", "VTP": "Chuyen phat",
    "MWG": "Ban le", "FRT": "Ban le", "DGW": "Ban le", "PNJ": "Ban le",
    "MSN": "Tieu dung", "SAB": "Tieu dung", "VNM": "Tieu dung", "PAN": "Tieu dung",
    "KDC": "Tieu dung", "SBT": "Tieu dung", "TLG": "Tieu dung", "MSH": "Det may",
    "GIL": "Det may", "BAF": "Chan nuoi", "DBC": "Chan nuoi", "HAG": "Nong nghiep",
    "ANV": "Thuy san", "VHC": "Thuy san", "ASM": "Thuy san", "LSS": "Nong nghiep",
    "FPT": "Cong nghe", "CMG": "Cong nghe", "ELC": "Cong nghe",
    "IMP": "Duoc", "DHC": "Giay", "HT1": "Xi mang", "BMP": "Vat lieu",
    "PTB": "Vat lieu", "VGC": "Vat lieu", "TCH": "Bat dong san", "VPI": "Bat dong san",
}
