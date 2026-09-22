# Báo cáo nhập thay đổi PTDTTC-main — 22/09/2026

Gửi @vuthanhtri-a11y.

Đã nhập mã nguồn, dữ liệu và báo cáo từ `PTDTTC-main/PTDTTC-main` vào repo
`vuthanhtri-a11y/PTDTTC`, đối chiếu với commit gốc
`f6535a6cb7fa171e31447c26998971be7c02da21`.

## Phạm vi và cách nhập

- Nguồn là snapshot không có thư mục `.git`; nhập theo nội dung file, không giả lập lịch sử commit của nguồn.
- **7 file hiện có được sửa, 1.915 file mới được nhập.** Đã so sánh byte và SHA-256 với nguồn cho toàn bộ 1.922 file này.
- Trong số file mới, 1.648 file thuộc `tradingview-mcp`, gồm mã nguồn, kiểm thử, dữ liệu phân tích và ảnh báo cáo. Thay gitlink cũ `0ac960ad548597d0d1e5fb2bf7bd9a7a50faa87b` bằng các file thực vì repo đích chỉ có liên kết, không có `.gitmodules` hoặc nội dung module.
- Thêm báo cáo này, `SYNC_MANIFEST_20260922.json` (danh sách và SHA-256 từng file), và `.gitignore` để bỏ qua môi trường, thư viện cài đặt, thông tin đăng nhập và cache chạy chương trình.
- Giữ nguyên các file đích ngoài phạm vi nhập; không xóa dữ liệu vì thiếu ở nguồn. Các khác biệt chỉ do CRLF/LF được bỏ qua.
- Không nhập `.git`, `.venv`, `.uv-cache`, `node_modules`, `__pycache__`, log, cache graph, `.env`, `.agents`, `.claude`, `.codex`, `AGENTS.md`, hoặc các tài liệu chỉ dẫn agent/skill. Đây là dữ liệu môi trường hoặc chỉ dẫn riêng của phiên; quy định onboarding yêu cầu không ghi thêm tài liệu skill/prompt xuống đĩa. Các file loại trừ không được tính trong 1.922 file trên.
- Gitlink `PTDTTC` lồng sẵn trong repo được giữ nguyên; nguồn tại đường dẫn đó cũng rỗng.

## Thay đổi chính

| Thành phần | Thay đổi được nhập |
|---|---|
| `CHIEN_LUOC_DAI_HAN.md` | Bổ sung mục 12: thiết kế, kiểm định, kết quả bác bỏ và giới hạn dữ liệu của CANSLIM ngày 22/09. |
| `canslim.py`, `canslim_data.py`, `canslim_backtest.py` | Thêm bộ lấy dữ liệu, chấm điểm theo ngày hiệu lực BCTC, backtest và kiểm định; đi kèm 225 file dữ liệu CANSLIM. |
| `lt_config.py` | Bổ sung ngưỡng CANSLIM; giữ đúng nguồn: `CANSLIM_CHAN_MUA = False`, `CANSLIM_KET_QUA = "bac_bo"`. |
| `lt_screener.py`, `data/tham_dinh.json` | Tích hợp hồ sơ CANSLIM, cờ dòng tiền V3, phân biệt phần máy chấm và thẩm định của người; thống nhất điều kiện lọc/checklist mua. CANSLIM hiện không chặn mua. |
| `lt_allocator.py` | Giới hạn mua theo tiền thực và phí, trần giá trị mã/ngành, số vị thế còn trống và lô giao dịch; dùng ngày mô phỏng nhất quán. |
| `ranking.py`, `weekly_rank.py` | Dùng chung phân vị, xử lý đồng điểm ổn định giữa các lần sắp xếp dữ liệu. |
| `lt_backtest_scope.js` | Chấm lại điểm trong rổ đã lọc; xử lý đồng điểm và tính drawdown từ NAV đầu kỳ. |
| `tradingview-mcp` | Nhập đầy đủ mã nguồn bridge, CLI, kiểm thử và dữ liệu phân tích; gồm bản sửa thoát CLI Node/Windows và đường dẫn test Windows được mô tả trong `REVIEW_CODEBASE.md`. |
| `data`, `exports` | Nhập các bản quét, candidates, phiếu thẩm định, kết quả kiểm định, báo cáo và script mới ngày 18–22/09, cùng hồ sơ phân tích TradingView ngày 19/09. |

Chi tiết các lỗi sửa trong đợt rà soát trước nằm ở `REVIEW_CODEBASE.md`. Báo cáo này
mô tả nội dung được nhập; không tuyên bố đã kiểm toán độc lập toàn bộ mô hình đầu tư.

## Kiểm chứng tại repo đích

| Kiểm tra | Kết quả |
|---|---|
| Đối chiếu file nguồn/đích và SHA-256 | 1.922/1.922 khớp |
| `python -m unittest discover -s tests -v` | 32/32 qua |
| `node --test tests/backtest_scope.test.cjs` | 3/3 qua |
| Trong `tradingview-mcp`: `npm.cmd run test:unit` | 159/159 qua, gồm test gọi dịch vụ biên dịch Pine |
| Trong `tradingview-mcp`: `npm.cmd run lint` | Exit 0; 0 lỗi, 4 cảnh báo biến/import chưa dùng có sẵn |

Python dùng runtime có sẵn trong `.venv` của thư mục nguồn (3.14.7); Node 24.19.0.
Thư viện TradingView được cài theo lockfile bằng `npm ci --ignore-scripts`.
Không chạy E2E với TradingView Desktop và không chạy lại toàn bộ backtest lịch sử
trong lần đồng bộ này. Các số liệu lịch sử được nhập nguyên trạng từ nguồn.

Các giới hạn đã được ghi trong bản nguồn vẫn còn: giá dự phòng cho mã đang giữ
nhưng rơi khỏi candidates, rủi ro dữ liệu nhìn trước trong FF5, và giới hạn cửa sổ
dữ liệu CANSLIM. Bốn cảnh báo lint nằm trong `src/core/data.js`, `src/core/pane.js`
và `src/tools/watchlist.js` của TradingView.
