import os
import datetime
import xlsxwriter


class ExcelExporter:
    """Export data to Excel files."""

    def __init__(self, output_dir="exports"):
        """Initialize the Excel exporter.

        Args:
            output_dir: Directory to save generated Excel files
        """
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def _get_attr(self, obj, attr, default=None):
        """Helper to get attribute from dict or object"""
        if isinstance(obj, dict):
            return obj.get(attr, default)
        else:
            return getattr(obj, attr, default)

    def export_assessments(self, assessments, filename=None):
        """Export a list of assessments to an Excel file.

        Args:
            assessments: List of Assessment objects
            filename: Optional filename (if not provided, auto-generate one)

        Returns:
            str: Path to the generated Excel file
        """
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.output_dir}/Assessments_Export_{timestamp}.xlsx"
        elif not filename.startswith(self.output_dir):
            filename = f"{self.output_dir}/{filename}"

        # Create workbook and add worksheets
        workbook = xlsxwriter.Workbook(filename)

        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#D7E4BC'
        })

        date_format = workbook.add_format({
            'num_format': 'yyyy-mm-dd',
            'border': 1
        })

        cell_format = workbook.add_format({
            'border': 1,
            'valign': 'vcenter'
        })

        risk_high_format = workbook.add_format({
            'border': 1,
            'bold': True,
            'fg_color': '#FFC7CE',
            'font_color': '#9C0006'
        })

        risk_medium_format = workbook.add_format({
            'border': 1,
            'bold': True,
            'fg_color': '#FFEB9C',
            'font_color': '#9C6500'
        })

        risk_low_format = workbook.add_format({
            'border': 1,
            'bold': True,
            'fg_color': '#C6EFCE',
            'font_color': '#006100'
        })

        # Add Summary worksheet
        summary_sheet = workbook.add_worksheet('Summary')

        # Set column widths
        summary_sheet.set_column('A:A', 20)
        summary_sheet.set_column('B:B', 15)

        # Add title
        summary_sheet.merge_range('A1:B1', 'Risk Assessment Summary', header_format)
        summary_sheet.write('A2', 'Generated Date', cell_format)
        summary_sheet.write('B2', datetime.datetime.now().strftime("%Y-%m-%d"), date_format)

        # Calculate statistics - handle both dict and object formats
        total_assessments = len(assessments)
        high_risk = sum(1 for a in assessments if self._get_attr(a, 'risk_level') == "High")
        medium_risk = sum(1 for a in assessments if self._get_attr(a, 'risk_level') == "Medium")
        low_risk = sum(1 for a in assessments if self._get_attr(a, 'risk_level') == "Low")

        # Calculate percentage if we have assessments
        high_pct = (high_risk / total_assessments * 100) if total_assessments > 0 else 0
        medium_pct = (medium_risk / total_assessments * 100) if total_assessments > 0 else 0
        low_pct = (low_risk / total_assessments * 100) if total_assessments > 0 else 0

        # Calculate average score
        scores = [self._get_attr(a, 'risk_score') for a in assessments if self._get_attr(a, 'risk_score') is not None]
        avg_score = sum(scores) / len(scores) if scores else 0

        # Write summary data
        summary_data = [
            ['Total Assessments', total_assessments],
            ['High Risk', high_risk],
            ['Medium Risk', medium_risk],
            ['Low Risk', low_risk],
            ['Average Risk Score', round(avg_score, 2)],
        ]

        row = 4
        summary_sheet.write(row, 0, 'Risk Statistics', header_format)
        summary_sheet.write(row, 1, '', header_format)
        row += 1

        for item in summary_data:
            summary_sheet.write(row, 0, item[0], cell_format)
            summary_sheet.write(row, 1, item[1], cell_format)
            row += 1

        # Add chart for risk distribution
        risk_chart = workbook.add_chart({'type': 'pie'})

        # Add the data for the pie chart
        summary_sheet.write('A12', 'Risk Level', header_format)
        summary_sheet.write('B12', 'Count', header_format)
        summary_sheet.write('A13', 'High', risk_high_format)
        summary_sheet.write('B13', high_risk, cell_format)
        summary_sheet.write('A14', 'Medium', risk_medium_format)
        summary_sheet.write('B14', medium_risk, cell_format)
        summary_sheet.write('A15', 'Low', risk_low_format)
        summary_sheet.write('B15', low_risk, cell_format)

        # Configure the chart
        risk_chart.add_series({
            'name': 'Risk Distribution',
            'categories': ['Summary', 12, 0, 14, 0],
            'values': ['Summary', 12, 1, 14, 1],
            'points': [
                {'fill': {'color': '#FFC7CE'}},  # High risk (red)
                {'fill': {'color': '#FFEB9C'}},  # Medium risk (orange)
                {'fill': {'color': '#C6EFCE'}},  # Low risk (green)
            ],
        })

        risk_chart.set_title({'name': 'Risk Distribution'})
        risk_chart.set_style(10)

        # Insert the chart into the worksheet
        summary_sheet.insert_chart('D10', risk_chart, {'x_offset': 25, 'y_offset': 10})

        # Department statistics
        departments = {}
        for assessment in assessments:
            dept = self._get_attr(assessment, 'department')
            if dept:
                if assessment.department not in departments:
                    departments[dept] = {
                        'count': 0,
                        'high': 0,
                        'medium': 0,
                        'low': 0,
                        'total_score': 0
                    }

                departments[dept]['count'] += 1

                rl = self._get_attr(assessment, 'risk_level')
                if rl == "High":
                    departments[dept]['high'] += 1
                elif rl == "Medium":
                    departments[dept]['medium'] += 1
                elif rl == "Low":
                    departments[dept]['low'] += 1

                rs = self._get_attr(assessment, 'risk_score')
                if rs is not None:
                    departments[dept]['total_score'] += rs

        # If we have departments, create a department summary
        if departments:
            row = 25
            summary_sheet.merge_range(f'A{row}:E{row}', 'Department Risk Summary', header_format)
            row += 1

            # Write headers
            headers = ['Department', 'Assessments', 'High', 'Medium', 'Low', 'Avg Score']
            for col, header in enumerate(headers):
                summary_sheet.write(row, col, header, header_format)
            row += 1

            # Write department data
            for dept, data in sorted(departments.items()):
                avg_score = data['total_score'] / data['count'] if data['count'] > 0 else 0

                summary_sheet.write(row, 0, dept, cell_format)
                summary_sheet.write(row, 1, data['count'], cell_format)
                summary_sheet.write(row, 2, data['high'], risk_high_format if data['high'] > 0 else cell_format)
                summary_sheet.write(row, 3, data['medium'], risk_medium_format if data['medium'] > 0 else cell_format)
                summary_sheet.write(row, 4, data['low'], risk_low_format if data['low'] > 0 else cell_format)
                summary_sheet.write(row, 5, round(avg_score, 2), cell_format)
                row += 1

        # Add Assessments worksheet
        assessment_sheet = workbook.add_worksheet('All Assessments')

        # Set column widths
        assessment_sheet.set_column('A:A', 8)  # ID
        assessment_sheet.set_column('B:B', 30)  # Title
        assessment_sheet.set_column('C:C', 15)  # Department
        assessment_sheet.set_column('D:D', 12)  # Date
        assessment_sheet.set_column('E:E', 10)  # Risk Level
        assessment_sheet.set_column('F:F', 10)  # Risk Score
        assessment_sheet.set_column('G:G', 30)  # Scope
        assessment_sheet.set_column('H:H', 30)  # Findings
        assessment_sheet.set_column('I:I', 30)  # Recommendations

        # Write headers
        headers = ['ID', 'Title', 'Department', 'Date', 'Risk Level', 'Risk Score',
                   'Scope', 'Findings', 'Recommendations']
        for col, header in enumerate(headers):
            assessment_sheet.write(0, col, header, header_format)

        # Write assessment data
        for row, assessment in enumerate(assessments, start=1):
            assessment_sheet.write(row, 0, self._get_attr(assessment, 'id', ''), cell_format)
            assessment_sheet.write(row, 1, self._get_attr(assessment, 'title', ''), cell_format)
            assessment_sheet.write(row, 2, self._get_attr(assessment, 'department', ''), cell_format)

            # Format and write date
            date_val = self._get_attr(assessment, 'assessment_date') or self._get_attr(assessment, 'created_at')
            if date_val and hasattr(date_val, 'strftime'):
                assessment_sheet.write_datetime(row, 3, date_val, date_format)
            elif isinstance(date_val, str):
                assessment_sheet.write(row, 3, date_val, cell_format)
            else:
                assessment_sheet.write(row, 3, 'N/A', cell_format)

            # Format and write risk level
            risk_level = self._get_attr(assessment, 'risk_level', 'N/A')
            risk_format = cell_format
            if risk_level == "High":
                risk_format = risk_high_format
            elif risk_level == "Medium":
                risk_format = risk_medium_format
            elif risk_level == "Low":
                risk_format = risk_low_format

            assessment_sheet.write(row, 4, risk_level, risk_format)

            # Write risk score
            risk_score = self._get_attr(assessment, 'risk_score')
            if risk_score is not None:
                assessment_sheet.write(row, 5, risk_score, cell_format)
            else:
                assessment_sheet.write(row, 5, 'N/A', cell_format)

            # Write details
            assessment_sheet.write(row, 6, self._get_attr(assessment, 'scope', ''), cell_format)
            assessment_sheet.write(row, 7, self._get_attr(assessment, 'findings', ''), cell_format)
            assessment_sheet.write(row, 8, self._get_attr(assessment, 'recommendations', ''), cell_format)

        # Add High Risk worksheet
        high_risk_assessments = [a for a in assessments if self._get_attr(a, 'risk_level') == "High"]
        if high_risk_assessments:
            high_risk_sheet = workbook.add_worksheet('High Risk')

            # Set column widths (same as main assessment sheet)
            high_risk_sheet.set_column('A:A', 8)  # ID
            high_risk_sheet.set_column('B:B', 30)  # Title
            high_risk_sheet.set_column('C:C', 15)  # Department
            high_risk_sheet.set_column('D:D', 12)  # Date
            high_risk_sheet.set_column('E:E', 10)  # Risk Score
            high_risk_sheet.set_column('F:F', 30)  # Findings
            high_risk_sheet.set_column('G:G', 30)  # Recommendations

            # Write headers
            headers = ['ID', 'Title', 'Department', 'Date', 'Risk Score', 'Findings', 'Recommendations']
            for col, header in enumerate(headers):
                high_risk_sheet.write(0, col, header, header_format)

            # Write high risk assessment data
            for row, assessment in enumerate(high_risk_assessments, start=1):
                high_risk_sheet.write(row, 0, assessment.id, cell_format)
                high_risk_sheet.write(row, 1, assessment.title or '', cell_format)
                high_risk_sheet.write(row, 2, assessment.department or '', cell_format)

                # Format and write date
                if hasattr(assessment.assessment_date, 'strftime'):
                    high_risk_sheet.write_datetime(row, 3, assessment.assessment_date, date_format)
                else:
                    high_risk_sheet.write(row, 3, 'N/A', cell_format)

                # Write risk score
                if assessment.risk_score is not None:
                    high_risk_sheet.write(row, 4, assessment.risk_score, cell_format)
                else:
                    high_risk_sheet.write(row, 4, 'N/A', cell_format)

                # Write details
                high_risk_sheet.write(row, 5, assessment.findings or '', cell_format)
                high_risk_sheet.write(row, 6, assessment.recommendations or '', cell_format)

        # Add Risk Factors worksheet
        factors_sheet = workbook.add_worksheet('Risk Factors')

        # Set column widths
        factors_sheet.set_column('A:A', 8)  # Assessment ID
        factors_sheet.set_column('B:B', 30)  # Assessment Title
        factors_sheet.set_column('C:C', 25)  # Factor Name
        factors_sheet.set_column('D:D', 10)  # Factor Value

        # Write headers
        headers = ['ID', 'Assessment', 'Risk Factor', 'Value']
        for col, header in enumerate(headers):
            factors_sheet.write(0, col, header, header_format)

        # Write risk factor data
        row = 1
        for assessment in assessments:
            if assessment.risk_factors:
                for factor in assessment.risk_factors:
                    if isinstance(factor, dict) and "name" in factor and "value" in factor:
                        factors_sheet.write(row, 0, assessment.id, cell_format)
                        factors_sheet.write(row, 1, assessment.title or '', cell_format)
                        factors_sheet.write(row, 2, factor["name"], cell_format)

                        # Write factor value
                        if isinstance(factor["value"], (int, float)):
                            factors_sheet.write(row, 3, factor["value"], cell_format)
                        else:
                            factors_sheet.write(row, 3, str(factor["value"]), cell_format)

                        row += 1

        # Close the workbook
        workbook.close()

        return filename

    def export_department_assessments(self, department, assessments, filename=None):
        """Export assessments for a specific department.

        Args:
            department: Department name
            assessments: List of assessments for this department
            filename: Optional filename (if not provided, auto-generate one)

        Returns:
            str: Path to the generated Excel file
        """
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.output_dir}/{department}_Assessments_{timestamp}.xlsx"
        elif not filename.startswith(self.output_dir):
            filename = f"{self.output_dir}/{filename}"

        # Filter assessments to department if not already filtered
        if department:
            dept_assessments = [a for a in assessments if a.department == department]
        else:
            dept_assessments = assessments

        # Create workbook
        workbook = xlsxwriter.Workbook(filename)

        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#D7E4BC'
        })

        date_format = workbook.add_format({
            'num_format': 'yyyy-mm-dd',
            'border': 1
        })

        cell_format = workbook.add_format({
            'border': 1,
            'valign': 'vcenter'
        })

        risk_high_format = workbook.add_format({
            'border': 1,
            'bold': True,
            'fg_color': '#FFC7CE',
            'font_color': '#9C0006'
        })

        risk_medium_format = workbook.add_format({
            'border': 1,
            'bold': True,
            'fg_color': '#FFEB9C',
            'font_color': '#9C6500'
        })

        risk_low_format = workbook.add_format({
            'border': 1,
            'bold': True,
            'fg_color': '#C6EFCE',
            'font_color': '#006100'
        })

        # Add Summary worksheet
        summary_sheet = workbook.add_worksheet('Department Summary')

        # Set column widths
        summary_sheet.set_column('A:A', 25)
        summary_sheet.set_column('B:B', 15)

        # Add title
        summary_sheet.merge_range('A1:B1', f'{department} Department Risk Assessment', header_format)
        summary_sheet.write('A2', 'Generated Date', cell_format)
        summary_sheet.write('B2', datetime.datetime.now().strftime("%Y-%m-%d"), date_format)

        # Calculate statistics
        total_assessments = len(dept_assessments)
        high_risk = sum(1 for a in dept_assessments if a.risk_level == "High")
        medium_risk = sum(1 for a in dept_assessments if a.risk_level == "Medium")
        low_risk = sum(1 for a in dept_assessments if a.risk_level == "Low")

        avg_score = (sum(a.risk_score for a in dept_assessments if a.risk_score is not None) /
                     total_assessments) if total_assessments > 0 else 0

        # Write summary data
        summary_data = [
            ['Total Assessments', total_assessments],
            ['High Risk', high_risk],
            ['Medium Risk', medium_risk],
            ['Low Risk', low_risk],
            ['Average Risk Score', round(avg_score, 2)],
        ]

        row = 4
        summary_sheet.write(row, 0, 'Risk Statistics', header_format)
        summary_sheet.write(row, 1, '', header_format)
        row += 1

        for item in summary_data:
            summary_sheet.write(row, 0, item[0], cell_format)
            summary_sheet.write(row, 1, item[1], cell_format)
            row += 1

        # Add chart for risk distribution
        risk_chart = workbook.add_chart({'type': 'pie'})

        # Add the data for the pie chart
        summary_sheet.write('A12', 'Risk Level', header_format)
        summary_sheet.write('B12', 'Count', header_format)
        summary_sheet.write('A13', 'High', risk_high_format)
        summary_sheet.write('B13', high_risk, cell_format)
        summary_sheet.write('A14', 'Medium', risk_medium_format)
        summary_sheet.write('B14', medium_risk, cell_format)
        summary_sheet.write('A15', 'Low', risk_low_format)
        summary_sheet.write('B15', low_risk, cell_format)

        # Configure the chart
        risk_chart.add_series({
            'name': 'Risk Distribution',
            'categories': ['Department Summary', 12, 0, 14, 0],
            'values': ['Department Summary', 12, 1, 14, 1],
            'points': [
                {'fill': {'color': '#FFC7CE'}},  # High risk (red)
                {'fill': {'color': '#FFEB9C'}},  # Medium risk (orange)
                {'fill': {'color': '#C6EFCE'}},  # Low risk (green)
            ],
        })

        risk_chart.set_title({'name': 'Risk Distribution'})
        risk_chart.set_style(10)

        # Insert the chart into the worksheet
        summary_sheet.insert_chart('D10', risk_chart, {'x_offset': 25, 'y_offset': 10})

        # Add Assessments worksheet
        assessment_sheet = workbook.add_worksheet('Assessments')

        # Set column widths
        assessment_sheet.set_column('A:A', 8)  # ID
        assessment_sheet.set_column('B:B', 30)  # Title
        assessment_sheet.set_column('C:C', 12)  # Date
        assessment_sheet.set_column('D:D', 10)  # Risk Level
        assessment_sheet.set_column('E:E', 10)  # Risk Score
        assessment_sheet.set_column('F:F', 30)  # Scope
        assessment_sheet.set_column('G:G', 30)  # Findings
        assessment_sheet.set_column('H:H', 30)  # Recommendations

        # Write headers
        headers = ['ID', 'Title', 'Date', 'Risk Level', 'Risk Score',
                   'Scope', 'Findings', 'Recommendations']
        for col, header in enumerate(headers):
            assessment_sheet.write(0, col, header, header_format)

        # Write assessment data
        for row, assessment in enumerate(dept_assessments, start=1):
            assessment_sheet.write(row, 0, assessment.id, cell_format)
            assessment_sheet.write(row, 1, assessment.title or '', cell_format)

            # Format and write date
            if hasattr(assessment.assessment_date, 'strftime'):
                assessment_sheet.write_datetime(row, 2, assessment.assessment_date, date_format)
            else:
                assessment_sheet.write(row, 2, 'N/A', cell_format)

            # Format and write risk level
            risk_format = cell_format
            if assessment.risk_level == "High":
                risk_format = risk_high_format
            elif assessment.risk_level == "Medium":
                risk_format = risk_medium_format
            elif assessment.risk_level == "Low":
                risk_format = risk_low_format

            assessment_sheet.write(row, 3, assessment.risk_level or 'N/A', risk_format)

            # Write risk score
            if assessment.risk_score is not None:
                assessment_sheet.write(row, 4, assessment.risk_score, cell_format)
            else:
                assessment_sheet.write(row, 4, 'N/A', cell_format)

            # Write details
            assessment_sheet.write(row, 5, assessment.scope or '', cell_format)
            assessment_sheet.write(row, 6, assessment.findings or '', cell_format)
            assessment_sheet.write(row, 7, assessment.recommendations or '', cell_format)

        # Add Risk Factors worksheet
        factors_sheet = workbook.add_worksheet('Risk Factors')

        # Set column widths
        factors_sheet.set_column('A:A', 8)  # Assessment ID
        factors_sheet.set_column('B:B', 30)  # Assessment Title
        factors_sheet.set_column('C:C', 25)  # Factor Name
        factors_sheet.set_column('D:D', 10)  # Factor Value

        # Write headers
        headers = ['ID', 'Assessment', 'Risk Factor', 'Value']
        for col, header in enumerate(headers):
            factors_sheet.write(0, col, header, header_format)

        # Write risk factor data
        row = 1
        for assessment in dept_assessments:
            if assessment.risk_factors:
                for factor in assessment.risk_factors:
                    if isinstance(factor, dict) and "name" in factor and "value" in factor:
                        factors_sheet.write(row, 0, assessment.id, cell_format)
                        factors_sheet.write(row, 1, assessment.title or '', cell_format)
                        factors_sheet.write(row, 2, factor["name"], cell_format)

                        # Write factor value
                        if isinstance(factor["value"], (int, float)):
                            factors_sheet.write(row, 3, factor["value"], cell_format)
                        else:
                            factors_sheet.write(row, 3, str(factor["value"]), cell_format)

                        row += 1

        # Close the workbook
        workbook.close()

        return filename
