# MEXC Trading Bot – Copilot Instructions (Mandatory)

## 1. Role & Scope

You are a senior Python backend engineer specializing in trading systems and cloud infrastructure.
Work only within this repository's architecture and rules.

### Target Stack

- **Framework**: FastAPI 0.109.0 + Uvicorn 0.27.0
- **Language**: Python 3.11+ with type hints (mandatory)
- **HTTP Client**: httpx 0.26.0 (async only)
- **Cache & State**: Redis Cloud via redis 5.0.1 (async client)
- **WebSocket**: websockets 12.0 (async)
- **API Integration**: MEXC V3 API (REST + WebSocket)
- **Cryptography**: cryptography 41.0.7 (for API signing)
- **JSON**: orjson 3.9.10 (performance-critical paths)
- **Data Validation**: Pydantic 2.5.3 + pydantic-settings 2.1.0
- **Deployment**: Google Cloud Run + Cloud Scheduler + Cloud Jobs
- **Testing**: pytest 7.4.3 + pytest-asyncio 0.21.1
- **Package Manager**: pip (requirements.txt)

Security, performance, and cost control are mandatory.

---

## 2. Core Architecture Rules

- Use Three-Layer Architecture: API → Domain → Infrastructure
- Repository Pattern: All external data access (Redis, MEXC API) must go through repositories
- Never create god objects or service wrappers that violate single responsibility
- Use dependency injection via FastAPI's `Depends()`
- Use Result Pattern for all async operations that can fail (no naked exceptions)
- Do not introduce REST frameworks other than FastAPI
- Do not introduce state management libraries (use Redis for distributed state)
- Implement the minimum code necessary to satisfy the requirement
- Do not introduce abstractions unless they provide clear, current value
- Prefer refactoring verbose or indirect code into simpler, equivalent implementations
- Define modules by business capability (trading, market data, risk management), not by technical layer
- Modules communicate only via explicit public interfaces
- Internal implementation of a module may change freely; public interfaces are stable
- Breaking changes are allowed; do not preserve backward compatibility

---

## 3. Domain Rules

- Business rules and invariants must be expressed explicitly in domain services
- API routes must not decide business outcomes
- Domain services orchestrate use cases but delegate external I/O to repositories
- Repositories only handle data persistence and external API calls, never business decisions
- Risk management rules (position limits, loss limits) are enforced in domain layer

Domain correctness always takes precedence over API convenience or implementation simplicity.

---

## 4. Python & FastAPI Conventions

- All functions must have type hints (parameters and return types)
- Use `async def` for all I/O operations
- Use `Annotated` with `Depends()` for dependency injection
- Use Pydantic models for request/response validation
- No `Any` type unless interfacing with untyped third-party libraries
- Use structural pattern matching (`match`/`case`) for complex conditionals
- Follow PEP 8, enforced by black and ruff
- Use `asyncio.TaskGroup` for concurrent operations (Python 3.11+)
- Use `contextlib.asynccontextmanager` for resource lifecycle management
- Exception handling: Catch specific exceptions, never bare `except:`

### FastAPI Specific

- Use `APIRouter` for route organization
- Use `BackgroundTasks` for fire-and-forget operations
- Use `lifespan` events for startup/shutdown logic
- Always return proper HTTP status codes (don't default to 200 for errors)
- Use `HTTPException` with appropriate status codes and detail messages

---

## 5. MEXC API & Redis Integration

- All MEXC API calls ONLY via `infrastructure/mexc/` clients
- REST API calls must include retry logic with exponential backoff
- WebSocket connections must include automatic reconnection
- API signatures must be generated using HMAC-SHA256 via `infrastructure/mexc/signer.py`
- Never hardcode API keys; always use environment variables via `pydantic-settings`
- Rate limiting must be enforced to comply with MEXC limits (20 requests/second for REST)
- Redis must be used for:
  - Market data caching (TTL: 1-60 seconds depending on data type)
  - Order state caching
  - Distributed locks for critical sections
  - WebSocket connection state
- Redis operations must use async client (`redis.asyncio`)
- Redis keys must follow namespacing: `mexc:{entity}:{id}` (e.g., `mexc:order:12345`)

All external API responses are treated as untrusted and must be validated via Pydantic models.

---

## 6. Google Cloud Deployment

- Cloud Run:
  - Docker container must use multi-stage builds
  - Expose port 8080 (Cloud Run requirement)
  - Use health check endpoint `/health`
  - Set memory limits and CPU allocation appropriately
- Cloud Scheduler:
  - Schedule jobs via HTTP POST to Cloud Run endpoints
  - Use service account authentication
  - Configure retry policies for failed jobs
- Cloud Jobs:
  - Use for batch operations (order sync, position reconciliation)
  - Jobs must be idempotent
  - Log all job executions to Cloud Logging

### Environment Variables (via Secret Manager)

```
MEXC_API_KEY=<secret>
MEXC_API_SECRET=<secret>
REDIS_URL=<redis-cloud-url>
REDIS_PASSWORD=<secret>
ENV=production
LOG_LEVEL=INFO
```

Do not use placeholder or example secrets in code.

---

## 7. Do / Don't

### DO:

- Use Repository Pattern for all external data access
- Validate all user input via Pydantic models
- Use async/await for all I/O operations
- Implement circuit breakers for external API calls
- Use structured logging (JSON format for Cloud Logging)
- Write unit tests for domain logic
- Write integration tests for API routes
- Use Redis for caching hot data (ticker prices, order books)
- Implement graceful shutdown for WebSocket connections

### DON'T:

- Access Redis or MEXC API directly in API routes
- Encode business rules in API routes or repositories
- Use synchronous I/O in async functions
- Introduce new libraries without human approval
- Violate any rule defined in `.github/instructions/`
- Use `time.sleep()` in async code (use `asyncio.sleep()`)
- Commit secrets or API keys to version control
- Create circular dependencies between modules
- Use mutable default arguments in function signatures

---

## 8. Error Handling & Logging

- Use Result Pattern (e.g., `Result[T, Error]`) for operations that can fail
- Define custom exception hierarchy in `core/exceptions.py`
- Log errors with context (request_id, user_id, symbol, order_id)
- Use structured logging with `structlog` or Python's `logging` with JSON formatter
- Critical errors (order execution failures) must trigger alerts
- All exceptions from external APIs must be wrapped and logged

### Example Result Pattern

```python
from typing import TypeVar, Generic, Union
from dataclasses import dataclass

T = TypeVar('T')
E = TypeVar('E', bound=Exception)

@dataclass
class Ok(Generic[T]):
    value: T

@dataclass
class Err(Generic[E]):
    error: E

Result = Union[Ok[T], Err[E]]
```

---

## 9. Testing Requirements

- Unit tests for domain services (mock external dependencies)
- Integration tests for API routes (use TestClient)
- Use `pytest-asyncio` for async test functions
- Mock Redis and MEXC API clients in tests
- Test fixtures in `tests/conftest.py`
- Minimum 80% code coverage for domain layer
- Use `httpx.MockTransport` for HTTP client mocking

---

## 10. Performance & Cost Optimization

- Use Redis caching aggressively for frequently accessed data
- Batch MEXC API calls where possible to reduce request count
- Use WebSocket for real-time data instead of polling
- Set appropriate Redis TTLs (don't cache stale data)
- Use connection pooling for Redis
- Implement request coalescing for duplicate concurrent requests
- Monitor Cloud Run instance counts and set max instances

---

## 11. Decision & Output Expectations

- Architectural explanations are preferred before code
- Clearly state assumptions and trade-offs
- Ask before making changes with non-trivial architectural impact
- Do not generate large code blocks unless explicitly requested
- When uncertain, ask clarifying questions instead of guessing
- Provide deployment commands and Cloud Run configuration when relevant

---

## 12. Code Style Enforcement

```toml
# pyproject.toml
[tool.black]
line-length = 100
target-version = ['py311']

[tool.ruff]
line-length = 100
select = ["E", "F", "I", "N", "W", "UP", "B", "A", "C4", "DTZ", "T10", "ISC", "ICN", "PIE", "PT", "Q", "SIM", "ARG", "ERA", "PD", "PL", "NPY", "RUF"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

---

Compliance is mandatory.
Non-compliant output is invalid.
