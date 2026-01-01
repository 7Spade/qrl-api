# GitHub Copilot Memory 儲存記錄

## 📅 儲存日期
2026-01-01

## ✅ 已儲存的記憶清單

本次工作中，已使用 `store_memory` 工具成功儲存以下 8 個核心專案記憶：

### 1. ng-lin 專案定義
- **主題**: ng-lin project definition
- **類別**: general
- **來源**: docs/01-vision/01-problem-statement.md, docs/00-index/00-index.md, README.md
- **內容**: ng-lin (GigHub) 是一個工地施工進度追蹤管理系統，實作 Causality-Driven Event-Sourced Process System，使用 Angular 20, Firebase/Firestore, ng-alain 框架

### 2. 核心系統目標
- **主題**: core system goals
- **類別**: general
- **來源**: docs/01-vision/02-system-goals.md
- **內容**: 主要目標包括：(1) 完整的不可變事件記錄與因果元數據，(2) 明確的因果關係追蹤，(3) 任意時間點的確定性狀態重播，(4) 決策模擬與 what-if 分析能力

### 3. 任務階層結構
- **主題**: task hierarchical structure
- **類別**: general
- **來源**: docs/dev/0.md lines 1-150
- **內容**: 任務遵循 3 層階層：合約項次 → 父任務 → 子任務 → 孫任務。每層可使用 TaskSplit 事件拆分，必須遵守守恆原則（金額守恆、數量守恆）。父任務拆分後成為容器，不能直接執行。

### 4. 問題陳述與動機
- **主題**: problem statement and motivation
- **類別**: general
- **來源**: docs/01-vision/01-problem-statement.md
- **內容**: 要解決的核心問題：傳統 CRUD 系統丟失變更歷史、因果關係和決策能力。純事件溯源缺乏明確的因果建模和模擬能力。系統提供不可變性、可審計性、時間旅行查詢和確定性重播。

### 5. 核心架構原則
- **主題**: core architectural principles
- **類別**: general
- **來源**: docs/00-index/00-index.md lines 90-110
- **內容**: 四個核心架構原則：(1) Event = Fact（事件描述已發生的事情，不是命令），(2) State = Derived（所有狀態從事件重播），(3) Causality = Explicit（每個事件記錄其成因），(4) Replay = Deterministic（相同事件產生相同狀態）

### 6. 分層架構模型
- **主題**: layered architecture model
- **類別**: general
- **來源**: docs/00-index/00-index.md lines 109-120
- **內容**: 三層架構：L0 (Fact) - 僅不可變事件定義，L1 (Process) - 事件連接與流程編排（saga/process manager），L2 (Projection) - 衍生讀模型與查詢優化。依賴流：UI → Features → Core → Infrastructure，Infrastructure 實作 Core 介面。

### 7. 技術棧與版本
- **主題**: technology stack and versions
- **類別**: general
- **來源**: docs/00-index/00-index.md lines 121-128, README.md lines 20-30
- **內容**: 關鍵技術：Angular 20 (standalone components)、TypeScript 5.9、Firebase 20.0.1 (Firestore 資料存儲、Cloud Functions)、ng-alain 企業 UI 框架、ng-zorro-antd 元件。支援組織/團隊/夥伴的多租戶架構，透過 Firestore Security Rules 實現複雜權限管理。

### 8. 品質與性能目標
- **主題**: quality and performance targets
- **類別**: general
- **來源**: docs/01-vision/02-system-goals.md lines 50-70
- **內容**: 品質目標：99.9% 可用性、事件寫入 <100ms (P95)、查詢回應 <50ms (P95)、重播速度 >10000 events/sec。開發標準：100% 可重播測試、完整事件追蹤以便除錯、模組化架構。營運：完整可觀測性、時間點恢復、根因分析、向後相容的演化。

## 🔍 如何查詢這些記憶

### 搜尋所有相關記憶
```javascript
memory-search_nodes({ query: "ng-lin" })
memory-search_nodes({ query: "architectural" })
memory-search_nodes({ query: "event sourcing" })
```

### 查看特定主題
```javascript
memory-open_nodes({ names: ["ng-lin project definition"] })
memory-open_nodes({ names: ["core architectural principles"] })
memory-open_nodes({ names: ["task hierarchical structure"] })
memory-open_nodes({ names: ["technology stack and versions"] })
```

### 讀取全部記憶
```javascript
memory-read_graph()
```

## 📚 相關文件

- [完整使用指南](./COPILOT_MEMORY_GUIDE.md)
- [快速參考卡](./COPILOT_MEMORY_QUICK_REFERENCE.md)
- [範例腳本](../scripts/store-project-memories.js)

## 💡 使用建議

1. **開發新功能前**：搜尋相關架構原則和業務規則
2. **程式碼審查時**：檢查是否違反已儲存的規範
3. **閱讀文件後**：儲存新發現的重要資訊
4. **定期維護**：每月審查並更新記憶

## 🔄 維護記錄

| 日期 | 動作 | 說明 |
|------|------|------|
| 2026-01-01 | 初始儲存 | 儲存 8 個核心專案記憶 |

---

**注意**: 這些記憶儲存在 GitHub Copilot 的知識圖譜中，會在 AI 助手提供建議時自動使用。定期更新以保持資訊的準確性。
