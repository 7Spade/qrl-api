<!-- markdownlint-disable-file -->
# Release Changes: Strategy runtime runbook

**Related Plan**: none  
**Implementation Date**: 2025-12-31

## Summary

Recorded the processing request per instructions and documented a concise runtime path to start the bot, trigger strategies, and align execution with Context7/CCXT exchange call ordering.

## Changes

### Added

- Copilot-Processing.md - Captures the incoming user request and processing note.

### Modified

- docs/05-Strategies-and-Data.md - Added a strategy runtime quickstart with `/control` + `/execute` steps and a Context7/CCXT call-sequence reminder to avoid stale quotes.

### Removed

- none

## Release Summary

**Total Files Affected**: 2

### Files Created (1)

- Copilot-Processing.md - Processing tracker for this task.

### Files Modified (1)

- docs/05-Strategies-and-Data.md - Runtime quickstart and trading flow guidance.

### Files Removed (0)

- none

### Dependencies & Infrastructure

- **New Dependencies**: none
- **Updated Dependencies**: none
- **Infrastructure Changes**: none
- **Configuration Updates**: none

### Deployment Notes

Documentation-only; no runtime changes. Keep Redis and API endpoints aligned with the quickstart when exercising strategies.
