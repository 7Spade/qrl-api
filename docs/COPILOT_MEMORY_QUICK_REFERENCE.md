# GitHub Copilot Memory 快速參考卡

## 🚀 常用指令

### 儲存記憶
```javascript
store_memory({
  category: "general",           // general, file_specific, user_preferences, bootstrap_and_build
  citations: "docs/file.md",     // 來源引用
  fact: "簡短事實陳述",          // < 200 字元
  reason: "為何需要記住",         // 2-3 句說明
  subject: "主題標籤"            // 1-2 個詞
})
```

### 搜尋記憶
```javascript
memory-search_nodes({ query: "關鍵字" })
```

### 查看特定記憶
```javascript
memory-open_nodes({ names: ["主題名稱"] })
```

### 讀取全部記憶
```javascript
memory-read_graph()
```

### 批次建立實體
```javascript
memory-create_entities({
  entities: [
    {
      name: "實體名稱",
      entityType: "類型",
      observations: ["觀察1", "觀察2"]
    }
  ]
})
```

### 建立關係
```javascript
memory-create_relations({
  relations: [
    {
      from: "實體A",
      to: "實體B",
      relationType: "關係類型"
    }
  ]
})
```

### 更新記憶
```javascript
memory-add_observations({
  observations: [
    {
      entityName: "實體名稱",
      contents: ["新觀察"]
    }
  ]
})
```

### 刪除記憶
```javascript
memory-delete_observations({
  deletions: [
    {
      entityName: "實體名稱",
      observations: ["要刪除的觀察"]
    }
  ]
})

memory-delete_entities({
  entityNames: ["實體名稱1", "實體名稱2"]
})
```

## 📋 記憶類別 (category)

| 類別 | 用途 | 範例 |
|------|------|------|
| `general` | 專案通用知識 | 架構原則、業務規則 |
| `file_specific` | 特定文件相關 | 某個檔案的特殊慣例 |
| `user_preferences` | 團隊偏好設定 | 編碼風格、工具選擇 |
| `bootstrap_and_build` | 建置和啟動 | 版本資訊、建置指令 |

## ✅ 應該儲存的資訊

- ✅ 架構決策和原則
- ✅ 技術棧版本資訊
- ✅ 業務規則和領域知識
- ✅ 編碼規範和慣例
- ✅ 常見問題的解決方案
- ✅ 不可違反的約束條件

## ❌ 不應該儲存的資訊

- ❌ 敏感資訊 (密碼、API 金鑰)
- ❌ 完整的程式碼片段
- ❌ 過於細節的實作
- ❌ 臨時性的實驗內容
- ❌ 未經驗證的猜測
- ❌ 頻繁變動的資料

## 🎯 ng-lin 專案已儲存記憶

查詢方式：

```javascript
// 查看專案定義
memory-open_nodes({ names: ["ng-lin project definition"] })

// 查看架構原則
memory-open_nodes({ names: ["core architectural principles"] })

// 查看任務結構
memory-open_nodes({ names: ["task hierarchical structure"] })

// 查看技術棧
memory-open_nodes({ names: ["technology stack and versions"] })

// 搜尋所有相關
memory-search_nodes({ query: "ng-lin" })
memory-search_nodes({ query: "architectural" })
memory-search_nodes({ query: "event sourcing" })
```

## 💡 實用技巧

### 1. 使用詳細引用
```javascript
citations: "docs/architecture.md lines 45-60, PR #123, User: 2024-01-15"
```

### 2. 建立知識網絡
```javascript
// 先建立實體
memory-create_entities({
  entities: [
    { name: "Event Bus", entityType: "component", observations: [...] },
    { name: "Task Service", entityType: "service", observations: [...] }
  ]
})

// 再建立關係
memory-create_relations({
  relations: [
    { from: "Task Service", to: "Event Bus", relationType: "uses" }
  ]
})
```

### 3. 定期維護
- 每月審查 `memory-read_graph()`
- 刪除過時資訊
- 更新版本號
- 補充新決策

## 📖 完整文檔

詳細使用說明請參閱：**[docs/COPILOT_MEMORY_GUIDE.md](../docs/COPILOT_MEMORY_GUIDE.md)**

## 📞 需要幫助？

1. 查看完整使用指南
2. 執行 `memory-search_nodes({ query: "你的問題" })`
3. 在團隊頻道詢問

---

**提示**: 將此參考卡加入書籤，隨時查閱！
