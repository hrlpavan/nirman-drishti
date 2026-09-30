"""
Generate Nirman-Drishti Presentation Deck (Landscape PDF) for Hack2Skill submission.
"""

import os
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def create_presentation_deck(output_path="Nirman_Drishti_Presentation_Deck.pdf"):
    # Landscape Letter: 11 x 8.5 inches (792 x 612 pt)
    doc = SimpleDocTemplate(
        output_path,
        pagesize=landscape(letter),
        leftMargin=40,
        rightMargin=40,
        topMargin=35,
        bottomMargin=35
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "SlideTitle",
        parent=styles["Heading1"],
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#0f2a4a"),
        spaceAfter=15,
        alignment=0
    )
    
    cover_title = ParagraphStyle(
        "CoverTitle",
        parent=styles["Heading1"],
        fontSize=32,
        leading=38,
        textColor=colors.HexColor("#0f2a4a"),
        alignment=1,
        spaceAfter=10
    )

    cover_subtitle = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontSize=15,
        leading=20,
        textColor=colors.HexColor("#334155"),
        alignment=1,
        spaceAfter=25
    )

    meta_style = ParagraphStyle(
        "CoverMeta",
        parent=styles["Normal"],
        fontSize=11,
        leading=16,
        textColor=colors.HexColor("#64748b"),
        alignment=1
    )

    heading2 = ParagraphStyle(
        "Heading2",
        parent=styles["Heading2"],
        fontSize=15,
        leading=19,
        textColor=colors.HexColor("#1e3a8a"),
        spaceAfter=8
    )

    body = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#1e293b")
    )

    bullet_style = ParagraphStyle(
        "Bullet",
        parent=body,
        leftIndent=15,
        spaceAfter=6
    )

    story = []

    emblem_path = "data/assets/emblem_of_india.png"

    # ==================== SLIDE 1: COVER SLIDE ====================
    story.append(Spacer(1, 40))
    if os.path.exists(emblem_path):
        emblem = RLImage(emblem_path, width=45, height=72)
        emblem.hAlign = 'CENTER'
        story.append(emblem)
        story.append(Spacer(1, 15))

    story.append(Paragraph("<b>NIRMAN-DRISHTI (निर्माण-दृष्टि)</b>", cover_title))
    story.append(Paragraph("Autonomous Multimodal Forensic Audit Engine for Public Infrastructure & Civic Works", cover_subtitle))
    
    meta_text = (
        "<b>Event:</b> Build with AI: Code for Communities 2.0 (Google Cloud & Hack2Skill)<br/>"
        "<b>Track:</b> Track 1 — AI for Digital Public Infrastructure & Governance<br/>"
        "<b>Target Users:</b> District Magistrates (DMs), Vigilance Officers, Members of Parliament (MPs)"
    )
    story.append(Paragraph(meta_text, meta_style))
    story.append(PageBreak())

    # ==================== SLIDE 2: THE PROBLEM ====================
    story.append(Paragraph("<b>The Problem: The Rs. 10 Lakh Crore Leak in Public Works</b>", title_style))
    story.append(Paragraph(
        "India spends over <b>Rs. 10 Lakh Crore ($120B+)</b> annually on rural and urban infrastructure (PMGSY roads, Jal Jeevan Mission drinking water, MPLADS community facilities). However, physical verification before treasury disbursement is completely manual.",
        body
    ))
    story.append(Spacer(1, 15))

    prob_data = [
        [
            Paragraph("<b>1. Recycled / Staged Evidence</b>", heading2),
            Paragraph("<b>2. Ghost Roads & Distance Violations</b>", heading2),
            Paragraph("<b>3. Schedule of Rates (SoR) Inflation</b>", heading2)
        ],
        [
            Paragraph("Contractors submit photos of older completed roads or adjacent projects to claim milestone payouts before actual execution.", body),
            Paragraph("Funds drawn for unexecuted works or projects executed kilometers away from the sanctioned alignment with no geo-verification.", body),
            Paragraph("Invoices billed at inflated rates above government ceilings (e.g. Bitumen billed at Rs. 88k/MT vs Rs. 65k/MT approved SoR).", body)
        ]
    ]
    t_prob = Table(prob_data, colWidths=[230, 230, 230])
    t_prob.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('PADDING', (0,0), (-1,-1), 12),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    story.append(t_prob)
    story.append(PageBreak())

    # ==================== SLIDE 3: THE SOLUTION ====================
    story.append(Paragraph("<b>The Solution: Nirman-Drishti Core AI Engine</b>", title_style))
    story.append(Paragraph(
        "Nirman-Drishti functions as an automated digital vigilance auditor that runs <b>3 instant multimodal checks in under 5 seconds</b> before any public money leaves the exchequer.",
        body
    ))
    story.append(Spacer(1, 15))

    sol_data = [
        [
            Paragraph("<b>Check 1: Geospatial Audit</b>", heading2),
            Paragraph("<b>Check 2: Gemini 2.0 Vision</b>", heading2),
            Paragraph("<b>Check 3: Rate Reconciliation</b>", heading2)
        ],
        [
            Paragraph("• Haversine distance calculation from tender coordinates.<br/>• Extracts EXIF metadata directly from evidence image.<br/>• Flags geofence perimeter breaches.", body),
            Paragraph("• Gemini Multimodal Vision stage detection.<br/>• Identifies raw gravel (WBM) vs finished bituminous wear coat.<br/>• Flags structural defects & missing layers.", body),
            Paragraph("• Line-by-line comparison with State Schedule of Rates.<br/>• Quantity ceiling verification against sanction.<br/>• Flags phantom/unsanctioned items automatically.", body)
        ]
    ]
    t_sol = Table(sol_data, colWidths=[230, 230, 230])
    t_sol.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f0fdf4")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#bbf7d0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#dcfce7")),
        ('PADDING', (0,0), (-1,-1), 12),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    story.append(t_sol)
    story.append(PageBreak())

    # ==================== SLIDE 4: BENCHMARK RESULTS ====================
    story.append(Paragraph("<b>Real-World Benchmark Results (Demonstrated Cases)</b>", title_style))
    story.append(Paragraph("Nirman-Drishti was tested against realistic public works claims across multiple government schemes:", body))
    story.append(Spacer(1, 12))

    case_data = [
        [Paragraph("<b>Scenario / Tender</b>", heading2), Paragraph("<b>Claimed Amount</b>", heading2), Paragraph("<b>AI Forensic Findings</b>", heading2), Paragraph("<b>Verdict</b>", heading2)],
        [
            Paragraph("<b>PMGSY Rural Road</b><br/>(Honnavar to Karki, 1.8km)", body),
            Paragraph("Rs. 48.0 Lakhs", body),
            Paragraph("• Photo taken 11.5 km outside tender geofence.<br/>• Visual evidence shows raw gravel (tar missing).<br/>• Bitumen billed at Rs. 88k/MT vs Rs. 65k/MT SoR.<br/>• Phantom item of Rs. 2.25L detected.", body),
            Paragraph("<b>REJECTED</b><br/>Risk: 100/100<br/><b>Saved: Rs. 48 Lakhs</b>", body)
        ],
        [
            Paragraph("<b>Jal Jeevan Mission</b><br/>(Solar Pump, PHC Shirwal)", body),
            Paragraph("Rs. 14.5 Lakhs", body),
            Paragraph("• GPS coordinates matched within 28 meters.<br/>• Solar array, 5HP pump, and tank verified operational.<br/>• Line-item rates match approved SoR exactly.", body),
            Paragraph("<b>APPROVED</b><br/>Risk: 0/100<br/>Disbursed: Rs. 14.5L", body)
        ],
        [
            Paragraph("<b>MPLADS Community Center</b><br/>(Najafgarh Skill Center)", body),
            Paragraph("Rs. 32.5 Lakhs", body),
            Paragraph("• Frame stage verified on site.<br/>• Rate inflation detected on RCC M25 concrete (billed Rs. 8,200 vs Rs. 6,400 approved).", body),
            Paragraph("<b>VIGILANCE HOLD</b><br/>Risk: 15/100<br/>Withheld: Rs. 3.15L", body)
        ]
    ]
    t_case = Table(case_data, colWidths=[150, 95, 330, 115])
    t_case.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f2a4a")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    story.append(t_case)
    story.append(PageBreak())

    # ==================== SLIDE 5: ARCHITECTURE & TECH STACK ====================
    story.append(Paragraph("<b>System Architecture & Google Tech Stack</b>", title_style))
    story.append(Spacer(1, 10))

    arch_data = [
        [Paragraph("<b>Component Layer</b>", heading2), Paragraph("<b>Technologies Used</b>", heading2), Paragraph("<b>Functional Role</b>", heading2)],
        [
            Paragraph("<b>Multimodal AI Layer</b>", body),
            Paragraph("Google Gemini 2.0 Flash / Pro API", body),
            Paragraph("Spatial vision inspection, layer identification, and automated discrepancy explanation.", body)
        ],
        [
            Paragraph("<b>Geospatial Layer</b>", body),
            Paragraph("Google Maps / OpenStreetMap / Folium", body),
            Paragraph("GIS mapping of constituency tenders, geofencing, and distance offset verification.", body)
        ],
        [
            Paragraph("<b>Administrative Cockpit</b>", body),
            Paragraph("Streamlit, Python, HTML/CSS Engine", body),
            Paragraph("Dual-theme (Light/Dark) operational dashboard for District Collectors and MPs.", body)
        ],
        [
            Paragraph("<b>DPI & Trust Layer</b>", body),
            Paragraph("ReportLab, SHA-256 Cryptographic Engine", body),
            Paragraph("Official Government of India PDF inspection certificates with cryptographic tamper seals.", body)
        ]
    ]
    t_arch = Table(arch_data, colWidths=[160, 200, 330])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e3a8a")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('PADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    story.append(t_arch)
    story.append(PageBreak())

    # ==================== SLIDE 6: WHY IT WINS ====================
    story.append(Paragraph("<b>Strategic Value: Why Nirman-Drishti Wins</b>", title_style))
    story.append(Spacer(1, 10))

    why_data = [
        [
            Paragraph("<b>Direct Fit for Indian Governance</b>", heading2),
            Paragraph("<b>Zero-Competition Blue Ocean</b>", heading2),
            Paragraph("<b>Production-Grade Ready</b>", heading2)
        ],
        [
            Paragraph("Tailor-made for the authorities (District Magistrates, MPs, Vigilance Directors) evaluating the challenge.", body),
            Paragraph("Bypasses common 'pothole reporting chatbots' to solve the real trillion-rupee contracting and verification bottleneck.", body),
            Paragraph("Complete with 100% passing test assertions, official PDF certificate generation, and live dual-theme dashboard.", body)
        ]
    ]
    t_why = Table(why_data, colWidths=[230, 230, 230])
    t_why.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#eff6ff")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#bfdbfe")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#dbeafe")),
        ('PADDING', (0,0), (-1,-1), 12),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    story.append(t_why)
    story.append(Spacer(1, 30))

    story.append(Paragraph(
        "<b>Repository:</b> https://github.com/hrlpavan/nirman-drishti &bull; "
        "<b>Track:</b> AI for Digital Public Infrastructure & Governance",
        meta_style
    ))

    doc.build(story)
    print(f"Presentation deck created at: {output_path}")

if __name__ == "__main__":
    create_presentation_deck()
