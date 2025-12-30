<!-- markdownlint-disable-file -->
# Release Changes: Progressive architecture migration

**Related Plan**: none
**Implementation Date**: 2025-12-30

## Summary

Initialized changes log to track progressive migration into `src/app` per `ARCHITECTURE_TREE.md`.

## Changes

### Added

- src/app/application/account/{get_balance.py,list_orders.py,list_trades.py,dto.py} - Shims exposing legacy account use cases and constants.
- src/app/application/account/balance_service.py - Canonical BalanceService implementation in application layer (≤4000 bytes).
- src/app/application/market/{get_price.py,get_orderbook.py,get_klines.py,dto.py} - Shims for market use cases and symbols.
- src/app/application/trading/{execute_trade.py,validate_trade.py,update_position.py,manage_risk.py,workflow.py} - Trading service shims for application layer.
- src/app/application/bot/{start.py,stop.py,status.py} - Bot control shims re-exporting TradingService.
- src/app/domain/ports/{account_port.py,market_port.py,trade_port.py,position_port.py} - Domain port shims mapping legacy interfaces.
- src/app/domain/ports/{cost_port.py,price_port.py} - Canonical ports for cost/price repositories.
- src/app/infrastructure/exchange/mexc/_shared/{http_client.py,response_parser.py} - Shared HTTP helpers for MEXC layout.
- src/app/infrastructure/exchange/mexc/http/{auth/headers.py,auth/sign_request.py,market/get_price.py,market/get_orderbook.py,account/get_balance.py,account/list_orders.py,trade/place_order.py,trade/cancel_order.py} - HTTP adapters delegating to legacy mexc_client and services.
- src/app/infrastructure/exchange/mexc/ws/{connect.py,handlers.py} - WS adapter shims re-exporting legacy websocket helpers.
- src/app/infrastructure/exchange/mexc/adapters/{account_adapter.py,market_adapter.py} - Adapter shims exposing MEXCClient.
- src/app/infrastructure/persistence/redis/connection/{connect.py,pool.py} - Redis connection shims to legacy client.
- src/app/infrastructure/persistence/redis/codecs/json_codec.py - Minimal JSON codec placeholder.
- src/app/infrastructure/persistence/redis/keys/{account_keys.py,market_keys.py} - Key constants aligning with target layout.
- src/app/infrastructure/persistence/redis/repos/{account_balance_repo.py,market_price_repo.py} - Repo shims re-exporting legacy cache mixins.
- src/app/infrastructure/bot_runtime/{lifecycle.py,executor.py,risk_adapter.py} - Bot runtime shims exposing TradingBot.
- src/app/infrastructure/scheduler/cloud_tasks.py - Scheduler shim re-exporting legacy tasks router.
- src/app/shared/{clock.py,ids.py,typing.py,errors.py} - Shared utility shims and placeholders.
- src/app/domain/models/{account.py,balance.py} - Minimal domain model placeholders.
- src/app/infrastructure/config/{settings.py,env.py} - Config shims referencing legacy config.

### Modified

- api/account/balance.py - Imports BalanceService from migrated application layer.
- services/account/balance_service_core.py - Wrapper re-exporting migrated BalanceService.
- src/app/application/account/get_balance.py - Points to migrated BalanceService.
- src/app/infrastructure/exchange/mexc/http/account/get_balance.py - Points to migrated BalanceService.
- domain/interfaces/{account.py,market.py,trade.py,position.py,cost.py,price.py} - Wrap to re-export canonical ports in src/app/domain/ports.

### Removed

- none

## Release Summary

**Total Files Affected**: 9

### Files Created (3)

- src/app/application/account/balance_service.py - Migrated BalanceService implementation.
- src/app/domain/ports/{cost_port.py,price_port.py} - Added canonical cost/price ports.
- .copilot-tracking/changes/20251230-migration-changes.md - Tracks migration progress and file movements.

### Files Modified (6)

- api/account/balance.py
- services/account/balance_service_core.py
- src/app/application/account/get_balance.py
- src/app/infrastructure/exchange/mexc/http/account/get_balance.py
- domain/interfaces/{account.py,market.py,trade.py,position.py,cost.py,price.py}

### Files Removed (0)

- none

### Dependencies & Infrastructure

- **New Dependencies**: none
- **Updated Dependencies**: none
- **Infrastructure Changes**: none
- **Configuration Updates**: none

### Deployment Notes

No deployment impact for logging setup.
