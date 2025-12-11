import flet as ft
from flet import Icons

from src.utils.theme import get_theme_colors, create_modern_button
from src.views.common.base_view import BaseView
from .cards.statistics import build_statistics_row
from .cards.risk_distribution import build_risk_distribution_card
from .cards.recent_assessments import build_recent_assessments_card


class DashboardView(BaseView):
    """Main dashboard composed of modular card sections."""

    def __init__(self, page, auditing_client, on_navigate, current_user=None):
        self.auditing_client = auditing_client
        self.on_navigate = on_navigate
        self.current_user = current_user
        self.assessments_data = []
        self.recent_assessments = []
        self.stats = {
            "active_assessments": 0,
            "high_risk_areas": 0,
            "completed_this_month": 0,
            "pending_reviews": 0,
        }

        colors = get_theme_colors(
            page.theme_mode if hasattr(page, "theme_mode") else ft.ThemeMode.LIGHT
        )
        actions = [
            create_modern_button(
                colors,
                "Export Data",
                icon=Icons.DOWNLOAD,
                on_click=self.export_assessments,
                style="primary",
            ),
            create_modern_button(
                colors,
                "New Assessment",
                icon=Icons.ADD,
                on_click=self.handle_new_assessment,
                style="success",
            ),
        ]

        super().__init__(page, "Risk Assessment Dashboard", actions=actions, colors=colors)
        self.build_dashboard()
        
        # Load real data from API
        self.load_data()

    def build_dashboard(self) -> None:
        colors = self.colors
        self.cards_column.controls.clear()
        self.add_card(build_statistics_row(self.stats, colors, self.on_navigate))
        self.add_card(build_risk_distribution_card(colors, self.on_navigate))
        self.add_card(build_recent_assessments_card(colors, self.on_navigate, self.recent_assessments))

    def load_data(self):
        """Load assessment data when dashboard is shown"""
        if hasattr(self, 'page') and self.page:
            self.page.run_task(self._load_assessments_data)

    async def _load_assessments_data(self):
        """Load assessments data from the API"""
        try:
            print("DEBUG: Dashboard loading assessments from API...")
            # Load assessments from API
            api_assessments = await self.auditing_client.get_assessments()
            print(f"DEBUG: API returned {len(api_assessments) if api_assessments else 0} assessments")
            
            if api_assessments:
                # Convert API data to Assessment objects
                from src.models.assessment import Assessment
                self.assessments_data = [Assessment.from_json(a) for a in api_assessments]
                print(f"DEBUG: Converted to {len(self.assessments_data)} Assessment objects")
                
                # Get the 5 most recent assessments
                sorted_assessments = sorted(
                    self.assessments_data, 
                    key=lambda x: x.updated_at if x.updated_at else x.created_at,
                    reverse=True
                )
                self.recent_assessments = sorted_assessments[:5]
                print(f"DEBUG: Selected {len(self.recent_assessments)} recent assessments")
                
                # Update statistics
                self._update_statistics()
                
                # Rebuild dashboard with new data
                self.build_dashboard()
                if hasattr(self, 'page') and self.page:
                    self.page.update()
            else:
                print("DEBUG: No assessments data from API")
                    
        except Exception as e:
            print(f"Error loading assessments from API: {e}")
            import traceback
            traceback.print_exc()
            # Keep empty data on error
            self.assessments_data = []
            self.recent_assessments = []

    def _update_statistics(self):
        """Update dashboard statistics based on loaded data"""
        if not self.assessments_data:
            return
            
        # Count active assessments (assuming those with recent updates are active)
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        active_count = 0
        high_risk_count = 0
        completed_count = 0
        
        for assessment in self.assessments_data:
            # Count high risk assessments
            if assessment.risk_level == "High":
                high_risk_count += 1
            
            # For now, count all assessments as active and completed
            # This is a simplified approach since we don't have proper status tracking
            active_count += 1
            completed_count += 1
        
        self.stats = {
            "active_assessments": active_count,
            "high_risk_areas": high_risk_count,
            "completed_this_month": completed_count,
            "pending_reviews": max(0, len(self.assessments_data) - completed_count),
        }

    # Placeholder handlers
    def export_assessments(self, _):
        pass

    def handle_new_assessment(self, _):
        pass
