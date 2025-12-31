<!-- markdownlint-disable-file -->
# Release Changes: Limit klines to QRLUSDT

**Related Plan**: none
**Implementation Date**: 2025-12-31

## Summary

Restricted klines endpoint to only serve QRL/USDT, documented the limitation, and added tests to enforce the behavior.

## Changes

### Added

- None

### Modified

- src/app/interfaces/http/market.py - Normalize symbols and reject non-QRLUSDT klines with a 404.
- tests/test_market_routes.py - Added coverage for klines symbol validation and normalization.
- README.md - Documented that the klines endpoint only supports QRL/USDT.

### Removed

- None

## Release Summary

**Total Files Affected**: 3

### Files Created (0)

- None

### Files Modified (3)

- src/app/interfaces/http/market.py - Enforce QRLUSDT-only klines and surface proper HTTP errors.
- tests/test_market_routes.py - Added klines validation tests for normalized symbol and rejection path.
- README.md - Noted klines endpoint only supports QRL/USDT.

### Files Removed (0)

- None

### Dependencies & Infrastructure

- **New Dependencies**: none
- **Updated Dependencies**: none
- **Infrastructure Changes**: none
- **Configuration Updates**: none

### Deployment Notes

No deployment impact; API now returns 404 for non-QRLUSDT klines.
