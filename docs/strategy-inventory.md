---
post_title: 'Strategy Inventory Report'
author1: 'Copilot Agent'
post_slug: 'strategy-inventory-report'
microsoft_alias: 'copilot'
featured_image: 'none'
categories:
  - 'documentation'
tags:
  - 'strategy'
  - 'inventory'
ai_note: 'Generated with assistance from GitHub Copilot'
summary: 'Current implemented strategies in the qrl-api codebase.'
post_date: '2025-12-31'
---

## Purpose
Summarize strategies that are already implemented in the repository to clarify what the bot currently supports.

## Trading strategies in code
### Moving Average crossover with cost filter
- Location: `src/app/domain/strategies/trading_strategy.py`.
- Defaults pull `MA_SHORT_PERIOD` and `MA_LONG_PERIOD` from `src/app/infrastructure/config/settings.py` (7 and 25 by default).
- Logic: calculates short/long simple moving averages; returns `HOLD` if inputs are missing. Generates `BUY` when the short MA is above the long MA and the current price is at or below average cost, and `SELL` when the short MA is below the long MA and price exceeds average cost by ~3%; otherwise `HOLD`.
- Includes `calculate_signal_strength` to quantify MA spread and `calculate_moving_average` helper.

### Runtime MA spread threshold
- Location: `src/app/infrastructure/bot_runtime/phases/strategy.py`.
- Uses shared helpers in `src/app/infrastructure/bot_runtime/utils.py` to derive short/long MAs with the same configured periods.
- Signal rule: if short MA exceeds long MA by `config.SIGNAL_THRESHOLD` the phase emits `BUY`; if short MA is below long MA by the same threshold it emits `SELL`; otherwise it emits `HOLD`. Falls back to `HOLD` when there is insufficient price history.

### Strategy wrappers and service surface
- `src/app/domain/strategies/base.py` defines the `BaseStrategy` protocol contract.
- `src/app/domain/strategies/example_strategy.py` simply reuses `TradingStrategy` while satisfying the protocol.
- `src/app/application/trading/services/trading/strategy_service.py` currently acts as a stub and returns `HOLD` until expanded, so no additional strategy logic is present there.

## Supporting strategy utilities
- `src/app/application/trading/services/market/cache_strategy.py` wraps market responses with source and timestamp metadata for cache-aware behavior.
