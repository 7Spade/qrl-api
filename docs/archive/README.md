# Archive Directory

This directory contains historical documentation, analysis reports, and obsolete files that are no longer actively used but preserved for reference.

## Directory Structure

### `/legacy-api/`
**Purpose:** Historical MEXC API v3 documentation and implementation notes

**Contents:**
- MEXC v3 API documentation (account, market, wallet, WebSocket)
- API balance fix documentation
- Legacy WebSocket implementation guides

**Status:** Superseded by current implementation in `src/`

**Retention:** Kept for historical reference and migration context

---

### `/optimization-reports/`
**Purpose:** Historical code analysis and optimization reports from initial development phases

**Contents:**
- **PHASE2_MODULE_ANALYSIS_REPORT.md** - Initial module structure analysis
- **PHASE3_COUPLING_ANALYSIS_REPORT.md** - Code coupling analysis
- **PHASE4_DEAD_CODE_ANALYSIS_REPORT.md** - Dead code identification
- **PHASE5_DUPLICATION_ANALYSIS_REPORT.md** - Code duplication analysis
- **REFACTORING_ROADMAP.md** - Obsolete refactoring plans (completed)
- **DOCUMENTATION_CLEANUP_PLAN.md** - Documentation cleanup plan (executed)
- **CONTAINER_STARTUP_FIX.md** - Container startup debugging notes
- **documentation_analysis.md** - Documentation structure analysis
- **srp_violations.md** - Single Responsibility Principle violations report

**Status:** Analysis completed, recommendations implemented or superseded

**Retention:** Kept for historical context and audit trail

---

### `/optimization-scripts/`
**Purpose:** Python scripts used for automated code analysis during optimization phases

**Contents:**
- `analyze_coupling.py` - Coupling analysis script
- `analyze_dead_code.py` - Dead code detection script
- `analyze_documentation.py` - Documentation analysis script
- `analyze_duplication.py` - Code duplication detection script
- `analyze_modules.py` - Module structure analysis script
- `analyze_srp.py` - SRP violation detection script

**Status:** Analysis tools no longer actively maintained

**Retention:** Kept for reproducibility and future reference if similar analysis needed

---

### `/optimization-data/`
**Purpose:** Raw JSON output from optimization analysis scripts

**Contents:**
- `coupling_analysis.json` - Coupling metrics and relationships
- `dead_code_analysis.json` - Dead code detection results
- `documentation_analysis.json` - Documentation coverage data
- `duplication_analysis.json` - Code duplication metrics
- `module_inventory.json` - Complete module structure inventory
- `srp_violations.json` - SRP violation details

**Status:** Historical data from completed analysis phases

**Retention:** Kept for audit trail and reproducibility

---

### Root Files

#### `production_success_plan.txt`
**Purpose:** Early production deployment planning notes

**Status:** Obsolete - replaced by structured deployment guides in `docs/03-Deployment.md`

**Retention:** Historical reference only

---

## Current Active Documentation

For current, actively maintained documentation, see:

### Core Guides
- `docs/01-Quickstart-and-Map.md` - Quick start guide
- `docs/02-System-Overview.md` - System architecture overview
- `docs/03-Deployment.md` - Deployment procedures
- `docs/04-Operations-and-Tasks.md` - Operations and task management
- `docs/05-Strategies-and-Data.md` - Trading strategies and data
- `docs/06-API-Compliance-and-Accounts.md` - API compliance

### Architecture Documentation
- `docs/ADR-001-*.md` - Architecture Decision Records
- `docs/ARCHITECTURE_RULES.md` - Architecture principles
- `docs/ARCHITECTURE_TREE.md` - System structure

### Implementation Guides
- `docs/IMPLEMENTATION-COMPLETE.md` - Implementation status
- `docs/MIGRATION-REMOVED-ENDPOINTS.md` - Migration guide
- `docs/CLOUD-RUN-COST-OPTIMIZATION.md` - Cost optimization
- `docs/TASKS-ENDPOINTS-REFERENCE.md` - Tasks API reference

---

## Archive Management Policy

**What Gets Archived:**
- Completed analysis reports
- Obsolete planning documents
- Legacy API documentation
- Historical implementation notes
- Superseded guides and procedures

**What Stays Active:**
- Current system documentation
- Active ADRs and architecture guides
- Current implementation references
- API documentation for active endpoints

**Retention Period:**
- All archived files: Indefinite (for historical reference)
- Review annually to determine if any files can be permanently removed

---

**Last Updated:** 2026-01-01
**Maintained By:** Development Team
