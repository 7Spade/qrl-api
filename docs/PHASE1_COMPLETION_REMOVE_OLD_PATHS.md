# Phase 1 Completion: Remove Old Paths

## 目標 (Goal)

完成 Phase 1 的最後步驟：移除舊的導入路徑，同時保持功能正常運作。
Complete the final steps of Phase 1: Remove old import paths while maintaining functionality.

## 策略 (Strategy)

**關鍵洞察**: "不影響功能" 意味著先更新所有導入引用，然後才移除舊結構。
**Key Insight**: "Without affecting functionality" means update all import references first, THEN remove old structure.

---

## Stage 1: 分析 (Analysis) - 30 分鐘

### Task 1.1: 搜索並記錄所有舊導入用法
**Search and Catalog All Old Import Usages**

**發現結果 (Findings)**:
- 共 12 個文件使用舊導入路徑
- 9 個文件在 domain 層（內部引用）
- 3 個文件在 tests

**Domain 層文件 (9 files)**:
```python
# 1. src/app/domain/position/updater.py (2 imports)
from src.app.domain.models.position import Position
from src.app.domain.position.calculator import PositionManager

# 2. src/app/domain/strategies/indicators/__init__.py (1 import)
from src.app.domain.strategies.indicators.ma_signal_generator import MASignalGenerator

# 3. src/app/domain/strategies/example_strategy.py (2 imports)
from src.app.domain.strategies.trading_strategy import TradingStrategy as LegacyTradingStrategy
from src.app.domain.strategies.base import BaseStrategy

# 4. src/app/domain/strategies/filters/__init__.py (1 import)
from src.app.domain.strategies.filters.cost_filter import CostFilter

# 5. src/app.domain/strategies/trading_strategy.py (2 imports)
from src.app.domain.strategies.indicators import MASignalGenerator
from src.app.domain.strategies.filters import CostFilter

# 6. src/app/domain/risk/limits.py (2 imports)
from src.app.domain.risk.validators.trade_frequency_validator import ...
from src.app.domain.risk.validators.position_validator import PositionValidator

# 7. src/app/domain/risk/validators/__init__.py (2 imports)
from src.app.domain.risk.validators.trade_frequency_validator import ...
from src.app.domain.risk.validators.position_validator import PositionValidator
```

**測試文件 (3 files)**:
```python
# tests/test_module_imports.py (3 imports)
from src.app.domain.position.calculator import PositionManager
from src.app.domain.risk.limits import RiskManager
from src.app.domain.strategies.trading_strategy import TradingStrategy
```

**複雜度 (Complexity)**: 2/10
**時間 (Time)**: 30 minutes ✅ DONE

---

## Stage 2: 導入更新 (Import Updates) - 2 小時

### Task 1.2: 更新 Domain 層內部導入 (9 files)
**Update Domain Layer Internal Imports**

**需要更新的文件清單**:

1. **src/app/domain/position/updater.py**
```python
# OLD
from src.app.domain.models.position import Position
from src.app.domain.position.calculator import PositionManager

# NEW
from src.app.domain.trading.entities import Position
from src.app.domain.trading.services.position import PositionManager
```

2. **src/app/domain/strategies/indicators/__init__.py**
```python
# OLD
from src.app.domain.strategies.indicators.ma_signal_generator import MASignalGenerator

# NEW
from src.app.domain.trading.strategies.indicators.ma_signal_generator import MASignalGenerator
```

3. **src/app/domain/strategies/example_strategy.py**
```python
# OLD
from src.app.domain.strategies.trading_strategy import TradingStrategy as LegacyTradingStrategy
from src.app.domain.strategies.base import BaseStrategy

# NEW
from src.app.domain.trading.strategies.trading_strategy import TradingStrategy as LegacyTradingStrategy
from src.app.domain.trading.strategies.base import BaseStrategy
```

4. **src/app/domain/strategies/filters/__init__.py**
```python
# OLD
from src.app.domain.strategies.filters.cost_filter import CostFilter

# NEW
from src.app.domain.trading.strategies.filters.cost_filter import CostFilter
```

5. **src/app/domain/strategies/trading_strategy.py**
```python
# OLD
from src.app.domain.strategies.indicators import MASignalGenerator
from src.app.domain.strategies.filters import CostFilter

# NEW
from src.app.domain.trading.strategies.indicators import MASignalGenerator
from src.app.domain.trading.strategies.filters import CostFilter
```

6. **src/app/domain/risk/limits.py**
```python
# OLD
from src.app.domain.risk.validators.trade_frequency_validator import ...
from src.app.domain.risk.validators.position_validator import PositionValidator

# NEW
from src.app.domain.trading.services.risk.validators.trade_frequency_validator import ...
from src.app.domain.trading.services.risk.validators.position_validator import PositionValidator
```

7. **src/app/domain/risk/validators/__init__.py**
```python
# OLD
from src.app.domain.risk.validators.trade_frequency_validator import ...
from src.app.domain.risk.validators.position_validator import PositionValidator

# NEW
from src.app.domain.trading.services.risk.validators.trade_frequency_validator import ...
from src.app.domain.trading.services.risk.validators.position_validator import PositionValidator
```

**複雜度 (Complexity)**: 5/10
**時間 (Time)**: 1.5 hours

---

### Task 1.3: 更新測試導入 (3 files)
**Update Test Imports**

**tests/test_module_imports.py**:
```python
# OLD
from src.app.domain.position.calculator import PositionManager
from src.app.domain.risk.limits import RiskManager
from src.app.domain.strategies.trading_strategy import TradingStrategy

# NEW
from src.app.domain.trading.services.position import PositionManager
from src.app.domain.trading.services.risk import RiskManager
from src.app.domain.trading.strategies import TradingStrategy
```

**複雜度 (Complexity)**: 3/10
**時間 (Time)**: 30 minutes

---

### Task 1.4: 驗證導入編譯
**Verify Imports Compile**

```bash
# Compile check all updated files
python -m py_compile src/app/domain/position/updater.py
python -m py_compile src/app/domain/strategies/indicators/__init__.py
python -m py_compile src/app/domain/strategies/example_strategy.py
python -m py_compile src/app/domain/strategies/filters/__init__.py
python -m py_compile src/app/domain/strategies/trading_strategy.py
python -m py_compile src/app/domain/risk/limits.py
python -m py_compile src/app/domain/risk/validators/__init__.py
python -m py_compile tests/test_module_imports.py
```

**複雜度 (Complexity)**: 2/10
**時間 (Time)**: 15 minutes

---

## Stage 3: 結構移除 (Structure Removal) - 30 分鐘

### Task 1.5: 移除舊目錄文件
**Remove Old Directory Files**

**要保留的**:
- domain/trading/* (所有新文件)

**要移除的**:
- domain/models/ (except __pycache__)
- domain/events/ (except __pycache__)  
- domain/strategies/ (except __pycache__)
- domain/position/ (entire directory)
- domain/risk/ (entire directory)

**命令 (Commands)**:
```bash
# Remove old directories (keeping __pycache__ is ok, will be in .gitignore)
rm -rf src/app/domain/models/*.py
rm -rf src/app/domain/events/*.py
rm -rf src/app/domain/strategies/*.py
rm -rf src/app/domain/position/
rm -rf src/app/domain/risk/
```

**複雜度 (Complexity)**: 3/10
**時間 (Time)**: 15 minutes

---

### Task 1.6: 清理舊的 __init__.py 重新導出
**Clean Up Old __init__.py Re-exports**

Since we're removing the old directories entirely, we also remove their __init__.py files with re-exports and deprecation warnings.

**複雜度 (Complexity)**: 2/10
**時間 (Time)**: 15 minutes

---

## Stage 4: 驗證 (Validation) - 1 小時

### Task 1.7: 運行完整測試套件
**Run Full Test Suite**

```bash
# Run all domain tests
pytest tests/domain/ -v

# Run full test suite
pytest tests/ -v
```

**預期結果 (Expected)**:
- 64 passed, 5 failed (same as baseline)
- 0 new failures
- All import errors resolved

**複雜度 (Complexity)**: 5/10
**時間 (Time)**: 45 minutes

---

### Task 1.8: 最終驗證和文檔更新
**Final Validation and Documentation Update**

**驗證檢查清單 (Validation Checklist)**:
- [ ] All old import paths removed from codebase
- [ ] All new import paths work correctly
- [ ] All tests passing (baseline maintained)
- [ ] No old directory structures remain (except domain/trading/)
- [ ] Documentation updated

**需要更新的文檔**:
- README.md (remove backward compatibility section, keep migration guide as history)
- PHASE1_COMPLETION_SUMMARY.md (add final completion status)

**複雜度 (Complexity)**: 3/10
**時間 (Time)**: 15 minutes

---

## 總結 (Summary)

### 任務統計 (Task Statistics)
- **總任務數**: 8 tasks
- **總時間**: 3-4 hours
- **複雜度範圍**: 2-5/10
- **平均複雜度**: 3.1/10

### 文件更新統計 (File Update Statistics)
- **Domain 層**: 9 files
- **測試**: 3 files
- **總計**: 12 files

### 目錄移除 (Directories to Remove)
- domain/models/
- domain/events/
- domain/strategies/
- domain/position/
- domain/risk/

### 成功標準 (Success Criteria)
- ✅ 所有測試通過 (All tests passing)
- ✅ 零導入錯誤 (Zero import errors)
- ✅ 舊結構完全移除 (Old structure completely removed)
- ✅ 僅保留 domain/trading/ (Only domain/trading/ remains)
- ✅ 功能完全不變 (Functionality unchanged)

---

## 執行順序 (Execution Order)

1. Task 1.1: ✅ DONE (Analysis complete)
2. Task 1.2: Update domain layer imports
3. Task 1.3: Update test imports
4. Task 1.4: Verify compilation
5. Task 1.5: Remove old directories
6. Task 1.6: Clean up re-exports
7. Task 1.7: Run test suite
8. Task 1.8: Final validation

**當前狀態 (Current Status)**: Ready to execute Tasks 1.2-1.8
