# 策略設計：數學公式與計算步驟詳解

> **文檔目的**: 提供完整的策略設計公式、計算步驟與實現邏輯，確保所有策略組件都有精確的數學定義

## 📋 目錄

1. [核心策略公式](#核心策略公式)
2. [移動平均線 (MA) 計算](#移動平均線-ma-計算)
3. [信號生成邏輯](#信號生成邏輯)
4. [倉位管理公式](#倉位管理公式)
5. [成本計算公式](#成本計算公式)
6. [風險控制公式](#風險控制公式)
7. [完整計算範例](#完整計算範例)

---

## 核心策略公式

### 1. 移動平均線 (MA) 計算

#### 1.1 簡單移動平均 (SMA)

**公式**:
```
SMA(n) = Σ(P_i) / n

其中:
- P_i = 第 i 個週期的價格
- n = 移動平均週期數
- i = 1 到 n
```

**實現步驟**:

```python
# 步驟 1: 收集最近 n 個價格
prices = [P_1, P_2, P_3, ..., P_n]

# 步驟 2: 計算總和
sum_prices = P_1 + P_2 + P_3 + ... + P_n

# 步驟 3: 除以週期數
MA = sum_prices / n
```

**範例計算** (MA_7):
```
價格序列: [0.0480, 0.0485, 0.0490, 0.0495, 0.0500, 0.0505, 0.0510]
週期 n = 7

步驟 1: 加總
sum = 0.0480 + 0.0485 + 0.0490 + 0.0495 + 0.0500 + 0.0505 + 0.0510
    = 0.3465

步驟 2: 除以週期
MA_7 = 0.3465 / 7
     = 0.04950 USDT/QRL
```

#### 1.2 短期與長期 MA

**配置**:
- 短期 MA (MA_short): 7 週期
- 長期 MA (MA_long): 25 週期

**計算要求**:
```
MA_short 需要至少 7 個歷史價格
MA_long 需要至少 25 個歷史價格
```

---

## 移動平均線 (MA) 計算

### 2.1 MA 交叉判斷

#### 金叉 (Golden Cross) - 買入信號前置條件

**定義**: 短期 MA 上穿長期 MA

**數學表達式**:
```
當前時刻 t:
  MA_short(t) > MA_long(t)

前一時刻 t-1:
  MA_short(t-1) ≤ MA_long(t-1)

金叉條件: 
  [MA_short(t) > MA_long(t)] AND [MA_short(t-1) ≤ MA_long(t-1)]
```

**判斷步驟**:
```python
# 步驟 1: 計算當前 MA 值
ma_short_current = calculate_ma(prices_short)
ma_long_current = calculate_ma(prices_long)

# 步驟 2: 計算前一時刻 MA 值
ma_short_previous = calculate_ma(prices_short[:-1])
ma_long_previous = calculate_ma(prices_long[:-1])

# 步驟 3: 判斷交叉
golden_cross = (
    ma_short_current > ma_long_current and
    ma_short_previous <= ma_long_previous
)
```

#### 死叉 (Death Cross) - 賣出信號前置條件

**定義**: 短期 MA 下穿長期 MA

**數學表達式**:
```
當前時刻 t:
  MA_short(t) < MA_long(t)

前一時刻 t-1:
  MA_short(t-1) ≥ MA_long(t-1)

死叉條件:
  [MA_short(t) < MA_long(t)] AND [MA_short(t-1) ≥ MA_long(t-1)]
```

### 2.2 信號強度計算

**公式**:
```
Signal_Strength = [(MA_short - MA_long) / MA_long] × 100%

其中:
- Signal_Strength > 0: 上升趨勢 (買入傾向)
- Signal_Strength < 0: 下降趨勢 (賣出傾向)
- |Signal_Strength| 越大，信號越強
```

**範例**:
```
MA_short = 0.0505
MA_long = 0.0495

Signal_Strength = [(0.0505 - 0.0495) / 0.0495] × 100%
                = [0.0010 / 0.0495] × 100%
                = 2.02%

解讀: 短期 MA 高於長期 MA 2.02%，顯示溫和上升趨勢
```

---

## 信號生成邏輯

### 3.1 買入信號 (BUY) 完整公式

**必要條件組合**:
```
BUY_Signal = (MA_Crossover_Condition) AND (Price_Condition) AND (Risk_Condition)

其中:
1. MA_Crossover_Condition: MA_short > MA_long
2. Price_Condition: Current_Price ≤ Average_Cost × 1.00
3. Risk_Condition: All risk checks pass
```

**詳細步驟**:

**步驟 1: MA 條件檢查**
```python
ma_short = calculate_ma(short_prices, period=7)
ma_long = calculate_ma(long_prices, period=25)

ma_condition = ma_short > ma_long
```

**步驟 2: 價格條件檢查**
```python
# 只在價格低於或等於平均成本時買入
price_threshold = avg_cost * 1.00  # 100% of average cost

price_condition = current_price <= price_threshold
```

**步驟 3: 風險檢查**
```python
risk_checks = {
    'daily_limit': daily_trades < MAX_DAILY_TRADES,
    'trade_interval': time_since_last_trade >= MIN_TRADE_INTERVAL,
    'usdt_balance': usdt_balance > 0
}

risk_condition = all(risk_checks.values())
```

**步驟 4: 最終判斷**
```python
if ma_condition and price_condition and risk_condition:
    signal = "BUY"
else:
    signal = "HOLD"
```

**完整範例**:
```
輸入數據:
- MA_short = 0.0505
- MA_long = 0.0495
- Current_Price = 0.0490
- Average_Cost = 0.0500
- Daily_Trades = 3 (max: 5)
- Time_Since_Last = 400s (min: 300s)
- USDT_Balance = 250

步驟 1: MA 條件
ma_condition = 0.0505 > 0.0495 = TRUE ✓

步驟 2: 價格條件
price_threshold = 0.0500 × 1.00 = 0.0500
price_condition = 0.0490 ≤ 0.0500 = TRUE ✓

步驟 3: 風險條件
daily_limit = 3 < 5 = TRUE ✓
trade_interval = 400 ≥ 300 = TRUE ✓
usdt_balance = 250 > 0 = TRUE ✓
risk_condition = TRUE ✓

步驟 4: 最終信號
BUY_Signal = TRUE AND TRUE AND TRUE = TRUE
=> 信號: BUY ✓
```

### 3.2 賣出信號 (SELL) 完整公式

**必要條件組合**:
```
SELL_Signal = (MA_Crossover_Condition) AND (Profit_Condition) AND (Risk_Condition)

其中:
1. MA_Crossover_Condition: MA_short < MA_long
2. Profit_Condition: Current_Price ≥ Average_Cost × 1.03
3. Risk_Condition: All risk checks pass
```

**詳細步驟**:

**步驟 1: MA 條件檢查**
```python
ma_condition = ma_short < ma_long
```

**步驟 2: 利潤條件檢查**
```python
# 只在價格高於平均成本 3% 時賣出
profit_threshold = avg_cost * 1.03  # 103% of average cost

profit_condition = current_price >= profit_threshold
```

**步驟 3: 倉位保護檢查**
```python
# 確保不賣出核心倉位
total_qrl = get_total_qrl()
core_qrl = total_qrl * CORE_POSITION_PCT  # 70% 核心
tradeable_qrl = total_qrl - core_qrl

position_check = tradeable_qrl > 0
```

**步驟 4: 最終判斷**
```python
if ma_condition and profit_condition and position_check:
    signal = "SELL"
else:
    signal = "HOLD"
```

**完整範例**:
```
輸入數據:
- MA_short = 0.0495
- MA_long = 0.0505
- Current_Price = 0.0520
- Average_Cost = 0.0500
- Total_QRL = 10,000
- Core_Position = 70%

步驟 1: MA 條件
ma_condition = 0.0495 < 0.0505 = TRUE ✓

步驟 2: 利潤條件
profit_threshold = 0.0500 × 1.03 = 0.0515
profit_condition = 0.0520 ≥ 0.0515 = TRUE ✓
實際利潤率 = (0.0520 - 0.0500) / 0.0500 = 4.0% ✓

步驟 3: 倉位檢查
core_qrl = 10,000 × 0.70 = 7,000
tradeable_qrl = 10,000 - 7,000 = 3,000
position_check = 3,000 > 0 = TRUE ✓

步驟 4: 最終信號
SELL_Signal = TRUE AND TRUE AND TRUE = TRUE
=> 信號: SELL ✓
```

---

## 倉位管理公式

### 4.1 三層倉位架構

**定義**:
```
Total_QRL = Core_QRL + Swing_QRL + Active_QRL

其中:
- Core_QRL: 核心倉位 (60-70%)
- Swing_QRL: 波段倉位 (20-30%)
- Active_QRL: 機動倉位 (10%)
```

**計算公式**:
```
Core_QRL = Total_QRL × Core_Position_PCT
Swing_QRL = Total_QRL × Swing_Position_PCT
Active_QRL = Total_QRL × Active_Position_PCT

約束條件:
Core_Position_PCT + Swing_Position_PCT + Active_Position_PCT = 1.0
Core_Position_PCT ≥ 0.60 (最低 60%)
```

**完整計算範例**:
```
輸入: Total_QRL = 10,000

標準配置:
- Core_Position_PCT = 0.70 (70%)
- Swing_Position_PCT = 0.20 (20%)
- Active_Position_PCT = 0.10 (10%)

步驟 1: 計算各層倉位
Core_QRL = 10,000 × 0.70 = 7,000 QRL
Swing_QRL = 10,000 × 0.20 = 2,000 QRL
Active_QRL = 10,000 × 0.10 = 1,000 QRL

步驟 2: 驗證約束
總和 = 7,000 + 2,000 + 1,000 = 10,000 ✓
核心比例 = 7,000 / 10,000 = 0.70 ≥ 0.60 ✓

步驟 3: 計算可交易數量
Tradeable_QRL = Swing_QRL + Active_QRL
              = 2,000 + 1,000
              = 3,000 QRL (最多可賣出)
```

### 4.2 動態倉位調整

**牛市配置** (價格上升趨勢):
```
當檢測到牛市時:
- Core_Position_PCT → 0.75 (提高至 75%)
- Swing_Position_PCT → 0.18
- Active_Position_PCT → 0.07

牛市判斷條件:
Price > MA_50 AND MA_50 > MA_200 AND RSI > 55
```

**熊市配置** (價格下降趨勢):
```
當檢測到熊市時:
- Core_Position_PCT → 0.60 (降至 60%)
- Swing_Position_PCT → 0.25
- Active_Position_PCT → 0.15 (增加機動性)

熊市判斷條件:
Price < MA_50 AND MA_50 < MA_200 AND RSI < 45
```

**調整算法**:
```python
def adjust_position_layers(total_qrl: float, market_phase: str) -> dict:
    """
    根據市場階段調整倉位配置
    
    參數:
        total_qrl: 總 QRL 持倉
        market_phase: 'BULL', 'BEAR', 或 'SIDEWAYS'
    
    返回:
        {'core': float, 'swing': float, 'active': float}
    """
    if market_phase == 'BULL':
        core_pct = 0.75
        swing_pct = 0.18
        active_pct = 0.07
    elif market_phase == 'BEAR':
        core_pct = 0.60
        swing_pct = 0.25
        active_pct = 0.15
    else:  # SIDEWAYS
        core_pct = 0.70
        swing_pct = 0.20
        active_pct = 0.10
    
    return {
        'core': total_qrl * core_pct,
        'swing': total_qrl * swing_pct,
        'active': total_qrl * active_pct
    }
```

---

## 成本計算公式

### 5.1 平均成本計算

**加權平均成本公式**:
```
Average_Cost = (Σ(Purchase_i × Amount_i)) / Total_Amount

其中:
- Purchase_i: 第 i 次購買的價格
- Amount_i: 第 i 次購買的數量
- Total_Amount: 總持倉數量
```

**分步計算**:

**步驟 1: 計算總投入成本**
```
Total_Cost = Purchase_1 × Amount_1 + 
             Purchase_2 × Amount_2 + 
             ... + 
             Purchase_n × Amount_n
```

**步驟 2: 計算總數量**
```
Total_Amount = Amount_1 + Amount_2 + ... + Amount_n
```

**步驟 3: 計算平均成本**
```
Average_Cost = Total_Cost / Total_Amount
```

**完整範例**:
```
交易歷史:
1. 買入 5,000 QRL @ 0.0500 = 250 USDT
2. 買入 3,000 QRL @ 0.0480 = 144 USDT
3. 買入 2,000 QRL @ 0.0520 = 104 USDT

步驟 1: 計算總成本
Total_Cost = (5,000 × 0.0500) + (3,000 × 0.0480) + (2,000 × 0.0520)
           = 250 + 144 + 104
           = 498 USDT

步驟 2: 計算總數量
Total_Amount = 5,000 + 3,000 + 2,000
             = 10,000 QRL

步驟 3: 計算平均成本
Average_Cost = 498 / 10,000
             = 0.0498 USDT/QRL
```

### 5.2 新買入後的成本更新

**增量成本計算**:
```
New_Average_Cost = (Current_Total_Cost + New_Purchase_Cost) / 
                   (Current_Total_Amount + New_Purchase_Amount)

其中:
Current_Total_Cost = Current_Average_Cost × Current_Total_Amount
New_Purchase_Cost = New_Purchase_Price × New_Purchase_Amount
```

**完整計算範例**:
```
當前狀態:
- Current_Average_Cost = 0.0498
- Current_Total_Amount = 10,000 QRL

新買入:
- New_Purchase_Price = 0.0470
- New_Purchase_Amount = 2,000 QRL

步驟 1: 計算當前總成本
Current_Total_Cost = 0.0498 × 10,000 = 498 USDT

步驟 2: 計算新購買成本
New_Purchase_Cost = 0.0470 × 2,000 = 94 USDT

步驟 3: 計算總成本
Total_Cost = 498 + 94 = 592 USDT

步驟 4: 計算總數量
Total_Amount = 10,000 + 2,000 = 12,000 QRL

步驟 5: 計算新平均成本
New_Average_Cost = 592 / 12,000
                 = 0.0493 USDT/QRL

成本變化: 0.0498 → 0.0493 (-1.0%)
```

### 5.3 賣出後的成本保持

**重要原則**: 
```
賣出操作不改變平均成本
Average_Cost_After_Sell = Average_Cost_Before_Sell

原因: 賣出是實現利潤，不影響剩餘持倉的成本基礎
```

**範例**:
```
賣出前:
- Average_Cost = 0.0498
- Total_Amount = 10,000 QRL

賣出:
- Sell_Price = 0.0520
- Sell_Amount = 2,000 QRL

賣出後:
- Average_Cost = 0.0498 (保持不變)
- Total_Amount = 8,000 QRL
- Realized_Profit = (0.0520 - 0.0498) × 2,000 = 44 USDT
```

---

## 風險控制公式

### 6.1 每日交易次數限制

**公式**:
```
Daily_Trades_Allowed = Daily_Trades_Count < MAX_DAILY_TRADES

其中:
- Daily_Trades_Count: 當日已完成交易次數
- MAX_DAILY_TRADES: 每日最大交易次數 (預設: 5)
```

**檢查邏輯**:
```python
def check_daily_limit(daily_trades: int, max_daily_trades: int = 5) -> bool:
    """
    檢查每日交易限制
    
    返回: True 允許交易, False 禁止交易
    """
    if daily_trades >= max_daily_trades:
        print(f"❌ 達到每日交易上限: {daily_trades}/{max_daily_trades}")
        return False
    
    remaining = max_daily_trades - daily_trades
    print(f"✓ 剩餘交易次數: {remaining}")
    return True
```

### 6.2 最小交易間隔

**公式**:
```
Trade_Interval_OK = (Current_Time - Last_Trade_Time) ≥ MIN_TRADE_INTERVAL

其中:
- Current_Time: 當前時間戳 (秒)
- Last_Trade_Time: 上次交易時間戳 (秒)
- MIN_TRADE_INTERVAL: 最小間隔 (預設: 300 秒 = 5 分鐘)
```

**計算範例**:
```
Last_Trade_Time = 1735286400 (2025-12-27 10:00:00)
Current_Time = 1735286650 (2025-12-27 10:04:10)
MIN_TRADE_INTERVAL = 300 秒

計算:
Elapsed_Time = 1735286650 - 1735286400
             = 250 秒

檢查:
Trade_Interval_OK = 250 ≥ 300
                  = FALSE ❌

需要等待: 300 - 250 = 50 秒
```

### 6.3 核心倉位保護

**可賣出數量計算**:
```
Max_Sell_Amount = Total_QRL - Core_QRL
                = Total_QRL - (Total_QRL × Core_Position_PCT)
                = Total_QRL × (1 - Core_Position_PCT)

約束: Max_Sell_Amount ≥ 0
```

**完整檢查**:
```python
def calculate_max_sell_amount(
    total_qrl: float,
    core_position_pct: float = 0.70
) -> float:
    """
    計算最大可賣出數量
    
    參數:
        total_qrl: 總持倉
        core_position_pct: 核心倉位比例 (預設 70%)
    
    返回:
        最大可賣出數量
    """
    core_qrl = total_qrl * core_position_pct
    max_sell = total_qrl - core_qrl
    
    print(f"總持倉: {total_qrl} QRL")
    print(f"核心倉位: {core_qrl} QRL ({core_position_pct*100}%)")
    print(f"最大可賣: {max_sell} QRL")
    
    return max(0, max_sell)  # 確保非負

# 範例
total_qrl = 10000
max_sell = calculate_max_sell_amount(total_qrl)
# 輸出:
# 總持倉: 10000 QRL
# 核心倉位: 7000.0 QRL (70.0%)
# 最大可賣: 3000.0 QRL
```

### 6.4 USDT 儲備保護

**最小 USDT 儲備公式**:
```
Min_USDT_Reserve = Total_Value × Reserve_PCT

其中:
- Total_Value: 總資產價值 (QRL 價值 + USDT)
- Reserve_PCT: 儲備比例 (預設: 0.20 = 20%)
```

**買入限制計算**:
```
Max_USDT_For_Buy = Current_USDT - Min_USDT_Reserve

約束: Max_USDT_For_Buy ≥ 0
```

**完整範例**:
```
當前狀態:
- QRL_Balance = 10,000
- Current_Price = 0.0500
- USDT_Balance = 300
- Reserve_PCT = 0.20

步驟 1: 計算總價值
QRL_Value = 10,000 × 0.0500 = 500 USDT
Total_Value = 500 + 300 = 800 USDT

步驟 2: 計算最小儲備
Min_USDT_Reserve = 800 × 0.20 = 160 USDT

步驟 3: 計算可用於買入的 USDT
Max_USDT_For_Buy = 300 - 160 = 140 USDT

步驟 4: 計算可買入數量
Max_QRL_Buy = 140 / 0.0500 = 2,800 QRL
```

### 6.5 單筆交易限額

**公式**:
```
Max_Single_Trade_Amount = Tradeable_Amount × Max_Trade_PCT

其中:
- Tradeable_Amount: 可交易數量
- Max_Trade_PCT: 單筆最大比例 (預設: 0.30 = 30%)
```

**賣出限額計算**:
```
賣出場景:
Tradeable_QRL = Total_QRL - Core_QRL
Max_Sell_Single = Tradeable_QRL × 0.30

範例:
Total_QRL = 10,000
Core_QRL = 7,000
Tradeable_QRL = 3,000

Max_Sell_Single = 3,000 × 0.30 = 900 QRL

解讀: 單次最多賣出 900 QRL
```

**買入限額計算**:
```
買入場景:
Available_USDT = USDT_Balance - Min_Reserve
Max_USDT_Single = Available_USDT × 0.30

範例:
USDT_Balance = 300
Min_Reserve = 160
Available_USDT = 140

Max_USDT_Single = 140 × 0.30 = 42 USDT

Max_QRL_Buy = 42 / Current_Price
            = 42 / 0.0500
            = 840 QRL

解讀: 單次最多買入 840 QRL (花費 42 USDT)
```

---

## 完整計算範例

### 7.1 完整交易週期模擬

**初始狀態**:
```
日期: 2025-12-27 09:00:00
QRL 持倉: 10,000
Average_Cost: 0.0500 USDT/QRL
USDT 餘額: 500
當前價格: 0.0490 USDT/QRL
Daily_Trades: 0
```

**倉位配置**:
```
Core_QRL = 10,000 × 0.70 = 7,000
Swing_QRL = 10,000 × 0.20 = 2,000
Active_QRL = 10,000 × 0.10 = 1,000
Tradeable_QRL = 3,000
```

---

#### 情境 1: 買入決策

**時間**: 09:30:00

**步驟 1: 收集最近價格計算 MA**
```
短期價格 (最近 7 個):
[0.0495, 0.0493, 0.0491, 0.0489, 0.0488, 0.0487, 0.0490]

MA_short = (0.0495 + 0.0493 + 0.0491 + 0.0489 + 0.0488 + 0.0487 + 0.0490) / 7
         = 0.3433 / 7
         = 0.04904

長期價格 (最近 25 個):
[0.0510, 0.0508, ..., 0.0490] (省略中間值)

MA_long = 0.04850
```

**步驟 2: 判斷 MA 條件**
```
MA_short = 0.04904
MA_long = 0.04850
MA_Condition = 0.04904 > 0.04850 = TRUE ✓

信號強度 = (0.04904 - 0.04850) / 0.04850 × 100%
         = 1.11%
```

**步驟 3: 判斷價格條件**
```
Current_Price = 0.0490
Average_Cost = 0.0500
Price_Threshold = 0.0500 × 1.00 = 0.0500

Price_Condition = 0.0490 ≤ 0.0500 = TRUE ✓

折扣率 = (0.0500 - 0.0490) / 0.0500 × 100%
       = 2.0% (低於成本 2%)
```

**步驟 4: 風險檢查**
```
Daily_Limit_Check:
  Daily_Trades = 0 < 5 = TRUE ✓

Interval_Check:
  Last_Trade_Time = None (首次交易)
  Interval_OK = TRUE ✓

USDT_Check:
  USDT_Balance = 500 > 0 = TRUE ✓

Risk_Condition = TRUE ✓
```

**步驟 5: 計算買入數量**
```
可用 USDT:
Min_Reserve = (10,000 × 0.0490 + 500) × 0.20
            = (490 + 500) × 0.20
            = 990 × 0.20
            = 198 USDT

Available_USDT = 500 - 198 = 302 USDT

單次最大買入:
Max_USDT_Single = 302 × 0.30 = 90.6 USDT

實際買入 (保守策略，使用 50%):
Buy_USDT = 90.6 × 0.50 = 45.3 USDT

Buy_QRL = 45.3 / 0.0490
        = 924.5 QRL (四捨五入至 924)
```

**步驟 6: 執行買入並更新成本**
```
買入前:
- Total_QRL = 10,000
- Average_Cost = 0.0500
- Total_Cost = 10,000 × 0.0500 = 500 USDT

買入:
- Buy_Amount = 924 QRL
- Buy_Price = 0.0490
- Buy_Cost = 924 × 0.0490 = 45.28 USDT

買入後:
- New_Total_QRL = 10,000 + 924 = 10,924
- New_Total_Cost = 500 + 45.28 = 545.28
- New_Average_Cost = 545.28 / 10,924
                   = 0.04992 USDT/QRL

成本變化: 0.0500 → 0.04992 (-0.16%)
USDT 餘額: 500 - 45.28 = 454.72 USDT
```

**步驟 7: 更新交易計數**
```
Daily_Trades = 0 + 1 = 1
Last_Trade_Time = 1735286400 + 1800 = 1735288200
```

---

#### 情境 2: 賣出決策

**時間**: 14:00:00 (4.5 小時後)
**當前價格**: 0.0520 USDT/QRL

**步驟 1: 計算最新 MA**
```
MA_short = 0.05100 (新數據加入後)
MA_long = 0.05150 (新數據加入後)
```

**步驟 2: 判斷 MA 條件**
```
MA_Condition = 0.05100 < 0.05150 = TRUE ✓ (死叉)
```

**步驟 3: 判斷利潤條件**
```
Current_Price = 0.0520
Average_Cost = 0.04992
Profit_Threshold = 0.04992 × 1.03 = 0.05142

Profit_Condition = 0.0520 ≥ 0.05142 = TRUE ✓

實際利潤率 = (0.0520 - 0.04992) / 0.04992 × 100%
           = 4.17%
```

**步驟 4: 倉位檢查**
```
Current_Total_QRL = 10,924
Core_QRL = 10,924 × 0.70 = 7,646.8
Tradeable_QRL = 10,924 - 7,646.8 = 3,277.2

Position_Check = 3,277.2 > 0 = TRUE ✓
```

**步驟 5: 風險檢查**
```
Daily_Trades = 1 < 5 = TRUE ✓

Elapsed_Time = 14:00:00 - 09:30:00
             = 4.5 小時
             = 16,200 秒

Interval_Check = 16,200 ≥ 300 = TRUE ✓
```

**步驟 6: 計算賣出數量**
```
單次最大賣出:
Max_Sell_Single = 3,277.2 × 0.30 = 983.2 QRL

實際賣出 (保守策略，使用 50%):
Sell_QRL = 983.2 × 0.50 = 491.6 QRL (四捨五入至 491)
```

**步驟 7: 執行賣出**
```
賣出:
- Sell_Amount = 491 QRL
- Sell_Price = 0.0520
- Sell_USDT = 491 × 0.0520 = 25.53 USDT

成本保持:
- Average_Cost = 0.04992 (不變)

已實現利潤:
Realized_Profit = 491 × (0.0520 - 0.04992)
                = 491 × 0.00208
                = 10.21 USDT

利潤率 = 10.21 / (491 × 0.04992) × 100%
       = 10.21 / 24.51 × 100%
       = 41.7% (相對投入成本)

更新後:
- Total_QRL = 10,924 - 491 = 10,433
- USDT_Balance = 454.72 + 25.53 = 480.25
- Average_Cost = 0.04992 (保持)
```

**步驟 8: 更新交易計數**
```
Daily_Trades = 1 + 1 = 2
Last_Trade_Time = Current_Time
```

---

#### 情境 3: 持有決策 (HOLD)

**時間**: 16:00:00
**當前價格**: 0.0505 USDT/QRL

**步驟 1: 計算 MA**
```
MA_short = 0.05080
MA_long = 0.05090
```

**步驟 2: 檢查信號條件**
```
買入檢查:
MA_Condition = 0.05080 > 0.05090 = FALSE ✗
=> 不滿足買入 MA 條件

賣出檢查:
MA_Condition = 0.05080 < 0.05090 = TRUE ✓
Profit_Threshold = 0.04992 × 1.03 = 0.05142
Profit_Condition = 0.0505 ≥ 0.05142 = FALSE ✗
=> 不滿足賣出利潤條件 (差 0.92%)

結論: HOLD (持有不動)
```

**步驟 3: 狀態維持**
```
無交易發生:
- Total_QRL = 10,433 (不變)
- USDT_Balance = 480.25 (不變)
- Average_Cost = 0.04992 (不變)
- Daily_Trades = 2 (不變)
```

---

### 7.2 一週交易週期匯總

**週一至週日完整記錄**:

```
=== 週一 (2025-12-27) ===
09:30 - 買入 924 QRL @ 0.0490
  成本: 0.0500 → 0.04992
  USDT: 500 → 454.72

14:00 - 賣出 491 QRL @ 0.0520
  利潤: +10.21 USDT
  USDT: 454.72 → 480.25

16:00 - 持有 (價格 0.0505)
  
日末狀態:
  QRL: 10,433
  USDT: 480.25
  平均成本: 0.04992
  交易次數: 2

=== 週二 (2025-12-28) ===
10:00 - 買入 1,050 QRL @ 0.0475
  成本: 0.04992 → 0.04950
  USDT: 480.25 → 430.38

15:30 - 持有 (價格 0.0490)

日末狀態:
  QRL: 11,483
  USDT: 430.38
  平均成本: 0.04950
  交易次數: 1

=== 週三至週五 ===
[類似記錄...]

=== 週末總結 ===
週初狀態:
  QRL: 10,000 @ 0.0500
  USDT: 500
  總價值: 1,000 USDT

週末狀態:
  QRL: 12,150 @ 0.04850
  USDT: 385
  總價值: 1,074 USDT (按初始價 0.0500)

成果:
  QRL 增加: +2,150 (+21.5%)
  平均成本降低: -3.0%
  總價值增長: +7.4%
  已實現利潤: +68 USDT
  交易次數: 12 次
```

---

## 8. 公式速查表

### 8.1 核心公式匯總

| 項目 | 公式 | 說明 |
|------|------|------|
| **簡單移動平均** | `MA(n) = Σ(P_i) / n` | 計算 n 期價格平均值 |
| **信號強度** | `Strength = (MA_short - MA_long) / MA_long × 100%` | MA 間距百分比 |
| **買入條件** | `MA_short > MA_long AND Price ≤ Cost × 1.00` | 金叉 + 價格低於成本 |
| **賣出條件** | `MA_short < MA_long AND Price ≥ Cost × 1.03` | 死叉 + 利潤 ≥ 3% |
| **平均成本** | `Avg = Σ(Price_i × Amount_i) / Σ(Amount_i)` | 加權平均買入成本 |
| **核心倉位** | `Core = Total × 0.70` | 70% 永不交易 |
| **可交易量** | `Tradeable = Total - Core` | 總量減核心 |
| **最大單筆** | `Max_Single = Tradeable × 0.30` | 可交易量的 30% |
| **USDT 儲備** | `Reserve = Total_Value × 0.20` | 總價值 20% 保留 |

### 8.2 風控閾值

| 參數 | 預設值 | 說明 |
|------|--------|------|
| `MAX_DAILY_TRADES` | 5 | 每日最大交易次數 |
| `MIN_TRADE_INTERVAL` | 300 秒 | 最小交易間隔 (5 分鐘) |
| `CORE_POSITION_PCT` | 0.70 | 核心倉位比例 (70%) |
| `BUY_THRESHOLD` | 1.00 | 買入價格閾值 (≤ 成本) |
| `SELL_THRESHOLD` | 1.03 | 賣出價格閾值 (≥ 成本×1.03) |
| `MAX_TRADE_PCT` | 0.30 | 單筆最大交易比例 (30%) |
| `USDT_RESERVE_PCT` | 0.20 | USDT 儲備比例 (20%) |
| `MA_SHORT_PERIOD` | 7 | 短期 MA 週期 |
| `MA_LONG_PERIOD` | 25 | 長期 MA 週期 |

---

## 9. 實現檢查清單

### 9.1 策略實現驗證

- [ ] MA 計算實現與公式一致
- [ ] 信號生成邏輯完整
- [ ] 買入條件正確 (MA + 價格 + 風險)
- [ ] 賣出條件正確 (MA + 利潤 + 倉位)
- [ ] 成本計算準確
- [ ] 倉位分層正確
- [ ] 風控限制生效

### 9.2 邊界條件測試

- [ ] MA 數據不足時的處理
- [ ] 零持倉情況
- [ ] 零 USDT 情況
- [ ] 達到每日上限
- [ ] 交易間隔不足
- [ ] 核心倉位保護
- [ ] 數值溢出保護

### 9.3 性能優化

- [ ] MA 計算緩存
- [ ] Redis 數據結構優化
- [ ] 批量計算優化
- [ ] 異步處理

---

## 10. 參考資料

### 10.1 相關文檔

- [QRL 屯幣累積策略詳解](./1-qrl-accumulation-strategy.md)
- [策略、資料來源與倉位分層](./05-Strategies-and-Data.md)
- [架構設計參考](./ADR-001-Architecture-Diagrams.md)

### 10.2 實現代碼

- `src/app/domain/strategies/trading_strategy.py` - 策略實現
- `src/app/domain/risk/limits.py` - 風險管理
- `src/app/domain/position/calculator.py` - 倉位計算

---

**版本**: 1.0.0  
**最後更新**: 2025-12-27  
**作者**: QRL Trading Bot Development Team
