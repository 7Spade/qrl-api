## Websocket User Data Streams (MEXC V3)

- REST base: `https://api.mexc.com`. WS base: `wss://wbs-api.mexc.com/ws?listenKey=<key>`.
- Listen key lifecycle: `POST /api/v3/userDataStream` creates a key (valid 60m). `PUT /api/v3/userDataStream` extends 60m (send ~every 30m). `DELETE /api/v3/userDataStream` closes it. `GET /api/v3/userDataStream` lists active keys.
- Limits: per UID up to 60 listen keys; each key supports 5 WS links; each WS ≤24h. Send `PING` to keep alive; reconnect and re-subscribe on disconnects.

### Private channels (protobuf)
- Default set: `spot@private.account.v3.api.pb`, `spot@private.deals.v3.api.pb`, `spot@private.orders.v3.api.pb`.
- Subscribe: `{"id":1,"method":"SUBSCRIPTION","params":["spot@private.account.v3.api.pb"]}` (repeat for other channels). Unsubscribe with `UNSUBSCRIPTION`.

### Protocol Buffers integration
- Private channels also use `PushDataV3ApiWrapper` messages (schema: https://github.com/mexcdevelop/websocket-proto).
- Python generation: `protoc *.proto --python_out=src/app/infrastructure/external/proto`.
- Use the shared decoder `decode_push_data` or create a custom one via `build_protobuf_decoder` in `src/app/infrastructure/external/mexc/websocket/market_streams.py`. Pass it as `binary_decoder` when constructing `MEXCWebSocketClient` or `connect_user_stream`.
- Apply local masking/filters for sensitive fields before forwarding to UI or logs.

### Minimal flow
1. Create a listen key and keep it alive on a 30m cadence.
2. Connect `wss://wbs-api.mexc.com/ws?listenKey=<key>`.
3. Subscribe to the private channels you need; handle `{id, code, msg}` acks.
4. Maintain heartbeat with PING/PONG; on drops, reconnect with the same (still-valid) listen key or request a new one, then re-subscribe.
