# -*- coding: utf-8 -*-
"""
build_report_ff5.py — Dung lai Bao_cao_chien_luoc_dau_tu.docx theo KHUNG HIEN HANH.

Ban cu (build_report_khung_cu.py, da chuyen vao archive_khung_cu/) viet ve khung
cuoc thi "P(ve nhat)" bi bo ngay 17/08/2026. File nay dung ban moi:

  * Phan 1-3 lay NGUYEN VAN tu Triet_ly_dau_tu_FF5.docx — do la ban DA CHOT ve
    triet ly / chinh sach / chien luoc. Khong viet lai, chi tai trinh bay.
  * Phan 4 tro di viet moi, lap dung nhung cho ma FF5 tro toi nhung chua co:
      - "Cac chi tieu dinh luong cua muc tieu va nguong rui ro ... o phan sau"  -> Phan 4
      - "buoc kiem tra tap trung theo yeu to rui ro da neu o muc 6.1"           -> muc 6.1
      - "quy trinh dung da duoc viet thanh ma va neu o phu luc phuong phap"     -> Phu luc A
  * Moi con so hieu nang lay tu data/backtest_pha_luoi_20260826.json (4 pha luoi).
    KHONG dung 13,89% / -21,3% / t = 0,87 nua — xem muc 8 CHIEN_LUOC_DAI_HAN.md.

Chay: PYTHONIOENCODING=utf-8 python build_report_ff5.py
"""

import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

import docx
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor, Cm
from docx.table import Table
from docx.text.paragraph import Paragraph

from lt_config import HOLDINGS, TIEN_MAT, PORTFOLIOS, LOC, EXIT

NGUON_FF5 = "Triet_ly_dau_tu_FF5.docx"
OUT = "Bao_cao_chien_luoc_dau_tu.docx"
BODY_FONT = "Times New Roman"

# Cac doan trong FF5 von la TIEU DE PHU nhung duoc luu o style Normal.
TIEU_DE_PHU = {
    "Vì sao Quỹ đi từ dưới lên",
    "Quy trình bốn bước",
    "Bước 1 — Bộ lọc cứng: mã này có được phép mua không",
    "Bước 2 — Xếp hạng: trong số các mã đạt chuẩn, chọn mã nào trước",
    "Bước 3 — Thẩm định từ dưới lên: lớp có quyền phủ quyết",
    "Bước 4 — Định giá và điểm mua",
    "Quy tắc bán",
    "Bốn quy tắc thoát",
    "Quy tắc thứ năm: bán bớt khi giá quá nóng",
    "Vì sao Quỹ không đặt giá mục tiêu để chốt lời",
    "Chặn cứng và biên không giao dịch",
    "Kỷ luật khi giá đi ngược kỳ vọng",
    "Xử lý hai vị thế không đạt tiêu chí từ đầu kỳ",
    "Chiến lược cho giai đoạn hiện tại",
}
# Tieu de cua cac hop luu y trong FF5 (docx xuat ra thanh mot chuoi lien, phai
# tach lai de in dam dung phan tieu de).
HOP_TIEU_DE = [
    "Điểm cần nhấn",
    "Tự kiểm tra bắt buộc",
    "Giới hạn tự đặt cho quy tắc này",
    "Điều đã đưa vào quy trình sau tình huống này",
]

# Sua tham chieu noi bo bi sai trong ban FF5 (tro toi "Phan 5" trong khi ba tru
# cot nam o Phan 1). Sua o muc typo, khong dong toi noi dung.
SUA_THAM_CHIEU = [("đã nêu ở Phần 5", "đã nêu ở Phần 1")]


# ------------------------------------------------------------------ Tien ich
def setup_styles(doc):
    n = doc.styles["Normal"]
    n.font.name = BODY_FONT
    n.font.size = Pt(12)
    n._element.rPr.rFonts.set(qn("w:eastAsia"), BODY_FONT)
    n.paragraph_format.space_after = Pt(6)
    n.paragraph_format.line_spacing = 1.4

    for i, sz in ((1, 16), (2, 13), (3, 12)):
        s = doc.styles[f"Heading {i}"]
        s.font.name = BODY_FONT
        s.font.size = Pt(sz)
        s.font.bold = True
        s.font.color.rgb = RGBColor(0x1A, 0x1A, 0x1A)
        s.paragraph_format.space_before = Pt(14 if i == 1 else 10)
        s.paragraph_format.space_after = Pt(6)

    cap = doc.styles.add_style("Chu thich bang", 1)
    cap.base_style = doc.styles["Normal"]
    cap.font.size = Pt(10)
    cap.font.italic = True
    cap.paragraph_format.space_before = Pt(2)
    cap.paragraph_format.space_after = Pt(10)

    box = doc.styles.add_style("Hop luu y", 1)
    box.base_style = doc.styles["Normal"]
    box.font.size = Pt(11)
    box.paragraph_format.left_indent = Cm(0.6)


def vn(x, nd=2, dau=False):
    """So kieu Viet: dau phay thap phan. VD vn(9.0512, 2) -> '9,05'."""
    t = f"{x:+.{nd}f}" if dau else f"{x:.{nd}f}"
    return t.replace(".", ",").replace("-", "−")   # dau tru thuc, khong phai gach noi


def vnd(x):
    """Tien dong kieu Viet: dau cham phan cach hang nghin."""
    return f"{x:,.0f}".replace(",", ".")


def para(doc, text, bold=False, italic=False, style=None):
    p = doc.add_paragraph(style=style) if style else doc.add_paragraph()
    r = p.add_run(text)
    r.bold = bold
    r.italic = italic
    return p


def bullets(doc, items):
    for it in items:
        doc.add_paragraph(it, style="List Bullet")


def table(doc, header, rows, caption=None, widths=None, bold_first=True):
    t = doc.add_table(rows=1, cols=len(header))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(header):
        c = t.rows[0].cells[i]
        c.text = ""
        r = c.paragraphs[0].add_run(str(h))
        r.bold = True
        r.font.size = Pt(10)
        shd = OxmlElement("w:shd")
        shd.set(qn("w:fill"), "E8E8E8")
        c._tc.get_or_add_tcPr().append(shd)
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            run = cells[i].paragraphs[0].add_run(str(v))
            run.font.size = Pt(10)
            if i == 0 and bold_first:
                run.bold = True
    if widths:
        for r_ in t.rows:
            for i, w in enumerate(widths):
                r_.cells[i].width = Cm(w)
    if caption:
        doc.add_paragraph(caption, style="Chu thich bang")
    return t


def hop(doc, tieu_de, noi_dung):
    """Hop luu y co vien, dung cho cac canh bao phuong phap."""
    t = doc.add_table(rows=1, cols=1)
    t.style = "Table Grid"
    c = t.rows[0].cells[0]
    c.text = ""
    p = c.paragraphs[0]
    r = p.add_run(tieu_de + "  ")
    r.bold = True
    r.font.size = Pt(11)
    r2 = p.add_run(noi_dung)
    r2.font.size = Pt(11)
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), "F4F4F4")
    c._tc.get_or_add_tcPr().append(shd)
    doc.add_paragraph()
    return t


# ------------------------------------------- Nhap nguyen van Phan 1-3 tu FF5
def nhap_ff5(doc):
    """Doc Triet_ly_dau_tu_FF5.docx va tai trinh bay Phan 1-3 vao bao cao moi."""
    if not os.path.exists(NGUON_FF5):
        sys.exit(f"Khong tim thay {NGUON_FF5} — Phan 1-3 lay nguyen van tu file nay.")
    src = docx.Document(NGUON_FF5)
    n_p = n_t = 0
    for child in src.element.body.iterchildren():
        if child.tag.endswith("}p"):
            p = Paragraph(child, src)
            t = p.text.strip()
            if not t:
                continue
            for a, b in SUA_THAM_CHIEU:
                t = t.replace(a, b)
            n_p += 1
            if p.style.name.startswith("Heading"):
                doc.add_heading(t, 1)
            elif t in TIEU_DE_PHU:
                doc.add_heading(t, 2)
            elif t.startswith("Bảng "):
                doc.add_paragraph(t, style="Chu thich bang")
            elif t.startswith("Nguồn:"):
                doc.add_paragraph(t, style="Chu thich bang")
            elif p.style.name == "List Paragraph":
                doc.add_paragraph(t, style="List Bullet")
            else:
                para(doc, t)
        elif child.tag.endswith("}tbl"):
            tb = Table(child, src)
            rows = [[c.text.strip().replace("\n", " ") for c in r.cells] for r in tb.rows]
            if not rows:
                continue
            n_t += 1
            if len(rows[0]) == 1:                     # hop luu y mot o
                txt = rows[0][0]
                td = next((h for h in HOP_TIEU_DE if txt.startswith(h)), None)
                if td:
                    hop(doc, td, txt[len(td):].strip())
                else:
                    hop(doc, "Lưu ý", txt)
            else:
                table(doc, rows[0], rows[1:])
    return n_p, n_t


# --------------------------------------------------------------- So lieu
def so_lieu():
    bt = json.load(io.open("data/backtest_pha_luoi_20260826.json", encoding="utf-8"))
    gia = {}
    scan = json.load(io.open("data/scan_20260825.json", encoding="utf-8"))
    for k, v in scan.items():
        if not k.startswith("_"):
            gia[k] = v[0]
    cands = json.load(io.open("data/candidates_20260825.json", encoding="utf-8"))
    return bt, gia, cands


def build():
    bt, gia, cands = so_lieu()
    ts = bt["thamso_4pha"]
    phas = [bt[f"pha{i}"] for i in range(4)]
    # Tinh lai trung binh tu 4 pha thay vi doc so da lam tron trong file.
    tb = {
        "B1": {"cagr": sum(p["B1"]["cagr"] for p in phas) / 4,
               "mdd": sum(p["B1"]["mdd"] for p in phas) / 4},
        "VNINDEX": {"cagr": sum(p["VNINDEX"] for p in phas) / 4},
    }
    tb["B1"]["vuot"] = (tb["B1"]["cagr"] - tb["VNINDEX"]["cagr"]) * 100
    b1s = sorted(p["B1"]["cagr"] for p in phas)
    ivs = sorted(p["VNINDEX"] for p in phas)

    pk = "DM2"
    cfg = PORTFOLIOS[pk]
    hold = HOLDINGS[pk]
    tien = TIEN_MAT[pk]
    gt = {ma: kl * gia.get(ma, gv) for ma, kl, gv in hold}
    tong_cp = sum(gt.values())
    nav = tong_cp + tien
    von = cfg["von_ban_dau"]

    doc = Document()
    setup_styles(doc)
    for s in doc.sections:
        s.left_margin = s.right_margin = Cm(2.5)

    # ----------------------------------------------------------- Trang bia
    for _ in range(6):
        doc.add_paragraph()
    t = doc.add_paragraph()
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = t.add_run("BÁO CÁO CHIẾN LƯỢC ĐẦU TƯ")
    r.bold = True
    r.font.size = Pt(22)
    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rs = sub.add_run("Triết lý, chính sách, chiến lược\nvà bằng chứng kiểm định trên thị trường Việt Nam")
    rs.italic = True
    rs.font.size = Pt(13)
    doc.add_paragraph()
    for line in ("Quỹ Medici", "Kỳ báo cáo: tính đến 26/08/2026",
                 "Người lập:  [ ]", "Ngày nộp:  [ ]"):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run(line).font.size = Pt(12)
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    # ----------------------------------------------------------- Muc luc
    doc.add_heading("MỤC LỤC", 1)
    for line in ("1. Triết lý đầu tư", "2. Chính sách đầu tư", "3. Chiến lược đầu tư",
                 "4. Chỉ tiêu định lượng và ngưỡng rủi ro",
                 "5. Dữ liệu, phương pháp và kết quả kiểm định",
                 "6. Thiết lập danh mục", "7. Hạn chế và rủi ro", "8. Kết luận",
                 "Phụ lục A — Phương pháp dựng chuỗi nhân tố Fama–French Việt Nam",
                 "Phụ lục B — Mã nguồn và khả năng tái lập"):
        doc.add_paragraph(line)
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    # ------------------------------------------------- Phan 1-3: nguyen van
    n_p, n_t = nhap_ff5(doc)
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    # ------------------------------------- Phan 4: chi tieu va nguong rui ro
    doc.add_heading("4. Chỉ tiêu định lượng và ngưỡng rủi ro", 1)
    para(doc, "Phần 2 nêu mục tiêu của Quỹ bằng lời và hoãn phần định lượng lại. "
              "Phần này trả nốt: mỗi con số dưới đây là một ràng buộc cứng, được "
              "cài trực tiếp vào mã vận hành và kiểm tra tự động ở mỗi kỳ rà soát.")

    table(doc,
          ["Chỉ tiêu", "Ngưỡng", "Cơ sở"],
          [["Tỷ suất sinh lời đòi hỏi", "9,67%/năm",
            "Fama–French 5 nhân tố bản Việt Nam, Bảng CS.1"],
           ["Mốc so sánh", "VN-Index, tỷ suất bình quân gộp nhiều năm",
            "Phần 2 — không cam kết vượt theo từng tháng hay từng quý"],
           ["Thanh khoản tối thiểu", f"{LOC['thanh_khoan_min']/1e9:.0f} tỷ đồng/phiên (bình quân 20 phiên)",
            "Vào và ra được vị thế mà không tự làm lệch giá"],
           ["Biên độ dao động tối đa", f"ATR ngày ≤ {LOC['atr_max']*100:.0f}%",
            "Chặn an toàn, loại nhóm đầu cơ cực đoan"],
           ["Trần một mã", f"{cfg['tran_ma']:.0%} NAV (tài khoản dự thi); 15% (tài khoản còn lại)",
            "Không để một vị thế quyết định kết quả cả danh mục"],
           ["Trần một ngành", f"{cfg['tran_nganh']:.0%} NAV (dự thi); 30% (còn lại)",
            "Bổ sung bằng kiểm tra tập trung theo yếu tố rủi ro, mục 6.1"],
           ["Chặn cứng theo giá vốn", f"−{EXIT['stop_tham_hoa']:.0%}",
            "Ngoại lệ duy nhất giữa hai kỳ rà soát"],
           ["Biên không giao dịch", f"{EXIT['bien_khong_giao_dich']:.0%} NAV",
            "Lệch nhỏ hơn ngưỡng này thì không cân lại, vì phí lớn hơn lợi ích"],
           ["Số ô danh mục", "10 (tài khoản chính) · 8 (tài khoản dự thi)",
            "Con số đã chốt — xem cảnh báo ở mục 5.4"]],
          caption="Bảng 4.1 — Các ràng buộc định lượng đang áp dụng.",
          widths=[5.5, 4.8, 6.2])

    para(doc, "Về mức sụt giảm chấp nhận được, Quỹ không đặt một con số trần rồi "
              "hành động khi chạm nó — làm vậy sẽ biến quản trị rủi ro thành dự "
              "báo thị trường. Thay vào đó, mức sụt giảm là KẾT QUẢ ĐO ĐƯỢC của "
              "bộ quy tắc: kiểm định trên 52 tháng cho mức sụt giảm tối đa "
              f"{vn(abs(tb['B1']['mdd'])*100, 1)}%. Con số đó là điều nhà đầu tư phải "
              "chấp nhận trước khi góp vốn, không phải điều Quỹ hứa sẽ giữ.")

    # --------------------------------- Phan 5: du lieu, phuong phap, ket qua
    doc.add_heading("5. Dữ liệu, phương pháp và kết quả kiểm định", 1)

    doc.add_heading("5.1. Nguồn dữ liệu", 2)
    table(doc,
          ["Bộ dữ liệu", "Phạm vi", "Dùng để"],
          [["Giá tuần HOSE", "112 mã, 300 phiên tuần, 11/2020 – 08/2026",
            "Kiểm định hệ thống trên 52 tháng"],
           ["Giá ngày HOSE", "113 mã, 300 phiên, tính đến 25/08/2026",
            "Bộ lọc và bảng xếp hạng của kỳ rà soát hiện tại"],
           ["Báo cáo tài chính", "vnstock, 2010 – 2026",
            "Dựng chuỗi nhân tố Fama–French, Phụ lục A"],
           ["Lợi suất TPCP 10 năm", "21/08/2026", "Lãi suất phi rủi ro trong Bảng CS.1"]],
          caption="Bảng 5.1 — Các bộ dữ liệu sử dụng.",
          widths=[5.0, 6.0, 5.5])
    para(doc, "Dữ liệu giá lấy qua giao diện TradingView, độ trễ 15 phút trong "
              "phiên; mọi con số trong báo cáo này đều là giá đóng cửa nên độ trễ "
              "không ảnh hưởng. Quy trình quét có một bẫy đã gặp và đã chặn: khi "
              "đổi mã trên biểu đồ, tên mã đổi TRƯỚC khi dữ liệu mới về, nên vòng "
              "lặp ngây thơ gán dữ liệu mã trước cho mã sau mà không báo lỗi. "
              "Cách chặn: tính chữ ký của chuỗi giá và chỉ nhận khi chữ ký khác "
              "mã liền trước và lặp lại giống nhau ở hai lần đọc cách nhau 250 "
              "mili-giây. Mỗi lần quét đều kiểm tra trùng lặp trước khi dùng.")

    doc.add_heading("5.2. Thiết kế kiểm định và một sai lầm đã phát hiện", 2)
    para(doc, "Hệ thống được kiểm định trên 52 tháng (04/2022 – 08/2026), 112 mã "
              "HOSE, đã trừ phí 0,4% cho mỗi vòng quay. Mỗi đầu tháng, hệ thống "
              "chạy đúng bộ lọc và bảng xếp hạng ở Phần 3, áp bốn quy tắc thoát, "
              "rồi phân bổ nghịch với biến động.")
    para(doc, "Bản kiểm định đầu tiên, chạy ngày 17/08/2026, báo cáo 13,89%/năm và "
              "mức sụt giảm −21,3%. Ngày 26/08 chúng tôi chạy lại và phát hiện con "
              "số đó không lặp lại. Nguyên nhân không phải lỗi lập trình: chạy lại "
              "đúng phương pháp cũ trên đúng lưới cũ tái tạo được 14,07% và −21,4%. "
              "Nguyên nhân là bản đầu tiên chỉ chạy MỘT lưới lấy mẫu tháng.")
    hop(doc, "Bẫy phương pháp — pha của lưới lấy mẫu.",
        "Dữ liệu tuần được lấy mẫu bốn tuần một lần để tạo chuỗi tháng. Có bốn "
        "cách neo lưới đó, tuỳ chọn tuần nào làm mốc, và bốn cách này khác nhau "
        "chỉ bằng một tuần. Chạy cả bốn: CAGR của cùng một phương pháp dao động "
        "từ 9,38% đến 14,54%. Con số 13,89% công bố ban đầu là lần rút thăm cao "
        "thứ hai trong bốn. Nó không sai, nhưng nó chưa bao giờ là một ước lượng "
        "— nó là một quan sát. Từ báo cáo này trở đi, mọi con số hiệu năng đều "
        "là trung bình của cả bốn pha, và biên độ giữa các pha được công bố kèm.")

    doc.add_heading("5.3. Kết quả", 2)
    table(doc,
          ["Chỉ tiêu", "Hệ thống", "VN-Index mua & giữ"],
          [["Tỷ suất bình quân gộp (TB 4 pha)", f"{vn(tb['B1']['cagr']*100)}%/năm",
            f"{vn(tb['VNINDEX']['cagr']*100)}%/năm"],
           ["Biên độ giữa bốn pha", f"{vn(b1s[0]*100)}% – {vn(b1s[-1]*100)}%",
            f"{vn(ivs[0]*100)}% – {vn(ivs[-1]*100)}%"],
           ["Mức sụt giảm tối đa", f"{vn(tb['B1']['mdd']*100, 1)}%", "—"],
           ["Vượt chỉ số", f"{vn(tb['B1']['vuot'], 2, dau=True)} điểm phần trăm/năm", "—"],
           ["Alpha tháng, thống kê t", "t = 0,04 – 0,24 tuỳ pha", "—"],
           ["Tỷ suất sinh lời đòi hỏi (Bảng CS.1)", "9,67%/năm", "—"]],
          caption="Bảng 5.2 — Kết quả kiểm định, 52 tháng, trung bình bốn pha lưới, đã trừ phí.",
          widths=[6.5, 5.0, 5.0])

    para(doc, "Ba điều phải đọc đúng từ bảng này.", bold=True)
    bullets(doc, [
        "Hệ thống vượt VN-Index +0,72 điểm phần trăm mỗi năm, với thống kê t từ "
        "0,04 đến 0,24. Không pha nào đạt ý nghĩa thống kê ở bất kỳ mức thông "
        "thường nào. Với 52 tháng quan sát, khoảng cách này nằm gọn trong dao "
        "động ngẫu nhiên, và Quỹ không được phép trình bày nó như một năng lực "
        "đã được chứng minh.",
        "Tỷ suất đo được (9,05%) thấp hơn tỷ suất đòi hỏi theo Fama–French "
        "(9,67%). Nói theo đúng ngôn ngữ của mô hình: trên mẫu này, hệ thống "
        "chưa bù đủ phần rủi ro mà chính nó đang mang.",
        "Mức sụt giảm −29,5% sâu hơn mức của chỉ số. Đây là con số ổn định nhất "
        "trong cả bộ đo, và là điều Phần 2 muốn nhà đầu tư chấp nhận trước.",
    ])

    doc.add_heading("5.4. Ba tham số thiết kế: cái nào đo được, cái nào chỉ là đã chốt", 2)
    para(doc, "Khi bản kiểm định đầu tiên hỏng, mọi tham số từng được biện minh "
              "bằng nó đều phải đo lại. Kết quả chia làm hai loại rõ rệt.")
    table(doc,
          ["Tham số", "Kết luận cũ (một pha)", "Đo lại (trung bình bốn pha)", "Trạng thái"],
          [["Số ô danh mục", "8–10 ô tốt nhất; 10 ô cho 13,9%",
            "5 ô 10,66% > 10 ô 9,05%; 5 ô thắng ở 4/4 pha", "ĐẢO NGƯỢC"],
           ["Chu kỳ rà soát", "Hằng quý làm tụt 13,89% → 7,06%",
            "Hằng quý 11,67% > hằng tháng 9,05%; thắng 3/4 pha", "ĐẢO NGƯỢC"],
           ["Phân bổ 1/biến động", "Lợi nhuận ngang bằng, sụt giảm nhỏ hơn",
            f"{vn(tb['B1']['cagr']*100)}% / "
            f"{vn(tb['B1']['mdd']*100, 1)}% so với "
            f"{vn(ts['phan_bo']['can_bang_deu']['cagr']*100)}% / "
            f"{vn(ts['phan_bo']['can_bang_deu']['mdd']*100, 1)}%; nhỏ hơn ở 4/4 pha",
            "GIỮ NGUYÊN"]],
          caption="Bảng 5.3 — Ba tham số thiết kế, đo lại trên bốn pha lưới.",
          widths=[3.6, 4.4, 5.4, 3.1])
    para(doc, "Quỹ KHÔNG đổi số ô và KHÔNG đổi chu kỳ rà soát theo bảng trên. Lý "
              "do là hai phép đo cho hai kết luận ngược nhau, nên điều đọc được "
              "chắc chắn nhất không phải \"5 ô tốt hơn 10 ô\" mà là \"hai tham số "
              "này không đo được ở cỡ mẫu 52 tháng\". Đổi tham số theo phép đo "
              "mới nhất chỉ là thay một lần rút thăm bằng một lần rút thăm khác. "
              "Chúng được giữ vì là con số đã chốt trong Phần 3, và báo cáo này "
              "nói đúng như vậy thay vì viện dẫn một bằng chứng không tồn tại.")
    para(doc, "Phân bổ nghịch với biến động là lựa chọn thiết kế duy nhất trong "
              "toàn hệ thống mà lý do ban đầu vẫn đứng vững sau khi đo lại: lợi "
              "nhuận ngang bằng cân bằng đều, nhưng sụt giảm nhỏ hơn ở cả bốn "
              "pha. Đúng như đã ghi từ đầu — chọn nó vì rủi ro, không vì lợi nhuận.")

    doc.add_heading("5.5. Bốn lỗi hiện thực đã phát hiện và sửa", 2)
    para(doc, "Đối chiếu từng dòng mã vận hành với Phần 3 phát hiện bốn chỗ hệ "
              "thống chạy khác điều đã chốt. Ghi lại đầy đủ vì một quy trình chỉ "
              "có giá trị khi bản chạy và bản viết là một.")
    table(doc,
          ["#", "Chỗ sai", "Bản đã chạy", "Bản đúng theo Phần 3"],
          [["1", "Quy tắc thoát số 3", "So giá trị điểm với ngưỡng 0,60",
            "So THỨ HẠNG vị trí với ngưỡng 40% trong rổ đã lọc"],
           ["2", "Bộ lọc cứng", "Thêm chất lượng xu hướng và sức mạnh 6 tháng làm điều kiện lọc",
            "Đúng năm điều kiện của Bảng CL.1; hai tiêu chí kia là thành phần xếp hạng"],
           ["3", "Bước 3 và Bước 4", "Một thang điểm 10 suy \"chất lượng\" và \"định giá\" từ dữ liệu giá",
            "Người thẩm định, có quyền phủ quyết; thiếu kết luận thì không được mua"],
           ["4", "Lệnh bán", "Bán phần chênh so với danh mục mục tiêu, tức tái cơ cấu toàn bộ mỗi kỳ",
            "Chỉ bán khi hỏng một trong bốn quy tắc thoát"]],
          caption="Bảng 5.4 — Bốn sai lệch giữa mã vận hành và quy trình đã chốt, đã sửa ngày 25–26/08/2026.",
          widths=[0.8, 3.4, 6.0, 6.3])
    para(doc, "Lỗi thứ ba đáng nói riêng. Thang điểm cũ cộng điểm cho \"chất lượng "
              "doanh nghiệp\" bằng thanh khoản, quan hệ giữa hai đường trung bình "
              "và độ mượt của xu hướng, rồi cộng điểm cho \"định giá\" bằng sức "
              "mạnh giá 6 tháng và 3 tháng. Toàn bộ là dữ liệu giá đeo nhãn cơ "
              "bản. Đó đúng là loại nhầm lẫn mà Phần 2 đã cảnh báo khi giải thích "
              "vì sao bỏ CAPM: hệ thống tự khen mình vì những thứ vốn chỉ là phơi "
              "nhiễm rủi ro. Thang điểm đã bị xoá, thay bằng hai cửa do người "
              "quyết, và mặc định khi thiếu kết luận là KHÔNG được mua — vì nếu "
              "mặc định là được mua thì lớp phủ quyết không tồn tại.")

    # ------------------------------------------- Phan 6: thiet lap danh muc
    doc.add_heading("6. Thiết lập danh mục", 1)

    doc.add_heading("6.1. Kiểm tra tập trung theo yếu tố rủi ro", 2)
    para(doc, "Phần 3 đã nêu điểm yếu của cách đi từ dưới lên: danh mục dễ vô "
              "tình gom nhiều mã cùng phụ thuộc một yếu tố vĩ mô trong khi nhãn "
              "ngành của chúng khác nhau, khiến trần ngành trông như đã tuân thủ "
              "nhưng rủi ro thật thì không được kiểm soát. Bước kiểm tra này nhóm "
              "lại các vị thế theo yếu tố rủi ro chung thay vì theo tên ngành.")

    nhom = {
        "Tín dụng nội địa và bất động sản": ["MSB", "LPB", "STB", "VHM"],
        "Giá dầu và biên lọc hoá dầu": ["BSR"],
        "Thương mại và vận tải biển toàn cầu": ["GMD"],
    }
    rows = []
    for ten, mas in nhom.items():
        v = sum(gt[m] for m in mas if m in gt)
        rows.append([ten, ", ".join(mas), vnd(v), f"{vn(v/nav*100, 1)}%"])
    rows.append(["Tiền mặt", "—", vnd(tien), f"{vn(tien/nav*100, 1)}%"])
    table(doc, ["Yếu tố rủi ro chung", "Vị thế", "Giá trị (đồng)", "% NAV"], rows,
          caption="Bảng 6.1 — Danh mục nhóm lại theo yếu tố rủi ro, không theo nhãn ngành. "
                  "Số liệu đóng cửa 25/08/2026.",
          widths=[6.0, 4.0, 3.5, 2.5])

    v_bank = sum(gt[m] for m in nhom["Tín dụng nội địa và bất động sản"] if m in gt)
    para(doc, f"Kết quả đúng như điều Phần 3 lo ngại. Theo nhãn ngành, ngân hàng "
              f"chiếm {vn(sum(gt[m] for m in ['MSB', 'LPB', 'STB']) / nav * 100, 1)}% "
              f"và bất động sản {vn(gt['VHM'] / nav * 100, 1)}% — cả hai đều dưới trần "
              f"{cfg['tran_nganh']:.0%}. Nhưng bốn vị thế đó cùng phụ thuộc một "
              f"biến số: mặt bằng lãi suất và chất lượng tín dụng trong nước. "
              f"Gộp lại chúng chiếm {vn(v_bank/nav*100, 1)}% NAV và "
              f"{vn(v_bank/tong_cp*100, 1)}% phần vốn đã giải ngân. Danh mục có sáu mã "
              f"nhưng chỉ khoảng ba cược độc lập.", bold=False)
    hop(doc, "Điều này không phải một lựa chọn.",
        "Ở kỳ rà soát 25/08/2026, chỉ 12 trong 112 mã qua được bộ lọc cứng, và "
        "chúng tự dồn vào một số ít ngành. Quỹ không thể đa dạng hoá thêm mà "
        "không hạ tiêu chuẩn, và hạ tiêu chuẩn để cho đủ ô là điều Phần 2 đã "
        "loại trừ. Cách xử lý đúng là ghi nhận mức tập trung thật và nói ra, "
        "không phải che nó sau một trần ngành đã tuân thủ về mặt hình thức.")

    doc.add_heading("6.2. Trạng thái danh mục", 2)
    rows = []
    for ma, kl, gv in sorted(hold):
        g = gia.get(ma, gv)
        rows.append([ma, vnd(kl), vnd(gv), vnd(g), vnd(gt[ma]),
                     f"{vn((g/gv-1)*100, 2, dau=True)}%"])
    table(doc, ["Mã", "Khối lượng", "Giá vốn", "Giá 25/08", "Giá trị", "Lãi/lỗ"], rows,
          caption="Bảng 6.2 — Vị thế đang nắm giữ, giá đóng cửa 25/08/2026.",
          widths=[2.0, 2.6, 2.6, 2.6, 3.2, 2.5])
    table(doc, ["Khoản mục", "Giá trị (đồng)", "% NAV"],
          [["Cổ phiếu", vnd(tong_cp), f"{vn(tong_cp/nav*100, 1)}%"],
           ["Tiền mặt", vnd(tien), f"{vn(tien/nav*100, 1)}%"],
           ["Tổng tài sản ròng", vnd(nav), "100,0%"],
           ["Vốn góp ban đầu", vnd(von), "—"],
           ["Thay đổi", ("−" if nav < von else "+") + vnd(abs(nav-von)),
            f"{vn((nav/von-1)*100, 2, dau=True)}%"]],
          caption="Bảng 6.3 — Tổng hợp danh mục.",
          widths=[6.0, 5.0, 4.0])
    para(doc, f"Tỷ trọng tiền mặt {vn(tien/nav*100, 1)}% không phải một dự báo. Nó là "
              f"số ô không tìm được cổ phiếu đạt chuẩn, cộng thêm một khoản phát "
              f"sinh từ sai sót vận hành nêu ngay dưới đây.")

    hop(doc, "Ghi nhận một lệch so với kế hoạch đã chốt.",
        "Kế hoạch ngày 19/08/2026 có một lệnh mua với nhánh bắt buộc: nếu chưa "
        "khớp trước ngày 21/08 thì mua ở giá thị trường. Lệnh đó không khớp và "
        "nhánh bắt buộc đã không được thực hiện. Hệ quả là tỷ trọng tiền mặt cao "
        "hơn thiết kế khoảng mười điểm phần trăm, và một ô danh mục để trống "
        "không phải vì thiếu mã đạt chuẩn. Ghi lại vì đây đúng là sai lầm loại "
        "thứ nhất trong cách phân loại ở Phần 3 — sai vì không tuân thủ quy "
        "trình, chứ không phải tuân thủ đúng mà kết quả xấu — và loại đó phải "
        "sửa ngay ở người vận hành.")

    para(doc, "Kỳ rà soát 01/09/2026 — kết quả áp bốn quy tắc thoát:", bold=True)
    by = {c["ma"]: c for c in cands}
    rows = []
    for ma, kl, gv in sorted(hold):
        c = by.get(ma)
        if not c:
            rows.append([ma, "—", "—", "không còn trong bảng xếp hạng — chấm tay"])
            continue
        vi = [n for n, ok in c["sell_checklist"] if ok]
        rows.append([ma, f"{c['thu']}/12", vn(c["thu_hang"], 2),
                     "BÁN — " + ", ".join(vi) if vi else "Giữ"])
    table(doc, ["Mã", "Thứ hạng", "Vị trí", "Kết luận"], rows,
          caption="Bảng 6.4 — Áp bốn quy tắc thoát trên dữ liệu 25/08/2026. "
                  "Quy tắc 4 (luận điểm doanh nghiệp) chưa rà soát tại thời điểm lập báo cáo.",
          widths=[2.0, 2.6, 2.4, 8.0])

    # ------------------------------------------------ Phan 7: han che
    doc.add_heading("7. Hạn chế và rủi ro", 1)
    bullets(doc, [
        "Nền thống kê mỏng. 52 tháng quan sát cho thống kê t từ 0,04 đến 0,24. "
        "Không có kết luận nào trong báo cáo này đạt ý nghĩa thống kê, và phần "
        "vượt chỉ số nêu ở Bảng 5.2 phải được đọc là \"không phân biệt "
        "được với không\", không phải \"nhỏ nhưng có thật\".",
        "Bốn pha lưới không phải bốn quan sát độc lập. Chúng dùng chung phần lớn "
        "dữ liệu; việc lấy trung bình bốn pha loại bỏ được sự may rủi của một "
        "lần rút thăm, nhưng không nhân bốn lượng thông tin.",
        "Chuỗi nhân tố Fama–French Việt Nam chưa được Quỹ tự dựng xong. Phần bù "
        "kỳ vọng hiện là ước lượng từ quá khứ, đã thu hẹp một nửa về 0; hệ số "
        "tải suy từ đặc điểm doanh nghiệp chứ chưa hồi quy trên chuỗi nhân tố "
        "thật. Quy trình dựng ở Phụ lục A.",
        "Thiên lệch người sống sót trong rổ kiểm định. Rổ 112 mã lấy theo danh "
        "sách niêm yết hiện tại, nên các doanh nghiệp đã huỷ niêm yết không có "
        "trong mẫu. Chiều của thiên lệch là làm kết quả đẹp hơn thực tế.",
        "Bộ lọc xu hướng có chữ ký đã biết: thắng khi thị trường xấu, thua khi "
        "thị trường tăng mạnh. Đây là đánh đổi đã chấp nhận trước, không phải "
        "một phát hiện mới, và nó có nghĩa Quỹ sẽ đi chậm hơn chỉ số trong "
        "những đợt phục hồi rộng.",
        "Quy tắc thứ năm chưa được kiểm định như phần còn lại của hệ thống, và "
        "hiện chưa chạy được vì thiếu hai trường dữ liệu: phân phối khoảng cách "
        "giá đến trung bình trung hạn trong hai năm, và chuỗi khối lượng. Đó là "
        "lý do nó bị giới hạn ở việc giảm nửa vị thế.",
        "Lớp thẩm định ở Bước 3 chưa loại được mã nào tính đến ngày lập báo cáo, "
        "vì kết luận thẩm định chưa được nhập cho kỳ đầu tiên. Theo đúng quy "
        "định tự kiểm tra bắt buộc, điều này được ghi nhận như một cảnh báo: "
        "một lớp phủ quyết chưa từng phủ quyết thì chưa chứng minh được là nó "
        "tồn tại.",
    ])

    # ------------------------------------------------ Phan 8: ket luan
    doc.add_heading("8. Kết luận", 1)
    para(doc, "Quỹ vận hành một hệ thống kết hợp lớp giá trị và lớp đà tăng "
              "trưởng, đi từ dưới lên qua bốn cửa kiểm tra nối tiếp, nắm giữ "
              "theo kỳ hạn dài và chỉ bán theo bốn quy tắc định sẵn. Toàn bộ "
              "quy trình đã được viết ra trước khi biết kết quả, và bản chạy đã "
              "được đối chiếu từng dòng với bản viết.")
    para(doc, "Về hiệu quả, kết luận trung thực là: trên 52 tháng, hệ thống cho "
              f"{vn(tb['B1']['cagr']*100)}%/năm so với {vn(tb['VNINDEX']['cagr']*100)}% "
              f"của VN-Index, với mức sụt giảm sâu hơn ({vn(tb['B1']['mdd']*100, 1)}%) "
              "và không có ý nghĩa thống kê ở bất kỳ pha lấy mẫu nào. Quỹ chưa "
              "chứng minh được năng lực tạo alpha. Điều Quỹ chứng minh được là "
              "một quy trình có kỷ luật, có thể tái lập, và tự phát hiện được "
              "lỗi của chính mình — bốn lỗi hiện thực ở Bảng 5.4 và bẫy pha lưới "
              "ở mục 5.2 đều do quy trình rà soát nội bộ tìm ra, không phải do "
              "thị trường chỉ ra bằng thua lỗ.")
    para(doc, "Giá trị của một hệ thống có quy tắc nằm ở chỗ nó vẫn chạy như cũ "
              "đúng vào lúc người vận hành muốn làm khác đi. Trong kỳ này, hai "
              "lần hệ thống đã làm đúng việc đó: khi bảng độ nhạy mới gợi ý đổi "
              "số ô, và khi kết quả đo lại gợi ý bỏ một quy tắc thoát. Cả hai "
              "lần, tham số được giữ nguyên vì bằng chứng không đủ mạnh để đổi.")

    # ------------------------------------------------ Phu luc A
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
    doc.add_heading("Phụ lục A — Phương pháp dựng chuỗi nhân tố Fama–French Việt Nam", 1)
    para(doc, "Quy trình đã được viết thành mã chạy được tại "
              "xay_dung_factor_ff5_vn.py, giai đoạn 2010–2026, theo bản 2×3 của "
              "Fama & French (2015).")
    bullets(doc, [
        "Lợi suất tháng tính trên giá đã điều chỉnh cổ tức và chia tách. Lãi "
        "suất phi rủi ro quy về tháng bằng luỹ thừa bậc 1/12, không chia 12 — "
        "chia 12 sai khoảng 2% giá trị mỗi năm ở mặt bằng lãi suất Việt Nam.",
        "SMB, HML, RMW, CMA dựng theo lưới 2×3: chia đôi theo vốn hoá, chia ba "
        "theo biến đặc trưng ở phân vị 30% và 70%, danh mục trong mỗi ô đánh "
        "trọng số theo vốn hoá.",
        "Lợi nhuận hoạt động định nghĩa là doanh thu thuần trừ giá vốn, chi phí "
        "lãi vay và chi phí bán hàng & quản lý.",
        "Cảnh báo đã ghi ngay trong mã nguồn: lấy danh sách mã theo \"đang niêm "
        "yết hôm nay\" rồi chạy ngược về 2010 sẽ loại mọi doanh nghiệp đã huỷ "
        "niêm yết, thổi phồng có hệ thống phần bù nhân tố, nặng nhất ở SMB vì "
        "cổ phiếu nhỏ chết nhiều nhất. Làm đúng đòi hỏi dựng danh sách niêm yết "
        "theo từng năm.",
    ])

    # ------------------------------------------------ Phu luc B
    doc.add_heading("Phụ lục B — Mã nguồn và khả năng tái lập", 1)
    table(doc,
          ["Tệp", "Chức năng"],
          [["lt_config.py", "Toàn bộ tham số: bộ lọc, trọng số xếp hạng, ngưỡng thoát, trần"],
           ["lt_scan_tradingview.js", "Quét giá từ TradingView, có cơ chế chặn bẫy dữ liệu cũ"],
           ["lt_screener.py", "Bước 1 và Bước 2: bộ lọc cứng và bảng xếp hạng"],
           ["data/tham_dinh.json", "Bước 3 và Bước 4: kết luận thẩm định do người nhập"],
           ["lt_allocator.py", "Phân bổ 1/biến động, áp trần, sinh lệnh theo bốn quy tắc thoát"],
           ["lt_backtest_scope.js", "Kiểm định 52 tháng, ba phạm vi xếp hạng × bốn pha lưới"],
           ["xay_dung_factor_ff5_vn.py", "Dựng chuỗi nhân tố Fama–French Việt Nam"],
           ["data/backtest_pha_luoi_20260826.json", "Toàn bộ số thô của Bảng 5.2 và 5.3"],
           ["CHIEN_LUOC_DAI_HAN.md", "Nhật ký thay đổi quy trình, kèm lý do từng lần đổi"]],
          caption="Bảng B1 — Danh mục mã nguồn.",
          widths=[6.5, 9.0])
    para(doc, "Tệp lt_backtest_tradingview.js được giữ lại nhưng không dùng: nó "
              "xếp hạng trên toàn rổ thay vì rổ đã qua lọc, và chỉ chạy một pha "
              "lưới. Mọi con số trong báo cáo này sinh từ lt_backtest_scope.js.")

    doc.save(OUT)
    return OUT, n_p, n_t, nav


if __name__ == "__main__":
    out, n_p, n_t, nav = build()
    print(f"Da nhap {n_p} doan + {n_t} bang nguyen van tu {NGUON_FF5}")
    print(f"NAV danh muc bao cao: {nav:,.0f} d")
    print(f"-> {out}")
