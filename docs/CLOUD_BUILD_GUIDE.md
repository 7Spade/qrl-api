# Google Cloud Build Complete Deployment Guide

> **完整的 Cloud Build 部署流程說明**

## 📖 概述

本指南說明如何使用一個命令 `gcloud builds submit --config=cloudbuild.yaml .` 完成整個部署流程：

```
Dockerfile → Build Image (Cloud Build) → Push to Artifact Registry → Deploy to Cloud Run
```

## 🎯 目標

執行 `gcloud builds submit --config=cloudbuild.yaml .` 後自動完成：

1. ✅ 驗證 Dockerfile 和 Python 代碼
2. ✅ 建立 Docker 映像
3. ✅ 測試映像
4. ✅ 推送到 Artifact Registry
5. ✅ 部署到 Cloud Run
6. ✅ 驗證部署成功

## 🚀 快速開始

### 方式 1: 使用自動化腳本（推薦）

```bash
# Step 1: 設置密鑰
./setup-secrets.sh

# Step 2: 部署
./deploy.sh
```

### 方式 2: 手動執行

```bash
# 前置作業
gcloud auth login
gcloud config set project qrl-api

# 啟用必要的 API
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    secretmanager.googleapis.com

# 建立 Artifact Registry
gcloud artifacts repositories create qrl-trading-api \
    --repository-format=docker \
    --location=asia-southeast1

# 設置密鑰（手動）
echo -n "your_api_key" | gcloud secrets create mexc-api-key --data-file=-
echo -n "your_secret" | gcloud secrets create mexc-secret-key --data-file=-
echo -n "redis://..." | gcloud secrets create redis-url --data-file=-

# 授權
PROJECT_NUMBER=$(gcloud projects describe qrl-api --format='value(projectNumber)')
for secret in mexc-api-key mexc-secret-key redis-url; do
    gcloud secrets add-iam-policy-binding $secret \
        --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
        --role="roles/secretmanager.secretAccessor"
done

# 執行部署
gcloud builds submit --config=cloudbuild.yaml .
```

## 📋 部署流程詳解

### cloudbuild.yaml 架構

```yaml
steps:
  # ========== 階段 1: 預先驗證 ==========
  - validate-dockerfile  # 驗證 Dockerfile 語法
  - lint-python         # 檢查 Python 代碼

  # ========== 階段 2: 建立映像 ==========
  - build-image         # 建立 Docker 映像（帶標籤）
  
  # ========== 階段 3: 測試映像 ==========
  - test-image          # 驗證映像完整性
  
  # ========== 階段 4: 推送映像 ==========
  - push-latest         # 推送 :latest 標籤
  - push-commit-tag     # 推送 :git-sha 標籤
  
  # ========== 階段 5: 部署服務 ==========
  - deploy-cloud-run    # 部署到 Cloud Run
  
  # ========== 階段 6: 驗證部署 ==========
  - verify-deployment   # 檢查健康狀態
  - update-traffic      # 更新流量到新版本
```

### 關鍵特性

#### 1. 多標籤支援

每次建立都會產生兩個標籤：
- `latest`: 永遠指向最新版本
- `{git-sha}`: 特定 commit 版本（可追溯）

#### 2. 零停機部署

```yaml
- '--no-traffic'        # 先部署不導流量
# ... 驗證成功後 ...
- 'update-traffic --to-latest'  # 才切換流量
```

#### 3. 自動驗證

```bash
# 映像驗證
- 檢查映像是否存在
- 檢查映像大小
- 驗證健康檢查配置

# 部署驗證
- 等待服務就緒
- 測試 /health 端點
- 顯示服務資訊
```

## 📊 部署後驗證

### 1. 獲取服務 URL

```bash
SERVICE_URL=$(gcloud run services describe qrl-trading-api \
    --region=asia-southeast1 \
    --format='value(status.url)')
echo "Service URL: $SERVICE_URL"
```

### 2. 健康檢查

```bash
curl "$SERVICE_URL/health"
# 預期: {"status":"healthy","redis":"connected","mexc":"connected"}
```

### 3. 檢查狀態

```bash
curl "$SERVICE_URL/status" | jq
```

### 4. 查看 API 文檔

```bash
open "$SERVICE_URL/docs"
```

### 5. 查看日誌

```bash
# 即時日誌
gcloud run services logs tail qrl-trading-api --region=asia-southeast1

# 歷史日誌
gcloud run services logs read qrl-trading-api --region=asia-southeast1 --limit=50
```

### 6. 查看建置歷史

```bash
gcloud builds list --limit=10
```

## 🔧 進階配置

### 自訂部署參數

```bash
gcloud builds submit \
    --config=cloudbuild.yaml \
    --substitutions=_SERVICE_NAME=my-api,_REGION=us-central1 \
    .
```

可用的替換變數：
- `_SERVICE_NAME`: 服務名稱（預設: qrl-trading-api）
- `_REGION`: 部署區域（預設: asia-southeast1）
- `_REPOSITORY`: Artifact Registry 倉庫
- `_IMAGE_NAME`: 映像名稱
- `_IMAGE_TAG`: 映像標籤（預設: latest）

### 修改資源配置

編輯 `cloudbuild.yaml` 中的 Cloud Run 部署步驟：

```yaml
# 資源限制
- '--memory=1Gi'        # 記憶體（預設: 512Mi）
- '--cpu=2'             # CPU（預設: 1）
- '--min-instances=1'   # 最小實例（預設: 0）
- '--max-instances=20'  # 最大實例（預設: 10）
```

## 🔒 安全性

### Secret Manager 配置

所有敏感資訊都儲存在 Secret Manager：

```bash
# 查看現有密鑰
gcloud secrets list

# 查看密鑰版本
gcloud secrets versions list mexc-api-key

# 更新密鑰
echo -n "new_value" | gcloud secrets versions add mexc-api-key --data-file=-
```

### IAM 權限檢查

```bash
# 檢查 Cloud Build 服務帳戶權限
PROJECT_NUMBER=$(gcloud projects describe qrl-api --format='value(projectNumber)')
gcloud projects get-iam-policy qrl-api \
    --flatten="bindings[].members" \
    --filter="bindings.members:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"
```

## 📦 建置優化

### .gcloudignore 配置

排除不必要的檔案以加快建置速度：

```
# Git 檔案
.git/
.github/

# 文檔
docs/
*.md
!README.md

# Python 快取
__pycache__/
*.pyc
venv/

# 測試
tests/
.pytest_cache/
```

### 建置效能

- **機器類型**: N1_HIGHCPU_8（高效能）
- **並行步驟**: 獨立步驟會自動並行執行
- **快取層**: Docker 層快取自動優化

## 🔍 故障排除

### 1. 建置失敗

```bash
# 查看建置日誌
gcloud builds log $(gcloud builds list --limit=1 --format='value(id)')

# 常見問題：
# - Dockerfile 語法錯誤 → 檢查 Dockerfile
# - Python 語法錯誤 → 執行 python -m py_compile *.py
# - 權限錯誤 → 檢查 IAM 權限
```

### 2. 部署失敗

```bash
# 查看 Cloud Run 日誌
gcloud run services logs read qrl-trading-api --limit=100

# 常見問題：
# - Redis 連線失敗 → 檢查 REDIS_URL 密鑰
# - MEXC API 錯誤 → 驗證 API 密鑰
# - 依賴缺失 → 檢查 requirements.txt
```

### 3. 服務無法訪問

```bash
# 檢查服務狀態
gcloud run services describe qrl-trading-api --region=asia-southeast1

# 設為公開訪問
gcloud run services add-iam-policy-binding qrl-trading-api \
    --region=asia-southeast1 \
    --member="allUsers" \
    --role="roles/run.invoker"
```

### 4. 密鑰訪問錯誤

```bash
# 重新授權
PROJECT_NUMBER=$(gcloud projects describe qrl-api --format='value(projectNumber)')
for secret in mexc-api-key mexc-secret-key redis-url; do
    gcloud secrets add-iam-policy-binding $secret \
        --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
        --role="roles/secretmanager.secretAccessor"
done
```

## 📈 監控與告警

### Cloud Console 監控

訪問：
```
https://console.cloud.google.com/run/detail/asia-southeast1/qrl-trading-api/metrics
```

### 指標監控

```bash
# 請求數
gcloud monitoring time-series list \
    --filter='metric.type="run.googleapis.com/request_count"'

# 延遲
gcloud monitoring time-series list \
    --filter='metric.type="run.googleapis.com/request_latencies"'

# 錯誤率
gcloud monitoring time-series list \
    --filter='metric.type="run.googleapis.com/request_count" AND metric.label.response_code_class="5xx"'
```

## 🔄 CI/CD 整合

### GitHub Actions 範例

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - uses: google-github-actions/auth@v1
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}
      
      - uses: google-github-actions/setup-gcloud@v1
      
      - name: Deploy
        run: gcloud builds submit --config=cloudbuild.yaml .
```

## 💰 成本估算

### 免費額度

- **Cloud Run**: 200 萬請求/月
- **Cloud Build**: 120 建置分鐘/天
- **Artifact Registry**: 0.5 GB 儲存
- **Secret Manager**: 6 個密鑰，1 萬次訪問/月

### 超出免費額度後

- Cloud Run: ~$0.00002400/請求
- Cloud Build: $0.003/建置分鐘
- Artifact Registry: $0.10/GB/月
- 預估月費: **$0-5**（一般使用）

## 📚 相關文件

- [QUICK_DEPLOY.md](../QUICK_DEPLOY.md) - 快速部署指南
- [DEPLOYMENT.md](../DEPLOYMENT.md) - 完整部署文檔
- [README.md](../README.md) - 專案說明
- [cloudbuild.yaml](../cloudbuild.yaml) - 建置配置
- [Dockerfile](../Dockerfile) - 容器配置

## 🆘 支援

遇到問題？

1. 查看 [故障排除](#故障排除) 章節
2. 檢查 [GitHub Issues](https://github.com/7Spade/qrl-api/issues)
3. 查看 Cloud Run 日誌
4. 聯繫專案維護者

## ✅ 檢查清單

部署前確認：

- [ ] 已安裝 gcloud CLI
- [ ] 已登入 Google Cloud (`gcloud auth login`)
- [ ] 已設置專案 (`gcloud config set project qrl-api`)
- [ ] 已啟用必要的 API
- [ ] 已建立 Artifact Registry 倉庫
- [ ] 已設置 Secret Manager 密鑰
- [ ] 已授權服務帳戶訪問密鑰
- [ ] 已驗證 MEXC API 密鑰有效
- [ ] 已驗證 Redis 連線正常

部署後驗證：

- [ ] 建置成功完成
- [ ] 映像已推送到 Artifact Registry
- [ ] Cloud Run 服務已部署
- [ ] 健康檢查通過
- [ ] API 文檔可訪問
- [ ] 日誌正常無錯誤
- [ ] 監控指標顯示正常

---

**祝部署順利！** 🎉
