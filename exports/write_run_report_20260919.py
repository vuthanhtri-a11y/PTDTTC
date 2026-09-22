import json
from pathlib import Path
from statistics import mean

root = Path('exports/run_20260919')
candidates = json.loads(Path('data/candidates_20260918.json').read_text(encoding='utf-8'))
backtest = json.loads((root / 'backtest.json').read_text(encoding='utf-8'))
validation = json.loads((root / 'validation.json').read_text(encoding='utf-8'))
status = {'dat': 'Đạt', 'loai': 'Phủ quyết', 'cho': 'Chờ', 'chua': 'Chưa đánh giá'}
lines = [
    '# Kết quả quét TradingView và chạy chiến lược Quỹ — 19/09/2026', '',
    'Dữ liệu giá: đóng cửa **18/09/2026**. Phạm vi: **112 cổ phiếu HOSE trong rổ cấu hình của Quỹ + VNINDEX**, không phải toàn bộ cổ phiếu niêm yết Việt Nam. Đã đọc trực tiếp TradingView Desktop qua cầu nối có sẵn trong dự án.', '',
    'Kết quả: **11/112 mã qua bộ lọc**. Top kỹ thuật: **VIC, STB, MSB, VHM, BSR**. Theo hồ sơ thẩm định hiện lưu, chỉ **BSR và DHC** qua đủ bốn bước mua. DHC đồng thời vi phạm quy tắc giữ top 40%; cần đọc kết quả allocator cùng lịch rà soát, không suy diễn nhãn `buy_ready` thành lệnh mua ngay.', '',
    '## Xếp hạng candidate', '',
    'Điểm = 40% phân vị RS12 tháng bỏ tháng gần nhất + 30% RS6 tháng + 20% RS3 tháng + 10% chất lượng xu hướng; phân vị tính trong 11 mã đã qua lọc. Giá tính bằng đồng; RS12 là chênh lệch lợi suất với VNINDEX, đơn vị điểm phần trăm.', '',
    '| Hạng | Mã | Giá | Điểm | RS12 bỏ 1T | ATR | GTGD TB20 (tỷ/phiên) | B3 | B4 | Ngày hồ sơ |',
    '|---:|---|---:|---:|---:|---:|---:|---|---|---|',
]
for r in candidates:
    lines.append(f"| {r['thu']} | {r['ma']} | {r['gia']:,.0f} | {r['diem']:.2f} | {r['rs_252_skip21']*100:+.1f} | {r['atr']*100:.2f}% | {r['tov']/1e9:.1f} | {status[r['buoc3_tham_dinh']]} | {status[r['buoc4_dinh_gia']]} | {r['tham_dinh_ngay'] or 'Chưa có'} |")
lines += ['',
    'So với bản 15/09: HCM mới vào rổ đạt chuẩn; không mã nào rời rổ. STB lên hạng 2, MSB lên hạng 3; VHM xuống hạng 4 và DHC xuống hạng 9. DHC/HDB cùng điểm chính xác nên cùng thứ hạng tương đối 80%, dù thứ tự hiển thị là 9/10.', '',
    '**Diễn giải theo Quỹ:** VIC/STB/VHM bị phủ quyết ở B3. MSB/LPB/GMD chờ định giá; HCM chưa xong B4; BAF/HDB chưa thẩm định. BSR là mã duy nhất vừa qua bốn bước mua vừa còn trong top 40% giữ vị thế. Hồ sơ cơ bản/định giá được đọc từ `data/tham_dinh.json`, chưa được tái thẩm định bằng thông tin mới trong lần chạy này.', '',
    '## Chạy allocator và mô phỏng kỳ rà soát 21/09', '',
    '- Đã chạy screener, allocator ngày 19/09 và mô phỏng allocator ngày 21/09 trên cùng giá đóng cửa 18/09. Đây là đầu ra mô hình, không có lệnh nào được gửi tới công ty chứng khoán.',
    '- DM1 thiếu dữ liệu vốn/vị thế trong cấu hình, nên allocator bỏ qua phân bổ.',
    '- DM2: NAV **60.640.363 đồng**, cổ phiếu **24.716.000 đồng (40,8%)**, tiền mặt **35.924.363 đồng (59,2%)**; đang có MSB 840, BSR 100, VHM 50, DHC 200 cổ phiếu theo sổ cấu hình.',
    '- Mô phỏng 21/09: **không có lệnh ròng**. Mua thêm 100 BSR bị khóa bởi gia hạn quy tắc 5 đến 30/09. DHC bị tín hiệu bán do hạng 80% nhưng allocator bù trừ với mua lại đúng 200 cổ phiếu, nên vị thế không đổi. Đây là hành vi code hiện tại; không đồng nghĩa DHC thỏa mọi quy tắc giữ.',
    '- MSB/VHM chưa có xác nhận `luan_diem_con_nguyen`; hồ sơ VHM phủ quyết mua mới nhưng chưa đánh dấu luận điểm gãy để kích hoạt quy tắc bán số 4. Trạng thái thiếu rà soát được giữ nguyên, không tự suy diễn thay Quỹ.',
    '- Ngưỡng định giá/khóa mua lại và lịch rà soát có thể làm một mã mạnh về kỹ thuật chưa đủ điều kiện giao dịch.', '',
    '## Backtest phần kỹ thuật', '',
    'Chạy `lt_backtest_scope.js` với lịch sử tuần mới lấy, giữ 300 quan sát VNINDEX gần nhất, lấy mẫu cách bốn quan sát tuần và dịch điểm cuối lần lượt 0/1/2/3 tuần. Mỗi pha có 75 điểm, dùng 22 điểm khởi động và 52 kỳ nắm giữ. Căn ngày theo timestamp, không căn lệch bằng độ dài chuỗi.', '',
    'B1 xếp hạng trong rổ qua lọc và chèn thứ hạng cho mã đang giữ rơi khỏi rổ; B2 bán khi mã đang giữ rời rổ. B1 gần cách mô tả chiến lược hiện tại hơn, nhưng allocator vẫn cần rà soát tay với mã rời rổ. Cấu hình backtest: 10 ô, trần mã 15%, giữ top 40%, biên 3%, phí vòng quay 0,4%.', '',
    '**CAGR dưới đây đã quy đổi theo thời gian lịch thực tế**. Engine gốc coi một kỳ bốn tuần như một tháng và dùng 12 kỳ/năm; số gốc được giữ trong JSON, số quy đổi nằm ở `cagr_calendar` và có sai số làm tròn nhỏ. Ngày cuối bảng là timestamp của bar tuần, không nhất thiết là ngày thứ Sáu đóng cửa.', '',
    '| Pha | Mốc đầu | Bar tuần cuối | CAGR B1 | CAGR B2 | CAGR VNINDEX | MDD B1 | t alpha B1 |',
    '|---:|---|---|---:|---:|---:|---:|---:|',
]
for p in backtest['phases']:
    b1,b2,idx = (p['results'][key] for key in ('CL_B1','CL_B2','VNINDEX'))
    lines.append(f"| {p['phase']} | {p['start']} | {p['end_week']} | {b1['cagr_calendar']:.2%} | {b2['cagr_calendar']:.2%} | {idx['cagr_calendar']:.2%} | {b1['mdd']:.2%} | {b1['t']:.2f} |")
avg = lambda key: mean(p['results'][key]['cagr_calendar'] for p in backtest['phases'])
lines += ['',
    f"Trung bình bốn pha: **B1 {avg('CL_B1'):.2%}/năm**, B2 {avg('CL_B2'):.2%}/năm, VNINDEX {avg('VNINDEX'):.2%}/năm. Tái cân bằng toàn bộ mỗi kỳ: {avg('tai_can_bang_moi_thang'):.2%}/năm; đối chứng bốc thăm một chuỗi hạt giống: {avg('boc_tham_10'):.2%}/năm. Bình quân pha là kiểm tra độ nhạy, không phải lợi suất một danh mục có thể giao dịch hay bốn mẫu độc lập.", '',
    '**Kết luận:** alpha chưa có bằng chứng thống kê thuyết phục (t của B1 chỉ 0,15–0,48); kết quả còn nhạy với điểm lấy mẫu. Không dùng số cũ 13,89%/năm như kết quả của chiến lược hiện tại.', '',
    '### Giới hạn của phép đo', '',
    '- Đây là backtest xấp xỉ phần kỹ thuật, không phải toàn bộ chiến lược Quỹ. Chưa có lịch sử thẩm định/định giá theo thời điểm, quy tắc bán tùy nghi, lịch rà soát bổ sung, khóa mua lại, trần ngành, lô giao dịch và thanh toán T+.',
    '- MA10/MA3 trên chuỗi lấy mẫu là đại diện xu hướng, không đúng hoàn toàn MA200/MA50 ngày. Trọng số dùng biến động lợi suất thay ATR; không tái lập đầy đủ bộ lọc thanh khoản/ATR lịch sử. Quy tắc chặn lỗ -25% theo giá vốn cũng chưa được mô phỏng.',
    '- Dùng rổ 112 mã hiện tại nên có thiên lệch chọn mẫu/sống sót. Không kiểm định trên một tập thời gian giữ riêng; mô hình tính tín hiệu và giá vào tại cùng điểm đóng cửa, chưa mô phỏng độ trễ khớp lệnh hoặc trượt giá.',
    '- MDD chỉ đo tại các điểm cách khoảng bốn tuần; sụt giảm trong kỳ có thể sâu hơn. Giá đọc đúng như TradingView cung cấp; chưa xác minh đầy đủ chính sách điều chỉnh cổ tức/total return.',
    '- Có tuần thiếu của BSI/PAN/VND/HHV trong giai đoạn khởi động 2020–2022: dùng giá quan sát gần nhất trước tuần thiếu, có ghi từng trường hợp trong `warmupFills`. Không có khoảng thiếu cần điền trong giai đoạn giao dịch mô phỏng.', '',
    '## Kiểm tra dữ liệu và đầu ra', '',
    f"- Hai lượt quét đều đủ 113/113 chuỗi, không mã lỗi. Khung ngày có {validation['bars_min']}–{validation['bars_max']} bar/mã; đủ tối thiểu 253 bar cho bộ lọc đang dùng. Tất cả bar ngày cuối cùng đều là 18/09/2026; kiểm tra thứ tự timestamp, dữ liệu số và giá dương đạt.",
    '- TradingView báo `setVisibleRange: Not implemented`; số bar thực nhận được ghi lại, không giả định mọi mã có 560 bar. Bộ quy tắc quá nóng cũ cần 500 quan sát đã bị bỏ từ 11/09, không được dùng trong kết quả này.',
    '- Kiểm thử hiện có: 12/12 Python và 3/3 Node đạt.',
    '- `../../data/scan_20260918.json`: dữ liệu đầu vào mới; `../../data/candidates_20260918.json`: 11 candidate.',
    '- `daily.json`, `weekly.json`: dữ liệu thô có timestamp; `validation.json`: kiểm tra dữ liệu; `backtest.json`: đủ kết quả bốn pha và đối chứng.',
    '- `screener.txt`, `allocator_20260919.txt`, `allocator_preview_20260921.txt`: log chạy.',
    '- `../../data/bao_cao_dau_tu_20260919.xlsx`: đầu ra Excel của allocator; `bao_cao_mo_phong_20260921_du_lieu_20260918.xlsx`: bản mô phỏng kỳ 21/09 (đã chuyển khỏi thư mục data để tránh nhầm là dữ liệu tương lai).', '',
    'Không thay đổi tham số chiến lược, sổ giao dịch hoặc hồ sơ thẩm định. Các file chạy bổ sung đặt trong `exports/`; môi trường Python cục bộ `.venv` chỉ cài thư viện cần cho allocator.',
]
(root / 'BAO_CAO.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
print('Saved', root / 'BAO_CAO.md')
