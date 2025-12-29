## MEXC Spot V3 – Account & Trade (REST) + User Data Stream (REST)

### REST – Account & Trade (signed)
- [POST /api/v3/order/test](https://www.mexc.com/api-docs/spot-v3/spot-account-trade#test-new-order-trade) – Validate params (empty success).
- [POST /api/v3/order](https://www.mexc.com/api-docs/spot-v3/spot-account-trade#new-order--trade) – Place order (`orderId/clientOrderId/status`).
- [GET /api/v3/order](https://www.mexc.com/api-docs/spot-v3/spot-account-trade#query-order-trade) – Query order (status, times, fills).
- [DELETE /api/v3/order](https://www.mexc.com/api-docs/spot-v3/spot-account-trade#cancel-order-trade) – Cancel (returns cancelled order info).
- [GET /api/v3/openOrders](https://www.mexc.com/api-docs/spot-v3/spot-account-trade#current-open-orders-user_data) – Open orders list.
- [DELETE /api/v3/openOrders](https://www.mexc.com/api-docs/spot-v3/spot-account-trade#cancel-open-orders-trade) – Cancel all for symbol.
- [GET /api/v3/allOrders](https://www.mexc.com/api-docs/spot-v3/spot-account-trade#all-orders-user_data) – Historical orders.
- [GET /api/v3/myTrades](https://www.mexc.com/api-docs/spot-v3/spot-account-trade#account-trade-list-user_data) – Trades (`id/orderId/price/qty/commission`).
- [GET /api/v3/account](https://www.mexc.com/api-docs/spot-v3/spot-account-trade#account-information-user_data) – Balances (`free/locked`) & permissions.

### User Data Stream (REST for listen key)
- [POST /api/v3/userDataStream](https://www.mexc.com/api-docs/spot-v3/websocket-user-data-streams#generate-listen-key) – Generate listen key.
- [PUT /api/v3/userDataStream](https://www.mexc.com/api-docs/spot-v3/websocket-user-data-streams#extend-listen-key-validity) – Keepalive.
- [GET /api/v3/userDataStream](https://www.mexc.com/api-docs/spot-v3/websocket-user-data-streams#get-valid-listen-keys) – List active keys.
- [DELETE /api/v3/userDataStream](https://www.mexc.com/api-docs/spot-v3/websocket-user-data-streams#close-listen-key) – Close key.
