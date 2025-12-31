## 05 策略、資料來源與倉位分層

**核心原則**：以 API 為真實餘額、Redis 為機器人視角；倉位分層保護核心持幣。

### 屯幣累積策略（精華）
- 目標：增加 QRL 數量，不追求短期 USDT。  
- 分層：核心 60–70% 永不賣、波段 20%、機動 10%。  
- USDT 儲備：15–25% 用於回調買入；禁止滿倉。  
- 交易節奏：成本遞減（買低、賣高再買回），或不對稱網格（買密賣疏）。  

### 資料來源策略
- QRL/USDT 餘額：**只用 `/account/balance`**（真實、即時）。  
- avg_cost / unrealized & realized PnL：來自 Redis 成本資料（機器人內部計算）。  
- 總價值顯示：使用 API 餘額 + 最新價格。  
- Fallback：若 API 失敗才暫用 Redis 倉位，但需明示可能為舊資料。  

### 倉位分層（Position Layers）
- Redis key：`bot:QRLUSDT:position:layers`（Hash，含 core_qrl/swing_qrl/active_qrl/last_adjust）。  
- API `/status` 可帶出 `position_layers` 區塊，Dashboard 顯示核心/波段/機動。  
- 交易限制：賣出時不得觸碰核心倉位；可交易數量 = 總持倉 - 核心。  

### 風控速記
1. 不在平均成本以上買入；賣出需高於 avg_cost × 1.05。  
2. 單日交易次數與單筆占比受限（避免手續費吞噬）。  
3. 極端行情：暴漲保留核心、暴跌分批買入、流動性不足則暫停交易。  

### 策略跑起來的最短路徑
- 依賴：設定 `.env`（MEXC_API_KEY、MEXC_SECRET_KEY、REDIS_URL），啟動 Redis（本地或 Redis Cloud）。  
- 啟動 API：`uvicorn main:app --host 0.0.0.0 --port 8080`，確認 `/health` 為 200。  
- 開啟機器人：  
  ```bash
  curl -X POST http://localhost:8080/control \
    -H "Content-Type: application/json" \
    -d '{"action": "start"}'
  ```  
- 執行策略（可先 dry run）：  
  ```bash
  curl -X POST http://localhost:8080/execute \
    -H "Content-Type: application/json" \
    -d '{"pair":"QRL/USDT","strategy":"ma-crossover","dry_run":true}'
  ```  
- 觀察狀態：`GET /status` 應包含 `position_layers`、`avg_cost`，並可透過 Redis `HGETALL bot:QRLUSDT:position` 驗證。  
- Context7/CCXT 交易順序建議：先載入市場、讀取行情（`fetch_ticker`），再送單（`create_order`）；對應本專案，先確保 `/market/price/{symbol}` 快取完成再觸發 `/execute`，避免使用到舊報價。  

### 實務檢查
```bash
redis-cli HGETALL bot:QRLUSDT:position          # 應包含 qrl_balance/usdt_balance/avg_cost
redis-cli HGETALL bot:QRLUSDT:position:layers   # 檢查 core/swing/active
redis-cli TTL bot:QRLUSDT:price:latest          # 必須為 -1（永久）
```

### 延伸閱讀（附錄）
- 詳細策略案例與程式範例：`1-qrl-accumulation-strategy.md`  
- 分層 API 與前端展示：`POSITION_LAYERS.md`  
- 資料權威判定細節：`DATA_SOURCE_STRATEGY.md`  
