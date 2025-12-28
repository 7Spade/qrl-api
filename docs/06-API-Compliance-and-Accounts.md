## 06 API 合規與子帳號

**重點**：遵循 MEXC 官方 v3 規格、正確簽名與授權；支援子帳號查詢。

### 合規檢查
- 基址：`https://api.mexc.com`，Spot v3。  
- 必要標頭：`Content-Type: application/json`、`X-MEXC-APIKEY`。  
- 簽名：`HMAC-SHA256(secret, urlencode(sorted(params)))`，含 `timestamp`（毫秒）與可選 `recvWindow`。  
- 主要端點（實作對應官方）：  
  - `GET /api/v3/account`（簽名）  
  - `GET /api/v3/ticker/24hr`（公開）  
  - `GET /api/v3/ticker/price`（公開）  
  - `POST /api/v3/order`（簽名，需 side/type/quantity 或 quoteOrderQty）  
- 來源參考：見 `MEXC_API_COMPLIANCE.md`。

### 子帳號（Broker）
- 列表：`GET /account/sub-accounts`。  
- 餘額查詢：`GET /account/sub-account/balance?email=...&sub_account_id=...`（至少提供一個）。  
- 配置：  
  ```bash
  MEXC_API_KEY=broker_key
  MEXC_SECRET_KEY=broker_secret
  SUB_ACCOUNT_EMAIL=optional-default
  SUB_ACCOUNT_ID=optional-default
  ```
- 權限要求：Broker 帳、讀取帳戶 + Spot Trading，禁止提款。  
- 前端：Dashboard 下拉顯示子帳號（切換功能可擴充）。  
- 詳細情境與錯誤處理：`SUB_ACCOUNT_GUIDE.md`、`TROUBLESHOOTING.md`。

### 常見問題速解
- 401 / 403：檢查 API Key 是否啟用、未過期、權限包含 Spot Trading/Read，IP 白名單。  
- 簽名錯誤：確認 `timestamp` 為毫秒，參數排序後再簽名。  
- 子帳號空集合：非 Broker 帳或權限不足；需更換為 Broker Key。  

### 安全建議
- 僅啟用所需權限（Spot Trading、Read），禁用 Withdraw。  
- 90 天內輪換金鑰，啟用 IP 白名單。  
- 金鑰存放 Secret Manager 或 `.env`，避免寫入程式碼庫。  
