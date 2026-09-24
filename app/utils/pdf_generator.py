# app/utils/pdf_generator.py
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import os


class PDFReportGenerator:
    @staticmethod
    def generate_risk_report(risk_metrics, high_risk_loans, medium_risk_loans, low_risk_loans, filename):
        """Generate a PDF risk assessment report"""
        
        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#0A6E4A'),
            alignment=TA_CENTER,
            spaceAfter=30
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#0A6E4A'),
            spaceAfter=12
        )
        
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.grey,
            alignment=TA_CENTER,
            spaceAfter=20
        )
        
        # Title
        story.append(Paragraph("LOAN MASTER - RISK ASSESSMENT REPORT", title_style))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", subtitle_style))
        story.append(Spacer(1, 20))
        
        # Summary Statistics
        story.append(Paragraph("1. SUMMARY STATISTICS", heading_style))
        
        summary_data = [
            ['Metric', 'Value'],
            ['Total Loans Analyzed', str(risk_metrics.get('total_loans', 0))],
            ['Average Risk Score', f"{risk_metrics.get('average_risk', 0):.1f}%"],
            ['Default Rate', f"{risk_metrics.get('default_rate', 0):.1f}%"],
            ['High Risk Loans', str(risk_metrics.get('high_risk', 0))],
            ['Medium Risk Loans', str(risk_metrics.get('medium_risk', 0))],
            ['Low Risk Loans', str(risk_metrics.get('low_risk', 0))],
        ]
        
        summary_table = Table(summary_data, colWidths=[2.5*inch, 2.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0A6E4A')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Risk Distribution
        story.append(Paragraph("2. RISK DISTRIBUTION", heading_style))
        
        total = risk_metrics.get('total_loans', 1)
        high_pct = (risk_metrics.get('high_risk', 0) / total * 100) if total > 0 else 0
        medium_pct = (risk_metrics.get('medium_risk', 0) / total * 100) if total > 0 else 0
        low_pct = (risk_metrics.get('low_risk', 0) / total * 100) if total > 0 else 0
        
        risk_distribution = [
            ['Risk Level', 'Count', 'Percentage'],
            ['High Risk', str(risk_metrics.get('high_risk', 0)), f"{high_pct:.1f}%"],
            ['Medium Risk', str(risk_metrics.get('medium_risk', 0)), f"{medium_pct:.1f}%"],
            ['Low Risk', str(risk_metrics.get('low_risk', 0)), f"{low_pct:.1f}%"],
        ]
        
        risk_table = Table(risk_distribution, colWidths=[1.5*inch, 1.5*inch, 1.5*inch])
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0A6E4A')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#C0392B')),
            ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#F39C12')),
            ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#2D7D46')),
            ('TEXTCOLOR', (0, 1), (-1, 1), colors.white),
            ('TEXTCOLOR', (0, 2), (-1, 2), colors.white),
            ('TEXTCOLOR', (0, 3), (-1, 3), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(risk_table)
        story.append(Spacer(1, 20))
        
        # High Risk Loans
        if high_risk_loans:
            story.append(Paragraph("3. HIGH RISK LOANS", heading_style))
            high_risk_data = [['ID', 'Borrower', 'Amount', 'Risk Score']]
            for loan in high_risk_loans[:10]:
                high_risk_data.append([
                    f"#{loan.id}",
                    loan.borrower.full_name,
                    f"KSh {loan.loan_amount:,.2f}",
                    f"{loan.risk_score}%"
                ])
            
            high_table = Table(high_risk_data, colWidths=[0.8*inch, 1.8*inch, 1.5*inch, 1.2*inch])
            high_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#C0392B')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(high_table)
            story.append(Spacer(1, 20))
        
        # Medium Risk Loans
        if medium_risk_loans:
            story.append(Paragraph("4. MEDIUM RISK LOANS", heading_style))
            medium_risk_data = [['ID', 'Borrower', 'Amount', 'Risk Score']]
            for loan in medium_risk_loans[:10]:
                medium_risk_data.append([
                    f"#{loan.id}",
                    loan.borrower.full_name,
                    f"KSh {loan.loan_amount:,.2f}",
                    f"{loan.risk_score}%"
                ])
            
            medium_table = Table(medium_risk_data, colWidths=[0.8*inch, 1.8*inch, 1.5*inch, 1.2*inch])
            medium_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F39C12')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(medium_table)
            story.append(Spacer(1, 20))
        
        # Footer
        story.append(Spacer(1, 30))
        story.append(Paragraph("_" * 80, styles['Normal']))
        story.append(Paragraph("Loan Master - Risk Assessment Report", styles['Normal']))
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d')}", styles['Normal']))
        story.append(Paragraph("© 2026 Loan Master. All rights reserved.", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        return filename