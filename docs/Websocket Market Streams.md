## Websocket Market Streams (MEXC V3)

- Base WS: `wss://wbs-api.mexc.com/ws`, max 30 subscriptions per connection, each link ≤24h. Empty subscriptions close after ~30s; idle streams close after ~60s. Send `{"method":"PING"}` regularly and expect `PONG`.
- Symbols must be uppercase.
- Subscribe: `{"id":1,"method":"SUBSCRIPTION","params":["<channel>"]}`. Unsubscribe with `UNSUBSCRIPTION`. Re-subscribe after reconnects.

### Channel templates
- Trades: `spot@public.aggre.deals.v3.api.pb@{100ms|10ms}@<SYMBOL>`
- Klines: `spot@public.kline.v3.api.pb@<SYMBOL>@<Min1|Min5|Min15|Min30|Min60|Hour4|Hour8|Day1|Week1|Month1>`
- Diff depth: `spot@public.aggre.depth.v3.api.pb@{100ms|10ms}@<SYMBOL>` (check `fromVersion`/`toVersion`; if gaps, refresh REST snapshot `https://api.mexc.com/api/v3/depth?symbol=<SYMBOL>&limit=1000` before applying deltas).
- Partial depth: `spot@public.limit.depth.v3.api.pb@<SYMBOL>@{5|10|20}`
- Book ticker: `spot@public.aggre.bookTicker.v3.api.pb@{100ms|10ms}@<SYMBOL>`
- Book ticker (batch): `spot@public.bookTicker.batch.v3.api.pb@<SYMBOL>`
- Mini tickers: `spot@public.miniTickers.v3.api.pb@<TZ>` (all symbols) or `spot@public.miniTicker.v3.api.pb@<SYMBOL>@<TZ>` (single symbol, e.g., `UTC+8`).

### Protocol Buffers integration
- `.api.pb` channels emit `PushDataV3ApiWrapper` protobuf messages (schema: https://github.com/mexcdevelop/websocket-proto).
- Generate classes: `protoc *.proto --python_out=src/app/infrastructure/external/proto`.
- Default decoder: `decode_push_data` in `src/app/infrastructure/external/mexc/websocket/market_streams.py` converts bytes to dict via `google.protobuf.json_format.MessageToDict`.
- Custom parsing: `build_protobuf_decoder(YourMessage)` and pass as `binary_decoder` to websocket helpers (e.g., `MEXCWebSocketClient` or `connect_public_trades`).

### Minimal flow
1. Build the channel string from the templates above.
2. Send SUBSCRIPTION and handle `{id, code, msg}` acknowledgements.
3. Keep the link alive with PING/PONG; reconnect and re-subscribe on drops.
4. For depth data, ensure version continuity; otherwise reload the snapshot before applying incremental updates.
