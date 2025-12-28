# 建立 mexc-secret-key
gcloud secrets create mexc-secret-key --replication-policy="automatic"

# 將值加入最新版本（假設存在 .env 讀取）
$MEXC_SECRET_KEY = (Select-String -Path .env -Pattern '^MEXC_SECRET_KEY=').ToString().Split('=')[1].Trim()
echo $MEXC_SECRET_KEY | gcloud secrets versions add mexc-secret-key --data-file=-


# 取得專案編號
$PROJECT_NUMBER = gcloud projects describe qrl-api --format="value(projectNumber)"

# 授權給 Compute default service account
gcloud secrets add-iam-policy-binding mexc-api-key `
  --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" `
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding mexc-secret-key `
  --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" `
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding redis-url `
  --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" `
  --role="roles/secretmanager.secretAccessor"
