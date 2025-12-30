infrastructure/
├─ bot/                          # 核心交易逻辑（六阶段流程、指标计算）
│   ├─ __init__.py
│   ├─ bot_core/
│   │   ├─ __init__.py
│   │   └─ core.py               # TradingBot 六阶段核心逻辑
│   └─ bot_utils.py              # 辅助函数（MA 计算、PnL 计算等）
│
├─ config/                       # 配置
│   ├─ __init__.py
│   ├─ config.py                 # 包装全局配置（API key、环境参数等）
│   └─ settings.py               # 配置实现
│
├─ external/                     # 第三方 / 外部服务客户端
│   ├─ __init__.py               # 统一导出 mexc_client、redis_client
│   ├─ mexc_client/              # MEXC API 客户端
│   │   ├─ __init__.py
│   │   ├─ core.py               # 客户端实现
│   │   └─ client.py             # 向后兼容导出
│   └─ redis_client/             # Redis 客户端（asyncio，分层 mixin）
│       ├─ __init__.py
│       ├─ core.py               # 连接池 / 健康检查，汇总 mixin
│       ├─ client.py             # 向后兼容导出
│       ├─ balance_cache.py      # 账户余额 / 总资产缓存
│       ├─ market_cache.py       # 行情缓存（ticker / orderbook / trades / klines）
│       ├─ bot_status_repo.py    # 机器人状态存取
│       ├─ position_repo.py      # 持仓快照
│       ├─ position_layers_repo.py # 分层持仓
│       ├─ price_repo.py         # 价格快照 & 历史
│       ├─ trade_counter_repo.py # 交易计数 / 最近交易时间
│       ├─ trade_history_repo.py # 交易历史
│       ├─ cost_repo.py          # 成本 / PnL
│       └─ mexc_raw_repo.py      # MEXC 原始响应留存
│
├─ tasks/                        # Cloud Scheduler / FastAPI 任务
│   ├─ __init__.py
│   ├─ auth.py                   # 请求验证（Cloud Scheduler / OIDC）
│   ├─ mexc_tasks_core.py        # 01-min / 05-min / 15-min 任务逻辑
│   ├─ mexc_tasks.py             # 任务路由包装
│   └─ router.py                 # FastAPI 路由
│
├─ utils/                        # 通用工具函数
│   ├─ __init__.py
│   ├─ redis_helpers_core.py     # Redis 辅助函数实现
│   ├─ redis_helpers.py          # 包装导出
│   ├─ utils_core.py             # 其他通用工具函数实现
│   └─ utils.py                  # 包装导出
│
├─ __init__.py
├─ bot.py                        # 交易入口文件（实例化 TradingBot）
└─ cloud_tasks.py                # Cloud Tasks / FastAPI 入口文件

# 额外的 utils（架构说明档中提到）
# 如 decorators、redis_keys、redis_manager 等，落位于 infrastructure/utils/ 下，可按需扩展。
