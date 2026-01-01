# Cloud Scheduler 15-min-job + Rebalance Integration 討論文檔

## 📚 文檔索引

本次任務的完整文檔已創建，包含三個主要文件：

### 1. [ADR-001-Rebalance-Integration-15min-Job.md](./ADR-001-Rebalance-Integration-15min-Job.md)
**架構決策記錄（Architectural Decision Record）**

📋 **內容：**
- 背景與需求說明
- Rebalance 邏輯完整說明（輸入、計算、輸出）
- 三種整合方案詳細比較
  - 方案 A：HTTP 內部調用
  - 方案 B：直接引入 RebalanceService
  - 方案 C：共享模組化方法（**推薦**）
- 實施計劃（5 個階段）
- 風險與緩解措施
- 監控與日誌建議
- Cloud Scheduler 配置範例

🎯 **適合對象：**
- 架構師、技術決策者
- 需要了解為什麼選擇某種方案
- 需要完整實施計劃的開發者

### 2. [ADR-001-Architecture-Diagrams.md](./ADR-001-Architecture-Diagrams.md)
**架構圖與視覺化說明**

📊 **內容：**
- 當前架構 vs 目標架構對比（ASCII 圖）
- Rebalance 邏輯完整流程圖
- 詳細數據流圖
- 共享模組結構設計
- 錯誤處理流程圖
- 完整時序圖
- 關鍵決策點分析
- 後續優化機會

🎯 **適合對象：**
- 視覺化學習者
- 需要快速理解系統架構
- Code Review 參考
- 新團隊成員快速上手

### 3. [ADR-001-Rebalance-Logic-Deep-Dive.md](./ADR-001-Rebalance-Logic-Deep-Dive.md)
**再平衡邏輯深度解析**

🔍 **內容：**
- 核心概念詳細說明（什麼是對稱再平衡？）
- 完整算法逐步解析（包含代碼和數學公式）
- 詳細決策樹分析
- 5 個真實案例場景
  - 案例 1：價格上漲，賣出 QRL
  - 案例 2：價格下跌，買入 QRL
  - 案例 3：資金不足處理
  - 案例 4：閾值保護機制
  - 案例 5：（更多...）
- 參數調優完整指南
  - target_ratio (目標比率)
  - min_notional_usdt (最小交易額)
  - threshold_pct (偏差閾值)
  - 推薦配置矩陣
- 風險考量與緩解措施
  - 滑點風險
  - 市場深度不足
  - 頻繁交易手續費
  - 極端市場條件
  - 部分成交風險
- 優化建議
  - TWAP 分層執行
  - 價格預測整合
  - 多級閾值系統
  - 成本基礎追蹤
  - 回測系統

🎯 **適合對象：**
- 需要深入理解再平衡邏輯的開發者
- 量化策略研究者
- 參數調優工作
- 風險管理評估

## 📝 問題陳述（原始需求）

> 如何實現Cloud Scheduler > src\app\interfaces\tasks\15-min-job.py然後一併觸發src\app\interfaces\tasks\rebalance.py
> 先不動代碼 先在RP討論好同時把rebalance.py 的整個再平衡邏輯拿出來討論

## ✅ 已完成工作

### 階段 1：文檔與討論（已完成）
- [x] 分析現有代碼庫結構
- [x] 記錄當前 15-min-job 實現
- [x] 記錄 rebalance.py 實現
- [x] 提取並記錄完整再平衡邏輯
- [x] 創建架構決策文檔（3 份）

### 創建的文檔（共 ~40KB）：
1. **ADR-001-Rebalance-Integration-15min-Job.md** (9KB)
   - 架構決策記錄
   - 方案比較與推薦

2. **ADR-001-Architecture-Diagrams.md** (14KB)
   - 完整的視覺化架構圖
   - 數據流和時序圖

3. **ADR-001-Rebalance-Logic-Deep-Dive.md** (18KB)
   - 算法深度解析
   - 案例分析與優化建議

## 🎯 核心發現與建議

### 當前系統狀態

**15-min-job.py** (簡單 keepalive)
```python
@router.post("/runtime")
async def runtime_keepalive():
    return {"success": True, "message": "15-min-job"}
```

**rebalance.py** (完整再平衡邏輯)
```python
@router.post("/rebalance/symmetric")
async def task_rebalance_symmetric(...):
    # 認證檢查
    # Redis 連接
    # 調用 RebalanceService
    # 返回計劃
```

### 推薦方案：共享模組化方法

**為什麼？**
- ✅ 代碼重用性高（認證、連接邏輯共享）
- ✅ 性能優化（直接調用，無 HTTP 開銷）
- ✅ 易於維護（單一職責原則）
- ✅ 易於測試（各模組獨立）
- ✅ 可擴展性強（未來任務受益）

**架構概覽：**
```
src/app/interfaces/tasks/
├── shared/
│   └── task_utils.py          # 共享工具
│       ├── require_scheduler_auth()
│       ├── ensure_redis_connected()
│       └── handle_task_error()
│
├── 15-min-job.py              # 更新後整合再平衡
├── rebalance.py               # 可選：使用共享模組
└── router.py
```

## 🔄 Rebalance 邏輯摘要

**目標：** 維持 QRL 和 USDT 的**價值**比例為 50:50

**關鍵參數：**
- `target_ratio = 0.5` (50%)
- `min_notional_usdt = 5.0` (最小交易 5 USDT)
- `threshold_pct = 0.01` (1% 偏差閾值)

**決策流程：**
1. 計算總價值：`total = qrl * price + usdt`
2. 計算偏差：`delta = qrl_value - target_value`
3. 判斷動作：
   - HOLD：價格無效、偏差過小
   - SELL：QRL 價值過高（delta > 0）
   - BUY：QRL 價值過低（delta < 0）

**示例：**
```
初始：100 QRL @ 1 USDT + 100 USDT (50:50 ✅)
價格漲至 2 USDT：
  → QRL 價值 200 USDT, USDT 100 USDT (67:33 ❌)
  → 賣出 25 QRL
  → 結果：75 QRL @ 2 + 150 USDT (50:50 ✅)
```

## ❓ 待討論問題

以下問題需要團隊決策：

1. **執行順序**
   - Q: Rebalance 應該在成本/損益更新之前還是之後執行？
   - A: 建議：先更新成本，後執行再平衡（使用最新數據）

2. **錯誤處理**
   - Q: 如果 rebalance 失敗，是否應該阻止整個 15-min-job 完成？
   - A: 建議：隔離錯誤，記錄但不阻斷（各任務獨立）

3. **認證策略**
   - Q: 兩個操作是否使用相同的認證檢查？
   - A: 建議：共享認證邏輯（提取到 task_utils）

4. **日誌詳細度**
   - Q: 組合操作的日誌應該多詳細？
   - A: 建議：結構化 JSON 日誌，包含各階段執行時間和結果

5. **計劃儲存**
   - Q: 是否分別儲存成本更新和再平衡計劃？
   - A: 建議：分別儲存到不同 Redis key，便於追蹤

6. **Cloud Scheduler 配置**
   - Q: 保留獨立的 rebalance job 還是整合？
   - A: 建議：整合到 15-min-job，保留 rebalance 端點作為手動觸發備用

## 📋 下一步行動

### 階段 2：團隊討論（當前階段）
- [ ] 審查三份 ADR 文檔
- [ ] 回答上述 6 個討論問題
- [ ] 確認推薦方案或提出替代方案
- [ ] 批准實施計劃

### 階段 3：實施準備
- [ ] 創建共享工具模組
- [ ] 編寫單元測試框架
- [ ] 準備測試環境

### 階段 4：代碼實現
- [ ] 實現共享認證和連接邏輯
- [ ] 更新 15-min-job.py
- [ ] （可選）重構 rebalance.py 使用共享模組
- [ ] 編寫完整測試

### 階段 5：部署與監控
- [ ] 更新 `docs/04-Operations-and-Tasks.md`
- [ ] 配置監控指標
- [ ] 部署到測試環境
- [ ] 驗證後部署到生產環境

## 📚 參考資源

### 代碼位置
- `src/app/interfaces/tasks/15-min-job.py` - 當前 keepalive 端點
- `src/app/interfaces/tasks/rebalance.py` - 再平衡端點
- `src/app/application/trading/services/trading/rebalance_service.py` - 核心邏輯
- `tests/test_rebalance_service.py` - 測試用例

### 相關文檔
- `README.md` - 項目概覽
- `docs/02-System-Overview.md` - 系統架構
- `docs/04-Operations-and-Tasks.md` - 任務與監控

### 外部參考
- [Cloud Scheduler 文檔](https://cloud.google.com/scheduler/docs)
- [MEXC API v3 文檔](https://www.mexc.com/api-docs/spot-v3/introduction)
- [FastAPI 文檔](https://fastapi.tiangolo.com/)

## 🤝 貢獻者注意事項

如果您是新加入此討論的成員：

1. **快速上手**：先閱讀本 README 獲得概覽
2. **深入理解**：根據您的角色閱讀相應的 ADR 文檔
3. **提供反饋**：在 PR 中留下您的意見和問題
4. **參與討論**：回答待討論問題或提出新問題

## 📞 聯絡方式

如有任何問題或建議，請在 GitHub PR 中留言討論。

---

**最後更新：** 2026-01-01  
**狀態：** 文檔階段完成，等待團隊審查  
**下一步：** 團隊討論與決策
