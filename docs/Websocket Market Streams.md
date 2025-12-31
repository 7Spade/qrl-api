## Websocket Market Streams (V3, protobuf)

- Base: `wss://wbs-api.mexc.com/ws` (24h cap, max 30 subs). Server drops empty sessions after 30s; send `{"method":"PING"}` periodically and respond `{"method":"PONG"}`. Symbols are uppercase.

### Core channels
- Trades: `spot@public.aggre.deals.v3.api.pb@(100ms|10ms)@<SYMBOL>`
- Klines: `spot@public.kline.v3.api.pb@<SYMBOL>@<INTERVAL>` (Min1..Month1)
- Diff depth: `spot@public.aggre.depth.v3.api.pb@(100ms|10ms)@<SYMBOL>`
- Partial depth: `spot@public.limit.depth.v3.api.pb@<SYMBOL>@(5|10|20)`
- Book ticker: `spot@public.aggre.bookTicker.v3.api.pb@(100ms|10ms)@<SYMBOL>`
- Book ticker batch: `spot@public.bookTicker.batch.v3.api.pb@<SYMBOL>`
- Mini tickers: `spot@public.miniTickers.v3.api.pb@<TZ>` or `spot@public.miniTicker.v3.api.pb@<SYMBOL>@<TZ>`

Subscribe example:
```json
{"method":"SUBSCRIPTION","params":["spot@public.aggre.deals.v3.api.pb@100ms@BTCUSDT"]}
```

### Protocol Buffers integration
- Official schema: https://github.com/mexcdevelop/websocket-proto.
- Generated bindings live in `src/app/infrastructure/external/proto/websocket_pb/`.
- Python decoder: `from src.app.infrastructure.external.mexc.websocket.market_streams import decode_push_data` (default for WS helpers).
- Custom decode sample:
```python
from src.app.infrastructure.external.proto.websocket_pb import PublicAggreDealsV3Api_pb2
from src.app.infrastructure.external.mexc.websocket.market_streams import build_protobuf_decoder
decode_deals = build_protobuf_decoder(PublicAggreDealsV3Api_pb2.PublicAggreDealsV3Api)
```

### Local order book reconstruction (diff depth)
- Snapshot first: `https://api.mexc.com/api/v3/depth?symbol=<SYMBOL>&limit=1000`.
- Track the last `toVersion`; apply a push only when `fromVersion == lastToVersion + 1`. Gaps or resets → refresh snapshot.
- Apply a push only if your snapshot version falls inside `[fromVersion, toVersion]`; otherwise refresh snapshot.
- Quantity `0` means remove that price level; other quantities are absolute values to replace/insert.
- Repeat the same checks after every refresh to keep the book monotonic and gap-free.
