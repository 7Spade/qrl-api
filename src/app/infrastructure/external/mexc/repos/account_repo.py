"""Account endpoints mixin.

MEXC API Balance Query Note:
The `/api/v3/account` endpoint is the ONLY direct method to query account
balances in MEXC Spot API v3. It returns ALL asset balances - there is no
endpoint or parameter to filter by specific assets. All balance query methods
in this class ultimately call this endpoint.

Reference: https://www.mexc.com/api-docs/spot-v3/spot-account-trade#account-information
"""

from typing import Any, Dict, Optional

from src.app.infrastructure.external.mexc.account import (
    build_balance_map,
    fetch_balance_snapshot,
)


class AccountRepoMixin:
    async def get_account_info(self) -> Dict[str, Any]:
        """Get complete account information including all asset balances.

        This is the most direct method provided by MEXC API v3 for querying
        account balances. No more granular endpoint exists for querying
        specific assets only.

        Returns:
            Dict containing account info and balances for ALL assets
        """
        return await self._request("GET", "/api/v3/account", signed=True)

    async def get_asset_balance(self, asset: Optional[str] = None) -> Dict[str, Any]:
        """Get balance for a specific asset or all assets.

        Note: This method calls get_account_info() which returns ALL asset balances
        from the MEXC API, then filters client-side. MEXC API v3 does not provide
        an endpoint to query specific assets directly.

        Args:
            asset: Specific asset symbol (e.g., 'QRL', 'USDT'), or None for all

        Returns:
            Balance dict for the specified asset, or full account info if asset is None
        """
        account_info = await self.get_account_info()
        if asset:
            for balance in account_info.get("balances", []):
                if balance.get("asset") == asset:
                    return balance
            return {"asset": asset, "free": "0", "locked": "0"}
        return account_info

    async def get_balance(self, asset: Optional[str] = None) -> Dict[str, Any]:
        """Get processed balance map for specific asset or all tracked assets.

        This method provides a cleaner interface than get_account_info() by returning
        only relevant assets (QRL, USDT) with computed totals. However, it still
        calls get_account_info() internally as MEXC API doesn't support filtered queries.

        Args:
            asset: Specific asset symbol to retrieve, or None for all tracked assets

        Returns:
            Balance map with 'free', 'locked', and 'total' fields
        """
        account_info = await self.get_account_info()
        balances = build_balance_map(account_info)
        if asset:
            return balances.get(
                asset, {"asset": asset, "free": "0", "locked": "0", "total": 0}
            )
        return balances

    async def get_balance_snapshot(self) -> Dict[str, Any]:
        """Get comprehensive balance snapshot for QRL/USDT trading.

        Fetches QRL and USDT balances along with current QRL price to provide
        a complete snapshot for trading decisions. This is a convenience method
        that combines balance and price data in a single call.

        Returns:
            Dict containing balances, prices, and raw account info
        """
        return await fetch_balance_snapshot(self)


# Backward-compatible alias expected by package exports
AccountRepository = AccountRepoMixin

__all__ = ["AccountRepoMixin", "AccountRepository"]
