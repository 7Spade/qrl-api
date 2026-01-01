# Router Standardization Plan

## 🚨 Current Problems Identified

根據 @7Spade 的審查，發現以下嚴重的架構問題：

### 1. 無集中註冊入口

**問題：**
- 路由器直接在 `main.py` 中一個個註冊
- 沒有統一的路由器註冊機制
- 修改路由需要修改核心啟動文件

**當前狀態（main.py）：**
```python
from src.app.interfaces.http.status import router as status_router
from src.app.interfaces.http.market import router as market_router
from src.app.interfaces.http.account import router as account_router
from src.app.interfaces.http.bot import router as bot_router
from src.app.interfaces.http.sub_account import router as sub_account_router
from src.app.interfaces.tasks.router import router as cloud_tasks_router

# Register all routers
app.include_router(status_router)
app.include_router(market_router)
app.include_router(account_router)
app.include_router(bot_router)
app.include_router(sub_account_router)
app.include_router(cloud_tasks_router)
```

### 2. Router 寫法不一致

**問題類型：**

#### A. Prefix 定義位置不一致

**HTTP 路由器（在 router 定義時設定 prefix）：**
```python
# account.py
router = APIRouter(prefix="/account", tags=["Account"])

# market.py
router = APIRouter(prefix="/market", tags=["Market Data"])
```

**Task 路由器（也在 router 定義時設定 prefix）：**
```python
# task_15_min_job.py
router = APIRouter(prefix="/tasks", tags=["Cloud Tasks"])

# rebalance.py
router = APIRouter(prefix="/tasks", tags=["Cloud Tasks"])
```

**問題：** 所有 task 路由器都設定同樣的 `/tasks` prefix，導致：
- 重複的 prefix 聲明
- 難以理解實際路徑結構
- 修改 prefix 需要改多個文件

#### B. 錯誤處理模式不一致

**模式 1 - 簡單 try-catch：**
```python
# market.py
@router.get("/price/{symbol}")
async def price_endpoint(symbol: str):
    try:
        result = await get_price(symbol, mexc_client)
        return result
    except Exception as e:
        logger.error(f"Failed to get price: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

**模式 2 - 多層異常處理：**
```python
# task_15_min_job.py
async def task_15_min_job(...):
    try:
        # ... logic ...
    except HTTPException:
        raise  # 重新拋出 HTTP 異常
    except ValueError as exc:
        logger.error(f"Validation error: {exc}")
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.error(f"Execution failed: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))
```

**模式 3 - 條件檢查 + 異常：**
```python
# account.py
@router.get("/sub-accounts")
async def get_configured_sub_account():
    try:
        if not config.MEXC_API_KEY or not config.MEXC_SECRET_KEY:
            raise HTTPException(status_code=401, detail="API keys not configured")
        # ... logic ...
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

#### C. 依賴注入模式不一致

**模式 1 - 函數內部導入：**
```python
# account.py
def _get_mexc_client():
    from src.app.infrastructure.external import mexc_client
    return mexc_client
```

**模式 2 - 模組級導入：**
```python
# task_15_min_job.py
from src.app.infrastructure.external import mexc_client, redis_client
```

**模式 3 - 混合模式：**
```python
# account.py - 有些用函數，有些直接導入
async def _cache_orders(payload):
    try:
        from src.app.infrastructure.external import redis_client  # 函數內
        # ...
```

#### D. 日誌格式不一致

**樣式 1 - 簡單格式：**
```python
logger.info(f"Retrieved {len(sub_accounts)} sub-accounts")
```

**樣式 2 - 結構化格式：**
```python
logger.info(f"[15-min-job] Started - authenticated via {auth_method}")
```

**樣式 3 - 詳細診斷格式：**
```python
logger.info(
    f"[15-min-job] Balance snapshot - "
    f"QRL: {qrl_total:.4f}, "
    f"USDT: {usdt_total:.4f}, "
    # ... 多行
)
```

#### E. 返回格式不一致

**格式 1 - 完整結構：**
```python
return {
    "success": True,
    "source": "api",
    "data": result,
    "timestamp": datetime.now().isoformat(),
}
```

**格式 2 - 簡化結構：**
```python
return result  # 直接返回數據
```

**格式 3 - Task 專用格式：**
```python
return {
    "status": "success",
    "task": "15-min-job",
    "auth": auth_method,
    # ...
}
```

### 3. Code Style 落差很大

**問題：**

#### A. Docstring 風格不一致

**完整 docstring：**
```python
async def task_15_min_job(...):
    """
    15-minute scheduled task handler.

    Executes two operations:
    1. Cost/PnL update (future implementation)
    2. Symmetric rebalance plan generation

    Authentication:
        Requires Cloud Scheduler authentication...

    Returns:
        dict: Task execution results...
    """
```

**簡短 docstring：**
```python
async def get_account_balance():
    """Get account balance with fallback to cached snapshot."""
```

**無 docstring：**
```python
def _get_mexc_client():
    from src.app.infrastructure.external import mexc_client
    return mexc_client
```

#### B. 類型註解不一致

**完整類型註解：**
```python
async def get_klines(
    symbol: str,
    interval: str = "1m",
    limit: int = 100,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
):
```

**部分類型註解：**
```python
async def task_15_min_job(
    x_cloudscheduler: Optional[str] = Header(None, alias="X-CloudScheduler"),
    authorization: Optional[str] = Header(None),
):  # 無返回類型
```

**無類型註解：**
```python
def _has_credentials(mexc_client):  # 參數和返回都無類型
    return bool(...)
```

#### C. 命名風格不一致

**函數命名：**
- `get_account_balance()` - 清晰的動詞+名詞
- `price_endpoint()` - 帶 `_endpoint` 後綴（冗餘）
- `task_15_min_job()` - 帶 `task_` 前綴
- `_build_balance_service()` - 帶 `_build_` 前綴
- `_get_mexc_client()` - 帶 `_get_` 前綴

**變數命名：**
- `mexc_client` vs `client` vs `mexc`
- `snapshot` vs `result` vs `data`
- `exc` vs `e` vs `error`

---

## 🎯 標準化方案

### Phase 1: 建立集中路由器註冊機制

**目標：** 創建統一的路由器註冊入口，移除 `main.py` 中的直接註冊

**實施步驟：**

1. **創建 `src/app/interfaces/__init__.py`（路由器聚合器）**

```python
"""
Centralized router aggregator for all API endpoints.

This module provides a single point of router registration,
eliminating the need to modify main.py when adding new routes.
"""
import logging
from fastapi import APIRouter

logger = logging.getLogger(__name__)

# Create master router
api_router = APIRouter()

# ===== HTTP Routers =====
try:
    from src.app.interfaces.http.status import router as status_router
    from src.app.interfaces.http.market import router as market_router
    from src.app.interfaces.http.account import router as account_router
    from src.app.interfaces.http.bot import router as bot_router
    from src.app.interfaces.http.sub_account import router as sub_account_router
    
    api_router.include_router(status_router)
    api_router.include_router(market_router)
    api_router.include_router(account_router)
    api_router.include_router(bot_router)
    api_router.include_router(sub_account_router)
    
    logger.info("HTTP routers registered successfully")
except Exception as e:
    logger.error(f"Failed to register HTTP routers: {e}", exc_info=True)

# ===== Task Routers =====
try:
    from src.app.interfaces.tasks.router import router as tasks_router
    api_router.include_router(tasks_router)
    logger.info("Task routers registered successfully")
except Exception as e:
    logger.error(f"Failed to register task routers: {e}", exc_info=True)

__all__ = ["api_router"]
```

2. **修改 `main.py` 使用集中註冊**

```python
# BEFORE (舊方式 - 一個個註冊):
from src.app.interfaces.http.status import router as status_router
from src.app.interfaces.http.market import router as market_router
# ... 更多導入 ...

app.include_router(status_router)
app.include_router(market_router)
# ... 更多註冊 ...

# AFTER (新方式 - 集中註冊):
from src.app.interfaces import api_router

app.include_router(api_router)
logger.info("All API routers registered via centralized aggregator")
```

**優勢：**
- ✅ 單一註冊入口
- ✅ 添加新路由不需修改 `main.py`
- ✅ 錯誤處理集中管理
- ✅ 啟動日誌清晰

### Phase 2: 統一 Router Prefix 處理

**目標：** 在路由器聚合層統一處理 prefix，各路由器不再自行設定

**標準模式：**

```python
# ===== 路由器定義層（無 prefix） =====
# src/app/interfaces/http/account.py
router = APIRouter(tags=["Account"])  # 移除 prefix

@router.get("/balance")  # 相對路徑
async def get_account_balance():
    ...

# ===== 聚合層（設定 prefix） =====
# src/app/interfaces/__init__.py
from src.app.interfaces.http.account import router as account_router

# 在聚合時設定 prefix
api_router.include_router(account_router, prefix="/account")
```

**遷移計劃：**
1. 移除所有路由器文件中的 `prefix` 參數
2. 在聚合層 (`__init__.py`) 統一設定 prefix
3. 更新所有路由路徑為相對路徑

### Phase 3: 統一錯誤處理模式

**標準模式：**

```python
@router.get("/endpoint")
async def endpoint_handler(...):
    """Endpoint description."""
    try:
        # 業務邏輯
        result = await service.operation()
        return result
    
    except HTTPException:
        # 重新拋出 FastAPI HTTP 異常（已包含狀態碼和詳情）
        raise
    
    except ValueError as e:
        # 驗證錯誤 - 400 Bad Request
        logger.error(f"[endpoint] Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        # 未預期錯誤 - 500 Internal Server Error
        logger.error(f"[endpoint] Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
```

**規則：**
- ✅ 所有端點都使用此模式
- ✅ HTTPException 優先級最高（立即重新拋出）
- ✅ ValueError 映射到 400
- ✅ 其他異常映射到 500
- ✅ 使用 `exc_info=True` 記錄完整堆棧

### Phase 4: 統一依賴注入模式

**標準模式（FastAPI Depends）：**

```python
from fastapi import Depends
from src.app.infrastructure.external import mexc_client, redis_client

# 定義依賴函數
def get_mexc_client():
    """Get MEXC client instance."""
    return mexc_client

def get_redis_client():
    """Get Redis client instance."""
    return redis_client

# 在路由中使用
@router.get("/endpoint")
async def endpoint_handler(
    mexc: MexcClient = Depends(get_mexc_client),
    redis: RedisClient = Depends(get_redis_client)
):
    # 使用注入的依賴
    data = await mexc.get_data()
    await redis.cache(data)
    return data
```

**遷移步驟：**
1. 創建 `src/app/interfaces/dependencies.py` 統一管理依賴
2. 將所有 `_get_*` 函數移至依賴文件
3. 使用 `Depends()` 注入依賴
4. 移除函數內部的動態導入

### Phase 5: 統一日誌格式

**標準格式：**

```python
# 端點開始
logger.info(f"[{endpoint_name}] Started - {context_info}")

# 關鍵步驟
logger.info(f"[{endpoint_name}] Step description - key=value, key2=value2")

# 成功完成
logger.info(f"[{endpoint_name}] Completed - duration={duration_ms}ms, result={summary}")

# 錯誤
logger.error(f"[{endpoint_name}] Error type: {error_message}", exc_info=True)
```

**規則：**
- ✅ 使用 `[endpoint_name]` 作為前綴
- ✅ 關鍵信息使用 `key=value` 格式
- ✅ 錯誤日誌包含 `exc_info=True`
- ✅ 避免多行字符串拼接

### Phase 6: 統一返回格式

**HTTP 端點標準格式：**

```python
{
    "success": true,
    "source": "api" | "cache",
    "data": <actual_data>,
    "timestamp": "2024-01-01T12:00:00",
    "metadata": {  # 可選
        "count": 10,
        "symbol": "QRLUSDT"
    }
}
```

**Task 端點標準格式：**

```python
{
    "status": "success" | "error",
    "task": "task-name",
    "auth": "scheduler" | "oidc",
    "timestamp": "2024-01-01T12:00:00",
    "duration_ms": 123,
    "result": <task_specific_data>
}
```

### Phase 7: 統一代碼風格

**標準：**

1. **Docstring：** 所有公開函數必須有 docstring
   ```python
   async def function_name(param: str) -> dict:
       """
       Brief description.
       
       Args:
           param: Parameter description
       
       Returns:
           dict: Return value description
       
       Raises:
           HTTPException: When error occurs
       """
   ```

2. **類型註解：** 所有參數和返回值必須有類型
   ```python
   async def handler(
       symbol: str,
       limit: int = 100
   ) -> dict:
   ```

3. **命名規範：**
   - 公開函數：`get_account_balance()` （動詞開頭）
   - 私有函數：`_build_service()` （單下劃線前綴）
   - 端點處理器：不需要 `_endpoint` 後綴
   - 異常變數：統一使用 `e`

---

## 🚀 實施計劃

### 階段 1：建立基礎架構（優先級：最高）
- [ ] 創建 `src/app/interfaces/__init__.py`（集中註冊）
- [ ] 創建 `src/app/interfaces/dependencies.py`（依賴注入）
- [ ] 修改 `main.py` 使用集中註冊
- [ ] 測試啟動和基本路由

### 階段 2：HTTP 路由器標準化（優先級：高）
- [ ] 移除 HTTP 路由器的 prefix
- [ ] 統一錯誤處理模式
- [ ] 統一返回格式
- [ ] 添加完整類型註解和 docstring

### 階段 3：Task 路由器標準化（優先級：高）
- [ ] 重構 `tasks/router.py` 使用新模式
- [ ] 統一 task 路由器結構
- [ ] 統一日誌格式
- [ ] 統一返回格式

### 階段 4：代碼質量提升（優先級：中）
- [ ] 執行 `black` 格式化
- [ ] 執行 `ruff` linting
- [ ] 執行 `mypy` 類型檢查
- [ ] 修復所有警告

### 階段 5：文檔和測試（優先級：中）
- [ ] 更新 API 文檔
- [ ] 添加集成測試
- [ ] 創建架構文檔
- [ ] 創建貢獻指南

---

## 📏 代碼規範文檔

### 新增文件：`CONTRIBUTING.md`

詳細的代碼風格指南、路由器創建規範、PR 檢查清單等。

### 新增文件：`docs/ARCHITECTURE.md`

完整的架構文檔，說明：
- 路由器註冊機制
- 依賴注入模式
- 錯誤處理標準
- 日誌規範

---

## ✅ 預期效益

### 一致性
- ✅ 所有路由器遵循相同模式
- ✅ 統一的錯誤處理和日誌
- ✅ 一致的代碼風格

### 可維護性
- ✅ 集中管理路由器註冊
- ✅ 清晰的依賴注入
- ✅ 完整的類型檢查

### 開發體驗
- ✅ 添加新路由不需修改核心文件
- ✅ 清晰的架構指南
- ✅ 完整的文檔

### 質量保證
- ✅ 自動化代碼格式化
- ✅ 類型檢查捕獲錯誤
- ✅ Linting 強制規範

---

## 📊 當前狀態總結

| 項目 | 當前狀態 | 目標狀態 |
|------|---------|----------|
| 路由器註冊 | ❌ 分散在 main.py | ✅ 集中在 __init__.py |
| Prefix 管理 | ❌ 各路由器自行定義 | ✅ 聚合層統一管理 |
| 錯誤處理 | ❌ 3+ 種模式 | ✅ 1 種標準模式 |
| 依賴注入 | ❌ 混亂（函數內導入/模組級） | ✅ FastAPI Depends |
| 日誌格式 | ❌ 3+ 種風格 | ✅ 結構化統一格式 |
| 返回格式 | ❌ 不一致 | ✅ HTTP/Task 各有標準 |
| Docstring | ❌ 有/無/不完整 | ✅ 所有公開函數必須有 |
| 類型註解 | ❌ 部分缺失 | ✅ 完整註解 |
| 命名規範 | ❌ 多種風格混用 | ✅ 統一命名規則 |

---

## 🔧 立即行動項

1. **審查此方案** - 確認標準化方向是否符合需求
2. **優先級確認** - 確定最優先需要標準化的部分
3. **開始實施** - 從 Phase 1 開始逐步重構

---

**狀態：** 📋 等待審查和批准  
**預計工作量：** ~5-7 個工作階段  
**風險：** 中等（需要大量代碼修改，但不影響功能）  
**建議：** 分階段實施，每階段完成後測試驗證
