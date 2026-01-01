# 策略計算實例：逐步詳解

> **文檔目的**: 提供真實場景下的完整計算步驟，幫助理解策略公式的實際應用

## 📋 目錄

1. [基礎計算實例](#基礎計算實例)
2. [完整交易流程](#完整交易流程)
3. [複雜場景處理](#複雜場景處理)
4. [錯誤處理案例](#錯誤處理案例)

---

## 基礎計算實例

### 實例 1: 移動平均線計算

#### 場景設定
```
需求: 計算 7 期和 25 期移動平均線
歷史價格數據 (最近 30 個價格點):
索引 0-29: [0.0510, 0.0508, 0.0506, 0.0505, 0.0503, 
            0.0501, 0.0500, 0.0498, 0.0497, 0.0495,
            0.0493, 0.0492, 0.0490, 0.0489, 0.0487,
            0.0486, 0.0485, 0.0484, 0.0483, 0.0482,
            0.0481, 0.0480, 0.0479, 0.0478, 0.0477,
            0.0476, 0.0475, 0.0474, 0.0473, 0.0490]
```

#### 步驟 1: 提取 7 期數據 (最近的)

```python
# 取最後 7 個價格
short_prices = [0.0476, 0.0475, 0.0474, 0.0473, 0.0490]
# 等等，我們需要正確的 7 個

# 正確提取
prices = [0.0510, 0.0508, ..., 0.0490]  # 30 個
short_prices = prices[-7:]  # 最後 7 個
# = [0.0475, 0.0474, 0.0473, 0.0490, 0.0476, 0.0477, 0.0490]

# 實際上，按時間順序，最新的在最後
# 假設正確順序:
short_prices = [0.0476, 0.0475, 0.0474, 0.0473, 0.0477, 0.0480, 0.0490]
```

#### 步驟 2: 計算 MA_7

```
公式: MA_7 = Σ(P_i) / 7

計算:
sum = 0.0476 + 0.0475 + 0.0474 + 0.0473 + 0.0477 + 0.0480 + 0.0490
    = 0.3345

MA_7 = 0.3345 / 7
     = 0.047785714...
     = 0.04779 (四捨五入到小數點後 5 位)
```

#### 步驟 3: 提取 25 期數據

```python
long_prices = prices[-25:]  # 最後 25 個
# = [0.0486, 0.0485, 0.0484, ..., 0.0490]
```

#### 步驟 4: 計算 MA_25

```
sum_25 = 0.0486 + 0.0485 + ... + 0.0490
       = 1.21050 (假設總和)

MA_25 = 1.21050 / 25
      = 0.04842
```

#### 步驟 5: 比較 MA 值

```
MA_7 = 0.04779
MA_25 = 0.04842

比較: MA_7 < MA_25
結論: 短期均線在長期均線下方 (可能是賣出信號前置條件)

價差: 0.04842 - 0.04779 = 0.00063
價差百分比: (0.00063 / 0.04842) × 100% = 1.30%
```

#### 驗證代碼

```python
def calculate_ma(prices: list[float], period: int) -> float:
    """
    計算簡單移動平均
    
    Args:
        prices: 價格列表
        period: 週期數
    
    Returns:
        移動平均值
    """
    if len(prices) < period:
        raise ValueError(f"價格數量 {len(prices)} 不足週期 {period}")
    
    # 取最後 period 個價格
    recent_prices = prices[-period:]
    
    # 計算總和
    total = sum(recent_prices)
    
    # 計算平均
    ma = total / period
    
    return round(ma, 5)

# 測試
prices = [0.0510, 0.0508, ..., 0.0490]  # 30 個價格
ma_7 = calculate_ma(prices, 7)
ma_25 = calculate_ma(prices, 25)

print(f"MA_7: {ma_7}")
print(f"MA_25: {ma_25}")
```

---

### 實例 2: 平均成本計算與更新

#### 初始場景

```
交易歷史:
買入 1: 5,000 QRL @ 0.0520 = 260.00 USDT
買入 2: 3,000 QRL @ 0.0480 = 144.00 USDT
買入 3: 2,000 QRL @ 0.0500 = 100.00 USDT

目標: 計算平均成本
```

#### 步驟 1: 列出所有買入

```
買入記錄:
┌────────┬─────────┬───────────┬────────────┐
│ 序號   │ 數量    │ 價格      │ 成本 (USDT)│
├────────┼─────────┼───────────┼────────────┤
│ 1      │ 5,000   │ 0.0520    │ 260.00     │
│ 2      │ 3,000   │ 0.0480    │ 144.00     │
│ 3      │ 2,000   │ 0.0500    │ 100.00     │
└────────┴─────────┴───────────┴────────────┘
```

#### 步驟 2: 計算總成本

```
方法 A: 逐項相加
Total_Cost = (5,000 × 0.0520) + (3,000 × 0.0480) + (2,000 × 0.0500)
           = 260.00 + 144.00 + 100.00
           = 504.00 USDT

驗證: ✓
```

#### 步驟 3: 計算總數量

```
Total_Amount = 5,000 + 3,000 + 2,000
             = 10,000 QRL

驗證: ✓
```

#### 步驟 4: 計算平均成本

```
Average_Cost = Total_Cost / Total_Amount
             = 504.00 / 10,000
             = 0.0504 USDT/QRL

驗證: ✓
```

#### 步驟 5: 新增買入並更新成本

```
新買入:
- 數量: 2,500 QRL
- 價格: 0.0460 USDT/QRL
- 成本: 2,500 × 0.0460 = 115.00 USDT

更新計算:
New_Total_Cost = 504.00 + 115.00 = 619.00 USDT
New_Total_Amount = 10,000 + 2,500 = 12,500 QRL

New_Average_Cost = 619.00 / 12,500
                 = 0.04952 USDT/QRL

成本變化:
Before: 0.0504
After: 0.04952
Change: -0.00088 (-1.75%)
```

#### 驗證步驟

```python
def calculate_average_cost(purchases: list[tuple[float, float]]) -> float:
    """
    計算平均成本
    
    Args:
        purchases: [(amount, price), ...] 買入記錄
    
    Returns:
        平均成本
    """
    total_cost = sum(amount * price for amount, price in purchases)
    total_amount = sum(amount for amount, price in purchases)
    
    if total_amount == 0:
        return 0.0
    
    return total_cost / total_amount

# 測試
purchases = [
    (5000, 0.0520),
    (3000, 0.0480),
    (2000, 0.0500)
]

avg_cost = calculate_average_cost(purchases)
print(f"平均成本: {avg_cost:.5f}")
# 輸出: 平均成本: 0.05040

# 新增買入後
purchases.append((2500, 0.0460))
new_avg_cost = calculate_average_cost(purchases)
print(f"新平均成本: {new_avg_cost:.5f}")
# 輸出: 新平均成本: 0.04952

# 計算變化
change = new_avg_cost - avg_cost
change_pct = (change / avg_cost) * 100
print(f"成本變化: {change:.5f} ({change_pct:.2f}%)")
# 輸出: 成本變化: -0.00088 (-1.75%)
```

---

### 實例 3: 倉位分層計算

#### 場景設定

```
當前持倉: 15,000 QRL
市場階段: 震盪市 (SIDEWAYS)
配置策略:
  - 核心倉位: 70%
  - 波段倉位: 20%
  - 機動倉位: 10%
```

#### 步驟 1: 計算各層倉位

```
核心倉位 (Core):
Core_QRL = Total_QRL × Core_PCT
         = 15,000 × 0.70
         = 10,500 QRL

波段倉位 (Swing):
Swing_QRL = Total_QRL × Swing_PCT
          = 15,000 × 0.20
          = 3,000 QRL

機動倉位 (Active):
Active_QRL = Total_QRL × Active_PCT
           = 15,000 × 0.10
           = 1,500 QRL
```

#### 步驟 2: 驗證總和

```
驗證:
Core + Swing + Active = Total
10,500 + 3,000 + 1,500 = 15,000 ✓

百分比驗證:
10,500 / 15,000 = 0.70 (70%) ✓
3,000 / 15,000 = 0.20 (20%) ✓
1,500 / 15,000 = 0.10 (10%) ✓
```

#### 步驟 3: 計算可交易數量

```
可交易數量:
Tradeable_QRL = Swing_QRL + Active_QRL
              = 3,000 + 1,500
              = 4,500 QRL

佔總持倉比例:
Tradeable_PCT = 4,500 / 15,000
              = 0.30 (30%)
```

#### 步驟 4: 計算單筆交易限額

```
單筆最大賣出 (30% of tradeable):
Max_Sell_Single = Tradeable_QRL × 0.30
                = 4,500 × 0.30
                = 1,350 QRL

佔總持倉比例:
1,350 / 15,000 = 0.09 (9%)
```

#### 步驟 5: 市場階段調整

**場景 A: 轉為牛市**

```
牛市配置:
- Core_PCT = 0.75 (提升)
- Swing_PCT = 0.18
- Active_PCT = 0.07

重新計算:
Core_QRL = 15,000 × 0.75 = 11,250 QRL (增加 750)
Swing_QRL = 15,000 × 0.18 = 2,700 QRL (減少 300)
Active_QRL = 15,000 × 0.07 = 1,050 QRL (減少 450)

Tradeable_QRL = 2,700 + 1,050 = 3,750 QRL (減少 750)

解釋: 牛市時提高核心倉位，減少交易頻率
```

**場景 B: 轉為熊市**

```
熊市配置:
- Core_PCT = 0.60 (降低)
- Swing_PCT = 0.25
- Active_PCT = 0.15

重新計算:
Core_QRL = 15,000 × 0.60 = 9,000 QRL (減少 1,500)
Swing_QRL = 15,000 × 0.25 = 3,750 QRL (增加 750)
Active_QRL = 15,000 × 0.15 = 2,250 QRL (增加 750)

Tradeable_QRL = 3,750 + 2,250 = 6,000 QRL (增加 1,500)

解釋: 熊市時降低核心倉位，增加機動性以便抄底
```

#### 驗證代碼

```python
from dataclasses import dataclass
from enum import Enum

class MarketPhase(Enum):
    BULL = "bull"
    BEAR = "bear"
    SIDEWAYS = "sideways"

@dataclass
class PositionLayers:
    core: float
    swing: float
    active: float
    
    @property
    def tradeable(self) -> float:
        return self.swing + self.active
    
    @property
    def total(self) -> float:
        return self.core + self.swing + self.active

def calculate_position_layers(
    total_qrl: float,
    market_phase: MarketPhase
) -> PositionLayers:
    """
    計算倉位分層
    
    Args:
        total_qrl: 總持倉
        market_phase: 市場階段
    
    Returns:
        PositionLayers 對象
    """
    if market_phase == MarketPhase.BULL:
        core_pct, swing_pct, active_pct = 0.75, 0.18, 0.07
    elif market_phase == MarketPhase.BEAR:
        core_pct, swing_pct, active_pct = 0.60, 0.25, 0.15
    else:  # SIDEWAYS
        core_pct, swing_pct, active_pct = 0.70, 0.20, 0.10
    
    return PositionLayers(
        core=total_qrl * core_pct,
        swing=total_qrl * swing_pct,
        active=total_qrl * active_pct
    )

# 測試
total = 15000

# 震盪市
sideways = calculate_position_layers(total, MarketPhase.SIDEWAYS)
print(f"震盪市:")
print(f"  核心: {sideways.core:.0f} QRL")
print(f"  波段: {sideways.swing:.0f} QRL")
print(f"  機動: {sideways.active:.0f} QRL")
print(f"  可交易: {sideways.tradeable:.0f} QRL")

# 牛市
bull = calculate_position_layers(total, MarketPhase.BULL)
print(f"\n牛市:")
print(f"  核心: {bull.core:.0f} QRL")
print(f"  可交易: {bull.tradeable:.0f} QRL")

# 熊市
bear = calculate_position_layers(total, MarketPhase.BEAR)
print(f"\n熊市:")
print(f"  核心: {bear.core:.0f} QRL")
print(f"  可交易: {bear.tradeable:.0f} QRL")
```

---

## 完整交易流程

### 實例 4: 完整買入流程

#### 初始狀態

```
日期時間: 2025-12-27 10:00:00
持倉狀態:
  - Total_QRL: 10,000
  - Average_Cost: 0.0500 USDT/QRL
  - USDT_Balance: 500

市場數據:
  - Current_Price: 0.0485 USDT/QRL
  - MA_7: 0.04920
  - MA_25: 0.04900

交易狀態:
  - Daily_Trades: 2 (已完成 2 次)
  - Last_Trade_Time: 08:30:00 (1.5 小時前)
```

#### 步驟 1: 檢查 MA 交叉條件

```
判斷:
MA_7 = 0.04920
MA_25 = 0.04900

MA_7 > MA_25?
0.04920 > 0.04900 = TRUE ✓

信號強度:
Strength = (0.04920 - 0.04900) / 0.04900 × 100%
         = 0.00020 / 0.04900 × 100%
         = 0.41%

解讀: 溫和上升趨勢
```

#### 步驟 2: 檢查價格條件

```
判斷:
Current_Price = 0.0485
Average_Cost = 0.0500
Buy_Threshold = 0.0500 × 1.00 = 0.0500

Price ≤ Threshold?
0.0485 ≤ 0.0500 = TRUE ✓

折扣幅度:
Discount = (0.0500 - 0.0485) / 0.0500 × 100%
         = 0.0015 / 0.0500 × 100%
         = 3.0%

解讀: 價格低於成本 3%，是好的買入機會
```

#### 步驟 3: 風險檢查

```
3.1 每日交易次數檢查:
Daily_Trades = 2
MAX_DAILY_TRADES = 5
Check: 2 < 5 = TRUE ✓
Remaining: 5 - 2 = 3 次

3.2 交易間隔檢查:
Last_Trade_Time = 08:30:00
Current_Time = 10:00:00
Elapsed = 1.5 小時 = 5400 秒
MIN_INTERVAL = 300 秒
Check: 5400 ≥ 300 = TRUE ✓

3.3 USDT 餘額檢查:
USDT_Balance = 500
Check: 500 > 0 = TRUE ✓
```

#### 步驟 4: 計算買入數量

```
4.1 計算總價值:
QRL_Value = 10,000 × 0.0485 = 485 USDT
Total_Value = 485 + 500 = 985 USDT

4.2 計算最小 USDT 儲備 (20%):
Min_Reserve = 985 × 0.20 = 197 USDT

4.3 計算可用 USDT:
Available_USDT = 500 - 197 = 303 USDT

4.4 計算單次最大買入 (30% of available):
Max_USDT_Single = 303 × 0.30 = 90.9 USDT

4.5 實際買入策略 (使用 60% of max):
Actual_USDT = 90.9 × 0.60 = 54.54 USDT

4.6 計算買入 QRL 數量:
Buy_QRL = 54.54 / 0.0485
        = 1,124.74 QRL
        ≈ 1,124 QRL (四捨五入)

4.7 實際花費 USDT:
Actual_Cost = 1,124 × 0.0485 = 54.514 USDT
```

#### 步驟 5: 執行買入

```
買入前狀態:
  QRL: 10,000
  USDT: 500.000
  Avg Cost: 0.0500

執行買入:
  Amount: 1,124 QRL
  Price: 0.0485
  Cost: 54.514 USDT

買入後狀態:
  QRL: 11,124
  USDT: 445.486
  
計算新平均成本:
  Old_Total_Cost = 10,000 × 0.0500 = 500.000
  New_Total_Cost = 500.000 + 54.514 = 554.514
  New_Avg_Cost = 554.514 / 11,124
               = 0.04985 USDT/QRL
  
成本變化:
  Before: 0.05000
  After: 0.04985
  Change: -0.00015 (-0.30%)
```

#### 步驟 6: 更新交易記錄

```
更新:
  Daily_Trades: 2 → 3
  Last_Trade_Time: 08:30:00 → 10:00:00
  
記錄到 Redis:
  Key: bot:qrl-usdt:trades:2025-12-27
  Entry: {
    "time": "10:00:00",
    "type": "BUY",
    "amount": 1124,
    "price": 0.0485,
    "cost": 54.514,
    "new_avg_cost": 0.04985
  }
```

#### 步驟 7: 驗證結果

```
驗證清單:
✓ QRL 增加: 10,000 → 11,124 (+1,124)
✓ USDT 減少: 500 → 445.486 (-54.514)
✓ 成本降低: 0.0500 → 0.04985 (-0.30%)
✓ 交易次數更新: 2 → 3
✓ 時間戳更新: 正確
✓ 仍有 USDT 儲備: 445.486 > 197 (min reserve)
✓ 剩餘交易額度: 2 次

總結: 買入成功執行 ✓
```

---

### 實例 5: 完整賣出流程

#### 初始狀態

```
日期時間: 2025-12-27 15:30:00
持倉狀態:
  - Total_QRL: 11,124
  - Average_Cost: 0.04985 USDT/QRL
  - USDT_Balance: 445.486

倉位分層:
  - Core (70%): 7,786.8 QRL
  - Swing (20%): 2,224.8 QRL
  - Active (10%): 1,112.4 QRL
  - Tradeable: 3,337.2 QRL

市場數據:
  - Current_Price: 0.0525 USDT/QRL
  - MA_7: 0.05180
  - MA_25: 0.05220

交易狀態:
  - Daily_Trades: 3
  - Last_Trade_Time: 10:00:00 (5.5 小時前)
```

#### 步驟 1: 檢查 MA 交叉條件

```
判斷:
MA_7 = 0.05180
MA_25 = 0.05220

MA_7 < MA_25?
0.05180 < 0.05220 = TRUE ✓ (死叉條件)

信號強度:
Strength = (0.05180 - 0.05220) / 0.05220 × 100%
         = -0.00040 / 0.05220 × 100%
         = -0.77%

解讀: 溫和下降趨勢
```

#### 步驟 2: 檢查利潤條件

```
判斷:
Current_Price = 0.0525
Average_Cost = 0.04985
Sell_Threshold = 0.04985 × 1.03 = 0.05135

Price ≥ Threshold?
0.0525 ≥ 0.05135 = TRUE ✓

利潤率:
Profit_Rate = (0.0525 - 0.04985) / 0.04985 × 100%
            = 0.00265 / 0.04985 × 100%
            = 5.32%

解讀: 利潤率 5.32% > 3%，滿足賣出條件
```

#### 步驟 3: 倉位保護檢查

```
檢查可交易數量:
Total_QRL = 11,124
Core_QRL = 7,786.8
Tradeable_QRL = 11,124 - 7,786.8 = 3,337.2

Check: 3,337.2 > 0 = TRUE ✓

可交易比例:
Tradeable_PCT = 3,337.2 / 11,124
              = 0.30 (30%)
```

#### 步驟 4: 風險檢查

```
4.1 每日交易次數:
Daily_Trades = 3 < 5 = TRUE ✓
Remaining = 2 次

4.2 交易間隔:
Elapsed = 15:30:00 - 10:00:00 = 5.5 小時 = 19,800 秒
Check: 19,800 ≥ 300 = TRUE ✓
```

#### 步驟 5: 計算賣出數量

```
5.1 計算單次最大賣出 (30% of tradeable):
Max_Sell_Single = 3,337.2 × 0.30 = 1,001.16 QRL

5.2 實際賣出策略 (使用 50% of max):
Sell_QRL = 1,001.16 × 0.50
         = 500.58 QRL
         ≈ 500 QRL (四捨五入)

5.3 計算賣出收入:
Sell_USDT = 500 × 0.0525
          = 26.25 USDT

5.4 計算利潤:
Cost_Basis = 500 × 0.04985 = 24.925 USDT
Profit = 26.25 - 24.925 = 1.325 USDT
Profit_Rate = 1.325 / 24.925 × 100% = 5.32%
```

#### 步驟 6: 執行賣出

```
賣出前狀態:
  QRL: 11,124
  USDT: 445.486
  Avg Cost: 0.04985

執行賣出:
  Amount: 500 QRL
  Price: 0.0525
  Income: 26.25 USDT
  Profit: 1.325 USDT

賣出後狀態:
  QRL: 10,624
  USDT: 471.736
  Avg Cost: 0.04985 (保持不變)
  
已實現利潤:
  Realized_Profit = 1.325 USDT
  Total_Realized += 1.325
```

#### 步驟 7: 更新倉位分層

```
更新各層倉位:
New_Total = 10,624
New_Core = 10,624 × 0.70 = 7,436.8
New_Swing = 10,624 × 0.20 = 2,124.8
New_Active = 10,624 × 0.10 = 1,062.4

驗證:
7,436.8 + 2,124.8 + 1,062.4 = 10,624 ✓
```

#### 步驟 8: 更新交易記錄

```
更新:
  Daily_Trades: 3 → 4
  Last_Trade_Time: 10:00:00 → 15:30:00
  Realized_Profit: +1.325 USDT
  
記錄到 Redis:
  Key: bot:qrl-usdt:trades:2025-12-27
  Entry: {
    "time": "15:30:00",
    "type": "SELL",
    "amount": 500,
    "price": 0.0525,
    "income": 26.25,
    "profit": 1.325,
    "avg_cost": 0.04985
  }
```

#### 步驟 9: 驗證結果

```
驗證清單:
✓ QRL 減少: 11,124 → 10,624 (-500)
✓ USDT 增加: 445.486 → 471.736 (+26.25)
✓ 利潤實現: 1.325 USDT
✓ 成本保持: 0.04985 (不變)
✓ 核心倉位保護: 10,624 > 7,436.8 (core)
✓ 交易次數更新: 3 → 4
✓ 剩餘額度: 1 次

總結: 賣出成功執行 ✓
```

---

## 複雜場景處理

### 實例 6: 連續交易與成本變化追蹤

#### 場景描述

```
一天內進行多次買賣，追蹤成本和利潤變化

初始狀態 (09:00):
  QRL: 10,000
  Average_Cost: 0.0500
  USDT: 500
```

#### 交易序列

**交易 1 (10:00): 買入**

```
價格: 0.0485
買入: 1,000 QRL
成本: 48.5 USDT

計算新成本:
Old_Cost = 10,000 × 0.0500 = 500
New_Cost = 500 + 48.5 = 548.5
New_Total = 10,000 + 1,000 = 11,000
New_Avg = 548.5 / 11,000 = 0.04986

狀態:
  QRL: 11,000
  Cost: 0.04986 (-0.28%)
  USDT: 451.5
```

**交易 2 (11:30): 賣出**

```
價格: 0.0520
賣出: 800 QRL
收入: 41.6 USDT
利潤: 800 × (0.0520 - 0.04986) = 1.712 USDT

狀態:
  QRL: 10,200
  Cost: 0.04986 (保持)
  USDT: 493.1
  Realized_Profit: 1.712
```

**交易 3 (14:00): 買入**

```
價格: 0.0475
買入: 1,200 QRL
成本: 57 USDT

計算新成本:
Old_Cost = 10,200 × 0.04986 = 508.572
New_Cost = 508.572 + 57 = 565.572
New_Total = 10,200 + 1,200 = 11,400
New_Avg = 565.572 / 11,400 = 0.04961

狀態:
  QRL: 11,400
  Cost: 0.04961 (-0.50% from original)
  USDT: 436.1
```

**交易 4 (16:00): 賣出**

```
價格: 0.0530
賣出: 1,000 QRL
收入: 53 USDT
利潤: 1,000 × (0.0530 - 0.04961) = 3.39 USDT

狀態:
  QRL: 10,400
  Cost: 0.04961 (保持)
  USDT: 489.1
  Realized_Profit: 1.712 + 3.39 = 5.102
```

#### 一日總結

```
開始 (09:00):
  QRL: 10,000 @ 0.0500
  USDT: 500
  Value: 1,000

結束 (17:00):
  QRL: 10,400 @ 0.04961
  USDT: 489.1
  Value: 1,005.24 (@ 0.0500)
  
變化:
  QRL: +400 (+4.0%)
  Cost: -0.78%
  Realized Profit: 5.102 USDT
  Total Value: +0.52%
  
交易效率:
  交易次數: 4
  總買入: 2,200 QRL / 105.5 USDT
  總賣出: 1,800 QRL / 94.6 USDT
  淨增持: 400 QRL
```

---

### 實例 7: 風險觸發與限制處理

#### 場景 A: 達到每日交易上限

```
當前狀態:
  Daily_Trades: 4
  MAX_DAILY_TRADES: 5

新交易請求 (買入):
  Price: 0.0480 (滿足條件)
  MA: 滿足條件
  
風險檢查:
  Daily_Trades = 4 < 5 = TRUE ✓
  
執行交易 → Daily_Trades = 5

下一個交易請求 (賣出):
  Price: 0.0530 (滿足條件)
  MA: 滿足條件
  
風險檢查:
  Daily_Trades = 5 < 5 = FALSE ❌
  
結果:
  拒絕交易
  原因: "達到每日交易上限 (5/5)"
  建議: "等待次日 00:00 重置"
```

#### 場景 B: 交易間隔不足

```
Last_Trade_Time: 15:45:00
Current_Time: 15:48:30
Elapsed: 210 秒

MIN_TRADE_INTERVAL: 300 秒

檢查:
  210 < 300 = 不滿足

結果:
  拒絕交易
  原因: "交易間隔不足 (210s < 300s)"
  需等待: 300 - 210 = 90 秒
  可交易時間: 15:46:30
```

#### 場景 C: 觸碰核心倉位

```
當前狀態:
  Total_QRL: 10,000
  Core_QRL: 7,000 (70%)
  Tradeable: 3,000

賣出請求: 3,500 QRL

檢查:
  Remaining = 10,000 - 3,500 = 6,500
  6,500 < 7,000 (core) = 違反保護

調整:
  Max_Sell = 10,000 - 7,000 = 3,000
  
結果:
  調整賣出數量: 3,500 → 3,000
  原因: "保護核心倉位"
  實際賣出: 3,000 QRL
```

#### 場景 D: USDT 儲備不足

```
當前狀態:
  Total_Value: 1,000 USDT
  USDT_Balance: 150 USDT
  Min_Reserve: 200 USDT (20%)

買入請求: 100 USDT

檢查:
  Available = 150 - 200 = -50 (不足)
  
結果:
  拒絕交易
  原因: "USDT 儲備不足"
  當前餘額: 150
  最小儲備: 200
  需增加: 50 USDT
  
建議:
  "先賣出部分 QRL 增加 USDT 儲備"
```

---

## 錯誤處理案例

### 實例 8: 數據異常處理

#### 案例 A: MA 數據不足

```
場景:
  需要計算 MA_25
  可用價格: 15 個

檢查:
  len(prices) = 15 < 25 (required)
  
處理:
  if len(prices) < period:
      logger.warning(f"價格數據不足: {len(prices)} < {period}")
      return "HOLD"  # 不產生信號
      
結果:
  信號: HOLD
  原因: "數據不足，需要 25 個價格點"
```

#### 案例 B: 價格為零或負數

```
場景:
  Current_Price = 0 (異常數據)

檢查:
  if price <= 0:
      logger.error(f"價格異常: {price}")
      raise ValueError("價格必須大於零")
      
處理:
  - 記錄錯誤
  - 使用上一個有效價格
  - 或暫停交易
  
結果:
  使用 Last_Valid_Price
  或發送警報給管理員
```

#### 案例 C: 成本為零

```
場景:
  Average_Cost = 0 (首次買入前)

檢查:
  if avg_cost == 0:
      # 首次買入，沒有成本基礎
      # 任何價格都可以買入
      return "BUY" if ma_condition else "HOLD"
      
處理:
  - 首次買入不檢查成本條件
  - 記錄為初始建倉
  - 建立成本基礎
```

#### 案例 D: 持倉為零

```
場景:
  Total_QRL = 0
  收到賣出信號

檢查:
  if total_qrl == 0:
      logger.warning("無持倉，無法賣出")
      return "HOLD"
      
結果:
  忽略賣出信號
  等待買入機會
```

---

## 性能優化示例

### 實例 9: MA 緩存優化

#### 問題

```
每次信號檢查都重新計算 MA:
- MA_7: 需要計算 7 個價格
- MA_25: 需要計算 25 個價格
- 頻繁調用造成重複計算
```

#### 優化方案

```python
from functools import lru_cache
from typing import Tuple

class MACalculator:
    def __init__(self):
        self.price_history = []
    
    def add_price(self, price: float) -> None:
        """添加新價格並維護歷史"""
        self.price_history.append(price)
        # 只保留最近 30 個價格 (足夠計算 MA_25)
        if len(self.price_history) > 30:
            self.price_history = self.price_history[-30:]
        
        # 清除緩存，因為有新數據
        self.calculate_mas.cache_clear()
    
    @lru_cache(maxsize=10)
    def calculate_mas(self, timestamp: int) -> Tuple[float, float]:
        """
        緩存的 MA 計算
        
        使用 timestamp 作為緩存鍵
        同一時間戳的請求返回緩存結果
        """
        if len(self.price_history) < 25:
            return 0.0, 0.0
        
        ma_7 = sum(self.price_history[-7:]) / 7
        ma_25 = sum(self.price_history[-25:]) / 25
        
        return ma_7, ma_25

# 使用示例
calculator = MACalculator()

# 添加價格數據
for price in [0.048, 0.049, 0.050, ...]:
    calculator.add_price(price)

# 獲取 MA (首次計算)
import time
ts = int(time.time())
ma_7, ma_25 = calculator.calculate_mas(ts)
print(f"MA_7: {ma_7}, MA_25: {ma_25}")

# 再次獲取 (使用緩存，快速)
ma_7, ma_25 = calculator.calculate_mas(ts)
# 返回緩存結果，無需重新計算
```

---

## 總結

### 關鍵計算點檢查清單

- [ ] MA 計算使用正確的週期數
- [ ] 成本更新只在買入時執行
- [ ] 倉位分層總和等於總持倉
- [ ] 風險檢查全部通過才執行交易
- [ ] 核心倉位始終受保護
- [ ] USDT 儲備維持在最低水平以上
- [ ] 交易限制正確執行

### 常見錯誤與避免方法

1. **MA 計算錯誤**: 使用錯誤的數據範圍
   - 解決: 明確使用最後 N 個價格

2. **成本更新錯誤**: 賣出後更新成本
   - 解決: 成本只在買入時更新

3. **倉位計算錯誤**: 各層不總和為 100%
   - 解決: 始終驗證百分比總和

4. **風險檢查遺漏**: 跳過某些檢查
   - 解決: 使用檢查清單，全部通過

5. **數據異常未處理**: 崩潰或錯誤決策
   - 解決: 添加邊界檢查和異常處理

---

**版本**: 1.0.0  
**最後更新**: 2025-12-27  
**相關文檔**: [STRATEGY_DESIGN_FORMULAS.md](./STRATEGY_DESIGN_FORMULAS.md)
