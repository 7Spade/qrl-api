# Migration Checklist

Track progress of architecture migration from legacy to `src/app`.

**Last Updated**: 2025-12-31  
**Current Phase**: 3 (Domain Layer)  
**Overall Progress**: 40%

---

## Quick Status

| Phase | Component | Files | Status | Time Est. |
|-------|-----------|-------|--------|-----------|
| 1 | Repositories | 5 | ✅ DONE | - |
| 2 | Trading Services | 7 | ✅ DONE | - |
| 3 | Domain Layer | 14 | ⏳ TODO | 3.5h |
| 4 | Infrastructure | 71 | ⏳ TODO | 5.5h |
| 5 | Services | 18 | ⏳ TODO | 2h |
| 6 | API Layer | 32 | ⏳ TODO | 3h |
| 7 | Cleanup | - | ⏳ TODO | 1h |

**Total Remaining**: 142 files, ~15 hours, ~2 work days

---

## Phase 3: Domain Layer (14 files)

### Domain Interfaces → Ports (7 files)
- [ ] `domain/interfaces/cost.py` → `src/app/domain/ports/cost_port.py`
- [ ] `domain/interfaces/market.py` → `src/app/domain/ports/market_port.py`
- [ ] `domain/interfaces/trade.py` → `src/app/domain/ports/trade_port.py`
- [ ] `domain/interfaces/position.py` → `src/app/domain/ports/position_port.py`
- [ ] `domain/interfaces/account.py` → `src/app/domain/ports/account_port.py`
- [ ] `domain/interfaces/price.py` → `src/app/domain/ports/price_port.py`
- [ ] `domain/interfaces/__init__.py` → Create shim

### Risk Manager (2 files)
- [ ] `domain/risk_manager/core.py` → `src/app/domain/risk/*.py`
- [ ] `domain/risk_manager/__init__.py` → Create shim

### Trading Strategy (2 files)
- [ ] `domain/trading_strategy/core.py` → `src/app/domain/strategies/*.py`
- [ ] `domain/trading_strategy/__init__.py` → Create shim

### Position Manager (2 files)
- [ ] `domain/position_manager/core.py` → `src/app/domain/position/*.py`
- [ ] `domain/position_manager/__init__.py` → Create shim

### Main Domain Shim
- [ ] `domain/__init__.py` → Create comprehensive shim

---

## Phase 4: Infrastructure (71 files)

### Redis Client (15 files)
#### Connection
- [ ] `infrastructure/external/redis_client/client.py`
- [ ] `infrastructure/external/redis_client/core.py`

#### Repositories
- [ ] `infrastructure/external/redis_client/trade_counter_repo.py`
- [ ] `infrastructure/external/redis_client/cost_repo.py`
- [ ] `infrastructure/external/redis_client/position_repo.py`
- [ ] `infrastructure/external/redis_client/price_repo.py`
- [ ] `infrastructure/external/redis_client/balance_cache.py`
- [ ] `infrastructure/external/redis_client/market_cache.py`
- [ ] `infrastructure/external/redis_client/position_layers_repo.py`
- [ ] `infrastructure/external/redis_client/bot_status_repo.py`
- [ ] `infrastructure/external/redis_client/mexc_raw_repo.py`
- [ ] `infrastructure/external/redis_client/trade_history_repo.py`

#### Shims
- [ ] `infrastructure/external/redis_client/__init__.py`
- [ ] `infrastructure/external/__init__.py`

### MEXC Client (~40 files)
#### Authentication
- [ ] `infrastructure/external/mexc_client/utils/signature.py`
- [ ] `infrastructure/external/mexc_client/utils/parser.py`
- [ ] `infrastructure/external/mexc_client/utils/types.py`

#### Market Endpoints
- [ ] `infrastructure/external/mexc_client/endpoints/market.py` (split)

#### Account Endpoints
- [ ] `infrastructure/external/mexc_client/endpoints/account.py` (split)

#### Trade Endpoints
- [ ] `infrastructure/external/mexc_client/endpoints/order.py` (split)

#### Sub-Account
- [ ] `infrastructure/external/mexc_client/endpoints/sub_account.py`
- [ ] `infrastructure/external/mexc_client/endpoints/helpers.py`

#### WebSocket
- [ ] `infrastructure/external/mexc_client/ws_client.py`
- [ ] `infrastructure/external/mexc_client/ws_channels.py`

#### Client Core
- [ ] `infrastructure/external/mexc_client/connection.py`
- [ ] `infrastructure/external/mexc_client/account.py`
- [ ] `infrastructure/external/mexc_client/client.py`
- [ ] `infrastructure/external/mexc_client/trade_repo.py`

#### Adapters (create new)
- [ ] Create `adapters/market_adapter.py`
- [ ] Create `adapters/account_adapter.py`

#### Shims
- [ ] `infrastructure/external/mexc_client/__init__.py`

### Bot Runtime (8 files)
- [ ] `infrastructure/bot/bot_core/core.py`
- [ ] `infrastructure/bot/bot_core/startup.py`
- [ ] `infrastructure/bot/bot_core/cleanup.py`
- [ ] `infrastructure/bot/bot_core/execution.py`
- [ ] `infrastructure/bot/bot_core/strategy.py`
- [ ] `infrastructure/bot/bot_core/risk.py`
- [ ] `infrastructure/bot/bot_core/data_collection.py`
- [ ] `infrastructure/bot/bot_utils.py`

### Config
- [ ] Verify `infrastructure/config/` completeness
- [ ] Create shim if needed

### Infrastructure Shims
- [ ] `infrastructure/__init__.py` → Comprehensive shim

---

## Phase 5: Services (18 files)

### Market Services (10 files)
- [ ] `services/market/market_service_core.py`
- [ ] `services/market/cache_policy.py`
- [ ] `services/market/cache_service.py`
- [ ] `services/market/cache_strategy.py`
- [ ] `services/market/market_service.py`
- [ ] `services/market/mexc_client_service.py`
- [ ] `services/market/price_history_manager.py`
- [ ] `services/market/price_repo_service.py`
- [ ] `services/market/price_resolver.py`
- [ ] `services/market/__init__.py` → Shim

### Account Services (verified)
- [ ] Verify `services/account/` fully migrated
- [ ] Update shims if needed

### Trading Service Core
- [ ] Split `services/trading/trading_service_core.py` (11939 bytes)
  - [ ] Create `_trading_service_init.py`
  - [ ] Create `_trading_service_execute.py`
  - [ ] Create `_trading_service_finalize.py`
  - [ ] Create `_trading_service.py` (main)
- [ ] Update imports in src/app files
- [ ] Update `services/trading/__init__.py` shim

### Services Main Shim
- [ ] `services/__init__.py` → Comprehensive shim

---

## Phase 6: API Layer (32 files)

### Analysis
- [ ] Map all API imports to dependencies
- [ ] Identify which need adapters

### Market Routes (8 files)
- [ ] `api/market/price.py`
- [ ] `api/market/ticker.py`
- [ ] `api/market/orderbook.py`
- [ ] `api/market/klines.py`
- [ ] `api/market/exchange_info.py`
- [ ] `api/market/book_ticker.py`
- [ ] `api/market/agg_trades.py`
- [ ] Update `src/app/interfaces/http/market.py`

### Account Routes (5 files)
- [ ] `api/account/balance.py`
- [ ] `api/account/orders.py`
- [ ] `api/account/trades.py`
- [ ] `api/account/position.py`
- [ ] Update `src/app/interfaces/http/account.py`

### Bot Routes (3 files)
- [ ] `api/bot/start.py`
- [ ] `api/bot/stop.py`
- [ ] `api/bot/status.py`
- [ ] Update `src/app/interfaces/http/bot.py`

### Status Routes
- [ ] `api/status/health.py`
- [ ] `api/status/metrics.py`
- [ ] Update `src/app/interfaces/http/status.py`

### Sub-Account Routes
- [ ] `api/sub_account/*.py`
- [ ] Update `src/app/interfaces/http/sub_account.py`

### Route Files
- [ ] `api/market_routes.py`
- [ ] `api/account_routes.py`
- [ ] `api/bot_routes.py`
- [ ] `api/status_routes.py`
- [ ] `api/sub_account_routes.py`

### Main Entry
- [ ] Update `main.py` to only import from `src/app/interfaces/http/`

---

## Phase 7: Legacy Cleanup

### Verification
- [ ] Search for legacy imports in src/app
  ```bash
  grep -r "from domain" src/app --include="*.py"
  grep -r "from infrastructure" src/app --include="*.py" | grep -v "from src"
  grep -r "from api\." src/app --include="*.py"
  grep -r "from services" src/app --include="*.py" | grep -v "from src"
  grep -r "from repositories" src/app --include="*.py" | grep -v "from src"
  ```
- [ ] Fix any remaining imports

### Testing
- [ ] Run full test suite: `pytest tests/`
- [ ] Manual API testing all endpoints
- [ ] Test application startup
- [ ] Verify bot execution
- [ ] Check logs for errors

### Removal
- [ ] Delete `/domain/` directory
- [ ] Delete `/infrastructure/` directory
- [ ] Delete `/api/` directory
- [ ] Delete `/services/` directory
- [ ] Delete `/repositories/` directory

### Documentation
- [ ] Update README.md
- [ ] Update ARCHITECTURE_TREE.md
- [ ] Add migration completion note
- [ ] Create ADR (Architecture Decision Record)

---

## Commit Tracking

### Completed Commits
1. ✅ Migrate repositories layer to src/app/infrastructure/persistence/redis/repos
2. ✅ Migrate trading service helpers to src/app/application/trading
3. ✅ Update trading_service_core imports to use new structure

### Planned Commits
4. ⏳ Migrate domain interfaces to src/app/domain/ports
5. ⏳ Migrate domain risk_manager to src/app/domain/risk
6. ⏳ Migrate domain trading_strategy to src/app/domain/strategies
7. ⏳ Migrate domain position_manager to src/app/domain/position
8. ⏳ Migrate Redis client to src/app/infrastructure/persistence/redis
9. ⏳ Migrate MEXC client (part 1) to src/app/infrastructure/exchange/mexc
10. ⏳ Migrate MEXC client (part 2) - adapters and integration
11. ⏳ Migrate bot runtime to src/app/infrastructure/bot_runtime
12. ⏳ Migrate market services to src/app/application/market
13. ⏳ Split and migrate trading_service_core
14. ⏳ Migrate API market routes to src/app/interfaces/http
15. ⏳ Migrate API account routes to src/app/interfaces/http
16. ⏳ Migrate API bot routes to src/app/interfaces/http
17. ⏳ Migrate remaining API routes to src/app/interfaces/http
18. ⏳ Final cleanup: remove legacy directories

---

## Notes

- All new files must be <4000 bytes
- Create shims for backward compatibility
- Test after each major component
- Commit after each phase
- No breaking changes allowed
- Document any deviations

---

**End of Checklist**
