import sys
from pathlib import Path
import types

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def test_domain_interfaces_exports():
    from domain import interfaces

    assert interfaces.IMarketDataProvider.__name__ == "IMarketDataProvider"
    assert interfaces.IAccountDataProvider.__name__ == "IAccountDataProvider"
    assert interfaces.IPositionRepository.__name__ == "IPositionRepository"
    assert interfaces.IPriceRepository.__name__ == "IPriceRepository"
    assert interfaces.ITradeRepository.__name__ == "ITradeRepository"
    assert interfaces.ICostRepository.__name__ == "ICostRepository"


def test_domain_core_packages():
    from src.app.domain.trading.services.position.calculator import PositionManager
    from src.app.domain.trading.services.risk.limits import RiskManager
    from src.app.domain.trading.strategies.trading_strategy import TradingStrategy

    assert PositionManager.__module__.endswith("calculator")
    assert RiskManager.__module__.endswith("limits")
    assert TradingStrategy.__module__.endswith("trading_strategy")


def test_infrastructure_wrappers():
    from src.app.infrastructure.bot_runtime import TradingBot
    from src.app.infrastructure.config import Config, config
    from infrastructure.external import MEXCClient, mexc_client
    from infrastructure.external.redis_client import RedisClient, redis_client

    assert isinstance(config, Config)
    assert TradingBot is not None
    assert isinstance(mexc_client, MEXCClient)
    assert isinstance(redis_client, RedisClient)


def test_task_router_wrapper():
    from src.app.interfaces.tasks.router import router

    paths = {route.path for route in router.routes}
    assert "/tasks/01-min-job" in paths
    assert "/tasks/05-min-job" in paths
    assert "/tasks/15-min-job" in paths


def test_utils_wrappers():
    from src.app.infrastructure import utils

    assert isinstance(utils, types.ModuleType)
    assert hasattr(utils, "handle_redis_errors")
    assert hasattr(utils, "RedisDataManager")


def test_repository_and_service_wrappers():
    from src.app.infrastructure.persistence.repos.account import CostRepository, PositionRepository
    from src.app.infrastructure.persistence.repos.market import PriceRepository
    from src.app.infrastructure.persistence.repos.trade import TradeRepository
    from services.market import MarketService
    from services.trading import TradingService

    assert CostRepository.__module__.endswith("cost_repository_core")
    assert PositionRepository.__module__.endswith("position_repository_core")
    assert PriceRepository.__module__.endswith("price_repository_core")
    assert TradeRepository.__module__.endswith("trade_repository_core")
    assert MarketService.__module__.endswith("market_service_core")
    assert TradingService.__module__.endswith("trading_service_core")
