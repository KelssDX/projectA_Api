import json
import csv
from datetime import datetime
from io import StringIO


class ExportManager:
    """Handles exporting assessment data to various formats"""
    
    def __init__(self):
        self.supported_formats = ['json', 'csv', 'txt']
    
    async def export_assessment(self, assessment_data, format_type='json'):
        """
        Export assessment data to specified format
        
        Args:
            assessment_data: Dictionary containing assessment data
            format_type: Export format ('json', 'csv', 'txt')
        
        Returns:
            Tuple of (content, filename, mime_type)
        """
        if not assessment_data:
            raise ValueError("No assessment data provided")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        reference_id = assessment_data.get('referenceId', 'unknown')
        
        if format_type.lower() == 'json':
            return self._export_json(assessment_data, reference_id, timestamp)
        elif format_type.lower() == 'csv':
            return self._export_csv(assessment_data, reference_id, timestamp)
        elif format_type.lower() == 'txt':
            return self._export_txt(assessment_data, reference_id, timestamp)
        else:
            raise ValueError(f"Unsupported export format: {format_type}")
    
    def _export_json(self, assessment_data, reference_id, timestamp):
        """Export assessment data as JSON"""
        content = json.dumps(assessment_data, indent=2, default=str)
        filename = f"assessment_{reference_id}_{timestamp}.json"
        mime_type = "application/json"
        
        return content, filename, mime_type
    
    def _export_csv(self, assessment_data, reference_id, timestamp):
        """Export assessment data as CSV"""
        output = StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow(['Field', 'Value'])
        
        # Write basic information
        basic_fields = [
            ('Reference ID', assessment_data.get('referenceId', '')),
            ('Title', assessment_data.get('title', '')),
            ('Department', assessment_data.get('department', '')),
            ('Project', assessment_data.get('project', '')),
            ('Assessment Date', assessment_data.get('assessmentDate', '')),
            ('Risk Score', assessment_data.get('riskScore', '')),
            ('Risk Level', assessment_data.get('riskLevel', ''))
        ]
        
        for field, value in basic_fields:
            writer.writerow([field, value])
        
        # Write risk assessments if available
        risk_assessments = assessment_data.get('riskAssessments', [])
        if risk_assessments:
            writer.writerow(['', ''])  # Empty row
            writer.writerow(['Risk Assessments', ''])
            writer.writerow(['ID', 'Risk', 'Control', 'Outcome', 'Likelihood', 'Impact'])
            
            for assessment in risk_assessments:
                writer.writerow([
                    assessment.get('id', ''),
                    assessment.get('risk', ''),
                    assessment.get('control', ''),
                    assessment.get('outcome', ''),
                    assessment.get('likelihood', ''),
                    assessment.get('impact', '')
                ])
        
        content = output.getvalue()
        output.close()
        
        filename = f"assessment_{reference_id}_{timestamp}.csv"
        mime_type = "text/csv"
        
        return content, filename, mime_type
    
    def _export_txt(self, assessment_data, reference_id, timestamp):
        """Export assessment data as formatted text"""
        lines = []
        lines.append("RISK ASSESSMENT REPORT")
        lines.append("=" * 50)
        lines.append("")
        
        # Basic Information
        lines.append("BASIC INFORMATION")
        lines.append("-" * 20)
        lines.append(f"Reference ID: {assessment_data.get('referenceId', 'N/A')}")
        lines.append(f"Title: {assessment_data.get('title', 'N/A')}")
        lines.append(f"Department: {assessment_data.get('department', 'N/A')}")
        lines.append(f"Project: {assessment_data.get('project', 'N/A')}")
        lines.append(f"Assessment Date: {assessment_data.get('assessmentDate', 'N/A')}")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Risk Summary
        lines.append("RISK SUMMARY")
        lines.append("-" * 15)
        lines.append(f"Risk Score: {assessment_data.get('riskScore', 'N/A')}")
        lines.append(f"Risk Level: {assessment_data.get('riskLevel', 'N/A')}")
        lines.append("")
        
        # Risk Assessments
        risk_assessments = assessment_data.get('riskAssessments', [])
        if risk_assessments:
            lines.append("DETAILED RISK ASSESSMENTS")
            lines.append("-" * 30)
            
            for i, assessment in enumerate(risk_assessments, 1):
                lines.append(f"{i}. Risk Assessment ID: {assessment.get('id', 'N/A')}")
                lines.append(f"   Risk: {assessment.get('risk', 'N/A')}")
                lines.append(f"   Control: {assessment.get('control', 'N/A')}")
                lines.append(f"   Outcome: {assessment.get('outcome', 'N/A')}")
                lines.append(f"   Likelihood: {assessment.get('likelihood', 'N/A')}")
                lines.append(f"   Impact: {assessment.get('impact', 'N/A')}")
                lines.append("")
        
        # Findings and Recommendations
        findings = assessment_data.get('findings', '')
        if findings:
            lines.append("FINDINGS")
            lines.append("-" * 10)
            lines.append(findings)
            lines.append("")
        
        recommendations = assessment_data.get('recommendations', '')
        if recommendations:
            lines.append("RECOMMENDATIONS")
            lines.append("-" * 15)
            lines.append(recommendations)
            lines.append("")
        
        # Footer
        lines.append("=" * 50)
        lines.append("End of Report")
        
        content = "\n".join(lines)
        filename = f"assessment_{reference_id}_{timestamp}.txt"
        mime_type = "text/plain"
        
        return content, filename, mime_type
    
    async def export_heatmap_data(self, heatmap_data, format_type='csv'):
        """
        Export heatmap data to specified format
        
        Args:
            heatmap_data: Dictionary containing heatmap data
            format_type: Export format ('csv', 'json')
        
        Returns:
            Tuple of (content, filename, mime_type)
        """
        if not heatmap_data:
            raise ValueError("No heatmap data provided")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        reference_id = heatmap_data.get('referenceId', 'unknown')
        
        if format_type.lower() == 'csv':
            return self._export_heatmap_csv(heatmap_data, reference_id, timestamp)
        elif format_type.lower() == 'json':
            return self._export_json(heatmap_data, f"heatmap_{reference_id}", timestamp)
        else:
            raise ValueError(f"Unsupported heatmap export format: {format_type}")
    
    def _export_heatmap_csv(self, heatmap_data, reference_id, timestamp):
        """Export heatmap data as CSV matrix"""
        output = StringIO()
        writer = csv.writer(output)
        
        heatmap_grid = heatmap_data.get('heatmapGrid', {})
        
        if not heatmap_grid:
            writer.writerow(['No heatmap data available'])
            content = output.getvalue()
            output.close()
            
            filename = f"heatmap_{reference_id}_{timestamp}.csv"
            return content, filename, "text/csv"
        
        # Get all unique impact and likelihood levels
        impact_levels = set()
        likelihood_levels = set()
        
        for impact, likelihood_dict in heatmap_grid.items():
            impact_levels.add(impact)
            for likelihood in likelihood_dict.keys():
                likelihood_levels.add(likelihood)
        
        # Sort levels (could be improved with proper ordering)
        impact_levels = sorted(list(impact_levels))
        likelihood_levels = sorted(list(likelihood_levels))
        
        # Write header row
        header = ['Impact \\ Likelihood'] + likelihood_levels
        writer.writerow(header)
        
        # Write data rows
        for impact in impact_levels:
            row = [impact]
            for likelihood in likelihood_levels:
                count = heatmap_grid.get(impact, {}).get(likelihood, 0)
                row.append(count)
            writer.writerow(row)
        
        content = output.getvalue()
        output.close()
        
        filename = f"heatmap_{reference_id}_{timestamp}.csv"
        mime_type = "text/csv"
        
        return content, filename, mime_type
    
    def get_supported_formats(self):
        """Get list of supported export formats"""
        return self.supported_formats.copy()


# Utility functions for file operations
def save_export_file(content, filename, mime_type):
    """
    Save exported content to file (for desktop applications)
    
    Args:
        content: File content as string
        filename: Suggested filename
        mime_type: MIME type of the content
    
    Returns:
        Boolean indicating success
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error saving file: {e}")
        return False


def generate_filename(base_name, reference_id=None, format_type='txt'):
    """
    Generate a standardized filename for exports
    
    Args:
        base_name: Base name for the file
        reference_id: Assessment reference ID
        format_type: File format extension
    
    Returns:
        Generated filename
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if reference_id:
        return f"{base_name}_{reference_id}_{timestamp}.{format_type}"
    else:
        return f"{base_name}_{timestamp}.{format_type}" 
