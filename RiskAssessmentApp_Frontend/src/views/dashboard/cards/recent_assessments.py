import flet as ft
from flet import Icons
from src.utils.theme import create_modern_button, ThemeColors


def build_recent_assessments_card(colors: ThemeColors, on_navigate, recent_assessments=None) -> ft.Column:
    """Build card listing recent assessments."""
    # Create responsive table with custom layout
    header = ft.Container(
        height=40,
        bgcolor=colors.surface,
        border=ft.border.only(bottom=ft.BorderSide(1, colors.border)),
        padding=ft.padding.only(left=24, right=24),
        content=ft.Row([
            ft.Container(expand=2, content=ft.Text("Assessment", weight=ft.FontWeight.BOLD, color=colors.text_secondary)),
            ft.Container(expand=1, content=ft.Text("Department", weight=ft.FontWeight.BOLD, color=colors.text_secondary)),
            ft.Container(expand=1, content=ft.Text("Risk Level", weight=ft.FontWeight.BOLD, color=colors.text_secondary)),
        ], expand=True)
    )
    
    # Generate rows from real data or show empty state
    rows = []
    if recent_assessments and len(recent_assessments) > 0:
        for assessment in recent_assessments:
            # Set risk level color
            risk_color = "#95a5a6"  # Default gray
            if assessment.risk_level == "High":
                risk_color = "#e74c3c"  # Red
            elif assessment.risk_level == "Medium":
                risk_color = "#f39c12"  # Orange
            elif assessment.risk_level == "Low":
                risk_color = "#2ecc71"  # Green
            
            rows.append(ft.Container(
                height=50,
                bgcolor=colors.surface,
                border=ft.border.only(bottom=ft.BorderSide(1, colors.border)),
                padding=ft.padding.only(left=24, right=24),
                content=ft.Row([
                    ft.Container(expand=2, content=ft.Text(assessment.title or "Untitled Assessment", color=colors.text_primary, overflow=ft.TextOverflow.ELLIPSIS)),
                    ft.Container(expand=1, content=ft.Text(assessment.department or "-", color=colors.text_primary, overflow=ft.TextOverflow.ELLIPSIS)),
                    ft.Container(expand=1, content=ft.Text(assessment.risk_level or "N/A", color=risk_color, weight=ft.FontWeight.BOLD)),
                ], expand=True)
            ))
    else:
        # Show empty state
        rows.append(ft.Container(
            height=100,
            alignment=ft.alignment.center,
            content=ft.Column([
                ft.Icon(Icons.ASSESSMENT, size=40, color=colors.text_secondary),
                ft.Text("No recent assessments found", color=colors.text_secondary, size=16),
            ], spacing=10, alignment=ft.MainAxisAlignment.CENTER)
        ))
    
    table = ft.Column([header] + rows, spacing=0, expand=True)
    return ft.Column(
        [
            ft.Row(
                [
                    ft.Text("Recent Assessments", size=20, weight=ft.FontWeight.BOLD, color=colors.text_primary),
                    create_modern_button(colors, "View All", icon=Icons.LIST_ALT, on_click=lambda _: on_navigate("assessments", "list"), style="secondary", width=100),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            ft.Divider(color=colors.border, height=20),
            table,
        ],
        spacing=16,
    )
