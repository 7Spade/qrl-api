## 09 文檔盤點與分類

**目標**：完整列出文檔、分類用途、標記優先級（core/secondary/appendix/outdated），便於後續維護。

### 盤點結果
| 檔名 | 用途分類 | 優先級 | 備註 |
|------|----------|--------|------|
| 00-Cloud Run Deploy.md | 部署 | core | 原始 Cloud Run 指南，保留原樣 |
| 01-Quickstart-and-Map.md | 快速開始 | core | 5 分鐘啟動與路線圖 |
| 02-System-Overview.md | 架構/資料流 | core | 系統概要與資料權威 |
| 03-Deployment.md | 部署 | core | 本地/Docker/Cloud Run 摘要 |
| 04-Operations-and-Tasks.md | 營運/排程/監控 | core | Scheduler、監控指標 |
| 05-Strategies-and-Data.md | 策略/資料 | core | 屯幣策略、倉位分層、資料來源 |
| 06-API-Compliance-and-Accounts.md | API/合規 | core | MEXC 簽名、子帳號 |
| 07-Fixes-and-Troubleshooting.md | 修復/排障 | core | 核心修復與常見故障 |
| 08-Costs-and-Controls.md | 成本/風控 | core | 成本估算、安全最小化 |
| README.md | 專案總覽 | core | 根目錄主說明 |
| INDEX.md | 導航 | core | 主索引，對應 00–09 |
| 1-qrl-accumulation-strategy.md | 策略詳解 | appendix | 深度案例與程式片段 |
| 2-bot.md | 設計 | appendix | 機器人設計詳述 |
| 3-cost.md | 成本 | appendix | 詳細成本分析 |
| 4-scheduler.md | 排程 | appendix | Scheduler 配置細節 |
| 5-SCHEDULED_TASKS_DESIGN.md | 設計 | appendix | 任務系統設計 |
| 6-ARCHITECTURE_CHANGES.md | 架構 | appendix | 架構變更紀錄 |
| DATA_SOURCE_STRATEGY.md | 資料權威 | appendix | API vs Redis 權威策略 |
| MEXC_API_COMPLIANCE.md | API/合規 | appendix | 官方規格對照 |
| MONITORING_GUIDE.md | 監控 | appendix | 監控與健康檢查詳解 |
| POSITION_LAYERS.md | 策略/倉位 | appendix | 分層資料結構與前端展示 |
| SUB_ACCOUNT_GUIDE.md | API/子帳號 | appendix | 子帳號用法與錯誤處理 |
| TROUBLESHOOTING.md | 排障 | appendix | 詳細故障處理 |
| mexc-dev-url.md | 參考 | appendix | 官方連結彙整 |

### 標準化與維護建議
- 仍有用的深度內容標記為 appendix；無過時項目需移除的暫無。  
- 新增文檔時請跟隨 `NN-Title.md` 命名（核心）或放入 appendix 區。  
- 每月快速檢查：新增檔是否登錄在此表、是否符合語氣與 H2 開頭。  
