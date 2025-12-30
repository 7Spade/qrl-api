infrastructure\external\
├─ redis_client/                         ← redis-py 主體套件
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
