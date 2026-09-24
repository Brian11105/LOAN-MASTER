# app/utils/user_pdf_generator.py
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime


class UserReportGenerator:
    @staticmethod
    def generate_user_report(user, loans, payments, risk_score, crb_score, crb_rating, filename):
        """Generate a PDF report for a user's loans and payments"""
        
        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#0A6E4A'),
            alignment=TA_CENTER,
            spaceAfter=10
        )
        
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.grey,
            alignment=TA_CENTER,
            spaceAfter=20
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=13,
            textColor=colors.HexColor('#0A6E4A'),
            spaceAfter=10
        )
        
        # Title
        story.append(Paragraph("LOAN MASTER - USER STATEMENT", title_style))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", subtitle_style))
        story.append(Spacer(1, 10))
        
        # User Information
        story.append(Paragraph("1. USER INFORMATION", heading_style))
        
        user_data = [
            ['Full Name', user.full_name],
            ['Username', user.username],
            ['Email', user.email],
            ['Phone Number', user.phone_number],
            ['ID Number', user.id_number],
            ['Date Registered', user.date_registered.strftime('%Y-%m-%d') if user.date_registered else 'N/A'],
        ]
        
        user_table = Table(user_data, colWidths=[2*inch, 3.5*inch])
        user_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#0A6E4A')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(user_table)
        story.append(Spacer(1, 15))
        
        # Account Summary
        story.append(Paragraph("2. ACCOUNT SUMMARY", heading_style))
        
        total_loans = len(loans)
        active_loans = len([l for l in loans if l.status == 'ACTIVE'])
        total_borrowed = sum(l.loan_amount for l in loans if l.status in ['ACTIVE', 'COMPLETED'])
        pending_repayments = sum(l.monthly_installment for l in loans if l.status == 'ACTIVE')
        
        summary_data = [
            ['Metric', 'Value'],
            ['Total Loans', str(total_loans)],
            ['Active Loans', str(active_loans)],
            ['Total Borrowed', f"KSh {total_borrowed:,.2f}"],
            ['Pending Repayments', f"KSh {pending_repayments:,.2f}"],
            ['Risk Score', f"{risk_score}%"],
            ['CRB Score', f"{crb_score} ({crb_rating})"],
        ]
        
        summary_table = Table(summary_data, colWidths=[2.5*inch, 3*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0A6E4A')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 15))
        
        # Your Loans
        story.append(Paragraph("3. YOUR LOANS", heading_style))
        
        if loans:
            loans_data = [
                ['Loan ID', 'Amount (KSh)', 'Period', 'Monthly (KSh)', 'Status', 'Risk Score']
            ]
            
            for loan in loans:
                loans_data.append([
                    f"#{loan.id}",
                    f"{loan.loan_amount:,.2f}",
                    f"{loan.loan_period} months",
                    f"{loan.monthly_installment:,.2f}",
                    loan.status,
                    f"{loan.risk_score}%"
                ])
            
            loans_table = Table(loans_data, colWidths=[0.8*inch, 1.3*inch, 1.0*inch, 1.3*inch, 1.0*inch, 0.9*inch])
            loans_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0A6E4A')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            story.append(loans_table)
        else:
            story.append(Paragraph("No loans found.", styles['Normal']))
        
        story.append(Spacer(1, 15))
        
        # Recent Payments
        story.append(Paragraph("4. RECENT PAYMENTS", heading_style))
        
        if payments:
            payments_data = [
                ['Date', 'Amount (KSh)', 'Status', 'Receipt Number']
            ]
            
            for payment in payments:
                payments_data.append([
                    payment.payment_date.strftime('%Y-%m-%d') if payment.payment_date else 'N/A',
                    f"{payment.amount:,.2f}",
                    payment.status,
                    payment.receipt_number or 'N/A'
                ])
            
            payments_table = Table(payments_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 2.0*inch])
            payments_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0A6E4A')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            story.append(payments_table)
        else:
            story.append(Paragraph("No payments found.", styles['Normal']))
        
        # Footer
        story.append(Spacer(1, 30))
        story.append(Paragraph("_" * 80, styles['Normal']))
        story.append(Paragraph("Loan Master - User Statement", styles['Normal']))
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d')}", styles['Normal']))
        story.append(Paragraph("© 2026 Loan Master. All rights reserved.", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        return filename