# QRL Trading API Architecture Restructure Visual Guide

## Before & After Comparison

### Current Structure (Before)

```
src/app/
├── domain/
│   ├── events/                    [✅ Keep, Move to domain/trading/]
│   │   └── trading_events.py
│   ├── models/                    [⚠️ Split & Reorganize]
│   │   ├── order.py              → entities/
│   │   ├── trade.py              → entities/
│   │   ├── position.py           → entities/
│   │   ├── account.py            → entities/
│   │   ├── price.py              → value_objects/
│   │   └── balance.py            → value_objects/
│   ├── ports/                     [❌ MOVE to application/]
│   │   ├── account_port.py
│   │   ├── execution_port.py
│   │   ├── market_port.py
│   │   └── ...
│   ├── position/                  [⚠️ Move to services/]
│   │   ├── calculator.py
│   │   └── updater.py
│   ├── risk/                      [⚠️ Move to services/]
│   │   ├── limits.py
│   │   └── validators/
│   └── strategies/                [✅ Keep, Move to domain/trading/]
│       ├── base.py
│       ├── indicators/
│       └── filters/
│
├── application/
│   ├── account/                   [❌ CONSOLIDATE into trading/]
│   │   ├── balance_service.py
│   │   ├── get_balance.py
│   │   └── ...
│   ├── bot/                       [❌ CONSOLIDATE into trading/]
│   │   ├── start.py
│   │   ├── status.py
│   │   └── stop.py
│   ├── market/                    [❌ CONSOLIDATE into trading/]
│   │   ├── get_price.py
│   │   ├── get_klines.py
│   │   └── ...
│   └── trading/                   [⚠️ REORGANIZE]
│       ├── execute_trade.py
│       ├── services/
│       └── ...
│
├── infrastructure/
│   ├── external/                  [❌ REMOVE]
│   │   └── mexc/                 [❌ DUPLICATE - Remove]
│   ├── exchange/                  [✅ Keep & Enhance]
│   │   └── mexc/
│   │       ├── rest_client.py
│   │       └── ws_client.py
│   ├── redis/                     [✅ Keep]
│   ├── scheduler/                 [✅ Keep]
│   └── bot_runtime/               [⚠️ Review]
│
└── interfaces/
    ├── http/                      [✅ Keep]
    │   └── routes/
    ├── tasks/                     [⚠️ RENAME to background/]
    └── templates/                 [✅ Keep]
```

### Target Structure (After)

```
src/app/
├── domain/
│   └── trading/                   [🔴 NEW: Business Truth]
│       ├── entities/              [NEW]
│       │   ├── order.py          ← from models/
│       │   ├── trade.py          ← from models/
│       │   ├── position.py       ← from models/
│       │   └── account.py        ← from models/
│       ├── value_objects/         [NEW]
│       │   ├── symbol.py         [NEW]
│       │   ├── price.py          ← from models/
│       │   ├── quantity.py       [NEW]
│       │   ├── leverage.py       [NEW]
│       │   └── balance.py        ← from models/
│       ├── strategies/            ← from strategies/
│       │   ├── base.py
│       │   ├── signal.py
│       │   └── indicators/
│       ├── services/              [NEW]
│       │   ├── risk_service.py   ← from risk/
│       │   ├── position_service.py ← from position/
│       │   └── validators/       ← from risk/validators/
│       ├── events/                ← from events/
│       │   ├── signal_generated.py
│       │   ├── order_requested.py
│       │   └── position_updated.py
│       ├── repositories.py        [NEW: Interfaces only]
│       └── errors.py              [NEW: Domain exceptions]
│
├── application/
│   └── trading/                   [🟠 NEW: Use Case Orchestration]
│       ├── use_cases/             [NEW]
│       │   ├── execute_trade.py  ← from trading/
│       │   ├── get_balance.py    ← from account/
│       │   ├── get_price.py      ← from market/
│       │   └── sync_state.py     [NEW]
│       ├── services/              [Reorganized]
│       │   ├── trading_bot_service.py ← from bot/
│       │   ├── execution_service.py
│       │   └── market_service.py
│       ├── ports/                 [NEW]
│       │   ├── exchange_port.py  ← from domain/ports/
│       │   ├── market_data_port.py ← from domain/ports/
│       │   └── position_repo_port.py
│       ├── dtos/                  [NEW]
│       │   ├── signal_dto.py
│       │   ├── order_dto.py
│       │   └── position_dto.py
│       └── commands/              [NEW]
│           ├── place_order_cmd.py
│           └── update_position_cmd.py
│
├── infrastructure/                [🟡 Technical Implementation]
│   ├── exchange/
│   │   └── mexc/                 [Consolidated & Enhanced]
│   │       ├── rest_client.py   [httpx]
│   │       ├── ws_client.py     [websockets]
│   │       ├── signer.py        [HMAC SHA256]
│   │       ├── adapters.py      [Port implementations]
│   │       └── protobuf_decoder.py
│   ├── redis/
│   │   ├── client.py
│   │   ├── position_cache.py
│   │   └── lock.py
│   └── scheduler/
│       └── jobs.py
│
└── interfaces/                    [🟢 I/O Layer]
    ├── http/
    │   ├── routes/
    │   │   ├── trading.py
    │   │   ├── market.py
    │   │   └── account.py
    │   ├── schemas.py            [Pydantic]
    │   └── deps.py
    ├── background/                ← renamed from tasks/
    │   └── scheduler_tasks.py
    ├── websocket/                 [NEW if needed]
    │   └── market_stream.py
    └── templates/                 [Keep]
        └── dashboard.html
```

## Migration Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     PHASE 1: DOMAIN                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  domain/models/*.py                                         │
│         ↓                                                   │
│  ┌──────────────┐              ┌──────────────────┐        │
│  │   Entities   │              │  Value Objects   │        │
│  │  (mutable)   │              │   (immutable)    │        │
│  └──────────────┘              └──────────────────┘        │
│         ↓                               ↓                   │
│  domain/trading/entities/     domain/trading/value_objects/│
│                                                             │
│  domain/position/ & domain/risk/                           │
│         ↓                                                   │
│  domain/trading/services/                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   PHASE 2: APPLICATION                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  application/{account,bot,market}/                         │
│         ↓                                                   │
│  ┌──────────────┐    ┌──────────────┐    ┌─────────────┐  │
│  │  Use Cases   │    │   Services   │    │    Ports    │  │
│  └──────────────┘    └──────────────┘    └─────────────┘  │
│         ↓                    ↓                    ↓         │
│  application/trading/use_cases/                            │
│  application/trading/services/                             │
│  application/trading/ports/                                │
│                                                             │
│  + NEW: dtos/, commands/                                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                 PHASE 3: INFRASTRUCTURE                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  infrastructure/external/mexc/  ──┐                        │
│                                   ↓                         │
│  infrastructure/exchange/mexc/ ──→ CONSOLIDATE             │
│                                   ↓                         │
│  infrastructure/exchange/mexc/                             │
│    ├── rest_client.py     (HTTP)                           │
│    ├── ws_client.py       (WebSocket)                      │
│    ├── signer.py          (HMAC)                           │
│    └── adapters.py        (Port Impl)                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    PHASE 4: INTERFACES                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  interfaces/tasks/                                         │
│         ↓                                                   │
│  interfaces/background/  (renamed)                         │
│                                                             │
│  + NEW: websocket/ (if needed)                            │
│  + NEW: cli/ (if needed)                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Dependency Flow (After Restructure)

```
┌────────────────────────────────────────────────────────────┐
│                      INTERFACES                            │
│                (FastAPI / WS / REST)                       │
└───────────────────┬────────────────────────────────────────┘
                    │ depends on
                    ↓
┌────────────────────────────────────────────────────────────┐
│                     APPLICATION                            │
│               (Use Cases / Services)                       │
└───────────────────┬────────────────────────────────────────┘
                    │ depends on
                    ↓
┌────────────────────────────────────────────────────────────┐
│                       DOMAIN                               │
│                  (Business Truth)                          │
└────────────────────▲───────────────────────────────────────┘
                     │ implements
                     │
┌────────────────────┴───────────────────────────────────────┐
│                  INFRASTRUCTURE                            │
│          (Redis / MEXC / Scheduler)                        │
└────────────────────────────────────────────────────────────┘
```

## Key Architectural Boundaries

### ✅ ALLOWED Dependencies

```
Interfaces    → Application → Domain
Infrastructure → Domain (via interfaces)
Infrastructure → Application (via ports)
```

### ❌ FORBIDDEN Dependencies

```
Domain       ↛ Application
Domain       ↛ Infrastructure
Domain       ↛ Interfaces
Application  ↛ Interfaces
```

## File Movement Checklist

### Domain Layer
- [ ] `domain/models/order.py` → `domain/trading/entities/order.py`
- [ ] `domain/models/trade.py` → `domain/trading/entities/trade.py`
- [ ] `domain/models/position.py` → `domain/trading/entities/position.py`
- [ ] `domain/models/account.py` → `domain/trading/entities/account.py`
- [ ] `domain/models/price.py` → `domain/trading/value_objects/price.py`
- [ ] `domain/models/balance.py` → `domain/trading/value_objects/balance.py`
- [ ] `domain/strategies/*` → `domain/trading/strategies/`
- [ ] `domain/events/*` → `domain/trading/events/`
- [ ] `domain/position/*` → `domain/trading/services/position/`
- [ ] `domain/risk/*` → `domain/trading/services/risk/`

### Application Layer
- [ ] `domain/ports/*` → `application/trading/ports/`
- [ ] `application/account/*` → `application/trading/use_cases/`
- [ ] `application/market/*` → `application/trading/use_cases/`
- [ ] `application/bot/*` → `application/trading/services/bot/`
- [ ] Existing `application/trading/*` → Reorganize into new structure

### Infrastructure Layer
- [ ] Consolidate `infrastructure/external/mexc/` into `infrastructure/exchange/mexc/`
- [ ] Ensure proper MEXC structure: rest_client, ws_client, signer, adapters

### Interfaces Layer
- [ ] Rename `interfaces/tasks/` → `interfaces/background/`
- [ ] Create `interfaces/websocket/` if needed
- [ ] Create `interfaces/cli/` if needed

## Testing Strategy

### Per-Phase Testing

**Phase 1 (Domain):**
```bash
# Test domain layer only
pytest tests/domain/ -v

# Check no forbidden imports
grep -r "import fastapi\|import redis\|import httpx" src/app/domain/
```

**Phase 2 (Application):**
```bash
# Test application layer
pytest tests/application/ -v

# Check proper dependency direction
python architecture_guard.py --check-application
```

**Phase 3 (Infrastructure):**
```bash
# Test infrastructure
pytest tests/infrastructure/ -v

# Verify MEXC consolidation
ls -la src/app/infrastructure/exchange/mexc/
```

**Phase 4 (Interfaces):**
```bash
# Test API endpoints
pytest tests/interfaces/ -v

# Manual API testing
curl http://localhost:8080/health
```

**Phase 5 (Integration):**
```bash
# Full test suite
pytest -v

# Architecture validation
python architecture_guard.py --full-check
```

## Success Metrics

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Domain purity | ~90% | 100% | [ ] |
| Proper layering | ~75% | 100% | [ ] |
| Test coverage | ~85% | ≥85% | [ ] |
| Architecture violations | ~5 | 0 | [ ] |
| Import errors | 0 | 0 | [ ] |
| Functional regressions | 0 | 0 | [ ] |

## References

- [✨.md](./✨.md) - Clean Architecture specification
- [ARCHITECTURE_RESTRUCTURE_PLAN.md](./ARCHITECTURE_RESTRUCTURE_PLAN.md) - Detailed plan
- `architecture_guard.py` - Validation tool
