# Chiến lược đầu tư dài hạn — Danh mục 1 (200tr) & Danh mục 2 (60tr)

**Chốt ngày 17/08/2026.** Thay thế hoàn toàn khung "tối đa hoá P(về nhất)" của cuộc thi.

---

## 0. Triết lý đầu tư tích hợp: Peter Lynch + kỹ thuật

Triết lý nền tảng của hệ thống này là kết hợp giữa hai nguyên tắc:

1. **Giá trị theo Peter Lynch**: mua doanh nghiệp tốt, hiểu rõ mô hình kinh doanh, ưu tiên lợi nhuận bền vững, ROE tốt, dòng tiền dương và giá hợp lý. Một cổ phiếu không là "rẻ" chỉ vì giá thấp; nó phải là doanh nghiệp có chất lượng thực.
2. **Xác nhận kỹ thuật theo quan điểm mô hình**: không được mua chỉ vì doanh nghiệp tốt mà không xem thị trường đang đứng ở đâu. Xu hướng dài hạn, cấu trúc giá và sức mạnh tương đối so với chỉ số là các "cửa kiểm tra" để tránh mua vào đúng thời điểm quá yếu hoặc quá đắt.

Nói ngắn gọn: **chọn doanh nghiệp tốt, định giá hợp lý, rồi chờ kỹ thuật xác nhận xu hướng ủng hộ**.

### Nguyên lý vận hành

- **Lớp 1 — Chất lượng doanh nghiệp**: doanh thu, lợi nhuận, ROE, dòng tiền, quản trị và mô hình kinh doanh rõ ràng.
- **Lớp 2 — Định giá**: không mua theo cảm giác, mà mua ở mức giá vừa đủ hấp dẫn so với năng lực sinh lời thực tế.
- **Lớp 3 — Xác nhận kỹ thuật**: giá phải đang ở trong xu hướng tăng, mạnh hơn thị trường, không bị rơi khỏi đường hỗ trợ dài hạn.

### Checklist mua (điều kiện bắt buộc)

Chỉ mua khi cổ phiếu thỏa mãn đồng thời tất cả các mệnh đề dưới đây:

- [ ] Doanh nghiệp có mô hình kinh doanh rõ ràng, lợi nhuận thực chất, ROE/ROIC ổn định hoặc tăng trưởng bền
- [ ] Không nằm trong nhóm doanh nghiệp khó hiểu, quản trị yếu hoặc lợi nhuận bị bóp méo
- [ ] Giá không quá đắt so với sinh lời và tốc độ tăng trưởng (P/E, PEG, EV/EBITDA hoặc FCF yield hợp lý)
- [ ] Giá đóng cửa > MA200 và MA50 > MA200
- [ ] RS 12 tháng (bỏ 1 tháng gần nhất) > 0, nghĩa là mạnh hơn VNINDEX
- [ ] Xu hướng dài hạn còn sạch, không quá chập chờn hoặc mất đà
- [ ] ATR không quá cao để tránh đầu cơ cực đoan
- [ ] Không đang ở trạng thái quá nóng kỹ thuật hoặc giá đã vượt quá định giá hợp lý

### Checklist bán / dừng lỗ (điều kiện thoát)

Bán hoặc dừng nắm giữ khi ít nhất một điều kiện sau xảy ra:

- [ ] Giá rơi dưới 97% MA200 (đệm 3% chống nhiễu)
- [ ] RS 12 tháng suy yếu xuống dưới −5% so với VNINDEX
- [ ] Cổ phiếu rơi khỏi top 40% xếp hạng điểm
- [ ] Xuất hiện tín hiệu phá vỡ cấu trúc dài hạn hoặc mô hình doanh nghiệp xấu đi rõ rệt
- [ ] Vượt quá mức cắt lỗ theo kỷ luật (ví dụ −25% so với giá vốn nếu áp dụng rủi ro cứng)

### Qui tắc tránh sai lầm

- Không mua cổ phiếu chỉ vì "được khuyên" hoặc vì đã tăng mạnh.
- Không mua doanh nghiệp mình không hiểu.
- Không coi kỹ thuật là nguyên nhân quyết định duy nhất; kỹ thuật chỉ là lớp xác nhận, không thay thế giá trị hạ tầng.
- Không cố gắng mua ở đáy tuyệt đối; thay vào đó, ưu tiên mua khi cơ bản tốt và thị trường đã bắt đầu xác nhận sự phục hồi.

Kết luận ngắn gọn:

> Mua doanh nghiệp tốt ở giá hợp lý, nhưng chỉ vào khi xu hướng và kỹ thuật đang ủng hộ. Đây là sự kết hợp giữa "đầu tư giá trị" và "đầu tư theo xu hướng" — chặt chẽ về chất lượng, cẩn trọng về thời điểm, và kỷ luật về rủi ro.

---

## 1. Đổi hàm mục tiêu

| | Khung cũ (đã bỏ) | Khung mới |
|---|---|---|
| Mục tiêu | `P(về nhất)` trong 8 người, 2 tháng | Tốc độ gộp vốn dài hạn `E[log NAV]` |
| Hệ quả | Khuyến khích tập trung, chọn mã biến động cao, coi thường sụt giảm | Ưu tiên mã mạnh bền, kiểm soát sụt giảm, vòng quay thấp |
| Nắm giữ | 9–20 phiên | Nhiều tháng, không có hạn giữ |
| Chốt lời | Trailing 3% từ đỉnh | Không có mục tiêu chốt lời; chỉ bán khi hỏng tiêu chí |

Các file `tournament_sim.py`, `final_sim.py`, `contest_sim.py`, `allocator.py` (softmax ER), `strategy_backtest.py`, `backtest_portfolio.py` đã chuyển sang `archive_khung_cu/`. Không dùng lại.

---

## 2. Hệ thống ba tầng

### Tầng 1 — Bộ lọc cứng (mã có được phép mua không)

| Điều kiện | Ngưỡng | Lý do |
|---|---|---|
| Thanh khoản | GTGD TB 20 phiên ≥ 10 tỷ/phiên | 200tr vào/ra không làm lệch giá |
| Xu hướng dài hạn | Giá đóng cửa > MA200 | Chỉ nắm giữ mã đang ở pha tăng |
| Cấu trúc | MA50 > MA200 | Loại mã mới hồi kỹ thuật trong xu hướng giảm |
| **Mạnh hơn thị trường** | RS 12 tháng (bỏ 1 tháng gần nhất) > 0 | Đây chính là điều kiện "mạnh hơn VN-Index" |
| Chặn an toàn | ATR ≤ 6%/phiên | Loại mã đầu cơ cực đoan |

Bỏ 1 tháng gần nhất (skip-month) là chuẩn học thuật: đảo chiều ngắn hạn làm nhiễu tín hiệu momentum.

### Tầng 2 — Điểm xếp hạng (chọn mã nào trong số đạt chuẩn)

`Điểm = 0,40 × RS12T(bỏ 1T) + 0,30 × RS6T + 0,20 × RS3T + 0,10 × Chất lượng xu hướng`

Tất cả tính bằng **phân vị** trong rổ, không dùng giá trị tuyệt đối. Chất lượng xu hướng = R² của log(giá) theo thời gian trên ~6 tháng — momentum "mượt" bền hơn momentum "giật cục".

**Không còn dùng `p` (xác suất thắng) hay `ER`.** Kiểm định hoán vị trước đây cho p-value 0,689: `p` không có sức phân biệt, và softmax khuếch đại nó theo hàm mũ nên khuếch đại nhiễu.

### Tầng 3 — Phân bổ (mua bao nhiêu)

- Tỷ trọng ∝ **1 / ATR** (rủi ro ngang nhau giữa các vị thế), không theo điểm xếp hạng.
- Trần 15%/mã (DM1), 20%/mã (DM2); trần ngành 30% (DM1), 40% (DM2).
- Trần trùng lặp: một mã ≤ 10% **tổng tài sản hai tài khoản**, áp sau khi làm tròn lô.
- **Tiền mặt sinh ra tự động**: mỗi "ô" không tìm được mã đạt chuẩn thì ô đó nằm tiền. Không có bất kỳ quy tắc canh chỉ số nào — đã kiểm chứng 17/08 rằng bộ lọc VNINDEX theo MA50 **không** dự báo được hướng chỉ số.

Số ô: **DM1 = 10, DM2 = 8** (đo được, xem mục 4).

### Luật thoát

Rà soát **đầu mỗi tháng**. Giữ tiếp khi còn đủ **cả ba**:

1. Giá đóng cửa > 0,97 × MA200 (đệm 3% chống nhiễu)
2. RS 12 tháng so với VNINDEX > −5%
3. Còn trong **top 40%** bảng xếp hạng điểm

Hỏng bất kỳ điều nào → bán toàn bộ vị thế, tiền chuyển sang mã đứng đầu danh sách chờ. Lệch tỷ trọng < 3% NAV thì **không** điều chỉnh (biên không giao dịch). Chặn cứng một chiều: −25% so với giá vốn.

---

## 3. Kết quả backtest (52 tháng, 04/2022 → 08/2026, 112 mã HOSE)

Đã trừ phí 0,4%/vòng quay. Dữ liệu tuần lấy từ TradingView, mỗi điểm cách 4 tuần.

| Chiến lược | Lợi nhuận/năm | Sụt giảm tối đa | Vòng quay/năm |
|---|---|---|---|
| **Hệ thống này (10 ô, rà soát tháng)** | **13,89%** | **−21,3%** | 1,77× |
| VNINDEX mua & giữ | 7,51% | −20,2% | 0 |
| Tái cân bằng toàn bộ mỗi tháng (không giữ lại) | 6,95% | −34,5% | 4,51× |
| Cân bằng đều toàn bộ mã qua lọc | 2,93% | −27,4% | 3,43× |
| **Bốc thăm 10 mã từ rổ đã qua lọc** | 2,43% | −27,6% | — |
| Top 10 điểm RS nhưng **bỏ** bộ lọc xu hướng | 2,28% | −35,8% | 4,23× |

**Ba điều đọc được:**

1. **Bộ lọc xu hướng là phần đóng góp lớn nhất** (2,28% → 13,89%). Mua mã mạnh mà không kiểm tra xu hướng dài hạn thì vô ích.
2. **Xếp hạng RS có tạo giá trị** — 13,89% so với 2,43% của bốc thăm trong cùng rổ đã lọc. Đây là điểm khác biệt lớn nhất so với tầng xếp hạng ER cũ (nằm ở phân vị 4%, tệ hơn bốc thăm).
3. **Tốc độ THOÁT quan trọng hơn tốc độ vào.** Rà soát hằng quý thay vì hằng tháng làm tụt 13,89% → 7,06%. Nhưng *tái cân bằng* toàn bộ mỗi tháng lại chỉ còn 6,95% vì phí — nên: **soát hằng tháng, giao dịch chỉ khi luật kích hoạt.**

**Cân bằng đều vs 1/ATR:** lợi nhuận gần như nhau (13,26% vs 13,89%) nhưng 1/ATR cho sụt giảm nhỏ hơn rõ rệt (−25,0% vs −21,3%). Đó là lý do chọn 1/ATR — vì rủi ro, không vì lợi nhuận.

### Độ nhạy (chạy để tự kiểm tra, đừng tin một con số đơn lẻ)

| Ngưỡng top | 25% | 33% | **40%** | 50% | 60% |
|---|---|---|---|---|---|
| Lợi nhuận/năm | 11,9% | 12,6% | **15,4%** | 10,3% | 8,1% |

| Số ô | 5 | 6 | **8** | **10** | 12 | 15 |
|---|---|---|---|---|---|---|
| Lợi nhuận/năm | 8,6% | 10,5% | **13,1%** | **13,9%** | 9,4% | 8,6% |

---

## 4. ⚠️ Cảnh báo phải đọc trước khi tin con số

1. **Alpha tháng +0,54%, t = 0,87 → KHÔNG có ý nghĩa thống kê.** Với 52 tháng, chênh lệch 6 điểm/năm so với VNINDEX vẫn nằm trong dao động ngẫu nhiên. Không được viết vào báo cáo như một kết luận chắc chắn.
2. **Ngưỡng 40% là đỉnh của bề mặt độ nhạy** → phải coi là may. Điều đáng tin là *cả họ* 25–60% đều thắng VNINDEX, không phải riêng con số 40%.
3. **Chia đôi giai đoạn cho hai bức tranh trái ngược:**
   - 04/2022 → 06/2024: hệ thống **+15,4%/năm** trong khi VNINDEX **−1,4%/năm**
   - 06/2024 → 08/2026: hệ thống **+12,9%/năm** trong khi VNINDEX **+17,2%/năm**

   Đây là chữ ký kinh điển của chiến lược theo xu hướng: **vượt trội khi thị trường xấu, thua khi thị trường tăng mạnh.** Phải chấp nhận trước, đừng bỏ hệ thống giữa chừng vì lý do này.
4. **Chỉ 5,8 năm dữ liệu, một thị trường.** Chưa qua được một chu kỳ đầy đủ.

---

## 5. Trạng thái ngày 17/08/2026

Quét 112 mã HOSE: **chỉ 8 mã qua được bộ lọc** (7,1%). VNINDEX 1.727,46 đang **dưới MA200 (1.776)**. Độ rộng thị trường rất hẹp — đó là lý do hệ thống tự động giữ 17–38% tiền mặt, không phải vì phán đoán chủ quan về thị trường.

| # | Mã | Giá | Điểm | RS12T | RS6T | RS3T | ATR% | Ngành |
|---|---|---|---|---|---|---|---|---|
| 1 | VIC | 198.000 | 0,81 | +269,8% | +41,4% | −2,9% | 3,42 | Bất động sản |
| 2 | MSB | 16.100 | 0,61 | +16,3% | +38,0% | +21,5% | 1,47 | Ngân hàng |
| 3 | STB | 74.200 | 0,60 | +25,0% | +26,2% | +13,3% | 2,46 | Ngân hàng |
| 4 | VHM | 68.200 | 0,56 | +39,9% | +36,2% | −5,0% | 4,78 | Bất động sản |
| 5 | LPB | 50.900 | 0,51 | +27,9% | +23,3% | +7,0% | 3,27 | Ngân hàng |
| 6 | BSR | 26.000 | 0,43 | +64,1% | +14,1% | −8,5% | 4,09 | Dầu khí |
| 7 | GMD | 78.800 | 0,31 | +16,3% | +12,5% | +10,9% | 2,64 | Cảng biển |
| 8 | VPI | 60.700 | 0,16 | +3,5% | +4,2% | +9,2% | 2,88 | Bất động sản |

Bảng lệnh cụ thể: `data/ke_hoach_20260817.txt` (sinh bằng `lt_allocator.py`).

**Vị thế hiện tại không đạt chuẩn mới:** PVT (MA50 < MA200, thua VNINDEX 12T), TCB (dưới MA200), VNM (MA50 < MA200), BAF (thua VNINDEX 12T). MSB đang giữ ở DM2 thì **đạt chuẩn** — giữ nguyên.

---

## 6. Quy trình vận hành hằng tháng

1. Mở TradingView Desktop, khung ngày. Dán `lt_scan_tradingview.js` vào `ui_evaluate`, chờ xong (~3–10 phút), kiểm tra trùng dữ liệu, xuất ra `data/scan_YYYYMMDD.json`.
2. `PYTHONIOENCODING=utf-8 python lt_screener.py` → bảng xếp hạng + `data/candidates_YYYYMMDD.json`.
3. Cập nhật `HOLDINGS` và `TIEN_MAT` trong `lt_config.py` cho khớp sao kê.
4. `PYTHONIOENCODING=utf-8 python lt_allocator.py` → bảng lệnh.
5. Đặt lệnh. Trong tháng **không làm gì** trừ khi chạm chặn cứng −25%.

---

## 7. File trong thư mục

| File | Vai trò |
|---|---|
| `lt_config.py` | Toàn bộ tham số: vốn, số ô, bộ lọc, luật thoát, phân ngành |
| `lt_screener.py` | Lọc + xếp hạng RS |
| `lt_allocator.py` | Phân bổ 1/ATR, trần, làm tròn lô, sinh lệnh |
| `lt_scan_tradingview.js` | Quét dữ liệu từ TradingView |
| `lt_backtest_tradingview.js` | Backtest, đúng đoạn code đã tạo ra số ở mục 3 |
| `exit_rules.py`, `regime_test.py` | Bằng chứng cũ cho nguyên tắc "không đặt mục tiêu chốt lời" — vẫn còn giá trị |
| `archive_khung_cu/` | Khung P(về nhất) đã bỏ, giữ lại để đối chiếu báo cáo |
