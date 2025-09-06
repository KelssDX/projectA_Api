"""
Test the Modern Heatmap Dashboard in Desktop Mode
"""
import flet as ft
from views.modern_heatmap_dashboard import ModernHeatmapDashboard
from views.enhanced_heatmap_workspace import EnhancedHeatmapWorkspace


async def main(page: ft.Page):
    """Test application for modern heatmap features in desktop mode"""
    
    page.title = "Modern Heatmap Dashboard - Desktop Test"
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
            ft.Text("🎯 Modern Heatmap Dashboard - Desktop Mode", 
                   size=18, color="white", weight=ft.FontWeight.BOLD),
            ft.Container(expand=True),
            ft.SegmentedButton(
                selected={test_mode},
                segments=[
                    ft.Segment(value="basic", label=ft.Text("Basic Dashboard")),
                    ft.Segment(value="enhanced", label=ft.Text("Enhanced Workspace"))
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
            try:
                dashboard = ModernHeatmapDashboard(page=page, user=mock_user)
                main_content.content = dashboard
            except Exception as e:
                main_content.content = ft.Container(
                    content=ft.Column([
                        ft.Text("Error loading Basic Dashboard:", color="#e74c3c", size=16),
                        ft.Text(str(e), size=12),
                        ft.Text("This may be due to missing backend connections.", size=12, color="#7f8c8d")
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    alignment=ft.alignment.center
                )
        else:
            try:
                workspace = EnhancedHeatmapWorkspace(page=page, user=mock_user)
                main_content.content = workspace
            except Exception as e:
                main_content.content = ft.Container(
                    content=ft.Column([
                        ft.Text("Error loading Enhanced Workspace:", color="#e74c3c", size=16),
                        ft.Text(str(e), size=12),
                        ft.Text("This may be due to missing backend connections.", size=12, color="#7f8c8d")
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    alignment=ft.alignment.center
                )
        page.update()
    
    # Create demo view with instructions
    demo_content = ft.Container(
        padding=30,
        content=ft.Column([
            ft.Text("🚀 Modern Heatmap Dashboard Features", 
                   size=24, weight=ft.FontWeight.BOLD, color="#2c3e50"),
            ft.Container(height=20),
            
            ft.Row([
                ft.Card(
                    content=ft.Container(
                        padding=20,
                        width=400,
                        content=ft.Column([
                            ft.Text("✨ Multi-Tasking Modes", size=18, weight=ft.FontWeight.BOLD),
                            ft.Text("• Dashboard Mode (70/30 split)", size=14),
                            ft.Text("• Split View (50/50 heatmap/form)", size=14),
                            ft.Text("• Overlay Mode (fullscreen)", size=14),
                            ft.Container(height=10),
                            ft.Text("Perfect for different workflow needs!", 
                                   size=12, color="#7f8c8d", italic=True)
                        ])
                    )
                ),
                
                ft.Container(width=20),
                
                ft.Card(
                    content=ft.Container(
                        padding=20,
                        width=400,
                        content=ft.Column([
                            ft.Text("🎯 Interactive Features", size=18, weight=ft.FontWeight.BOLD),
                            ft.Text("• Click cells for instant actions", size=14),
                            ft.Text("• Hover animations & tooltips", size=14),
                            ft.Text("• Real-time synchronization", size=14),
                            ft.Container(height=10),
                            ft.Text("85-90% faster assessment creation!", 
                                   size=12, color="#2ecc71", weight=ft.FontWeight.BOLD)
                        ])
                    )
                )
            ]),
            
            ft.Container(height=30),
            
            ft.Row([
                ft.Card(
                    content=ft.Container(
                        padding=20,
                        width=400,
                        content=ft.Column([
                            ft.Text("🤖 Smart Analytics", size=18, weight=ft.FontWeight.BOLD),
                            ft.Text("• AI-powered insights", size=14),
                            ft.Text("• Risk trend analysis", size=14),
                            ft.Text("• Predictive recommendations", size=14),
                            ft.Container(height=10),
                            ft.Text("Intelligent risk intelligence!", 
                                   size=12, color="#3498db", italic=True)
                        ])
                    )
                ),
                
                ft.Container(width=20),
                
                ft.Card(
                    content=ft.Container(
                        padding=20,
                        width=400,
                        content=ft.Column([
                            ft.Text("⚡ Efficiency Gains", size=18, weight=ft.FontWeight.BOLD),
                            ft.Text("• Parallel assessment processing", size=14),
                            ft.Text("• Context-aware pre-filling", size=14),
                            ft.Text("• Team collaboration features", size=14),
                            ft.Container(height=10),
                            ft.Text("Work smarter, not harder!", 
                                   size=12, color="#f39c12", weight=ft.FontWeight.BOLD)
                        ])
                    )
                )
            ]),
            
            ft.Container(height=40),
            
            ft.Row([
                ft.ElevatedButton(
                    text="📊 Try Basic Dashboard",
                    icon=ft.icons.DASHBOARD,
                    bgcolor="#3498db",
                    color="white",
                    width=200,
                    height=50,
                    on_click=lambda e: (setattr(globals(), 'test_mode', 'basic'), update_content())
                ),
                
                ft.Container(width=20),
                
                ft.ElevatedButton(
                    text="🚀 Try Enhanced Workspace",
                    icon=ft.icons.WORKSPACES,
                    bgcolor="#2ecc71",
                    color="white",
                    width=200,
                    height=50,
                    on_click=lambda e: (setattr(globals(), 'test_mode', 'enhanced'), update_content())
                ),
                
                ft.Container(width=20),
                
                ft.ElevatedButton(
                    text="🏠 Back to Demo",
                    icon=ft.icons.HOME,
                    bgcolor="#95a5a6",
                    color="white",
                    width=200,
                    height=50,
                    on_click=lambda e: show_demo()
                )
            ], alignment=ft.MainAxisAlignment.CENTER)
        ], alignment=ft.MainAxisAlignment.CENTER)
    )
    
    def show_demo():
        main_content.content = demo_content
        page.update()
    
    # Layout
    page.add(ft.Column([header, main_content], spacing=0, expand=True))
    
    # Start with demo view
    show_demo()


if __name__ == "__main__":
    print("🎯 Starting Modern Heatmap Desktop Test...")
    print("✨ Features: Multi-tasking modes, interactive cells, real-time sync")
    print("🚀 Note: Some features may require backend API connection")
    ft.app(target=main, view=ft.AppView.FLET_APP) 