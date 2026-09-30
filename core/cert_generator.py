"""
Nirman-Drishti DPI Audit Certificate Generator
Generates an official tamper-evident PDF inspection report for District Collector / PFMS.
Includes the Lion Capital of Ashoka and sanitizes all currency characters to prevent tofu boxes.
"""

import os
from datetime import datetime
from .models import ProjectTender, ContractorClaim, ForensicAuditResult


def clean_pdf_text(val: any) -> str:
    """
    Sanitizes strings for standard Type-1 PDF fonts.
    Replaces Unicode Rupee symbol ₹ with 'Rs. ' to avoid square/tofu glyph rendering.
    """
    if val is None:
        return ""
    text = str(val)
    # Replace Rupee symbol with standard INR/Rs. representation
    text = text.replace("₹", "Rs. ")
    return text


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
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors

        doc = SimpleDocTemplate(
            pdf_filename,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=28,
            bottomMargin=28
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "GovTitle",
            parent=styles["Heading1"],
            fontSize=15,
            leading=18,
            alignment=1,  # Center
            textColor=colors.HexColor("#0f2a4a"),
        )
        subtitle_style = ParagraphStyle(
            "GovSubtitle",
            parent=styles["Normal"],
            fontSize=9.5,
            leading=13,
            alignment=1,
            textColor=colors.HexColor("#334155"),
        )
        body_style = styles["Normal"]
        bold_style = ParagraphStyle("Bold", parent=body_style, fontName="Helvetica-Bold")

        story = []

        # 1. Official State Emblem of India (Lion Capital of Ashoka) in the Middle
        emblem_candidates = [
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "assets", "emblem_of_india.png"),
            os.path.join("data", "assets", "emblem_of_india.png"),
        ]
        for candidate in emblem_candidates:
            if os.path.exists(candidate):
                emblem = RLImage(candidate, width=44, height=70)
                emblem.hAlign = "CENTER"
                story.append(emblem)
                story.append(Spacer(1, 4))
                break

        # 2. Header
        story.append(Paragraph("<b>GOVERNMENT OF INDIA</b>", title_style))
        story.append(Paragraph("STATE PUBLIC WORKS DEPARTMENT &bull; DIRECTORATE OF DIGITAL VIGILANCE", subtitle_style))
        story.append(Paragraph("<b>NIRMAN-DRISHTI AUTONOMOUS FORENSIC INSPECTION CERTIFICATE</b>", subtitle_style))
        story.append(Spacer(1, 10))

        # 3. Verdict Banner Color
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
            fontSize=11,
            textColor=colors.white,
            alignment=1,
            fontName="Helvetica-Bold",
        )

        banner_table = Table([[Paragraph(banner_text, verdict_style)]], colWidths=[540])
        banner_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), banner_color),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))
        story.append(banner_table)
        story.append(Spacer(1, 12))

        # 4. Project Details Table (All texts and currencies sanitized)
        claimed_amt_str = f"Rs. {claim.claimed_amount_inr:,.2f}"
        rec_amt_str = f"Rs. {audit.recommended_disbursement_inr:,.2f}"
        flagged_amt_str = f"Rs. {audit.total_flagged_amount_inr:,.2f}"
        geofence_str = "VERIFIED (Within perimeter)" if audit.geospatial_verified else f"VIOLATION ({audit.distance_from_site_meters:.0f}m away)"

        details_data = [
            [Paragraph("<b>Audit ID:</b>", body_style), Paragraph(clean_pdf_text(audit.audit_id), body_style),
             Paragraph("<b>Date & Time:</b>", body_style), Paragraph(clean_pdf_text(audit.timestamp[:19]), body_style)],
            [Paragraph("<b>Project Tender:</b>", body_style), Paragraph(clean_pdf_text(tender.project_name), body_style),
             Paragraph("<b>Scheme:</b>", body_style), Paragraph(clean_pdf_text(tender.scheme), body_style)],
            [Paragraph("<b>Contractor:</b>", body_style), Paragraph(clean_pdf_text(tender.contractor_name), body_style),
             Paragraph("<b>Department:</b>", body_style), Paragraph(clean_pdf_text(tender.department), body_style)],
            [Paragraph("<b>Claim ID:</b>", body_style), Paragraph(clean_pdf_text(claim.claim_id), body_style),
             Paragraph("<b>MB Reference:</b>", body_style), Paragraph(clean_pdf_text(claim.measurement_book_ref), body_style)],
            [Paragraph("<b>Claimed Amount:</b>", body_style), Paragraph(claimed_amt_str, bold_style),
             Paragraph("<b>Recommended Release:</b>", body_style), Paragraph(rec_amt_str, bold_style)],
            [Paragraph("<b>Flagged Overcharge:</b>", body_style), Paragraph(flagged_amt_str, bold_style),
             Paragraph("<b>Geofence Status:</b>", body_style), Paragraph(geofence_str, body_style)],
        ]

        details_table = Table(details_data, colWidths=[120, 150, 120, 150])
        details_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#dddddd")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#eeeeee")),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(details_table)
        story.append(Spacer(1, 12))

        # 5. Vision & Findings Section
        story.append(Paragraph("<b>FORENSIC VISION & GEOSPATIAL OBSERVATIONS:</b>", bold_style))
        story.append(Paragraph(f"&bull; <b>Detected Physical Stage:</b> {clean_pdf_text(audit.vision_stage_detected)}", body_style))
        for obs in audit.vision_observations:
            story.append(Paragraph(f"&bull; {clean_pdf_text(obs)}", body_style))
        story.append(Spacer(1, 8))

        # 6. Discrepancies Table
        if audit.discrepancies:
            story.append(Paragraph("<b>AUDIT NON-CONFORMANCES & FINANCIAL DISCREPANCIES:</b>", bold_style))
            disc_rows = [[
                Paragraph("<b>Category</b>", bold_style),
                Paragraph("<b>Severity</b>", bold_style),
                Paragraph("<b>Description</b>", bold_style),
                Paragraph("<b>Flagged Amount</b>", bold_style),
            ]]
            for d in audit.discrepancies:
                disc_amt_str = f"Rs. {d.financial_impact_inr:,.2f}"
                disc_rows.append([
                    Paragraph(clean_pdf_text(d.category), body_style),
                    Paragraph(clean_pdf_text(d.severity), body_style),
                    Paragraph(clean_pdf_text(d.description), body_style),
                    Paragraph(disc_amt_str, body_style),
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
            story.append(Spacer(1, 12))

        # 7. Executive Recommendation Summary
        story.append(Paragraph("<b>EXECUTIVE RECOMMENDATION SUMMARY:</b>", bold_style))
        story.append(Paragraph(clean_pdf_text(audit.recommendation_summary), body_style))
        story.append(Spacer(1, 12))

        # 8. Cryptographic DPI Hash
        story.append(Paragraph("<b>DIGITAL TAMPER-EVIDENT AUDIT SEAL (DPI / DEPA / DIGILOCKER):</b>", bold_style))
        story.append(Paragraph(f"<code>SHA256: {audit.audit_hash}</code>", body_style))
        story.append(Paragraph("<i>This document is algorithmically generated and cryptographically verifiable on the Nirman-Drishti Public Ledger.</i>", subtitle_style))

        doc.build(story)
        return pdf_filename

    except ImportError:
        # Fallback if reportlab is still installing
        txt_filename = os.path.join(output_dir, f"Audit_Cert_{audit.audit_id}.txt")
        with open(txt_filename, "w") as f:
            f.write("=== NIRMAN-DRISHTI AUDIT CERTIFICATE ===\n")
            f.write(f"Audit ID: {audit.audit_id}\n")
            f.write(f"Verdict: {audit.verdict}\n")
            f.write(f"Risk Score: {audit.risk_score}/100\n")
            f.write(f"Summary: {clean_pdf_text(audit.recommendation_summary)}\n")
            f.write(f"Audit Hash: {audit.audit_hash}\n")
        return txt_filename
