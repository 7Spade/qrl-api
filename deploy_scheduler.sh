#!/bin/bash
#
# Cloud Scheduler 部署腳本 - QRL 交易機器人
# 每 3 分鐘執行一次交易策略
#
# 使用方法:
#   ./deploy_scheduler.sh <CLOUD_RUN_URL> <PROJECT_ID> <REGION>
#
# 範例:
#   ./deploy_scheduler.sh https://qrl-trading-api-xxxxx-uc.a.run.app my-project-123 asia-east1
#

set -e

# 檢查參數
if [ "$#" -lt 3 ]; then
    echo "錯誤: 缺少必要參數"
    echo ""
    echo "使用方法:"
    echo "  $0 <CLOUD_RUN_URL> <PROJECT_ID> <REGION>"
    echo ""
    echo "範例:"
    echo "  $0 https://qrl-trading-api-xxxxx-uc.a.run.app my-project-123 asia-east1"
    echo ""
    exit 1
fi

CLOUD_RUN_URL=$1
PROJECT_ID=$2
REGION=$3
JOB_NAME="qrl-trading-api-trigger"
SERVICE_ACCOUNT="${PROJECT_ID}@appspot.gserviceaccount.com"

echo "========================================="
echo "QRL 交易機器人 - Cloud Scheduler 部署"
echo "========================================="
echo ""
echo "配置資訊:"
echo "  專案 ID:       $PROJECT_ID"
echo "  區域:          $REGION"
echo "  Cloud Run URL: $CLOUD_RUN_URL"
echo "  執行頻率:      每 3 分鐘"
echo "  服務帳戶:      $SERVICE_ACCOUNT"
echo ""

# 確認是否繼續
read -p "是否繼續部署? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "已取消部署"
    exit 0
fi

echo ""
echo "步驟 1/4: 檢查 Cloud Scheduler API 是否啟用..."
gcloud services enable cloudscheduler.googleapis.com --project=$PROJECT_ID

echo ""
echo "步驟 2/4: 檢查是否已存在同名的排程作業..."
if gcloud scheduler jobs describe $JOB_NAME --location=$REGION --project=$PROJECT_ID &>/dev/null; then
    echo "警告: 已存在名為 '$JOB_NAME' 的排程作業"
    read -p "是否刪除並重新建立? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "刪除現有排程作業..."
        gcloud scheduler jobs delete $JOB_NAME --location=$REGION --project=$PROJECT_ID --quiet
    else
        echo "已取消部署"
        exit 0
    fi
fi

echo ""
echo "步驟 3/4: 建立 Cloud Scheduler 排程作業..."
gcloud scheduler jobs create http $JOB_NAME \
    --schedule="*/3 * * * *" \
    --uri="${CLOUD_RUN_URL}/execute" \
    --http-method=POST \
    --location=$REGION \
    --project=$PROJECT_ID \
    --description="QRL/USDT 囤幣機器人 - 每 3 分鐘執行一次" \
    --time-zone="Asia/Taipei" \
    --attempt-deadline=180s \
    --max-retry-attempts=3 \
    --min-backoff=30s \
    --max-backoff=120s \
    --headers="Content-Type=application/json" \
    --oidc-service-account-email=$SERVICE_ACCOUNT

echo ""
echo "步驟 4/4: 驗證排程作業..."
gcloud scheduler jobs describe $JOB_NAME --location=$REGION --project=$PROJECT_ID

echo ""
echo "========================================="
echo "✅ 部署完成!"
echo "========================================="
echo ""
echo "排程作業資訊:"
echo "  名稱:     $JOB_NAME"
echo "  執行頻率: 每 3 分鐘 (*/3 * * * *)"
echo "  下次執行: 約 3 分鐘後"
echo "  時區:     Asia/Taipei (UTC+8)"
echo ""
echo "查看排程作業狀態:"
echo "  gcloud scheduler jobs describe $JOB_NAME --location=$REGION"
echo ""
echo "手動觸發執行 (測試用):"
echo "  gcloud scheduler jobs run $JOB_NAME --location=$REGION"
echo ""
echo "暫停排程作業:"
echo "  gcloud scheduler jobs pause $JOB_NAME --location=$REGION"
echo ""
echo "恢復排程作業:"
echo "  gcloud scheduler jobs resume $JOB_NAME --location=$REGION"
echo ""
echo "刪除排程作業:"
echo "  gcloud scheduler jobs delete $JOB_NAME --location=$REGION"
echo ""
