## 10 文檔優化與壓縮摘要

### 原則與範圍
- 採用 **semantic-equivalent minimization**：刪減冗餘、保留決策與責任；不新增概念。
- **權威閱讀集**：INDEX + 00–09 + 本檔。其餘附錄僅供歷史追溯，不作為日常依據。
- 變更僅更新導航與壓縮摘要，避免擾動已驗證的核心說明。

### 原始索引（路徑/大小/時間）
所有列出的檔案皆位於 `docs/`，格式為 Markdown。
### 核心（00–09 + INDEX）
| 檔案 | 大小 | 修改日 |
|------|------|--------|
| 00-Cloud Run Deploy.md | 2.7KB | 2025-12-28 |
| 01-Quickstart-and-Map.md | 1.8KB | 2025-12-28 |
| 02-System-Overview.md | 2.3KB | 2025-12-28 |
| 03-Deployment.md | 3.5KB | 2025-12-28 |
| 04-Operations-and-Tasks.md | 2.2KB | 2025-12-28 |
| 05-Strategies-and-Data.md | 1.9KB | 2025-12-28 |
| 06-API-Compliance-and-Accounts.md | 1.7KB | 2025-12-28 |
| 07-Fixes-and-Troubleshooting.md | 2.1KB | 2025-12-28 |
| 08-Costs-and-Controls.md | 1.6KB | 2025-12-28 |
| 09-Doc-Inventory.md | 2.3KB | 2025-12-28 |
| INDEX.md | 2.8KB | 2025-12-28 |
| 10-Doc-Optimization.md | 5.7KB | 2025-12-28 |

### 附錄（歷史/深度，已壓縮）
| 檔案 | 大小 | 修改日 |
|------|------|--------|
| 1-qrl-accumulation-strategy.md | 37.1KB | 2025-12-28 |
| 2-bot.md | 57.2KB | 2025-12-28 |
| 3-cost.md | 12.3KB | 2025-12-28 |
| 4-scheduler.md | 8.0KB | 2025-12-28 |
| 5-SCHEDULED_TASKS_DESIGN.md | 11.0KB | 2025-12-28 |
| 6-ARCHITECTURE_CHANGES.md | 10.9KB | 2025-12-28 |
| DATA_SOURCE_STRATEGY.md | 6.0KB | 2025-12-28 |
| MEXC_API_COMPLIANCE.md | 5.5KB | 2025-12-28 |
| MONITORING_GUIDE.md | 7.4KB | 2025-12-28 |
| POSITION_LAYERS.md | 4.6KB | 2025-12-28 |
| README.md | 57.2KB | 2025-12-28 |
| SUB_ACCOUNT_GUIDE.md | 8.0KB | 2025-12-28 |
| TROUBLESHOOTING.md | 8.6KB | 2025-12-28 |
| mexc-dev-url.md | 0.8KB | 2025-12-28 |

### 分類與重疊（壓縮決策）
- 核心 00–09 已涵蓋快速導覽、部署、營運、策略、合規、成本、修復；保持不動。
- 本檔提供附錄的**唯一壓縮版行為準則**；原附錄改為「archive」，僅在需要原始細節時查閱。
- 對應關係：
  - **策略/倉位**：`1-qrl-accumulation-strategy.md`、`POSITION_LAYERS.md` → 以 05 + 本檔摘要為準。
  - **排程/設計**：`4-scheduler.md`、`5-SCHEDULED_TASKS_DESIGN.md` → 以 04 + 本檔節奏為準。
  - **資料權威**：`DATA_SOURCE_STRATEGY.md` → 以 05/07 + 本檔規則為準。
  - **合規/帳戶**：`MEXC_API_COMPLIANCE.md`、`SUB_ACCOUNT_GUIDE.md` → 以 06 + 本檔簡表為準。
  - **監控/修復**：`MONITORING_GUIDE.md`、`6-ARCHITECTURE_CHANGES.md`、`TROUBLESHOOTING.md` → 以 07 + 本檔排障順序為準。

### 壓縮摘要（決策與責任）
### 交易與倉位
- 餘額權威：MEXC `/account/balance`，僅在 API 失敗且 Redis 有值時短暫 fallback；Dashboard 不得用 Redis 覆蓋 API 餘額。
- 成本/盈虧權威：Redis `cost_data`；`/status` 需合併 position + cost，平均成本採加權計算並持久化。
- 倉位分層：`bot:QRLUSDT:position:layers` 內含 core/swing/active；賣出不得觸碰 core，API `/status` 可回傳 `position_layers`。
- 原始回應：保留 `mexc:raw:*` 供審計與重算。

### 排程與任務
- 價格：每 10s 更新 `price:latest`（永久）、`price:cached`（≈30s TTL），並記錄歷史。
- 餘額同步：每 30s 取 API，寫入 `bot:QRLUSDT:position`（含時間戳）。
- 成本刷新：每 1 分鐘以最新價格重算 unrealized/avg_cost。
- 策略執行：預設每 5 分鐘；需 `bot_status=running`，並檢查每日次數、最小間隔與風控上限。
- 認證：Cloud Scheduler 可用 `X-CloudScheduler` 或 OIDC Bearer；日誌需標註來源。

### 合規與帳戶
- 簽名遵循 MEXC V3；遵守 20 rps 上限並重試退避。
- 子帳戶操作須 Broker API Key；401/403 先檢查角色與 audience，必要時刷新 Broker 列表。
- 憑證僅來自環境變數；禁止寫入倉庫。

### 監控與排障
- 健康檢查：`/health` 覆蓋 Redis/MEXC 連線；失敗時先檢查雲端日誌。
- 連線壽命：FastAPI lifespan 管理 Redis 連線池並確保 `aclose()`。
- TTL 檢查：`price:latest` 應為 -1；`price:cached` 為 0–30s；缺失時先重觸發價格任務。
- 排障順序：health → Cloud Task/Run 日誌 → `mexc:raw:*` → `/account/balance` 簽名與權限 → 需要時再查舊附錄。

### 最小集合（優化後）
- 日常閱讀：INDEX + 00–09 + 本檔即覆蓋決策、權責、節奏、風控。
- 附錄：標記為 archive/歷史；如需程式片段或完整案例才查閱。
- 新增內容優先合併到既有 NN 檔或本檔的對應章節，避免平行版本。

### 指標
- **Before（核心 + 附錄，不含本檔）**：約 26,406 詞，core 1,992 vs appendix 24,414；閱讀成本集中在附錄。
- **Optimized Canonical Set**：core 1,992 + 本檔 459 ≈ 2,451 詞；相對於原附錄（24,414 詞）日常閱讀量下降約 90%。
- 檔案仍保留供審計；實際參考集已縮小至精簡集合。

### 等效驗證
- 覆蓋範圍：資料權威、倉位分層、價格/餘額/成本更新節奏、策略執行前置條件、MEXC 合規、子帳號要求、監控與排障流程。
- 未引入新概念，僅刪除冗餘敘述；如需細節可回看對應附錄。
- 變更前後決策與責任一致：誰是權威資料、何時更新、誰負責簽名/權限、如何排障皆保持不變。

### 防膨脹維護
- 新增文檔需標註核心/歷史，並更新 09/本檔索引；若字數增加需附壓縮版本。
- 優先修改既有 NN 檔或本檔章節；禁止另開平行敘述。
- 每月檢查：若核心已涵蓋新資訊，請合併並在附錄標註來源，再將原新稿轉為 archive。
- PR 審核：若引入新長文，需同時提交對應壓縮段落與更新的分類表。此流程即為持續「Anti-bloat」守則。
