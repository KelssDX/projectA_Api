# Master Implementation Plan: Enterprise Audit Analytics Platform

> **Goal**: Transform ProjectA into a world-class audit analytics platform rivaling SAP, Oracle GRC, and enterprise audit tools.

---

## Project Status Dashboard

| Phase | Status | Progress |
|-------|--------|----------|
| Phase 1: Database Schema | ✅ Complete | 100% |
| Phase 2: Backend Models | ✅ Complete | 100% |
| Phase 3: Repository Layer | ✅ Complete | 100% |
| Phase 4: API Controllers | ✅ Complete | 100% |
| Phase 5: Audit Universe View | ✅ Complete | 100% |
| Phase 6: Analytics Widgets | ✅ Complete | 100% |
| Phase 7: Drill-Down Implementation | ✅ Complete | 100% |
| Phase 8: Heatmap Integration | ✅ Complete | 100% |
| Phase 9: Testing & Polish | � In Progress | 0% |

**Legend**: ✅ Complete | 🔄 In Progress | 🔲 Not Started | ⚠️ Blocked

---

## Implementation Progress Log

### Completed (2026-01-18)

**Phase 1: Database Schema**
- ✅ Created `Affine.Engine/SQL/AuditUniverse_Schema.sql`
- Tables: audit_universe, audit_findings, audit_recommendations, audit_coverage, risk_trend_history
- Lookup tables: ra_audit_universe_levels, ra_finding_severity, ra_finding_status, ra_recommendation_status
- Indexes, triggers, and seed data included

**Phase 2: Backend Models**
- ✅ `AuditUniverseNode.cs` - Hierarchy nodes with children support
- ✅ `AuditFinding.cs` - Findings with aging calculations
- ✅ `AuditRecommendation.cs` - Recommendations tracking
- ✅ `AuditCoverage.cs` - Coverage metrics and trend data
- ✅ `AuditUniverseRequests.cs` - Request/Response DTOs
- ✅ `DrillDownContext.cs` - Analytics drill-down support

**Phase 3: Repository Layer**
- ✅ `IAuditUniverseRepository.cs` / `AuditUniverseRepository.cs`
- ✅ `IAuditFindingsRepository.cs` / `AuditFindingsRepository.cs`
- Full CRUD, hierarchy traversal, department linking, analytics queries

**Phase 4: API Controllers**
- ✅ `AuditUniverseController.cs` - 12 endpoints for hierarchy management
- ✅ `AuditFindingsController.cs` - 15 endpoints for findings, recommendations, analytics
- ✅ Registered in DI container (Program.cs)

**Phase 5: Frontend - Audit Universe View**
- ✅ `audit_universe_view.py` - Full tree view with CRUD dialogs
- ✅ Added API methods to `auditing_client.py`
- ✅ Integrated into main.py navigation

**Phase 6: Analytics Widgets (Complete)**
- ✅ `findings_aging_widget.py` - Findings aging analysis
- ✅ `risk_trend_widget.py` - Risk trend visualization
- ✅ `audit_coverage_widget.py` - Audit coverage treemap
- ✅ `risk_velocity_widget.py` - Risk velocity gauge meter
- ✅ `department_comparison_widget.py` - Department risk comparison
- ✅ `control_effectiveness_widget.py` - Control effectiveness dashboard
- ✅ `heatmap_embed_widget.py` - Embedded heatmap for dashboard
- ✅ `compliance_scorecard_widget.py` - Compliance scorecard
- ✅ Updated `analytical_dashboard.py` with all widget imports and registry
- ✅ Added `BaseWidget` class to `base_widget.py`

**Phase 7: Drill-Down Implementation (Complete - 2026-01-27)**
- ✅ `drill_down_panel.py` - Panel for displaying drill-down details
- ✅ `breadcrumb_trail.py` - Navigation breadcrumbs for drill-down hierarchy
- ✅ `hierarchy_selector.py` - Dropdown and tree selector for filtering
- ✅ Created `views/components/` package with `__init__.py`

**Phase 8: Heatmap Integration (Complete - 2026-01-27)**
- ✅ Enhanced `heatmap_embed_widget.py` with hierarchy filter sync
- ✅ Added compact mode support for dashboard embedding
- ✅ Implemented cell click drill-down with context
- ✅ Added `set_hierarchy_filter()`, `set_compact_mode()`, `set_filters()` methods

---

### Updates (2026-01-27)
- FIXED: Analytical dashboard drill-down navigation now targets valid views and passes context filters.
- UPDATED: Assessment list now applies drill-down filters (reference, risk level, department) on entry.
- UPDATED: Added audit universe selector to analytics header and wired selection into widget filters.
- UPDATED: BaseWidget now supports vertical resize handle for embedded analytics widgets.
- UPDATED: Linked departments to audit universe nodes and seeded assessment department_ids so drill-down can resolve via hierarchy.
- FIXED: Hierarchy selector now handles AuditUniverse/GetHierarchy response shape (rootNodes).
- UPDATED: Operational Risk tab now uses assessment selector + standard table styling and shows data for selected reference.
- ðŸ”§ **FIXED**: Embedded heatmap widget now normalizes `heatmapGrid` API payloads into widget `cells/summary` so analytical report widgets render data correctly.

## Phase 1: Database Schema

### Tasks
- [ ] **1.1** Create `audit_universe` table (hierarchical structure)
- [ ] **1.2** Create `audit_universe_department_link` table
- [ ] **1.3** Create `audit_findings` table
- [ ] **1.4** Create `audit_recommendations` table
- [ ] **1.5** Create `audit_coverage` table
- [ ] **1.6** Create indexes for performance optimization
- [ ] **1.7** Insert seed data for testing

**Files to Create/Modify**:
- `Database/audit_universe_schema.sql`

---

## Phase 2: Backend Models (C#)

### Tasks
- [ ] **2.1** Create `AuditUniverseNode.cs` model
- [ ] **2.2** Create `AuditFinding.cs` model
- [ ] **2.3** Create `AuditRecommendation.cs` model
- [ ] **2.4** Create `AuditCoverage.cs` model
- [ ] **2.5** Create request/response DTOs
- [ ] **2.6** Create drill-down context models

**Files to Create**:
- `Affine.Engine/Model/Auditing/AuditUniverse/AuditUniverseNode.cs`
- `Affine.Engine/Model/Auditing/AuditUniverse/AuditFinding.cs`
- `Affine.Engine/Model/Auditing/AuditUniverse/AuditRecommendation.cs`
- `Affine.Engine/Model/Auditing/AuditUniverse/AuditCoverage.cs`
- `Affine.Engine/Model/Auditing/AuditUniverse/AuditUniverseRequests.cs`
- `Affine.Engine/Model/Auditing/Analytics/DrillDownContext.cs`

---

## Phase 3: Repository Layer

### Tasks
- [ ] **3.1** Create `IAuditUniverseRepository` interface
- [ ] **3.2** Implement `AuditUniverseRepository` class
  - [ ] `GetHierarchyAsync()` - Full tree structure
  - [ ] `GetNodeWithChildrenAsync(id)` - Node with children
  - [ ] `GetNodeAsync(id)` - Single node
  - [ ] `CreateNodeAsync(node)` - Create node
  - [ ] `UpdateNodeAsync(node)` - Update node
  - [ ] `DeleteNodeAsync(id)` - Delete node
  - [ ] `LinkDepartmentAsync(nodeId, deptId)` - Link department
  - [ ] `UnlinkDepartmentAsync(nodeId, deptId)` - Unlink department
  - [ ] `GetLinkedDepartmentsAsync(nodeId)` - Get linked departments
- [ ] **3.3** Create `IAuditFindingsRepository` interface
- [ ] **3.4** Implement `AuditFindingsRepository` class
- [ ] **3.5** Enhance `IRiskHeatMapRepository` with drill-down methods
- [ ] **3.6** Register repositories in DI container

**Files to Create/Modify**:
- `Affine.Engine/Repository/Auditing/IAuditUniverseRepository.cs`
- `Affine.Engine/Repository/Auditing/AuditUniverseRepository.cs`
- `Affine.Engine/Repository/Auditing/IAuditFindingsRepository.cs`
- `Affine.Engine/Repository/Auditing/AuditFindingsRepository.cs`
- `Affine.Auditing.API/Program.cs` (DI registration)

---

## Phase 4: API Controllers

### Tasks
- [ ] **4.1** Create `AuditUniverseController.cs` with endpoints:
  - [ ] `GET /api/v1/AuditUniverse/GetHierarchy`
  - [ ] `GET /api/v1/AuditUniverse/GetNode/{id}`
  - [ ] `POST /api/v1/AuditUniverse/CreateNode`
  - [ ] `PUT /api/v1/AuditUniverse/UpdateNode/{id}`
  - [ ] `DELETE /api/v1/AuditUniverse/DeleteNode/{id}`
  - [ ] `POST /api/v1/AuditUniverse/LinkDepartment`
  - [ ] `DELETE /api/v1/AuditUniverse/UnlinkDepartment`
  - [ ] `GET /api/v1/AuditUniverse/GetLinkedDepartments/{nodeId}`
- [ ] **4.2** Create `AuditFindingsController.cs` with endpoints:
  - [ ] `GET /api/v1/AuditFindings/GetAll`
  - [ ] `GET /api/v1/AuditFindings/GetByReference/{referenceId}`
  - [ ] `GET /api/v1/AuditFindings/GetAging`
  - [ ] `POST /api/v1/AuditFindings/Create`
  - [ ] `PUT /api/v1/AuditFindings/Update/{id}`
- [ ] **4.3** Enhance `RiskGraphsController.cs`:
  - [ ] `GET /api/v1/RiskGraphs/GetDrillDown`
  - [ ] `GET /api/v1/RiskGraphs/GetFindingsAging`
  - [ ] `GET /api/v1/RiskGraphs/GetAuditCoverageMap`
  - [ ] `GET /api/v1/RiskGraphs/GetRiskTrend`
  - [ ] `GET /api/v1/RiskGraphs/GetRiskVelocity`

**Files to Create/Modify**:
- `Affine.Auditing.API/Controllers/AuditUniverseController.cs`
- `Affine.Auditing.API/Controllers/AuditFindingsController.cs`
- `Affine.Auditing.API/Controllers/RiskGraphsController.cs`

---

## Phase 5: Frontend - Audit Universe View

### Tasks
- [ ] **5.1** Create `audit_universe_view.py` - Main hierarchy management view
- [ ] **5.2** Create tree view component for hierarchy visualization
- [ ] **5.3** Create node detail panel (view/edit selected node)
- [ ] **5.4** Create node CRUD dialogs (Add/Edit/Delete)
- [ ] **5.5** Implement department linking functionality
- [ ] **5.6** Add search/filter capabilities
- [ ] **5.7** Create `audit_universe_controller.py` for API integration
- [ ] **5.8** Add navigation menu entry in `main.py`

**Files to Create/Modify**:
- `RiskAssessmentApp_Frontend/src/views/audit_universe/audit_universe_view.py`
- `RiskAssessmentApp_Frontend/src/views/audit_universe/__init__.py`
- `RiskAssessmentApp_Frontend/src/controllers/audit_universe_controller.py`
- `RiskAssessmentApp_Frontend/src/main.py`

---

## Phase 6: Analytics Widgets (8 New Widgets) ✅ COMPLETE

### Tasks
- [x] **6.1** Create `findings_aging_widget.py` - Open Findings Aging Analysis
- [x] **6.2** Create `audit_coverage_widget.py` - Audit Coverage Map (treemap)
- [x] **6.3** Create `risk_trend_widget.py` - Risk Trend Analysis (multi-line chart)
- [x] **6.4** Create `risk_velocity_widget.py` - Risk Velocity Meter (gauge)
- [x] **6.5** Create `department_comparison_widget.py` - Department Risk Comparison
- [x] **6.6** Create `control_effectiveness_widget.py` - Control Effectiveness Dashboard
- [x] **6.7** Create `heatmap_embed_widget.py` - Embedded Heatmap Widget
- [x] **6.8** Create `compliance_scorecard_widget.py` - Compliance Scorecard
- [x] **6.9** Update widget registry in `analytical_dashboard.py`

**Files Created/Modified**:
- ✅ `RiskAssessmentApp_Frontend/src/views/widgets/findings_aging_widget.py`
- ✅ `RiskAssessmentApp_Frontend/src/views/widgets/audit_coverage_widget.py`
- ✅ `RiskAssessmentApp_Frontend/src/views/widgets/risk_trend_widget.py`
- ✅ `RiskAssessmentApp_Frontend/src/views/widgets/risk_velocity_widget.py`
- ✅ `RiskAssessmentApp_Frontend/src/views/widgets/department_comparison_widget.py`
- ✅ `RiskAssessmentApp_Frontend/src/views/widgets/control_effectiveness_widget.py`
- ✅ `RiskAssessmentApp_Frontend/src/views/widgets/heatmap_embed_widget.py`
- ✅ `RiskAssessmentApp_Frontend/src/views/widgets/compliance_scorecard_widget.py`
- ✅ `RiskAssessmentApp_Frontend/src/views/analytics/analytical_dashboard.py`
- ✅ `RiskAssessmentApp_Frontend/src/views/widgets/base_widget.py` (Added BaseWidget class)

---

## Phase 7: Drill-Down Implementation ✅ COMPLETE

### Tasks
- [x] **7.1** Create `DrillDownPanel` component for detail views
- [x] **7.2** Implement drill-down navigation in each widget
- [x] **7.3** Add breadcrumb trail component
- [x] **7.4** Create hierarchy selector dropdown for dashboard filtering
- [x] **7.5** Implement data caching for drill-down performance

**Files Created**:
- ✅ `RiskAssessmentApp_Frontend/src/views/components/drill_down_panel.py`
- ✅ `RiskAssessmentApp_Frontend/src/views/components/breadcrumb_trail.py`
- ✅ `RiskAssessmentApp_Frontend/src/views/components/hierarchy_selector.py`
- ✅ `RiskAssessmentApp_Frontend/src/views/components/__init__.py`

---

## Phase 8: Heatmap Integration ✅ COMPLETE

### Tasks
- [x] **8.1** Refactor existing heatmap into reusable component
- [x] **8.2** Create `heatmap_embed_widget.py` wrapper for dashboard
- [x] **8.3** Implement cell click drill-down
- [x] **8.4** Sync heatmap with hierarchy filter
- [x] **8.5** Add compact mode for dashboard view

**Files Modified**:
- ✅ `RiskAssessmentApp_Frontend/src/views/widgets/heatmap_embed_widget.py`
  - Added `audit_universe_id` parameter for hierarchy filtering
  - Added `compact_mode` parameter and dynamic cell sizing
  - Added `set_hierarchy_filter()`, `set_compact_mode()`, `set_filters()` methods
  - Updated API call to include hierarchy filter
- ✅ `RiskAssessmentApp_Frontend/src/views/dashboard/heatmap.py` (existing)

---

## Phase 9: Testing & Polish 🔄 IN PROGRESS

### Tasks
- [ ] **9.1** Backend unit tests for repositories
- [ ] **9.2** Backend integration tests for controllers
- [x] **9.3** Frontend syntax verification ✅
- [ ] **9.4** Performance optimization (< 3s dashboard load)
- [ ] **9.5** UI/UX polish and responsive design
- [ ] **9.6** Documentation update

**Progress (2026-01-27)**:
- ✅ All new widget files pass Python syntax check
- ✅ All component files pass Python syntax check
- ✅ analytical_dashboard.py compiles successfully
- ✅ base_widget.py compiles successfully
- 🔧 **FIXED**: Dashboard widget instantiation bug (incorrect arguments for new widgets)
- 🔧 **FIXED**: Missing DrillDownPanel integration in dashboard
- 🔧 **FIXED**: `ImportError` by removing `transform` import and using `ft.Offset` in dashboard
- 🔧 **FIXED**: `Tooltip` error in `BaseWidget` (switched to `ft.Icon(tooltip=...)`)
- 🔧 **FIXED**: Constructor signature mismatches in 3 widgets
- 🔧 **FIXED**: `MarketRiskWidget` numeric argument error
- 🔧 **FIXED**: `RiskVelocityWidget` NoneType error
- 🔧 **FIXED**: `AuditingAPIClient` missing `get_heatmap_data` method
- 🔧 **UPDATED**: Enabled Heatmap and Audit Coverage widgets by default




---

## Existing Features (Already Complete)

### Backend API ✅
- Risk Assessment CRUD (40+ endpoints)
- Heatmap generation
- Basic analytical report endpoint
- Department/Project management
- User management
- Workflow integration (Elsa v3)

### Frontend ✅
- Modern 5-step assessment form
- Assessment list/detail views
- Basic heatmap view
- Department/Project/User management
- 5 basic widgets (Market Risk, Inherent vs Residual, Top Risks, Category Distribution, Control Coverage)

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (Python/Flet)                       │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────┐  │
│  │ Audit        │  │ Analytics    │  │ Risk Assessment       │  │
│  │ Universe     │  │ Dashboard    │  │ Management            │  │
│  │ Management   │  │ (13 Widgets) │  │                       │  │
│  └──────────────┘  └──────────────┘  └───────────────────────┘  │
│                           │                                      │
│              ┌────────────┴────────────┐                        │
│              │   API Client Layer      │                        │
│              └────────────┬────────────┘                        │
└───────────────────────────┼─────────────────────────────────────┘
                            │ REST API
┌───────────────────────────┼─────────────────────────────────────┐
│                    BACKEND (.NET 8)                              │
├───────────────────────────┼─────────────────────────────────────┤
│  ┌────────────────────────┴────────────────────────────────┐    │
│  │                    API Controllers                       │    │
│  │  • RiskAssessmentController  • AuditUniverseController   │    │
│  │  • RiskGraphsController      • AuditFindingsController   │    │
│  └────────────────────────┬────────────────────────────────┘    │
│                           │                                      │
│  ┌────────────────────────┴────────────────────────────────┐    │
│  │                  Repository Layer                        │    │
│  │  • RiskAssessmentRepository  • AuditUniverseRepository   │    │
│  │  • RiskHeatMapRepository     • AuditFindingsRepository   │    │
│  └────────────────────────┬────────────────────────────────┘    │
└───────────────────────────┼─────────────────────────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────────┐
│                     PostgreSQL                                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ Risk Assessment │  │ Audit Universe  │  │ Audit Findings  │  │
│  │ Tables          │  │ Hierarchy       │  │ & Coverage      │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Quick Start Commands

```bash
# Backend
cd Affine.Auditing.API
dotnet run

# Frontend
cd RiskAssessmentApp_Frontend
python -m src.main

# Database Migration
psql -U postgres -d riskassessment -f Database/audit_universe_schema.sql
```

---

## Success Criteria

- [ ] Users can manage a 4+ level audit universe hierarchy
- [ ] All charts support drill-down to lower levels
- [ ] Heatmap is embedded in analytical dashboard
- [ ] 8 new analytical widgets available
- [ ] Audit coverage and findings aging visible
- [ ] Performance: Dashboard loads in < 3 seconds
- [ ] Responsive design works on 1080p+ screens

---

*Last Updated: 2026-01-27*
*Version: 1.7*

