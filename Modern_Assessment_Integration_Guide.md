# Modern Assessment Components - Integration Guide

## 🚀 **Quick Start**

### **1. Using the Modern Assessment Form**

Replace your existing assessment form with the new modern wizard:

```python
from views.assessment.modern_form import ModernAssessmentForm

# In your main application
def show_new_assessment(page, user):
    form = ModernAssessmentForm(
        page=page,
        user=user,
        assessment_data=None,  # For new assessment
        reference_id=None,     # Will create new reference
        on_save=handle_assessment_saved,
        on_cancel=handle_form_cancelled
    )
    
    page.views.append(ft.View("/assessment/new", [form]))
    page.update()

def handle_assessment_saved(result):
    print(f"Assessment saved with result: {result}")
    # Navigate back to assessment list or show success

def handle_form_cancelled():
    print("Form cancelled by user")
    # Navigate back to previous view
```

### **2. Using the Modern Assessment Details**

Replace your existing details view with the enhanced version:

```python
from views.assessment.modern_details import ModernAssessmentDetails

def show_assessment_details(page, user, reference_id):
    details = ModernAssessmentDetails(
        page=page,
        user=user,
        reference_id=reference_id,
        on_back=handle_back_to_list,
        on_edit=handle_edit_assessment
    )
    
    page.views.append(ft.View(f"/assessment/{reference_id}", [details]))
    page.update()

def handle_back_to_list():
    # Navigate back to assessment list
    page.go("/assessments")

def handle_edit_assessment(reference_id):
    # Navigate to edit form
    show_edit_assessment(page, user, reference_id)
```

### **3. Editing Existing Assessments**

```python
def show_edit_assessment(page, user, reference_id):
    # Load existing assessment data first
    assessment_data = load_assessment_data(reference_id)
    
    form = ModernAssessmentForm(
        page=page,
        user=user,
        assessment_data=assessment_data,  # Pre-populate form
        reference_id=reference_id,        # Update existing
        on_save=handle_assessment_updated,
        on_cancel=handle_edit_cancelled
    )
    
    page.views.append(ft.View(f"/assessment/{reference_id}/edit", [form]))
    page.update()
```

## 🔧 **Configuration**

### **1. API Integration Setup**

Ensure your `AssessmentController` is properly configured:

```python
# In controllers/assessment_controller.py
class AssessmentController:
    def __init__(self):
        self.auditing_client = AuditingAPIClient()
        
    # Make sure all required methods are implemented:
    # - get_risk_assessment(reference_id)
    # - create_risk_assessment(assessment_data)
    # - update_risk_assessment(reference_id, update_data)
    # - start_control_testing(reference_id, testing_data)
    # - get_risks(), get_controls(), get_outcomes(), etc.
    # - get_heatmap_data(reference_id)
```

### **2. User Object Requirements**

The modern components expect a user object with these properties:

```python
class User:
    def __init__(self):
        self.id = "user_id"
        self.name = "User Name"
        self.email = "user@example.com"
        self.role = "Auditor"
        self.department = "IT Audit"
```

## 📋 **Navigation Integration**

### **1. Main Assessment List Integration**

```python
def create_assessment_list_view(page, user):
    # Your existing assessment list
    list_view = AssessmentListView(page, user)
    
    # Add modern form navigation
    def show_new_modern_assessment():
        form = ModernAssessmentForm(
            page, user, 
            on_save=lambda result: page.go("/assessments"),
            on_cancel=lambda: page.go("/assessments")
        )
        page.views.append(ft.View("/assessment/new", [form]))
        page.update()
    
    # Add button to list view
    new_button = ft.ElevatedButton(
        text="New Assessment (Modern)",
        icon=ft.icons.ADD,
        bgcolor="#2ecc71",
        color="white",
        on_click=lambda e: show_new_modern_assessment()
    )
    
    return list_view
```

### **2. Route Handling**

```python
def route_change(route):
    page.views.clear()
    
    if page.route == "/assessments":
        page.views.append(ft.View("/assessments", [create_assessment_list()]))
    
    elif page.route == "/assessment/new":
        form = ModernAssessmentForm(page, user, 
                                   on_save=lambda r: page.go("/assessments"),
                                   on_cancel=lambda: page.go("/assessments"))
        page.views.append(ft.View("/assessment/new", [form]))
    
    elif page.route.startswith("/assessment/") and page.route.endswith("/edit"):
        reference_id = extract_reference_id(page.route)
        form = ModernAssessmentForm(page, user, reference_id=reference_id,
                                   on_save=lambda r: page.go(f"/assessment/{reference_id}"),
                                   on_cancel=lambda: page.go(f"/assessment/{reference_id}"))
        page.views.append(ft.View(page.route, [form]))
    
    elif page.route.startswith("/assessment/"):
        reference_id = extract_reference_id(page.route)
        details = ModernAssessmentDetails(page, user, reference_id=reference_id,
                                         on_back=lambda: page.go("/assessments"),
                                         on_edit=lambda rid: page.go(f"/assessment/{rid}/edit"))
        page.views.append(ft.View(page.route, [details]))
    
    page.update()
```

## ⚙️ **Customization Options**

### **1. Styling Customization**

```python
# Override colors in the modern components
class CustomModernForm(ModernAssessmentForm):
    def _get_risk_color(self, risk_level):
        # Custom color scheme
        colors = {
            "Critical": "#8B0000",  # Dark red
            "High": "#DC143C",      # Crimson
            "Medium": "#FF8C00",    # Dark orange
            "Low": "#32CD32",       # Lime green
            "Very Low": "#228B22"   # Forest green
        }
        return colors.get(risk_level, "#95a5a6")
```

### **2. Step Customization**

```python
class CustomAssessmentForm(ModernAssessmentForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize the number of steps or step names
        self.total_steps = 4  # Reduce to 4 steps
    
    def _build_step_content(self):
        # Override to customize step content
        if self.current_step == 0:
            return self._build_basic_info_step()
        elif self.current_step == 1:
            return self._build_combined_risk_controls_step()
        # ... etc
```

## 🔍 **Troubleshooting**

### **Common Issues**

#### **1. API Connection Errors**
```python
# Check if backend APIs are running
# Verify API_CONFIG in config.py
# Check network connectivity

# Add debugging to form initialization
async def _load_lookup_data(self):
    try:
        print("Loading lookup data...")
        tasks = [...]  # Your API calls
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"API call {i} failed: {result}")
        
    except Exception as e:
        print(f"Error loading lookup data: {e}")
```

#### **2. Form Not Updating**
```python
# Ensure page.update() is called after state changes
def _refresh_ui(self):
    self.step_indicator.content = self._build_step_indicator().content
    self.content_container.content = self._build_step_content()
    if hasattr(self, 'page') and self.page:
        self.page.update()  # Important!
```

#### **3. Missing User Properties**
```python
# Ensure user object has required properties
if not hasattr(user, 'name') or not user.name:
    user.name = "Unknown User"
if not hasattr(user, 'id') or not user.id:
    user.id = "1"
```

## 📊 **Performance Optimization**

### **1. Lazy Loading**
```python
# Load lookup data only when needed
async def _load_lookup_data_lazy(self, data_type):
    if data_type not in self.lookup_data:
        if data_type == 'risks':
            self.lookup_data['risks'] = await self.assessment_controller.get_risks()
        # ... etc
```

### **2. Caching**
```python
# Cache lookup data across form instances
class LookupDataCache:
    _cache = {}
    _cache_time = {}
    
    @classmethod
    async def get_cached_data(cls, data_type, loader_func):
        if data_type in cls._cache:
            return cls._cache[data_type]
        
        data = await loader_func()
        cls._cache[data_type] = data
        return data
```

## 🎯 **Best Practices**

1. **Always handle exceptions** in async methods
2. **Provide user feedback** for long-running operations
3. **Validate form data** before submission
4. **Use proper navigation patterns** with callbacks
5. **Test with real API data** during development
6. **Implement proper cleanup** in component destructors

## 📝 **Migration Checklist**

- [ ] Update imports to use modern components
- [ ] Ensure AssessmentController has all required methods
- [ ] Configure proper user object structure
- [ ] Update navigation/routing logic
- [ ] Test form submission and editing flows
- [ ] Verify heatmap integration works
- [ ] Test export functionality
- [ ] Validate control testing workflow
- [ ] Check error handling and user feedback
- [ ] Perform UI/UX testing on different screen sizes

## 🎉 **Success!**

Your application now has a modern, professional risk assessment system that provides:
- ✅ **Enterprise-grade UI/UX**
- ✅ **Full API integration**
- ✅ **Professional auditing workflows**
- ✅ **Team collaboration features**
- ✅ **Advanced reporting capabilities**

The modern assessment system is ready for production use in professional auditing environments! 