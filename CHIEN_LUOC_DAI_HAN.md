# Chiến lược đầu tư dài hạn — Danh mục 1 (200tr) & Danh mục 2 (60tr)

**Chốt ngày 17/08/2026.** Thay thế hoàn toàn khung "tối đa hoá P(về nhất)" của cuộc thi.

> 🔴 **Từ 05/10/2026: KHUNG GIAI ĐOẠN 2** — đúng khung đã công bố ở Mục 9 báo cáo giai đoạn 1 nộp BTC (tr. 69–73): *"Doanh nghiệp tốt là điều kiện (Fisher), giá hợp lý là nguyên tắc (Graham), xu hướng xác nhận là kỷ luật (Medici)."* **Trụ 1 — chế độ thị trường** đặt *trần* tỷ trọng cổ phiếu (Tăng 100% · Điều chỉnh 60% · Giảm 0% = bán hết, khoá mua). **Trụ 2 — năm cổng + ba trục + biên an toàn kép** chọn mã: chỉ phiếu Đạt, giá ≤ 0,85 × Thận trọng, bán khi chạm Cơ sở. RS và ATR bỏ khỏi bộ lọc; quy tắc 5 bỏ; mọi lệnh cần phiếu ghi trước giờ đặt. Mục 0, 2, 6, 7 đã sửa theo; **mục 14** ghi đủ 17 quyết định, bằng chứng, lệnh đầu tiên (bán hết ngày 05/10) và các sai lệch phải công bố. **Phần chọn mã vẫn chưa có backtest; lớp chế độ có phép đo trên VN-Index (mục 14.4).**
>
> 🔴 **Từ kỳ soát 01/10/2026: khung TOP-DOWN, hai nhánh song song, quét toàn thị trường, bỏ Bước 2 (xếp hạng).** Máy tìm mọi cổ phiếu HOSE + HNX + UPCoM đang trong xu hướng; Quỹ tự chọn rổ cơ bản theo top-down; **giao điểm hai rổ là lựa chọn của Quỹ.** Mọi mô tả luật đang chạy ở mục 0, 2, 6, 7 đã sửa theo; mục 13 ghi đủ 14 quyết định và lý do. **Hệ thống từ 01/10/2026 chưa có backtest.**

---

## 0. Triết lý đầu tư — từ 05/10/2026: Graham + Fisher + kỷ luật xu hướng

> *"Doanh nghiệp tốt là điều kiện (Fisher), giá hợp lý là nguyên tắc (Graham), xu hướng xác nhận là kỷ luật (Medici)."* — Mục 9 báo cáo giai đoạn 1, tr. 71.

Khi phân tích cơ bản và xu hướng giá cho hai tín hiệu ngược nhau, Quỹ **đứng ngoài**: không mua mã chưa được xu hướng xác nhận, và bán mã đang giữ khi xu hướng gãy (giá < 97% MA200, xét ở kỳ soát). Mục tiêu: **tăng trưởng với rủi ro thấp** (tr. 72) — Quỹ chấp nhận đánh đổi tốc độ tăng trưởng lấy sụt giảm nông hơn, và đã đo cái giá đó (mục 14.4).

### Checklist mua — từ 05/10/2026 (đủ tất cả)

- [ ] Chế độ thị trường **không phải Giảm**, và tổng cổ phiếu sau lệnh ≤ trần (Tăng 100%, Điều chỉnh 60%)
- [ ] Mã nằm trong **rổ cơ bản top-down đã chốt** (vĩ mô → ngành → doanh nghiệp, mục 13)
- [ ] **Phiếu năm cổng + ba trục kết luận Đạt, còn hạn**: tổng ≥ 4, không trục nào bằng 0, không cổng nào bật. Nhãn "đạt" không có phiếu thì không đủ
- [ ] Có **hai kịch bản định giá** (Thận trọng, Cơ sở) và giá ≤ **0,85 × Thận trọng**
- [ ] **Xu hướng xác nhận**: giá > MA200, MA50 > MA200, thanh khoản khớp lệnh ≥ 10 tỷ/phiên
- [ ] Có **phiếu lệnh** ghi trước giờ đặt (`PHIEU_LENH`); lệnh mua chỉ đặt sau một kỳ soát

### Checklist bán — từ 05/10/2026 (một điều là bán toàn bộ)

- [ ] Chế độ thị trường sang **Giảm** — xét mỗi phiên
- [ ] Giá đóng cửa **≥ giá trị Cơ sở** — xét mỗi phiên
- [ ] **Chặn cứng −25%** so với giá vốn — xét mỗi phiên
- [ ] **Dây bẫy luận điểm** bị chạm, hoặc mã bị loại khỏi rổ (quy tắc 4) — xét ngay khi có số liệu
- [ ] Giá < **97% MA200** — xét ở kỳ soát đầu tháng
- Ở kỳ soát: cổ phiếu vượt trần chế độ quá 3% NAV thì **cắt theo tỷ lệ** về trần

### Quy tắc tránh sai lầm

- Không bán theo cảm quan (quy tắc 5 đã bỏ). Không đặt lệnh chưa có phiếu ghi trước.
- Không nâng giá trị Cơ sở để giữ tiếp: chỉ nâng bằng phiếu mới dựa trên BCTC mới, ghi trước khi giá chạm.
- Không mua doanh nghiệp mình không hiểu, không mua vì "được khuyên" hay vì đã tăng mạnh.
- Không miễn trừ theo mã: chế độ Giảm bán cả mã tốt nhất danh mục.

<details><summary>(lịch sử, 17/08–04/10/2026) Triết lý cũ: Peter Lynch + kỹ thuật</summary>

## 0 (cũ). Triết lý đầu tư tích hợp: Peter Lynch + kỹ thuật

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
- [ ] ~~Cổ phiếu rơi khỏi top 40% theo thứ hạng vị trí~~ — **ĐÃ BỎ 01/10/2026** cùng Bước 2 (mục 13)
- [ ] **Mã không còn trong rổ cơ bản** — bị loại ở tầng vĩ mô, ngành hay doanh nghiệp (kể cả phủ quyết V1–V5, luận điểm gãy) — nhập tay ở `data/tham_dinh.json`
- [ ] Chặn cứng −25% so với giá vốn — ngoại lệ duy nhất giữa hai kỳ rà soát

### Qui tắc tránh sai lầm

- Không mua cổ phiếu chỉ vì "được khuyên" hoặc vì đã tăng mạnh.
- Không mua doanh nghiệp mình không hiểu.
- Không coi kỹ thuật là nguyên nhân quyết định duy nhất; kỹ thuật chỉ là lớp xác nhận, không thay thế giá trị hạ tầng.
- Không cố gắng mua ở đáy tuyệt đối; thay vào đó, ưu tiên mua khi cơ bản tốt và thị trường đã bắt đầu xác nhận sự phục hồi.

Kết luận ngắn gọn:

> Mua doanh nghiệp tốt ở giá hợp lý, nhưng chỉ vào khi xu hướng và kỹ thuật đang ủng hộ. Đây là sự kết hợp giữa "đầu tư giá trị" và "đầu tư theo xu hướng" — chặt chẽ về chất lượng, cẩn trọng về thời điểm, và kỷ luật về rủi ro.

</details>

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

> **Từ 05/10/2026 (mục 14):** thêm **Trụ 1 — chế độ thị trường** đứng trên cả ba tầng: tổng cổ phiếu ≤ trần của chế độ, Giảm = bán hết và khoá mua. Tầng 1 bỏ RS và ATR (còn thanh khoản, giá > MA200, MA50 > MA200). Giao điểm phải qua thêm **phiếu Đạt còn hạn** và **biên an toàn ≥ 15% dưới Thận trọng**. Luật thoát: bỏ quy tắc 2 (RS) và quy tắc 5 (cảm quan), thêm bán khi chạm Cơ sở và khi chế độ Giảm.
>
> **Từ 01/10/2026:** Tầng 1 chạy trên **toàn thị trường** (HOSE + HNX + UPCoM, `lt_scan_vietcap.py`), điều kiện không đổi, RS luôn so với VNINDEX. **Tầng 2 đã bỏ** — thay bằng giao điểm với rổ cơ bản top-down do người lập. Tầng 3 giữ nguyên, trừ trần ngành dùng ngành người gán trong rổ. Chi tiết mục 13.

### Tầng 1 — Bộ lọc cứng (mã có được phép mua không)

| Điều kiện | Ngưỡng | Lý do |
|---|---|---|
| Thanh khoản | GTGD TB 20 phiên ≥ 10 tỷ/phiên | 200tr vào/ra không làm lệch giá |
| Xu hướng dài hạn | Giá đóng cửa > MA200 | Chỉ nắm giữ mã đang ở pha tăng |
| Cấu trúc | MA50 > MA200 | Loại mã mới hồi kỹ thuật trong xu hướng giảm |
| ~~**Mạnh hơn thị trường**~~ | ~~RS 12 tháng (bỏ 1 tháng gần nhất) > 0~~ | **ĐÃ BỎ 04/10/2026** (quyết định 5, mục 14): đà tăng tương đối loại đúng nhóm mã Trụ 2 cần tìm; chữ L có dấu ngược (mục 12.2) |
| ~~Chặn an toàn~~ | ~~ATR ≤ 6%/phiên~~ | **ĐÃ BỎ 04/10/2026** (cam kết #2 báo cáo giai đoạn 1): chưa loại mã nào trong 9 kỳ quét; biến động vẫn được xử lý ở 1/ATR |

Bỏ 1 tháng gần nhất (skip-month) là chuẩn học thuật: đảo chiều ngắn hạn làm nhiễu tín hiệu momentum.

### ~~Tầng 2 — Điểm xếp hạng~~ — ĐÃ BỎ 01/10/2026

> Phần dưới giữ làm hồ sơ. Việc chọn mã nào trước nay do `uu_tien` người gán trong rổ cơ bản quyết định, phá hoà bằng ATR thấp trước (mục 13, quyết định 5).

`Điểm = 0,40 × RS12T(bỏ 1T) + 0,30 × RS6T + 0,20 × RS3T + 0,10 × Chất lượng xu hướng`

Tất cả tính bằng **phân vị trong rổ ĐÃ QUA BỘ LỌC CỨNG** (không phải toàn rổ 112 mã), không dùng giá trị tuyệt đối — theo đúng `Triet_ly_dau_tu_FF5.docx`, Bước 2. Chất lượng xu hướng = R² của log(giá) theo thời gian trên ~6 tháng — momentum "mượt" bền hơn momentum "giật cục".

Ngoài giá trị điểm, mỗi mã còn có **thứ hạng vị trí** `thu_hang = (i−1)/(n−1)` sau khi sắp xếp giảm dần theo điểm, với `i` là vị trí và `n` là số mã qua lọc. Luật thoát số 3 hỏi về **thứ hạng**, không về giá trị điểm — hai thứ này khác nhau và việc lẫn lộn chúng đã là một lỗi thật (xem mục 7).

⚠️ **R² và RS 6 tháng là thành phần XẾP HẠNG ở tầng này, không phải điều kiện lọc ở Tầng 1.** Bản `lt_screener.py` trước 25/08/2026 đưa `trend_r2 ≥ 0,20` và `RS6T ≥ 0` vào bộ lọc cứng — biến một tiêu chí "để xếp trước sau" thành một tiêu chí "được phép hay không". Đã gỡ bỏ.

**Không còn dùng `p` (xác suất thắng) hay `ER`.** Kiểm định hoán vị trước đây cho p-value 0,689: `p` không có sức phân biệt, và softmax khuếch đại nó theo hàm mũ nên khuếch đại nhiễu.

### Tầng 3 — Phân bổ (mua bao nhiêu)

- Tỷ trọng ∝ **1 / ATR** (rủi ro ngang nhau giữa các vị thế), không theo điểm xếp hạng.
- Trần 15%/mã (DM1), 20%/mã (DM2); trần ngành 30% (DM1), 40% (DM2).
- ~~Trần trùng lặp: một mã ≤ 10% **tổng tài sản hai tài khoản**, áp sau khi làm tròn lô.~~ **ĐÃ BỎ 02/09/2026** — xem mục 9.
- **Tiền mặt sinh ra tự động**: mỗi "ô" không tìm được mã đạt chuẩn thì ô đó nằm tiền. ~~Không có bất kỳ quy tắc canh chỉ số nào — đã kiểm chứng 17/08 rằng bộ lọc VNINDEX theo MA50 **không** dự báo được hướng chỉ số.~~ **Từ 05/10/2026:** tổng cổ phiếu còn bị chặn trên bởi **trần chế độ thị trường** (Tăng 100% · Điều chỉnh 60% · Giảm 0%). Dải chỉ là trần — cuộc thi chỉ cho mua cổ phiếu nên không có ETF để lấp sàn — vì vậy tiền mặt vẫn sinh ra khi thiếu mã đạt Trụ 2 (quyết định 3, mục 14). Lớp chế độ không dự báo hướng chỉ số; nó đổi tốc độ tăng trưởng lấy sụt giảm nông hơn (mục 14.4).

Số ô: **DM1 = 10, DM2 = 8** (đo được, xem mục 4).

### Luật thoát

> **Từ 05/10/2026 (mục 14, quyết định 1, 4, 6, 11, 12):** bán **toàn bộ** khi một trong các điều sau xảy ra — **mỗi phiên:** chế độ Giảm · giá đóng cửa ≥ giá trị Cơ sở · chặn cứng −25% · quy tắc 4 (người đánh `luan_diem_con_nguyen = false` khi dây bẫy chạm, hoặc loại khỏi rổ); **ở kỳ soát đầu tháng:** giá < 0,97 × MA200, và cắt theo tỷ lệ phần cổ phiếu vượt trần chế độ quá 3% NAV. **Quy tắc 2 (RS) và quy tắc 5 (cảm quan) đã bỏ.** Đoạn dưới là luật 01/10–04/10/2026, giữ để đối chiếu.

Rà soát **đầu mỗi tháng**. Giữ tiếp khi còn đủ **cả ba** (sửa 01/10/2026; số hiệu giữ như cũ để đối chiếu):

1. Giá đóng cửa > 0,97 × MA200 (đệm 3% chống nhiễu)
2. RS 12 tháng so với VNINDEX > −5%
3. ~~Thứ hạng vị trí ≤ 40% trong rổ đã qua bộ lọc~~ — **ĐÃ BỎ 01/10/2026.** Mục 8 đã đo tác động của nó là nhiễu (trung bình +0,07 điểm %)
4. **Mã còn nằm trong rổ cơ bản** — quy tắc duy nhất không đọc dữ liệu giá. Bị loại ở tầng vĩ mô, ngành hay doanh nghiệp đều là hỏng. Ba trạng thái: trong rổ / bị loại (→ bán) / **thiếu hoặc nhập sai kết luận (→ không tự bán, allocator in PHẢI CHẤM TAY)**

Hỏng bất kỳ điều nào → bán toàn bộ vị thế, tiền chuyển sang mã kế tiếp ở giao điểm theo thứ tự `uu_tien` rồi ATR; giao điểm rỗng thì phần vốn đó nằm tiền. Lệch tỷ trọng < 3% NAV thì **không** điều chỉnh (biên không giao dịch). Chặn cứng một chiều: −25% so với giá vốn — ngoại lệ duy nhất được kích hoạt giữa hai kỳ rà soát, và là quy tắc duy nhất trong hệ thống tham chiếu tới giá vốn.

**Lệnh bán CHỈ đến từ các quy tắc trên** (bốn quy tắc tới 30/09/2026, ba quy tắc từ 01/10/2026). Một mã không lọt vào danh mục mục tiêu nhưng vẫn trả lời "có" cho cả bốn câu thì **giữ nguyên** — không bán. Bản `lt_allocator.py` trước 25/08/2026 tính chênh lệch so với danh mục mục tiêu rồi bán phần dư, tức tái cơ cấu toàn bộ mỗi kỳ; backtest cho thấy tái cơ cấu toàn bộ hằng tháng chỉ đạt 6,95%/năm so với 13,89% của bán-theo-quy-tắc-thoát.

### Quy tắc thứ năm — bán theo cảm quan thị trường của quỹ (đổi ngày 11/09/2026)

> 🔴 **ĐÃ BỎ HẲN từ 05/10/2026** (quyết định 11, mục 14) — đúng cam kết #5 tr. 70 báo cáo giai đoạn 1: *"bỏ hẳn quy tắc bán theo cảm quan; lệnh nào thiếu lý do ghi trước giờ đặt thì người phê duyệt từ chối."* Sổ `LENH_QUY_TAC_5` giữ làm hồ sơ (4 lệnh, cả 4 ghi sau khi khớp). Thay bằng sổ `PHIEU_LENH` cho mọi lệnh. Phần dưới là lịch sử.

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

**Từ 05/10/2026 — hai nhịp** (quyết định 12, mục 14):

*Mỗi phiên, sau 15h:*

1. `PYTHONIOENCODING=utf-8 python lt_che_do.py` → chế độ thị trường + ba luật xét mỗi phiên (Giảm, −25%, chạm Cơ sở) cho từng mã đang giữ. Chỉ báo, không sinh bảng lệnh.
2. Có tín hiệu bán, hoặc dây bẫy chạm (đặt `luan_diem_con_nguyen = false`) → **ghi `PHIEU_LENH` trong `lt_config.py` kèm giờ ghi** → đặt lệnh phiên sau. Muốn có bảng lệnh: quét → screener → `NGAY_CHAY=<ngày đặt> LOAI_KY=hang_ngay python lt_allocator.py` (nhịp hằng ngày không bao giờ sinh lệnh mua).
3. Sau khi khớp: `data/so_giao_dich.json`, `HOLDINGS`, `TIEN_MAT`, trạng thái phiếu.

*Kỳ soát đầu tháng* (thứ tự là một phần của luật):

1. **Chốt rổ cơ bản** và **định giá hai kịch bản** (`dinh_gia.than_trong`, `dinh_gia.co_so`) trong `data/tham_dinh.json` **trước** bản quét. Phiếu năm cổng + ba trục hết hạn thì lập lại.
2. `lt_scan_vietcap.py` → `lt_screener.py` (in chế độ, ghi `data/che_do_YYYYMMDD.json`) → cập nhật `HOLDINGS`/`TIEN_MAT` → `lt_allocator.py` (mặc định `LOAI_KY=soat`: đủ mọi luật, cắt về trần, lệnh mua).
3. Ghi `PHIEU_LENH` cho từng lệnh trước giờ đặt. Bảng lệnh in `[CHUA CO PHIEU]` cho lệnh thiếu phiếu.

Rổ chưa chốt: allocator **vẫn sinh lệnh bán** theo luật giá và chế độ, chỉ chặn lệnh mua (đổi 04/10/2026 — trước đó dừng hẳn).

**Từ 01/10/2026 tới 04/10/2026** (thứ tự là một phần của luật — rổ phải chốt **trước** bản quét):

1. **Chốt rổ cơ bản** trong `data/tham_dinh.json`: `_ro_co_ban.vi_mo`, `_ro_co_ban.nganh`, và ở từng mã `trong_ro` / `nganh` / `uu_tien` / `ngay_vao_ro` / `ly_do_ro`. Mọi mã **đang giữ** phải có kết luận `trong_ro`. Ghi `_ro_co_ban.ngay_chot`.
2. `PYTHONIOENCODING=utf-8 python lt_scan_vietcap.py` → `data/scan_YYYYMMDD.json` (toàn thị trường, ~2 phút).
3. `PYTHONIOENCODING=utf-8 python lt_screener.py` → rổ xu hướng, rổ cơ bản, **giao điểm** + `data/candidates_YYYYMMDD.json`. Đọc dòng `[HANG RAO]` nếu có: rổ bị sửa sau bản quét.
4. Cập nhật `HOLDINGS` và `TIEN_MAT` trong `lt_config.py` cho khớp sao kê.
5. `PYTHONIOENCODING=utf-8 python lt_allocator.py` → bảng lệnh. Rổ chưa chốt thì allocator **dừng**, không sinh bảng lệnh.
6. Đặt lệnh bán ngay. Lệnh mua cho mã mới ra khi phiếu V1–V5 + Bước 4 xong, trong hạn chót của kỳ (`TOP_DOWN.han_chot_lenh_mua`). Trong tháng **không làm gì** trừ khi chạm chặn cứng −25%.

<details><summary>(lịch sử, 17/08–30/09/2026) Quy trình cũ</summary>

1. Mở TradingView Desktop, khung ngày. Dán `lt_scan_tradingview.js` vào `ui_evaluate`, chờ xong (~3–10 phút), kiểm tra trùng dữ liệu, xuất ra `data/scan_YYYYMMDD.json`.
2. `PYTHONIOENCODING=utf-8 python lt_screener.py` → bảng xếp hạng + `data/candidates_YYYYMMDD.json`.
3. Cập nhật `HOLDINGS` và `TIEN_MAT` trong `lt_config.py` cho khớp sao kê.
4. `PYTHONIOENCODING=utf-8 python lt_allocator.py` → bảng lệnh.
5. Đặt lệnh. Trong tháng **không làm gì** trừ khi chạm chặn cứng −25%.

</details>

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
| `lt_config.py` | Toàn bộ tham số: vốn, số ô, bộ lọc, luật thoát, hiệu lực top-down (`TOP_DOWN`), chế độ thị trường (`CHE_DO`), biên an toàn (`BIEN_AN_TOAN_MIN`), sổ phiếu lệnh (`PHIEU_LENH`) |
| `lt_che_do.py` | **Từ 04/10/2026** — Trụ 1: máy trạng thái chế độ thị trường (một nguồn cho screener, kiểm nhanh mỗi phiên và phép đo); chạy trực tiếp = kiểm nhanh mỗi phiên |
| `kiem_dinh_che_do_vnindex.py` | **Từ 04/10/2026** — đo lớp chế độ trên VN-Index 2004–2026 (mục 14.4); dữ liệu `data/vnindex_vietcap_20261002.json`, kết quả `data/kiem_dinh_che_do_vnindex_20261004.json` |
| `lt_scan_vietcap.py` | **Nguồn quét sản xuất từ 01/10/2026** — toàn HOSE + HNX + UPCoM từ Vietcap |
| `lt_screener.py` | Tầng 1 + rổ cơ bản + giao điểm + phiếu Đạt + biên an toàn + luật thoát; ghi `candidates_*` và `che_do_*` |
| `lt_allocator.py` | Chế độ thị trường (Giảm = bán hết, trần), phân bổ 1/ATR, trần mã/ngành, làm tròn lô, kiểm phiếu lệnh; nhịp `LOAI_KY=soat` / `hang_ngay` |
| `dashboard/` | **Từ 07/10/2026** — buồng lái vận hành (Streamlit, chỉ đọc): thị trường, vĩ mô, ngành, phễu chọn mã, danh mục & lệnh; nút quét chạy đúng chuỗi trên. Không đổi luật nào. Xem `dashboard/README.md` |
| `lt_scan_tradingview.js` | Quét 112 mã HOSE từ TradingView — từ 01/10/2026 chỉ để đối chiếu |
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

> 🔴 **01/10/2026: đoạn dưới đo HỆ CŨ** (112 mã HOSE, có xếp hạng RS, có luật thoát 3). Hệ thống từ 01/10/2026 **chưa có backtest**: phần chọn mã do người làm nên không backtest được; phần máy sẽ đo bằng phép thử đăng ký trước P2 (mục 13.4). Trích đoạn dưới chỉ khi ghi rõ là hệ cũ.

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

1. **Ba trục A/B/C của phiếu cũ.** Quyết định 3 bỏ ba trục **với giả định** 3a sẽ thay phần tăng trưởng. 3a đã bị bác bỏ, nên câu hỏi mở lại: Bước 3 quay về phiếu năm cổng, ba trục như trước, hay chỉ giữ V1–V5? Code chưa đổi gì ở phần này (phiếu là thủ công), nên hiện trạng = phiếu cũ. → **Đã chốt 04/10/2026 (mục 14, quyết định 8–9): năm cổng + ba trục, chỉ phiếu Đạt còn hạn được mua.**
2. Có đăng ký phép đo mới "A làm tiêu chí nghiêng tỷ trọng" (12.2, hậu kiểm) hay không.

### 12.6 Sửa bản nháp mục 9.4 của báo cáo

**Dòng cuối Bảng 9.2 thay bằng:**

| Nguồn | Giai đoạn | Kết quả | Giới hạn |
|---|---|---|---|
| Kiểm định đăng ký trước của Quỹ trên HOSE (mục 12) | 02/2022 – 09/2026, 112 mã, 4 pha lưới | CANSLIM làm cổng cứng: CAGR 2,3%/năm, so với 10,0% khi không có cổng; t = −1,00; 0/4 pha dương → **bác bỏ**. Không chữ nào có ý nghĩa thống kê; L và M có dấu ngược | Thiên lệch sống sót; BCTC bản mới nhất; không có chữ I; chủ yếu do tiền nằm không (giải ngân 16–20%) |

**Đoạn "Đọc bảng theo đúng phạm vi" thay bằng:** CANSLIM đã cho kết quả tốt ở dạng bộ lọc trên thị trường Mỹ, nhưng các sản phẩm thực chiến xây theo nó lại kém chỉ số. Trên HOSE, kiểm định đăng ký trước của Quỹ **không xác nhận** chữ nào, kể cả L và M. Dùng làm cổng cứng trên rổ 112 mã, CANSLIM để tiền nằm không phần lớn thời gian và bị bác bỏ theo đúng ngưỡng đã chốt trước. Quỹ vì vậy **không** thay Bước 3 bằng CANSLIM. Tín hiệu duy nhất đáng theo dõi là chữ A trong rổ đã qua bộ lọc, và nó sẽ được đo bằng một phép thử đăng ký mới.

**File:** `canslim_data.py`, `canslim.py`, `canslim_backtest.py`, `tests/test_canslim.py`, `data/canslim_cache/`, `data/canslim_20260922.{json,md}`, `data/canslim_backtest_20260922.json`. Sao lưu: `data/CHIEN_LUOC_DAI_HAN_backup_20260922.md`, `data/lt_config_backup_20260922.py`, `data/lt_screener_backup_20260922.py`.

---

## 13. Chuyển sang top-down, quét toàn thị trường, bỏ Bước 2 — ngày 01/10/2026

**Quyết định của user ngày 01/10/2026:** mở rộng phạm vi quét từ 112 mã HOSE ra **toàn thị trường (HOSE, HNX, UPCoM)** và **xoá Bước 2 (xếp hạng)** vì theo đánh giá của user, bước này không đóng góp gì cho chiến lược. Khi được chất vấn, user đổi cả cấu trúc: **chiến lược thành top-down và chạy hai nhánh song song — Quỹ tự chọn rổ cổ phiếu theo cơ bản, máy tìm toàn bộ cổ phiếu đang trong xu hướng, giao điểm là lựa chọn của Quỹ.** Mười bốn quyết định dưới đây được chốt lần lượt, mỗi quyết định trước khi sang câu tiếp.

### 13.1 Bằng chứng có sẵn lúc quyết định — ghi thẳng

- **Bỏ luật thoát 3** có số liệu ủng hộ: mục 8 đo tác động của nó là nhiễu (+2,44 / −2,71 / −2,52 / +3,06 điểm %, trung bình +0,07).
- **Bỏ xếp hạng để chọn mã khi vào lệnh thì CHƯA từng được đo lại.** Con số duy nhất (13,89% xếp hạng so với 2,43% bốc thăm, mục 3) nằm trong mục đã bị đánh dấu "không trích dẫn". Nói cách khác, chưa có phép đo nào chứng minh bước này có ích, nhưng cũng chưa có phép đo nào chứng minh nó vô ích. Quyết định bỏ là quyết định của người, không phải kết luận từ dữ liệu.

### 13.2 Mười bốn quyết định

| # | Quyết định |
|---|---|
| 1 | **Xoá luật thoát 3** (thứ hạng ≤ 40%). Còn: MA200 có đệm 3%, RS12T > −5%, luật 4, chặn cứng −25% |
| 2 | **Top-down, hai nhánh song song.** Nhánh người → rổ cơ bản; nhánh máy → rổ xu hướng toàn thị trường. **Giao điểm là lựa chọn của Quỹ** |
| 3 | Rổ cơ bản **chính là** Bước 3 viết lại theo top-down (vĩ mô → ngành → doanh nghiệp); tầng doanh nghiệp vẫn phải qua **V1–V5**. Bước 4 (định giá) chỉ áp ở giao điểm. Rổ lưu trong `tham_dinh.json` |
| 4 | Luật thoát 4 = **mã không còn trong rổ**, loại ở tầng nào cũng vậy. Mọi thay đổi rổ ghi ngày và lý do, **chốt trước khi chạy quét hoặc allocator** của kỳ đó |
| 5 | Giao điểm nhiều mã hơn số ô: theo `uu_tien` người gán (chốt cùng lúc với rổ), phá hoà bằng **ATR thấp trước** |
| 6 | Nguồn quét: **`lt_scan_vietcap.py`**, giữ đúng schema 15 trường; kỳ đầu đối chiếu với TradingView trên 112 mã cũ (13.3) |
| 7 | Tầng 1 giữ nguyên năm điều kiện cho mọi sàn; RS luôn so với **VNINDEX** |
| 8 | Trần ngành dùng **ngành người gán trong rổ**; bỏ bảng `NGANH`. Mã ở giao điểm thiếu ngành → không mua, in cảnh báo |
| 9 | **Hiệu lực ngay từ kỳ soát 01/10/2026** |
| 10 | Không có ngoại lệ chuyển tiếp: hôm nay chốt vĩ mô, ngành và giữ/loại từng mã đang nắm (MSB, BSR, DHC) **rồi mới** quét và đặt lệnh bán |
| 11 | Hạn chót lệnh mua kỳ 01/10: **thứ Hai 05/10/2026**. Quá hạn → nằm tiền tới 01/11 |
| 12 | Khoá whipsaw VHM (tới 01/11), gia hạn quy tắc 5 MSB (tới 17/10) và bản thân quy tắc 5: **giữ nguyên** |
| 13 | Tài liệu ghi thẳng "hệ thống từ 01/10/2026 chưa có backtest"; sửa các phần mô tả luật đang chạy, giữ nguyên các mục lịch sử |
| 14 | Đăng ký trước phép đo P2 (13.4) |

**Lần đổi luật thứ tư giữa cuộc thi, và lần thứ ba do Quỹ chọn** (17/08 đổi khung, 11/09 đổi quy tắc 5, 16/09 thêm mốc soát do BTC đặt, 01/10 đổi sang top-down). Báo cáo cuối kỳ phải ghi đúng câu này. Người đề xuất đã khuyến nghị lùi hiệu lực tới 01/11 để không đổi luật giữa cuộc thi và để rổ cơ bản tồn tại trước khi luật dựa vào nó có hiệu lực; user chọn áp ngay.

**Ba trạng thái của luật 4, không phải hai.** Trong rổ → được mua; bị loại → bán toàn bộ; **thiếu hoặc nhập sai** (ví dụ ngành của mã không có trong rổ ngành, chưa có phiếu V1–V5) → không mua, **không tự bán**, allocator in `PHAI CHAM TAY`. Quy về "bị loại" thì một lỗi gõ nhầm sẽ bán vị thế; quy về "trong rổ" thì thiếu phiếu vẫn được mua. Rổ chưa chốt (`_ro_co_ban.ngay_chot` rỗng) thì allocator dừng hẳn, không sinh bảng lệnh.

**Hàng rào thời điểm được cưỡng chế bằng máy:** `lt_screener.py` in `[HANG RAO]` khi `ngay_chot` của rổ sau ngày bản quét, hoặc khi `tham_dinh.json` được sửa sau file quét.

**Lỗ hổng mục 10.3 đóng luôn:** screener nay ghi bản ghi cho **mọi mã đang giữ** kể cả đã rớt Tầng 1, nên chặn cứng −25% kiểm được bằng giá thật thay vì lùi về giá vốn. Có test hồi quy.

### 13.3 Đối chiếu nguồn quét — Vietcap với TradingView, trên bản quét 21/09/2026

Dựng lại đúng ngày 21/09 bằng tham số `to` của Vietcap trên 113 mã của `scan_20260921.json` (`data/scan_vietcap_doi_chieu_20260921.json`):

| Trường | Trung vị lệch | Ghi chú |
|---|---|---|
| Giá, r21, MA50, ATR | 0 | Lệch lớn chỉ ở mã có sự kiện quyền |
| r252 | 1,3 điểm % | Vietcap điều chỉnh cổ tức, TradingView không |
| **Giá trị giao dịch** | **8,7%** (p90 47%) | **TradingView cộng cả giao dịch thoả thuận.** KDC: một phiên TradingView ghi 253 nghìn CP, Vietcap 41 nghìn; các phiên khác trùng |

- Ngưỡng ở `LOC` là "giá trị **khớp lệnh**" — Vietcap đo đúng định nghĩa, TradingView đo thừa. Mọi con số thanh khoản trong các bản quét cũ đều cao hơn định nghĩa.
- DGC: bước −20% ngày giao dịch không hưởng quyền, TradingView **không** điều chỉnh (r21 lệch 17 điểm %). Vietcap có.
- **Tầng 1 hai nguồn cho cùng kết quả**, trừ LPB (Vietcap cho qua, TradingView loại).

Chạy toàn thị trường thử ngày 01/10 (ra thư mục nháp, **không** ghi vào `data/` để giữ hàng rào): 1.522 mã yêu cầu, 1.238 mã ghi được, 280 mã ngừng giao dịch > 10 ngày bị bỏ, 5 mã mới niêm yết thiếu dữ liệu; **100 giây**. Rổ xu hướng trên dữ liệu 30/09: **21 mã (HOSE 17/402, HNX 1/269, UPCoM 3/566)** — HNX và UPCoM chỉ thêm 4 mã, không phải hàng trăm. Ngưỡng 10 tỷ khớp lệnh là nguyên nhân chính.

### 13.4 Đăng ký trước — phép đo P2 (chốt 01/10/2026, TRƯỚC khi chạy)

| Hạng mục | Nội dung |
|---|---|
| Câu hỏi | Bộ lọc xu hướng Tầng 1 trên **toàn thị trường**, **không có** phần chọn của người, có vượt VN-Index không? |
| Biến thể chính | Mỗi kỳ tháng rút **ngẫu nhiên 8 mã** từ danh sách qua Tầng 1 (1.000 lần rút), 1/ATR, trần mã 20%, thoát theo **hai luật xu hướng** (MA200 đệm 3%, RS12T > −5%) + chặn cứng −25%. Biên không giao dịch 3%, phí 0,4%, khớp phiên sau. Luật 4 không mô phỏng được nên bỏ trống |
| Đối chứng phụ | Cùng biến thể, chỉ trên rổ 112 mã HOSE cũ — đo riêng phần đóng góp của việc mở rộng rổ |
| Dữ liệu | Giá đã điều chỉnh từ Vietcap, cửa sổ dài nhất có được, 4 pha lưới |
| Thiên lệch sống sót | `getAll` có 232 mã đã huỷ niêm yết; đưa vào nếu gap-chart còn trả dữ liệu, không thì ghi thành giới hạn. **Chưa kiểm chứng** |
| Ngưỡng | Như P1: **chấp nhận** khi ≥ 3/4 pha dương và t Newey-West ≥ 2; **chưa kết luận** khi 1 ≤ t < 2; **bác bỏ** khi t < 1 |
| Hệ quả nếu bác bỏ | Báo cáo ghi phần máy không có bằng chứng tạo giá trị, toàn bộ gánh nặng chọn mã nằm ở rổ cơ bản. **Không** tự động đổi luật |
| Lịch | Chạy sau 17/10/2026, xong trước kỳ soát 01/11/2026 |

### 13.5 Việc còn mở — CHỜ NGƯỜI

1. **Hôm nay, trước khi quét:** điền `_ro_co_ban` (vĩ mô, ngành, `ngay_chot`) và kết luận `trong_ro` / `nganh` / `uu_tien` cho MSB, BSR, DHC trong `data/tham_dinh.json`.
2. Phiếu V1–V5 + Bước 4 cho mã mới ở giao điểm, hạn **05/10/2026**.
3. Câu hỏi mở từ mục 12.5 (ba trục A/B/C) nay trả lời một phần: tầng doanh nghiệp của rổ dùng **V1–V5**. Ba trục có còn là điều kiện hay không vẫn chưa chốt. → **Đã chốt 04/10/2026: ba trục là điều kiện (mục 14, quyết định 9).**
4. Gộp quy tắc 5 vào luật 4 mới (rút mã khỏi rổ) — xét ở kỳ 01/11, không phải hôm nay. → **Đã giải quyết 04/10/2026: quy tắc 5 bỏ hẳn từ 05/10 (mục 14, quyết định 11).**

⚠️ **Sai lệch quy trình đã biết, ghi cùng ngày:** bản quét sản xuất `data/scan_20261001.json` (chạy 02:47 ngày 01/10) được chạy **trước** khi rổ cơ bản chốt, theo yêu cầu của user, trái với quyết định 4 và 10 vừa chốt cùng ngày. Rổ lập cho kỳ 01/10 vì vậy là rổ lập **sau khi đã thấy rổ xu hướng** 21 mã. Ghi lại để kỳ sau đối chiếu, không phải để bào chữa. Báo cáo: https://claude.ai/artifact/EN4YUxHdLVuK3ReG8fsbbc

**File:** `lt_scan_vietcap.py` (mới), `lt_config.py`, `lt_screener.py`, `lt_allocator.py`, `tests/test_portfolio.py`, `tests/test_canslim.py`, `data/tham_dinh.json` (khung `_ro_co_ban` rỗng). 40/40 test đạt. Sao lưu: `data/CHIEN_LUOC_DAI_HAN_backup_20261001.md`, `data/lt_config_backup_20261001.py`, `data/lt_screener_backup_20261001.py`, `data/lt_allocator_backup_20261001.py`, `data/tham_dinh_backup_20261001.json`.

---

## 14. Khung Giai đoạn 2 — chốt 04/10/2026, hiệu lực từ 05/10/2026

**Nguồn:** báo cáo giai đoạn 1 đã nộp BTC (`medici - mid term report.pdf`, 83 trang, xuất từ Canva ngày 27/09/2026 theo metadata), **Mục 9 "Bài học kinh nghiệm và định hướng giai đoạn 2"** (tr. 69–73). Toàn bộ khung GĐ2 đã công bố ở đó — kể cả câu *"Nếu VN-Index đóng cửa dưới 1,738.84 điểm, Quỹ chuyển toàn bộ sang tiền mặt"* (tr. 72). Ngày 04/10 user cho chất vấn khung này; 17 quyết định dưới đây được chốt (1–5 từng câu một, 6–17 duyệt một lần theo bảng đề xuất). Bản phân tích "góc nhìn giám khảo" (`khung-chien-luoc-giai-doan-2-medici.md`) là tóm tắt của chính Mục 9.

### 14.1 Đối chiếu trước khi quyết — những gì kiểm được

| Báo cáo GĐ1 ghi | Kiểm được (dữ liệu tới 02/10/2026) |
|---|---|
| VN-Index 1.815,66, trên MA200 1,29% → Điều chỉnh | Đó là phiên **18/09**. Đóng cửa 02/10: **1.737,71**; MA200 1.795,65 → ngưỡng 97% = 1.741,78. Dưới cả ngưỡng đó lẫn con số 1.738,84 đã công bố → **chế độ Giảm**. 8 phiên phân phối/25 |
| "Chạy lại trong hơn 12 năm, lớp này cắt sụt giảm tối đa từ 54% xuống 37%; CAGR 6,3% → 5,7%" | **Không có file, script hay dữ liệu nào đứng sau** (đã gỡ khỏi phần lý do ngày 22/09, mục 12.1). Phép đo đăng ký trước của Quỹ cho cổng gần giống (cổng M): CAGR 10,0% → 8,8%, sụt giảm −41,1% → −30,6%, t = −0,41 → bác bỏ |
| Bảng 9.3: VHM 5,85% / MSB 17,87% / DHC 12,06% / BSR 4,98% | VHM đã bán hết 22/09; MSB 840 → 440 và BSR 200 → 100 theo quy tắc 5. Ngày 02/10 cổ phiếu chỉ còn **27,5% NAV** — đã dưới dải 40–60% |
| Hạn 30/09: đối chiếu CASA MSB; lập phiếu BSR | Không có bản ghi nào sau 14/09; BSR chưa có phiếu |
| V1–V5 (tr. 72) | Đánh số lệch phiếu thật (phiếu: V2 kiểm toán, V3 dòng tiền/V3b, V4 bên liên quan, V5 xử phạt/pha loãng); thiếu luật "có trục = 0 → phủ quyết" |
| Bán khi chạm kịch bản Cơ sở | Ngược `khong_co_muc_tieu_chot_lai = True` đang chạy |
| Thận trọng/Cơ sở; DHC mua thêm dưới 35.700 | Dữ liệu chỉ có `co_so`/`upside`; 35.700 = 0,85 × 42,0. DHC 02/10 = 39.000 → biên 7% |
| "Bỏ hẳn quy tắc bán theo cảm quan" (tr. 70) | Quy tắc 5 vẫn dùng ngày 01/10 (50 MSB), ghi sổ 04/10 sau khi khớp |

### 14.2 Mười bảy quyết định

| # | Quyết định | Lý do / bằng chứng |
|---|---|---|
| 1 | **Khung GĐ2 hiệu lực từ 05/10/2026.** Chế độ Giảm bật ở phiên 02/10 → bán toàn bộ MSB/BSR/DHC sáng 05/10, khoá mua mới | Luật và ngưỡng đã công bố trong báo cáo nộp BTC **trước** khi tín hiệu bật → đây là thực hiện cam kết, không phải chọn sau khi thấy kết quả. Người đề xuất ban đầu khuyến nghị lùi tới 01/11; rút lại khi đọc được tr. 72 |
| 2 | **Thoát Giảm có độ trễ:** vào khi đóng cửa < 0,97 × MA200 (ngưỡng tính lại mỗi phiên), chỉ ra khi đóng cửa > MA200; vùng giữa giữ trạng thái trước | Bảng 9.2 hở ở vùng 97–100% MA200. Trên VN-Index 10/2014–10/2026: đối xứng 35 lần vào Giảm, 24 lần < 10 phiên; độ trễ 15 lần, 5 lần < 10 phiên, sụt giảm thấp hơn (14.4). Cùng khoảng lệch 3% Quỹ dùng cho từng mã |
| 3 | **Dải tỷ trọng là trần:** Tăng ≤ 100%, Điều chỉnh ≤ 60%, Giảm 0%. Thiếu mã đạt Trụ 2 → tiền mặt | Cuộc thi chỉ cho mua cổ phiếu → không có ETF để lấp sàn. Hệ quả: cách sửa sai lầm #4 ở tr. 70 phải viết lại trong báo cáo GĐ2 |
| 4 | **Giữ luật bán giá < 97% MA200; bỏ luật RS 12T < −5%** | MA200 là kỷ luật xu hướng, đúng câu "đứng ngoài" tr. 71 và đối xứng với Trụ 1; RS là đà tăng tương đối — bán mã còn rẻ khi chỉ số chạy nhanh hơn, đúng sai lầm #1; chữ L có dấu ngược (−2,0%, t −1,42) |
| 5 | **Bỏ RS > 0 và ATR ≤ 6% ở đầu vào** | Đối xứng với 4. RS loại AAA, NTP, QNS, SBT, VEA, VTZ trên bản quét 01/10 — mã tăng đều nhưng chậm hơn chỉ số. ATR: cam kết #2 tr. 70, không loại mã nào. Rổ xu hướng 01/10: 21 → 29 mã |
| 6 | **Bán toàn bộ khi giá đóng cửa chạm Cơ sở**, như đã công bố. Cơ sở chỉ được nâng bằng phiếu mới dựa trên BCTC mới, ghi trước khi giá chạm | Tr. 72. Bằng chứng cũ "không chốt lời" (56.496 lệnh) đo mục tiêu +3% trong ≤ 20 phiên, không áp thẳng vào giá trị nội tại. Cái giá: cắt sớm doanh nghiệp tăng trưởng |
| 7 | **Hai kịch bản định giá** `than_trong`/`co_so` (nghìn đồng/CP); thiếu một → không mua; Thận trọng ghi rõ từng giả định bất lợi + định giá ngược. **DHC tạm: Thận trọng 42,0 / Cơ sở 51,0, `can_dung_lai = true`** | Báo cáo đã dùng 42,0 làm mốc 35.700 và "biên 13%"; 51,0 là giá mục tiêu phiếu 13/09. Gỡ xung đột 42/51 treo từ 14/09 |
| 8 | **Năm cổng chuẩn = bộ trong phiếu:** V1 cách kiếm tiền · V2 ý kiến kiểm toán · V3 dòng tiền (V3b ngân hàng) · V4 bên liên quan · V5 xử phạt/pha loãng. "Lợi nhuận cốt lõi" (V4 của báo cáo) gộp vào V3: LNST đem so loại lãi đánh giá lại/bất thường | Cả 5 phiếu đã lập (kể cả 3 phủ quyết VHM, STB, BAF) dùng bộ này; tr. 72 mô tả lệch. V3b trả lời một phần rủi ro "loại hết ngân hàng" của góc nhìn giám khảo |
| 9 | **Luật kết luận theo phiếu:** Đạt = tổng ≥ 4 **và không trục nào = 0** và không cổng nào bật; Chờ = không mua mới, đang giữ thì giữ; phiếu quá hạn = chưa thẩm định. **Chỉ phiếu Đạt còn hạn được mua** — nhãn không có phiếu không đủ | Tr. 72 thiếu vế "trục = 0", mà phủ quyết VHM dùng đúng vế đó |
| 10 | **Giữ rổ cơ bản top-down 01/10** làm nhánh người; chốt `ngay_chot` trước bản quét của kỳ đầu tiên thị trường ra khỏi Giảm | Câu kết tr. 73: "vĩ mô sẽ quyết định lợi thế nằm ở ngành nào" |
| 11 | **Bỏ hẳn quy tắc 5 từ 05/10.** Mọi lệnh cần **phiếu lệnh** (`PHIEU_LENH`) ghi kèm giờ, trước giờ đặt | Cam kết #5 tr. 70 |
| 12 | **Nhịp xét:** mỗi phiên (đóng cửa, đặt lệnh phiên sau) — chế độ, −25%, chạm Cơ sở, quy tắc 4 (dây bẫy, xét khi có số liệu); kỳ soát đầu tháng — MA200, cắt về trần, lệnh mua | Ba luật đầu là phép so giá đơn giản và là lớp giữ thành quả; MA200 hằng ngày sẽ nhiễu. Mua chỉ sau kỳ soát — giữ nguyên GĐ1 |
| 13 | **Báo cáo GĐ2 không viết "chiến lược không đổi"**; viết "triết lý và mục tiêu không đổi; GĐ2 thực thi đúng khung đã công bố ở Mục 9" (đoạn mẫu 14.7) | Tr. 71 "triết lý của Quỹ được viết lại", tr. 73 "quyết định đổi chiến lược" — giám khảo đang cầm bản đó. Câu mẫu giữ ý liên tục và kỷ luật mà không mâu thuẫn |
| 14 | **Tự công bố các sai lệch** (14.6) | Tốt hơn để giám khảo tự đối chiếu sổ |
| 15 | **Đính chính dòng "12 năm 54% → 37%"**, thay bằng phép đo tái lập được trên VN-Index (14.4), ghi rõ đo trên chỉ số; script vào repo | Mục 12.1 |
| 16 | **Sau 17/10:** chạy hệ thống cũ trên giấy từ 21/09 và đặt kết quả thật cạnh **E1VFVN30** (chỉ làm thước đo) | Cam kết tr. 73 |
| 17 | Áp cho cả DM1 (đang rỗng) | — |

**Lần đổi luật thứ năm giữa cuộc thi, lần thứ tư do Quỹ chọn** (17/08 đổi khung, 11/09 đổi quy tắc 5, 16/09 thêm mốc soát do BTC đặt, 01/10 top-down, 05/10 khung GĐ2). Khác bốn lần trước ở một điểm phải nói rõ trong báo cáo: **luật và ngưỡng của lần này đã được công bố trong báo cáo nộp BTC trước khi tín hiệu bật** — tín hiệu 02/10, bản PDF xuất 27/09.

**Lựa chọn hiện thực do người đề xuất đặt, user có thể bác:** (a) vùng 97–100% MA200 chỉ được *xấu đi* sang Điều chỉnh (khi MA50 < MA200 hoặc phiên phân phối ≥ 5), không bao giờ *tốt lên* Tăng; (b) ở kỳ soát, phần cổ phiếu vượt trần quá 3% NAV được cắt **theo tỷ lệ** mọi vị thế, giữ cấu trúc 1/ATR; (c) rổ cơ bản chưa chốt thì allocator vẫn sinh lệnh bán theo luật giá và chế độ (trước 04/10 nó dừng hẳn) — không đổi thì lệnh bán 05/10 không in ra được; (d) mua mới cần **cả** nhãn `buoc4 = "dat"` lẫn biên an toàn máy tính; (e) chế độ không xác định được (bản quét cũ thiếu chuỗi VN-Index) → không mua, không bán ép.

### 14.3 Luật đang chạy từ 05/10/2026 — bản gọn

- **Trụ 1 — chế độ** (`CHE_DO`, `lt_che_do.py`): Giảm khi đóng cửa < 0,97 × MA200, ra khi > MA200. Ngoài Giảm: Tăng khi đóng cửa > MA200, MA50 > MA200 và phiên phân phối < 5/25; còn lại Điều chỉnh. Phiên phân phối: VN-Index giảm ≥ 0,2% với khối lượng cao hơn phiên trước. Trần: 100% / 60% / 0%.
- **Đầu vào:** thanh khoản ≥ 10 tỷ/phiên, giá > MA200, MA50 > MA200 — toàn HOSE + HNX + UPCoM.
- **Trụ 2:** rổ cơ bản đã chốt → phiếu Đạt còn hạn → `buoc4 = "dat"` → giá ≤ 0,85 × Thận trọng.
- **Phân bổ:** 1/ATR, trần mã 20% (DM2) / 15% (DM1), trần ngành 40% / 30%, thứ tự `uu_tien` rồi ATR thấp — như cũ — rồi chặn bởi trần chế độ.
- **Bán toàn bộ:** chế độ Giảm · chạm Cơ sở · −25% · quy tắc 4 (mỗi phiên) · giá < 0,97 × MA200 (kỳ soát).
- **Ghi lệnh:** phiếu trước giờ đặt; sau khi khớp ghi sổ. Không còn quy tắc 5.

### 14.4 Bằng chứng: phép đo chế độ trên VN-Index

`kiem_dinh_che_do_vnindex.py` gọi đúng hàm `chuoi_che_do()` đang chạy. Tín hiệu ở giá đóng cửa phiên s, khớp phiên s+1; phí 0,2% mỗi lần đổi tỷ trọng; tiền mặt lãi 0%; VN-Index là chỉ số giá (không gồm cổ tức). Dữ liệu: `data/vnindex_vietcap_20261002.json` (5.660 phiên, 2004–2026). Kết quả: `data/kiem_dinh_che_do_vnindex_20261004.json`.

| 10/2014 – 10/2026 | CAGR | Sụt giảm tối đa | Tỷ trọng TB | Lần vào Giảm | < 10 phiên | Trung vị |
|---|---|---|---|---|---|---|
| Mua và giữ VN-Index | 9,1% | −45,3% | 1,00 | — | — | — |
| **Luật đang chạy: trần 100/60/0, độ trễ** | **6,1%** | **−21,7%** | 0,56 | 15 | 5 | 21 phiên |
| Chỉ lớp Giảm (100/0), độ trễ | 7,0% | −28,1% | 0,71 | 15 | 5 | 21 phiên |
| Chỉ lớp Giảm (100/0), đối xứng | 7,1% | −31,7% | 0,78 | 35 | 24 | 3 phiên |

| 10/2004 – 10/2026 | CAGR | Sụt giảm tối đa | Tỷ trọng TB |
|---|---|---|---|
| Mua và giữ VN-Index | 9,6% | −79,9% | 1,00 |
| Luật đang chạy | 8,5% | −63,4% | 0,53 |
| Chỉ lớp Giảm, độ trễ | 11,3% | −61,9% | 0,67 |

**Đọc đúng phạm vi:**

1. Trên 12 năm, luật đang chạy **cắt sụt giảm tối đa từ −45,3% xuống −21,7%, đổi lại CAGR 9,1% → 6,1%** khi nắm chỉ số theo đúng trần. Đây là con số thay cho "54% → 37%".
2. Phần lớn chênh lệch CAGR đến từ việc nắm trung bình 56% thay vì 100% — đúng đánh đổi đã công bố ("tăng trưởng với rủi ro thấp"). Riêng trần 60% ở Điều chỉnh tốn khoảng 0,8 điểm CAGR (6,95% → 6,11%) để đổi 6,4 điểm sụt giảm (−28,1% → −21,7%).
3. Trên cả 22 năm, chỉ lớp Giảm còn **vượt** mua-và-giữ (11,3% so với 9,6%) vì tránh được phần lớn năm 2008; nhưng sụt giảm vẫn −62%: lớp chế độ không chặn được một thị trường giảm kéo dài có nhiều nhịp hồi lên trên MA200.
4. **Không** phải phép đo hệ thống chọn mã của Quỹ (hệ thống thật thường nắm dưới trần vì thiếu mã đạt Trụ 2); một đường giá, một thị trường, **không đăng ký trước**; không cộng cổ tức (bất lợi cho mua-và-giữ) và không cộng lãi tiền gửi (bất lợi cho lớp chế độ). Là bằng chứng tham khảo, không phải kiểm định.

### 14.5 Lệnh đầu tiên theo khung — 05/10/2026

Bảng lệnh: `data/ke_hoach_20261005.txt` (`NGAY_CHAY=2026-10-05 LOAI_KY=hang_ngay python lt_allocator.py`, bản quét `data/scan_20261004.json`, chế độ `data/che_do_20261004.json`).

| Phiếu | Lệnh | Giá 02/10 | Giá trị | Căn cứ |
|---|---|---|---|---|
| 1 | BÁN 440 MSB | 14.050 | 6.182.000 | chế độ Giảm |
| 2 | BÁN 100 BSR | 30.450 | 3.045.000 | chế độ Giảm + chạm Cơ sở 30.000 |
| 3 | BÁN 200 DHC | 39.000 | 7.800.000 | chế độ Giảm |

NAV 02/10 là 61.805.397 → sau lệnh 100% tiền ≈ 61.774.748 (phí ≈ 30.649). Ba phiếu ghi 04/10 18:57, trước giờ đặt. **Kiểm trước khi đặt:** 140 CP thưởng MSB (GDKHQ 28/08) đã về tài khoản chưa — chưa về thì chỉ bán được 300, phần còn lại bán ngay khi về; 40 CP là lô lẻ. Ra khỏi Giảm khi VN-Index đóng cửa > 1.795,65 (+3,3% so với 02/10).

Hệ quả kéo theo: kế hoạch mua lại 50 VHM của lệnh ngoài luật #1 (hạn 16/10) **hết căn cứ** — VHM bị phủ quyết và chế độ Giảm khoá mua (`LENH_NGOAI_LUAT[0]["ket_thuc"]`).

### 14.6 Sai lệch phải công bố trong báo cáo GĐ2

1. **Quy tắc 5 vẫn được dùng trong giai đoạn 2**, trái với cách sửa #5 báo cáo công bố: 22/09 (300 + 50 MSB, trước ngày xuất PDF 27/09) và 01/10 (50 MSB, sau ngày xuất). Cả bốn lệnh quy tắc 5 (kể cả BSR 16/09) ghi sổ **sau** khi khớp — lệnh 01/10 ghi ngày 04/10.
2. **MSB:** tr. 73 ghi "Giữ, dừng mua thêm" cho kỳ 01/10; thực tế đã bán 400/840 CP trước khi chế độ Giảm bật.
3. **Hai hạn 30/09 không làm:** đối chiếu CASA của MSB, lập phiếu BSR.
4. **Bảng 9.3 đã cũ ngay lúc xuất PDF:** tỷ trọng ngày 18/09, trong khi VHM đã bán hết và MSB đã bán 350 CP ngày 22/09.
5. **Con số 12 năm** ở tr. 69 và tr. 72 không tái lập được (14.4 thay thế).
6. **Đánh số V1–V5** ở tr. 72 lệch phiếu thật; thiếu vế "trục = 0".

### 14.7 Đoạn dùng cho báo cáo giai đoạn 2 (viết cho giám khảo)

> **Kỷ luật đã công bố, thực hiện đúng ngưỡng.** Triết lý và mục tiêu của Quỹ không đổi so với Mục 9 báo cáo giai đoạn 1: doanh nghiệp tốt là điều kiện, giá hợp lý là nguyên tắc, xu hướng xác nhận là kỷ luật; mục tiêu là tăng trưởng với rủi ro thấp. Giai đoạn 2 thực thi đúng khung đã công bố. Ngày 02/10/2026 VN-Index đóng cửa ở 1.737,71 điểm, dưới ngưỡng 1.738,84 điểm đã viết trong báo cáo, và Quỹ chuyển toàn bộ danh mục sang tiền mặt trong phiên 05/10/2026 — kể cả DHC, mã duy nhất đạt 5/6 điểm thẩm định — vì quy tắc không miễn trừ theo mã.

> **Đính chính.** Báo cáo giai đoạn 1 viết rằng lớp chế độ thị trường, chạy lại trong hơn 12 năm, cắt mức sụt giảm tối đa từ 54% xuống 37%. Quỹ không tái lập được con số này từ dữ liệu và mã nguồn của mình, nên rút lại. Phép đo thay thế, tái lập được: nắm VN-Index theo đúng trần của từng chế độ (100% / 60% / 0%) từ 10/2014 đến 10/2026 cắt sụt giảm tối đa từ −45,3% xuống −21,7%, đổi lại tăng trưởng kép giảm từ 9,1% xuống 6,1% một năm. Đây là phép đo trên chỉ số, không phải trên hệ thống chọn cổ phiếu của Quỹ.

> **Làm rõ bốn điểm của khung.** (1) Quỹ chỉ rời chế độ Giảm khi VN-Index đóng cửa trở lại trên MA200, để tránh vào ra liên tục quanh ngưỡng 97%. (2) Dải tỷ trọng là mức trần, không phải mức sàn: cuộc thi chỉ cho phép cổ phiếu, nên khi không đủ mã đạt chuẩn, phần còn lại nằm tiền mặt. Cách sửa sai lầm #4 vì vậy khác điều đã viết ở tr. 70 — bảng chế độ quyết định mức trần, còn tiền mặt dưới trần là lựa chọn đứng ngoài khi thiếu doanh nghiệp đạt chuẩn ở giá hợp lý. (3) Bộ lọc xu hướng giữ điều kiện giá trên MA200 và MA50 trên MA200, bỏ điều kiện sức mạnh tương đối và biến động; mã đang giữ vẫn bị bán khi giá rơi dưới 97% MA200. (4) Năm cổng phủ quyết theo đúng phiếu Quỹ đã lập: cách kiếm tiền, ý kiến kiểm toán, dòng tiền (biến thể riêng cho ngân hàng), bên liên quan, xử phạt và pha loãng; một trục bằng 0 điểm cũng là phủ quyết.

> **Ba rủi ro thực thi.** Bộ lọc quá chặt với ngân hàng: ngân hàng dùng biến thể V3b (lãi và phí phải thu, bao phủ nợ xấu) thay cho phép thử dòng tiền. Độ trễ và nhiễu của đường trung bình: luật ra có độ trễ giảm số lần vào chế độ Giảm trên VN-Index 12 năm từ 35 xuống 15. Tính chủ quan của định giá: mỗi mã có hai kịch bản ghi rõ giả định kèm định giá ngược, và giá trị cơ sở chỉ được nâng khi có báo cáo tài chính mới, ghi trước khi giá chạm.

Kèm bảng sai lệch 14.6.

### 14.8 Việc còn mở

1. **Sau khi khớp 05/10:** ghi giá khớp vào `data/so_giao_dich.json`, sửa `HOLDINGS`/`TIEN_MAT`, đổi trạng thái phiếu 1–3.
2. **Sau 17/10:** hệ thống cũ chạy trên giấy từ 21/09, đặt cạnh E1VFVN30 (quyết định 16); phép thử P2 (13.4) phải **đăng ký lại** vì Tầng 1 đã bỏ RS/ATR.
3. **Trước kỳ soát đầu tiên ngoài chế độ Giảm:** chốt rổ cơ bản; dựng lại hai kịch bản DHC; lập phiếu BSR (hiện chỉ có nhãn); BCTC quý III/2026 của MSB (cuối 10/2026) là tài liệu mở lại phiếu Chờ.
4. Mọi mã trong `tham_dinh.json` trừ DHC chưa có `than_trong` → hiện **không mã nào mua được** dù thị trường có ra khỏi Giảm.

**File:** `lt_che_do.py` (mới), `kiem_dinh_che_do_vnindex.py` (mới), `lt_config.py`, `lt_screener.py`, `lt_allocator.py`, `lt_scan_vietcap.py` (thêm khối `_vnindex`), `tests/test_che_do.py` (mới), `tests/test_portfolio.py`, `tests/test_canslim.py`, `data/tham_dinh.json`; dữ liệu `data/scan_20261004.json`, `data/candidates_20261004.json`, `data/che_do_20261004.json`, `data/ke_hoach_20261005.txt`, `data/vnindex_vietcap_20261002.json`, `data/kiem_dinh_che_do_vnindex_20261004.json`. **55/55 test đạt.** Sao lưu: `data/CHIEN_LUOC_DAI_HAN_backup_20261004.md`, `data/lt_config_backup_20261004b.py`, `data/lt_screener_backup_20261004.py`, `data/lt_allocator_backup_20261004.py`, `data/lt_scan_vietcap_backup_20261004.py`, `data/tham_dinh_backup_20261004.json`, `data/test_portfolio_backup_20261004.py`.
