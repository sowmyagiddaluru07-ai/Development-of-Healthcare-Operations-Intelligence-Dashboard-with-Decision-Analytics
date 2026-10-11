"""PDF Report Generator for Medical Operations Intelligence using ReportLab."""
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from analytics.kpi_engine import KPIEngine


class PDFReportGenerator:
    """Generates executive PDF reports from MongoDB metrics."""

    def __init__(self, db):
        self.db = db
        self.kpi_engine = KPIEngine(db)

    def generate_executive_report(self, output_path="reports/Executive_Operations_Report.pdf", facility_id=None):
        """Generate a complete executive PDF report."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        doc = SimpleDocTemplate(output_path, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor('#1a237e'), spaceAfter=12)
        subtitle_style = ParagraphStyle('SubTitleStyle', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#666666'), spaceAfter=20)
        h2_style = ParagraphStyle('H2Style', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#0d47a1'), spaceBefore=12, spaceAfter=8)

        story = []

        # Title Block
        story.append(Paragraph("Medical Operations Intelligence", title_style))
        story.append(Paragraph(f"Executive Operations Report | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", subtitle_style))
        story.append(Spacer(1, 10))

        # KPIs Section
        kpis = self.kpi_engine.get_executive_kpis(facility_id=facility_id)
        story.append(Paragraph("1. Key Operational Performance Indicators", h2_style))

        kpi_table_data = [
            ["Metric Name", "Current Value", "Metric Name", "Current Value"],
            ["Total Patients", f"{kpis.get('total_patients', 0):,}", "Total Revenue", f"${kpis.get('total_revenue', 0):,.2f}"],
            ["Bed Occupancy Rate", f"{kpis.get('bed_occupancy_rate', 0):.1f}%", "Avg Wait Time", f"{kpis.get('avg_waiting_time', 0):.0f} min"],
            ["Staff Utilization", f"{kpis.get('staff_utilization_rate', 0):.1f}%", "Claim Denial Rate", f"{kpis.get('claim_denial_rate', 0):.1f}%"],
            ["No-Show Rate", f"{kpis.get('no_show_rate', 0):.1f}%", "Operational Health Score", f"{kpis.get('operational_health_score', 0):.1f} / 100"]
        ]

        t = Table(kpi_table_data, colWidths=[140, 120, 140, 120])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f5f5f5')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
        ]))
        story.append(t)
        story.append(Spacer(1, 20))

        # Summary Paragraph
        story.append(Paragraph("2. Operational Health & Summary", h2_style))
        summary_text = (
            f"The overall operational health score for facility `{facility_id or 'All Facilities'}` stands at "
            f"<b>{kpis.get('operational_health_score', 85.0):.1f}%</b>. Total patient visits logged stand at "
            f"<b>{kpis.get('total_patients', 0):,}</b> generating <b>${kpis.get('total_revenue', 0):,.2f}</b> in billed revenue."
        )
        story.append(Paragraph(summary_text, styles['Normal']))

        doc.build(story)
        print(f"✅ Generated PDF report: {output_path}")
        return output_path
