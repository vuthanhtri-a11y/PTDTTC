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
- [ ] Cổ phiếu rơi khỏi **top 40% theo THỨ HẠNG VỊ TRÍ** trong rổ đã qua bộ lọc
- [ ] Luận điểm doanh nghiệp đã gãy (Bước 3 đổi kết luận) — nhập tay ở `data/tham_dinh.json`
- [ ] Chặn cứng −25% so với giá vốn — ngoại lệ duy nhất giữa hai kỳ rà soát

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

Tất cả tính bằng **phân vị trong rổ ĐÃ QUA BỘ LỌC CỨNG** (không phải toàn rổ 112 mã), không dùng giá trị tuyệt đối — theo đúng `Triet_ly_dau_tu_FF5.docx`, Bước 2. Chất lượng xu hướng = R² của log(giá) theo thời gian trên ~6 tháng — momentum "mượt" bền hơn momentum "giật cục".

Ngoài giá trị điểm, mỗi mã còn có **thứ hạng vị trí** `thu_hang = (i−1)/(n−1)` sau khi sắp xếp giảm dần theo điểm, với `i` là vị trí và `n` là số mã qua lọc. Luật thoát số 3 hỏi về **thứ hạng**, không về giá trị điểm — hai thứ này khác nhau và việc lẫn lộn chúng đã là một lỗi thật (xem mục 7).

⚠️ **R² và RS 6 tháng là thành phần XẾP HẠNG ở tầng này, không phải điều kiện lọc ở Tầng 1.** Bản `lt_screener.py` trước 25/08/2026 đưa `trend_r2 ≥ 0,20` và `RS6T ≥ 0` vào bộ lọc cứng — biến một tiêu chí "để xếp trước sau" thành một tiêu chí "được phép hay không". Đã gỡ bỏ.

**Không còn dùng `p` (xác suất thắng) hay `ER`.** Kiểm định hoán vị trước đây cho p-value 0,689: `p` không có sức phân biệt, và softmax khuếch đại nó theo hàm mũ nên khuếch đại nhiễu.

### Tầng 3 — Phân bổ (mua bao nhiêu)

- Tỷ trọng ∝ **1 / ATR** (rủi ro ngang nhau giữa các vị thế), không theo điểm xếp hạng.
- Trần 15%/mã (DM1), 20%/mã (DM2); trần ngành 30% (DM1), 40% (DM2).
- ~~Trần trùng lặp: một mã ≤ 10% **tổng tài sản hai tài khoản**, áp sau khi làm tròn lô.~~ **ĐÃ BỎ 02/09/2026** — xem mục 9.
- **Tiền mặt sinh ra tự động**: mỗi "ô" không tìm được mã đạt chuẩn thì ô đó nằm tiền. Không có bất kỳ quy tắc canh chỉ số nào — đã kiểm chứng 17/08 rằng bộ lọc VNINDEX theo MA50 **không** dự báo được hướng chỉ số.

Số ô: **DM1 = 10, DM2 = 8** (đo được, xem mục 4).

### Luật thoát

Rà soát **đầu mỗi tháng**. Giữ tiếp khi còn đủ **cả bốn** (Bảng CL.4 của `Triet_ly_dau_tu_FF5.docx`):

1. Giá đóng cửa > 0,97 × MA200 (đệm 3% chống nhiễu)
2. RS 12 tháng so với VNINDEX > −5%
3. **Thứ hạng vị trí ≤ 40%** trong rổ đã qua bộ lọc — tức `thu_hang ≤ 0,40`. Đây là quy tắc **thay thế**, không phải quy tắc cắt lỗ
4. **Luận điểm doanh nghiệp còn nguyên vẹn như khi mua** — quy tắc duy nhất không đọc dữ liệu giá; kết luận do người nhập vào `data/tham_dinh.json`, trường `luan_diem_con_nguyen`

Hỏng bất kỳ điều nào → bán toàn bộ vị thế, tiền chuyển sang mã đứng đầu danh sách chờ; danh sách chờ rỗng thì phần vốn đó nằm tiền. Lệch tỷ trọng < 3% NAV thì **không** điều chỉnh (biên không giao dịch). Chặn cứng một chiều: −25% so với giá vốn — ngoại lệ duy nhất được kích hoạt giữa hai kỳ rà soát, và là quy tắc duy nhất trong hệ thống tham chiếu tới giá vốn.

**Lệnh bán CHỈ đến từ bốn quy tắc trên.** Một mã không lọt vào danh mục mục tiêu nhưng vẫn trả lời "có" cho cả bốn câu thì **giữ nguyên** — không bán. Bản `lt_allocator.py` trước 25/08/2026 tính chênh lệch so với danh mục mục tiêu rồi bán phần dư, tức tái cơ cấu toàn bộ mỗi kỳ; backtest cho thấy tái cơ cấu toàn bộ hằng tháng chỉ đạt 6,95%/năm so với 13,89% của bán-theo-quy-tắc-thoát.

### Quy tắc thứ năm — bán theo cảm quan thị trường của quỹ (đổi ngày 11/09/2026)

**Quyết định của user ngày 11/09/2026:** quy tắc 5 không còn là "bán bớt khi giá quá nóng" mà là **bán theo cảm quan thị trường của quỹ**, dùng để tăng tính chủ động ứng phó với biến động thị trường. Đây là quy tắc **tuỳ nghi**: người quyết, hệ thống không sinh tín hiệu, không có backtest nào đứng sau.

| Tham số (user chốt 11/09, trước khi có lệnh nào theo luật mới) | Giá trị |
|---|---|
| Bán tối đa mỗi lần | **50% vị thế** đang giữ — không đóng hẳn. Thoát toàn phần vẫn chỉ do bốn quy tắc đã kiểm chứng |
| Hiệu lực | **Tới kỳ soát kế tiếp** — kỳ soát lấy lại quyền, allocator được mua lại phần đã bán nếu mã còn qua bốn quy tắc |
| Gia hạn | Quỹ ghi `gia_han_den` + `ngay_ghi_gia_han` **trước ngày soát** → allocator không mua lại phần đã bán tới hết ngày gia hạn. Ghi trong/sau ngày soát = không hiệu lực |
| Sổ lệnh | `LENH_QUY_TAC_5` trong `lt_config.py`, ghi **trước khi đặt lệnh**, bắt buộc có trường `cam_quan` (lý do bằng lời) |

`lt_allocator.py` in sổ này mỗi lần chạy, kiểm tra trần 50% (`[VUOT TRAN 50%]`), trường thiếu (`[THIEU: ...]`) và tính hợp lệ của gia hạn. Đã thử 4 ca giả lập ngày 11/09: gia hạn hợp lệ khoá đúng phần mua lại, bán vượt trần bị gắn cờ, gia hạn ghi đúng ngày chạy bị bác, thiếu `cam_quan` bị gắn cờ.

**Không áp dụng hồi tố:** lệnh bán 50 VHM ngày 07/09 vẫn là **lệnh ngoài luật #1**, vì luật mới chưa tồn tại lúc đó.

**Lý do bỏ bản cũ:** bản "giá quá nóng" chưa từng chạy được trên dữ liệu thật. Dấu hiệu (a) cần 500 quan sát, nhưng TradingView Desktop 3.4.1 báo `setVisibleRange: Not implemented` nên mỗi mã chỉ có 300 bar (251 quan sát). Code cũ: `data/lt_config_backup_20260911.py`, `data/lt_screener_backup_20260911.py`. Các trường `dma50`/`vol60`/`c60` vẫn nằm trong schema quét (chỉ được nối thêm vào cuối) nhưng không còn được đọc.

⚠️ **Điều báo cáo cuối kỳ phải nói rõ:** từ 11/09 hệ thống có một đường thoát không có bằng chứng thống kê. Bằng chứng gần nhất có liên quan — 56.496 lệnh mô phỏng cho alpha âm với chốt lãi tại mục tiêu, và lọc theo chỉ số không dự báo được hướng đi — đều nghiêng về phía bất lợi cho bán tuỳ nghi. Sổ `LENH_QUY_TAC_5` tồn tại để đo xem cảm quan của quỹ thực tế đúng hay sai bao nhiêu lần.

#### (lịch sử, 17/08–10/09/2026) Bản cũ — bán bớt khi giá quá nóng

Bốn quy tắc trên bán vì cổ phiếu yếu đi; quy tắc thứ năm bán vì lý do ngược lại. Chỉ hành động khi **cả ba** dấu hiệu cùng xuất hiện: (a) khoảng cách giá–MA trung hạn giãn tới vùng rộng nhất mà chính mã đó từng ghi nhận trong hai năm; (b) định giá vượt vùng cao nhất vài năm gần nhất mà năng lực sinh lời không đổi tương ứng; (c) nhịp tăng kèm khối lượng đột biến rồi cạn dần trong khi giá vẫn lên.

Khi đủ ba, **giảm tỷ trọng xuống một nửa** — không được đóng hoàn toàn vị thế. Ranh giới này là cố ý: quy tắc thứ năm chưa được backtest như phần còn lại của hệ thống, nên không được phép vô hiệu hoá những quy tắc đã kiểm chứng.

🔧 **Trạng thái hiện thực — CẬP NHẬT 07/09/2026: ĐÃ ĐO ĐƯỢC (a) và (c); (b) vẫn do người.**

> Bản trước ngày này: "CHƯA CHẠY ĐƯỢC" — (a) thiếu lịch sử, (c) thiếu chuỗi khối lượng.
>
> 🔴 **Đính chính cùng ngày:** việc bán 50 VHM ngày 07/09/2026 **không phải** lần vận dụng quy tắc 5. Tên chính thức của nó là **"Lệnh chốt lãi một phần theo yêu cầu người góp vốn"** — lệnh ngoài luật #1, ghi ở `LENH_NGOAI_LUAT` trong `lt_config.py`, không thuộc khung này. Trong tên cố ý **không có số hiệu quy tắc nào**: chỉ cần chữ "quy tắc 5" nằm trong tên là sáu tuần sau cả quỹ sẽ nhớ lại như thể hệ thống đã bảo làm. Phần bổ sung dưới đây vẫn giữ nguyên giá trị: để lần sau câu "giá quá nóng" là một **phép đo** chứ không phải một **nhãn dán**.

**Đã sửa gì**

| Dấu hiệu | Trước 07/09 | Nay |
|---|---|---|
| (a) giá–MA50 giãn tới vùng rộng nhất 2 năm | 300 bar ≈ 1,2 năm, không đủ | `lt_scan_tradingview.js` đặt visible range lui 1.200 ngày → **≥560 bar**; trường `dma50 = [khoảng cách, phân vị, số quan sát]` |
| (b) định giá vượt vùng cao nhất | thiếu | vẫn **người nhập** — trường `dinh_gia_qua_cao` trong `data/tham_dinh.json`. Cố ý không suy từ giá |
| (c) KL đột biến rồi cạn dần mà giá vẫn lên | thiếu | trường `vol60` + `c60` — 60 phiên khối lượng **và** giá đóng cửa |

Ngưỡng cụ thể nằm ở `QUA_NONG` trong `lt_config.py`: đỉnh KL đo bằng trung bình 5 phiên, phải ≥ 1,8× trung vị cửa sổ và nằm trong 2/3 đầu; "cạn" = KL hiện tại ≤ 0,75× đỉnh; "giá vẫn lên" = đóng cửa hôm nay > đóng cửa ngày đỉnh.

**Ba trạng thái, không phải hai.** Mỗi dấu hiệu trả về `CO` / `khong` / `?`. Dấu `?` = **không đo được** (thiếu lịch sử hoặc thiếu kết luận người) và **không được quy về "không quá nóng"** — nếu quy về thì một bản quét thiếu dữ liệu sẽ tự động trả lời một câu nó chưa từng hỏi. `lt_screener.py` in cảnh báo cho mọi mã còn dấu `?`.

**Đối chiếu độc lập với định giá.** Khi người kết luận "định giá quá cao" nhưng giá hiện tại vẫn **thấp hơn** `dinh_gia.co_so` đã ghi, screener in `[MAU THUAN]`. Đây chính là ca VHM ngày 07/09: bán 77,70 trong khi cơ sở định giá ghi 80,6 — thấp hơn giá trị hợp lý 3,6%.

⚠️ **Vẫn CHỈ BÁO CÁO, KHÔNG SINH LỆNH** (`QUA_NONG_TU_DONG_BAN = False`). Ngưỡng ở `QUA_NONG` **chưa từng được backtest** như bốn quy tắc kia; đo được không có nghĩa là đã kiểm chứng. Tỷ lệ bán vẫn khoá ở 0,50.

🔵 **Câu hỏi "có nên khoá không cho mua lại sau khi quy tắc 5 cắt nửa" — ĐÃ ĐÓNG, trả lời: KHÔNG.** Câu hỏi này mở ra khi tưởng lệnh 07/09 là quy tắc 5. Sau đính chính, nó không phải, nên không có gì để khoá. Thêm khoá lúc này sẽ là đổi luật phân bổ giữa cuộc thi để hợp thức hoá một lệnh ngoài luật — đúng loại sai lệch mà sổ đã ghi hai lần. Việc allocator đòi mua lại 50 VHM ở kỳ soát sau **không phải lỗ hổng**: đó là hệ thống nói rằng theo luật đã chốt, vị thế này lẽ ra vẫn giữ đủ. Nếu về sau quy tắc 5 thật sự kích hoạt (đủ cả ba dấu hiệu đo được) thì lúc đó mới xét lại — và phải xét **trước** khi nhìn bảng lệnh của kỳ đó.

📌 **Ban quét cũ vẫn đọc được:** `lt_screener.load()` bù `None` cho cột thiếu, nên `scan_*.json` từ 04/09 trở về trước chạy bình thường và mọi dấu hiệu quy tắc 5 hiện dấu `?`. Muốn quy tắc 5 chạy thật thì phải **quét lại bằng bản `lt_scan_tradingview.js` từ 07/09/2026** — cụ thể là bản quét cuối tháng 9 cho kỳ soát 01/10.

🧾 **Sai lệch schema đã sửa cùng dịp:** bản quét 04/09 trên thực tế ghi **12 trường** (thêm `r1`, `r5`) nhưng `lt_scan_tradingview.js` trên đĩa vẫn là bản 10 trường và `FIELDS` của screener cũng chỉ khai 10 — hai trường đó tồn tại trong dữ liệu mà không tồn tại trong code. Nay `FIELDS` khai đủ 15 và file `.js` sinh đủ 15.

### Bước 3 và Bước 4 — hai cửa do người quyết

`Triet_ly_dau_tu_FF5.docx` đặt hai bước sau bảng xếp hạng, và cả hai đều có **quyền phủ quyết**:

- **Bước 3 — thẩm định từ dưới lên:** doanh nghiệp → ngành → vĩ mô (Bảng CL.2). "Một mã đứng đầu bảng xếp hạng vẫn bị loại nếu không qua được lớp này."
- **Bước 4 — định giá và điểm mua:** giá đòi hỏi mọi giả định đều đúng → đưa vào danh sách chờ, không mua.

Kết luận nhập tay vào `data/tham_dinh.json`. **Thiếu kết luận = chưa được mua**, không phải mặc định đạt — nếu mặc định là đạt thì lớp phủ quyết không tồn tại.

**Tự kiểm tra bắt buộc:** nếu một kỳ rà soát mà lớp thẩm định không loại được mã nào, ghi nhận đó như một cảnh báo. Một lớp phủ quyết không bao giờ phủ quyết thì trên thực tế không tồn tại. `lt_screener.py` in cảnh báo này tự động.

⚠️ **Thang điểm `investment_score` (10 điểm) đã bị bỏ ngày 25/08/2026.** Nó cộng điểm cho "quality" và "valuation" bằng thanh khoản, MA50/MA200, R² và RS — toàn bộ là dữ liệu giá đeo nhãn cơ bản. Chính `Triet_ly_dau_tu_FF5.docx` gọi tên lỗi đó: quỹ sẽ "tự khen mình vì những thứ vốn chỉ là phơi nhiễm rủi ro, và đó là loại nhầm lẫn khó phát hiện nhất vì nó luôn nhầm theo hướng có lợi cho người đo".

---

## 3. Kết quả backtest — ⚠️ BẢN GHI LỊCH SỬ, ĐÃ BỊ THAY THẾ

> 🔴 **Toàn bộ mục 3 đo trên MỘT pha lưới lấy mẫu (neo 17/08/2026) và phạm vi xếp hạng cũ (toàn rổ). Ngày 26/08/2026 đo lại trên bốn pha lưới với phạm vi theo bản chốt: các con số bên dưới KHÔNG lặp lại, và bốn trong năm kết luận thiết kế bị đảo ngược. Xem mục 8. Giữ mục này để đối chiếu, KHÔNG trích dẫn.**

### (lịch sử) Kết quả backtest (52 tháng, 04/2022 → 08/2026, 112 mã HOSE)

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

### Lịch rà soát — ngoại lệ một lần cho DM2 (chốt 16/09/2026)

Nguyên tắc nền không đổi: **rà soát đầu mỗi tháng**, mua bán chỉ diễn ra sau một kỳ soát.

Ban tổ chức cuộc thi chia giải làm hai giai đoạn, **giai đoạn 2 bắt đầu 21/09/2026**. Đó là **mốc báo cáo**: không reset điểm (return tính liên tục 17/08 → ~17/10), không đổi luật đầu tư, không đổi vốn. Vì cuộc thi không bắt đầu vào đầu tháng nên lịch soát đầu tháng lệch pha với lịch cuộc thi — thêm **một kỳ soát tại 21/09** để danh mục nộp báo cáo giai đoạn 2 là danh mục đã được soát. **Kỳ 01/10 vẫn giữ.** Chỉ áp dụng cho **DM2**; DM1 giữ nguyên nhịp đầu tháng. Mốc này hết hiệu lực sau 17/10.

| Mốc | Việc |
|---|---|
| 21/09 (T2), sau đóng cửa | Quét TradingView → `lt_screener.py` → **bảng xếp hạng** |
| Đêm 21/09 | Làm phiếu Bước 3/4 → `data/tham_dinh.json`, **xong trước khi chạy allocator** |
| 22/09 (T3) | Đặt **lệnh bán** (không cần thẩm định). Lệnh **mua** ra khi phiếu đủ, hạn chót **25/09** |
| 01/10 | Kỳ soát đầu tháng, chạy bình thường |
| 01/11 | Kỳ soát tiếp theo; nhịp trở lại đầu tháng |

Thẩm định làm **sau** bảng xếp hạng nhưng **trước** bảng lệnh — đúng hàng rào đã chốt ở mục 11 bên dưới (*"phải xét trước khi nhìn bảng lệnh của kỳ đó"*). Quá hạn 25/09 thì phần mua đợi kỳ 01/10.

**Ba điều khoản kèm theo** (`LICH_SOAT`, `KHOA_WHIPSAW`, `BAO_LUU_TIN_HIEU` trong `lt_config.py`; cưỡng chế trong `lt_allocator.py`):

1. **Khoá chống whipsaw.** Mã bị bốn quy tắc thoát bán ở kỳ 21/09 **không được allocator mua lại ở kỳ 01/10**; khoá tới 01/11. Lý do: quy tắc 3 so thứ hạng vị trí trong rổ đã lọc (~12 mã) nên top 40% chỉ là 5 mã — ràng buộc chính và rất nhạy. Đã đo được: thêm **đúng 1 bar** làm r252 của VNINDEX tụt 4,3 điểm phần trăm, đẩy HCM khỏi bộ lọc và MSB khỏi top 40% **dù giá không đổi**. Soát lại sau 7 phiên là lấy mẫu lại đúng chỉ báo nhạy nhất. Phí **không** phải lý do: khứ hồi 0,26% trên một ô ~3,5tr chỉ ≈ 9.100đ (0,015% NAV).
2. **Điều khoản bảo lưu — luật mới không hồi tố.** Mọi **tín hiệu bán đã phát sinh trước 16/09/2026** giữ nguyên lịch thực thi cũ **01/10**. Mốc 21/09 chỉ áp cho tín hiệu **mới** sinh từ chính đợt quét 21/09. Không có điều khoản này thì việc thêm mốc tự động đẩy sớm một lệnh bán đã nằm chờ sẵn 7 phiên — tức đổi lịch để thay đổi số phận một quyết định có trước khi lịch đổi. Viết thành điều khoản **chung**, không miễn trừ theo mã: miễn trừ đích danh một mã là đúng thứ lớp phủ quyết sinh ra để chống. Mã đang được bảo lưu: **VHM** (phủ quyết Bước 3 ngày 13/09).
3. **Quy tắc 5.** 21/09 **là** "kỳ soát kế tiếp" — hệ thống lấy lại quyền mua lại phần đã bán theo cảm quan. Muốn giữ lâu hơn thì ghi `gia_han_den` + `ngay_ghi_gia_han` **trước** ngày soát, đúng cơ chế đã có.

**Vì sao mốc này không phải "đổi luật để hợp thức hoá một quyết định đã có sẵn"** — lỗi đã ghi hai lần trong sổ: mốc 21/09 **do BTC đặt**, không phải quỹ chọn, và được chốt ngày **16/09, trước khi nhìn bất kỳ bảng lệnh nào** của kỳ đó. Báo cáo cuối kỳ phải ghi lại đúng câu này. Đây là lần thứ ba luật đổi giữa cuộc thi (17/08 đổi khung, 11/09 đổi quy tắc 5, 16/09 thêm mốc soát); hai lần trước do quỹ chọn, lần này không.

**Hệ quả đã biết và chấp nhận:** báo cáo nộp 21/09 phản ánh danh mục **trước** khi soát (vì đặt lệnh 22/09); và kỳ 01/10 chỉ còn 11 phiên tới 17/10 nên lệnh **mua** ở kỳ đó gần như không kịp có tác dụng mà vẫn chịu phí.

**Đã thử 11 ca giả lập ngày 16/09** (nhận diện kỳ bổ sung cho đúng danh mục; bảo lưu giữ VHM ở 21/09 rồi hết hiệu lực ở 01/10; gia hạn quy tắc 5 chặn mua lại BSR ở 21/09 rồi mở ở 01/10; khoá whipsaw chặn ở 01/10 rồi mở ở 01/11) — 11/11 đạt. Chạy thử allocator với `NGAY_CHAY=2026-09-21` và `2026-10-01` cho kết quả đúng thiết kế.

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

---

## 7. Đồng bộ với `Triet_ly_dau_tu_FF5.docx` — sửa ngày 25/08/2026

Tài liệu triết lý đã chốt là bản có thẩm quyền về **phương pháp**; các con số ngưỡng vẫn lấy từ tài liệu này. Khi đối chiếu, phát hiện bốn chỗ code chạy khác tài liệu:

| # | Chỗ sai | Bản cũ | Bản đúng theo FF5 |
|---|---|---|---|
| 1 | Luật thoát số 3 | `lt_screener.py` so **giá trị điểm** `diem < 0,60` | So **thứ hạng vị trí** `thu_hang > 0,40` |
| 2 | Bộ lọc cứng | Thêm `trend_r2 ≥ 0,20` và `RS6T ≥ 0` làm điều kiện lọc | Đúng 5 điều kiện Bảng CL.1; R² và RS6T chỉ là thành phần xếp hạng |
| 3 | Bước 3 + 4 | `investment_score` suy "quality"/"valuation" từ dữ liệu giá | Người thẩm định, có quyền phủ quyết; thiếu kết luận = không được mua |
| 4 | Lệnh bán | `lt_allocator.py` bán phần chênh so với danh mục mục tiêu | Chỉ bán khi hỏng một trong bốn quy tắc thoát |

### Phạm vi tính phân vị — điểm phải nói rõ

Ngày 25/08 tôi từng đề xuất tính phân vị trên **toàn rổ 112 mã**, vì `lt_backtest_tradingview.js` (dòng 62–66, 92) — đoạn code sinh ra con số 13,89%/năm — làm đúng như vậy. Tài liệu FF5 đã chốt lại theo hướng khác: "phân vị trong rổ **đã qua bộ lọc**". Bản chốt thắng, và code đã sửa theo.

⚠️ **Hệ quả bắt buộc phải ghi nhận: con số 13,89%/năm và sụt giảm −21,3% hiện KHÔNG còn đo đúng hệ thống đang chạy.** Backtest xếp hạng trên toàn rổ; hệ thống chạy xếp hạng trong rổ đã lọc. Với ngưỡng 40%, hai cách cho kết quả rất khác nhau: toàn rổ 112 mã → top 40% là 45 mã, điều kiện thứ hạng gần như không bao giờ ràng buộc; rổ đã lọc 12 mã → top 40% chỉ là 5 mã, điều kiện này trở thành ràng buộc chính.

**Phải chạy lại `lt_backtest_tradingview.js` với phạm vi xếp hạng = rổ đã lọc, và đo lại cả bề mặt độ nhạy của ngưỡng 40%, trước khi trích dẫn bất kỳ con số hiệu năng nào trong báo cáo.** Cho tới lúc đó, mọi con số ở mục 3 phải được ghi kèm chú thích rằng chúng đo phiên bản cũ.

### Đối chiếu trên dữ liệu 25/08/2026

12 mã qua bộ lọc cứng. Top 40% theo thứ hạng vị trí = 5 mã đầu bảng (VIC, STB, VHM, MSB, LPB).

| Mã DM2 | Thứ hạng | `thu_hang` | Quy tắc 1 | Quy tắc 2 | Quy tắc 3 | Kết luận |
|---|---|---|---|---|---|---|
| STB | 2/12 | 0,09 | đạt | đạt | đạt | giữ |
| VHM | 3/12 | 0,18 | đạt | đạt | đạt | giữ |
| MSB | 4/12 | 0,27 | đạt | đạt | đạt | giữ |
| LPB | 5/12 | 0,36 | đạt | đạt | đạt | giữ |
| GMD | 8/12 | 0,64 | đạt | đạt | **hỏng** | **bán** |
| BSR | 10/12 | 0,82 | đạt | đạt | **hỏng** | **bán** |

Quy tắc 4 chưa rà soát được cho mã nào — `data/tham_dinh.json` còn rỗng. Phải điền trước kỳ soát 01/09/2026.

### File liên quan

- `data/tham_dinh.json` — kết luận Bước 3 + Bước 4 do người nhập; có hướng dẫn ngay trong file.
- `data/CHIEN_LUOC_DAI_HAN_backup_20260825.md`, `data/lt_config_backup_20260825.py` — bản trước khi sửa.

---

## 8. Đo lại backtest — 4 pha lưới, ngày 26/08/2026

Chạy `lt_backtest_scope.js` trên 300 bar tuần của 112 mã, lấy mẫu tháng theo **bốn pha lưới** (neo vào 24/08, 17/08, 10/08, 03/08). Kết quả đầy đủ: `data/backtest_pha_luoi_20260826.json`.

### Đối chứng: harness trung thực

Pha 1 (kết thúc 17/08/2026) tái tạo gần đúng bản chạy ngày 17/08:

| | Bản công bố 17/08 | Pha 1 chạy lại |
|---|---|---|
| CAGR | 13,89% | **14,07%** |
| Sụt giảm | −21,3% | −21,4% |
| Alpha tháng · t | +0,54% · 0,87 | +0,51% · 0,81 |

Sai lệch nhỏ đến từ một tuần dữ liệu thêm ở đuôi. Vậy code đo là đúng; vấn đề nằm ở chỗ khác.

### Kết quả bốn pha

| Pha (ngày cuối) | A — toàn rổ | B1 — rổ đã lọc | B2 — rổ đã lọc, rơi lọc là bán | Tắt quy tắc 3 | VNINDEX |
|---|---|---|---|---|---|
| 24/08 | 10,36% | 7,65% | 7,10% | 10,09% | 8,32% |
| 17/08 | 14,07% | 9,37% | 9,22% | 6,66% | 8,09% |
| 10/08 | 9,38% | 8,70% | 8,08% | 6,18% | 7,71% |
| 03/08 | 14,54% | 10,49% | 10,49% | 13,55% | 9,23% |
| **Trung bình** | **12,09%** | **9,05%** | 8,72% | 9,12% | **8,34%** |
| Sụt giảm TB | −23,2% | −29,5% | −29,8% | — | — |
| Vượt index (điểm %) | +3,75 | **+0,72** | +0,39 | +0,78 | — |

t-stat của alpha tháng: A từ 0,28 đến 0,81; B1 từ 0,04 đến 0,24. **Không pha nào, không phạm vi nào đạt ý nghĩa thống kê.**

### Bốn điều đọc được

1. **Con số 13,89% là một trong bốn lần rút thăm của pha lưới, và là lần cao thứ hai.** Trung bình bốn pha của cùng phương pháp A là 12,09%, biên độ 9,38–14,54%. Dịch lưới lấy mẫu đúng một tuần làm CAGR đổi tới 5,2 điểm phần trăm. Con số công bố không sai, nhưng nó chưa bao giờ là một ước lượng — nó là một quan sát.

2. **Phạm vi theo bản chốt (B1) vượt index trung bình +0,72 điểm phần trăm/năm, t từ 0,04 đến 0,24.** Không phân biệt được với 0. Đây là con số phải dùng cho báo cáo, không phải 13,89%.

3. **Phạm vi A tốt hơn B1 ở cả 4/4 pha, và vượt index ở cả 4/4 pha.** Nhưng bốn pha dùng chung phần lớn dữ liệu nên đây **không** phải bốn quan sát độc lập; dấu hiệu 4/4 yếu hơn vẻ ngoài của nó rất nhiều.

4. **Phát biểu vững nhất trong cả bộ số: thu hẹp rổ xếp hạng làm sụt giảm sâu hơn** — B1 tệ hơn A ở cả 4/4 pha, trung bình −29,5% so với −23,2%. Chênh lệch sụt giảm thường được ước lượng chính xác hơn chênh lệch lợi suất, nên đây là kết luận đáng tin nhất ở đây.

### Đính chính một kết luận sai

Chạy riêng pha 0 cho thấy tắt hẳn quy tắc thoát 3 tốt hơn (10,09% so với 7,65%). **Kết luận đó sai.** Chênh lệch theo từng pha là +2,44 / −2,71 / −2,52 / +3,06 điểm phần trăm, trung bình +0,07. Tác động của quy tắc 3 là nhiễu, không phải tín hiệu, và nó cũng là lựa chọn thiết kế kém ổn định nhất trong cả bảng (biên độ 6,18–13,55%). Giữ nguyên quy tắc 3 theo bản chốt.

### Việc phải làm với `lt_allocator.py`

Bản sửa 25/08 hiện thực **B2**: mã đang giữ mà rơi khỏi bộ lọc cứng thì bán ngay. Đó là một quy tắc thoát thứ năm không có trong Bảng CL.4 — tài liệu chỉ cho phép bán theo bốn câu hỏi. B1 vừa đúng văn bản hơn, vừa tốt hơn ở **cả 4/4 pha** (trung bình +0,33 điểm phần trăm). Đã đổi sang B1: mã rơi khỏi bộ lọc vẫn được chấm bằng bốn quy tắc, thứ hạng lấy bằng vị trí điểm của nó chen vào bảng xếp hạng của nhóm qua lọc.

### Ba tham số thiết kế: đo lại trên 4 pha, phạm vi bản chốt

**Số ô — kết luận cũ bị đảo ngược hoàn toàn.**

| Số ô | 5 | 6 | 8 | **10** | 12 | 15 |
|---|---|---|---|---|---|---|
| Bản cũ (1 pha, phạm vi A) | 8,6% | 10,5% | 13,1% | **13,9%** | 9,4% | 8,6% |
| **TB 4 pha, phạm vi B1** | **10,66%** | 10,50% | 9,08% | **9,05%** | 8,04% | 8,05% |

Bản cũ kết luận "8–10 ô là tốt nhất, quá ít ô thì phụ thuộc may rủi". Đo lại cho điều ngược lại: **5 ô tốt hơn 10 ô ở cả 4/4 pha.** Có thể có cơ chế thật đằng sau — với rổ đã lọc, top 40% chỉ khoảng 12 mã, nên N càng lớn thì càng nhiều vị thế nằm sát ngưỡng và bị quy tắc 3 xoay vòng. Nhưng hai phép đo cho hai kết luận ngược nhau thì điều đọc được chắc chắn nhất là: **số ô không đo được ở cỡ mẫu này.** Giữ 10 ô (DM1) và 8 ô (DM2) vì đó là con số đã chốt, không phải vì dữ liệu ủng hộ.

**Chu kỳ rà soát — kết luận cũ cũng bị đảo ngược.**

| | Hằng tháng | Hằng quý |
|---|---|---|
| Bản cũ (1 pha, phạm vi A) | 13,89% | 7,06% |
| **TB 4 pha, phạm vi B1** | **9,05%** | **11,67%** |
| Sụt giảm TB | −29,5% | **−24,1%** |
| Theo từng pha | 7,65 / 9,37 / 8,70 / 10,49 | 4,84 / 12,10 / 10,73 / 18,99 |

Hằng quý tốt hơn hằng tháng ở 3/4 pha và trung bình +2,6 điểm phần trăm, với sụt giảm nông hơn 5,3 điểm. **Phát biểu "tốc độ THOÁT quan trọng hơn tốc độ vào" không còn được dữ liệu ủng hộ.** Nhưng biên độ của nhánh hằng quý cực rộng (4,84–18,99%) nên đây cũng không phải bằng chứng cho chiều ngược lại. Giữ rà soát hằng tháng theo bản chốt.

**Phân bổ 1/ATR — lựa chọn thiết kế DUY NHẤT sống sót.**

| | CAGR TB | Sụt giảm TB |
|---|---|---|
| 1/ATR | 9,05% | **−29,5%** |
| Cân bằng đều | 9,29% | −30,9% |

Lợi nhuận ngang nhau, và 1/ATR cho sụt giảm nhỏ hơn ở **cả 4/4 pha**. Đúng y như lý do đã ghi từ đầu: *chọn 1/ATR vì rủi ro, không vì lợi nhuận*. Đây là chỗ duy nhất trong toàn bộ hệ thống mà lý do ban đầu vẫn đứng vững sau khi đo lại.

### Con số dùng cho báo cáo từ nay

> Hệ thống, đo trên 52 tháng (04/2022–08/2026), 112 mã HOSE, đã trừ phí 0,4%/vòng quay, lấy trung bình bốn pha lưới lấy mẫu: **CAGR 9,1%, sụt giảm tối đa −29,5%, vượt VN-Index +0,7 điểm phần trăm/năm với t ≈ 0,2 — không có ý nghĩa thống kê.** VN-Index cùng kỳ 8,3%.

Mọi trích dẫn con số 13,89% / −21,3% / t = 0,87 trong tài liệu cũ phải được thay bằng đoạn trên.

### Đã kiểm tra: hai file Word KHÔNG chứa con số hỏng

- `Triet_ly_dau_tu_FF5.docx` — bản chốt, cố ý không có con số hiệu năng nào; chỉ mô tả phương pháp. **Không cần sửa.**
- `Bao_cao_chien_luoc_dau_tu.docx` — dựng ngày 14/08/2026, viết về **khung cuộc thi cũ** (luật thoát A/C, 56.496 lệnh mô phỏng, kiểm định hoán vị p = 0,689). Không chứa 13,89% hay bất kỳ con số nào của khung dài hạn. **Không cần sửa con số**, nhưng toàn bộ file mô tả một khung đã bị bỏ ngày 17/08 — cần dựng lại nếu muốn nó phản ánh hệ thống hiện hành.
- `bao_cao_dm2_20260818.html` và `bao_cao_dm2_20260819.html` có trích 13,89% / −21,3% / t = 0,87. **Cố ý không sửa**: đó là báo cáo theo phiên, mỗi phiên một bản ghi riêng, và chúng đúng với thông tin có tại ngày đó. Việc đính chính thuộc về báo cáo cuối kỳ, không phải việc viết lại bản ghi cũ.

---

## 9. Bỏ trần trùng lặp — ngày 02/09/2026

Quy tắc *"một mã ≤ 10% tổng tài sản hai tài khoản, áp sau khi làm tròn lô"* (Tầng 3) **đã bị xoá**. Đây là quyết định của người vận hành, không phải kết luận từ backtest.

### Bằng chứng đo được ngày 02/09 (NAV DM2 = 60.155.732đ, DM1 rỗng)

| Ràng buộc | Giá trị | Ghi chú |
|---|---|---|
| Trần mã DM2 (20% NAV) | 12.031.146đ | bản chốt 17/08 |
| Trần trùng lặp (10% tổng 2 tài khoản) | **6.015.573đ** | chặt gấp đôi trần mã |
| Ticket tối thiểu DM2 | 5.000.000đ | |

Vì DM1 rỗng từ 25/08, "10% tổng tài sản hai tài khoản" thoái hoá thành "10% của riêng DM2". Hệ quả: **trần mã 20% của DM2 không bao giờ có hiệu lực** — nó bị trần trùng lặp che hoàn toàn, thành chữ chết trong chính tài liệu này.

Cộng với ticket tối thiểu, mọi lệnh mua phải rơi vào cửa sổ **5.000.000 – 6.015.573đ**, rộng đúng 1,02 triệu. Mã nào không có bội số nguyên của giá trị một lô lọt vào cửa sổ đó thì bị ép về 0, bất kể xếp hạng:

| Mã | Giá | 1 lô | 2 lô | Kết quả |
|---|---|---|---|---|
| VHM (hạng 3, qua cả 4 cửa) | 73.000 | 7.300.000 | 14.600.000 | **0** |
| DHC (qua cả 4 cửa) | 36.900 | 3.690.000 (dưới ticket) | 7.380.000 (vượt trần) | **0** |
| LPB | 49.950 | 4.995.000 (hụt ticket 5.000đ) | 9.990.000 | **0** |
| MSB | 13.350 | 1.335.000 | … | 400 CP |
| BSR | 26.600 | 2.660.000 | 5.320.000 | 200 CP |

Toàn bộ dải thị giá **> 60.200đ** và **30.100 – 49.950đ** bị chặn sạch (cùng ba dải hẹp hơn: 20.100–24.950, 15.050–16.650, 12.050–12.450).

### Lý do bỏ, không phải nới

Một trần đặt bằng **số tiền tuyệt đối** đang thay bảng xếp hạng quyết định thứ tự ưu tiên, và nó thưởng cho mã thị giá thấp. Đó đúng là loại lệch chuẩn mà hệ thống này được dựng ra để tránh: `Triet_ly_dau_tu_FF5.docx` nói thứ hạng quyết định *mã nào được chọn trước*, còn 1/ATR quyết định *mua bao nhiêu* — không có chỗ nào cho thị giá.

Chặn tập trung còn lại: **trần mã (15% DM1 / 20% DM2) + trần ngành (30% / 40%)**.

### Sai lệch quy trình phải ghi nhận

Sổ ngày 26/08 và 29/08 đều ghi: *"phải chốt TRAN_TRUNG_LAP TRƯỚC 01/09, không được chốt sau khi nhìn bảng lệnh."* Quyết định này trên thực tế được đưa **sau** khi đã nhìn bảng lệnh 02/09 và thấy nó chặn DHC. Ghi lại để kỳ sau đối chiếu — đây là một sai lệch đã biết, không phải một lời bào chữa.

### Ảnh hưởng lên bảng lệnh 02/09

Trước khi bỏ: mua BSR 200. Sau khi bỏ: **mua thêm DHC 200 (7.380.000đ)**; VHM có tỷ trọng mục tiêu 100 CP đúng bằng số đang giữ nên không sinh lệnh. Tỷ trọng cổ phiếu mục tiêu tăng từ 17,7% lên 48,8%.

### File đã sửa

`lt_config.py` (xoá hằng số + khối ghi chú lý do), `lt_allocator.py` (xoá vòng 3, sửa dòng ghi chú từng in sai ràng buộc), `build_report_ff5.py` (gỡ dòng bảng tham số). Bản sao lưu trước khi sửa: `data/lt_config_backup_20260902.py`, `data/lt_allocator_backup_20260902.py`, `data/CHIEN_LUOC_DAI_HAN_backup_20260902.md`.

---

## 10. Sửa hai lỗi bảng lệnh — ngày 02/09/2026

### 10.1 Bán rồi mua lại cùng một mã (vòng rửa)

Bảng lệnh in cả `BÁN 200 BSR` lẫn `MUA 200 BSR` trong cùng một kỳ: quy tắc thoát 3 đuổi BSR ra (hạng 0,70 > 0,40) trong khi `chon()` lấp tới 8 ô từ danh sách đủ điều kiện nên nó quay lại ngay ở dưới. Vị thế không đổi, chỉ mất phí hai chiều.

**Đây không phải hành vi đã backtest.** Trong `lt_backtest_scope.js`, mã rơi khỏi `keep` vẫn nằm trong `pool` và được chọn lại, nhưng harness tính vòng quay bằng `to += Math.abs(w[k] − prev[k])` (dòng 123) nên tỷ trọng giữ nguyên → **turnover = 0, chi phí = 0**. Bán thật rồi mua lại thật sẽ làm kết quả thực tế kém backtest đúng bằng phần phí đó — một khoản lệch có hệ thống, không phải ngẫu nhiên.

**Cách sửa: bù trừ lệnh bán/mua cùng mã trước khi in bảng.** Sửa cho khớp harness, không đổi luật — quy tắc thoát vẫn kích hoạt, bảng xếp hạng vẫn chọn lại, chỉ không đặt lệnh cho phần chồng lấn. Phần dư vẫn thành lệnh thật: bán nhiều hơn mua → còn lệnh bán phần chênh; mua nhiều hơn bán → còn lệnh mua phần chênh. Kết cục vị thế luôn bằng tỷ trọng mục tiêu, đúng như harness.

Bảng lệnh in thêm khối `DA BU TRU` ghi rõ mã nào bị bù trừ, vì lý do gì và tránh được bao nhiêu phí — không được im lặng bỏ lệnh.

Kỳ 02/09: BSR 200 CP bù trừ, **tránh 21.280đ phí rửa**.

### 10.2 Dòng tổng kết chỉ trừ lệnh bán, không cộng lệnh mua

`SAU KHI ĐẶT LỆNH` tính `con_lai = đang_giữ − bán`, bỏ qua toàn bộ lệnh mua, nên báo "3 mã / cổ phiếu 43,3%" trong khi bảng lệnh ngay phía trên có lệnh mua. Đã sửa thành `đang_giữ − bán + mua`, và tỷ trọng chia cho **NAV sau phí** (chia cho NAV trước phí thì hai tỷ trọng cộng lại ra 99,9%).

Kỳ 02/09 sau khi sửa: **5 mã (BSR, DHC, MSB, STB, VHM) — cổ phiếu 38.764.000 (64,5%), tiền mặt 21.348.300 (35,5%), NAV 60.112.300.** Đã đối chiếu độc lập bằng một phép tính tay riêng, khớp tới đơn vị đồng.

### 10.3 Phát hiện kèm theo — chặn cứng −25% KHÔNG kiểm được cho mã đã rớt bộ lọc

Khi chạy thử với vị thế giả lập, lộ ra một lỗ hổng **có sẵn từ trước, chưa sửa**: `lt_screener.py` chỉ ghi vào `candidates_*.json` những mã **qua bộ lọc cứng**. Mã đang giữ mà đã rớt bộ lọc thì không có bản ghi, nên `gia.get(ma)` trả về `None` và code lùi về **giá vốn**. Kết quả: điều kiện `g <= gv × 0,75` không bao giờ đúng — **chặn cứng −25% không thể kích hoạt cho đúng nhóm mã cần nó nhất.**

Một cổ phiếu sập thường thủng MA200 trước, tức rớt bộ lọc trước, rồi mới giảm tới −25%. Vậy chặn cứng đang tắt đúng vào lúc nó có việc.

Hiện allocator in cảnh báo `PHAI CHAM TAY` kèm dòng nói rõ chặn cứng không kiểm được cho nhóm này. **Chưa sửa gốc** — sửa gốc cần đọc giá từ `scan_*.json` thay vì chỉ `candidates_*.json`, là một thay đổi luồng dữ liệu, chưa làm.

---

## 11. Lần đầu lớp phủ quyết Bước 3 loại một mã ĐANG NẮM GIỮ — ngày 14/09/2026

Mục 2 có một câu tự kiểm tra: *"một lớp phủ quyết không bao giờ phủ quyết thì trên thực tế không tồn tại."* Ngày 14/09/2026 câu đó được trả lời lần đầu bằng một vị thế thật.

**Chuỗi nhân quả — ghi đúng thứ tự, vì thứ tự mới là bằng chứng:**

1. **Luận điểm lúc mua (17–19/08):** quỹ mua STB dựa trên **thông tin sơ bộ từ báo cáo phân tích của các công ty chứng khoán**, chưa tự thẩm định độc lập từ BCTC.
2. **Khi tự thu thập dữ liệu để viết báo cáo giữa kỳ**, quỹ phát hiện thông tin **phủ quyết chính luận điểm ban đầu**. Kết quả chấm thành phiếu thẩm định Bước 3 ngày 13/09: **năm cổng phủ quyết đều KHÔNG bật**, nhưng điểm là **1/6** — trục A = 0, trục B = 1, trục C = 0. Luật kết luận có hai nhánh (tổng ≤ 2, hoặc có trục = 0) và **cả hai cùng thoả**.
3. **14/09 đặt `luan_diem_con_nguyen = false`** → quy tắc thoát số 4 → **bán toàn bộ 100 CP @76.900**, không phải một nửa.

**Vì sao phải qua trường `luan_diem_con_nguyen` chứ không phải `buoc3_tham_dinh`:** `sell_checklist()` trong `lt_screener.py` **không đọc** kết luận Bước 3. Ghi `buoc3_tham_dinh = "loai"` chỉ tắt `buy_ready`; vị thế đang giữ vẫn được giữ nguyên. Bước 3 là **cửa mua**. Với mã đang nắm, phủ quyết Bước 3 phải được dịch sang ngôn ngữ của luật thoát — tức quy tắc 4 — thì mới có hiệu lực. Đây không phải lỗi thiết kế mà là ranh giới cố ý: nó buộc người ra quyết định phải nói thẳng "luận điểm đã gãy" thay vì để một nhãn thẩm định âm thầm bán hàng.

**Lệnh này TRONG LUẬT.** Không ghi vào `LENH_NGOAI_LUAT`, không ghi vào `LENH_QUY_TAC_5`. Hệ thống sinh ra nó, không phải cảm quan.

**Số liệu:** 100 × 76.900 = 7.690.000 − phí/thuế 0,25% (19.225) = **7.670.775 ròng**; giá vốn 74.200 → lãi ròng **+250.775 (+3,38%)**. Tiền mặt DM2: 25.054.252 → **32.725.027**. Còn 4 mã: MSB 840, BSR 200, VHM 50, DHC 200.

**Điều đáng ghi nhất không phải lãi 3,38%.** Là chỗ này: một luận điểm xây trên báo cáo phân tích bên thứ ba, chưa qua thẩm định độc lập, **là luận điểm chưa từng được kiểm**. Nó không "gãy" vào tháng 9 — nó vốn đã mỏng từ tháng 8, và chỉ lộ ra khi quỹ tự đọc số gốc. Hệ quả cho quy trình: **Bước 3 phải chạy TRƯỚC khi mua, không phải khi viết báo cáo giữa kỳ.** Bốn mã còn lại (MSB, BSR, VHM, DHC) đều đang mang nhãn `buoc3 = "dat"` nhập ngày 01/09 và `luan_diem` vẫn rỗng — cùng tình trạng mà STB đã ở, chỉ là chưa ai đọc lại.

**Dữ liệu:** `data/tham_dinh.json` → `STB.buoc3_chi_tiet` (năm cổng, ba trục, bảng V3b bốn kỳ, kiểm định độ bền bốn cách đọc, ba việc mở lại phiếu trước hạn 12/12/2026) và `STB.da_ban`. Sao lưu: `data/tham_dinh_backup_20260914.json`, `data/lt_config_backup_20260914.py`, `data/CHIEN_LUOC_DAI_HAN_backup_20260914.md`.

---

## 12. Bước 3a CANSLIM — đăng ký trước, kiểm định, BÁC BỎ — ngày 22/09/2026

Đề xuất "Thay Bước 3 bằng thẩm định CANSLIM" (bản nháp mục 9.4 của báo cáo) được chất vấn qua 9 quyết định, rồi đo bằng phép thử **đăng ký trước**. Kết quả: **BÁC BỎ**. Mục này ghi lại theo đúng thứ tự: quyết định, dữ liệu, kết quả, phản biện, và những gì còn mở.

### 12.1 Chín quyết định (chốt trước khi chạy)

| # | Quyết định |
|---|---|
| 1 | Dòng "Kiểm định 12 năm của Quỹ (Mục 8.7): quán tính 0,52, t = 5,8; M cắt sụt giảm −54% → −37%" **không có trong project** (không có file, không có script, dữ liệu giá không dài tới 12 năm) và **mâu thuẫn** với mục 2 (lọc VNINDEX theo MA50 không dự báo được hướng) và mục 8 (t ≈ 0,2). Đã gỡ khỏi phần lý do; L và M được coi là giả thuyết cần đo như mọi chữ khác. |
| 2 | Dữ liệu lợi nhuận: BCTC quý và năm từ API công khai của Vietcap (`canslim_data.py`), 112 mã HOSE, **ngày hiệu lực = ngày công bố muộn nhất trong các phần BCTC**, và không sớm hơn cuối quý + 20 ngày. |
| 3 | Bước 3 = **3a CANSLIM (máy chấm)** + **3b năm cổng phủ quyết V1–V5 (người)**; mã phải qua cả hai. |
| 4 | Nhánh chính: **M, C, A là cổng cứng; N, S, L cộng điểm, cần ≥ 2/3**. Nhánh đối chứng: cả sáu chữ đều qua. Ngưỡng ở `CANSLIM` trong `lt_config.py`. |
| 5 | **I bỏ khỏi luật máy.** Không có dữ liệu tương đương 13F. Nhánh thăm dò "khối ngoại mua ròng" **không chạy được**: Vietcap chỉ có ảnh chụp room ngoại hiện tại, không có lịch sử. |
| 6 | Phép đo P1: hệ thống B1 **có** 3a so với **không có** 3a, 4 pha lưới, 8 ô, trần 20%, 1/ATR, biên không giao dịch 3%, phí 0,4%, t Newey-West. **Chấp nhận** khi ≥ 3/4 pha dương, t ≥ 2 và sụt giảm không tệ hơn quá 3 điểm %. **Chưa kết luận** khi 1 ≤ t < 2. **Bác bỏ** khi t < 1. |
| 7 | Công tắc `CANSLIM_CHAN_MUA` bật hay tắt theo kết quả. Bác bỏ thì gỡ khỏi báo cáo, chỉ lưu hồ sơ. V1–V5 vẫn chặn trong mọi trường hợp. |
| 8 | V3 máy tính (dòng tiền HĐKD 3 năm / LNST 3 năm < 50%) **chỉ làm cờ** cho người lập phiếu 3b, không chặn mua. |
| 9 | Kết quả máy chấm ghi ra `data/canslim_YYYYMMDD.json`. `tham_dinh.json` giữ nguyên vai trò file kết luận của **người**. |

**Lệch khỏi đăng ký trước, do dữ liệu, ghi thẳng:** cửa sổ dự kiến là 2016–08/2026, nhưng Vietcap chỉ có BCTC từ Q1/2018, mà chữ A cần 16 quý LNST liên tục. Cửa sổ thực tế vì vậy là **02/2022 → 09/2026** (≈ 54 kỳ tháng), gần trùng với cửa sổ 04/2022–08/2026 của mục 8. Không có ngưỡng nào bị chỉnh sau khi xem kết quả.

### 12.2 Kết quả P1 (sau khi sửa các lỗi phản biện chỉ ra, xem 12.3)

| Biến thể | CAGR TB 4 pha | Sụt giảm TB (theo ngày) | Chênh lệch/kỳ so với B1 | t TB | Pha dương | Giải ngân TB | Phán quyết |
|---|---|---|---|---|---|---|---|
| B1 (không 3a) | **10,0%** | −41,1% | — | — | — | 94–96% | — |
| **3a nhánh chính** | **2,3%** | −19,9% | **−0,89%** | **−1,00** | **0/4** | 16–20% | **BÁC BỎ** |
| 3a đối chứng (6 chữ) | 2,4% | −13,0% | −0,90% | −0,98 | 0/4 | 10–14% | BÁC BỎ |
| 3a chính + cờ V3 chặn | 2,8% | −19,9% | −0,85% | −0,95 | 0/4 | 16–19% | BÁC BỎ |
| Chỉ M làm cổng | 8,8% | −30,6% | −0,19% | −0,41 | 2/4 | 64–70% | BÁC BỎ |
| VN-Index | 4,6% | | | | | | |

Nguồn: `data/canslim_backtest_20260922.json`, chạy lại bằng `python canslim_backtest.py`.

**Cơ chế thất bại — đọc đúng phạm vi:** nhánh chính chỉ giữ trung bình **1,3–1,6 mã / 8 ô**. Có 36–39/54 kỳ không có mã nào vừa qua Tầng 1 vừa qua 3a. Phần lớn chênh lệch đến từ **tiền nằm không**, không phải từ việc chọn mã. Phân rã của Codex: khoảng −1,09 điểm %/kỳ đến từ mức giải ngân, +0,09 điểm %/kỳ là phần dư. Phán quyết bác bỏ là bác bỏ **luật phân bổ này**: 3a làm cổng cứng trong rổ 112 mã. Nó **không** chứng minh CANSLIM chọn mã tệ hơn.

**Kiểm định từng chữ** (lợi suất vượt VN-Index 3 tháng tới, nhóm qua trừ nhóm không qua, t Newey-West, 51 kỳ, rổ ≥ 10 tỷ/phiên như đăng ký): C −0,8% (t −0,64) · A +0,9% (t +0,70) · N −0,0% (t −0,01) · S −0,5% (t −0,67) · L −2,0% (t −1,42) · M: VN-Index 3 tháng sau khi M **sai** lại tăng hơn khi M đúng 3,2 điểm % (t −0,86). **Không chữ nào có ý nghĩa thống kê**, theo cả hai chiều. L và M, hai chữ mà bản nháp 9.4.2 gọi là "đã được xác nhận trên HOSE", là hai chữ **có dấu ngược**. Kết quả này khớp với mục 2 và mục 8, không khớp với dòng "12 năm".

**Chẩn đoán HẬU KIỂM** (không dùng để phán quyết, vì được nghĩ ra sau khi đã xem kết quả):
- Lợi suất trên phần vốn đã giải ngân: 3a chính 1,15–2,11%/kỳ, so với B1 0,95–1,60%/kỳ.
- Kiểm định từng chữ chỉ trong rổ đã qua Tầng 1: A +2,8% (t 1,54). Tổ hợp C+A+NSL: +4,0% (t 1,99), nhưng **chỉ 6 kỳ**.

Hai con số này gợi ý rằng chữ A **có thể** có giá trị khi dùng làm **tiêu chí nghiêng tỷ trọng** chứ không phải cổng cứng. Đó là **một giả thuyết mới**. Muốn dùng thì phải đăng ký một phép đo mới, có ngày mới, không được hồi tố lên kết quả này.

### 12.3 Phản biện đối kháng (Codex, 22/09/2026) — 15 điểm

Đã sửa rồi chạy lại. Phán quyết không đổi.

| # | Lỗi | Xử lý |
|---|---|---|
| 2 | Biên 3% khôi phục tỷ trọng cũ sau khi đã áp trần, dẫn tới giải ngân tới 107% và một mã 22,9% | `gioi_han()` áp lại trần 20% và tổng 98% |
| 3 | Mỗi phần BCTC không giữ ngày công bố riêng | Lưu `pd_<phần>`, lấy ngày muộn nhất (177/3.772 quý có ngày khác nhau) |
| 4 | Tín hiệu và lệnh cùng giá đóng cửa | Khớp lệnh ở phiên a+1 |
| 7 | ATR xấp xỉ bằng trị tuyệt đối %thay đổi | ATR14 true range |
| 8 | Mã đang giữ mà thiếu dữ liệu thì bị bán ngầm | Giữ nguyên |
| 9 | Sụt giảm chỉ đo ở mốc tháng | Đo theo ngày |
| 11–14 | S bị yêu cầu ≥ 10 phiên mỗi chiều; LNST = 0 bị thay bằng LNST tổng; "không năm nào giảm" bị hiểu là tăng ngặt; nhận diện ngân hàng nhìn cả kỳ chưa công bố | Đã sửa, có test |
| Lúc dừng | `python canslim.py 2016-09-18` (trước đầu lịch sử): `get_indexer` trả −1, lấy nhầm phiên **cuối** 22/09/2026, tức dùng dữ liệu tương lai mà không báo | `vi_tri_ngay()` báo lỗi khi ngày nằm ngoài lịch; áp cho cả `luoi()` của backtest; có 3 test hồi quy. Backtest không đi qua nhánh này nên số liệu không đổi |

**Chưa sửa được, ghi làm giới hạn:**
1. BCTC là **bản mới nhất** (có thể đã điều chỉnh hồi tố), không phải bản công bố lần đầu.
2. **Thiên lệch sống sót:** rổ là mã đang niêm yết hôm nay.
3. Đây là **bản xấp xỉ B1 theo ngày**, không phải bản tái tạo số học của mục 8: không có trần ngành, không có chặn −25%.
4. "Chỉ mua mới phải qua 3a": mã đang giữ vẫn được tăng tỷ trọng mà không phải qua 3a.
5. Kiểm định từng chữ so trên toàn rổ thanh khoản, gồm cả những mã B1 không bao giờ mua (vì vậy có thêm bản hậu kiểm trên rổ Tầng 1).

### 12.4 Trạng thái vận hành

- `CANSLIM_CHAN_MUA = False`, `CANSLIM_KET_QUA = "bac_bo"`. `lt_screener.py` in một dòng thông báo 3a đã bị bác bỏ, **không hiện cột CANSLIM**, và vẫn in **cờ V3**. Ngày 22/09 có 5 mã bị cờ: VHM, BAF, VPI, HCM, SBT. Với HCM (công ty chứng khoán), dòng tiền HĐKD gồm cả cho vay ký quỹ, nên cờ V3 **không có nghĩa**; phiếu 3b phải dùng biến thể riêng.
- Kiểm tra chéo: V3 máy tính **khớp phiếu tay**: VHM 18% (phiếu 18,1%), BAF −439% (−439,0%), DHC 144% (144,2%).
- `python canslim.py` vẫn chạy, ghi `data/canslim_YYYYMMDD.{json,md}` làm hồ sơ. Bảng ngày 22/09: **0/13 mã qua 3a**, vì M đang sai (MA50 VNINDEX 1.776 < MA200 1.793).

### 12.5 Việc còn mở — CHỜ NGƯỜI QUYẾT

1. **Ba trục A/B/C của phiếu cũ.** Quyết định 3 bỏ ba trục **với giả định** 3a sẽ thay phần tăng trưởng. 3a đã bị bác bỏ, nên câu hỏi mở lại: Bước 3 quay về phiếu năm cổng, ba trục như trước, hay chỉ giữ V1–V5? Code chưa đổi gì ở phần này (phiếu là thủ công), nên hiện trạng = phiếu cũ.
2. Có đăng ký phép đo mới "A làm tiêu chí nghiêng tỷ trọng" (12.2, hậu kiểm) hay không.

### 12.6 Sửa bản nháp mục 9.4 của báo cáo

**Dòng cuối Bảng 9.2 thay bằng:**

| Nguồn | Giai đoạn | Kết quả | Giới hạn |
|---|---|---|---|
| Kiểm định đăng ký trước của Quỹ trên HOSE (mục 12) | 02/2022 – 09/2026, 112 mã, 4 pha lưới | CANSLIM làm cổng cứng: CAGR 2,3%/năm, so với 10,0% khi không có cổng; t = −1,00; 0/4 pha dương → **bác bỏ**. Không chữ nào có ý nghĩa thống kê; L và M có dấu ngược | Thiên lệch sống sót; BCTC bản mới nhất; không có chữ I; chủ yếu do tiền nằm không (giải ngân 16–20%) |

**Đoạn "Đọc bảng theo đúng phạm vi" thay bằng:** CANSLIM đã cho kết quả tốt ở dạng bộ lọc trên thị trường Mỹ, nhưng các sản phẩm thực chiến xây theo nó lại kém chỉ số. Trên HOSE, kiểm định đăng ký trước của Quỹ **không xác nhận** chữ nào, kể cả L và M. Dùng làm cổng cứng trên rổ 112 mã, CANSLIM để tiền nằm không phần lớn thời gian và bị bác bỏ theo đúng ngưỡng đã chốt trước. Quỹ vì vậy **không** thay Bước 3 bằng CANSLIM. Tín hiệu duy nhất đáng theo dõi là chữ A trong rổ đã qua bộ lọc, và nó sẽ được đo bằng một phép thử đăng ký mới.

**File:** `canslim_data.py`, `canslim.py`, `canslim_backtest.py`, `tests/test_canslim.py`, `data/canslim_cache/`, `data/canslim_20260922.{json,md}`, `data/canslim_backtest_20260922.json`. Sao lưu: `data/CHIEN_LUOC_DAI_HAN_backup_20260922.md`, `data/lt_config_backup_20260922.py`, `data/lt_screener_backup_20260922.py`.
