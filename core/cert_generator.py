"""
Nirman-Drishti DPI Audit Certificate Generator
Generates an official tamper-evident PDF inspection report for District Collector / PFMS.
"""

import os
from datetime import datetime
from .models import ProjectTender, ContractorClaim, ForensicAuditResult


def generate_pdf_certificate(
    tender: ProjectTender,
    claim: ContractorClaim,
    audit: ForensicAuditResult,
    output_dir: str = "generated_certs"
) -> str:
    """
    Generates a formal Government of India style audit certificate in PDF format.
    Returns file path to generated PDF.
    """
    os.makedirs(output_dir, exist_ok=True)
    pdf_filename = os.path.join(output_dir, f"Audit_Cert_{audit.audit_id}.pdf")

    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors

        doc = SimpleDocTemplate(
            pdf_filename,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "GovTitle",
            parent=styles["Heading1"],
            fontSize=16,
            leading=20,
            alignment=1,  # Center
            textColor=colors.HexColor("#0f2a4a"),
        )
        subtitle_style = ParagraphStyle(
            "GovSubtitle",
            parent=styles["Normal"],
            fontSize=10,
            alignment=1,
            textColor=colors.HexColor("#555555"),
        )
        body_style = styles["Normal"]
        bold_style = ParagraphStyle("Bold", parent=body_style, fontName="Helvetica-Bold")

        story = []

        # Header
        story.append(Paragraph("<b>GOVERNMENT OF INDIA / STATE PUBLIC WORKS DEPARTMENT</b>", title_style))
        story.append(Paragraph("DIRECTORATE OF INFRASTRUCTURE AUDIT & DIGITAL VIGILANCE", subtitle_style))
        story.append(Paragraph("NIRMAN-DRISHTI AUTONOMOUS FORENSIC INSPECTION CERTIFICATE", subtitle_style))
        story.append(Spacer(1, 15))

        # Verdict Banner Color
        if audit.verdict == "APPROVED":
            banner_color = colors.HexColor("#1b5e20")
            banner_text = f"VERDICT: APPROVED FOR DISBURSEMENT (Risk Score: {audit.risk_score}/100)"
        elif audit.verdict == "FLAGGED_FOR_VIGILANCE":
            banner_color = colors.HexColor("#e65100")
            banner_text = f"VERDICT: FLAGGED FOR VIGILANCE SCRUTINY (Risk Score: {audit.risk_score}/100)"
        else:
            banner_color = colors.HexColor("#b71c1c")
            banner_text = f"VERDICT: REJECTED / CRITICAL FRAUD ALERT (Risk Score: {audit.risk_score}/100)"

        verdict_style = ParagraphStyle(
            "VerdictBanner",
            parent=styles["Normal"],
            fontSize=12,
            textColor=colors.white,
            alignment=1,
            fontName="Helvetica-Bold",
        )

        banner_table = Table([[Paragraph(banner_text, verdict_style)]], colWidths=[540])
        banner_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), banner_color),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))
        story.append(banner_table)
        story.append(Spacer(1, 15))

        # Project Details Table
        details_data = [
            [Paragraph("<b>Audit ID:</b>", body_style), Paragraph(audit.audit_id, body_style),
             Paragraph("<b>Date & Time:</b>", body_style), Paragraph(audit.timestamp[:19], body_style)],
            [Paragraph("<b>Project Tender:</b>", body_style), Paragraph(tender.project_name, body_style),
             Paragraph("<b>Scheme:</b>", body_style), Paragraph(tender.scheme, body_style)],
            [Paragraph("<b>Contractor:</b>", body_style), Paragraph(tender.contractor_name, body_style),
             Paragraph("<b>Department:</b>", body_style), Paragraph(tender.department, body_style)],
            [Paragraph("<b>Claim ID:</b>", body_style), Paragraph(claim.claim_id, body_style),
             Paragraph("<b>MB Reference:</b>", body_style), Paragraph(claim.measurement_book_ref, body_style)],
            [Paragraph("<b>Claimed Amount:</b>", body_style), Paragraph(f"₹{claim.claimed_amount_inr:,.2f}", bold_style),
             Paragraph("<b>Recommended Release:</b>", body_style), Paragraph(f"₹{audit.recommended_disbursement_inr:,.2f}", bold_style)],
            [Paragraph("<b>Flagged Overcharge:</b>", body_style), Paragraph(f"₹{audit.total_flagged_amount_inr:,.2f}", bold_style),
             Paragraph("<b>Geofence Status:</b>", body_style), Paragraph("VERIFIED (Within perimeter)" if audit.geospatial_verified else f"VIOLATION ({audit.distance_from_site_meters:.0f}m away)", body_style)],
        ]

        details_table = Table(details_data, colWidths=[120, 150, 120, 150])
        details_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#dddddd")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#eeeeee")),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(details_table)
        story.append(Spacer(1, 15))

        # Vision & Findings Section
        story.append(Paragraph("<b>FORENSIC VISION & GEOSPATIAL OBSERVATIONS:</b>", bold_style))
        story.append(Paragraph(f"• <b>Detected Physical Stage:</b> {audit.vision_stage_detected}", body_style))
        for obs in audit.vision_observations:
            story.append(Paragraph(f"• {obs}", body_style))
        story.append(Spacer(1, 10))

        # Discrepancies Table
        if audit.discrepancies:
            story.append(Paragraph("<b>AUDIT NON-CONFORMANCES & FINANCIAL DISCREPANCIES:</b>", bold_style))
            disc_rows = [[
                Paragraph("<b>Category</b>", bold_style),
                Paragraph("<b>Severity</b>", bold_style),
                Paragraph("<b>Description</b>", bold_style),
                Paragraph("<b>Flagged Amount</b>", bold_style),
            ]]
            for d in audit.discrepancies:
                disc_rows.append([
                    Paragraph(d.category, body_style),
                    Paragraph(d.severity, body_style),
                    Paragraph(d.description, body_style),
                    Paragraph(f"₹{d.financial_impact_inr:,.2f}", body_style),
                ])
            disc_table = Table(disc_rows, colWidths=[110, 70, 260, 100])
            disc_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f0f4f8")),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cccccc")),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e0e0e0")),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            story.append(disc_table)
            story.append(Spacer(1, 15))

        # Executive Recommendation Summary
        story.append(Paragraph("<b>EXECUTIVE RECOMMENDATION SUMMARY:</b>", bold_style))
        story.append(Paragraph(audit.recommendation_summary, body_style))
        story.append(Spacer(1, 15))

        # Cryptographic DPI Hash
        story.append(Paragraph("<b>DIGITAL TAMPER-EVIDENT AUDIT SEAL (DPI / DEPA / DIGILOCKER):</b>", bold_style))
        story.append(Paragraph(f"<code>SHA256: {audit.audit_hash}</code>", body_style))
        story.append(Paragraph("<i>This document is algorithmically generated and cryptographically verifiable on the Nirman-Drishti Public Ledger.</i>", subtitle_style))

        doc.build(story)
        return pdf_filename

    except ImportError:
        # Fallback if reportlab is still installing
        txt_filename = os.path.join(output_dir, f"Audit_Cert_{audit.audit_id}.txt")
        with open(txt_filename, "w") as f:
            f.write(f"=== NIRMAN-DRISHTI AUDIT CERTIFICATE ===\n")
            f.write(f"Audit ID: {audit.audit_id}\n")
            f.write(f"Verdict: {audit.verdict}\n")
            f.write(f"Risk Score: {audit.risk_score}/100\n")
            f.write(f"Summary: {audit.recommendation_summary}\n")
            f.write(f"Audit Hash: {audit.audit_hash}\n")
        return txt_filename
