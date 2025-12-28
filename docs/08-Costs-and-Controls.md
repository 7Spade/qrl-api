## 08 成本、風險與安全控管

### 粗估月成本（Cloud Run 範例）
- Cloud Run：~$22（CPU 約 240 vCPU-hr；含免費額度可能更低）。  
- Memorystore (1GB Basic)：~$35。  
- Cloud Scheduler：3 個 Job 在免費額度內。  
- **總計約 $57**（使用託管 Redis）。  
- 節省：改用 Redis Cloud 免費層或降低 Job 頻率，可降至 ~$22–40。

### 安全最小化清單
- MEXC API：僅 Spot Trading/Read，禁用 Withdraw；90 天輪換；建議 IP 白名單。  
- Secrets：放 Secret Manager 或 .env，避免寫入程式碼。  
- Cloud Run：最小權限服務帳號；Scheduler/OIDC 只授予 `roles/run.invoker`。  
- Redis：啟用密碼/TLS，VPC 內聯；避免未驗證的公網存取。  
- 日誌：避免輸出金鑰與敏感資料；原始回應僅存 Redis，不回傳到公開端點。  

### 成本與風控的落地作法
1. 先以免費資源啟動：Docker + Redis Cloud Free；驗證後再上 Cloud Run。  
2. Scheduler 間隔 1–5 分鐘即可；頻率過高徒增費用與壓力。  
3. 啟用告警（04）；問題早期發現比事後排障便宜。  
4. 變更環境或金鑰後，務必重跑 `/tasks/update-price` 以刷新永久層資料。  

### 變更/升級前後檢查
```bash
curl ${SERVICE_URL}/health
redis-cli TTL bot:QRLUSDT:price:latest   # -1
gcloud logging read "severity>=ERROR" --limit=10
```

### 進階建議
- 需要更高安全：可考慮 Cloud Armor + VPC 連接，或限制來源網段。  
- 成本壓力：關閉空閒實例（Cloud Run min-instances=0）、降低記憶體至 512Mi。  
