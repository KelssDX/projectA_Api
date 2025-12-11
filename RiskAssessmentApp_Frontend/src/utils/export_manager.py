import csv
import io
import base64
from datetime import datetime
try:
    import pandas as pd
except ImportError:
    pd = None
    print("Warning: pandas not found. Excel export will be disabled.")

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
except ImportError:
    colors = None
    print("Warning: reportlab not found. PDF export will be disabled.")

class ExportManager:
    """
    Handles export of data to CSV, Excel, and PDF formats.
    """

    @staticmethod
    def _get_timestamp():
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    @staticmethod
    def _encode_bytes(data_bytes):
        """Encodes bytes to base64 string"""
        return base64.b64encode(data_bytes).decode("utf-8")

    def export_csv(self, data, headers, filename_prefix="export", metadata=None):
        """
        Export data to CSV.
        
        Args:
            data (list[dict]): List of data items
            headers (list[str] or dict): Column headers (key -> label map or list of keys)
            filename_prefix (str): Prefix for the filename
            metadata (dict): Optional assessment header info
            
        Returns:
            dict: {"filename": str, "data_uri": str}
        """
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write metadata header if provided
        if metadata:
            writer.writerow(["Assessment Information"])
            for key, value in metadata.items():
                writer.writerow([key, value])
            writer.writerow([])  # Empty row separator
        
        # Determine header keys and labels
        if isinstance(headers, dict):
            keys = list(headers.keys())
            labels = list(headers.values())
        else:
            keys = headers
            labels = headers
            
        writer.writerow(labels)
        
        for item in data:
            row = [str(item.get(k, "")) for k in keys]
            writer.writerow(row)
            
        csv_bytes = output.getvalue().encode("utf-8")
        b64_data = self._encode_bytes(csv_bytes)
        filename = f"{filename_prefix}_{self._get_timestamp()}.csv"
        
        return {
            "filename": filename,
            "data_uri": f"data:application/octet-stream;base64,{b64_data}"
        }

    def export_excel(self, data, headers, title="Report", filename_prefix="export", metadata=None):
        """
        Export data to Excel (.xlsx).
        """
        if pd is None:
            raise ImportError("pandas library is required for Excel export.")
            
        output = io.BytesIO()
        
        # Prepare DataFrame
        if isinstance(headers, dict):
            df_data = [{headers.get(k, k): item.get(k, "") for k in headers} for item in data]
        else:
            df_data = [{k: item.get(k, "") for k in headers} for item in data]
            
        df = pd.DataFrame(df_data)
        
        # Write to Excel
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            sheet_name = title[:31] if title else "Report"
            
            # Write metadata first if provided
            if metadata:
                meta_df = pd.DataFrame(list(metadata.items()), columns=["Field", "Value"])
                meta_df.to_excel(writer, index=False, sheet_name=sheet_name, startrow=0)
                # Write data below metadata with gap
                start_row = len(metadata) + 3
                df.to_excel(writer, index=False, sheet_name=sheet_name, startrow=start_row)
            else:
                df.to_excel(writer, index=False, sheet_name=sheet_name)
            
        excel_bytes = output.getvalue()
        b64_data = self._encode_bytes(excel_bytes)
        filename = f"{filename_prefix}_{self._get_timestamp()}.xlsx"
        
        return {
            "filename": filename,
            "data_uri": f"data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64_data}"
        }

    def export_pdf(self, data, headers, title="Report", filename_prefix="export", metadata=None):
        """
        Export data to PDF using ReportLab.
        """
        if colors is None:
            raise ImportError("reportlab library is required for PDF export.")
            
        output = io.BytesIO()
        doc = SimpleDocTemplate(output, pagesize=landscape(letter))
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        elements.append(Paragraph(title, styles['Title']))
        elements.append(Spacer(1, 12))
        
        # Add metadata section if provided
        if metadata:
            elements.append(Paragraph("Assessment Information", styles['Heading2']))
            elements.append(Spacer(1, 6))
            meta_data = [[Paragraph(f"<b>{k}:</b>", styles['Normal']), Paragraph(str(v), styles['Normal'])] for k, v in metadata.items()]
            meta_table = Table(meta_data, colWidths=[150, 300])
            meta_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(meta_table)
            elements.append(Spacer(1, 20))
            elements.append(Paragraph("Risk Items", styles['Heading2']))
            elements.append(Spacer(1, 6))
        
        # Prepare Table Data
        if isinstance(headers, dict):
            keys = list(headers.keys())
            labels = list(headers.values())
        else:
            keys = headers
            labels = headers
            
        table_data = [labels]
        for item in data:
            row = [str(item.get(k, "")) for k in keys]
            wrapped_row = [Paragraph(str(val), styles['Normal']) for val in row]
            table_data.append(wrapped_row)
        
        t = Table(table_data, repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elements.append(t)
        doc.build(elements)
        
        pdf_bytes = output.getvalue()
        b64_data = self._encode_bytes(pdf_bytes)
        filename = f"{filename_prefix}_{self._get_timestamp()}.pdf"
        
        return {
            "filename": filename,
            "data_uri": f"data:application/pdf;base64,{b64_data}"
        }

