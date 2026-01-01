# GitHub Copilot Memory 使用指南

## 📚 概述

本文檔說明如何使用 GitHub Copilot 的記憶功能 (Memory/Knowledge Graph) 來儲存和查詢專案的重要資訊，使 AI 助手能夠更好地理解專案上下文，提供更準確的建議。

## 🎯 為什麼需要記憶功能？

GitHub Copilot 的記憶系統讓 AI 能夠：
- ✅ **記住專案目標和架構原則** - 確保建議符合專案設計理念
- ✅ **追蹤關鍵決策和慣例** - 維持程式碼風格的一致性
- ✅ **理解領域知識** - 更好地處理業務邏輯和專業術語
- ✅ **避免重複錯誤** - 記錄反模式和已知問題
- ✅ **加速新成員上手** - 快速傳遞專案上下文

## 🧠 記憶系統核心概念

### 記憶的組成

GitHub Copilot 的記憶系統基於知識圖譜 (Knowledge Graph)，包含：

1. **實體 (Entities)** - 專案中的核心概念
   - 系統模組、架構層級
   - 關鍵技術和框架
   - 業務領域概念

2. **關係 (Relations)** - 實體之間的連接
   - "使用"、"依賴"、"實現"
   - "包含"、"擴展"、"替代"

3. **觀察 (Observations)** - 關於實體的具體事實
   - 版本號、配置選項
   - 使用慣例、最佳實踐
   - 限制條件、注意事項

## 🛠️ 核心指令詳解

### 1. `store_memory` - 儲存記憶

將重要資訊儲存到 Copilot 的知識圖譜中。

#### 基本語法

```typescript
store_memory({
  category: string,        // 記憶類別
  citations: string,       // 資訊來源引用
  fact: string,           // 要記住的事實 (< 200 字元)
  reason: string,         // 為何需要記住 (2-3 句說明)
  subject: string         // 主題標籤 (1-2 個詞)
})
```

#### 參數說明

| 參數 | 類型 | 說明 | 範例 |
|------|------|------|------|
| `category` | string | 記憶分類：`general`(通用), `file_specific`(文件特定), `user_preferences`(用戶偏好), `bootstrap_and_build`(建置相關) | `"general"` |
| `citations` | string | 資訊來源，如文件路徑、行號、用戶輸入 | `"docs/architecture.md lines 10-20"` |
| `fact` | string | 清晰簡潔的事實陳述 (< 200 字元) | `"使用 Angular 20 standalone components"` |
| `reason` | string | 詳細說明為何儲存此記憶及其重要性 (2-3 句) | `"此資訊對於理解專案架構至關重要，將影響所有未來的元件開發決策"` |
| `subject` | string | 主題標籤，便於分類和查詢 (1-2 詞) | `"angular conventions"` |

#### 實際使用範例

```javascript
// 範例 1: 儲存架構原則
store_memory({
  category: "general",
  citations: "docs/00-index/00-index.md lines 90-110",
  fact: "Event = Fact: 事件描述已發生的事情，不是命令。State = Derived: 所有狀態從事件重播得出",
  reason: "這是系統的核心架構原則，違反會破壞事件溯源的保證。在程式碼審查和開發新功能時必須遵守這些原則",
  subject: "architectural principles"
})

// 範例 2: 儲存技術棧版本
store_memory({
  category: "bootstrap_and_build",
  citations: "package.json, README.md",
  fact: "專案使用 Angular 20.3.0、TypeScript 5.9、Firebase 20.0.1、Node.js 20.x LTS",
  reason: "確保所有開發建議和套件安裝都使用正確的版本，避免相容性問題",
  subject: "tech stack versions"
})

// 範例 3: 儲存業務規則
store_memory({
  category: "general",
  citations: "docs/dev/0.md lines 30-50",
  fact: "Task 拆分必須遵守金額守恆和數量守恆原則，父任務金額 = 所有子任務金額總和",
  reason: "這是業務邏輯的核心約束，確保財務數據一致性。實作任務拆分功能時必須驗證此規則",
  subject: "task splitting rules"
})

// 範例 4: 儲存編碼規範
store_memory({
  category: "user_preferences",
  citations: "User feedback: code review comments",
  fact: "使用 signal() 和 computed() 進行狀態管理，避免使用傳統的 RxJS Subject",
  reason: "專案已標準化使用 Angular 20 的 Signals API。保持一致性可提高程式碼可讀性和可維護性",
  subject: "state management pattern"
})
```

### 2. `memory-read_graph` - 讀取整個知識圖譜

查看已儲存的所有記憶。

```javascript
memory-read_graph()
```

**輸出範例：**
```json
{
  "entities": [
    {
      "name": "ng-lin project",
      "entityType": "project",
      "observations": [
        "Angular 20 construction site tracking system",
        "Event-sourced architecture with causality tracking"
      ]
    }
  ],
  "relations": [
    {
      "from": "ng-lin",
      "to": "Angular 20",
      "relationType": "uses"
    }
  ]
}
```

### 3. `memory-search_nodes` - 搜尋記憶

根據關鍵字搜尋相關記憶。

```javascript
memory-search_nodes({
  query: "Angular components"  // 搜尋關鍵字
})
```

**使用場景：**
- 快速查找特定主題的相關資訊
- 驗證是否已儲存某項資訊
- 探索相關記憶

### 4. `memory-open_nodes` - 查詢特定記憶

根據實體名稱獲取詳細資訊。

```javascript
memory-open_nodes({
  names: ["architectural principles", "tech stack"]
})
```

### 5. `memory-create_entities` - 批次建立實體

一次建立多個實體和觀察。

```javascript
memory-create_entities({
  entities: [
    {
      name: "Event Bus",
      entityType: "system_component",
      observations: [
        "使用 BlueprintEventBus 處理領域事件",
        "支援跨模組事件通訊",
        "所有狀態變更必須發布事件"
      ]
    },
    {
      name: "Firestore Security",
      entityType: "security_layer",
      observations: [
        "使用 Firestore Security Rules 實現多租戶隔離",
        "支援組織/團隊/夥伴的複雜權限管理"
      ]
    }
  ]
})
```

### 6. `memory-create_relations` - 建立關係

定義實體之間的關聯。

```javascript
memory-create_relations({
  relations: [
    {
      from: "UI Layer",
      to: "Event Bus",
      relationType: "publishes to"
    },
    {
      from: "Event Bus",
      to: "Process Layer",
      relationType: "triggers"
    }
  ]
})
```

## 📋 記憶儲存最佳實踐

### ✅ 應該儲存什麼

1. **架構決策和原則**
   - 為何選擇特定技術
   - 系統設計的核心原則
   - 不可違反的架構約束

2. **技術棧和版本資訊**
   - 框架版本號
   - 重要依賴套件
   - 建置和測試指令

3. **業務規則和領域知識**
   - 核心業務邏輯
   - 計算公式和演算法
   - 資料驗證規則

4. **編碼規範和慣例**
   - 命名規則
   - 檔案組織方式
   - 常用模式和反模式

5. **已知問題和解決方案**
   - 常見錯誤的修正方式
   - 性能優化技巧
   - 相容性問題

### ❌ 不應該儲存什麼

1. **敏感資訊**
   - API 金鑰、密碼
   - 個人資料
   - 內部機密資訊

2. **過於細節的實作**
   - 完整的程式碼片段 (應引用文件位置)
   - 臨時性的實驗內容
   - 頻繁變動的細節

3. **過時或不確定的資訊**
   - 未經驗證的猜測
   - 已廢棄的做法
   - 計劃中但未實施的功能

## 🎯 實際工作流程

### 場景 1: 新功能開發前

```bash
# 1. 搜尋相關記憶
memory-search_nodes({ query: "event sourcing patterns" })

# 2. 查看架構原則
memory-open_nodes({ names: ["architectural principles"] })

# 3. 開始開發，確保遵守已記錄的原則
```

### 場景 2: 程式碼審查時

```bash
# 1. 檢查是否違反已知規範
memory-search_nodes({ query: "coding conventions" })

# 2. 記錄新發現的模式或問題
store_memory({
  category: "user_preferences",
  citations: "PR #123 code review",
  fact: "避免在 constructor 中使用 inject()，改用 constructor injection",
  reason: "團隊決定為了可讀性統一使用 constructor injection",
  subject: "dependency injection style"
})
```

### 場景 3: 閱讀文件後

```bash
# 儲存關鍵資訊到記憶
store_memory({
  category: "general",
  citations: "docs/architecture/overview.md",
  fact: "系統使用三層架構：L0 (Fact) - 事件定義、L1 (Process) - 流程編排、L2 (Projection) - 查詢模型",
  reason: "理解層級劃分對於正確放置程式碼至關重要，避免架構違規",
  subject: "layered architecture"
})
```

## 🔄 記憶維護

### 更新過時的記憶

當資訊變更時：

1. 先刪除舊的觀察
```javascript
memory-delete_observations({
  deletions: [
    {
      entityName: "tech stack",
      observations: ["使用 Angular 19"]
    }
  ]
})
```

2. 新增新的觀察
```javascript
memory-add_observations({
  observations: [
    {
      entityName: "tech stack",
      contents: ["使用 Angular 20.3.0"]
    }
  ]
})
```

### 刪除不再需要的記憶

```javascript
memory-delete_entities({
  entityNames: ["deprecated-feature", "old-approach"]
})
```

## 📖 ng-lin 專案已儲存的記憶

以下是本專案已儲存的核心記憶：

### 1. 專案定義
- **主題**: ng-lin project definition
- **內容**: 工地進度追蹤系統，使用 Causality-Driven Event-Sourced Process System
- **來源**: docs/01-vision/01-problem-statement.md, README.md

### 2. 核心目標
- **主題**: core system goals
- **內容**: 不可變事件記錄、因果關係追蹤、確定性重播、決策模擬
- **來源**: docs/01-vision/02-system-goals.md

### 3. 任務階層結構
- **主題**: task hierarchical structure
- **內容**: 合約項次 → 父任務 → 子任務 → 孫任務，遵守金額守恆原則
- **來源**: docs/dev/0.md

### 4. 架構原則
- **主題**: core architectural principles
- **內容**: Event = Fact, State = Derived, Causality = Explicit, Replay = Deterministic
- **來源**: docs/00-index/00-index.md

### 5. 分層架構
- **主題**: layered architecture model
- **內容**: L0 (Fact) → L1 (Process) → L2 (Projection)
- **來源**: docs/00-index/00-index.md

### 6. 技術棧
- **主題**: technology stack and versions
- **內容**: Angular 20, TypeScript 5.9, Firebase 20.0.1, ng-alain
- **來源**: README.md, package.json

### 7. 品質目標
- **主題**: quality and performance targets
- **內容**: 99.9% 可用性，事件寫入 <100ms，查詢 <50ms
- **來源**: docs/01-vision/02-system-goals.md

## 💡 進階技巧

### 1. 使用引用鏈

儲存時提供詳細的引用路徑：
```
citations: "docs/architecture/overview.md lines 45-60, 
           PR #123 discussion, 
           User input: 2024-01-15"
```

### 2. 建立知識網絡

使用 `create_relations` 建立概念之間的連接：
```javascript
memory-create_relations({
  relations: [
    { from: "Task", to: "Event Bus", relationType: "publishes to" },
    { from: "Event Bus", to: "Saga", relationType: "triggers" },
    { from: "Saga", to: "Process State", relationType: "manages" }
  ]
})
```

### 3. 分層儲存資訊

- **General**: 專案通用知識
- **File-specific**: 特定檔案的慣例
- **User preferences**: 團隊編碼風格

### 4. 定期審查和更新

每月或每個 Sprint：
1. 執行 `memory-read_graph()` 查看所有記憶
2. 刪除過時資訊
3. 補充新的重要決策
4. 更新版本資訊

## 🚀 快速開始

### 立即儲存專案核心資訊

執行以下腳本將 docs 目錄的專案目標儲存到記憶：

```bash
# 這些記憶已經被儲存，你可以直接使用
memory-search_nodes({ query: "ng-lin" })
memory-search_nodes({ query: "architectural" })
memory-open_nodes({ names: ["ng-lin project definition"] })
```

### 為你的功能儲存記憶

當你開發新功能時：

```javascript
// 1. 記錄功能決策
store_memory({
  category: "general",
  citations: "Feature design doc: feature-xyz.md",
  fact: "新功能 XYZ 使用 Command-Query 模式，命令發布事件，查詢讀取投影",
  reason: "符合 CQRS 原則，保持讀寫分離和事件溯源一致性",
  subject: "feature xyz architecture"
})

// 2. 記錄實作細節
store_memory({
  category: "file_specific",
  citations: "src/features/xyz/xyz.service.ts",
  fact: "XyzService 使用 signal() 管理本地狀態，使用 EventBus.publish() 發布領域事件",
  reason: "標準化狀態管理模式，其他類似 service 應遵循相同模式",
  subject: "xyz service patterns"
})
```

## 🔗 相關資源

- [GitHub Copilot 官方文檔](https://docs.github.com/en/copilot)
- [專案架構文件](./00-index/00-index.md)
- [系統目標文件](./01-vision/02-system-goals.md)
- [核心原則文件](./02-paradigm/04-core-principles.md)

## 📞 問題與回饋

如果你有關於記憶功能使用的問題：
1. 查看本文檔的範例
2. 執行 `memory-search_nodes({ query: "your question" })`
3. 在團隊頻道詢問

---

**版本**: v1.0.0  
**最後更新**: 2026-01-01  
**維護者**: ng-lin Team
