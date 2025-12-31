"""
Sub-account HTTP routes - manage sub-accounts, balances, and API keys.
"""
from datetime import datetime
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/account/sub-account", tags=["Sub-Accounts"])
logger = logging.getLogger(__name__)


def _get_mexc_client():
    from infrastructure.external import mexc_client
    return mexc_client


def _get_config():
    from infrastructure.config import config
    return config


@router.get("/list")
async def get_sub_accounts():
    """Get list of all sub-accounts."""
    mexc_client = _get_mexc_client()
    config = _get_config()

    try:
        if not config.MEXC_API_KEY or not config.MEXC_SECRET_KEY:
            raise HTTPException(
                status_code=401,
                detail={"error": "API keys not configured"},
            )

        async with mexc_client:
            sub_accounts = await mexc_client.get_sub_accounts()
            mode = "BROKER" if config.is_broker_mode else "SPOT"
            logger.info(f"Retrieved {len(sub_accounts)} sub-accounts")
            return {
                "success": True,
                "mode": mode,
                "sub_accounts": sub_accounts,
                "count": len(sub_accounts),
                "timestamp": datetime.now().isoformat(),
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get sub-accounts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/balance")
async def get_sub_account_balance(
    identifier: Optional[str] = None,
    email: Optional[str] = None,
    sub_account_id: Optional[str] = None,
):
    """Get balance for a specific sub-account."""
    mexc_client = _get_mexc_client()
    config = _get_config()

    sub_account_identifier = identifier or email or sub_account_id
    if not sub_account_identifier:
        raise HTTPException(
            status_code=400,
            detail="Sub-account identifier required",
        )

    try:
        mode = "BROKER" if config.is_broker_mode else "SPOT"
        balance_data = await mexc_client.get_sub_account_balance(sub_account_identifier)
        return {
            "success": True,
            "mode": mode,
            "sub_account_identifier": sub_account_identifier,
            "balance": balance_data,
            "timestamp": datetime.now().isoformat(),
        }
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get sub-account balance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transfer")
async def transfer_between_sub_accounts(
    from_account: str,
    to_account: str,
    asset: str,
    amount: str,
    from_type: str = "SPOT",
    to_type: str = "SPOT",
):
    """Transfer assets between sub-accounts."""
    mexc_client = _get_mexc_client()
    config = _get_config()

    if not config.MEXC_API_KEY or not config.MEXC_SECRET_KEY:
        raise HTTPException(status_code=401, detail="API keys not configured")

    try:
        result = await mexc_client.transfer_between_sub_accounts(
            from_account=from_account,
            to_account=to_account,
            asset=asset,
            amount=amount,
            from_type=from_type,
            to_type=to_type,
        )
        logger.info(f"Transfer: {amount} {asset} from {from_account} to {to_account}")
        return {
            "success": True,
            "transfer": {
                "from_account": from_account,
                "to_account": to_account,
                "asset": asset,
                "amount": amount,
            },
            "result": result,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Transfer failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api-key")
async def create_sub_account_api_key(
    sub_account: str,
    note: str = "QRL Trading API",
    permissions: str = "READ_ONLY",
):
    """Create API key for sub-account."""
    mexc_client = _get_mexc_client()

    try:
        result = await mexc_client.create_sub_account_api_key(
            sub_account=sub_account,
            note=note,
            permissions=permissions,
        )
        logger.info(f"Sub-account API key created for {sub_account}")
        return {
            "success": True,
            "sub_account": sub_account,
            "result": result,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Failed to create sub-account API key: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api-key")
async def delete_sub_account_api_key(sub_account: str, api_key: str):
    """Delete API key for sub-account."""
    mexc_client = _get_mexc_client()

    try:
        result = await mexc_client.delete_sub_account_api_key(
            sub_account=sub_account, api_key=api_key
        )
        logger.info(f"Sub-account API key deleted for {sub_account}")
        return {
            "success": True,
            "sub_account": sub_account,
            "result": result,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Failed to delete sub-account API key: {e}")
        raise HTTPException(status_code=500, detail=str(e))


__all__ = ["router"]
