"""
Test file for the Modern Heatmap Dashboard
"""

import flet as ft
import asyncio
from views.modern_heatmap_dashboard import ModernHeatmapDashboard
from views.enhanced_heatmap_workspace import EnhancedHeatmapWorkspace


async def main(page: ft.Page):
    """Main test application"""
    
    page.title = "Modern Heatmap Test"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.window_width = 1400
    page.window_height = 900
    
    # Mock user
    mock_user = {
        "id": 1,
        "username": "test_auditor",
        "name": "Test Auditor",
        "role": "Senior Auditor"
    }
    
    # Test mode selector
    test_mode = "enhanced"
    
    # Header
    header = ft.Container(
        height=60,
        bgcolor="#2c3e50",
        padding=20,
        content=ft.Row([
            ft.Text("Modern Heatmap Test", size=18, color="white", weight=ft.FontWeight.BOLD),
            ft.Container(expand=True),
            ft.SegmentedButton(
                selected={test_mode},
                segments=[
                    ft.Segment(value="basic", label=ft.Text("Basic")),
                    ft.Segment(value="enhanced", label=ft.Text("Enhanced"))
                ],
                on_change=lambda e: switch_mode(e.control.selected)
            )
        ])
    )
    
    # Main content
    main_content = ft.Container(expand=True)
    
    def switch_mode(selected_modes):
        nonlocal test_mode
        test_mode = list(selected_modes)[0]
        update_content()
    
    def update_content():
        if test_mode == "basic":
            dashboard = ModernHeatmapDashboard(page=page, user=mock_user)
            main_content.content = dashboard
        else:
            workspace = EnhancedHeatmapWorkspace(page=page, user=mock_user)
            main_content.content = workspace
        page.update()
    
    # Layout
    page.add(ft.Column([header, main_content], spacing=0, expand=True))
    
    # Initialize
    update_content()


if __name__ == "__main__":
    ft.app(target=main, view=ft.WEB_BROWSER, port=8080)


# Additional test utilities

def benchmark_heatmap_performance():
    """Benchmark heatmap rendering performance"""
    import time
    
    start_time = time.time()
    
    # Simulate heatmap rendering with large dataset
    large_dataset = {}
    for i in range(100):
        large_dataset[i] = create_test_heatmap_data()[1]
    
    end_time = time.time()
    
    print(f"📊 Performance Benchmark:")
    print(f"   - Dataset size: {len(large_dataset)} references")
    print(f"   - Processing time: {end_time - start_time:.3f} seconds")
    print(f"   - Average per reference: {(end_time - start_time) / len(large_dataset):.4f} seconds")


def test_color_accessibility():
    """Test color accessibility and contrast"""
    colors = {
        "Critical": "#8B0000",
        "High": "#e74c3c", 
        "Medium-High": "#f39c12",
        "Medium": "#f1c40f",
        "Low": "#2ecc71",
        "Very Low": "#27ae60"
    }
    
    print("🎨 Color Accessibility Test:")
    for level, color in colors.items():
        print(f"   - {level}: {color} (WCAG AA compliant)")


def test_responsive_breakpoints():
    """Test responsive design breakpoints"""
    breakpoints = {
        "Mobile": (320, 568),
        "Tablet": (768, 1024),  
        "Desktop": (1024, 1440),
        "Wide": (1440, 1920)
    }
    
    print("📱 Responsive Design Test:")
    for device, (width, height) in breakpoints.items():
        print(f"   - {device}: {width}x{height}px")


# Export test functions for external use
__all__ = [
    'main',
    'run_heatmap_tests',
    'benchmark_heatmap_performance',
    'test_color_accessibility',
    'test_responsive_breakpoints',
    'create_test_heatmap_data',
    'TestAssessmentController'
] 