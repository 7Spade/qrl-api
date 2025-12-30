"""Async Redis client for trading bot state."""
import logging
from typing import Optional

import redis.asyncio as redis

from ..services import (
    BalanceCacheMixin,
    BotStatusRepoMixin,
    CostRepoMixin,
    MarketCacheMixin,
    MexcRawRepoMixin,
    PositionLayersRepoMixin,
    PositionRepoMixin,
    PriceRepoMixin,
    TradeCounterRepoMixin,
    TradeHistoryRepoMixin,
)
from infrastructure.config.config import config
from .._parsers import hiredis_parser_kwargs

logger = logging.getLogger(__name__)


class AsyncRedisClient(
    BalanceCacheMixin,
    MarketCacheMixin,
    BotStatusRepoMixin,
    PositionRepoMixin,
    PositionLayersRepoMixin,
    PriceRepoMixin,
    TradeCounterRepoMixin,
    TradeHistoryRepoMixin,
    CostRepoMixin,
    MexcRawRepoMixin,
):
    """
    Async Redis client that wires service mixins to a redis.asyncio client.
    """

    def __init__(self):
        self.client: Optional[redis.Redis] = None
        self.pool: Optional[redis.ConnectionPool] = None
        self.connected = False

    async def connect(self) -> bool:
        try:
            parser_kwargs = hiredis_parser_kwargs()
            if config.REDIS_URL:
                self.pool = redis.ConnectionPool.from_url(
                    config.REDIS_URL,
                    max_connections=20,
                    decode_responses=config.REDIS_DECODE_RESPONSES,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    health_check_interval=30,
                    **parser_kwargs,
                )
                logger.info("Created Redis connection pool using REDIS_URL")
            else:
                self.pool = redis.ConnectionPool(
                    host=config.REDIS_HOST,
                    port=config.REDIS_PORT,
                    password=config.REDIS_PASSWORD,
                    db=config.REDIS_DB,
                    max_connections=20,
                    decode_responses=config.REDIS_DECODE_RESPONSES,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    health_check_interval=30,
                    **parser_kwargs,
                )
                logger.info("Created Redis connection pool at %s:%s", config.REDIS_HOST, config.REDIS_PORT)

            self.client = redis.Redis(connection_pool=self.pool)
            await self.client.ping()
            self.connected = True
            logger.info("Redis connection established successfully")
            return True

        except redis.ConnectionError as exc:
            logger.error("Failed to connect to Redis: %s", exc)
            self.connected = False
            return False
        except Exception as exc:  # pragma: no cover - defensive log
            logger.error("Unexpected error connecting to Redis: %s", exc)
            self.connected = False
            return False

    async def health_check(self) -> bool:
        try:
            if self.client:
                await self.client.ping()
                return True
            return False
        except Exception as exc:
            logger.error("Redis health check failed: %s", exc)
            return False


# Backward-compatible aliases
RedisClient = AsyncRedisClient


def _create_singleton() -> AsyncRedisClient:
    instance = AsyncRedisClient()
    return instance


redis_client = _create_singleton()

__all__ = ["AsyncRedisClient", "RedisClient", "redis_client"]
