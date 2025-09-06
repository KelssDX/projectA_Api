import os
import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing, Line
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie


class PDFGenerator:
    """Generate PDF reports for risk assessments."""

    def __init__(self, output_dir="reports"):
        """Initialize the PDF generator.

        Args:
            output_dir: Directory to save generated PDFs
        """
        # Use absolute path for reports
        self.output_dir = os.path.abspath(output_dir)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Initialize styles
        self.styles = getSampleStyleSheet()

        # Instead of adding new styles with the same names, modify existing ones
        # or use different names to avoid conflicts

        # Update existing styles
        self.styles['Title'].fontName = 'Helvetica-Bold'
        self.styles['Title'].fontSize = 16
        self.styles['Title'].spaceAfter = 12

        self.styles['Heading2'].fontName = 'Helvetica-Bold'
        self.styles['Heading2'].fontSize = 14
        self.styles['Heading2'].spaceAfter = 10
        self.styles['Heading2'].spaceBefore = 10

        # Add custom styles with unique names
        self.styles.add(ParagraphStyle(
            name='RiskHigh',
            fontName='Helvetica-Bold',
            fontSize=10,
            textColor=colors.red
        ))

        self.styles.add(ParagraphStyle(
            name='RiskMedium',
            fontName='Helvetica-Bold',
            fontSize=10,
            textColor=colors.orange
        ))

        self.styles.add(ParagraphStyle(
            name='RiskLow',
            fontName='Helvetica-Bold',
            fontSize=10,
            textColor=colors.green
        ))

    def generate_assessment_report(self, assessment):
        """Generate a PDF report for a risk assessment.

        Args:
            assessment: Assessment object with risk assessment data

        Returns:
            str: Path to the generated PDF file
        """
        # Generate filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.output_dir}/Assessment_{assessment.id}_{timestamp}.pdf"

        # Create the PDF document
        doc = SimpleDocTemplate(
            filename,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        # Container for the elements to be added to the document
        elements = []

        # Add title
        elements.append(Paragraph(f"Risk Assessment: {assessment.title}", self.styles['Title']))
        elements.append(Spacer(1, 0.25 * inch))

        # Add basic info table
        data = [
            ["Assessment ID", assessment.id],
            ["Department", assessment.department or "N/A"],
            ["Project", assessment.project or "N/A"],
            ["Date", assessment.assessment_date.strftime("%Y-%m-%d") if hasattr(assessment.assessment_date,
                                                                                'strftime') else "N/A"],
            ["Auditor", assessment.auditor or "N/A"],
        ]

        # Get risk level style
        risk_style = "RiskLow"
        if assessment.risk_level == "High":
            risk_style = "RiskHigh"
        elif assessment.risk_level == "Medium":
            risk_style = "RiskMedium"

        data.append(["Risk Score", f"{assessment.risk_score:.1f}" if assessment.risk_score is not None else "N/A"])
        data.append(["Risk Level", Paragraph(assessment.risk_level, self.styles[risk_style])])

        # Create the table
        table = Table(data, colWidths=[2 * inch, 3.5 * inch])
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 0.25 * inch))

        # Add scope
        elements.append(Paragraph("Scope", self.styles['Heading2']))
        elements.append(Paragraph(assessment.scope or "No scope provided", self.styles['Normal']))
        elements.append(Spacer(1, 0.25 * inch))

        # Add findings
        elements.append(Paragraph("Findings", self.styles['Heading2']))
        elements.append(Paragraph(assessment.findings or "No findings provided", self.styles['Normal']))
        elements.append(Spacer(1, 0.25 * inch))

        # Add recommendations
        elements.append(Paragraph("Recommendations", self.styles['Heading2']))
        elements.append(Paragraph(assessment.recommendations or "No recommendations provided", self.styles['Normal']))
        elements.append(Spacer(1, 0.25 * inch))

        # Add risk factors
        elements.append(Paragraph("Risk Factors", self.styles['Heading2']))

        if assessment.risk_factors:
            # Create table for risk factors
            risk_data = [["Factor", "Score"]]
            for factor in assessment.risk_factors:
                if isinstance(factor, dict) and "name" in factor and "value" in factor:
                    risk_data.append([
                        factor["name"],
                        f"{factor['value']:.1f}" if isinstance(factor["value"], (int, float)) else factor["value"]
                    ])

            if len(risk_data) > 1:  # If we have any factors
                risk_table = Table(risk_data, colWidths=[4 * inch, 1.5 * inch])
                risk_table.setStyle(TableStyle([
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('PADDING', (0, 0), (-1, -1), 6),
                ]))
                elements.append(risk_table)
            else:
                elements.append(Paragraph("No risk factors defined", self.styles['Normal']))
        else:
            elements.append(Paragraph("No risk factors defined", self.styles['Normal']))

        # Add risk factor chart if we have factors
        if assessment.risk_factors and len(assessment.risk_factors) > 0:
            elements.append(Spacer(1, 0.5 * inch))
            elements.append(Paragraph("Risk Factor Visualization", self.styles['Heading2']))

            # Create a drawing for the chart
            drawing = Drawing(400, 200)

            # Create the chart
            bc = VerticalBarChart()
            bc.x = 50
            bc.y = 50
            bc.height = 125
            bc.width = 300

            # Extract data
            data = []
            factor_names = []

            values = []
            for factor in assessment.risk_factors:
                if isinstance(factor, dict) and "name" in factor and "value" in factor:
                    try:
                        val = float(factor["value"])
                        values.append(val)
                        factor_names.append(factor["name"])
                    except (ValueError, TypeError):
                        pass

            if values:
                data.append(values)
                bc.data = data

                # Set axis labels
                bc.categoryAxis.categoryNames = factor_names
                bc.categoryAxis.labels.boxAnchor = 'ne'
                bc.categoryAxis.labels.dx = -8
                bc.categoryAxis.labels.dy = -2
                bc.categoryAxis.labels.angle = 30

                # Set colors
                bc.bars[0].fillColor = colors.skyblue

                # Add to drawing
                drawing.add(bc)

                # Add to document
                elements.append(drawing)

        # Build the PDF
        doc.build(elements)

        return filename

    def generate_department_report(self, department, assessments):
        """Generate a department-level risk report.

        Args:
            department: Department name
            assessments: List of assessments for this department

        Returns:
            str: Path to the generated PDF file
        """
        # Generate filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.output_dir}/Department_{department}_{timestamp}.pdf"

        # Create the PDF document
        doc = SimpleDocTemplate(
            filename,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        # Container for the elements to be added to the document
        elements = []

        # Add title
        elements.append(Paragraph(f"Risk Assessment Report: {department} Department", self.styles['Title']))
        elements.append(Spacer(1, 0.25 * inch))

        # Add summary
        elements.append(Paragraph("Risk Summary", self.styles['Heading2']))

        # Calculate risk statistics
        total_assessments = len(assessments)
        high_risk = sum(1 for a in assessments if a.risk_level == "High")
        medium_risk = sum(1 for a in assessments if a.risk_level == "Medium")
        low_risk = sum(1 for a in assessments if a.risk_level == "Low")
        avg_score = sum(a.risk_score for a in assessments if
                        a.risk_score is not None) / total_assessments if total_assessments > 0 else 0

        # Add summary table
        summary_data = [
            ["Total Assessments", str(total_assessments)],
            ["High Risk", str(high_risk)],
            ["Medium Risk", str(medium_risk)],
            ["Low Risk", str(low_risk)],
            ["Average Risk Score", f"{avg_score:.2f}"]
        ]

        summary_table = Table(summary_data, colWidths=[2.5 * inch, 1.5 * inch])
        summary_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 0.25 * inch))

        # Add risk distribution chart
        elements.append(Paragraph("Risk Distribution", self.styles['Heading2']))

        # Create a drawing for the chart
        drawing = Drawing(300, 200)

        # Create pie chart
        pie = Pie()
        pie.x = 150
        pie.y = 100
        pie.width = 100
        pie.height = 100

        # Set data
        pie.data = [high_risk, medium_risk, low_risk]
        pie.labels = ['High', 'Medium', 'Low']

        # Set colors
        pie.slices.strokeWidth = 0.5
        pie.slices[0].fillColor = colors.red
        pie.slices[1].fillColor = colors.orange
        pie.slices[2].fillColor = colors.green

        # Add to drawing
        drawing.add(pie)

        # Add to document
        elements.append(drawing)
        elements.append(Spacer(1, 0.25 * inch))

        # Add assessment listing
        elements.append(Paragraph("Assessments", self.styles['Heading2']))

        # Create table for assessments
        assessment_data = [["ID", "Title", "Date", "Risk Level", "Score"]]
        for assessment in assessments:
            risk_level = assessment.risk_level or "N/A"
            if risk_level == "High":
                risk_cell = Paragraph(risk_level, self.styles["RiskHigh"])
            elif risk_level == "Medium":
                risk_cell = Paragraph(risk_level, self.styles["RiskMedium"])
            elif risk_level == "Low":
                risk_cell = Paragraph(risk_level, self.styles["RiskLow"])
            else:
                risk_cell = risk_level

            assessment_date = assessment.assessment_date
            if hasattr(assessment_date, "strftime"):
                date_str = assessment_date.strftime("%Y-%m-%d")
            else:
                date_str = "N/A"

            score_str = f"{assessment.risk_score:.1f}" if assessment.risk_score is not None else "N/A"

            assessment_data.append([
                assessment.id,
                assessment.title,
                date_str,
                risk_cell,
                score_str
            ])

        if len(assessment_data) > 1:  # If we have any assessments
            assessment_table = Table(assessment_data,
                                     colWidths=[0.75 * inch, 2.5 * inch, 1 * inch, 1 * inch, 0.75 * inch])
            assessment_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(assessment_table)
        else:
            elements.append(Paragraph("No assessments available", self.styles['Normal']))

        # Build the PDF
        doc.build(elements)

        return filename

    def generate_summary_report(self, assessments):
        """Generate an overall summary report of all assessments.

        Args:
            assessments: List of all assessments

        Returns:
            str: Path to the generated PDF file
        """
        # Generate filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.output_dir}/Summary_Report_{timestamp}.pdf"

        # Create the PDF document
        doc = SimpleDocTemplate(
            filename,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        # Container for the elements to be added to the document
        elements = []

        # Add title and date
        elements.append(Paragraph("Risk Assessment Summary Report", self.styles['Title']))
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        elements.append(Paragraph(f"Generated on: {current_date}", self.styles['Normal']))
        elements.append(Spacer(1, 0.25 * inch))

        # Add overall statistics
        elements.append(Paragraph("Overall Risk Statistics", self.styles['Heading2']))

        # Calculate overall statistics
        total_assessments = len(assessments)
        high_risk = sum(1 for a in assessments if a.risk_level == "High")
        medium_risk = sum(1 for a in assessments if a.risk_level == "Medium")
        low_risk = sum(1 for a in assessments if a.risk_level == "Low")
        avg_score = sum(a.risk_score for a in assessments if
                        a.risk_score is not None) / total_assessments if total_assessments > 0 else 0

        # Get unique departments
        departments = set()
        for assessment in assessments:
            if assessment.department:
                departments.add(assessment.department)

        # Add overall statistics table
        stats_data = [
            ["Total Assessments", str(total_assessments)],
            ["High Risk", str(high_risk)],
            ["Medium Risk", str(medium_risk)],
            ["Low Risk", str(low_risk)],
            ["Average Risk Score", f"{avg_score:.2f}"],
            ["Departments Assessed", str(len(departments))]
        ]

        stats_table = Table(stats_data, colWidths=[2.5 * inch, 1.5 * inch])
        stats_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(stats_table)
        elements.append(Spacer(1, 0.25 * inch))

        # Add risk by department if we have departments
        if departments:
            elements.append(Paragraph("Risk by Department", self.styles['Heading2']))

            # Collect data by department
            dept_data = []
            for dept in sorted(departments):
                dept_assessments = [a for a in assessments if a.department == dept]
                dept_high = sum(1 for a in dept_assessments if a.risk_level == "High")
                dept_medium = sum(1 for a in dept_assessments if a.risk_level == "Medium")
                dept_low = sum(1 for a in dept_assessments if a.risk_level == "Low")
                dept_avg = sum(a.risk_score for a in dept_assessments if a.risk_score is not None) / len(
                    dept_assessments) if dept_assessments else 0

                # Calculate overall risk rating for department
                if dept_high > 0:
                    risk_cell = Paragraph("High", self.styles["RiskHigh"])
                elif dept_medium > 0:
                    risk_cell = Paragraph("Medium", self.styles["RiskMedium"])
                else:
                    risk_cell = Paragraph("Low", self.styles["RiskLow"])

                dept_data.append([
                    dept,
                    str(len(dept_assessments)),
                    str(dept_high),
                    str(dept_medium),
                    str(dept_low),
                    f"{dept_avg:.2f}",
                    risk_cell
                ])

            # Create department table
            if dept_data:
                dept_table_data = [["Department", "Assessments", "High", "Medium", "Low", "Avg Score", "Overall"]]
                dept_table_data.extend(dept_data)

                dept_table = Table(dept_table_data,
                                   colWidths=[1.3 * inch, 1 * inch, 0.6 * inch, 0.75 * inch, 0.6 * inch, 0.75 * inch,
                                              0.75 * inch])
                dept_table.setStyle(TableStyle([
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('PADDING', (0, 0), (-1, -1), 6),
                ]))
                elements.append(dept_table)
            else:
                elements.append(Paragraph("No department data available", self.styles['Normal']))

            elements.append(Spacer(1, 0.25 * inch))

        # Add recent assessments (last 5)
        elements.append(Paragraph("Recent Assessments", self.styles['Heading2']))

        # Sort by date
        sorted_assessments = sorted(
            [a for a in assessments if hasattr(a.assessment_date, 'strftime')],
            key=lambda x: x.assessment_date,
            reverse=True
        )

        recent_assessments = sorted_assessments[:5]

        # Create table for recent assessments
        recent_data = [["ID", "Title", "Department", "Date", "Risk Level"]]
        for assessment in recent_assessments:
            risk_level = assessment.risk_level or "N/A"
            if risk_level == "High":
                risk_cell = Paragraph(risk_level, self.styles["RiskHigh"])
            elif risk_level == "Medium":
                risk_cell = Paragraph(risk_level, self.styles["RiskMedium"])
            elif risk_level == "Low":
                risk_cell = Paragraph(risk_level, self.styles["RiskLow"])
            else:
                risk_cell = risk_level

            date_str = assessment.assessment_date.strftime("%Y-%m-%d")

            recent_data.append([
                assessment.id,
                assessment.title,
                assessment.department or "N/A",
                date_str,
                risk_cell
            ])

        if len(recent_data) > 1:  # If we have any recent assessments
            recent_table = Table(recent_data, colWidths=[0.6 * inch, 2.4 * inch, 1.2 * inch, 0.9 * inch, 0.9 * inch])
            recent_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(recent_table)
        else:
            elements.append(Paragraph("No recent assessments available", self.styles['Normal']))

        # Add high risk assessments
        elements.append(Spacer(1, 0.25 * inch))
        elements.append(Paragraph("High Risk Assessments", self.styles['Heading2']))

        high_risk_assessments = [a for a in assessments if a.risk_level == "High"]

        # Create table for high risk assessments
        high_risk_data = [["ID", "Title", "Department", "Date", "Score"]]
        for assessment in high_risk_assessments:
            date_str = assessment.assessment_date.strftime("%Y-%m-%d") if hasattr(assessment.assessment_date,
                                                                                  'strftime') else "N/A"
            score_str = f"{assessment.risk_score:.1f}" if assessment.risk_score is not None else "N/A"

            high_risk_data.append([
                assessment.id,
                assessment.title,
                assessment.department or "N/A",
                date_str,
                score_str
            ])

        if len(high_risk_data) > 1:  # If we have any high risk assessments
            high_risk_table = Table(high_risk_data,
                                    colWidths=[0.6 * inch, 2.4 * inch, 1.2 * inch, 0.9 * inch, 0.9 * inch])
            high_risk_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(high_risk_table)
        else:
            elements.append(Paragraph("No high risk assessments identified", self.styles['Normal']))

        # Build the PDF
        doc.build(elements)

        return filename
