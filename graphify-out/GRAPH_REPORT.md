# Graph Report - claude code for tradingview  (2026-09-06)

## Corpus Check
- 142 files · ~175,362 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 689 nodes · 1360 edges · 41 communities (30 shown, 8 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 32 edges (avg confidence: 0.8)
- Token cost: 284,163 input · 31,573 output

## Community Hubs (Navigation)
- Chiến lược dài hạn & báo cáo DM2
- Khung cũ: mô phỏng & luật thoát
- Phân bổ & sàng lọc danh mục
- Tài liệu & kỹ năng TradingView MCP
- Đăng ký công cụ MCP (tool registry)
- Nhân tố FF5 & xuất Excel TSSL
- Khởi chạy & kiểm tra sức khỏe CDP
- Quản lý tab & script Pine (CLI)
- Manifest gói npm
- Phát triển Pine & tự động hóa UI
- Bộ định tuyến CLI
- Điều khiển biểu đồ
- Đọc dữ liệu giá & chỉ báo
- Streaming poll-and-diff
- Dựng báo cáo FF5 (Word)
- Kết nối CDP & chụp màn hình
- Bar Replay
- Cảnh báo & pane
- Quét hàng loạt & vẽ hình
- Backtest phạm vi (scope)
- Backtest trên TradingView
- Quét mã qua TradingView
- Thêm & cấu hình chỉ báo
- Khung cũ: dựng báo cáo
- Dựng báo cáo DM (Word)
- Proxy nhân tố FF5
- Watchlist
- Khung cũ: mô phỏng cuối
- Kiểm thử CLI
- Khung cũ: mô phỏng cuộc thi
- Kiểm định chế độ thị trường
- CI pipeline
- Sao lưu lt_config 25/08
- Sao lưu lt_config 02/09
- Sao lưu lt_config 03/09
- Sao lưu lt_config 04/09
- Script khởi chạy Linux
- Script khởi chạy macOS

## God Nodes (most connected - your core abstractions)
1. `evaluate()` - 94 edges
2. `jsonResult()` - 29 edges
3. `safeString()` - 26 edges
4. `getClient()` - 25 edges
5. `evaluateAsync()` - 21 edges
6. `register()` - 16 edges
7. `Luật thoát — bốn quy tắc giữ tiếp (Bảng CL.4)` - 13 edges
8. `Tool Selection Decision Tree` - 13 edges
9. `Chiến lược đầu tư dài hạn (khung 17/08/2026)` - 12 edges
10. `scripts` - 11 edges

## Surprising Connections (you probably didn't know these)
- `Trượt giá thực hiện so với giá đóng cửa (chỉ số theo dõi)` --semantically_similar_to--> `Vòng rửa (bán rồi mua lại cùng mã) và cơ chế bù trừ lệnh`  [INFERRED] [semantically similar]
  bao_cao_dm2_20260819.html → CHIEN_LUOC_DAI_HAN.md
- `Backup chiến lược 02/09/2026 (trước khi bỏ trần trùng lặp)` --conceptually_related_to--> `Chiến lược đầu tư dài hạn (khung 17/08/2026)`  [EXTRACTED]
  data/CHIEN_LUOC_DAI_HAN_backup_20260902.md → CHIEN_LUOC_DAI_HAN.md
- `Cuộc thi đầu tư (8 người, 2 tháng, kết thúc 17/10/2026)` --conceptually_related_to--> `Hàm mục tiêu E[log NAV] — tốc độ gộp vốn dài hạn`  [INFERRED]
  bao_cao_dm2_20260819.html → CHIEN_LUOC_DAI_HAN.md
- `Báo cáo DM2 — 29/08/2026` --references--> `Trần trùng lặp 10% tổng hai tài khoản (đã bỏ 02/09/2026)`  [EXTRACTED]
  bao_cao_dm2_20260829.html → CHIEN_LUOC_DAI_HAN.md
- `Trần trùng lặp 10% tổng hai tài khoản (đã bỏ 02/09/2026)` --conceptually_related_to--> `Ô VIC treo suốt cuộc thi (1 lô = 33,7% NAV DM2 > trần 20%)`  [INFERRED]
  CHIEN_LUOC_DAI_HAN.md → bao_cao_dm2_20260819.html

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Bộ lọc cứng Tầng 1 — 5 điều kiện (Bảng CL.1)** — chien_luoc_dai_han_bo_loc_thanh_khoan, chien_luoc_dai_han_bo_loc_ma200, chien_luoc_dai_han_bo_loc_ma50_ma200, chien_luoc_dai_han_rs_12_thang_skip_month, chien_luoc_dai_han_chan_atr [EXTRACTED 1.00]
- **Luật thoát Bảng CL.4 — bốn quy tắc giữ tiếp + chặn cứng −25%** — chien_luoc_dai_han_quy_tac_thoat_1_ma200, chien_luoc_dai_han_quy_tac_thoat_2_rs12t, chien_luoc_dai_han_quy_tac_thoat_3_thu_hang, chien_luoc_dai_han_quy_tac_thoat_4_luan_diem, chien_luoc_dai_han_chan_cung_25 [EXTRACTED 1.00]
- **Đo lại 4 pha lưới 26/08 đảo ngược các kết luận thiết kế cũ** — chien_luoc_dai_han_do_lai_4_pha_luoi, chien_luoc_dai_han_backtest_13_89, chien_luoc_dai_han_so_o, chien_luoc_dai_han_phan_bo_1_atr, chien_luoc_dai_han_pham_vi_a_b1_b2 [EXTRACTED 1.00]
- **Pine Script agent development loop** — tradingview_mcp_skills_pine_develop_skill, tradingview_mcp_skills_pine_develop_skill_compile_loop, tradingview_mcp_claude_pine_development_tools, tradingview_mcp_research_pine_as_agent_output, tradingview_mcp_research_finding_pine_strongest [EXTRACTED 0.85]
- **Compact-by-default context management strategy** — tradingview_mcp_claude_context_management_rules, tradingview_mcp_claude_decision_tree, tradingview_mcp_claude_pine_graphics_tools, tradingview_mcp_research_context_window_constraint, tradingview_mcp_research_finding_context_primary [INFERRED 0.85]
- **Local CDP bridge to TradingView Desktop** — tradingview_mcp_readme_bridge, tradingview_mcp_claude_cdp_bridge_architecture, tradingview_mcp_security_policy, tradingview_mcp_setup_guide_install_flow, tradingview_mcp_claude_connection_tools [EXTRACTED 0.85]

## Communities (41 total, 8 thin omitted)

### Community 0 - "Chiến lược dài hạn & báo cáo DM2"
Cohesion: 0.06
Nodes (65): Báo cáo DM2 — 18/08/2026, Báo cáo DM2 — 19/08/2026, Báo cáo DM2 — 26/08/2026, Báo cáo DM2 — 29/08/2026, Báo cáo DM2 — 03/09/2026, Báo cáo DM2 — 04/09/2026, Chiến lược đầu tư dài hạn (khung 17/08/2026), Backtest lịch sử 13,89%/năm, sụt giảm −21,3%, t=0,87 (BẢN GHI ĐÃ BỊ THAY THẾ) (+57 more)

### Community 1 - "Khung cũ: mô phỏng & luật thoát"
Cohesion: 0.05
Nodes (51): allocate(), Candidate, cap_weights(), effective_tau(), allocator.py — Phan bo danh muc theo softmax(ER) cho cuoc thi dau tu 2 thang.…, Mot ung vien. price_k = gia theo NGHIN dong (nhu bang gia HOSE)., p toi thieu de ER > 0., TAU thuc te. Che do 'scaled' neo vao do phan tan cua ER nen muc do tap trung… (+43 more)

### Community 2 - "Phân bổ & sàng lọc danh mục"
Cohesion: 0.05
Nodes (56): chon(), eligible(), export_excel(), khoi_luong(), main(), nav(), lt_allocator.py — Phan bo danh muc dai han theo RUI RO NGANG NHAU (risk parity…, Lam tron ve lo GAN NHAT (khong phai lam tron xuong) roi kiem tra tran. Lam tron… (+48 more)

### Community 3 - "Tài liệu & kỹ năng TradingView MCP"
Cohesion: 0.05
Nodes (46): claude agent (connectivity / health-check assistant), performance-analyst agent, Alert Management tool family, batch_run multi-symbol scanner, CDP Bridge Architecture (MCP stdio to Electron via port 9222), Chart Control tool family, Chart Reading tool family, Connection Management tool family (tv_launch / tv_health_check / tv_discover) (+38 more)

### Community 4 - "Đăng ký công cụ MCP (tool registry)"
Cohesion: 0.13
Nodes (20): REPO_ROOT, _resolve(), update(), server, transport, registerAlertTools(), registerBatchTools(), registerCaptureTools() (+12 more)

### Community 5 - "Nhân tố FF5 & xuất Excel TSSL"
Cohesion: 0.10
Nodes (32): DataFrame, Series, dung_nhan_to(), _gan_nhom(), hoi_quy_ff5(), kiem_tra(), _lay(), main() (+24 more)

### Community 6 - "Khởi chạy & kiểm tra sức khỏe CDP"
Cohesion: 0.08
Nodes (26): getTargetInfo(), checkForUpdate(), _copyMsixPackageLocal(), discover(), healthCheck(), launch(), _resolveLaunchDeps(), _spawnDetached() (+18 more)

### Community 7 - "Quản lý tab & script Pine (CLI)"
Cohesion: 0.09
Nodes (23): chrome-remote-interface, outPath, t, targets, escaped, src, srcPath, t (+15 more)

### Community 8 - "Manifest gói npm"
Cohesion: 0.07
Nodes (27): eslint, @modelcontextprotocol/sdk, bin, tv, dependencies, chrome-remote-interface, @modelcontextprotocol/sdk, description (+19 more)

### Community 9 - "Phát triển Pine & tự động hóa UI"
Cohesion: 0.18
Nodes (23): evaluate(), getClient(), compile(), ensurePineEditorOpen(), getConsole(), getErrors(), getSource(), newScript() (+15 more)

### Community 10 - "Bộ định tuyến CLI"
Cohesion: 0.20
Nodes (7): commands, execute(), handleError(), printCommandHelp(), printHelp(), register(), run()

### Community 11 - "Điều khiển biểu đồ"
Cohesion: 0.20
Nodes (14): requireFinite(), getState(), getVisibleRange(), manageIndicator(), _resolve(), scrollToDate(), setSymbol(), setTimeframe() (+6 more)

### Community 12 - "Đọc dữ liệu giá & chỉ báo"
Cohesion: 0.19
Nodes (17): buildGraphicsJS(), ensureStrategyTesterReady(), getDepth(), getEquity(), getIndicator(), getOhlcv(), getPineBoxes(), getPineLabels() (+9 more)

### Community 13 - "Streaming poll-and-diff"
Cohesion: 0.23
Nodes (16): fetchAllPanes(), fetchLabels(), fetchLastBar(), fetchLines(), fetchQuote(), fetchTables(), fetchValues(), pollLoop() (+8 more)

### Community 14 - "Dựng báo cáo FF5 (Word)"
Cohesion: 0.23
Nodes (15): build(), bullets(), hop(), nhap_ff5(), para(), So kieu Viet: dau phay thap phan. VD vn(9.0512, 2) -> '9,05'., Tien dong kieu Viet: dau cham phan cach hang nghin., Hop luu y co vien, dung cho cac canh bao phuong phap. (+7 more)

### Community 15 - "Kết nối CDP & chụp màn hình"
Cohesion: 0.21
Nodes (12): connect(), findChartTarget(), findTargetById(), getBottomBar(), getChartCollection(), getMainSeriesBars(), KNOWN_PATHS, verifyAndReturn() (+4 more)

### Community 16 - "Bar Replay"
Cohesion: 0.39
Nodes (13): getReplayApi(), autoplay(), _resolve(), start(), status(), step(), stop(), trade() (+5 more)

### Community 17 - "Cảnh báo & pane"
Cohesion: 0.19
Nodes (12): evaluateAsync(), CONDITION_TYPE_MAP, create(), deleteAlerts(), list(), focus(), LAYOUT_NAMES, list() (+4 more)

### Community 18 - "Quét hàng loạt & vẽ hình"
Cohesion: 0.26
Nodes (9): getChartApi(), safeString(), batchRun(), __dirname, SCREENSHOT_DIR, drawShape(), getProperties(), removeOne() (+1 more)

### Community 19 - "Backtest phạm vi (scope)"
Cohesion: 0.38
Nodes (10): fwd(), ma(), mom(), prank(), px(), r2(), run(), snapshot() (+2 more)

### Community 20 - "Backtest trên TradingView"
Cohesion: 0.44
Nodes (10): fwd(), ma(), mom(), prank(), px(), r2(), run(), snapshot() (+2 more)

### Community 21 - "Quét mã qua TradingView"
Cohesion: 0.31
Nodes (5): bars(), grab(), metrics(), sig(), sleep()

### Community 22 - "Thêm & cấu hình chỉ báo"
Cohesion: 0.50
Nodes (8): addStudyFromSearch(), closeDialog(), delay(), openDialog(), searchStudies(), setInputs(), toggleVisibility(), typeQuery()

### Community 23 - "Khung cũ: dựng báo cáo"
Cohesion: 0.43
Nodes (7): build(), bullets(), para(), build_report.py — Sinh khung bao cao .docx tu ket qua phan tich. Moi bang so…, setup_styles(), table(), todo()

### Community 24 - "Dựng báo cáo DM (Word)"
Cohesion: 0.43
Nodes (7): build(), bullets(), para(), build_report.py — Sinh khung bao cao .docx tu ket qua phan tich. Moi bang so…, setup_styles(), table(), todo()

### Community 25 - "Proxy nhân tố FF5"
Cohesion: 0.33
Nodes (5): bootstrap_10tuan(), cv_frames(), BO NHAN TO PROXY — thay cho chuoi nhan to khong quan sat duoc sau 07/2021. Y…, Hon hop theo TUNG nhan to: voi xac suat w*_c lay khoi tu 5 nam tuong dong, con…, trong_so_toi_uu()

### Community 26 - "Watchlist"
Cohesion: 0.57
Nodes (6): add(), addBulk(), ensureWatchlistOpen(), get(), getActiveListInfo(), remove()

### Community 27 - "Khung cũ: mô phỏng cuối"
Cohesion: 0.40
Nodes (3): final_sim.py — P(ve nhat) voi tham so DO DUOC tu 56.496 lenh mo phong…, Mo phong CYCLES vong; moi vong rut che do thi truong roi rut 4 ket qua tuong…, simulate()

### Community 30 - "Kiểm định chế độ thị trường"
Cohesion: 0.50
Nodes (3): cluster_boot(), regime_test.py — Kiem dinh luat thoat tren 56.496 lenh mo phong, 8 nam, 30 ma.…, Bootstrap gop cum theo ma: lay mau lai 30 ma, tinh trung binh co trong so.

### Community 31 - "CI pipeline"
Cohesion: 0.67
Nodes (3): Unit tests exclude e2e (needs live TradingView + CDP), CI Pipeline (lint + unit tests), _deps / _resolve testability pattern

## Knowledge Gaps
- **76 isolated node(s):** `name`, `version`, `description`, `type`, `main` (+71 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 206 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `evaluate()` connect `Phát triển Pine & tự động hóa UI` to `Khởi chạy & kiểm tra sức khỏe CDP`, `Điều khiển biểu đồ`, `Đọc dữ liệu giá & chỉ báo`, `Streaming poll-and-diff`, `Kết nối CDP & chụp màn hình`, `Bar Replay`, `Cảnh báo & pane`, `Quét hàng loạt & vẽ hình`, `Thêm & cấu hình chỉ báo`, `Watchlist`?**
  _High betweenness centrality (0.064) - this node is a cross-community bridge._
- **Why does `chrome-remote-interface` connect `Quản lý tab & script Pine (CLI)` to `Manifest gói npm`, `Kết nối CDP & chụp màn hình`?**
  _High betweenness centrality (0.054) - this node is a cross-community bridge._
- **What connects `name`, `version`, `description` to the rest of the system?**
  _76 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Chiến lược dài hạn & báo cáo DM2` be split into smaller, more focused modules?**
  _Cohesion score 0.0625 - nodes in this community are weakly interconnected._
- **Should `Khung cũ: mô phỏng & luật thoát` be split into smaller, more focused modules?**
  _Cohesion score 0.051715309779825906 - nodes in this community are weakly interconnected._
- **Should `Phân bổ & sàng lọc danh mục` be split into smaller, more focused modules?**
  _Cohesion score 0.05367231638418079 - nodes in this community are weakly interconnected._
- **Should `Tài liệu & kỹ năng TradingView MCP` be split into smaller, more focused modules?**
  _Cohesion score 0.05410628019323672 - nodes in this community are weakly interconnected._