# MEXC Balance Query Method - Technical Explanation

## Question

> 有一個問題：https://www.mexc.com/api-docs/spot-v3/spot-account-trade#account-information 明確提到可以直接查詢餘額的方法，為什麼我們不用？

**Translation**: "There's a problem - The MEXC API docs clearly mention a method to directly query balance, why aren't we using it?"

## Answer: We ARE Using It

**The current implementation is already using the most direct method available in MEXC Spot API v3.**

### MEXC API v3 Constraints

According to the official MEXC API documentation at https://www.mexc.com/api-docs/spot-v3/spot-account-trade#account-information:

1. **Only One Endpoint for Account Balance**: 
   - Endpoint: `GET /api/v3/account`
   - This is the ONLY way to query account balances in MEXC Spot API v3
   
2. **No Asset Filtering Available**:
   - The endpoint ALWAYS returns balances for ALL assets
   - There is NO parameter to filter by specific assets (e.g., only QRL and USDT)
   - Request parameters: `recvWindow` (optional), `timestamp` (required)
   
3. **Client-Side Filtering Required**:
   - To get specific asset balances, we must:
     1. Call `/api/v3/account` (returns ALL assets)
     2. Filter the results client-side to extract desired assets

### Current Implementation

Our implementation in `src/app/infrastructure/external/mexc/repos/account_repo.py`:

```python
async def get_account_info(self) -> Dict[str, Any]:
    """Get complete account information including all asset balances.
    
    This is the most direct method provided by MEXC API v3 for querying
    account balances. No more granular endpoint exists for querying
    specific assets only.
    """
    return await self._request("GET", "/api/v3/account", signed=True)
```

This is exactly what the MEXC documentation recommends - it's the ONLY method available.

### Why Two API Calls?

You might notice we make two API calls in `fetch_balance_snapshot()`:

1. **`/api/v3/account`** - Get account balances (QRL, USDT, etc.)
2. **`/api/v3/ticker/price`** - Get current QRL/USDT price

This is necessary because:
- The account endpoint returns balances but NOT prices
- We need the current price to calculate QRL value in USDT
- MEXC API v3 doesn't provide a single endpoint that returns both

### Helper Methods Explained

We provide three methods for convenience:

1. **`get_account_info()`** - Direct API call, returns ALL assets
2. **`get_asset_balance(asset)`** - Calls `get_account_info()`, filters to one asset
3. **`get_balance(asset)`** - Calls `get_account_info()`, processes and filters assets

All three methods call the SAME endpoint (`/api/v3/account`) internally because that's the only option MEXC provides.

### Alternative APIs Considered

We reviewed other MEXC API endpoints:

- **`/api/v3/capital/config/getall`** - For deposit/withdraw network info, NOT balance
- **Sub-account endpoints** - Only for sub-accounts, not main account
- **WebSocket API** - Also uses the same account data structure

None of these provide a more direct way to query balances.

## Conclusion

✅ **Our implementation is optimal given MEXC API v3 constraints**

The `/api/v3/account` endpoint IS the "direct method" mentioned in the documentation. There is no more efficient way to query account balances in MEXC Spot API v3.

### What We've Done

1. ✅ Added comprehensive documentation to explain API limitations
2. ✅ Clarified why we use `get_account_info()` 
3. ✅ Documented that all helper methods ultimately call the same endpoint
4. ✅ Referenced official MEXC API documentation

### If You're Looking for Optimization

The best optimizations available are:

1. **Caching** (already implemented) - Store results in Redis with TTL
2. **Batching** - Combine multiple requests when possible
3. **WebSocket** - Use WebSocket streams for real-time updates (different use case)

But for REST API queries, we're already using the most direct method available.

## References

- [MEXC Spot API v3 - Account Information](https://www.mexc.com/api-docs/spot-v3/spot-account-trade#account-information)
- Implementation: `src/app/infrastructure/external/mexc/repos/account_repo.py`
- Balance Logic: `src/app/infrastructure/external/mexc/account.py`
