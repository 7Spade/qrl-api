# src/app skeleton

This directory mirrors the target layered layout described in `ARCHITECTURE_TREE.md`,
`結構.md`, and `調整結構.md`. The current runtime still uses the legacy modules in the
repository root (`api/`, `services/`, `repositories/`, `infrastructure/`); nothing has
been moved yet to avoid breaking behavior.

## Mapping (legacy → target)
- `api/` → `interfaces/http/`
- `infrastructure/tasks/` → `interfaces/tasks/`
- `services/` + `repositories/` → `application/`
- `domain/interfaces/` → `domain/ports/`
- `infrastructure/external/mexc_client/` → `infrastructure/exchange/mexc/`
- `infrastructure/external/redis_client/` → `infrastructure/persistence/redis/`
- `infrastructure/utils/` → `shared/`

## Notes
- All folders currently contain empty `__init__.py` files as placeholders.
- `bootstrap.py` will later assemble the application; `main.py` remains the active
  entrypoint for now.
- Keep new files ≤ 4000 characters to avoid oversized modules; when a file grows
  toward the limit, split by responsibility (e.g., per use case or endpoint).
- HTTP shims (`interfaces/http/*.py`) currently re-export legacy routers from `api/*`
  so routing behavior remains unchanged while migrations proceed.
