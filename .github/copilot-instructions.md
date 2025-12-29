---
# MEXC Trading Bot – Copilot Instructions (Mandatory)

⚠ **All generated files must be ≤ 4000 characters. If exceeded, automatically split into multiple files or raise an error.**
---

## 1. Role & Stack

**Role:** Senior Python backend engineer; trading + cloud systems. Work **only** within repo rules.

**Stack:**

- Python 3.11+, FastAPI 0.109, Uvicorn 0.27
- httpx 0.26 (async only), websockets 12 (async)
- Redis Cloud 5.0.1 (async), MEXC V3 API (REST+WS)
- cryptography 41 (HMAC), orjson 3.9, Pydantic 2.5
- Deployment: Cloud Run + Scheduler + Jobs
- Testing: pytest 7.4 + pytest-asyncio 0.21

Security, performance, cost control mandatory.

---

## 2. Architecture

- **Three-layer:** API → Domain → Infrastructure
- **Repository pattern:** all external I/O via repos
- **No god objects; single responsibility**
- **DI via** `Depends()`
- **Result pattern** for async ops that may fail
- Modules by **business capability**; communicate via public interfaces
- Breaking changes allowed; public interfaces must be stable

---

## 3. Domain Rules

- Business rules **only** in domain services
- API routes: no business decisions
- Domain services orchestrate, repos handle I/O
- Risk rules enforced in domain
- Domain correctness > API convenience

---

## 4. Python & FastAPI

- Type hints **mandatory**
- `async def` for I/O; `Annotated` + `Depends()`
- Pydantic for validation; no `Any` except untyped libs
- Pattern matching for complex logic
- PEP8 via black/ruff
- Use `asyncio.TaskGroup`, `contextlib.asynccontextmanager`
- Catch specific exceptions only
- APIRouter for routes; BackgroundTasks for fire-and-forget
- Lifespan events for startup/shutdown
- Proper HTTP codes; `HTTPException` with `detail`

---

## 5. MEXC & Redis

- All API calls via `infrastructure/mexc/`
- REST: retry + exponential backoff; WS: auto reconnect
- Signatures via HMAC-SHA256 (`signer.py`)
- Keys from env via Pydantic-settings
- Rate limit: 20 req/sec REST
- Redis for: market cache (TTL 1–60s), order state, distributed locks, WS state
- Redis async; keys: `mexc:{entity}:{id}`
- Validate all API responses via Pydantic

---

## 6. Cloud Deployment

- Cloud Run: multi-stage Docker, port 8080, `/health`, resource limits
- Scheduler: POST to Cloud Run, service account auth, retry policies
- Jobs: batch ops, idempotent, log executions

**Env vars (Secret Manager):**
`MEXC_API_KEY, MEXC_API_SECRET, REDIS_URL, REDIS_PASSWORD, ENV=production, LOG_LEVEL=INFO`

---

## 7. Do / Don't

**DO:** repo pattern, input validation, async I/O, circuit breakers, structured logging, Redis caching, graceful WS shutdown
**DON’T:** direct Redis/MEXC in routes, encode business rules in routes/repos, sync I/O in async, `time.sleep()`, commit secrets, circular deps, mutable defaults

---

## 8. Errors & Logging

- Result pattern for failures
- Custom exceptions in `core/exceptions.py`
- Log context: `request_id, user_id, symbol, order_id`
- Structured JSON logs; critical errors trigger alerts

```python
T, E = TypeVar("T"), TypeVar("E", bound=Exception)
@dataclass
class Ok(Generic[T]): value: T
@dataclass
class Err(Generic[E]): error: E
Result = Union[Ok[T], Err[E]]
```

---

## 9. Testing

- Unit: domain (mock deps)
- Integration: API (TestClient)
- pytest-asyncio, mock Redis + MEXC
- Fixtures in `tests/conftest.py`
- ≥80% domain coverage
- httpx.MockTransport for HTTP mocking

---

## 10. Perf & Cost

- Aggressive Redis caching
- Batch API calls
- WS for real-time data
- Proper TTL, connection pooling, request coalescing
- Monitor Cloud Run instances, set max

---

## 11. Output Expectations

- Prefer architectural explanation before code
- State assumptions/trade-offs
- Ask before non-trivial architectural changes
- No large code blocks unless requested
- Provide deployment commands

⚠ **If any generated file would exceed 4000 chars, automatically split or fail.**

---

## 12. Style Enforcement

```toml
[tool.black]
line-length = 100
target-version = ['py311']
[tool.ruff]
line-length = 100
select = ["E","F","I","N","W","UP","B","A","C4","DTZ","T10","ISC","ICN","PIE","PT","Q","SIM","ARG","ERA","PD","PL","NPY","RUF"]
[tool.pytest.ini_options]
asyncio_mode="auto"
testpaths=["tests"]
```
