"""
Account and balance helpers extracted from MEXC client core.
"""

from typing import TYPE_CHECKING, Any, Dict

from src.app.infrastructure.utils import safe_float


QRL_USDT_SYMBOL = "QRLUSDT"


if TYPE_CHECKING:
    from .client import MEXCClient


def build_balance_map(account_info: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    balances: Dict[str, Dict[str, str]] = {}
    for balance in account_info.get("balances", []):
        asset = balance.get("asset")
        if asset not in {"QRL", "USDT"}:
            continue
        balances[asset] = {
            "free": balance.get("free", "0"),
            "locked": balance.get("locked", "0"),
            "total": safe_float(balance.get("free", 0))
            + safe_float(balance.get("locked", 0)),
        }
    # Ensure keys exist even if exchange omits zero-balance assets
    balances.setdefault("QRL", {"free": "0", "locked": "0", "total": 0})
    balances.setdefault("USDT", {"free": "0", "locked": "0", "total": 0})
    return balances


async def fetch_balance_snapshot(client: "MEXCClient") -> Dict[str, Any]:
    """Fetch QRL/USDT spot balances with accompanying price data.

    This function provides the most direct and efficient way to get balance
    information given the constraints of the MEXC API v3, which doesn't
    support querying specific assets directly. We must:
    1. Call /api/v3/account to get ALL asset balances
    2. Filter client-side to extract QRL and USDT balances
    3. Call /api/v3/ticker/price to get current QRL/USDT price

    Args:
        client: MEXCClient instance with authentication configured

    Returns:
        Dict with structure:
        {
            "balances": {
                "QRL": {"free": str, "locked": str, "total": float, "price": float},
                "USDT": {"free": str, "locked": str, "total": float}
            },
            "prices": {"QRLUSDT": float},
            "raw": dict  # Full account info from MEXC API
        }

    Raises:
        ValueError: If QRL/USDT price is not available from exchange

    Note:
        MEXC API v3 does not provide an endpoint to query balances for specific
        assets only. The /api/v3/account endpoint always returns ALL assets.
        Reference: https://www.mexc.com/api-docs/spot-v3/spot-account-trade#account-information
    """
    account_info = await client.get_account_info()
    ticker = await client.get_ticker_price(QRL_USDT_SYMBOL)
    if ticker.get("price") is None:
        raise ValueError("Missing QRL/USDT price from exchange")

    price = safe_float(ticker.get("price"))
    balances = build_balance_map(account_info)

    qrl_balance = balances.get("QRL") or {"free": "0", "locked": "0", "total": 0}
    usdt_balance = balances.get("USDT") or {"free": "0", "locked": "0", "total": 0}

    return {
        "balances": {
            "QRL": {**qrl_balance, "price": price},
            "USDT": usdt_balance,
        },
        "prices": {QRL_USDT_SYMBOL: price},
        "raw": account_info,
    }


__all__ = ["build_balance_map", "fetch_balance_snapshot"]
