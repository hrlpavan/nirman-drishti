"""
Nirman-Drishti (निर्माण-दृष्टि)
Autonomous Multimodal Forensic Audit Engine for Public Infrastructure & Constituency Works
Streamlit Administrative Cockpit for District Collectors, MPs, and Vigilance Officers.
"""

import os
import json
import streamlit as st
import folium
from streamlit_folium import st_folium
from PIL import Image

from core.models import ProjectTender, ContractorClaim
from core.audit_engine import NirmanAuditEngine
from core.cert_generator import generate_pdf_certificate

# Set page configuration
st.set_page_config(
    page_title="Nirman-Drishti | AI Public Works Forensic Auditor",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Theme state management & custom styling
def get_theme_css(theme_mode: str) -> str:
    # Base adaptive styling using Streamlit native variables
    base_css = """
    <style>
        .main-header {
            font-size: 2.2rem;
            font-weight: 700;
            color: var(--text-color, #1e293b);
            margin-bottom: 0.2rem;
        }
        .sub-header {
            font-size: 1.05rem;
            color: var(--text-color, #475569);
            opacity: 0.85;
            margin-bottom: 1.5rem;
        }
        .metric-card {
            background-color: var(--secondary-background-color, #f8fafc);
            color: var(--text-color, #0f172a);
            border-radius: 8px;
            padding: 16px;
            border: 1px solid rgba(128, 128, 128, 0.2);
        }
        .status-badge-approved {
            background-color: rgba(34, 197, 94, 0.2);
            color: #22c55e;
            padding: 4px 12px;
            border-radius: 9999px;
            font-weight: 600;
            border: 1px solid rgba(34, 197, 94, 0.35);
        }
        .status-badge-rejected {
            background-color: rgba(239, 68, 68, 0.2);
            color: #ef4444;
            padding: 4px 12px;
            border-radius: 9999px;
            font-weight: 600;
            border: 1px solid rgba(239, 68, 68, 0.35);
        }
        .status-badge-vigilance {
            background-color: rgba(249, 115, 22, 0.2);
            color: #f97316;
            padding: 4px 12px;
            border-radius: 9999px;
            font-weight: 600;
            border: 1px solid rgba(249, 115, 22, 0.35);
        }
    </style>
    """
    if theme_mode == "🌙 Dark Mode":
        dark_override = """
        <style>
            :root {
                --background-color: #0e1117;
                --secondary-background-color: #1a1f2c;
                --text-color: #f1f5f9;
            }
            [data-testid="stAppViewContainer"] {
                background-color: #0e1117 !important;
                color: #f1f5f9 !important;
            }
            [data-testid="stSidebar"] {
                background-color: #141822 !important;
                color: #f1f5f9 !important;
            }
            .stMarkdown, p, span, label {
                color: #f1f5f9 !important;
            }
            .stMetricValue {
                color: #60a5fa !important;
            }
            div[data-testid="stMetric"] {
                background-color: #1a1f2c !important;
                border-radius: 8px;
                padding: 12px;
                border: 1px solid #2e384d;
            }
            .stTabs [data-baseweb="tab-list"] {
                background-color: #141822 !important;
                border-radius: 6px;
            }
            .stTabs [data-baseweb="tab"] {
                color: #cbd5e1 !important;
            }
            .stTabs [aria-selected="true"] {
                color: #60a5fa !important;
                border-bottom-color: #60a5fa !important;
            }
        </style>
        """
        return base_css + dark_override
    elif theme_mode == "☀️ Light Mode":
        light_override = """
        <style>
            :root {
                --background-color: #ffffff;
                --secondary-background-color: #f8fafc;
                --text-color: #0f172a;
            }
            [data-testid="stAppViewContainer"] {
                background-color: #ffffff !important;
                color: #0f172a !important;
            }
            [data-testid="stSidebar"] {
                background-color: #f1f5f9 !important;
                color: #0f172a !important;
            }
            .stMarkdown, p, span, label {
                color: #0f172a !important;
            }
            .stMetricValue {
                color: #1d4ed8 !important;
            }
            div[data-testid="stMetric"] {
                background-color: #f8fafc !important;
                border-radius: 8px;
                padding: 12px;
                border: 1px solid #e2e8f0;
            }
            .stTabs [data-baseweb="tab-list"] {
                background-color: #f1f5f9 !important;
                border-radius: 6px;
            }
            .stTabs [data-baseweb="tab"] {
                color: #475569 !important;
            }
            .stTabs [aria-selected="true"] {
                color: #1d4ed8 !important;
                border-bottom-color: #1d4ed8 !important;
            }
        </style>
        """
        return base_css + light_override
    else:
        # Auto / System theme adapts via standard CSS
        return base_css


@st.cache_data
def load_tenders():
    with open("data/tenders.json") as f:
        return [ProjectTender(**t) for t in json.load(f)]


@st.cache_data
def load_claims():
    with open("data/claims.json") as f:
        return [ContractorClaim(**c) for c in json.load(f)]


tenders_list = load_tenders()
claims_list = load_claims()
tender_dict = {t.tender_id: t for t in tenders_list}

# Sidebar - Settings & Mode
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/5/55/Emblem_of_India.svg", width=65)
    st.title("Nirman-Drishti")
    st.caption("Govt. of India DPI Forensic Infrastructure Auditor")
    st.markdown("---")

    st.markdown("### 🎨 Display Theme")
    theme_mode = st.radio(
        "Theme Mode",
        options=["🌓 Auto (System)", "☀️ Light Mode", "🌙 Dark Mode"],
        index=0,
        horizontal=False
    )
    st.markdown("---")

    api_key_input = st.text_input("Gemini API Key (Optional)", type="password", placeholder="Enter key for live vision")
    if api_key_input:
        os.environ["GEMINI_API_KEY"] = api_key_input
        st.success("Gemini API Key active!")
    else:
        st.info("Operating in Autonomous Rule & Forensic Verification Mode.")

    st.markdown("---")
    st.markdown("### 📋 Quick Claim Selector")
    claim_labels = {
        c.claim_id: f"{c.claim_id} ({c.tender_id}) - {c.milestone_name[:30]}..."
        for c in claims_list
    }
    selected_claim_id = st.selectbox(
        "Choose Claim to Audit:",
        options=list(claim_labels.keys()),
        format_func=lambda x: claim_labels[x],
        index=0
    )

    st.markdown("---")
    st.caption("Built for **Code for Communities 2.0** (Google Cloud & GDG)")

# Inject active theme stylesheet
st.markdown(get_theme_css(theme_mode), unsafe_allow_html=True)

selected_claim = next(c for c in claims_list if c.claim_id == selected_claim_id)
selected_tender = tender_dict[selected_claim.tender_id]
image_path = os.path.join("data/sample_images", selected_claim.photo_filename) if selected_claim.photo_filename else None

# Header Banner
st.markdown('<div class="main-header">🏛️ Nirman-Drishti (निर्माण-दृष्टि)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Autonomous Multimodal Forensic Audit Engine for Public Infrastructure & Constituency Works (MPLADS / PMGSY / JJM)</div>', unsafe_allow_html=True)

# Top Metrics Row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Sanctioned Budget", f"₹{sum(t.sanctioned_budget_inr for t in tenders_list)/1e5:,.1f} Lakhs")
with col2:
    st.metric("Active Civic Projects", len(tenders_list))
with col3:
    st.metric("Tender Under Audit", selected_tender.tender_id)
with col4:
    st.metric("Claimed Amount", f"₹{selected_claim.claimed_amount_inr/1e5:,.2f} Lakhs")

st.markdown("---")

# Main Audit Execution
audit_result = NirmanAuditEngine.audit_claim(selected_tender, selected_claim, image_path)

# Tabbed Interface
tab1, tab2, tab3 = st.tabs(["🔍 Forensic Audit & Evidence", "🗺️ Geospatial & Site Mapping", "📊 Bill of Quantities (BOQ) Reconciliation"])

with tab1:
    # Verdict Alert Banner
    if audit_result.verdict == "APPROVED":
        st.success(f"### ✅ {audit_result.verdict} — SAFE FOR DISBURSEMENT (Risk Score: {audit_result.risk_score}/100)")
    elif audit_result.verdict == "FLAGGED_FOR_VIGILANCE":
        st.warning(f"### ⚠️ {audit_result.verdict} — WITHHELD FOR EXECUTIVE SCRUTINY (Risk Score: {audit_result.risk_score}/100)")
    else:
        st.error(f"### 🚨 {audit_result.verdict} — CRITICAL FRAUD DETECTED (Risk Score: {audit_result.risk_score}/100)")

    st.write(f"**Recommendation Summary:** {audit_result.recommendation_summary}")

    col_img, col_forensic = st.columns([1, 1.2])

    with col_img:
        st.markdown("#### 📸 Contractor Submitted Site Photo")
        if image_path and os.path.exists(image_path):
            img = Image.open(image_path)
            st.image(img, use_container_width=True, caption=f"Evidence: {selected_claim.photo_filename}")
        else:
            st.info("No photographic evidence attached to this claim.")

        st.markdown("#### 🏛️ Project Details")
        st.write(f"**Project:** {selected_tender.project_name}")
        st.write(f"**Department:** {selected_tender.department}")
        st.write(f"**Scheme:** {selected_tender.scheme}")
        st.write(f"**Contractor:** {selected_tender.contractor_name}")
        st.write(f"**Measurement Book Ref:** `{selected_claim.measurement_book_ref}`")

    with col_forensic:
        st.markdown("#### 🔬 AI Forensic Analysis")
        st.write(f"**Physical Stage Identified:** `{audit_result.vision_stage_detected}`")
        st.write(f"**Geofence Verification:** {'✅ Within perimeter' if audit_result.geospatial_verified else f'❌ VIOLATION ({audit_result.distance_from_site_meters:.1f}m away)'}")

        st.markdown("##### 📌 Key Visual Observations:")
        for obs in audit_result.vision_observations:
            st.write(f"- {obs}")

        st.markdown("##### ⚠️ Detected Discrepancies & Non-Conformances:")
        if audit_result.discrepancies:
            for d in audit_result.discrepancies:
                severity_color = "red" if d.severity == "CRITICAL" else "orange" if d.severity == "HIGH" else "blue"
                st.markdown(f"- **[:{severity_color}[{d.severity}]]** *{d.category}*: {d.description}")
        else:
            st.write("None. All parameters conform to sanction guidelines.")

        st.markdown("---")
        # Financial summary box
        col_rec1, col_rec2 = st.columns(2)
        with col_rec1:
            st.metric("Questioned / Flagged Amount", f"₹{audit_result.total_flagged_amount_inr:,.2f}")
        with col_rec2:
            st.metric("Approved Disbursement", f"₹{audit_result.recommended_disbursement_inr:,.2f}")

        # PDF Certificate Download
        pdf_path = generate_pdf_certificate(selected_tender, selected_claim, audit_result)
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
            st.download_button(
                label="📄 Download Official Signed Inspection Certificate (PDF)",
                data=pdf_bytes,
                file_name=f"Audit_Certificate_{audit_result.audit_id}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        st.caption(f"🔒 Tamper-Proof Cryptographic Seal: `{audit_result.audit_hash}`")

with tab2:
    st.markdown("#### 🛰️ Geospatial Site Geofence & Coordinate Verification")
    st.write(f"**Sanctioned Tender Target:** `{selected_tender.target_lat:.5f}, {selected_tender.target_lng:.5f}`")
    st.write(f"**Claim Evidence Coordinates:** `{selected_claim.photo_lat:.5f}, {selected_claim.photo_lng:.5f}`")
    st.write(f"**Offset Distance:** `{audit_result.distance_from_site_meters:.1f} meters` (Allowed Radius: `{selected_tender.geo_fence_radius_meters}m`)")

    map_tiles = "CartoDB dark_matter" if theme_mode == "🌙 Dark Mode" else "CartoDB positron"
    m = folium.Map(location=[selected_tender.target_lat, selected_tender.target_lng], zoom_start=14, tiles=map_tiles)

    # Tender Sanctioned Area
    folium.Marker(
        [selected_tender.target_lat, selected_tender.target_lng],
        popup=f"Sanctioned Site: {selected_tender.project_name}",
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(m)

    folium.Circle(
        radius=selected_tender.geo_fence_radius_meters,
        location=[selected_tender.target_lat, selected_tender.target_lng],
        color="blue",
        fill=True,
        fill_opacity=0.15,
        tooltip=f"Authorized Perimeter ({selected_tender.geo_fence_radius_meters}m)"
    ).add_to(m)

    # Claim Photo Location
    if selected_claim.photo_lat and selected_claim.photo_lng:
        marker_color = "green" if audit_result.geospatial_verified else "red"
        folium.Marker(
            [selected_claim.photo_lat, selected_claim.photo_lng],
            popup=f"Claim Photo Location ({audit_result.distance_from_site_meters:.1f}m away)",
            icon=folium.Icon(color=marker_color, icon="camera")
        ).add_to(m)

        # Line connecting the two
        folium.PolyLine(
            [[selected_tender.target_lat, selected_tender.target_lng], [selected_claim.photo_lat, selected_claim.photo_lng]],
            color=marker_color,
            weight=2,
            dash_array="5, 5"
        ).add_to(m)

    st_folium(m, width=900, height=450)

with tab3:
    st.markdown("#### 📑 Tender Schedule of Rates (SoR) vs. Contractor Billed Items")
    tender_map = {item.item_code: item for item in selected_tender.boq_items}

    boq_table_data = []
    for item in selected_claim.claimed_items:
        tender_item = tender_map.get(item.item_code)
        if tender_item:
            rate_delta = item.claimed_unit_rate_inr - tender_item.approved_rate_inr
            qty_delta = item.claimed_qty - tender_item.tendered_qty
            status = "✅ Match" if (rate_delta <= 0 and qty_delta <= 0) else "❌ Overcharge"
            boq_table_data.append({
                "Item Code": item.item_code,
                "Description": item.description,
                "Claimed Qty": f"{item.claimed_qty:,.1f}",
                "Approved Qty": f"{tender_item.tendered_qty:,.1f}",
                "Billed Rate (₹)": f"₹{item.claimed_unit_rate_inr:,.2f}",
                "SoR Rate (₹)": f"₹{tender_item.approved_rate_inr:,.2f}",
                "Total Claimed (₹)": f"₹{item.total_claimed_amount_inr:,.2f}",
                "Status": status
            })
        else:
            boq_table_data.append({
                "Item Code": item.item_code,
                "Description": item.description,
                "Claimed Qty": f"{item.claimed_qty:,.1f}",
                "Approved Qty": "0.0 (Unsanctioned)",
                "Billed Rate (₹)": f"₹{item.claimed_unit_rate_inr:,.2f}",
                "SoR Rate (₹)": "N/A",
                "Total Claimed (₹)": f"₹{item.total_claimed_amount_inr:,.2f}",
                "Status": "🚨 Phantom Item"
            })

    st.dataframe(boq_table_data, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    "<center><small>Nirman-Drishti | AI for Digital Public Infrastructure & Governance | "
    "Designed for District Collectors, MPs, and Vigilance Officers | Powered by Google Cloud & Gemini</small></center>",
    unsafe_allow_html=True
)
