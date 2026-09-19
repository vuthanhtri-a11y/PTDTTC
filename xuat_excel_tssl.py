# -*- coding: utf-8 -*-
"""
xuat_excel_tssl.py — Xuat file Excel doi chieu TY SUAT DO DUOC voi TY SUAT DOI HOI.

Muc dich: cho thay khoang cach giua hai con so den tu dau, va nhung don bay nao
co the dong duoc khoang cach do — kem muc do tin cay cua tung don bay.

Diem then chot ve thiet ke file: MOI o tinh toan deu la CONG THUC EXCEL, khong
phai so cung. Doi mot gia dinh o sheet "Tham so" thi toan bo file tinh lai. Neu
ghi so cung thi file chi la mot buc anh, khong dung de tim huong giai quyet duoc.

Nguon so:
  * Ty suat doi hoi  : Bang CS.1 cua Triet_ly_dau_tu_FF5.docx (ban da chot)
  * Ty suat do duoc  : data/backtest_pha_luoi_20260826.json (4 pha luoi, 52 thang)

Chay: PYTHONIOENCODING=utf-8 python xuat_excel_tssl.py
"""

import io
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, Reference, Series, ScatterChart
from openpyxl.chart.label import DataLabelList
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

OUT = "data/TSSL_do_duoc_vs_doi_hoi.xlsx"

# ---------------------------------------------------------------- Dinh dang
F_TIEU_DE = Font(bold=True, size=14, color="1F3864")
F_HEAD = Font(bold=True, size=10, color="FFFFFF")
F_DAM = Font(bold=True, size=10)
F_TH = Font(italic=True, size=9, color="666666")
FILL_HEAD = PatternFill("solid", fgColor="1F3864")
FILL_NHOM = PatternFill("solid", fgColor="D9E2F3")
FILL_TOT = PatternFill("solid", fgColor="C6EFCE")
FILL_XAU = PatternFill("solid", fgColor="F4CCCC")
FILL_CANH = PatternFill("solid", fgColor="FFF2CC")
FILL_NHAP = PatternFill("solid", fgColor="FFF9E6")   # o duoc phep sua
# LUU Y: cong thuc va ma dinh dang trong file .xlsx phai dung DAU CHAM thap phan
# (chuan bat bien cua OOXML). Excel se tu hien thi thanh dau phay theo ngon ngu may.
# Viet dau phay o day se lam Excel bao loi cong thuc va dinh dang sai.
THIN = Side(style="thin", color="BFBFBF")
VIEN = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
PCT = '0.00"%"'
PP = '+0.00;-0.00'       # diem phan tram, co dau


def head(ws, row, cols, width=None):
    for i, c in enumerate(cols, start=1):
        cell = ws.cell(row=row, column=i, value=c)
        cell.font = F_HEAD
        cell.fill = FILL_HEAD
        cell.border = VIEN
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    if width:
        for i, w in enumerate(width, start=1):
            ws.column_dimensions[get_column_letter(i)].width = w


def tieu_de(ws, text, sub=None):
    ws["A1"] = text
    ws["A1"].font = F_TIEU_DE
    if sub:
        ws["A2"] = sub
        ws["A2"].font = F_TH


def vien_vung(ws, r1, r2, c1, c2):
    for r in range(r1, r2 + 1):
        for c in range(c1, c2 + 1):
            ws.cell(row=r, column=c).border = VIEN


def ghi_chu(ws, row, text, col=1, span=8):
    c = ws.cell(row=row, column=col, value=text)
    c.font = F_TH
    c.alignment = Alignment(wrap_text=True, vertical="top")
    ws.merge_cells(start_row=row, start_column=col, end_row=row, end_column=col + span - 1)
    ws.row_dimensions[row].height = 30


# ---------------------------------------------------------------- Du lieu
def nap():
    bt = json.load(io.open("data/backtest_pha_luoi_20260826.json", encoding="utf-8"))
    phas = [bt[f"pha{i}"] for i in range(4)]
    return bt, phas


# Bang CS.1 — Triet_ly_dau_tu_FF5.docx, 24/08/2026
NHAN_TO = [
    ("Rf — lãi suất phi rủi ro (TPCP 10 năm, 21/08/2026)", None, None, 4.56),
    ("MKT — rủi ro thị trường", 0.682, 8.13, None),
    ("SMB — quy mô", -0.131, 1.71, None),
    ("HML — giá trị", -0.116, 3.49, None),
    ("RMW — khả năng sinh lời", 0.118, 3.47, None),
    ("CMA — cường độ đầu tư", -0.170, 1.26, None),
]


def build():
    bt, phas = nap()
    wb = Workbook()

    # ============================================================ 1. THAM SO
    ws = wb.active
    ws.title = "1. Tham số"
    tieu_de(ws, "THAM SỐ ĐẦU VÀO",
            "Ô nền vàng là ô được phép sửa. Sửa xong, toàn bộ các sheet khác tự tính lại.")

    ws["A4"] = "A. Mô hình Fama–French 5 nhân tố (Bảng CS.1, bản chốt 24/08/2026)"
    ws["A4"].font = F_DAM
    head(ws, 5, ["Thành phần", "Hệ số tải b", "Phần bù λ (%/năm)", "Đóng góp (điểm %)"],
         width=[46, 14, 18, 18, 14, 14, 14, 14])
    r = 6
    for ten, b, lam, cong in NHAN_TO:
        ws.cell(row=r, column=1, value=ten).font = F_DAM
        if b is None:
            ws.cell(row=r, column=2, value="—").alignment = Alignment(horizontal="center")
            ws.cell(row=r, column=3, value="—").alignment = Alignment(horizontal="center")
            ws.cell(row=r, column=4, value=cong).number_format = "0.00"
        else:
            cb = ws.cell(row=r, column=2, value=b)
            cb.number_format = "0.000"
            cb.fill = FILL_NHAP
            cl = ws.cell(row=r, column=3, value=lam)
            cl.number_format = "0.00"
            cl.fill = FILL_NHAP
            cc = ws.cell(row=r, column=4, value=f"=B{r}*C{r}")
            cc.number_format = "0.00"
        r += 1
    RE_ROW = r
    ws.cell(row=r, column=1, value="TỶ SUẤT SINH LỜI ĐÒI HỎI (Re)").font = F_DAM
    ws.cell(row=r, column=4, value=f"=SUM(D6:D{r-1})").number_format = "0.00"
    ws.cell(row=r, column=4).font = F_DAM
    ws.cell(row=r, column=4).fill = FILL_CANH
    vien_vung(ws, 5, r, 1, 4)
    ghi_chu(ws, r + 1,
            "Re = Rf + b_MKT×MRP + b_SMB×λ_SMB + b_HML×λ_HML + b_RMW×λ_RMW + b_CMA×λ_CMA.  "
            "Bốn λ phi thị trường đã được thu hẹp một nửa về 0 vì không nhân tố nào có ý nghĩa "
            "thống kê vững. Hệ số tải suy từ đặc điểm danh mục, chưa hồi quy trên chuỗi nhân tố thật.")

    r += 3
    ws.cell(row=r, column=1, value="B. Đối chiếu CAPM (cùng Rf và cùng phần bù thị trường)").font = F_DAM
    r += 1
    ws.cell(row=r, column=1, value="Re theo CAPM = Rf + b_MKT × MRP")
    ws.cell(row=r, column=4, value="=D6+B7*C7").number_format = "0.00"
    CAPM_ROW = r
    r += 1
    ws.cell(row=r, column=1, value="Chênh lệch FF5 − CAPM (điểm %)")
    ws.cell(row=r, column=4, value=f"=D{RE_ROW}-D{CAPM_ROW}").number_format = PP
    vien_vung(ws, r - 2, r, 1, 4)
    ghi_chu(ws, r + 1,
            "Chênh lệch nhỏ vì bốn độ nghiêng nhân tố gần như triệt tiêu nhau: thưởng cho khả năng "
            "sinh lời bù lại phạt cho quy mô lớn, định giá đắt và cường độ đầu tư mạnh. Giá trị của "
            "việc đổi mô hình không nằm ở mức hạ ngưỡng mà ở chỗ biết mình đang cầm loại rủi ro gì.")

    r += 3
    ws.cell(row=r, column=1, value="C. Kết quả kiểm định — 4 pha lưới lấy mẫu, 52 tháng, đã trừ phí 0,4%/vòng quay").font = F_DAM
    r += 1
    PHA_HEAD = r
    head(ws, r, ["Pha lưới (ngày cuối)", "Quỹ — CAGR (%)", "VN-Index (%)",
                 "Vượt chỉ số (điểm %)", "Sụt giảm tối đa (%)", "Alpha tháng (%)", "Thống kê t"])
    r += 1
    PHA_R0 = r
    for i, p in enumerate(phas):
        ws.cell(row=r, column=1, value=f"Pha {i} — {p['ngay_cuoi']}").font = F_DAM
        ws.cell(row=r, column=2, value=p["B1"]["cagr"] * 100).number_format = "0.00"
        ws.cell(row=r, column=3, value=p["VNINDEX"] * 100).number_format = "0.00"
        ws.cell(row=r, column=4, value=f"=B{r}-C{r}").number_format = PP
        ws.cell(row=r, column=5, value=p["B1"]["mdd"] * 100).number_format = "0.0"
        ws.cell(row=r, column=6, value=p["B1"]["alpha"] * 100).number_format = "0.000"
        ws.cell(row=r, column=7, value=p["B1"]["t"]).number_format = "0.00"
        r += 1
    PHA_R1 = r - 1
    ws.cell(row=r, column=1, value="TRUNG BÌNH 4 PHA").font = F_DAM
    for c in (2, 3, 4, 5, 6, 7):
        L = get_column_letter(c)
        cell = ws.cell(row=r, column=c, value=f"=AVERAGE({L}{PHA_R0}:{L}{PHA_R1})")
        cell.number_format = PP if c == 4 else ("0,000" if c == 6 else "0,00")
        cell.font = F_DAM
        cell.fill = FILL_NHOM
    TB_ROW = r
    r += 1
    ws.cell(row=r, column=1, value="Biên độ (thấp nhất → cao nhất)").font = F_DAM
    ws.cell(row=r, column=2, value=f'=TEXT(MIN(B{PHA_R0}:B{PHA_R1}),"0.00")&" → "&TEXT(MAX(B{PHA_R0}:B{PHA_R1}),"0.00")')
    ws.cell(row=r, column=3, value=f'=TEXT(MIN(C{PHA_R0}:C{PHA_R1}),"0.00")&" → "&TEXT(MAX(C{PHA_R0}:C{PHA_R1}),"0.00")')
    BIEN_ROW = r
    vien_vung(ws, PHA_HEAD, r, 1, 7)
    ghi_chu(ws, r + 1,
            "Bốn pha khác nhau ở chỗ neo lưới lấy mẫu tháng vào tuần nào — chỉ lệch nhau một tuần. "
            "Chúng KHÔNG phải bốn quan sát độc lập vì dùng chung phần lớn dữ liệu; lấy trung bình "
            "loại được sự may rủi của một lần rút thăm, nhưng không nhân bốn lượng thông tin.")

    # ============================================================ 2. KHOANG CACH
    ws2 = wb.create_sheet("2. Khoảng cách")
    tieu_de(ws2, "ĐO ĐƯỢC so với ĐÒI HỎI — khoảng cách và ý nghĩa")
    ws2.column_dimensions["A"].width = 52
    for c in "BCDE":
        ws2.column_dimensions[c].width = 16

    r = 4
    ws2.cell(row=r, column=1, value="Chỉ tiêu").font = F_HEAD
    for i, c in enumerate(["Chỉ tiêu", "Giá trị (%/năm)", "Nguồn"], start=1):
        cell = ws2.cell(row=r, column=i, value=c)
        cell.font = F_HEAD
        cell.fill = FILL_HEAD
        cell.border = VIEN
    ws2.column_dimensions["C"].width = 42
    r += 1
    DO_DUOC = r
    ws2.cell(row=r, column=1, value="① Tỷ suất ĐO ĐƯỢC của Quỹ (TB 4 pha)").font = F_DAM
    ws2.cell(row=r, column=2, value=f"='1. Tham số'!B{TB_ROW}").number_format = "0.00"
    ws2.cell(row=r, column=3, value="Backtest 52 tháng, 4 pha lưới, đã trừ phí")
    r += 1
    VNI = r
    ws2.cell(row=r, column=1, value="② VN-Index mua & giữ (TB 4 pha)").font = F_DAM
    ws2.cell(row=r, column=2, value=f"='1. Tham số'!C{TB_ROW}").number_format = "0.00"
    ws2.cell(row=r, column=3, value="Cùng kỳ, cùng phương pháp đo")
    r += 1
    DOI_HOI = r
    ws2.cell(row=r, column=1, value="③ Tỷ suất ĐÒI HỎI theo FF5 (Re)").font = F_DAM
    ws2.cell(row=r, column=2, value=f"='1. Tham số'!D{RE_ROW}").number_format = "0.00"
    ws2.cell(row=r, column=3, value="Bảng CS.1 — ngưỡng bù đủ rủi ro đang mang")
    r += 1
    ws2.cell(row=r, column=1, value="④ Tỷ suất phi rủi ro (TPCP 10 năm)").font = F_DAM
    ws2.cell(row=r, column=2, value="='1. Tham số'!D6").number_format = "0.00"
    ws2.cell(row=r, column=3, value="Không rủi ro, không công sức")
    RF_R = r
    r += 2

    ws2.cell(row=r, column=1, value="KHOẢNG CÁCH").font = F_DAM
    ws2.cell(row=r, column=1).fill = FILL_NHOM
    r += 1
    G_ALPHA = r
    ws2.cell(row=r, column=1, value="Alpha theo FF5  =  ① − ③").font = F_DAM
    c = ws2.cell(row=r, column=2, value=f"=B{DO_DUOC}-B{DOI_HOI}")
    c.number_format = PP
    c.font = F_DAM
    ws2.cell(row=r, column=3, value="Âm = chưa bù đủ phần rủi ro đang mang")
    r += 1
    ws2.cell(row=r, column=1, value="Vượt chỉ số  =  ① − ②").font = F_DAM
    ws2.cell(row=r, column=2, value=f"=B{DO_DUOC}-B{VNI}").number_format = PP
    ws2.cell(row=r, column=3, value="Thống kê t từ 0,04 đến 0,24 → không phân biệt được với 0")
    r += 1
    ws2.cell(row=r, column=1, value="Phần bù trên lãi suất phi rủi ro  =  ① − ④").font = F_DAM
    ws2.cell(row=r, column=2, value=f"=B{DO_DUOC}-B{RF_R}").number_format = PP
    ws2.cell(row=r, column=3, value="Phần thưởng cho toàn bộ rủi ro và công sức bỏ ra")
    vien_vung(ws2, 4, r, 1, 3)

    # to mau o alpha
    r += 2
    ws2.cell(row=r, column=1,
             value="Đọc đúng ba con số trên").font = F_DAM
    r += 1
    for txt in [
        "Alpha FF5 âm KHÔNG có nghĩa hệ thống thua lỗ. Nó có nghĩa: với đúng những "
        "rủi ro mà danh mục đang phơi nhiễm (beta thị trường 0,682, nghiêng vốn hoá lớn, "
        "nghiêng tăng trưởng, nghiêng doanh nghiệp sinh lời tốt, nghiêng mở rộng tài sản "
        "nhanh), một nhà đầu tư có thể kỳ vọng 9,67%/năm mà không cần chọn mã. Quỹ đạt "
        "thấp hơn thế.",
        "Nhưng khoảng cách −0,6 điểm phần trăm nằm gọn trong sai số. Thống kê t của alpha "
        "vượt chỉ số chỉ 0,04–0,24, và bản thân tỷ suất đo được dao động 7,65–10,49% tuỳ "
        "pha lưới. Kết luận trung thực: KHÔNG phân biệt được Quỹ với ngưỡng đòi hỏi, chứ "
        "không phải Quỹ chắc chắn dưới ngưỡng.",
        "Vì vậy sheet 4 chia hướng giải quyết làm hai nhóm: nhóm nâng tử số (tỷ suất đạt "
        "được) và nhóm hạ mẫu số (ngưỡng đòi hỏi). Nhóm thứ hai chắc chắn về mặt cơ học; "
        "nhóm thứ nhất thì không.",
    ]:
        ghi_chu(ws2, r, txt, span=5)
        r += 1

    # Bieu do cot: bon moc
    ch = BarChart()
    ch.type = "col"
    ch.title = "Bốn mốc so sánh (%/năm)"
    ch.y_axis.title = "%/năm"
    ch.height, ch.width = 9, 18
    data = Reference(ws2, min_col=2, min_row=DO_DUOC, max_row=RF_R)
    cats = Reference(ws2, min_col=1, min_row=DO_DUOC, max_row=RF_R)
    ch.add_data(data, titles_from_data=False)
    ch.set_categories(cats)
    ch.dataLabels = DataLabelList()
    ch.dataLabels.showVal = True
    ch.legend = None
    ws2.add_chart(ch, "F4")

    # ============================================================ 3. PHAN RA FF5
    ws3 = wb.create_sheet("3. Phân rã đòi hỏi")
    tieu_de(ws3, "TỶ SUẤT ĐÒI HỎI ĐẾN TỪ ĐÂU — và mỗi hệ số tải đáng bao nhiêu")
    ws3.column_dimensions["A"].width = 46
    for c in "BCDEFG":
        ws3.column_dimensions[c].width = 17

    r = 4
    head(ws3, r, ["Thành phần", "Hệ số tải b", "Phần bù λ", "Đóng góp (điểm %)",
                  "Nếu b tăng 0,10", "Nếu b giảm 0,10", "Độ nhạy |Δ| trên 0,10 b"])
    r += 1
    R0 = r
    for i, (ten, b, lam, cong) in enumerate(NHAN_TO):
        src = 6 + i           # dong tuong ung tren sheet 1
        ws3.cell(row=r, column=1, value=ten).font = F_DAM
        if b is None:
            for c in range(2, 8):
                ws3.cell(row=r, column=c, value="—").alignment = Alignment(horizontal="center")
            ws3.cell(row=r, column=4, value=f"='1. Tham số'!D{src}").number_format = "0.00"
        else:
            ws3.cell(row=r, column=2, value=f"='1. Tham số'!B{src}").number_format = "0.000"
            ws3.cell(row=r, column=3, value=f"='1. Tham số'!C{src}").number_format = "0.00"
            ws3.cell(row=r, column=4, value=f"=B{r}*C{r}").number_format = "0.00"
            ws3.cell(row=r, column=5, value=f"=(B{r}+0.1)*C{r}").number_format = "0.00"
            ws3.cell(row=r, column=6, value=f"=(B{r}-0.1)*C{r}").number_format = "0.00"
            ws3.cell(row=r, column=7, value=f"=ABS(0.1*C{r})").number_format = "0.00"
        r += 1
    R1 = r - 1
    ws3.cell(row=r, column=1, value="TỔNG — Re").font = F_DAM
    ws3.cell(row=r, column=4, value=f"=SUM(D{R0}:D{R1})").number_format = "0.00"
    ws3.cell(row=r, column=4).fill = FILL_CANH
    ws3.cell(row=r, column=4).font = F_DAM
    vien_vung(ws3, 4, r, 1, 7)
    r += 2
    ghi_chu(ws3, r,
            "Cột cuối trả lời câu hỏi quan trọng nhất của sheet này: ngưỡng đòi hỏi KHÔNG cố định, "
            "nó là hàm của những gì Quỹ đang nắm. Beta thị trường là đòn bẩy lớn nhất — mỗi 0,10 "
            "beta đáng 0,81 điểm phần trăm ngưỡng, tức lớn hơn cả khoảng cách hiện tại. Giữ tiền mặt "
            "cũng hạ beta hiệu dụng, nên tỷ trọng tiền mặt cao vừa hạ tỷ suất đạt được vừa hạ ngưỡng.",
            span=7)
    r += 1
    ghi_chu(ws3, r,
            "Bốn nhân tố còn lại nhỏ hơn hẳn: 0,10 hệ số tải chỉ đáng 0,13–0,35 điểm phần trăm. "
            "Điều đó có nghĩa việc xoay danh mục sang mã giá trị hơn hay quy mô nhỏ hơn gần như "
            "không dịch được ngưỡng — chỉ beta mới dịch được.", span=7)

    ch = BarChart()
    ch.type = "bar"
    ch.title = "Đóng góp vào tỷ suất đòi hỏi (điểm %)"
    ch.height, ch.width = 9, 18
    ch.add_data(Reference(ws3, min_col=4, min_row=R0, max_row=R1), titles_from_data=False)
    ch.set_categories(Reference(ws3, min_col=1, min_row=R0, max_row=R1))
    ch.dataLabels = DataLabelList()
    ch.dataLabels.showVal = True
    ch.legend = None
    ws3.add_chart(ch, "I4")

    ch2 = BarChart()
    ch2.type = "bar"
    ch2.title = "Độ nhạy ngưỡng: mỗi 0,10 hệ số tải đáng bao nhiêu điểm %"
    ch2.height, ch2.width = 9, 18
    ch2.add_data(Reference(ws3, min_col=7, min_row=R0 + 1, max_row=R1), titles_from_data=False)
    ch2.set_categories(Reference(ws3, min_col=1, min_row=R0 + 1, max_row=R1))
    ch2.dataLabels = DataLabelList()
    ch2.dataLabels.showVal = True
    ch2.legend = None
    ws3.add_chart(ch2, "I24")

    # ============================================================ 4. HUONG GIAI QUYET
    ws4 = wb.create_sheet("4. Hướng giải quyết")
    tieu_de(ws4, "CÁC ĐÒN BẨY ĐÓNG KHOẢNG CÁCH — kèm mức độ tin cậy",
            "Đòn bẩy chỉ đáng làm khi hiệu ứng trung bình lớn hơn biên độ nhiễu giữa các pha.")
    ws4.column_dimensions["A"].width = 40
    for c in "BCDEFGH":
        ws4.column_dimensions[c].width = 15
    ws4.column_dimensions["I"].width = 60

    ts = bt["thamso_4pha"]
    so_o = ts["so_o"]
    tb_cagr = sum(p["B1"]["cagr"] for p in phas) / 4 * 100

    # (ten, cagr moi TB, cagr theo 4 pha, so pha thang, ghi chu)
    don_bay = [
        ("Giảm số ô từ 10 xuống 5",
         [so_o[f"pha{i}"]["5"] * 100 for i in range(4)], 4,
         "Đo được ở 4/4 pha. NHƯNG bản đo cũ kết luận NGƯỢC LẠI (10 ô tốt nhất). "
         "Hai phép đo trái nhau ⇒ tham số này không đo được ở cỡ mẫu 52 tháng."),
        ("Giảm số ô từ 10 xuống 6",
         [so_o[f"pha{i}"]["6"] * 100 for i in range(4)], 3,
         "Như trên, và yếu hơn: thắng 3/4 pha."),
        ("Rà soát hằng quý thay vì hằng tháng",
         [x * 100 for x in ts["chu_ky_ra_soat"]["theo_pha_quy"]], 3,
         "Thắng 3/4 pha, sụt giảm nông hơn 5,3 điểm. NHƯNG biên độ 4,84–18,99% "
         "là rộng nhất bảng, và trái với bản chốt (Phần 3 quy định rà soát đầu mỗi tháng)."),
        ("Xếp hạng trên toàn rổ thay vì rổ đã lọc",
         [p["A"]["cagr"] * 100 for p in phas], 4,
         "Hiệu ứng lớn nhất (+3,0 điểm) và thắng 4/4 pha, sụt giảm cũng nông hơn. "
         "NHƯNG trái trực tiếp với Bước 2 của bản chốt FF5."),
        ("Cân bằng đều thay vì 1/biến động",
         [None, None, None, ts["phan_bo"]["can_bang_deu"]["cagr"] * 100], 0,
         "CHỈ CÓ SỐ TRUNG BÌNH (đặt ở cột Trung bình), không lưu số theo pha. "
         "Lợi nhuận nhỉnh hơn 0,24 điểm nhưng sụt giảm SÂU HƠN ở 4/4 pha → đánh đổi xấu."),
        ("Tắt hẳn quy tắc thoát số 3",
         [p["tat_qt3"]["cagr"] * 100 for p in phas], 2,
         "Hiệu ứng trung bình +0,07 điểm, thắng 2/4 pha. Đây là nhiễu thuần tuý."),
    ]

    r = 4
    head(ws4, r, ["Đòn bẩy", "Pha 0", "Pha 1", "Pha 2", "Pha 3", "Trung bình",
                  "Δ so với hiện tại", "Thắng mấy pha", "Đánh giá"])
    r += 1
    DB0 = r
    for ten, vals, thang, gc in don_bay:
        ws4.cell(row=r, column=1, value=ten).font = F_DAM
        co_theo_pha = all(v is not None for v in vals)
        if co_theo_pha:
            for i, v in enumerate(vals):
                ws4.cell(row=r, column=2 + i, value=v).number_format = "0.00"
            ws4.cell(row=r, column=6, value=f"=AVERAGE(B{r}:E{r})").number_format = "0.00"
        else:
            for i in range(4):
                ws4.cell(row=r, column=2 + i, value="—").alignment = Alignment(horizontal="center")
            tbv = next(v for v in vals if v is not None)
            ws4.cell(row=r, column=6, value=tbv).number_format = "0.00"
        d = ws4.cell(row=r, column=7, value=f"=F{r}-'2. Khoảng cách'!B{DO_DUOC}")
        d.number_format = PP
        d.font = F_DAM
        ws4.cell(row=r, column=8, value=f"{thang}/4").alignment = Alignment(horizontal="center")
        g = ws4.cell(row=r, column=9, value=gc)
        g.alignment = Alignment(wrap_text=True, vertical="top")
        g.font = F_TH
        ws4.row_dimensions[r].height = 46
        r += 1
    DB1 = r - 1
    vien_vung(ws4, 4, DB1, 1, 9)

    r += 1
    ws4.cell(row=r, column=1, value="ĐÒN BẨY PHÍA NGƯỠNG ĐÒI HỎI (hạ mẫu số)").font = F_DAM
    ws4.cell(row=r, column=1).fill = FILL_NHOM
    r += 1
    head(ws4, r, ["Thay đổi", "Ngưỡng mới (%)", "Δ ngưỡng", "", "", "", "", "", "Đánh giá"])
    r += 1
    NG0 = r
    nguong = [
        ("Giảm beta thị trường 0,682 → 0,60", "=('1. Tham số'!D6+0.60*'1. Tham số'!C7"
         "+'1. Tham số'!B8*'1. Tham số'!C8+'1. Tham số'!B9*'1. Tham số'!C9"
         "+'1. Tham số'!B10*'1. Tham số'!C10+'1. Tham số'!B11*'1. Tham số'!C11)",
         "Hạ ngưỡng 0,67 điểm → ĐỦ để đảo dấu alpha FF5 (từ −0,62 thành +0,05) mà không "
         "cần cải thiện tỷ suất đạt được chút nào. Đạt bằng cách giữ nhiều tiền mặt hơn hoặc "
         "chọn mã beta thấp. Nhưng tiền mặt cũng kéo tỷ suất đạt được xuống — phải đo ròng."),
        ("Giảm beta thị trường 0,682 → 0,55", "=('1. Tham số'!D6+0.55*'1. Tham số'!C7"
         "+'1. Tham số'!B8*'1. Tham số'!C8+'1. Tham số'!B9*'1. Tham số'!C9"
         "+'1. Tham số'!B10*'1. Tham số'!C10+'1. Tham số'!B11*'1. Tham số'!C11)",
         "Hạ ngưỡng 1,07 điểm → alpha FF5 thành +0,45. Beta 0,55 tương ứng danh mục "
         "phòng thủ hơn hẳn hoặc tỷ trọng tiền mặt cao hơn nữa."),
        ("Nếu phần bù thị trường hạ 8,13 → 7,00", "=('1. Tham số'!D6+'1. Tham số'!B7*7.00"
         "+'1. Tham số'!B8*'1. Tham số'!C8+'1. Tham số'!B9*'1. Tham số'!C9"
         "+'1. Tham số'!B10*'1. Tham số'!C10+'1. Tham số'!B11*'1. Tham số'!C11)",
         "Không phải đòn bẩy — là rủi ro giả định. Cho thấy ngưỡng nhạy thế nào với "
         "một tham số Quỹ không kiểm soát và cũng không đo được."),
    ]
    for ten, ct, gc in nguong:
        ws4.cell(row=r, column=1, value=ten).font = F_DAM
        ws4.cell(row=r, column=2, value=ct).number_format = "0.00"
        ws4.cell(row=r, column=3, value=f"=B{r}-'2. Khoảng cách'!B{DOI_HOI}").number_format = PP
        g = ws4.cell(row=r, column=9, value=gc)
        g.alignment = Alignment(wrap_text=True, vertical="top")
        g.font = F_TH
        ws4.row_dimensions[r].height = 40
        r += 1
    vien_vung(ws4, NG0 - 1, r - 1, 1, 9)

    r += 2
    ws4.cell(row=r, column=1, value="KẾT LUẬN VỀ HƯỚNG GIẢI QUYẾT").font = F_DAM
    ws4.cell(row=r, column=1).fill = FILL_CANH
    r += 1
    for txt in [
        "1. Không đòn bẩy nào ở nhóm trên đáng tin. Đòn bẩy mạnh nhất (đổi phạm vi xếp "
        "hạng, +3,0 điểm) trái trực tiếp với bản chốt; hai đòn bẩy tiếp theo (số ô, chu kỳ "
        "rà soát) đều đã cho kết luận NGƯỢC LẠI ở phép đo trước, nên chúng đo cái nhiễu "
        "chứ không đo cái thật. Đổi tham số theo phép đo mới nhất chỉ là thay một lần rút "
        "thăm bằng một lần rút thăm khác.",
        "2. Đòn bẩy duy nhất chắc chắn về mặt cơ học nằm ở phía ngưỡng: hạ beta. Mỗi 0,10 "
        "beta đáng 0,81 điểm phần trăm ngưỡng — lớn hơn cả khoảng cách hiện tại. Nhưng đây "
        "là con dao hai lưỡi: hạ beta bằng cách giữ tiền mặt cũng hạ tỷ suất đạt được, nên "
        "phải đo ròng chứ không được kết luận từ một vế.",
        "3. Hướng đúng nhất lại không phải một đòn bẩy tham số: cỡ mẫu quá nhỏ. 52 tháng cho "
        "thống kê t khoảng 0,2. Muốn phân biệt được +0,7 điểm phần trăm với 0 ở mức tin cậy "
        "thông thường, cần khoảng 15–20 năm dữ liệu tháng, hoặc chuyển sang dữ liệu tuần để "
        "tăng số quan sát. Đó là việc đáng làm trước khi đổi bất kỳ tham số nào.",
        "4. Việc nên làm ngay và không tốn gì: bổ sung chuỗi nhân tố Việt Nam tự dựng "
        "(xay_dung_factor_ff5_vn.py) để hồi quy hệ số tải THẬT thay vì suy từ đặc điểm danh "
        "mục. Hiện cả năm hệ số tải đều là ước lượng, nên bản thân ngưỡng 9,67% cũng có sai "
        "số chưa được đo. Có thể khoảng cách −0,6 điểm nhỏ hơn sai số của chính cái ngưỡng.",
    ]:
        ghi_chu(ws4, r, txt, span=9)
        ws4.row_dimensions[r].height = 46
        r += 1

    ch = BarChart()
    ch.type = "col"
    ch.title = "Đòn bẩy phía tỷ suất đạt được — trung bình 4 pha (%/năm)"
    ch.y_axis.title = "%/năm"
    ch.height, ch.width = 10, 20
    ch.add_data(Reference(ws4, min_col=6, min_row=DB0, max_row=DB1), titles_from_data=False)
    ch.set_categories(Reference(ws4, min_col=1, min_row=DB0, max_row=DB1))
    ch.dataLabels = DataLabelList()
    ch.dataLabels.showVal = True
    ch.legend = None
    ws4.add_chart(ch, "K4")

    # ============================================================ 5. RUI RO - LOI NHUAN
    ws5 = wb.create_sheet("5. Rủi ro–Lợi nhuận")
    tieu_de(ws5, "MỖI PHƯƠNG ÁN ĐÁNH ĐỔI THẾ NÀO",
            "Trục hoành: mức sụt giảm tối đa. Trục tung: tỷ suất. Góc trên-trái là tốt nhất.")
    ws5.column_dimensions["A"].width = 40
    for c in "BCD":
        ws5.column_dimensions[c].width = 20

    r = 4
    head(ws5, r, ["Phương án", "Sụt giảm tối đa (%)", "CAGR (%/năm)", "Vượt ngưỡng đòi hỏi"])
    r += 1
    RR0 = r
    pa = [
        ("Hệ thống hiện hành (rổ đã lọc, 10 ô, tháng)",
         sum(p["B1"]["mdd"] for p in phas) / 4 * 100, tb_cagr),
        ("Xếp hạng toàn rổ",
         sum(p["A"]["mdd"] for p in phas) / 4 * 100,
         sum(p["A"]["cagr"] for p in phas) / 4 * 100),
        ("Rà soát hằng quý",
         ts["chu_ky_ra_soat"]["hang_quy"]["mdd"] * 100,
         ts["chu_ky_ra_soat"]["hang_quy"]["cagr"] * 100),
        ("Cân bằng đều",
         ts["phan_bo"]["can_bang_deu"]["mdd"] * 100,
         ts["phan_bo"]["can_bang_deu"]["cagr"] * 100),
        ("Tắt quy tắc thoát 3",
         sum(p["tat_qt3"]["mdd"] for p in phas) / 4 * 100,
         sum(p["tat_qt3"]["cagr"] for p in phas) / 4 * 100),
    ]
    for ten, mdd, cagr in pa:
        ws5.cell(row=r, column=1, value=ten).font = F_DAM
        ws5.cell(row=r, column=2, value=abs(mdd)).number_format = "0.0"
        ws5.cell(row=r, column=3, value=cagr).number_format = "0.00"
        c = ws5.cell(row=r, column=4, value=f"=C{r}-'2. Khoảng cách'!B{DOI_HOI}")
        c.number_format = PP
        r += 1
    RR1 = r - 1
    vien_vung(ws5, 4, RR1, 1, 4)

    sc = ScatterChart()
    sc.title = "Rủi ro – Lợi nhuận (trung bình 4 pha)"
    sc.x_axis.title = "Sụt giảm tối đa (%)"
    sc.y_axis.title = "CAGR (%/năm)"
    sc.style = 13
    sc.height, sc.width = 11, 20
    xref = Reference(ws5, min_col=2, min_row=RR0, max_row=RR1)
    for i in range(RR0, RR1 + 1):
        s = Series(Reference(ws5, min_col=3, min_row=i, max_row=i), xref, title_from_data=False)
        s.marker.symbol = "circle"
        s.marker.size = 9
        s.graphicalProperties.line.noFill = True
        s.tx = None
        sc.series.append(s)
    ws5.add_chart(sc, "F4")
    ghi_chu(ws5, RR1 + 2,
            "Đọc biểu đồ theo thứ tự các dòng trong bảng bên trái. Điểm quan trọng: phương án "
            "'xếp hạng toàn rổ' nằm cao hơn VÀ sang trái hơn hệ thống hiện hành, tức tốt hơn ở "
            "cả hai chiều — nhưng nó trái với bản chốt FF5, nên đây là thông tin để cân nhắc "
            "sửa bản chốt, không phải để lặng lẽ đổi code.", span=5)

    # ============================================================ 6. DU LIEU THO
    ws6 = wb.create_sheet("6. Dữ liệu thô")
    tieu_de(ws6, "DỮ LIỆU THÔ — toàn bộ số dùng trong file này")
    ws6.column_dimensions["A"].width = 34
    for c in "BCDEFG":
        ws6.column_dimensions[c].width = 14

    r = 4
    ws6.cell(row=r, column=1, value="A. Kết quả theo pha, ba phạm vi xếp hạng").font = F_DAM
    r += 1
    head(ws6, r, ["Pha / phạm vi", "CAGR (%)", "Sụt giảm (%)", "Alpha tháng (%)",
                  "Thống kê t", "VN-Index (%)", "Số mã qua lọc (trung vị)"])
    r += 1
    for i, p in enumerate(phas):
        for sc_ in ("A", "B1", "B2", "tat_qt3"):
            ws6.cell(row=r, column=1, value=f"Pha {i} ({p['ngay_cuoi']}) — {sc_}")
            ws6.cell(row=r, column=2, value=p[sc_]["cagr"] * 100).number_format = "0.00"
            ws6.cell(row=r, column=3, value=p[sc_]["mdd"] * 100).number_format = "0.0"
            ws6.cell(row=r, column=4, value=p[sc_]["alpha"] * 100).number_format = "0.000"
            ws6.cell(row=r, column=5, value=p[sc_]["t"]).number_format = "0.00"
            ws6.cell(row=r, column=6, value=p["VNINDEX"] * 100).number_format = "0.00"
            ws6.cell(row=r, column=7, value=p["pool_median"])
            r += 1
    vien_vung(ws6, 5, r - 1, 1, 7)

    r += 2
    ws6.cell(row=r, column=1, value="B. Độ nhạy số ô (CAGR %, phạm vi rổ đã lọc)").font = F_DAM
    r += 1
    head(ws6, r, ["Số ô", "Pha 0", "Pha 1", "Pha 2", "Pha 3", "Trung bình"])
    r += 1
    SO0 = r
    for n in ("5", "6", "8", "10", "12", "15"):
        ws6.cell(row=r, column=1, value=int(n)).font = F_DAM
        for i in range(4):
            ws6.cell(row=r, column=2 + i, value=so_o[f"pha{i}"][n] * 100).number_format = "0.00"
        ws6.cell(row=r, column=6, value=f"=AVERAGE(B{r}:E{r})").number_format = "0.00"
        r += 1
    SO1 = r - 1
    vien_vung(ws6, SO0 - 1, SO1, 1, 6)

    ch = LineChart()
    ch.title = "Độ nhạy số ô — mỗi pha một đường"
    ch.y_axis.title = "CAGR (%/năm)"
    ch.x_axis.title = "Số ô danh mục"
    ch.height, ch.width = 10, 20
    ch.add_data(Reference(ws6, min_col=2, max_col=6, min_row=SO0 - 1, max_row=SO1),
                titles_from_data=True)
    ch.set_categories(Reference(ws6, min_col=1, min_row=SO0, max_row=SO1))
    ws6.add_chart(ch, "I4")
    ghi_chu(ws6, SO1 + 2,
            "Bốn đường không cùng hình dạng — đó là toàn bộ vấn đề. Nếu số ô thật sự quan trọng "
            "thì bốn đường phải cùng dốc về một phía. Chúng không.", span=6)

    r = SO1 + 4
    ws6.cell(row=r, column=1, value="C. Nguồn").font = F_DAM
    r += 1
    for ten, gt in [
        ("Kết quả kiểm định", "data/backtest_pha_luoi_20260826.json (lt_backtest_scope.js)"),
        ("Mô hình FF5", "Bảng CS.1, Triet_ly_dau_tu_FF5.docx, ngày 24/08/2026"),
        ("Rf", "Lợi suất TPCP 10 năm ngày 21/08/2026"),
        ("Phần bù thị trường", "Damodaran, thị trường Việt Nam"),
        ("Bốn λ phi thị trường", "Trung bình ba nguồn thực nghiệm VN, đã thu hẹp một nửa về 0"),
        ("Giai đoạn kiểm định", "04/2022 – 08/2026, 52 tháng, 112 mã HOSE, phí 0,4%/vòng quay"),
    ]:
        ws6.cell(row=r, column=1, value=ten).font = F_DAM
        ws6.cell(row=r, column=2, value=gt)
        ws6.merge_cells(start_row=r, start_column=2, end_row=r, end_column=7)
        r += 1

    for w in wb.worksheets:
        w.sheet_view.showGridLines = False
    wb.save(OUT)
    return OUT


if __name__ == "__main__":
    p = build()
    print(f"-> {p}")
