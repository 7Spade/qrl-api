# Cloud Scheduler Setup Guide

This guide explains how to correctly configure Google Cloud Scheduler to trigger automatic rebalancing.

## Endpoint Architecture

The QRL Trading API has **two types** of rebalance endpoints:

### 1. Task Endpoints (for Cloud Scheduler)

**Purpose**: Scheduled automatic execution via Cloud Scheduler  
**Path**: `/tasks/rebalance/*`  
**Authentication**: Required (Cloud Scheduler headers)  
**Usage**: Automated portfolio management

| Endpoint | URL | Schedule Recommendation |
|----------|-----|------------------------|
| Symmetric Rebalance | `https://your-service.run.app/tasks/rebalance/symmetric` | Every 30 minutes (`*/30 * * * *`) |
| Intelligent Rebalance | `https://your-service.run.app/tasks/rebalance/intelligent` | Every 15 minutes (`*/15 * * * *`) |

### 2. HTTP Endpoints (for Manual Trigger)

**Purpose**: Manual execution via HTTP POST or frontend button  
**Path**: `/account/rebalance/*`  
**Authentication**: Not required (uses configured MEXC credentials)  
**Usage**: On-demand portfolio rebalancing

| Endpoint | URL | Usage |
|----------|-----|-------|
| Symmetric Rebalance | `https://your-service.run.app/account/rebalance/symmetric` | Manual trigger |
| Intelligent Rebalance | `https://your-service.run.app/account/rebalance/intelligent` | Manual trigger |

---

## Cloud Scheduler Configuration (Correct)

### Job 1: Symmetric Rebalance (Every 30 minutes)

```yaml
Name: symmetric-rebalance
Frequency: */30 * * * * (Asia/Taipei)
Target type: HTTP
URL: https://qrl-trading-api-545492969490.asia-southeast1.run.app/tasks/rebalance/symmetric
HTTP method: POST
Auth header: OIDC token
Service account: [your-scheduler-service-account]@[project].iam.gserviceaccount.com
Audience: https://qrl-trading-api-545492969490.asia-southeast1.run.app
```

### Job 2: Intelligent Rebalance (Every 15 minutes)

```yaml
Name: intelligent-rebalance
Frequency: */15 * * * * (Asia/Taipei)
Target type: HTTP
URL: https://qrl-trading-api-545492969490.asia-southeast1.run.app/tasks/rebalance/intelligent
HTTP method: POST
Auth header: OIDC token
Service account: [your-scheduler-service-account]@[project].iam.gserviceaccount.com
Audience: https://qrl-trading-api-545492969490.asia-southeast1.run.app
```

---

## Common Mistakes

### ❌ WRONG: Using `/account/` endpoints with Cloud Scheduler

```yaml
# This will NOT work correctly
URL: https://your-service.run.app/account/rebalance/symmetric
```

**Problem**: 
- `/account/` endpoints don't expect Cloud Scheduler auth headers
- Will return 401 or fail authentication validation
- Designed for manual HTTP calls, not scheduled jobs

### ✅ CORRECT: Using `/tasks/` endpoints with Cloud Scheduler

```yaml
# This is correct
URL: https://your-service.run.app/tasks/rebalance/symmetric
```

**Why**:
- `/tasks/` endpoints validate Cloud Scheduler authentication
- Proper logging and error handling for scheduled execution
- Designed specifically for automated scheduling

---

## Verifying Cloud Scheduler Configuration

### Step 1: Check Scheduler Job Logs

Go to Cloud Console → Cloud Scheduler → [Job Name] → View Logs

**Expected Success Log**:
```json
{
  "httpRequest": {
    "status": 200
  },
  "jsonPayload": {
    "status": "success",
    "task": "rebalance-symmetric",
    "plan": {
      "action": "BUY|SELL|HOLD"
    }
  }
}
```

**Common Error Logs**:

| HTTP Status | Meaning | Fix |
|-------------|---------|-----|
| 401 | Authentication failed | Check OIDC token configuration |
| 404 | Wrong endpoint URL | Update URL to `/tasks/rebalance/*` |
| 500 | Service error | Check application logs for details |

### Step 2: Check Application Logs

Go to Cloud Run → qrl-trading-api → Logs

**Search for**:
```
[rebalance-symmetric] Authenticated via
[rebalance-intelligent] Authenticated via
```

**Expected Log Entry**:
```
[rebalance-symmetric] Authenticated via OIDC
[rebalance-symmetric] Plan generated - Action: BUY, Quantity: 15.5000
[rebalance-symmetric] Executing BUY order - Quantity: 15.5000 QRL
[rebalance-symmetric] Order executed successfully - Order ID: 123456789, Status: FILLED
```

### Step 3: Manual Test Scheduler Endpoint

You can manually test the scheduler endpoint using `gcloud`:

```bash
gcloud scheduler jobs run symmetric-rebalance --location=asia-southeast1
```

Or simulate with curl (requires proper OIDC token):

```bash
# Get OIDC token
TOKEN=$(gcloud auth print-identity-token \
  --audiences=https://qrl-trading-api-545492969490.asia-southeast1.run.app)

# Call scheduler endpoint
curl -X POST "https://qrl-trading-api-545492969490.asia-southeast1.run.app/tasks/rebalance/symmetric" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-CloudScheduler: true"
```

---

## Current Issue Analysis (Your Case)

**Observed Symptoms**:
- QRL balance: 22.5700 (worth 67.03 USDT)
- USDT balance: 150.02
- No automatic rebalancing happening

**Root Cause**: Cloud Scheduler is configured to call **wrong endpoints**:
- Current: `https://.../account/rebalance/symmetric`
- Should be: `https://.../tasks/rebalance/symmetric`

**Impact**:
- Cloud Scheduler jobs likely failing with 401 or not executing properly
- No orders being placed automatically
- Portfolio remains imbalanced (30% QRL, 70% USDT)

**Solution**:

1. **Update Cloud Scheduler Jobs**:
   - Go to Cloud Console → Cloud Scheduler
   - Edit `symmetric` job → Change URL to `/tasks/rebalance/symmetric`
   - Edit `15-min-job` → Change URL to `/tasks/rebalance/intelligent`

2. **Verify Authentication**:
   - Ensure OIDC token is configured
   - Service account has `roles/run.invoker` permission

3. **Test Immediately**:
   ```bash
   gcloud scheduler jobs run symmetric-rebalance --location=asia-southeast1
   ```

4. **Monitor Logs**:
   - Check Cloud Scheduler logs for 200 OK responses
   - Check Cloud Run logs for rebalance execution
   - Should see order execution within 1 minute

---

## Expected Behavior (After Fix)

With correct configuration, you should see:

### Every 30 minutes (Symmetric Rebalance)
1. Cloud Scheduler triggers `/tasks/rebalance/symmetric`
2. Service analyzes balance: QRL 30% vs USDT 70%
3. Determines action: BUY ~15-16 QRL to reach 50/50
4. Executes market buy order on MEXC
5. Portfolio rebalanced: ~50% QRL, ~50% USDT

### Every 15 minutes (Intelligent Rebalance)
1. Cloud Scheduler triggers `/tasks/rebalance/intelligent`
2. Service checks MA indicators (MA_7 vs MA_25)
3. If golden cross + price <= cost_avg: BUY
4. If death cross + price >= cost_avg * 1.03: SELL
5. Otherwise: HOLD (no action)

---

## Additional Resources

- **Manual Rebalancing**: Use `/account/rebalance/*` endpoints via curl or frontend
- **Debug Endpoint**: `POST /tasks/debug/rebalance` to check service without executing orders
- **Application Logs**: Cloud Run → Logs → Filter: `rebalance`
- **Scheduler Logs**: Cloud Scheduler → [Job] → View Logs

---

## Quick Fix Commands

```bash
# 1. Update symmetric job URL
gcloud scheduler jobs update http symmetric-rebalance \
  --location=asia-southeast1 \
  --uri=https://qrl-trading-api-545492969490.asia-southeast1.run.app/tasks/rebalance/symmetric

# 2. Update intelligent job URL  
gcloud scheduler jobs update http 15-min-job \
  --location=asia-southeast1 \
  --uri=https://qrl-trading-api-545492969490.asia-southeast1.run.app/tasks/rebalance/intelligent

# 3. Test immediately
gcloud scheduler jobs run symmetric-rebalance --location=asia-southeast1
gcloud scheduler jobs run 15-min-job --location=asia-southeast1

# 4. Check logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=qrl-trading-api" \
  --limit 50 --format json | grep -i rebalance
```

---

**Last Updated**: 2026-01-02  
**Status**: Fix Required - Update Cloud Scheduler URLs from `/account/` to `/tasks/`
