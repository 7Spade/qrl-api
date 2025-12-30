redis_client/
├─ redis/                         ← redis-py 主體套件
│  ├─ __init__.py                 ← 初始化
│  ├─ asyncio/                    ← Async client
│  │  ├─ __init__.py
│  │  ├─ client.py                ← Async Redis client API
│  │  ├─ connection.py            ← Async connection
│  │  └─ pool.py                  ← Async connection pool
│  ├─ client.py                   ← Sync Redis client API
│  ├─ connection.py               ← Sync connection
│  ├─ pool.py                     ← Sync connection pool
│  ├─ commands/                   ← Redis commands 封裝
│  │   ├─ __init__.py
│  │   └─ ...                     ← 各類 command 模組
│  ├─ _parsers/                   ← ⭐ RESP 解析層
│  │  ├─ __init__.py
│  │  ├─ base.py                  ← Parser 基礎類別
│  │  ├─ socket.py                ← Socket / IO parser 支援
│  │  ├─ hiredis.py               ← 封裝 hiredis C parser
│  │  ├─ resp2.py                 ← Python fallback RESP2 parser
│  │  └─ resp3.py                 ← Python fallback RESP3 parser
│  └─ exceptions.py               ← Exception 定義
│
├─ hiredis/                        ← C 擴充套件
│  ├─ __init__.py
│  └─ hiredis*.pyd / .so          ← C binary

心智模型

[ Application ]
     |
[ Redis Service Layer ]
     |
[ redis-py (client + pool) ]
     |
[ hiredis (parser, optional) ]
     |
[ TCP Socket ]
     |
[ Redis Server ]

方向
[ My Code ]
      ↓
Redis / AsyncRedis Client
      ↓
Connection Pool
      ↓
Connection
      ↓
Socket IO (async / sync)
      ↓
RESP Parser 抽象層
      ├─ Python parser（fallback）
      └─ hiredis parser

本專案 redis_client 套件結構（單一職責 mixin）

infrastructure/external/redis_client/
├─ __init__.py                # 導出 RedisClient / redis_client 單例
├─ core.py                    # 連線池、健康檢查、集中匯入各 mixin，優先使用 HiredisParser
├─ client.py                  # 向後相容導出
├─ balance_cache.py           # 餘額 / 總資產快取
├─ market_cache.py            # 行情快取（ticker / orderbook / trades / klines）
├─ bot_status_repo.py         # Bot 狀態
├─ position_repo.py           # 持倉快照
├─ position_layers_repo.py    # 分層持倉
├─ price_repo.py              # 價格快照與歷史
├─ trade_counter_repo.py      # 交易計數 / 最近交易時間
├─ trade_history_repo.py      # 交易歷史
├─ cost_repo.py               # 成本 / PnL
└─ mexc_raw_repo.py           # MEXC 原始回應留存

Parser 策略：若環境安裝 hiredis 則 core.py 透過 parser_class=HiredisParser 啟用 C 解析器，否則回退內建 Python 解析器。
