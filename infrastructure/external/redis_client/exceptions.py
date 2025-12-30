"""Redis client specific exceptions."""


class RedisClientError(Exception):
    """Base Redis client error."""


__all__ = ["RedisClientError"]
