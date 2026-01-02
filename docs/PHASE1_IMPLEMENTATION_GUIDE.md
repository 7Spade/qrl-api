# Phase 1 Implementation Guide: Domain Layer Restructuring

## 概述 (Overview)

本指南提供 Phase 1 的詳細實施步驟，使用順序思維方法（Sequential Thinking）和 Software Planning Tool 規劃出具體的任務清單。

**目標**: 重組 domain 層以符合 Clean Architecture 原則，同時保持所有現有功能不變。

## 實施策略 (Implementation Strategy)

### 選擇方案：逐階段增量實施
基於風險分析，我們採用以下策略：

1. **先完成 Phase 1（推薦）**
   - ✅ 有自動化工具支持
   - ✅ Domain 層相對獨立
   - ✅ 可以建立工作流程
   - ✅ 驗證方法和工具
   - ✅ 成功後可應用到其他階段

2. **關鍵風險和緩解**
   - 風險：導入路徑更新可能遺漏
   - 緩解：使用 grep 搜索，創建檢查清單
   - 風險：測試可能失敗
   - 緩解：逐步運行測試，增量提交

## 任務清單 (Task List)

使用 Software Planning Tool 創建的詳細任務。總計 **21 個具體任務**，分為 6 個階段。

### Stage 1: 準備工作 (Preparation)
**複雜度**: 3/10 | **預計時間**: 2 小時

#### 任務 1.1: 創建 feature branch 並驗證基線
**複雜度**: 3/10
```bash
# 創建功能分支
git checkout -b feature/phase1-domain-restructure

# 運行基線測試
make test

# 記錄當前結構
tree src/app/domain -L 3 > docs/phase1_baseline_structure.txt
```

**驗收標準**:
- [ ] Feature branch 創建成功
- [ ] 所有測試通過
- [ ] 基線結構已記錄

#### 任務 1.2: 分析並記錄當前導入
**複雜度**: 4/10
```bash
# 尋找所有 domain 導入
grep -r "from src.app.domain" src/app/ > docs/phase1_import_map.txt

# 計算各模組導入數量
grep -r "from src.app.domain.models" src/app/ | wc -l
grep -r "from src.app.domain.strategies" src/app/ | wc -l
grep -r "from src.app.domain.events" src/app/ | wc -l
```

**驗收標準**:
- [ ] 導入映射文件已創建
- [ ] 識別出所有關鍵依賴
- [ ] 統計導入數量

---

### Stage 2: 自動化結構創建 (Automated Structure)
**複雜度**: 4/10 | **預計時間**: 1 小時

#### 任務 2.1: 運行自動化腳本（dry-run 模式）
**複雜度**: 2/10
```bash
# 運行 dry-run 預覽變更
python scripts/restructure_phase1_domain.py --dry-run

# 仔細檢查輸出:
# - domain/trading/ 結構將被創建
# - repositories.py 內容正確
# - errors.py 內容正確
```

**驗收標準**:
- [ ] Dry-run 成功完成
- [ ] 預覽的目錄結構正確
- [ ] 生成的文件內容合理

#### 任務 2.2: 執行自動化腳本創建結構
**複雜度**: 3/10
```bash
# 執行腳本
python scripts/restructure_phase1_domain.py --execute

# 驗證創建的結構
ls -la src/app/domain/trading/
ls -la src/app/domain/trading/entities/
ls -la src/app/domain/trading/value_objects/

# 檢查生成的文件
cat src/app/domain/trading/repositories.py
cat src/app/domain/trading/errors.py
```

**驗收標準**:
- [ ] domain/trading/ 結構已創建
- [ ] repositories.py 已生成（4個抽象類）
- [ ] errors.py 已生成（10個異常類）
- [ ] 所有 __init__.py 文件已創建

---

### Stage 3: 文件遷移 (File Migration)
**複雜度**: 6/10 | **預計時間**: 3 小時

#### 任務 3.1: 遷移實體文件
**複雜度**: 5/10
```bash
# 移動實體文件
mv src/app/domain/models/order.py src/app/domain/trading/entities/
mv src/app/domain/models/trade.py src/app/domain/trading/entities/
mv src/app/domain/models/position.py src/app/domain/trading/entities/
mv src/app/domain/models/account.py src/app/domain/trading/entities/

# 驗證內容未變
git diff --no-index src/app/domain/models/ src/app/domain/trading/entities/
```

**驗收標準**:
- [ ] Order.py 在正確位置
- [ ] Trade.py 在正確位置
- [ ] Position.py 在正確位置
- [ ] Account.py 在正確位置
- [ ] 文件內容完全不變

#### 任務 3.2: 遷移值對象文件
**複雜度**: 4/10
```bash
# 移動值對象文件
mv src/app/domain/models/price.py src/app/domain/trading/value_objects/
mv src/app/domain/models/balance.py src/app/domain/trading/value_objects/

# 驗證文件存在
ls -la src/app/domain/trading/value_objects/
```

**驗收標準**:
- [ ] Price.py 在正確位置
- [ ] Balance.py 在正確位置

#### 任務 3.3: 遷移策略目錄
**複雜度**: 5/10
```bash
# 複製策略目錄（暫時保留原目錄）
cp -r src/app/domain/strategies/* src/app/domain/trading/strategies/

# 驗證結構保留
diff -r src/app/domain/strategies/ src/app/domain/trading/strategies/

# 檢查子目錄
ls -la src/app/domain/trading/strategies/indicators/
ls -la src/app/domain/trading/strategies/filters/
```

**驗收標準**:
- [ ] 所有策略文件已遷移
- [ ] indicators/ 子目錄完整
- [ ] filters/ 子目錄完整

#### 任務 3.4: 遷移事件目錄
**複雜度**: 4/10
```bash
# 複製事件目錄
cp -r src/app/domain/events/* src/app/domain/trading/events/

# 驗證所有文件已遷移
ls -la src/app/domain/trading/events/
```

**驗收標準**:
- [ ] 所有事件文件已遷移

#### 任務 3.5: 遷移 Position 服務
**複雜度**: 5/10
```bash
# 移動 position 服務文件
mv src/app/domain/position/calculator.py src/app/domain/trading/services/position/
mv src/app/domain/position/updater.py src/app/domain/trading/services/position/

# 驗證文件在新位置
ls -la src/app/domain/trading/services/position/
```

**驗收標準**:
- [ ] calculator.py 在正確位置
- [ ] updater.py 在正確位置

#### 任務 3.6: 遷移 Risk 服務和驗證器
**複雜度**: 6/10
```bash
# 移動 risk 服務文件
mv src/app/domain/risk/limits.py src/app/domain/trading/services/risk/
mv src/app/domain/risk/stop_loss.py src/app/domain/trading/services/risk/

# 複製 validators 子目錄
cp -r src/app/domain/risk/validators/* src/app/domain/trading/services/risk/validators/

# 驗證結構
ls -la src/app/domain/trading/services/risk/
ls -la src/app/domain/trading/services/risk/validators/
```

**驗收標準**:
- [ ] limits.py 在正確位置
- [ ] stop_loss.py 在正確位置
- [ ] validators/ 子目錄完整

---

### Stage 4: 導入路徑更新 (Import Path Updates)
**複雜度**: 8/10 | **預計時間**: 4 小時

#### 任務 4.1: 更新 domain 層內部導入
**複雜度**: 7/10
```python
# 導入更新範例
# 之前:
from src.app.domain.models.order import Order
from src.app.domain.models.price import Price

# 之後:
from src.app.domain.trading.entities.order import Order
from src.app.domain.trading.value_objects.price import Price

# 使用 grep 測試模式
grep -r "from src.app.domain.models" src/app/domain/trading/
```

**驗收標準**:
- [ ] domain 層內所有導入已更新
- [ ] 無導入錯誤

#### 任務 4.2: 更新 application 層導入
**複雜度**: 8/10
```bash
# 尋找所有 application 層的 domain 導入
grep -r "from src.app.domain.models" src/app/application/ -l

# 系統性更新每個文件
# 更新後測試每個模組
python -c "from src.app.application.trading import *"
```

**驗收標準**:
- [ ] application 層所有導入已更新
- [ ] 每個模組可以成功導入

#### 任務 4.3: 更新 infrastructure 層導入
**複雜度**: 7/10
```bash
# 尋找 infrastructure 導入
grep -r "from src.app.domain" src/app/infrastructure/ -l

# 更新適配器中的導入路徑
# 更新後測試編譯
python -m py_compile src/app/infrastructure/**/*.py
```

**驗收標準**:
- [ ] infrastructure 層所有導入已更新
- [ ] 編譯無錯誤

#### 任務 4.4: 更新測試導入
**複雜度**: 6/10
```bash
# 更新測試導入
grep -r "from src.app.domain.models" tests/ -l

# 更新每個測試文件
# 更新後運行測試驗證
pytest tests/domain/test_entities.py -v
```

**驗收標準**:
- [ ] 測試文件所有導入已更新
- [ ] 測試可以運行

---

### Stage 5: 測試與驗證 (Testing & Validation)
**複雜度**: 7/10 | **預計時間**: 3 小時

#### 任務 5.1: 運行並修復 domain 層測試
**複雜度**: 7/10
```bash
# 運行 domain 特定測試
pytest tests/domain/ -v --tb=short

# 如果失敗，分析並修復:
# 1. 導入錯誤 → 檢查導入路徑
# 2. 模組未找到 → 驗證文件位置
# 3. 屬性錯誤 → 檢查 __init__.py 導出
```

**驗收標準**:
- [ ] 所有 domain 測試通過
- [ ] 無導入錯誤

#### 任務 5.2: 驗證所有導入可編譯
**複雜度**: 5/10
```bash
# 編譯所有 Python 文件檢查導入
python -m py_compile src/app/domain/trading/**/*.py

# 檢查導入錯誤
python -c "
from src.app.domain.trading.entities import *
from src.app.domain.trading.value_objects import *
from src.app.domain.trading.strategies import *
from src.app.domain.trading.services import *
print('All imports successful')
"
```

**驗收標準**:
- [ ] 所有文件編譯成功
- [ ] 所有模組可導入

#### 任務 5.3: 運行 linting 並修復問題
**複雜度**: 4/10
```bash
# 對 domain 層運行 linting
make lint

# 或特定運行:
ruff check src/app/domain/trading/

# 修復問題:
# - 導入順序
# - 未使用的導入
# - 行長度
# - 格式化
```

**驗收標準**:
- [ ] Linting 通過
- [ ] 代碼風格符合標準

#### 任務 5.4: 運行類型檢查並修復問題
**複雜度**: 6/10
```bash
# 運行類型檢查
make type

# 或特定運行:
mypy src/app/domain/trading/

# 修復類型錯誤:
# - 缺少類型提示
# - 不正確的類型註解
# - 導入類型 stubs
```

**驗收標準**:
- [ ] 類型檢查通過
- [ ] 所有類型註解正確

#### 任務 5.5: 運行完整測試套件驗證
**複雜度**: 8/10
```bash
# 運行完整應用測試套件
pytest tests/ -v

# 預期結果:
# - 所有測試通過或與基線相同
# - 沒有引入新的失敗
# - 測試覆蓋率維持在 85%+
```

**驗收標準**:
- [ ] 所有測試通過
- [ ] 測試覆蓋率 ≥85%
- [ ] 無新引入的失敗

---

### Stage 6: 清理與文檔 (Cleanup & Documentation)
**複雜度**: 3/10 | **預計時間**: 1 小時

#### 任務 6.1: 刪除舊目錄
**複雜度**: 3/10
```bash
# 驗證遷移完成後:

# 檢查無舊路徑引用
grep -r "from src.app.domain.models" src/app/
grep -r "from src.app.domain.position" src/app/
grep -r "from src.app.domain.risk" src/app/

# 如果無結果，安全刪除:
rm -rf src/app/domain/models/
rm -rf src/app/domain/position/
rm -rf src/app/domain/risk/
rm -rf src/app/domain/strategies/
rm -rf src/app/domain/events/
```

**驗收標準**:
- [ ] 無舊路徑引用
- [ ] 舊目錄已刪除

#### 任務 6.2: 更新文檔
**複雜度**: 3/10
```markdown
# 更新 README.md 專案結構部分:

## Project Structure (Updated)
src/app/
├── domain/
│   └── trading/
│       ├── entities/          # Order, Trade, Position, Account
│       ├── value_objects/     # Price, Balance
│       ├── strategies/        # Trading strategies
│       ├── services/          # Position, Risk services
│       ├── events/            # Domain events
│       ├── repositories.py    # Repository interfaces
│       └── errors.py          # Domain exceptions
```

**驗收標準**:
- [ ] README.md 已更新
- [ ] 架構文檔已更新
- [ ] 遷移完成已記錄

---

## 成功標準 (Success Criteria)

- [ ] 所有 domain 文件在 domain/trading/ 結構中
- [ ] repositories.py 和 errors.py 已創建
- [ ] 所有測試通過（100% 基線）
- [ ] 無導入錯誤
- [ ] Linting 通過
- [ ] 類型檢查通過
- [ ] 舊目錄已刪除
- [ ] 文檔已更新

## 回滾計劃 (Rollback Plan)

```bash
# 如果遇到問題，回滾到上一個提交
git reset --hard HEAD~1

# 或回滾特定變更
git checkout HEAD~1 -- src/app/domain/
```

## 預計時間表 (Estimated Timeline)

| 階段 | 時間 |
|------|------|
| Stage 1: 準備工作 | 2 小時 |
| Stage 2: 自動化結構 | 1 小時 |
| Stage 3: 文件遷移 | 3 小時 |
| Stage 4: 導入更新 | 4 小時 |
| Stage 5: 測試驗證 | 3 小時 |
| Stage 6: 清理文檔 | 1 小時 |
| **總計** | **~14 小時 (2 個工作日)** |

## Phase 1 之後的下一步

1. 檢視並記錄經驗教訓
2. 應用類似方法到 Phase 2（Application 層）
3. 繼續執行剩餘階段
4. 最終驗證和合併

---

## 使用 Software Planning Tool 追蹤

所有任務已添加到 Software Planning Tool 中，可以使用以下命令查看和更新：

```bash
# 查看所有任務
software-planning-tool-get_todos

# 更新任務狀態
software-planning-tool-update_todo_status --todoId="<id>" --isComplete=true
```

## 相關文檔

- [ARCHITECTURE_RESTRUCTURE_PLAN.md](./ARCHITECTURE_RESTRUCTURE_PLAN.md) - 詳細實施計劃
- [ARCHITECTURE_RESTRUCTURE_DIAGRAM.md](./ARCHITECTURE_RESTRUCTURE_DIAGRAM.md) - 視覺化指南
- [ARCHITECTURE_RESTRUCTURE_SUMMARY.md](./ARCHITECTURE_RESTRUCTURE_SUMMARY.md) - 執行摘要
- [scripts/README.md](../scripts/README.md) - 自動化工具指南

---

**文檔版本**: 1.0  
**最後更新**: 2026-01-02  
**狀態**: ✅ 就緒可執行  
**使用方法**: 順序思維 + Software Planning Tool
