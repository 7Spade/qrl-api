## MEXC Spot V3 – Wallet, Sub-Account, Rebate (REST)

### REST – Wallet (signed)
- [GET /api/v3/capital/config/getall](https://www.mexc.com/api-docs/spot-v3/wallet-endpoints#user-coin-information-user_data) – Coins/networks, deposit/withdraw flags, limits.
- [POST /api/v3/capital/deposit/address](https://www.mexc.com/api-docs/spot-v3/wallet-endpoints#generate-deposit-address-user_data) – Address/tag per chain.
- [GET /api/v3/capital/deposit/hisrec](https://www.mexc.com/api-docs/spot-v3/wallet-endpoints#deposit-history-user_data) – Deposit history (`txId/amount/network/status/time`).
- [POST /api/v3/capital/withdraw](https://www.mexc.com/api-docs/spot-v3/wallet-endpoints#withdraw-user_data) – Withdraw (`withdrawId/status`).
- [DELETE /api/v3/capital/withdraw](https://www.mexc.com/api-docs/spot-v3/wallet-endpoints#withdraw-cancel-user_data) – Cancel withdraw.
- [GET /api/v3/capital/withdraw/history](https://www.mexc.com/api-docs/spot-v3/wallet-endpoints#withdraw-history-user_data) – Withdraw history (address/amount/txId/status/time).

### REST – Sub-Account (signed)
- [POST /api/v3/sub-account/virtualSubAccount](https://www.mexc.com/api-docs/spot-v3/subaccount-endpoints#create-virtual-sub-account) – Create (returns subAccount).
- [GET /api/v3/sub-account/list](https://www.mexc.com/api-docs/spot-v3/subaccount-endpoints#query-virtual-sub-account) – List (`uid/status/createTime`).
- [POST /api/v3/sub-account/apiKey](https://www.mexc.com/api-docs/spot-v3/subaccount-endpoints#create-api-key) – Create key/permissions.
- [GET /api/v3/sub-account/apiKey](https://www.mexc.com/api-docs/spot-v3/subaccount-endpoints#query-api-key) – Query keys.
- [DELETE /api/v3/sub-account/apiKey](https://www.mexc.com/api-docs/spot-v3/subaccount-endpoints#delete-api-key) – Delete key.
- [POST /api/v3/capital/sub-account/universalTransfer](https://www.mexc.com/api-docs/spot-v3/subaccount-endpoints#sub-account-universal-transfer) – Transfer (`transferId/status`).

### REST – Rebate (signed)
- [GET /api/v3/rebate/history](https://www.mexc.com/api-docs/spot-v3/rebate-endpoints#get-rebate-history-records) – Rebate summary (invitee totals).
- [GET /api/v3/rebate/records/detail](https://www.mexc.com/api-docs/spot-v3/rebate-endpoints#get-rebate-records-detail) – Invitee detail (order, fee, rebate).
- [GET /api/v3/rebate/self-records/detail](https://www.mexc.com/api-docs/spot-v3/rebate-endpoints#get-self-rebate-records-detail) – Self rebate records.
