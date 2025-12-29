infrastructure/
│
├─ bot/                          # 核心交易逻辑
│   ├─ __init__.py
│   ├─ bot_core.py               # TradingBot 六阶段核心逻辑
│   └─ bot_utils.py              # 辅助函数（MA计算、PnL计算等）
│
├─ config/                       # 配置
│   ├─ __init__.py
│   └─ config.py                 # 全局配置（API key, 参数等）
│
├─ external/                     # 第三方或外部服务客户端
│   ├─ __init__.py
│   ├─ mexc_client.py            # MEXC API 客户端
│   └─ redis_client.py           # Redis 客户端
│
├─ tasks/                        # Cloud Scheduler / FastAPI 任务
│   ├─ __init__.py
│   ├─ auth.py                   # 请求验证（Cloud Scheduler / OIDC）
│   ├─ mexc_tasks.py             # 01-min / 05-min / 15-min 任务逻辑
│   └─ router.py                 # FastAPI 路由
│
├─ utils/                        # 通用工具函数
│   ├─ __init__.py
│   ├─ redis_helpers.py          # Redis 辅助函数
│   └─ utils.py                  # 其他通用工具函数
│
├─ __init__.py
├─ bot.py                        # 交易入口文件（实例化 TradingBot）
└─ cloud_tasks.py                # Cloud Tasks / FastAPI 入口文件
