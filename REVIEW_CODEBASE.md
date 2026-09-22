# Review codebase — 19/09/2026

## Phạm vi

Rà soát trực tiếp snapshot hiện tại (thư mục gốc không có `.git`). Trọng tâm là
`lt_screener.py` → `lt_allocator.py`, hai bộ xếp hạng ngày/tuần,
`lt_backtest_scope.js` và bộ kiểm tra của `tradingview-mcp`.
Các script FF5, báo cáo và thư mục lịch sử chỉ được đọc chọn lọc; đây không phải
chứng nhận rằng mọi mô hình và mọi dòng mã của project đã được kiểm toán.

## Vấn đề đã sửa

| Mức độ | Vấn đề và bằng chứng | Thay đổi |
|---|---|---|
| Cao | Allocator giữ vị thế cũ nhưng vẫn mua theo danh mục mục tiêu độc lập. Test với NAV 100.000, tiền mặt 0 sinh mua 10.000 và số dư âm 10.008. | Kiểm tra lệnh sau bù trừ bằng tiền mặt thực, tiền bán ròng và phí mua; ưu tiên thứ hạng. |
| Cao | Trần ngành kiểm bằng số mã không bảo đảm trần giá trị: 3 mã ATR thấp có tổng tỷ trọng 45%, trong khi cấu hình cho phép 30%. | Áp trần tổng tỷ trọng ngành; phần vượt để tiền mặt. Khi ra lệnh, tính cả vị thế giữ lại và tác động làm tròn lô. |
| Cao | Vị thế giữ lại không tiêu thụ số ô của danh mục mục tiêu mới. | Chặn mở vị thế vượt `so_vi_the`; kiểm tra trần mã, ticket tối thiểu khi mở mới, và số dư sau phí. Không bán bắt buộc vị thế cũ chỉ để ép về trần. |
| Cao | Backtest B1/B2 chỉ lọc bảng đã chấm điểm trên toàn rổ. Trong fixture, thêm mã luôn trượt bộ lọc làm CAGR B1 đổi 15,78% → 15,49%. | Tính lại phân vị từng thành phần trên rổ đã lọc, dùng điểm này cho cả chọn mua và thứ hạng giữ. B1 đánh giá mã rơi khỏi lọc so với rổ hợp lệ cố định. |
| Cao | Drawdown lấy đỉnh bắt đầu từ NAV sau kỳ đầu. Fixture chỉ có một kỳ lỗ ~9,98% nhưng báo drawdown 0%. | Khởi tạo chuỗi NAV bằng 1 trước kỳ nắm giữ đầu tiên. |
| Vừa | Giá trị bằng nhau nhận phân vị khác nhau theo thứ tự JSON; có thể đổi điểm và quyết định thoát. | Dùng phân vị trung bình cho giá trị bằng nhau; điểm tổng bằng nhau có cùng thứ hạng thoát, mã cổ phiếu chỉ phân xử thứ tự hiển thị/chọn trước. Áp dụng tương ứng cho backtest B. |
| Vừa | Bộ lọc trong `build_rows` đọc cờ cấu hình, trong `buy_checklist` bỏ qua cờ đó. | Gom vào `hard_filter_checks`, dùng chung điều kiện và lý do loại. |
| Vừa | Nhật ký gia hạn và tên file báo cáo dùng ngày thật trong khi lệnh dùng `NGAY_CHAY`. | Dùng `HOM_NAY` nhất quán trong allocator. |
| Vừa | CLI TradingView gọi `process.exit()` ngay sau tác vụ mạng; trên Node 24/Windows hai test biên dịch sập với `UV_HANDLE_CLOSING`. | Đặt `process.exitCode`, trả về khỏi nhánh xử lý và đóng CDP trong `finally`; để runtime hoàn tất ghi output/thu hồi tài nguyên. Hai test lỗi đã qua sau sửa. |
| Vừa | Test audit dùng URL `.pathname` làm đường dẫn Windows, tạo `C:\C:\New%20folder\...`. | Chuyển bằng `fileURLToPath`. |
| Bảo trì | Hàm phân vị ngày/tuần trùng lặp; import screener còn tự đổi encoding stdout của chương trình gọi. | Gom hàm phân vị vào `ranking.py`; chỉ cấu hình stdout tại entry point CLI. |

Trần giá trị lệnh mua dùng NAV trước giao dịch, nhất quán với mục tiêu hiện tại.
Phần giảm lệnh được in riêng. Lệnh bổ sung lô lẻ hiện có vẫn được giữ nếu đủ
ngân sách; khi giảm khối lượng vì giới hạn, làm tròn xuống lô chuẩn.
Heuristic giới hạn số mã/ngành ở bước chọn ban đầu vẫn giữ, nhưng không còn
được dùng thay cho kiểm tra trần giá trị.

## Kiểm chứng

- `python -m unittest discover -s tests -v`: **12/12** qua.
- `node --test tests/backtest_scope.test.cjs`: **3/3** qua.
- Trong `tradingview-mcp`, `npm.cmd run test:unit`: **159/159** qua. Bộ này
  thực tế có test gọi máy chủ biên dịch TradingView, nên không hoàn toàn offline.
- `npm.cmd run lint`: exit 0; còn **4 warning có sẵn** về biến/import không dùng
  trong `src/core/data.js`, `src/core/pane.js`, `src/tools/watchlist.js`.
- Smoke test đọc `scan_20260915.json`, qua screener được 10 mã, loại 102 mã,
  chạy allocator và tạo/đọc lại đủ 4 sheet Excel trong thư mục tạm: qua.
- Không ghi đè các bản quét, ứng viên, sổ giao dịch hoặc báo cáo lịch sử.
  Không gửi lệnh giao dịch. Chưa kiểm thử E2E với TradingView Desktop đang mở.

Python không có trong PATH của phiên này; kiểm tra dùng runtime có sẵn tại
`C:/Users/Thinkpad/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`.

## Giới hạn còn cần xử lý

1. **Các số backtest đã công bố cần chạy lại.** Sửa phạm vi xếp hạng, xử lý đồng
   điểm và drawdown làm thay đổi kết quả. Test hiện xác minh tính đúng của logic
   bằng dữ liệu tổng hợp; chưa tái tạo toàn bộ bộ giá lịch sử `window.__W` và các
   pha lưới để thay số trong tài liệu. File backtest cũ dành đối chiếu không sửa.
2. **Mã đang giữ rơi khỏi candidates mất giá cập nhật.** Allocator còn dùng giá
   vốn làm giá dự phòng; không thể xem NAV đó là mark-to-market đầy đủ hoặc kiểm
   chứng chặn lỗ -25%. Cần nguồn giá đầy đủ, đồng ngày cho mọi vị thế, tách khỏi
   danh sách được phép mua. Cảnh báo rà soát tay hiện có vẫn được giữ.
3. **Bù trừ mua/bán là chính sách hiện có, không phải chứng minh quy tắc thoát
   được thi hành.** Một mã có tín hiệu bán có thể lại được chọn mua và bù trừ.
   Comment hiện tại ghi rõ đây là quyết định để khớp harness; lần sửa này giữ
   chính sách đó. Không nên diễn giải output thành “đã thoát mọi mã vi phạm”.
4. **FF5 còn rủi ro nhìn trước dữ liệu.** `dung_nhan_to` ghép SLCP báo cáo năm y
   vào các tháng cùng năm y; `_tssl` dùng phân vị toàn mẫu để winsorize. Cần dữ
   liệu theo thời điểm công bố trước khi coi kết quả là backtest point-in-time.
   Ngoài ra `_gan_nhom` hiện đưa giá trị thiếu vào nhóm giữa, cần chính sách loại
   dữ liệu và fixture nhân tố riêng. Các vấn đề này chưa sửa trong đợt này.

## Chạy lại

```powershell
python -m unittest discover -s tests -v
node --test tests/backtest_scope.test.cjs
```

Trong thư mục `tradingview-mcp`:

```powershell
npm.cmd run lint
npm.cmd run test:unit
```
