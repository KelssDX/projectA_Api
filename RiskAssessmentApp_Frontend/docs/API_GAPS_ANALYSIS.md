# API Gaps Analysis: Frontend vs Backend

This document identifies the features that the frontend expects but are **missing** from the current backend APIs (`RiskGraphsController.cs` and `RiskAssessmentController.cs`).

## 🔍 **Current Backend API Coverage**

### ✅ **RiskGraphsController.cs**
- `GET /api/v1/RiskGraphs/GetHeatmap?referenceId={id}` - Risk heatmap for specific reference

### ✅ **RiskAssessmentController.cs**
- `GET /api/v1/RiskAssessment/GetRiskAssessment?referenceId={id}` - Get specific assessment
- `POST /api/v1/RiskAssessment/CreateRiskAssessment` - Create assessment
- `PUT /api/v1/RiskAssessment/UpdateRiskAssessment/{id}` - Update assessment
- `POST /api/v1/RiskAssessment/CreateReference` - Create reference
- `POST /api/v1/RiskAssessment/StartControlTesting/{id}` - Start control testing
- **Lookup endpoints**: GetRisks, GetControls, GetOutcomes, GetRiskLikelihoods, GetImpacts, etc.

---

## ❌ **MISSING Backend APIs** (Frontend Falls Back to Database)

### 1. **Department Management APIs**
**Frontend needs:** Full CRUD operations for departments

**📁 Frontend Files:**
- **Main View**: `views/departments_view.py` *(731 lines - complete department management UI)*
- **Controller**: Uses direct DB connections *(no controller file - direct SQL queries)*
- **Navigation**: `main.py` line 44 *(departments menu item)*

```csharp
// Missing endpoints that should be added to RiskAssessmentController or new DepartmentController:
GET    /api/v1/Departments                     // List all departments
POST   /api/v1/Departments                     // Create department  
GET    /api/v1/Departments/{id}                // Get specific department
PUT    /api/v1/Departments/{id}                // Update department
DELETE /api/v1/Departments/{id}                // Delete department
```

**Frontend usage:**
- Department management view with CRUD operations
- Risk level tracking per department
- Department head assignment
- Assessment counting per department

**📍 Key Code Locations:**
- **Database queries**: `views/departments_view.py` lines 24-37 *(load_departments method)*
- **CRUD operations**: `views/departments_view.py` lines 264-310 *(add department)*
- **Edit functionality**: `views/departments_view.py` lines 371-427 *(edit department)*
- **Delete functionality**: `views/departments_view.py` lines 443-485 *(delete department)*

### 2. **Project Management APIs**
**Frontend needs:** Full project portfolio management

**📁 Frontend Files:**
- **Main View**: `views/projects_view.py` *(1246 lines - complete project management UI)*
- **Controller**: Uses direct DB connections *(no controller file - direct SQL queries)*
- **Navigation**: `main.py` line 46 *(projects menu item)*

```csharp
// Missing endpoints that should be added:
GET    /api/v1/Projects                        // List all projects
POST   /api/v1/Projects                        // Create project
GET    /api/v1/Projects/{id}                   // Get specific project
PUT    /api/v1/Projects/{id}                   // Update project
DELETE /api/v1/Projects/{id}                   // Delete project
GET    /api/v1/Projects/ByDepartment/{deptId}  // Projects by department
```

**Frontend usage:**
- Project management view with full CRUD
- Project status tracking (Not Started, In Progress, Completed, On Hold)
- Budget management
- Project timelines (start/end dates)
- Risk level per project
- Department assignment

**📍 Key Code Locations:**
- **Database queries**: `views/projects_view.py` lines 15-49 *(load_projects method)*
- **Add project**: `views/projects_view.py` lines 393-434 *(show_add_project_dialog)*
- **Edit project**: `views/projects_view.py` lines 667-766 *(edit_project method)*
- **Delete project**: `views/projects_view.py` lines 944-980 *(delete_project method)*
- **Department integration**: `views/projects_view.py` lines 356-370 *(get_departments method)*

### 3. **User Management APIs**
**Frontend needs:** Complete user administration

**📁 Frontend Files:**
- **Main View**: `views/user_management.py` *(881 lines - complete user administration UI)*
- **Controller**: `controllers/user_controller.py` *(429 lines - falls back to database)*
- **Navigation**: `main.py` line 48 *(users menu item)*

```csharp
// Missing endpoints (Identity API only has Login):
GET    /api/v1/Users                           // List all users
POST   /api/v1/Users                           // Create user
GET    /api/v1/Users/{id}                      // Get specific user
PUT    /api/v1/Users/{id}                      // Update user
DELETE /api/v1/Users/{id}                      // Delete user
PUT    /api/v1/Users/{id}/Password             // Change password
GET    /api/v1/Users/ByRole/{role}             // Users by role
GET    /api/v1/Users/ByDepartment/{deptId}     // Users by department
```

**Frontend usage:**
- User management view with CRUD operations
- Role assignment (admin, auditor, user)
- Department assignment
- User profile management
- Password management

**📍 Key Code Locations:**
- **User listing**: `controllers/user_controller.py` lines 44-104 *(get_users method with database fallback)*
- **User creation**: `controllers/user_controller.py` lines 140-200 *(create_user method)*
- **User updates**: `controllers/user_controller.py` lines 226-320 *(update_user method)*
- **User deletion**: `controllers/user_controller.py` lines 342-390 *(delete_user method)*
- **UI implementation**: `views/user_management.py` *(complete user management interface)*

### 4. **Assessment List/Search APIs**
**Frontend needs:** General assessment listing and management

**📁 Frontend Files:**
- **Controller**: `controllers/assessment_controller.py` *(447 lines - partially uses API, falls back to DB)*
- **Main View**: `views/assessment/list.py` *(assessment listing view)*
- **Navigation**: `main.py` line 42 *(assessments menu item)*

```csharp
// Missing endpoints in RiskAssessmentController:
GET    /api/v1/RiskAssessment/Assessments      // List all assessments
GET    /api/v1/RiskAssessment/Assessments/Search?q={query} // Search assessments
GET    /api/v1/RiskAssessment/ByDepartment/{deptId}        // Assessments by department
GET    /api/v1/RiskAssessment/ByProject/{projectId}        // Assessments by project
GET    /api/v1/RiskAssessment/ByAuditor/{userId}           // Assessments by auditor
DELETE /api/v1/RiskAssessment/{referenceId}                // Delete assessment
```

**Frontend usage:**
- Assessment listing view with filtering
- Search functionality
- Assessment management
- Assessment deletion

**📍 Key Code Locations:**
- **Assessment listing**: `controllers/assessment_controller.py` lines 230-315 *(get_assessments with database fallback)*
- **Search/filtering**: `controllers/assessment_controller.py` lines 250-290 *(filter building logic)*
- **Assessment deletion**: `controllers/assessment_controller.py` lines 565-610 *(delete_assessment method)*
- **Legacy support**: `controllers/assessment_controller.py` lines 340-430 *(get_assessment by ID)*

### 5. **Dashboard/Statistics APIs**
**Frontend needs:** Dashboard metrics and visualizations

**📁 Frontend Files:**
- **Main View**: `views/dashboard.py` *(420 lines - dashboard with hardcoded statistics)*
- **Main App**: `main.py` lines 248-400 *(dashboard initialization with hardcoded data)*
- **Navigation**: `main.py` line 40 *(dashboard menu item)*

```csharp
// Missing endpoints for dashboard data:
GET    /api/v1/Dashboard/Statistics            // Overall statistics
GET    /api/v1/Dashboard/RiskByDepartment      // Risk distribution by department
GET    /api/v1/Dashboard/AssessmentTrends      // Assessment trends over time
GET    /api/v1/Dashboard/HighRiskAreas         // High risk areas summary
GET    /api/v1/Dashboard/RecentActivity        // Recent assessment activity
```

**Frontend usage:**
- Dashboard statistics (active assessments, high risk areas, completed assessments)
- Risk distribution charts by department
- Trend analysis
- Real-time metrics

**📍 Key Code Locations:**
- **Hardcoded statistics**: `main.py` lines 260-285 *(dashboard cards with static numbers)*
- **Risk distribution charts**: `main.py` lines 295-395 *(department risk visualization)*
- **Export functionality**: `main.py` lines 849-875 *(export options)*
- **Dashboard view**: `views/dashboard.py` *(complete dashboard implementation)*

### 6. **Enhanced Visualization APIs**
**Frontend needs:** More comprehensive reporting data

**📁 Frontend Files:**
- **Heatmap View**: `views/heatmap.py` *(430 lines - risk heatmap visualization)*
- **Controller Integration**: `controllers/assessment_controller.py` lines 115-135 *(get_heatmap_data method)*

```csharp
// Additional missing endpoints in RiskGraphsController:
GET    /api/v1/RiskGraphs/TrendAnalysis/{referenceId}     // Risk trends over time
GET    /api/v1/RiskGraphs/DepartmentComparison           // Risk comparison across departments
GET    /api/v1/RiskGraphs/ControlEffectiveness           // Control effectiveness metrics
GET    /api/v1/RiskGraphs/RiskMatrix                     // Overall risk matrix
```

**Frontend usage:**
- Advanced risk visualizations
- Comparative analysis
- Trend reporting
- Risk matrix displays

**📍 Key Code Locations:**
- **Heatmap visualization**: `views/heatmap.py` *(complete heatmap implementation)*
- **API integration**: `controllers/assessment_controller.py` lines 115-135 *(heatmap data fetching)*

---

## 🔧 **Immediate Impact**

### **Current Frontend Behavior:**
1. **Authentication** → Uses Identity API ✅ *(`controllers/auth_controller.py` lines 35-65)*
2. **Risk Assessment Operations** → Uses Auditing API ✅ *(`controllers/assessment_controller.py` lines 25-115)*
3. **Departments Management** → **Falls back to direct database queries** ❌ *(`views/departments_view.py` lines 24-37)*
4. **Projects Management** → **Falls back to direct database queries** ❌ *(`views/projects_view.py` lines 15-49)*
5. **User Management** → **Falls back to direct database queries** ❌ *(`controllers/user_controller.py` lines 44-104)*
6. **Dashboard Statistics** → **Uses hardcoded/calculated data** ❌ *(`main.py` lines 260-285)*
7. **Assessment Listing** → **Falls back to direct database queries** ❌ *(`controllers/assessment_controller.py` lines 230-315)*

### **Problems This Causes:**
- **Inconsistent data access patterns** (some via API, some via database)
- **Security concerns** (frontend directly accessing database)
- **Scalability issues** (bypassing API layer)
- **Data consistency risks** (no centralized business logic)
- **Difficult deployment** (frontend needs database access)

---

## 📋 **Quick Navigation Guide**

### **🔍 To See Missing Department API Usage:**
```bash
# Main department management file
RiskAssessmentApp_Frontend/views/departments_view.py

# Lines to focus on:
# 24-37:   load_departments() - direct DB queries
# 264-310: show_add_department_dialog() - create functionality  
# 371-427: edit_department() - update functionality
# 443-485: delete_department() - delete functionality
```

### **🔍 To See Missing Project API Usage:**
```bash
# Main project management file  
RiskAssessmentApp_Frontend/views/projects_view.py

# Lines to focus on:
# 15-49:   load_projects() - direct DB queries
# 393-434: show_add_project_dialog() - create functionality
# 667-766: edit_project() - update functionality  
# 944-980: delete_project() - delete functionality
```

### **🔍 To See Missing User API Usage:**
```bash
# User controller with database fallbacks
RiskAssessmentApp_Frontend/controllers/user_controller.py

# Lines to focus on:
# 44-104:  get_users() - list users with DB fallback
# 140-200: create_user() - create with DB fallback
# 226-320: update_user() - update with DB fallback
# 342-390: delete_user() - delete with DB fallback
```

### **🔍 To See Dashboard Data Needs:**
```bash
# Main app with hardcoded dashboard data
RiskAssessmentApp_Frontend/main.py

# Lines to focus on:
# 260-285: Hardcoded statistics cards
# 295-395: Risk distribution visualization
# 849-875: Export functionality

# Dashboard view implementation
RiskAssessmentApp_Frontend/views/dashboard.py
```

---

## 📋 **Recommended Solutions**

### **Option 1: Extend Existing Controllers**
Add missing endpoints to `RiskAssessmentController.cs`:
```csharp
// Add to RiskAssessmentController.cs
[Route("Departments")]
public async Task<IActionResult> GetDepartments() { ... }

[Route("Projects")]  
public async Task<IActionResult> GetProjects() { ... }

[Route("Assessments")]
public async Task<IActionResult> GetAllAssessments() { ... }
```

### **Option 2: Create New Controllers** (Recommended)
```csharp
// New controllers needed:
- DepartmentController.cs  (department CRUD)
- ProjectController.cs     (project management)  
- UserController.cs        (user management - extend Identity API)
- DashboardController.cs   (statistics and metrics)
- ReportingController.cs   (advanced reporting)
```

### **Option 3: Hybrid Approach**
- Keep existing controllers for core risk assessment functionality
- Add specific controllers for missing features
- Extend RiskGraphsController for additional visualizations

---

## 🎯 **Priority Recommendations**

### **High Priority** (Critical for frontend functionality)
1. **Department Management API** - Required for `views/departments_view.py`
2. **Assessment Listing API** - Required for assessment management in `controllers/assessment_controller.py`
3. **Dashboard Statistics API** - Required for `views/dashboard.py` and `main.py` dashboard

### **Medium Priority** (Important for complete functionality)  
4. **Project Management API** - Required for `views/projects_view.py`
5. **User Management API** - Required for `controllers/user_controller.py` and `views/user_management.py`
6. **Assessment Delete API** - Required for assessment lifecycle in `controllers/assessment_controller.py`

### **Low Priority** (Nice to have)
7. **Advanced Visualization APIs** - Enhanced reporting in `views/heatmap.py`
8. **Trend Analysis APIs** - Advanced analytics

---

## 💡 **Quick Wins**

Some endpoints can be implemented quickly by leveraging existing repository patterns:

1. **Assessment Listing** - Extend existing `IRiskAssessmentRepository`
2. **Department CRUD** - Should already exist in the engine layer
3. **Basic Statistics** - Aggregate queries on existing data

The frontend architecture is already prepared for these APIs - it just needs the backend endpoints to be implemented! 