## 1️⃣ 心智模型（精簡版）

`Application` → `Redis Service (cache/repo/history)` → `redis-py client` →
`Connection / Pool` → `Parser (hiredis/RESP fallback)` → `Redis Server`

---

## 2️⃣ 目錄結構（對齊拆分）

```text
infrastructure/external/redis_client/
├─ asyncio/                # Async Redis client
│  ├─ __init__.py
│  └─ client.py            # AsyncRedisClient + redis_client singleton
├─ services/               # 業務層 mixins（<4000 chars/檔）
│  ├─ balance_account_cache.py
│  ├─ balance_price_cache.py
│  ├─ balance_cache.py     # 聚合 mixin
│  ├─ market_price_cache.py
│  ├─ market_trades_cache.py
│  ├─ market_cache.py      # 聚合 mixin
│  ├─ bot_status_repo.py
│  ├─ position_repo.py / position_layers_repo.py
│  ├─ price_repo.py / cost_repo.py
│  ├─ trade_history_repo.py / trade_counter_repo.py
│  └─ mexc_raw_repo.py
├─ _parsers/               # RESP parser 層（hiredis wrapper + fallback）
│  ├─ __init__.py
│  ├─ base.py / socket.py / hiredis.py / resp2.py / resp3.py
├─ commands/               # 未來命令封裝 (placeholder)
├─ connection.py / pool.py # sync 介面 placeholder
├─ exceptions.py           # 自訂例外
├─ client.py               # 導出 RedisClient/redis_client
└─ core.py                 # 舊路徑相容 shim
```

---

## 3️⃣ 拆分理由（精簡）

* services/ 集中業務 mixins，已將 balance/market 分拆以符合單檔 < 4000 字元
* asyncio/ 與未來的 sync client 分層，保持對外介面 `RedisClient` 不變
* _parsers/ 收斂 hiredis optional 依賴，未安裝時自動 fallback
* commands/、connection.py、pool.py 先留 placeholder，方便後續擴充

---

## 4️⃣ 遷移優先順序

1. 建立資料夾結構（services/、asyncio/、_parsers/、commands/）
2. 把業務 mixins 移入 services/（必要時再細拆避免超過 4000 字元）
3. 將 async client 放到 asyncio/client.py，core.py/client.py 保持匯出相容
4. _parsers/ 先封裝 hiredis 可選依賴，後續可換 RESP parser
5. 每步檢查 imports / __all__，確保既有代碼只需 `from redis_client import redis_client`

---

## 5️⃣ 極簡原則

* 單一責任、層次分明，業務邏輯不觸底層 socket
* 每檔 < 4000 字元；超過就拆分成更細的 mixin/模組
* optional 依賴安全 fallback（hiredis 缺少時仍可運作）
