"""Broker sub-account endpoints."""
from typing import Any, Dict, Optional


class SubAccountBrokerRepoMixin:
    async def get_broker_sub_accounts(
        self, sub_account: Optional[str] = None, page: int = 1, limit: int = 10
    ) -> Dict[str, Any]:
        params = {"page": page, "limit": limit}
        if sub_account:
            params["subAccount"] = sub_account
        return await self._request(
            "GET", "/api/v3/broker/sub-account/list", params=params, signed=True
        )

    async def get_broker_sub_account_assets(self, sub_account: str) -> Dict[str, Any]:
        params = {"subAccount": sub_account}
        return await self._request(
            "GET", "/api/v3/broker/sub-account/assets", params=params, signed=True
        )

    async def broker_transfer_between_sub_accounts(
        self, from_account: str, to_account: str, asset: str, amount: str
    ) -> Dict[str, Any]:
        params = {
            "fromAccount": from_account,
            "toAccount": to_account,
            "asset": asset,
            "amount": amount,
        }
        return await self._request(
            "POST", "/api/v3/broker/sub-account/transfer", params=params, signed=True
        )

    async def create_broker_sub_account_api_key(
        self, sub_account: str, permissions: str, note: Optional[str] = None
    ) -> Dict[str, Any]:
        params = {
            "subAccount": sub_account,
            "permissions": permissions,
        }
        if note:
            params["note"] = note
        return await self._request(
            "POST", "/api/v3/broker/sub-account/apiKey", params=params, signed=True
        )


# Backward-compatible alias expected by package exports
SubAccountBrokerRepository = SubAccountBrokerRepoMixin

__all__ = ["SubAccountBrokerRepoMixin", "SubAccountBrokerRepository"]
