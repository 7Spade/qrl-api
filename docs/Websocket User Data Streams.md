## Websocket User Data Streams (V3, protobuf)

- REST base: `https://api.mexc.com`. WS base: `wss://wbs-api.mexc.com/ws?listenKey=<key>`.
- listenKey valid 60m; refresh with `PUT` every ≤30m; `DELETE` to close. Each key supports 5 WS links; up to 60 keys/UID. Connections max 24h.
- Default private channels: `spot@private.account.v3.api.pb`, `spot@private.deals.v3.api.pb`, `spot@private.orders.v3.api.pb`.

Subscribe example:
```json
{"method":"SUBSCRIPTION","params":["spot@private.orders.v3.api.pb"]}
```

### ListenKey endpoints
- `POST /api/v3/userDataStream` → `{"listenKey": "..."}` (start)
- `GET /api/v3/userDataStream` → list valid keys
- `PUT /api/v3/userDataStream` with `listenKey` → extend 60m
- `DELETE /api/v3/userDataStream` with `listenKey` → close

### Protocol Buffers integration
- Schema: https://github.com/mexcdevelop/websocket-proto; bindings already in `src/app/infrastructure/external/proto/websocket_pb/`.
- Default decoder: `decode_push_data` (used by WS helpers).
- Private stream sample:
```python
from src.app.infrastructure.external.mexc.ws.ws_client import connect_user_stream
async for msg in connect_user_stream():
    handle(msg)  # dict parsed from protobuf PushData
```
- Mask or filter sensitive fields before forwarding.

### Ops notes
- Heartbeat: send `{"method":"PING"}`; reply `{"method":"PONG"}` when asked.
- Retry listenKey keepalive on REST 429/5xx with backoff, but keep interval ≤30m.
- Limit one set of subscriptions per WS; open a new key if you need >30 subs.
