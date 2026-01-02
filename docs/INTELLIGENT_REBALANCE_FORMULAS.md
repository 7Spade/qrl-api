# 智能調倉策略：公式步驟詳解（下單至成交）

> **文檔目的**: 詳細描述智能調倉策略的完整公式與計算步驟，從市場分析、決策制定、訂單生成、下單執行到成交確認的全流程數學模型

## 📋 目錄

1. [智能調倉概述](#智能調倉概述)
2. [階段一：市場狀態評估](#階段一市場狀態評估)
3. [階段二：倉位計算與決策](#階段二倉位計算與決策)
4. [階段三：訂單參數計算](#階段三訂單參數計算)
5. [階段四：訂單執行追蹤](#階段四訂單執行追蹤)
6. [階段五：成交確認與倉位更新](#階段五成交確認與倉位更新)
7. [完整流程範例](#完整流程範例)
8. [公式快速參考](#公式快速參考)

---

## 智能調倉概述

### 核心定義

**智能調倉 (Intelligent Rebalancing)** 是一種動態倉位管理策略，結合：
- 對稱再平衡邏輯（50/50 價值目標）
- 分層倉位管理（核心/波段/機動）
- MA 交叉信號確認
- 風險控制檢查

### 與對稱再平衡的區別

```
對稱再平衡 (Symmetric Rebalance):
├─ 目標: 維持 QRL:USDT = 50:50 價值比例
├─ 決策: 單純基於價值偏差
└─ 執行: 立即全額調整

智能調倉 (Intelligent Rebalance):
├─ 目標: 維持 50:50 + 增加 QRL 持倉
├─ 決策: 價值偏差 + MA 信號 + 倉位層級
├─ 執行: 分層計算 + 風險檢查 + 訂單追蹤
└─ 優勢: 更精確的成本控制和累積效果
```

### 策略流程圖

```
開始
  ↓
[1] 市場狀態評估
  ├─ 獲取當前餘額
  ├─ 計算 MA_7 和 MA_25
  ├─ 評估信號強度
  └─ 檢查市場波動
  ↓
[2] 倉位計算與決策
  ├─ 計算價值偏差 (delta)
  ├─ 確定交易方向 (BUY/SELL/HOLD)
  ├─ 計算可交易數量
  └─ 應用倉位層級限制
  ↓
[3] 訂單參數計算
  ├─ 計算訂單數量
  ├─ 計算訂單價格
  ├─ 計算預期成本變化
  └─ 生成訂單結構
  ↓
[4] 訂單執行追蹤
  ├─ 提交訂單到 MEXC
  ├─ 記錄訂單 ID
  ├─ 監控成交狀態
  └─ 處理部分成交
  ↓
[5] 成交確認與倉位更新
  ├─ 驗證成交數量
  ├─ 更新餘額
  ├─ 重新計算平均成本
  ├─ 更新倉位層級
  └─ 記錄交易歷史
  ↓
結束
```

---

## 階段一：市場狀態評估

### 1.1 餘額獲取

**公式**:
```
Balance_State = {
  QRL_total: B_qrl,
  QRL_available: B_qrl_avail,
  QRL_locked: B_qrl_lock,
  USDT_total: B_usdt,
  USDT_available: B_usdt_avail,
  USDT_locked: B_usdt_lock,
  Price_current: P_curr
}

其中:
  B_qrl = QRL 總餘額
  B_qrl_avail = QRL 可用餘額 (未被訂單鎖定)
  B_qrl_lock = QRL 鎖定餘額 (訂單中)
  B_usdt = USDT 總餘額
  B_usdt_avail = USDT 可用餘額
  B_usdt_lock = USDT 鎖定餘額
  P_curr = 當前市場價格 (USDT/QRL)
```

**實現步驟**:
```python
# 步驟 1: 調用 MEXC 賬戶餘額 API
response = await mexc_client.get_account_balance()

# 步驟 2: 提取 QRL 和 USDT 數據
qrl_data = response['balances']['QRL']
usdt_data = response['balances']['USDT']

# 步驟 3: 解析餘額字段
balance_state = {
    'qrl_total': float(qrl_data['total']),
    'qrl_available': float(qrl_data['available']),
    'qrl_locked': float(qrl_data['locked']),
    'usdt_total': float(usdt_data['total']),
    'usdt_available': float(usdt_data['available']),
    'usdt_locked': float(usdt_data['locked']),
    'price_current': float(response['prices']['QRLUSDT'])
}
```

**範例**:
```
初始餘額狀態:
  QRL_total: 10,000 QRL
  QRL_available: 9,500 QRL
  QRL_locked: 500 QRL (掛單中)
  USDT_total: 500 USDT
  USDT_available: 450 USDT
  USDT_locked: 50 USDT (掛單中)
  Price_current: 0.05000 USDT/QRL
```

### 1.2 移動平均線計算

**公式**:
```
MA_short = Σ(P_i) / n_short    (i = 1 到 n_short)
MA_long = Σ(P_j) / n_long      (j = 1 到 n_long)

其中:
  P_i = 第 i 個週期的價格
  n_short = 短期週期數 (默認 7)
  n_long = 長期週期數 (默認 25)
```

**實現步驟**:
```python
# 步驟 1: 獲取歷史價格數據
prices_7 = await get_recent_prices(symbol='QRLUSDT', limit=7)
prices_25 = await get_recent_prices(symbol='QRLUSDT', limit=25)

# 步驟 2: 計算短期 MA
ma_short = sum(prices_7) / 7

# 步驟 3: 計算長期 MA
ma_long = sum(prices_25) / 25

# 步驟 4: 計算信號強度
signal_strength = (ma_short - ma_long) / ma_long * 100
```

**範例**:
```
價格數據 (最近 7 個):
  [0.04800, 0.04850, 0.04900, 0.04950, 0.05000, 0.05050, 0.05100]

MA_short 計算:
  sum = 0.04800 + 0.04850 + 0.04900 + 0.04950 + 0.05000 + 0.05050 + 0.05100
      = 0.34650
  MA_7 = 0.34650 / 7 = 0.04950 USDT/QRL

價格數據 (最近 25 個): 省略詳細列表
  MA_25 = 0.04920 USDT/QRL

信號強度:
  signal_strength = (0.04950 - 0.04920) / 0.04920 × 100
                  = 0.61%
```

### 1.3 市場信號判斷

**買入信號條件**:
```
BUY_Signal = (MA_short > MA_long) AND (P_curr ≤ Cost_avg × 1.00)

其中:
  MA_short = 短期移動平均
  MA_long = 長期移動平均
  P_curr = 當前市場價格
  Cost_avg = QRL 平均成本
```

**賣出信號條件**:
```
SELL_Signal = (MA_short < MA_long) AND (P_curr ≥ Cost_avg × 1.03)

其中:
  1.03 = 止盈閾值 (3% 利潤)
```

**持有信號條件**:
```
HOLD_Signal = NOT BUY_Signal AND NOT SELL_Signal
```

**範例**:
```
當前狀態:
  MA_short: 0.04950
  MA_long: 0.04920
  P_curr: 0.04950
  Cost_avg: 0.05000

判斷 BUY_Signal:
  MA_short > MA_long? 0.04950 > 0.04920 ✓
  P_curr ≤ Cost_avg? 0.04950 ≤ 0.05000 ✓
  結果: BUY_Signal = TRUE → 可以買入
```

---

## 階段二：倉位計算與決策

### 2.1 價值計算

**總價值公式**:
```
V_total = V_qrl + V_usdt

其中:
  V_qrl = B_qrl × P_curr    (QRL 的 USDT 價值)
  V_usdt = B_usdt           (USDT 本身價值)
```

**目標價值公式**:
```
V_target = V_total × R_target

其中:
  R_target = 目標比率 (默認 0.5 = 50%)
```

**價值偏差公式**:
```
Δ_value = V_qrl - V_target

其中:
  Δ_value > 0 → QRL 價值過高，需要賣出
  Δ_value < 0 → QRL 價值過低，需要買入
  Δ_value = 0 → 完美平衡
```

**範例**:
```
餘額狀態:
  B_qrl = 10,000 QRL
  B_usdt = 500 USDT
  P_curr = 0.05000 USDT/QRL

計算總價值:
  V_qrl = 10,000 × 0.05000 = 500 USDT
  V_usdt = 500 USDT
  V_total = 500 + 500 = 1,000 USDT

計算目標價值:
  V_target = 1,000 × 0.5 = 500 USDT

計算偏差:
  Δ_value = 500 - 500 = 0 USDT
  結果: 完美平衡，無需調整
```

### 2.2 可交易數量計算

**買入情況**:
```
Q_trade_buy = min(Q_needed, Q_max_buy)

其中:
  Q_needed = |Δ_value| / P_curr          (需要買入的數量)
  Q_max_buy = B_usdt_avail / P_curr      (最多能買入的數量)
```

**賣出情況**:
```
Q_trade_sell = min(Q_needed, Q_max_sell)

其中:
  Q_needed = |Δ_value| / P_curr          (需要賣出的數量)
  Q_max_sell = B_qrl_tradeable           (最多能賣出的數量)
```

**可交易 QRL 計算** (分層管理):
```
B_qrl_core = B_qrl × R_core                (核心倉位: 70%)
B_qrl_tradeable = B_qrl - B_qrl_core       (可交易: 30%)

其中:
  R_core = 核心倉位比率 (默認 0.7)
  B_qrl_tradeable = 可用於交易的 QRL 數量
```

**範例 1: 買入場景**:
```
餘額狀態:
  B_qrl = 8,000 QRL
  B_usdt_avail = 600 USDT
  P_curr = 0.05000 USDT/QRL
  V_total = 1,000 USDT
  Δ_value = -100 USDT (QRL 不足)

計算可買數量:
  Q_needed = |-100| / 0.05000 = 2,000 QRL
  Q_max_buy = 600 / 0.05000 = 12,000 QRL
  Q_trade_buy = min(2,000, 12,000) = 2,000 QRL
  
結果: 買入 2,000 QRL
```

**範例 2: 賣出場景**:
```
餘額狀態:
  B_qrl = 12,000 QRL
  B_usdt = 100 USDT
  P_curr = 0.05000 USDT/QRL
  V_total = 700 USDT
  Δ_value = +250 USDT (QRL 過多)

計算核心倉位:
  B_qrl_core = 12,000 × 0.7 = 8,400 QRL
  B_qrl_tradeable = 12,000 - 8,400 = 3,600 QRL

計算可賣數量:
  Q_needed = |250| / 0.05000 = 5,000 QRL
  Q_max_sell = 3,600 QRL (受限於可交易倉位)
  Q_trade_sell = min(5,000, 3,600) = 3,600 QRL

結果: 只能賣出 3,600 QRL (達到倉位限制)
```

### 2.3 閾值檢查

**最小交易額檢查**:
```
Notional_min = Q_trade × P_curr

條件: Notional_min ≥ T_min_notional

其中:
  T_min_notional = 最小交易額 (默認 5 USDT)
```

**偏差百分比檢查**:
```
Deviation_pct = |Δ_value| / V_total

條件: Deviation_pct ≥ T_threshold

其中:
  T_threshold = 偏差閾值 (默認 1% = 0.01)
```

**範例**:
```
計算結果:
  Q_trade = 100 QRL
  P_curr = 0.05000 USDT/QRL
  Δ_value = -5 USDT
  V_total = 1,000 USDT

檢查最小交易額:
  Notional = 100 × 0.05000 = 5.00 USDT
  5.00 ≥ 5.00 ✓ 通過

檢查偏差百分比:
  Deviation_pct = |-5| / 1,000 = 0.5%
  0.5% < 1% ✗ 不通過
  
決策: HOLD (偏差太小，避免頻繁交易)
```

---

## 階段三：訂單參數計算

### 3.1 訂單類型選擇

**市價單 vs 限價單**:
```
Order_Type = {
  MARKET: 追求立即成交，接受滑點
  LIMIT:  追求價格控制，可能部分成交或未成交
}

推薦邏輯:
  IF signal_strength > 1.5% AND urgency == HIGH:
    Order_Type = MARKET
  ELSE:
    Order_Type = LIMIT
```

### 3.2 限價單價格計算

**買入限價**:
```
P_limit_buy = P_curr × (1 - S_slippage)

其中:
  S_slippage = 滑點容忍度 (默認 0.2% = 0.002)
```

**賣出限價**:
```
P_limit_sell = P_curr × (1 + S_slippage)
```

**範例**:
```
當前價格:
  P_curr = 0.05000 USDT/QRL
  S_slippage = 0.002 (0.2%)

買入限價:
  P_limit_buy = 0.05000 × (1 - 0.002)
              = 0.05000 × 0.998
              = 0.04990 USDT/QRL

賣出限價:
  P_limit_sell = 0.05000 × (1 + 0.002)
               = 0.05000 × 1.002
               = 0.05010 USDT/QRL
```

### 3.3 訂單數量精度處理

**MEXC 數量規則**:
```
Q_order_raw = Q_trade  (原始計算數量)

數量精度調整:
  Q_order = floor(Q_order_raw / Q_step) × Q_step

其中:
  Q_step = 交易對的數量步長 (QRLUSDT: 0.01 QRL)
  floor() = 向下取整函數
```

**範例**:
```
計算數量:
  Q_trade = 1,234.567 QRL
  Q_step = 0.01 QRL

精度調整:
  Q_order = floor(1,234.567 / 0.01) × 0.01
          = floor(123,456.7) × 0.01
          = 123,456 × 0.01
          = 1,234.56 QRL

結果: 提交訂單數量為 1,234.56 QRL
```

### 3.4 訂單結構生成

**買入訂單**:
```python
buy_order = {
    'symbol': 'QRLUSDT',
    'side': 'BUY',
    'type': 'LIMIT',  # or 'MARKET'
    'quantity': 1234.56,  # QRL
    'price': 0.04990,     # USDT/QRL (限價單)
    'timeInForce': 'GTC',  # Good Till Cancel
    'newClientOrderId': 'rebal_buy_20260101120000'
}
```

**賣出訂單**:
```python
sell_order = {
    'symbol': 'QRLUSDT',
    'side': 'SELL',
    'type': 'LIMIT',
    'quantity': 3600.00,  # QRL
    'price': 0.05010,     # USDT/QRL
    'timeInForce': 'GTC',
    'newClientOrderId': 'rebal_sell_20260101120000'
}
```

---

## 階段四：訂單執行追蹤

### 4.1 訂單提交

**API 調用**:
```python
# 步驟 1: 準備訂單參數
order_params = {
    'symbol': 'QRLUSDT',
    'side': 'BUY',
    'type': 'LIMIT',
    'quantity': 1234.56,
    'price': 0.04990,
    'timestamp': int(time.time() * 1000)
}

# 步驟 2: 生成簽名
signature = hmac_sha256(order_params, api_secret)
order_params['signature'] = signature

# 步驟 3: 提交到 MEXC
response = await mexc_client.create_order(order_params)

# 步驟 4: 提取訂單 ID
order_id = response['orderId']
```

**響應結構**:
```json
{
  "orderId": "123456789",
  "symbol": "QRLUSDT",
  "status": "NEW",
  "side": "BUY",
  "type": "LIMIT",
  "price": "0.04990",
  "origQty": "1234.56",
  "executedQty": "0.00",
  "cummulativeQuoteQty": "0.00",
  "timeInForce": "GTC",
  "transactTime": 1704096000000
}
```

### 4.2 訂單狀態追蹤

**狀態查詢公式**:
```
Order_Status = QUERY_ORDER(order_id, symbol)

狀態類型:
  NEW:              已提交，未成交
  PARTIALLY_FILLED: 部分成交
  FILLED:           完全成交
  CANCELED:         已取消
  EXPIRED:          已過期
```

**輪詢策略**:
```
輪詢間隔計算:
  interval_base = 1 秒
  interval_max = 10 秒
  
  interval(n) = min(interval_base × 2^n, interval_max)
  
  其中 n = 輪詢次數 (0, 1, 2, 3, ...)
```

**實現步驟**:
```python
# 步驟 1: 初始化追蹤
order_tracker = {
    'order_id': '123456789',
    'status': 'NEW',
    'executed_qty': 0.0,
    'avg_price': 0.0,
    'poll_count': 0
}

# 步驟 2: 輪詢檢查 (每 1, 2, 4, 8, 10, 10... 秒)
while order_tracker['status'] not in ['FILLED', 'CANCELED', 'EXPIRED']:
    await asyncio.sleep(min(1 * 2 ** order_tracker['poll_count'], 10))
    
    # 查詢訂單狀態
    order_status = await mexc_client.query_order(
        symbol='QRLUSDT',
        orderId='123456789'
    )
    
    # 更新追蹤信息
    order_tracker['status'] = order_status['status']
    order_tracker['executed_qty'] = float(order_status['executedQty'])
    order_tracker['avg_price'] = calculate_avg_price(order_status)
    order_tracker['poll_count'] += 1
    
    # 超時保護 (最多輪詢 30 次)
    if order_tracker['poll_count'] > 30:
        break
```

### 4.3 部分成交處理

**成交進度公式**:
```
Progress = Q_executed / Q_original × 100%

其中:
  Q_executed = 已成交數量
  Q_original = 訂單原始數量
```

**剩餘數量公式**:
```
Q_remaining = Q_original - Q_executed
```

**範例**:
```
訂單信息:
  Q_original = 1,234.56 QRL
  Q_executed = 800.00 QRL (部分成交)

計算進度:
  Progress = 800.00 / 1,234.56 × 100%
           = 64.8%

計算剩餘:
  Q_remaining = 1,234.56 - 800.00
              = 434.56 QRL

決策:
  IF timeout_reached OR market_changed:
    取消剩餘訂單
    記錄部分成交結果
  ELSE:
    繼續等待成交
```

### 4.4 平均成交價計算

**加權平均價公式**:
```
P_avg = Σ(P_i × Q_i) / Σ(Q_i)

其中:
  P_i = 第 i 次成交的價格
  Q_i = 第 i 次成交的數量
  i = 1 到 n (成交次數)
```

**範例**:
```
訂單多次成交記錄:
  成交 1: 500.00 QRL @ 0.04990 USDT/QRL
  成交 2: 300.00 QRL @ 0.04985 USDT/QRL
  成交 3: 434.56 QRL @ 0.04980 USDT/QRL

計算平均價:
  分子 = (500.00 × 0.04990) + (300.00 × 0.04985) + (434.56 × 0.04980)
       = 24.95 + 14.955 + 21.641
       = 61.546 USDT
  
  分母 = 500.00 + 300.00 + 434.56
       = 1,234.56 QRL
  
  P_avg = 61.546 / 1,234.56
        = 0.04987 USDT/QRL

結果: 平均成交價為 0.04987 USDT/QRL
```

---

## 階段五：成交確認與倉位更新

### 5.1 餘額變化計算

**買入後餘額**:
```
B_qrl_new = B_qrl_old + Q_executed
B_usdt_new = B_usdt_old - (Q_executed × P_avg) - Fee_total

其中:
  Q_executed = 成交數量
  P_avg = 平均成交價
  Fee_total = 總手續費
```

**賣出後餘額**:
```
B_qrl_new = B_qrl_old - Q_executed
B_usdt_new = B_usdt_old + (Q_executed × P_avg) - Fee_total
```

**手續費計算**:
```
Fee_total = Notional × Fee_rate

其中:
  Notional = Q_executed × P_avg  (成交金額)
  Fee_rate = 0.001 (0.1% MEXC 一般費率)
```

**範例 - 買入成交**:
```
買入前餘額:
  B_qrl_old = 8,000 QRL
  B_usdt_old = 600 USDT

成交信息:
  Q_executed = 1,234.56 QRL
  P_avg = 0.04987 USDT/QRL

計算成交金額:
  Notional = 1,234.56 × 0.04987
           = 61.546 USDT

計算手續費:
  Fee_total = 61.546 × 0.001
            = 0.06155 USDT

計算新餘額:
  B_qrl_new = 8,000 + 1,234.56
            = 9,234.56 QRL
  
  B_usdt_new = 600 - 61.546 - 0.06155
             = 538.39 USDT

更新後餘額:
  QRL: 9,234.56 QRL
  USDT: 538.39 USDT
```

### 5.2 平均成本更新

**買入後成本更新**:
```
Cost_avg_new = (B_qrl_old × Cost_avg_old + Q_executed × P_avg) / B_qrl_new

其中:
  Cost_avg_old = 買入前的平均成本
  Cost_avg_new = 買入後的平均成本
```

**賣出後成本**:
```
Cost_avg_new = Cost_avg_old  (賣出不改變剩餘 QRL 的成本)
```

**範例 - 買入成本更新**:
```
買入前:
  B_qrl_old = 8,000 QRL
  Cost_avg_old = 0.05200 USDT/QRL
  總成本 = 8,000 × 0.05200 = 416.00 USDT

本次買入:
  Q_executed = 1,234.56 QRL
  P_avg = 0.04987 USDT/QRL
  新增成本 = 1,234.56 × 0.04987 = 61.546 USDT

計算新平均成本:
  分子 = 416.00 + 61.546 = 477.546 USDT
  分母 = 8,000 + 1,234.56 = 9,234.56 QRL
  
  Cost_avg_new = 477.546 / 9,234.56
               = 0.05172 USDT/QRL

結果: 平均成本從 0.05200 降至 0.05172
      降低了 0.54%
```

### 5.3 倉位層級更新

**重新計算倉位層級**:
```
B_qrl_core_new = B_qrl_new × R_core
B_qrl_swing_new = B_qrl_new × R_swing
B_qrl_active_new = B_qrl_new × R_active

其中:
  R_core = 0.70 (70% 核心)
  R_swing = 0.20 (20% 波段)
  R_active = 0.10 (10% 機動)
```

**範例**:
```
更新後 QRL 總量:
  B_qrl_new = 9,234.56 QRL

重新分配倉位:
  B_qrl_core = 9,234.56 × 0.70 = 6,464.19 QRL
  B_qrl_swing = 9,234.56 × 0.20 = 1,846.91 QRL
  B_qrl_active = 9,234.56 × 0.10 = 923.46 QRL

驗證:
  6,464.19 + 1,846.91 + 923.46 = 9,234.56 ✓
```

### 5.4 交易記錄儲存

**記錄結構**:
```python
trade_record = {
    'timestamp': '2026-01-01T12:00:00Z',
    'order_id': '123456789',
    'symbol': 'QRLUSDT',
    'side': 'BUY',
    'quantity_ordered': 1234.56,
    'quantity_executed': 1234.56,
    'avg_price': 0.04987,
    'total_cost': 61.546,
    'fee': 0.06155,
    'balance_before': {
        'qrl': 8000.00,
        'usdt': 600.00,
        'cost_avg': 0.05200
    },
    'balance_after': {
        'qrl': 9234.56,
        'usdt': 538.39,
        'cost_avg': 0.05172
    },
    'position_layers': {
        'core': 6464.19,
        'swing': 1846.91,
        'active': 923.46
    },
    'rebalance_plan': {
        'delta_value': -100.00,
        'target_value': 500.00,
        'action': 'BUY',
        'reason': 'QRL below target'
    }
}
```

**儲存到 Redis**:
```python
# 儲存到 Redis List (最近 100 筆交易)
await redis_client.lpush(
    'qrl:trades:history',
    json.dumps(trade_record)
)
await redis_client.ltrim('qrl:trades:history', 0, 99)

# 更新最新倉位狀態
await redis_client.set(
    'qrl:position:current',
    json.dumps(trade_record['balance_after'])
)
```

---

## 完整流程範例

### 範例：從分析到成交的完整週期

#### 初始狀態

```
時間: 2026-01-01 12:00:00
當前餘額:
  QRL: 8,000 QRL
  USDT: 600 USDT
  平均成本: 0.05200 USDT/QRL
  
市場狀態:
  當前價格: 0.05000 USDT/QRL
  MA_7: 0.04950 USDT/QRL
  MA_25: 0.04920 USDT/QRL
```

#### 步驟 1: 市場評估

```
計算總價值:
  V_qrl = 8,000 × 0.05000 = 400 USDT
  V_usdt = 600 USDT
  V_total = 1,000 USDT

計算目標價值:
  V_target = 1,000 × 0.5 = 500 USDT

計算偏差:
  Δ_value = 400 - 500 = -100 USDT
  → QRL 價值不足 100 USDT

判斷信號:
  MA_7 > MA_25? 0.04950 > 0.04920 ✓
  P_curr ≤ Cost? 0.05000 ≤ 0.05200 ✓
  → BUY_Signal = TRUE
```

#### 步驟 2: 計算交易數量

```
計算需要買入:
  Q_needed = |-100| / 0.05000 = 2,000 QRL

計算最大可買:
  Q_max_buy = 600 / 0.05000 = 12,000 QRL

確定交易數量:
  Q_trade = min(2,000, 12,000) = 2,000 QRL

檢查閾值:
  Notional = 2,000 × 0.05000 = 100 USDT
  100 ≥ 5 ✓
  
  Deviation = |-100| / 1,000 = 10%
  10% ≥ 1% ✓
  
決策: 買入 2,000 QRL
```

#### 步驟 3: 生成訂單

```
計算限價:
  P_limit = 0.05000 × (1 - 0.002)
          = 0.04990 USDT/QRL

調整數量精度:
  Q_order = floor(2,000 / 0.01) × 0.01
          = 2,000.00 QRL

生成訂單:
  {
    'symbol': 'QRLUSDT',
    'side': 'BUY',
    'type': 'LIMIT',
    'quantity': 2000.00,
    'price': 0.04990,
    'timeInForce': 'GTC'
  }
```

#### 步驟 4: 執行追蹤

```
提交訂單:
  T = 0s: 訂單提交，獲得 order_id = 123456789
  T = 1s: 查詢狀態 → NEW, executed = 0
  T = 3s: 查詢狀態 → PARTIALLY_FILLED, executed = 800
  T = 7s: 查詢狀態 → PARTIALLY_FILLED, executed = 1500
  T = 15s: 查詢狀態 → FILLED, executed = 2000

成交記錄:
  成交 1: 800 QRL @ 0.04990
  成交 2: 700 QRL @ 0.04988
  成交 3: 500 QRL @ 0.04985

計算平均價:
  P_avg = (800×0.04990 + 700×0.04988 + 500×0.04985) / 2000
        = (39.92 + 34.916 + 24.925) / 2000
        = 99.761 / 2000
        = 0.04988 USDT/QRL
```

#### 步驟 5: 倉位更新

```
計算手續費:
  Notional = 2,000 × 0.04988 = 99.76 USDT
  Fee = 99.76 × 0.001 = 0.09976 USDT

更新餘額:
  B_qrl_new = 8,000 + 2,000 = 10,000 QRL
  B_usdt_new = 600 - 99.76 - 0.09976 = 500.14 USDT

更新平均成本:
  Cost_old = 8,000 × 0.05200 = 416.00 USDT
  Cost_new = 2,000 × 0.04988 = 99.76 USDT
  Cost_avg_new = (416.00 + 99.76) / 10,000
               = 515.76 / 10,000
               = 0.05158 USDT/QRL
  
  成本降低: (0.05200 - 0.05158) / 0.05200 × 100%
          = 0.81%

更新倉位層級:
  核心倉位: 10,000 × 0.70 = 7,000 QRL
  波段倉位: 10,000 × 0.20 = 2,000 QRL
  機動倉位: 10,000 × 0.10 = 1,000 QRL
```

#### 最終狀態

```
時間: 2026-01-01 12:00:25 (25 秒完成)

更新後餘額:
  QRL: 10,000 QRL (+2,000)
  USDT: 500.14 USDT (-99.86)
  平均成本: 0.05158 USDT/QRL (-0.81%)

新的價值分布:
  V_qrl = 10,000 × 0.05000 = 500 USDT
  V_usdt = 500.14 USDT
  V_total = 1,000.14 USDT
  比例: 49.99% : 50.01% ≈ 50:50 ✓

成效:
  ✓ 達成 50:50 平衡目標
  ✓ QRL 持倉增加 25%
  ✓ 平均成本降低 0.81%
  ✓ 總價值維持不變 (1,000 → 1,000.14)
```

---

## 公式快速參考

### 價值與偏差計算
```
V_total = B_qrl × P_curr + B_usdt
V_target = V_total × R_target (R_target = 0.5)
Δ_value = V_qrl - V_target
```

### 交易數量計算
```
買入: Q_trade = min(|Δ_value| / P_curr, B_usdt_avail / P_curr)
賣出: Q_trade = min(|Δ_value| / P_curr, B_qrl - B_qrl_core)
```

### 訂單價格計算
```
買入限價: P_limit = P_curr × (1 - S_slippage)
賣出限價: P_limit = P_curr × (1 + S_slippage)
S_slippage = 0.002 (0.2%)
```

### 成交與成本更新
```
平均成交價: P_avg = Σ(P_i × Q_i) / Σ(Q_i)
買入後成本: Cost_new = (B_old × Cost_old + Q_exec × P_avg) / (B_old + Q_exec)
賣出後成本: Cost_new = Cost_old
```

### 手續費計算
```
Fee_total = (Q_executed × P_avg) × Fee_rate
Fee_rate = 0.001 (0.1%)
```

### 倉位層級分配
```
核心倉位: B_qrl × 0.70
波段倉位: B_qrl × 0.20
機動倉位: B_qrl × 0.10
可交易量: B_qrl - (B_qrl × 0.70)
```

### 閾值檢查
```
最小交易額: Q_trade × P_curr ≥ 5 USDT
偏差百分比: |Δ_value| / V_total ≥ 1%
```

---

## 總結

### 關鍵公式流程

```
[1] 餘額獲取
    → B_qrl, B_usdt, P_curr

[2] 價值計算
    → V_total = B_qrl × P_curr + B_usdt
    → Δ_value = (B_qrl × P_curr) - (V_total × 0.5)

[3] 數量決策
    → Q_trade = min(|Δ_value| / P_curr, B_available)
    → 檢查閾值

[4] 訂單生成
    → P_limit = P_curr × (1 ± S_slippage)
    → Q_order = floor(Q_trade / Q_step) × Q_step

[5] 執行追蹤
    → 輪詢狀態直到 FILLED
    → P_avg = Σ(P_i × Q_i) / Σ(Q_i)

[6] 倉位更新
    → B_new = B_old ± Q_executed
    → Cost_new = (B_old × Cost_old + Q_exec × P_avg) / B_new
    → 重新計算倉位層級
```

### 數據流圖

```
市場數據 → 餘額狀態 → 價值計算 → 偏差判斷
                                    ↓
交易記錄 ← 倉位更新 ← 成交確認 ← 訂單執行 ← 訂單生成
```

### 使用指南

1. **開發者**: 按照公式實現各個階段的計算邏輯
2. **測試人員**: 使用範例數據驗證計算準確性
3. **分析師**: 理解策略決策的數學依據
4. **運維人員**: 監控各階段的執行狀態和性能

---

**文檔版本**: 1.0  
**最後更新**: 2026-01-01  
**維護者**: QRL Trading System Team
