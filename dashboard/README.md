# Buồng lái Quỹ — dashboard vận hành hằng ngày

Streamlit, **chỉ đọc**. Đọc đầu ra của chuỗi `lt_scan_vietcap.py → lt_screener.py → lt_allocator.py`
trong `data/`, không viết lại luật nào: chế độ, phễu và lệnh lấy nguyên từ file pipeline ghi ra,
hoặc gọi lại hàm có sẵn của `lt_*.py`. Chốt thiết kế ngày 07/10/2026 (buổi chất vấn 7 câu + bảng 19 dòng).

## Chạy

Lần đầu (một lần):

```
uv venv .venv --python 3.12
uv pip install --python .venv/Scripts/python.exe -r requirements.txt pytest
```

Mỗi lần: nhấp đúp `chay_dashboard.bat` → mở http://localhost:8501 (chỉ nghe localhost).

Test: `.venv\Scripts\python -m pytest tests -q` (Python hệ thống không có streamlit sẽ tự bỏ qua
`tests/test_dashboard.py`).

## Bản cloud — Streamlit Community Cloud (repo private `vuthanhtri-a11y/PTDTTC`, nhánh `main`)

- **Chỉ đọc.** Nút Quét / Quét bù / Đẩy lên GitHub chỉ hiện khi mở từ chính máy (`localhost`). Mọi truy cập
  khác là bản chỉ đọc: ổ đĩa cloud bị xoá mỗi lần app khởi động lại nên bản quét chạy trên đó không bao giờ
  về GitHub, và người được mời xem không được kích một lần quét 1.500 request.
- **Số liệu lên cloud:** máy local bấm *Quét phiên hôm nay* → *Đẩy lên GitHub*. Nút này commit **đúng** các
  file pipeline mới (`data/scan_|candidates_|che_do_<8 số>.json`, `ke_hoach_<8 số>.txt`,
  `bao_cao_dau_tu_<8 số>.xlsx`) rồi push lên `main` (đổi bằng biến môi trường `DASHBOARD_NHANH`); Streamlit
  Cloud tự cập nhật sau ~1 phút. Sổ giao dịch, `tham_dinh.json`, `lt_config.py`, `vi_mo.json` vẫn commit tay.
  Chỉ push khi là fast-forward — GitHub có commit mới thì báo `git pull` trước, không ghi đè. Không bao giờ
  đẩy một lần **xoá** file; từ chối nếu máy không ở nhánh `main` hoặc còn commit tay chưa push (tự push trước).
- **Riêng tư:** app từ repo private mặc định private (chỉ developer xem); mời người xem bằng email qua nút
  *Share*. Mỗi tài khoản Community Cloud chỉ có **một** app private.
- **Tạo app:** share.streamlit.io → *Create app* → repo `vuthanhtri-a11y/PTDTTC`, branch `main`, main file
  `dashboard/app.py` → *Advanced settings* → Python **3.12** → Deploy. Đổi Python sau này phải xoá app rồi
  deploy lại. Phụ thuộc: `requirements.txt` ở gốc repo; theme: `.streamlit/config.toml`.
- Máy chủ cloud ở nước ngoài: chuỗi Yahoo tải được; Vietcap (biểu đồ chi tiết mã, VN30/HNX30, đường NAV,
  tên công ty) chưa kiểm từ cloud — lỗi mạng thì phần đó báo không tải được, phần đọc từ bản quét vẫn đúng.

## Giao diện — "Medici Terminal"

Khung Bloomberg terminal (nền tối cố định, thanh lệnh `GO`, dải báo giá, phím chức năng F1–F7, bảng
dày chữ đơn cách, trục giá bên phải), màu chủ đạo đo từ báo cáo Medici giai đoạn 1:

| Vai trò | Màu | Gốc Medici |
|---|---|---|
| Thanh lệnh, nền thương hiệu | `#390A5B` | bìa, trang chương |
| Phím chức năng đang chọn | `#682996` | logo, tiêu đề bảng |
| Nhãn, tiêu đề panel, header bảng | `#BB99FF` | điểm nhấn tím nhạt |
| Chữ số liệu | `#FCF9EA` | chữ kem trên nền tím |
| Nút / điểm tương tác | `#8B5CD6` | (dẫn xuất: 4,25:1 trên nền, chữ trắng 4,57:1) |
| Nền terminal / panel | `#110A1A` / `#170E23` | tím đậm kéo về gần đen |

Phông: Francois One (tiêu đề — phông của báo cáo), IBM Plex Mono (số liệu). Ba màu biểu đồ `#9D7BEA`
`#C98500` `#199E70` đã qua `validate_palette.js` trên nền `#110A1A` (kể cả all-pairs). Token ở đầu
`dashboard/ui.py`; theme Streamlit ở `.streamlit/config.toml` — sửa cả hai cùng lúc.

## Cập nhật số liệu — nút ở thanh bên

| Nút | Chạy | Ghi ra |
|---|---|---|
| **Quét phiên hôm nay** | quét toàn thị trường → screener → allocator nhịp hằng ngày → vĩ mô → tên công ty | `scan_/candidates_/che_do_<ngày dữ liệu>.json`, `ke_hoach_<ngày dữ liệu>.txt`, `bao_cao_dau_tu_<ngày dữ liệu>.xlsx` |
| **Quét bù N phiên** | `lt_scan_vietcap.py --den` + screener cho từng phiên thiếu, **không** allocator | `scan_/candidates_/che_do_<ngày>.json` |
| **Tải lại vĩ mô** | 7 chuỗi Yahoo | `data/cache_dashboard/vi_mo_yahoo.json` |

Cùng chạy được từ dòng lệnh: `.venv\Scripts\python -m dashboard.chay hom_nay | bu 2026-10-05 ... | vi_mo`.

**Tên file theo ngày dữ liệu.** Bản quét do dashboard sinh ra đặt tên theo phiên dữ liệu
(`scan_20261007.json` = phiên 07/10), không theo ngày chạy như quy ước cũ (`scan_20261004.json` chứa
phiên 02/10). Lý do: bản quét bù `--den D` cũng ghi `scan_D.json`, đặt theo ngày chạy sẽ đè nhau. Bộ chạy
**không bao giờ ghi đè** file đang chứa phiên khác — phiên đó hiện "không bù được" (01/10/2026:
`scan_20261001.json` đang chứa phiên 30/09). Bảng lệnh và Excel của allocator cũng đặt theo ngày dữ liệu
(ngày chạy ghi ở dòng đầu bảng lệnh): trước 09/10/2026 chúng đặt theo ngày chạy nên lần chạy phiên 09/10
đè mất bảng lệnh phiên 08/10 (chạy cùng ngày 09/10) — đã khôi phục từ git thành `ke_hoach_20261008.txt`.
Bảng lệnh cũ `ke_hoach_20261005.txt` vẫn chứa phiên 02/10.

Trước 15:00, phiên đang chạy bị bỏ (logic có sẵn của `lt_scan_vietcap.py`) — bản quét chỉ tới phiên trước.
Phiên bù tính phễu bằng `tham_dinh.json` và `HOLDINGS` **hiện tại**, không phải trạng thái ngày đó.

## Bảy tab

| Tab | Nội dung | Nguồn |
|---|---|---|
| Tổng quan | Chế độ, ngưỡng vào/ra Giảm, phiên phân phối, độ rộng, rổ xu hướng (± so phiên trước), NAV, việc phải làm | che_do, candidates, ke_hoach, lt_config |
| Thị trường | VN-Index/VN30/HNX30/E1VFVN30, VN-Index tô nền theo chế độ, độ rộng theo sàn, giá trị khớp 60 phiên, tăng/giảm, biến động mạnh | bản quét + Vietcap |
| Vĩ mô | Kết luận vĩ mô của rổ, 7 chuỗi Yahoo, bảng số VN nhập tay | `_ro_co_ban.vi_mo`, Yahoo, `data/vi_mo.json` |
| Ngành | 19 nhóm ICB cấp 2: độ rộng, lợi suất trung vị, heatmap, thứ hạng, tỷ trọng dòng tiền; ngành rổ (người gán) | bản quét, `_ro_co_ban.nganh` |
| Cổ phiếu | Phễu chính thức 6 tầng (đọc nguyên candidates), lý do rớt, mã đang giữ + checklist bán, rổ cơ bản & phiếu | candidates, tham_dinh |
| Khám phá | Lọc tự do toàn thị trường, tải CSV — **không phải tín hiệu của Quỹ**, không ghi file pipeline | bản quét |
| Danh mục & lệnh | NAV DM2 vs VN-Index/E1VFVN30, bảng lệnh, phiếu lệnh, lãi/lỗ, sổ, chi phí, sổ ngoài luật & quy tắc 5 | so_giao_dich, lt_config, ke_hoach |

Chọn một dòng trong bảng bất kỳ (hoặc ô **Tra mã**) → hộp chi tiết mã: giá 2 năm + MA50/MA200, mức
0,85 × Thận trọng / Thận trọng / Cơ sở, giá vốn và chặn −25%, checklist mua/bán, phiếu V1–V5 + ba trục, dây bẫy.

## Nhập số vĩ mô Việt Nam

Sửa tay `data/vi_mo.json` (hướng dẫn trong `_huong_dan`): thêm kỳ mới vào **cuối** `chuoi` của chỉ số,
ghi `nguon` và `ngay_nhap`. Quá 45 ngày không có kỳ mới → tô vàng. Không điền số khi không có nguồn.

## Những gì dashboard KHÔNG làm / giới hạn đã biết

- Không sửa luật, ngưỡng, rổ, phiếu hay sổ — ghi sổ vẫn làm ngoài app.
- Không có khối ngoại; không có HNX-Index/UPCoM-Index (Vietcap trả rỗng cho mã chỉ số này).
- Phân ngành ICB cấp 2 của Vietcap thô (8700 gộp mọi công ty chứng khoán).
- Đường NAV tái dựng bằng giá Vietcap **đã điều chỉnh**: MSB quy đổi 1,2 trước 28/08 (sự kiện trong sổ);
  sự kiện cổ phiếu ngoài sổ (GMD, sau khi Quỹ bán) đo từ giá khớp/giá điều chỉnh và nhân lại; cổ tức tiền
  (DHC) để lệch vài phần trăm trước ngày GDKHQ. Tiền mặt theo sổ, không gồm lãi tiền gửi/phí lặt vặt.
- Cảnh báo `[HÀNG RÀO]` là của screener, so thời gian sửa file — sau khi checkout git có thể báo sai.
- Bản quét TradingView cũ (112 mã HOSE, không có `_meta`) không hiện trong danh sách phiên.

## Cấu trúc

`nguon.py` (đọc file, phiên, Vietcap) · `thi_truong.py` · `nganh.py` · `vi_mo.py` · `pheu.py` ·
`danh_muc.py` (sổ, NAV, bảng lệnh) · `chay.py` (bộ chạy nút quét) · `ui.py` (định dạng VN, màu, khung
biểu đồ) · `bieu_do.py` · `chi_tiet.py` (hộp chi tiết mã) · `tab_*.py` · `app.py`.
Cache tải lại được ở `data/cache_dashboard/` (gitignore).
