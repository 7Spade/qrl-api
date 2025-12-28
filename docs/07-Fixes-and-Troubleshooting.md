## 07 核心修復與故障排除

**目標**：快速定位已知問題與修復點，並提供最短修復路徑。

### 已完成的關鍵修復（精華）
1. **Redis TTL 資料流失 (#24)**  
   - 永久層取消 TTL；快取層保留 30s。  
   - 方法：`set_latest_price`（永久）、`set_cached_price`（快取，過期後自動回退）。  
2. **原始 MEXC 回應缺失 (#25)**  
   - 儲存完整回應與歷史：`mexc:raw:account_info:*`、`mexc:raw:ticker_*`。  
   - 便於重算、除錯。  
3. **Scheduler 授權**  
   - 同時支援 `X-CloudScheduler` 與 OIDC Bearer；日誌標註來源。  
4. **Dashboard 資料一致性**  
   - 餘額只用 API；Redis 只做成本/分析。避免混用新舊資料。  
5. **FastAPI/Redis 資源管理**  
   - Lifespan 管理連線；Redis 連線池 + 正確 `aclose()`。

### 快速驗證腳本
```bash
redis-cli TTL bot:QRLUSDT:price:latest    # 應為 -1
redis-cli TTL bot:QRLUSDT:price:cached    # 0-30 之間
redis-cli GET mexc:raw:account_info:latest
gcloud logging read "jsonPayload.message=~'authenticated via'" --limit=5
```

### 常見問題與處理
- **Dashboard 餘額為 0 / ERROR**  
  - 檢查 MEXC API Key 是否設定、權限正確、未過期。  
  - `curl /account/balance` 驗證是否 200；如 401/403 按提示調整權限。  
- **Scheduler 401**  
  - audience 必須為 SERVICE_URL；服務帳號具 `roles/run.invoker`；或暫用 `X-CloudScheduler` 標頭測試。  
- **Redis 無資料**  
  - 手動呼叫 `/tasks/update-price`；確認 TTL 是否為 -1（永久層）。  
- **子帳號列表空白**  
  - 必須為 Broker 帳，改用 Broker API Key；詳見 06。  

### 排障流程（最短路徑）
1. `curl /health` → Redis/MEXC 是否連線。  
2. `gcloud logging read ... 'Cloud Task'` → 任務是否執行成功。  
3. `redis-cli GET mexc:raw:account_info:latest` → 原始回應是否存在。  
4. `curl /account/balance` → 權限與簽名是否正常。  
5. 若仍失敗：依 07 列的常見問題對症處理，或回看舊檔 `TROUBLESHOOTING.md`、`CONSOLIDATED_FIXES.md`。
