"""
build_report.py — Sinh khung bao cao .docx tu ket qua phan tich.

Moi bang so lieu deu la SO DA DO trong cac file phan tich. Cac doan can nguoi
viet duoc danh dau bang style "Cho dien" (chu nghieng, mau xam) va bat dau bang
dau [ ] de de tim va thay.

Chay:  python build_report.py
"""

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor, Cm

OUT = "Bao_cao_chien_luoc_dau_tu.docx"
BODY_FONT = "Times New Roman"


# ---------------------------------------------------------------- Tien ich
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

    fill = doc.styles.add_style("Cho dien", 1)
    fill.base_style = doc.styles["Normal"]
    fill.font.italic = True
    fill.font.color.rgb = RGBColor(0x88, 0x88, 0x88)

    cap = doc.styles.add_style("Chu thich bang", 1)
    cap.base_style = doc.styles["Normal"]
    cap.font.size = Pt(10)
    cap.font.italic = True
    cap.paragraph_format.space_before = Pt(2)
    cap.paragraph_format.space_after = Pt(10)


def todo(doc, text):
    doc.add_paragraph("[ ] " + text, style="Cho dien")


def para(doc, text, bold=False):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.bold = bold
    return p


def bullets(doc, items):
    for it in items:
        doc.add_paragraph(it, style="List Bullet")


def table(doc, header, rows, caption=None, widths=None):
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
            if i == 0:
                run.bold = True
    if widths:
        for r_ in t.rows:
            for i, w in enumerate(widths):
                r_.cells[i].width = Cm(w)
    if caption:
        doc.add_paragraph(caption, style="Chu thich bang")
    return t


# ---------------------------------------------------------------- Noi dung
def build():
    doc = Document()
    setup_styles(doc)
    for s in doc.sections:
        s.left_margin = s.right_margin = Cm(2.5)

    # ---------------------------------------------------------- Trang bia
    for _ in range(6):
        doc.add_paragraph()
    t = doc.add_paragraph()
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = t.add_run("XÂY DỰNG VÀ KIỂM ĐỊNH CHIẾN LƯỢC\nPHÂN BỔ DANH MỤC ĐẦU TƯ")
    r.bold = True
    r.font.size = Pt(20)

    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rs = sub.add_run("Từ kỳ vọng lợi nhuận đến luật thoát lệnh:\n"
                     "bằng chứng thực nghiệm trên thị trường chứng khoán Việt Nam")
    rs.italic = True
    rs.font.size = Pt(13)

    doc.add_paragraph()
    for line in ("Học viên:  [ ]", "Lớp / Khóa:  [ ]",
                 "Giảng viên hướng dẫn:  [ ]", "Ngày nộp:  [ ]"):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run(line).font.size = Pt(12)

    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    # ---------------------------------------------------------- Muc luc
    doc.add_heading("MỤC LỤC", 1)
    todo(doc, "Chèn mục lục tự động: References → Table of Contents → Automatic Table. "
              "Sau khi soạn xong nhấn chuột phải vào mục lục → Update Field → Update entire table.")
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    # ---------------------------------------------------------- 1
    doc.add_heading("1. TÓM TẮT ĐIỀU HÀNH", 1)
    todo(doc, "Viết sau cùng, khoảng 250–350 từ. Ba ý bắt buộc: (a) phát hiện chính — "
              "luật thoát hiện hành có alpha âm; (b) phát hiện phủ định — tầng phân bổ "
              "không tạo giá trị; (c) khuyến nghị và mức độ tin cậy.")

    para(doc, "Các số liệu chính để trích dẫn:", bold=True)
    table(doc,
          ["Chỉ tiêu", "Giá trị", "Cỡ mẫu"],
          [["Alpha luật thoát hiện hành (chế độ tăng)", "−0,235%/lệnh", "35.172"],
           ["Alpha luật thoát hiện hành (chế độ giảm)", "−0,692%/lệnh", "21.324"],
           ["Cải thiện khi đổi sang trailing stop 3% (tăng)", "+0,621%/lệnh", "30 cụm mã"],
           ["Cải thiện khi đổi sang trailing stop 3% (giảm)", "+0,710%/lệnh", "30 cụm mã"],
           ["Đóng góp của kỹ năng chọn điểm vào", "≈ +0,52%/lệnh", "35 lệnh thật"],
           ["Giá trị tăng thêm của tầng phân bổ softmax(ER)", "−3,06% (âm)", "6 cụm"],
           ["P(về nhất) — luật hiện hành / luật đề xuất", "7,8% / 25,9%", "σ nhóm 10%"]],
          "Bảng 1. Tổng hợp kết quả chính.", [8.5, 4.5, 3.0])

    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    # ---------------------------------------------------------- 2
    doc.add_heading("2. BỐI CẢNH VÀ HÀM MỤC TIÊU", 1)

    doc.add_heading("2.1. Cấu trúc cuộc thi", 2)
    bullets(doc, ["Chấm theo lợi nhuận thuần, kỳ thi kéo dài 2 tháng.",
                  "8 người dự thi. Không có luật loại vì mức sụt giảm tài sản.",
                  "Không được bán khống. Ràng buộc thanh toán T+2.",
                  "Không xem được bảng xếp hạng cho tới khi kết thúc.",
                  "Bắt buộc nộp báo cáo phân tích."])
    todo(doc, "Bổ sung quy chế chi tiết: vốn ban đầu, phí giao dịch áp dụng, danh mục "
              "cổ phiếu được phép, cách tính lợi nhuận cuối kỳ.")

    doc.add_heading("2.2. Hàm mục tiêu: vì sao không phải tối đa hóa tài sản", 2)
    para(doc, "Cấu trúc phần thưởng chỉ trả cho người về nhất khiến hàm mục tiêu trở "
              "thành P(về nhất) chứ không phải E[log W]. Đây là hàm lồi: về nhì và về "
              "thứ tám có giá trị gần như nhau. Hệ quả trực tiếp là hai điều thường "
              "đúng trong đầu tư dài hạn trở thành sai trong bối cảnh này:")
    bullets(doc, ["Giữ tiền mặt để hạ độ biến động làm giảm xác suất về nhất.",
                  "Tiêu chí Kelly — vốn tối ưu hóa tốc độ tăng trưởng dài hạn — "
                  "không phải tiêu chí đúng cho một kỳ thi hữu hạn."])
    para(doc, "Với 7 đối thủ, ngưỡng cần vượt là kỳ vọng của giá trị lớn nhất trong 7 "
              "mẫu, xấp xỉ 1,35 lần độ lệch chuẩn của nhóm trên mức trung bình. Chỉ có "
              "alpha là không đủ; cần cả phương sai có hướng.")
    todo(doc, "Nếu muốn chặt chẽ hơn, dẫn công thức kỳ vọng thống kê thứ tự của phân "
              "phối chuẩn và nêu giả định các đối thủ độc lập, đồng phân phối.")

    doc.add_heading("2.3. Ràng buộc không quan sát được bảng xếp hạng", 2)
    para(doc, "Vì không thấy vị trí của mình trong suốt kỳ thi, không thể áp dụng chiến "
              "thuật điều chỉnh mức độ tập trung theo thứ hạng — vốn là chiến thuật "
              "chuẩn trong các giải đầu tư. Mọi tham số phải được chốt trước và giữ "
              "nguyên, biến bài toán thành ra quyết định một lần.")

    # ---------------------------------------------------------- 3
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
    doc.add_heading("3. KHUNG LÝ THUYẾT", 1)

    doc.add_heading("3.1. Kỳ vọng lợi nhuận chuẩn hóa theo rủi ro", 2)
    para(doc, "Mỗi cơ hội được mô tả bằng xác suất thắng p và tỷ lệ lãi/lỗ b = Reward/Risk, "
              "với Risk chuẩn hóa bằng 1:")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("ER = p·b − (1 − p)")
    r.bold = True
    r.font.size = Pt(13)
    para(doc, "Điểm hòa vốn là p > 1/(1 + b). Đây là cổng lọc: dưới ngưỡng này, cơ hội "
              "bị loại — hợp lý vì quy chế cấm bán khống.")

    doc.add_heading("3.2. Phân bổ softmax và tham số nhiệt độ", 2)
    para(doc, "Trọng số được gán theo w_i = softmax(ER_i / τ). Tham số τ điều khiển mức "
              "độ tập trung: τ nhỏ dồn vốn vào cơ hội tốt nhất, τ lớn tiến về cân bằng đều.")
    para(doc, "Một vấn đề thiết kế được phát hiện trong quá trình xây dựng: τ tuyệt đối "
              "không bất biến với thang đo của ER. Khi thay đổi cách ước lượng p, dải ER "
              "dịch chuyển và cùng một giá trị τ mang ý nghĩa khác. Giải pháp là neo τ "
              "vào độ phân tán của chính ER: τ = k·σ(ER). Kiểm chứng cho thấy khi σ(ER) "
              "co từ 0,195 xuống 0,040, τ tự điều chỉnh từ 0,32 xuống 0,085 và hồ sơ "
              "trọng số giữ nguyên (40 / 29 / 19 / 12 phần trăm).")

    doc.add_heading("3.3. Một đơn giản hóa quan trọng", 2)
    para(doc, "Nếu b là thuộc tính của luật thoát chứ không phải của từng cổ phiếu — "
              "điều được xác nhận bằng dữ liệu ở Mục 6 — thì đặt b chung cho mọi mã cho:")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run("ER_i = p_i·(b + 1) − 1").bold = True
    para(doc, "Hằng số −1 triệt tiêu trong softmax, nên phân bổ chỉ còn phụ thuộc p_i, "
              "và (b+1)/τ gộp thành một tham số tập trung duy nhất. Tham số b chỉ quyết "
              "định có vào lệnh hay không, không quyết định chia vốn thế nào.")

    doc.add_heading("3.4. Vì sao không dùng tiêu chí Kelly", 2)
    todo(doc, "Trình bày Kelly f* = p − (1−p)/b và dạng đa tài sản f* = Σ⁻¹μ. Nêu hai "
              "lý do loại bỏ: (a) hàm mục tiêu của giải đấu không phải E[log W]; "
              "(b) ước lượng ma trận hiệp phương sai với cỡ mẫu hiện có sẽ khuếch đại "
              "sai số (hiện tượng error maximization).")

    # ---------------------------------------------------------- 4
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
    doc.add_heading("4. DỮ LIỆU VÀ PHƯƠNG PHÁP", 1)

    doc.add_heading("4.1. Nguồn dữ liệu", 2)
    table(doc,
          ["Bộ dữ liệu", "Phạm vi", "Quy mô", "Dùng cho"],
          [["Khuyến nghị thực tế", "30/07 – 10/08/2026", "60 khuyến nghị, 35 lệnh khớp",
            "Đo alpha thực, phản thực nghiệm luật thoát"],
           ["Giá lịch sử TradingView", "2018 – 2026", "30 mã, ~2.030 phiên/mã",
            "Kiểm định luật thoát theo chế độ thị trường"],
           ["Mô phỏng vào lệnh", "2018 – 2026", "56.496 lệnh",
            "Tách tác động luật thoát khỏi chất lượng điểm vào"]],
          "Bảng 2. Các bộ dữ liệu sử dụng.", [3.5, 3.2, 4.3, 5.0])

    doc.add_heading("4.2. Đính chính dữ liệu", 2)
    para(doc, "Trong quá trình kiểm tra, 5 lệnh (VHM, GMD, DGW, BID, MSB) được phát hiện "
              "vào đúng phiên cuối của cửa sổ dữ liệu, do đó thời gian nắm giữ bằng 0 "
              "phiên. Lợi nhuận chỉ số cùng kỳ của chúng bằng 0,00% nên phần “alpha” ghi "
              "nhận thực chất là biến động trong phiên không được trừ chỉ số — GMD ghi "
              "nhận +3,95% trong 0 phiên. Sau khi loại 5 lệnh này, alpha trung bình giảm "
              "từ +0,38% xuống +0,28% mỗi lệnh. Toàn bộ phân tích trong báo cáo dùng bộ "
              "35 lệnh đã hiệu chỉnh.")

    doc.add_heading("4.3. Phương pháp suy diễn thống kê", 2)
    bullets(doc, [
        "Bootstrap ghép cặp: các luật thoát được so sánh trên cùng tập điểm vào, "
        "nên dùng dữ liệu ghép cặp để loại nhiễu chung.",
        "Bootstrap gộp cụm theo mã: các lệnh mô phỏng chồng lấn nhau rất nhiều "
        "(vào lệnh mỗi phiên, nắm giữ ~9 phiên) nên sai số chuẩn thô sẽ thổi phồng "
        "mức ý nghĩa. Lấy mẫu lại ở cấp mã (30 cụm) xử lý triệt để tương quan nội mã.",
        "Kiểm định hoán vị: dùng để đánh giá sức phân biệt của biến phân loại setup.",
        "Block bootstrap theo ngày khuyến nghị: giữ nguyên cấu trúc phụ thuộc chéo "
        "bằng cách tái sử dụng nó thay vì ước lượng nó."])

    doc.add_heading("4.4. Một bẫy phương pháp đã tránh được", 2)
    para(doc, "Thiết kế ban đầu dự định học phân phối đồng thời của các kết quả rồi lấy "
              "trung bình mô phỏng để phân bổ. Cách này sai vì kỳ vọng là toán tử tuyến "
              "tính: E[Σ w_i r_i] = Σ w_i E[r_i], vế phải không chứa hiệp phương sai. "
              "Lấy trung bình xóa sạch chính cấu trúc phụ thuộc vừa học được; tương quan "
              "chỉ xuất hiện ở các mô-men bậc cao. Giải pháp là đọc P(vượt ngưỡng về nhất) "
              "từ mô phỏng thay vì đọc trung bình.")

    # ---------------------------------------------------------- 5
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
    doc.add_heading("5. KẾT QUẢ I — TẦNG PHÂN BỔ KHÔNG TẠO GIÁ TRỊ", 1)

    doc.add_heading("5.1. Thiết kế kiểm định", 2)
    para(doc, "Backtest walk-forward trên 6 cụm ngày khuyến nghị. Với mỗi cụm, p của "
              "từng loại setup chỉ được ước lượng từ các cụm trước đó, có co về base "
              "rate bằng Beta prior. Ba mốc so sánh được tách riêng để phân rã hiệu ứng "
              "chọn mã khỏi hiệu ứng đánh trọng số.")

    doc.add_heading("5.2. Kết quả", 2)
    table(doc,
          ["Chiến lược chọn mã", "Alpha gộp 6 cụm", "Phân vị so với bốc thăm"],
          [["Cân bằng đều toàn bộ ứng viên", "+2,92%", "—"],
           ["Bốc thăm ngẫu nhiên 4 mã", "+2,95%", "mốc so sánh"],
           ["Softmax chọn 4 mã theo ER", "−0,11%", "4%"],
           ["Cân bằng đều 4 mã chọn theo ER", "+1,00%", "15%"],
           ["Chọn 4 mã biến động cao nhất", "+0,21%", "7%"],
           ["Chọn 4 mã biến động thấp nhất", "+4,12%", "73% (không có ý nghĩa)"]],
          "Bảng 3. Hiệu suất các quy tắc chọn mã, đo bằng alpha gộp qua 6 cụm.",
          [7.0, 4.5, 4.5])

    para(doc, "Hai kết luận:", bold=True)
    bullets(doc, [
        "Tập trung là miễn phí. Rút từ toàn bộ ứng viên xuống 4 mã chọn ngẫu nhiên "
        "chỉ thay đổi alpha +0,02%. Số lượng vị thế là quyết định khẩu vị, không "
        "phải quyết định dựa trên dữ liệu.",
        "Toàn bộ chi phí nằm ở khâu chọn mã. Xếp hạng theo ER tốn 3,06% so với bốc "
        "thăm và rơi vào phân vị 4% của phân phối ngẫu nhiên."])

    doc.add_heading("5.3. Nguyên nhân gốc", 2)
    table(doc,
          ["Loại setup", "n", "p", "Alpha TB", "Độ lệch chuẩn"],
          [["Mua vùng chỉnh", "16", "68,8%", "+0,77%", "2,42%"],
           ["Mua breakout", "12", "66,7%", "+0,34%", "3,26%"]],
          "Bảng 4. Sức phân biệt của biến phân loại setup. Chênh lệch alpha +0,43%, "
          "sai số chuẩn 1,12%, t = 0,39. Kiểm định hoán vị 20.000 lần cho p-value = 0,689.",
          [5.0, 2.0, 2.5, 3.0, 3.5])

    para(doc, "Biến phân loại setup không có sức phân biệt đo được. Vì softmax khuếch "
              "đại chênh lệch ER theo hàm mũ, việc khuếch đại một tín hiệu rỗng gây hại "
              "chứ không trung tính. Kết luận quan trọng: softmax không phải là vấn đề; "
              "ước lượng p mới là vấn đề.")

    doc.add_heading("5.4. Đính chính một kết luận trước đó", 2)
    para(doc, "Nhận định “mua vùng chỉnh tốt hơn mua breakout” không được dữ liệu ủng hộ "
              "về giá trị trung bình. Điều dữ liệu ủng hộ là breakout có độ lệch chuẩn "
              "cao hơn (3,26% so với 2,42%) — một khẳng định về phương sai, không phải "
              "về kỳ vọng.")

    doc.add_heading("5.5. Cảnh báo về khai thác quá mức dữ liệu", 2)
    para(doc, "Năm quy tắc chọn mã đã được thử trên chỉ 6 quan sát. Kết quả tốt nhất "
              "(chọn theo biến động thấp) nằm ở phân vị 73%, tương đương p ≈ 0,27, hoàn "
              "toàn trong dao động ngẫu nhiên. Kết quả này không được coi là một phát hiện.")

    # ---------------------------------------------------------- 6
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
    doc.add_heading("6. KẾT QUẢ II — LUẬT THOÁT LỆNH", 1)

    doc.add_heading("6.1. Phản thực nghiệm trên tập lệnh thực", 2)
    para(doc, "Giữ nguyên 35 điểm vào đã thực hiện, chỉ thay đổi luật thoát:")
    table(doc,
          ["Luật thoát", "p", "b", "ER", "Alpha/lệnh", "Δ Alpha (KTC 95%)"],
          [["A. Chốt tại Mục tiêu 1", "68,6%", "0,69", "0,16", "+0,28%", "—"],
           ["B. Giữ đến hết kỳ", "71,4%", "0,75", "0,25", "+0,51%", "+0,23% [−0,01; +0,50]"],
           ["C. Trailing stop 3%", "71,4%", "0,82", "0,30", "+0,66%", "+0,38% [+0,10; +0,67]"],
           ["D. Nửa tại T1 + nửa trailing", "71,4%", "0,75", "0,25", "+0,56%", "+0,30% [+0,07; +0,55]"]],
          "Bảng 5. Phản thực nghiệm luật thoát trên 35 lệnh, bootstrap ghép cặp.",
          [5.2, 1.8, 1.6, 1.6, 2.4, 4.4])

    doc.add_heading("6.2. Mở rộng: 56.496 lệnh mô phỏng", 2)
    para(doc, "Để khắc phục ba hạn chế của mẫu nhỏ — cửa sổ chỉ 10 phiên, chỉ quan sát "
              "thị trường tăng, và trailing stop hầu như không kích hoạt — phân tích được "
              "mở rộng bằng dữ liệu 2018–2026. Vào lệnh tại giá mở cửa của mọi phiên trên "
              "30 mã, không lọc setup, nên kết quả đo thuần túy tác động của luật thoát. "
              "Chế độ thị trường xác định tại thời điểm vào lệnh bằng vị trí VNINDEX so "
              "với đường trung bình 50 phiên.")

    table(doc,
          ["Luật", "Chế độ", "n", "p", "W", "L", "b", "ER", "Alpha/lệnh"],
          [["A. Chốt +3% / cắt −4%", "Tăng", "35.172", "57,5%", "2,45%", "3,86%", "0,63", "−0,06", "−0,235%"],
           ["A", "Giảm", "21.324", "51,8%", "2,47%", "4,10%", "0,60", "−0,17", "−0,692%"],
           ["C. Trailing stop 3%", "Tăng", "35.172", "41,0%", "5,70%", "3,31%", "1,72", "+0,12", "+0,386%"],
           ["C", "Giảm", "21.324", "41,0%", "5,65%", "3,89%", "1,45", "+0,01", "+0,018%"]],
          "Bảng 6. Kết quả trên 56.496 lệnh mô phỏng, tính trên alpha vượt VNINDEX.",
          [4.0, 1.8, 2.0, 1.6, 1.6, 1.6, 1.4, 1.4, 2.0])

    para(doc, "Phát hiện quan trọng nhất: luật thoát hiện hành có alpha âm có ý nghĩa "
              "thống kê ở cả hai chế độ thị trường. Khoảng tin cậy gộp cụm theo mã là "
              "[−0,365%; −0,113%] khi thị trường tăng và [−0,828%; −0,553%] khi giảm. "
              "Chốt lãi tại +3% trong khi để lỗ chạy tới −4% là cấu trúc hủy hoại giá "
              "trị, độc lập với chất lượng điểm vào.", bold=True)

    doc.add_heading("6.3. Kiểm định theo chế độ thị trường", 2)
    table(doc,
          ["Chế độ", "C − A", "KTC 95%", "Số mã C thắng A"],
          [["Thị trường tăng (VNINDEX > MA50)", "+0,621%/lệnh", "[+0,390%; +0,879%]", "26/30"],
           ["Thị trường giảm (VNINDEX < MA50)", "+0,710%/lệnh", "[+0,478%; +0,958%]", "27/30"]],
          "Bảng 7. Chênh lệch giữa hai luật thoát, bootstrap gộp cụm theo mã, 30 cụm.",
          [6.0, 3.2, 4.3, 3.0])

    para(doc, "Trailing stop hữu ích hơn khi thị trường xuống — đúng lúc luật chốt tại "
              "mục tiêu để lỗ chạy tự do. Đây là kết quả ngược với lo ngại ban đầu rằng "
              "trailing stop chỉ hiệu quả trong xu hướng tăng.")

    doc.add_heading("6.4. Biến đổi hình dạng phân phối", 2)
    table(doc,
          ["Chỉ tiêu", "Luật A", "Luật C"],
          [["Tỷ lệ thắng", "57,5%", "41,0%"],
           ["Lãi trung bình khi thắng", "2,45%", "5,70%"],
           ["Lỗ trung bình khi thua", "3,86%", "3,31%"],
           ["Độ lệch chuẩn mỗi lệnh", "3,74%", "6,66%"],
           ["Độ lệch (skew) danh mục 2 tháng", "+0,09", "+0,34"],
           ["Thời gian nắm giữ trung bình", "6,1 phiên", "9,3 phiên"]],
          "Bảng 8. So sánh hình dạng phân phối lợi nhuận, chế độ thị trường tăng.",
          [7.0, 4.0, 4.0])

    para(doc, "Luật C đánh đổi tỷ lệ thắng lấy độ lớn khoản thắng: p giảm từ 57,5% xuống "
              "41,0% nhưng b tăng từ 0,63 lên 1,72. Độ lệch chuẩn mỗi lệnh gần gấp đôi và "
              "độ lệch của phân phối danh mục chuyển sang dương rõ rệt. Trong bối cảnh "
              "giải đấu, đây chính là hình dạng cần thiết.")

    # ---------------------------------------------------------- 7
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
    doc.add_heading("7. PHÂN RÃ NGUỒN GỐC ALPHA", 1)
    para(doc, "Có mốc so sánh từ điểm vào ngẫu nhiên cho phép tách hai thành phần:")
    table(doc,
          ["Thành phần", "Cách đo", "Giá trị"],
          [["Kỹ năng chọn điểm vào",
            "35 lệnh thật dưới luật A (+0,28%) trừ vào lệnh ngẫu nhiên dưới luật A, "
            "chế độ tăng (−0,235%)", "≈ +0,52%/lệnh"],
           ["Cải thiện từ luật thoát",
            "Chênh lệch C − A trên 56.496 lệnh mô phỏng", "+0,62 đến +0,71%/lệnh"]],
          "Bảng 9. Phân rã alpha theo nguồn gốc.", [4.5, 8.0, 3.0])
    para(doc, "Hai nguồn có độ lớn tương đương. Kỹ năng chọn mã là có thật, nhưng ước "
              "lượng dựa trên 35 lệnh nên rất nhiễu. Điểm khác biệt về mặt hành động: "
              "luật thoát có thể sửa ngay, còn kỹ năng chọn mã cần thời gian tích lũy.")

    # ---------------------------------------------------------- 8
    doc.add_heading("8. MÔ PHỎNG GIẢI ĐẤU", 1)
    doc.add_heading("8.1. Thiết lập mô hình", 2)
    bullets(doc, ["8 vòng phân bổ, mỗi vòng 4 vị thế cân bằng đều.",
                  "Tương quan nội danh mục 0,5, mô hình hóa qua copula Gaussian một yếu tố.",
                  "Chế độ thị trường rút ngẫu nhiên với tỷ lệ 62% tăng / 38% giảm, "
                  "theo phân bố quan sát được giai đoạn 2018–2026.",
                  "Đối thủ có alpha 2 tháng phân phối chuẩn quanh 0; beta triệt tiêu "
                  "giữa các thí sinh nên chỉ so sánh phần vượt chỉ số."])

    doc.add_heading("8.2. Kết quả", 2)
    table(doc,
          ["Chiến lược", "Alpha TB", "Độ lệch", "Skew", "PV 95%", "PV 99%"],
          [["A + kỹ năng chọn điểm vào", "+0,89%", "6,45%", "+0,09", "+11,50%", "+16,67%"],
           ["C + kỹ năng chọn điểm vào", "+6,30%", "9,57%", "+0,34", "+23,36%", "+30,16%"]],
          "Bảng 10. Phân phối alpha danh mục sau 2 tháng, 200.000 lần chạy.",
          [5.5, 2.4, 2.2, 1.8, 2.2, 2.2])

    table(doc,
          ["Độ biến động của nhóm thi", "5%", "8%", "10%", "12%", "15%"],
          [["Luật A (đang dùng)", "20,8%", "11,2%", "7,8%", "5,7%", "3,9%"],
           ["Luật C (đề xuất)", "46,3%", "32,8%", "25,9%", "20,5%", "14,7%"],
           ["Bội số cải thiện", "×2,2", "×2,9", "×3,4", "×3,6", "×3,8"]],
          "Bảng 11. Xác suất về nhất. Mức nền nếu 8 người ngang tài là 12,5%.",
          [5.5, 1.9, 1.9, 1.9, 1.9, 1.9])

    todo(doc, "Nếu cần, bổ sung biểu đồ mật độ phân phối alpha 2 tháng của hai luật thoát "
              "để minh họa sự khác biệt về đuôi phải.")

    # ---------------------------------------------------------- 9
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
    doc.add_heading("9. HẠN CHẾ VÀ RỦI RO", 1)
    bullets(doc, [
        "Mức Mục tiêu 1 (+3%) và cắt lỗ (−4%) là giá trị đại diện, không phải mức "
        "thật của từng khuyến nghị. Độ lớn kết quả phụ thuộc lựa chọn này; hướng thì không.",
        "Mô phỏng vào lệnh mọi phiên nên alpha âm của luật A không hàm ý danh mục "
        "thực tế có alpha âm — điểm vào có chọn lọc đóng góp thêm khoảng +0,52%/lệnh.",
        "Ước lượng kỹ năng chọn điểm vào dựa trên 35 lệnh trong cửa sổ 10 phiên, "
        "sai số rất lớn.",
        "Backtest tầng phân bổ chỉ có 6 cụm quan sát; các khoảng tin cậy rộng.",
        "Mô phỏng giải đấu giả định đối thủ có alpha phân phối chuẩn quanh 0 và độc "
        "lập với nhau — giả định này không kiểm chứng được.",
        "Dữ liệu giá đã điều chỉnh cổ tức và phát hành thêm; VHM có hệ số điều chỉnh 2,0.",
        "Toàn bộ phân tích bỏ qua tác động giá khi đặt lệnh và giả định khớp đủ khối lượng."])
    todo(doc, "Bổ sung các hạn chế riêng của quy chế cuộc thi nếu có: giới hạn số lệnh, "
              "danh mục mã được phép, quy định về tiền mặt.")

    # ---------------------------------------------------------- 10
    doc.add_heading("10. KẾT LUẬN VÀ KHUYẾN NGHỊ", 1)
    para(doc, "Khuyến nghị hành động", bold=True)
    table(doc,
          ["#", "Khuyến nghị", "Cơ sở", "Mức tin cậy"],
          [["1", "Thay luật chốt tại Mục tiêu 1 bằng trailing stop 3%",
            "56.496 lệnh, hai chế độ thị trường, 53/60 cặp mã-chế độ thắng", "Cao"],
           ["2", "Bỏ xếp hạng theo ER khi chọn mã; cân bằng đều",
            "Xếp hạng ER rơi vào phân vị 4% so với bốc thăm", "Trung bình"],
           ["3", "Số vị thế 4–9 tùy khẩu vị",
            "Tập trung không tốn alpha (+0,02%)", "Trung bình"],
           ["4", "Giữ engine phân bổ ở vai trò áp ràng buộc",
            "Cổng ER, trần vị thế, sàn ticket, làm tròn lô vẫn hữu ích", "—"]],
          "Bảng 12. Khuyến nghị và mức độ tin cậy.", [1.0, 5.5, 6.0, 2.5])

    todo(doc, "Viết đoạn kết 150–200 từ. Gợi ý nhấn mạnh: giá trị của việc kiểm định "
              "nghiêm túc nằm ở chỗ nó loại bỏ được những ý tưởng nghe hợp lý nhưng "
              "không có bằng chứng — trong nghiên cứu này là toàn bộ tầng phân bổ, "
              "kể cả các quy tắc chọn mã do chính nhóm đề xuất.")

    # ---------------------------------------------------------- Phu luc
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
    doc.add_heading("PHỤ LỤC A — MÃ NGUỒN VÀ KHẢ NĂNG TÁI LẬP", 1)
    table(doc,
          ["Tệp", "Chức năng"],
          [["allocator.py", "Engine phân bổ softmax(ER), áp ràng buộc, sinh lệnh kèm phí"],
           ["exit_rules.py", "Phản thực nghiệm luật thoát trên 35 lệnh, đo bằng alpha"],
           ["backtest_portfolio.py", "Backtest walk-forward, tách hiệu ứng chọn mã và đánh trọng số"],
           ["strategy_backtest.py", "Kiểm định các quy tắc chọn mã so với bốc thăm"],
           ["regime_test.py", "Kiểm định gộp cụm trên 56.496 lệnh theo chế độ thị trường"],
           ["tournament_sim.py", "Block bootstrap từ dữ liệu thực ra P(về nhất)"],
           ["final_sim.py", "Mô phỏng giải đấu với tham số đo được"]],
          "Bảng A1. Danh mục mã nguồn. Chạy bằng lệnh "
          "PYTHONIOENCODING=utf-8 python <tên tệp>.", [5.0, 10.0])
    todo(doc, "Nếu quy chế yêu cầu nộp mã nguồn, đính kèm thư mục hoặc dẫn liên kết kho lưu trữ.")

    doc.add_heading("PHỤ LỤC B — BẢNG SỐ LIỆU CHI TIẾT", 1)
    todo(doc, "Dán bảng alpha theo từng mã (30 dòng, tách theo chế độ thị trường) từ "
              "regime_test.py, và bảng 35 lệnh thực từ tệp Excel backtest.")

    doc.save(OUT)
    print(f"Da tao: {OUT}")
    print(f"  {len(doc.paragraphs)} doan, {len(doc.tables)} bang")
    n_todo = sum(1 for p in doc.paragraphs if p.style.name == "Cho dien")
    print(f"  {n_todo} cho can dien (danh dau bang [ ] va chu nghieng xam)")


if __name__ == "__main__":
    build()
