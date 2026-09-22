# Kết quả quét TradingView và chạy chiến lược Quỹ — 19/09/2026

Dữ liệu giá: đóng cửa **18/09/2026**. Phạm vi: **112 cổ phiếu HOSE trong rổ cấu hình của Quỹ + VNINDEX**, không phải toàn bộ cổ phiếu niêm yết Việt Nam. Đã đọc trực tiếp TradingView Desktop qua cầu nối có sẵn trong dự án.

Kết quả: **11/112 mã qua bộ lọc**. Top kỹ thuật: **VIC, STB, MSB, VHM, BSR**. Theo hồ sơ thẩm định hiện lưu, chỉ **BSR và DHC** qua đủ bốn bước mua. DHC đồng thời vi phạm quy tắc giữ top 40%; cần đọc kết quả allocator cùng lịch rà soát, không suy diễn nhãn `buy_ready` thành lệnh mua ngay.

## Xếp hạng candidate

Điểm = 40% phân vị RS12 tháng bỏ tháng gần nhất + 30% RS6 tháng + 20% RS3 tháng + 10% chất lượng xu hướng; phân vị tính trong 11 mã đã qua lọc. Giá tính bằng đồng; RS12 là chênh lệch lợi suất với VNINDEX, đơn vị điểm phần trăm.

| Hạng | Mã | Giá | Điểm | RS12 bỏ 1T | ATR | GTGD TB20 (tỷ/phiên) | B3 | B4 | Ngày hồ sơ |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | VIC | 241,200 | 0.96 | +187.6 | 3.68% | 1489.1 | Phủ quyết | Chưa đánh giá | 2026-09-01 |
| 2 | STB | 78,200 | 0.75 | +30.3 | 2.42% | 463.5 | Phủ quyết | Chờ | 2026-09-14 |
| 3 | MSB | 12,900 | 0.60 | +12.6 | 2.13% | 267.6 | Đạt | Chờ | 2026-09-14 |
| 4 | VHM | 71,000 | 0.58 | +25.7 | 3.40% | 705.9 | Phủ quyết | Chờ | 2026-09-14 |
| 5 | BSR | 30,200 | 0.57 | +50.8 | 3.82% | 336.7 | Đạt | Đạt | 2026-09-01 |
| 6 | LPB | 48,000 | 0.40 | +11.8 | 2.78% | 186.8 | Đạt | Chờ | 2026-09-01 |
| 7 | BAF | 32,050 | 0.40 | +8.1 | 1.29% | 79.5 | Chưa đánh giá | Chưa đánh giá | Chưa có |
| 8 | HCM | 25,500 | 0.37 | +2.0 | 2.78% | 144.9 | Đạt | Chưa đánh giá | 2026-09-01 |
| 9 | DHC | 36,550 | 0.33 | +4.8 | 2.89% | 16.2 | Đạt | Đạt | 2026-09-14 |
| 10 | HDB | 27,500 | 0.33 | +6.9 | 1.86% | 566.3 | Chưa đánh giá | Chưa đánh giá | Chưa có |
| 11 | GMD | 77,300 | 0.21 | +10.3 | 1.79% | 114.4 | Đạt | Chờ | 2026-09-01 |

So với bản 15/09: HCM mới vào rổ đạt chuẩn; không mã nào rời rổ. STB lên hạng 2, MSB lên hạng 3; VHM xuống hạng 4 và DHC xuống hạng 9. DHC/HDB cùng điểm chính xác nên cùng thứ hạng tương đối 80%, dù thứ tự hiển thị là 9/10.

**Diễn giải theo Quỹ:** VIC/STB/VHM bị phủ quyết ở B3. MSB/LPB/GMD chờ định giá; HCM chưa xong B4; BAF/HDB chưa thẩm định. BSR là mã duy nhất vừa qua bốn bước mua vừa còn trong top 40% giữ vị thế. Hồ sơ cơ bản/định giá được đọc từ `data/tham_dinh.json`, chưa được tái thẩm định bằng thông tin mới trong lần chạy này.

## Chạy allocator và mô phỏng kỳ rà soát 21/09

- Đã chạy screener, allocator ngày 19/09 và mô phỏng allocator ngày 21/09 trên cùng giá đóng cửa 18/09. Đây là đầu ra mô hình, không có lệnh nào được gửi tới công ty chứng khoán.
- DM1 thiếu dữ liệu vốn/vị thế trong cấu hình, nên allocator bỏ qua phân bổ.
- DM2: NAV **60.640.363 đồng**, cổ phiếu **24.716.000 đồng (40,8%)**, tiền mặt **35.924.363 đồng (59,2%)**; đang có MSB 840, BSR 100, VHM 50, DHC 200 cổ phiếu theo sổ cấu hình.
- Mô phỏng 21/09: **không có lệnh ròng**. Mua thêm 100 BSR bị khóa bởi gia hạn quy tắc 5 đến 30/09. DHC bị tín hiệu bán do hạng 80% nhưng allocator bù trừ với mua lại đúng 200 cổ phiếu, nên vị thế không đổi. Đây là hành vi code hiện tại; không đồng nghĩa DHC thỏa mọi quy tắc giữ.
- MSB/VHM chưa có xác nhận `luan_diem_con_nguyen`; hồ sơ VHM phủ quyết mua mới nhưng chưa đánh dấu luận điểm gãy để kích hoạt quy tắc bán số 4. Trạng thái thiếu rà soát được giữ nguyên, không tự suy diễn thay Quỹ.
- Ngưỡng định giá/khóa mua lại và lịch rà soát có thể làm một mã mạnh về kỹ thuật chưa đủ điều kiện giao dịch.

## Backtest phần kỹ thuật

Chạy `lt_backtest_scope.js` với lịch sử tuần mới lấy, giữ 300 quan sát VNINDEX gần nhất, lấy mẫu cách bốn quan sát tuần và dịch điểm cuối lần lượt 0/1/2/3 tuần. Mỗi pha có 75 điểm, dùng 22 điểm khởi động và 52 kỳ nắm giữ. Căn ngày theo timestamp, không căn lệch bằng độ dài chuỗi.

B1 xếp hạng trong rổ qua lọc và chèn thứ hạng cho mã đang giữ rơi khỏi rổ; B2 bán khi mã đang giữ rời rổ. B1 gần cách mô tả chiến lược hiện tại hơn, nhưng allocator vẫn cần rà soát tay với mã rời rổ. Cấu hình backtest: 10 ô, trần mã 15%, giữ top 40%, biên 3%, phí vòng quay 0,4%.

**CAGR dưới đây đã quy đổi theo thời gian lịch thực tế**. Engine gốc coi một kỳ bốn tuần như một tháng và dùng 12 kỳ/năm; số gốc được giữ trong JSON, số quy đổi nằm ở `cagr_calendar` và có sai số làm tròn nhỏ. Ngày cuối bảng là timestamp của bar tuần, không nhất thiết là ngày thứ Sáu đóng cửa.

| Pha | Mốc đầu | Bar tuần cuối | CAGR B1 | CAGR B2 | CAGR VNINDEX | MDD B1 | t alpha B1 |
|---:|---|---|---:|---:|---:|---:|---:|
| 0 | 2022-09-05 | 2026-09-14 | 13.09% | 13.09% | 9.74% | -29.38% | 0.48 |
| 1 | 2022-08-29 | 2026-09-07 | 9.50% | 9.72% | 8.76% | -25.86% | 0.15 |
| 2 | 2022-08-22 | 2026-09-03 | 10.38% | 10.32% | 9.55% | -24.02% | 0.18 |
| 3 | 2022-08-15 | 2026-08-24 | 12.67% | 12.21% | 9.55% | -28.28% | 0.47 |

Trung bình bốn pha: **B1 11.41%/năm**, B2 11.33%/năm, VNINDEX 9.40%/năm. Tái cân bằng toàn bộ mỗi kỳ: 10.60%/năm; đối chứng bốc thăm một chuỗi hạt giống: 2.78%/năm. Bình quân pha là kiểm tra độ nhạy, không phải lợi suất một danh mục có thể giao dịch hay bốn mẫu độc lập.

**Kết luận:** alpha chưa có bằng chứng thống kê thuyết phục (t của B1 chỉ 0,15–0,48); kết quả còn nhạy với điểm lấy mẫu. Không dùng số cũ 13,89%/năm như kết quả của chiến lược hiện tại.

### Giới hạn của phép đo

- Đây là backtest xấp xỉ phần kỹ thuật, không phải toàn bộ chiến lược Quỹ. Chưa có lịch sử thẩm định/định giá theo thời điểm, quy tắc bán tùy nghi, lịch rà soát bổ sung, khóa mua lại, trần ngành, lô giao dịch và thanh toán T+.
- MA10/MA3 trên chuỗi lấy mẫu là đại diện xu hướng, không đúng hoàn toàn MA200/MA50 ngày. Trọng số dùng biến động lợi suất thay ATR; không tái lập đầy đủ bộ lọc thanh khoản/ATR lịch sử. Quy tắc chặn lỗ -25% theo giá vốn cũng chưa được mô phỏng.
- Dùng rổ 112 mã hiện tại nên có thiên lệch chọn mẫu/sống sót. Không kiểm định trên một tập thời gian giữ riêng; mô hình tính tín hiệu và giá vào tại cùng điểm đóng cửa, chưa mô phỏng độ trễ khớp lệnh hoặc trượt giá.
- MDD chỉ đo tại các điểm cách khoảng bốn tuần; sụt giảm trong kỳ có thể sâu hơn. Giá đọc đúng như TradingView cung cấp; chưa xác minh đầy đủ chính sách điều chỉnh cổ tức/total return.
- Có tuần thiếu của BSI/PAN/VND/HHV trong giai đoạn khởi động 2020–2022: dùng giá quan sát gần nhất trước tuần thiếu, có ghi từng trường hợp trong `warmupFills`. Không có khoảng thiếu cần điền trong giai đoạn giao dịch mô phỏng.

## Kiểm tra dữ liệu và đầu ra

- Hai lượt quét đều đủ 113/113 chuỗi, không mã lỗi. Khung ngày có 300–1382 bar/mã; đủ tối thiểu 253 bar cho bộ lọc đang dùng. Tất cả bar ngày cuối cùng đều là 18/09/2026; kiểm tra thứ tự timestamp, dữ liệu số và giá dương đạt.
- TradingView báo `setVisibleRange: Not implemented`; số bar thực nhận được ghi lại, không giả định mọi mã có 560 bar. Bộ quy tắc quá nóng cũ cần 500 quan sát đã bị bỏ từ 11/09, không được dùng trong kết quả này.
- Kiểm thử hiện có: 12/12 Python và 3/3 Node đạt.
- `../../data/scan_20260918.json`: dữ liệu đầu vào mới; `../../data/candidates_20260918.json`: 11 candidate.
- `daily.json`, `weekly.json`: dữ liệu thô có timestamp; `validation.json`: kiểm tra dữ liệu; `backtest.json`: đủ kết quả bốn pha và đối chứng.
- `screener.txt`, `allocator_20260919.txt`, `allocator_preview_20260921.txt`: log chạy.
- `../../data/bao_cao_dau_tu_20260919.xlsx`: đầu ra Excel của allocator; `bao_cao_mo_phong_20260921_du_lieu_20260918.xlsx`: bản mô phỏng kỳ 21/09 (đã chuyển khỏi thư mục data để tránh nhầm là dữ liệu tương lai).

Không thay đổi tham số chiến lược, sổ giao dịch hoặc hồ sơ thẩm định. Các file chạy bổ sung đặt trong `exports/`; môi trường Python cục bộ `.venv` chỉ cài thư viện cần cho allocator.
