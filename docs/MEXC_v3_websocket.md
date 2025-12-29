## MEXC Spot V3 – WebSocket Streams

### Prerequisite
- User data streams require a listen key (see REST section in `MEXC_v3_account_wallet.md`). Connect with `wss://wbs-api.mexc.com/ws?listenKey=<key>`.

### WebSocket Market Streams
- [Live subscription/unsubscription](https://www.mexc.com/api-docs/spot-v3/websocket-market-streams#live-subscriptionunsubscription-to-data-streams) – SUBSCRIPTION/UNSUBSCRIPTION payloads.
- [Protocol Buffers integration](https://www.mexc.com/api-docs/spot-v3/websocket-market-streams#protocol-buffers-integration) – PB channels format.
- [Subscribe](https://www.mexc.com/api-docs/spot-v3/websocket-market-streams#subscribe-to-a-data-stream) / [Unsubscribe](https://www.mexc.com/api-docs/spot-v3/websocket-market-streams#unsubscribe-from-a-data-stream)
- [PING/PONG](https://www.mexc.com/api-docs/spot-v3/websocket-market-streams#pingpong-mechanism)
- [Trade streams](https://www.mexc.com/api-docs/spot-v3/websocket-market-streams#trade-streams)
- [K-line streams](https://www.mexc.com/api-docs/spot-v3/websocket-market-streams#k-line-streams)
- [Diff. depth stream](https://www.mexc.com/api-docs/spot-v3/websocket-market-streams#diffdepth-stream)
- [Partial book depth streams](https://www.mexc.com/api-docs/spot-v3/websocket-market-streams#partial-book-depth-streams)
- [Individual symbol book ticker](https://www.mexc.com/api-docs/spot-v3/websocket-market-streams#individual-symbol-book-ticker-streams)
- [Individual symbol book ticker (batch)](https://www.mexc.com/api-docs/spot-v3/websocket-market-streams#individual-symbol-book-ticker-streamsbatch-aggregation)
- [MiniTickers](https://www.mexc.com/api-docs/spot-v3/websocket-market-streams#minitickers) / [MiniTicker](https://www.mexc.com/api-docs/spot-v3/websocket-market-streams#miniticker)
- [Maintain local order book](https://www.mexc.com/api-docs/spot-v3/websocket-market-streams#how-to-properly-maintain-a-local-copy-of-the-order-book)

### WebSocket User Data Streams
- [Listen key lifecycle](https://www.mexc.com/api-docs/spot-v3/websocket-user-data-streams#listen-key) – Key validity rules.
- [Generate](https://www.mexc.com/api-docs/spot-v3/websocket-user-data-streams#generate-listen-key) / [Extend](https://www.mexc.com/api-docs/spot-v3/websocket-user-data-streams#extend-listen-key-validity) / [Close](https://www.mexc.com/api-docs/spot-v3/websocket-user-data-streams#close-listen-key) / [List](https://www.mexc.com/api-docs/spot-v3/websocket-user-data-streams#get-valid-listen-keys)
- [Spot account update](https://www.mexc.com/api-docs/spot-v3/websocket-user-data-streams#spot-account-update)
- [Spot account deals](https://www.mexc.com/api-docs/spot-v3/websocket-user-data-streams#spot-account-deals)
- [Spot account orders](https://www.mexc.com/api-docs/spot-v3/websocket-user-data-streams#spot-account-orders)
