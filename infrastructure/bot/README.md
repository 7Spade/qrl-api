# infrastructure/bot

QRL/USDT 專用的交易 bot 模組，按六階段流程拆分，並以 `bot_core` 專注流程、`bot_utils` 提供純計算工具。

## 目錄結構

```
bot/
├─ bot_core/
│  ├─ core.py        # TradingBot 主流程（六階段）
│  └─ __init__.py
├─ bot_utils.py      # MA、成本、PnL 等純計算函數
├─ __init__.py       # 封裝導出 TradingBot
```

## 設計重點
- **單一交易對**：僅支援 QRL/USDT。
- **六階段流程**：啟動→收數→策略→風控→執行→清理。
- **純計算抽離**：MA、成本、PnL 計算集中在 `bot_utils`，降低核心流程的分支與重複計算。
- **Redis 優先**：行情、倉位、成本寫入 Redis，避免重複查詢；缺資料時平滑降級。

## 推薦擴展點
- 在 `bot_utils` 增加新的指標計算（如 RSI、布林帶）。
- 在 `bot_core` 每個階段內保持單一責任，複雜邏輯請下沉到工具或服務層。
