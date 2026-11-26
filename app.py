"""
Nirman-Drishti: Simple AI Road Construction & Bill Verification Dashboard
Checks: (1) GPS Geofencing, (2) Computer Vision Road Surface, (3) Govt Bill Rate.
"""

from datetime import date
import json
import os
import tempfile
import streamlit as st
import folium
from streamlit_folium import st_folium
from PIL import Image

from core.models import ProjectTender, ContractorClaim, ClaimItem
from core.audit_engine import NirmanAuditEngine
from core.vision_auditor import extract_exif_metadata
from core.cert_generator import generate_pdf_certificate

st.set_page_config(page_title="Nirman-Drishti | AI Road Verification", page_icon="🛣️", layout="wide")


@st.cache_data
def load_road_tender() -> ProjectTender:
    with open("data/tenders.json") as f:
        return ProjectTender(**json.load(f)[0])


tender = load_road_tender()
tar_item = tender.boq_items[-1]  # Bituminous Concrete (75 MT @ Rs. 65,000)

st.title("🛣️ Nirman-Drishti")
st.caption("AI Road Construction Verification using **Computer Vision**, **GPS Geofencing**, and **Bill Check**")
st.markdown(
    f"**Approved Project:** {tender.project_name} &nbsp;|&nbsp; "
    f"**Govt Site GPS:** `{tender.target_lat}, {tender.target_lng}` (Allowed Radius: `{int(tender.geo_fence_radius_meters)}m`)"
)
st.divider()

# --- STEP 1: SIMPLE INPUTS ---
st.subheader("Step 1: Upload Road Photo & Contractor Bill")
col1, col2, col3 = st.columns(3)

with col1:
    demo_mode = st.radio(
        "Quick Preset or Custom Upload",
        options=["🔴 Demo 1: Fake Gravel Road", "🟢 Demo 2: Genuine Road Claim", "📸 Upload Custom Road Photo"],
    )
    uploaded = None
    if demo_mode == "📸 Upload Custom Road Photo":
        uploaded = st.file_uploader("Upload Road Photo (JPG/PNG)", type=["jpg", "jpeg", "png", "webp"])

    image_path = "data/sample_images/road_wbm_unpaved.jpg"
    exif_lat, exif_lng = None, None
    if uploaded is not None:
        tmp_path = os.path.join(tempfile.gettempdir(), f"road_upload_{uploaded.name}")
        with open(tmp_path, "wb") as f:
            f.write(uploaded.getbuffer())
        image_path = tmp_path
        exif = extract_exif_metadata(image_path)
        exif_lat, exif_lng = exif["lat"], exif["lng"]
        if exif_lat and exif_lng:
            st.success(f"Auto-extracted Photo GPS: {exif_lat:.4f}, {exif_lng:.4f}")

    if os.path.exists(image_path):
        st.image(Image.open(image_path), caption="Submitted Road Photo", width="stretch")

with col2:
    default_lat = exif_lat if exif_lat else (14.2814 if "Demo 2" in demo_mode else 14.3650)
    default_lng = exif_lng if exif_lng else (74.4533 if "Demo 2" in demo_mode else 74.5200)
    photo_lat = st.number_input("Photo Latitude", value=float(default_lat), format="%.4f")
    photo_lng = st.number_input("Photo Longitude", value=float(default_lng), format="%.4f")
    st.caption("Tip: `14.2814, 74.4533` is at the road site (28m). `14.3650, 74.5200` is 11.7 km away.")

with col3:
    stage_options = [
        "100% Finished Bituminous Tar Surface",
        "Stage 1: Compacted WBM Gravel Base",
    ]
    claimed_stage = st.selectbox(
        "Work Claimed by Contractor",
        options=stage_options,
        index=1 if "Demo 2" in demo_mode else 0,
    )
    billed_rate = st.number_input(
        f"Billed Rate ₹/Ton (Govt Rate: ₹{tar_item.approved_rate_inr:,.0f})",
        min_value=1000.0,
        value=float(tar_item.approved_rate_inr if "Demo 2" in demo_mode else 88000.0),
        step=1000.0,
    )
    claimed_qty = st.number_input(
        f"Claimed Tar Qty in Tons (Govt Limit: {tar_item.tendered_qty:.0f} Tons)",
        min_value=1.0,
        value=float(tar_item.tendered_qty if "Demo 2" in demo_mode else 110.0),
        step=5.0,
    )

line_total = round(billed_rate * claimed_qty, 2)
claim = ContractorClaim(
    claim_id="CLM-ROAD-01",
    tender_id=tender.tender_id,
    milestone_name=claimed_stage,
    claimed_completion_pct=100.0 if "100%" in claimed_stage else 85.0,
    claimed_amount_inr=line_total,
    claim_date=str(date.today()),
    photo_lat=photo_lat,
    photo_lng=photo_lng,
    photo_filename=uploaded.name if uploaded else "road_photo.jpg",
    measurement_book_ref="MB-ROAD-01",
    claimed_items=[
        ClaimItem(
            item_code=tar_item.item_code,
            description=tar_item.description,
            claimed_qty=claimed_qty,
            claimed_unit_rate_inr=billed_rate,
            total_claimed_amount_inr=line_total,
        )
    ],
)

result = NirmanAuditEngine.audit_claim(tender, claim, image_path)

st.divider()

# --- STEP 2: VERDICT & 3 SIMPLE CHECKS ---
if result.verdict == "APPROVED":
    st.success(f"### ✅ APPROVED — Genuine Work Verified (Risk Score: {result.risk_score}/100)")
elif result.verdict == "FLAGGED_FOR_VIGILANCE":
    st.warning(f"### ⚠️ HOLD — Rate Overcharge Detected (Risk Score: {result.risk_score}/100)")
else:
    st.error(f"### 🚨 REJECTED — Fraud / Mismatch Detected (Risk Score: {result.risk_score}/100)")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("#### 📍 1. GPS Geofence Check")
    st.write(f"**Distance from Site:** `{result.distance_from_site_meters:.1f} m` (Max `{int(tender.geo_fence_radius_meters)} m`)")
    st.write("✅ **PASSED** (Inside boundary)" if result.geospatial_verified else "❌ **FAILED** (Outside 500m boundary)")

with c2:
    st.markdown("#### 👁️ 2. Computer Vision Check")
    st.write(f"**Detected Surface:** `{result.vision_stage_detected}`")
    vision_failed = any(d.category == "VISION_MISMATCH" for d in result.discrepancies)
    st.write("❌ **FAILED** (Surface does not match claim)" if vision_failed else "✅ **PASSED** (Surface matches claim)")

with c3:
    st.markdown("#### 💰 3. Govt Bill Rate Check")
    st.write(f"**Contractor Bill:** `₹{line_total:,.0f}`")
    st.write(f"**Questioned Overcharge:** `₹{result.total_flagged_amount_inr:,.0f}`")
    bill_failed = any(d.category in ("RATE_INFLATION", "QUANTITY_OVERCLAIM") for d in result.discrepancies)
    st.write("❌ **OVERCHARGED**" if bill_failed else "✅ **PASSED** (Within Govt Rate)")

pdf_path = generate_pdf_certificate(tender, claim, result)
with open(pdf_path, "rb") as pf:
    st.download_button(
        "📄 Download Audit Report (PDF)",
        data=pf.read(),
        file_name=f"Nirman_Drishti_Report_{result.verdict}.pdf",
        mime="application/pdf",
    )

# --- LIVE MAP ---
st.markdown("#### 🗺️ Live GPS Geofence Map")
m = folium.Map(location=[tender.target_lat, tender.target_lng], zoom_start=13)
folium.Marker([tender.target_lat, tender.target_lng], popup="Approved Govt Road Site").add_to(m)
folium.Circle(radius=tender.geo_fence_radius_meters, location=[tender.target_lat, tender.target_lng], color="blue", fill=True).add_to(m)
pin_color = "green" if result.geospatial_verified else "red"
folium.Marker([photo_lat, photo_lng], popup=f"Photo GPS ({result.distance_from_site_meters:.1f}m)", icon=folium.Icon(color=pin_color)).add_to(m)
folium.PolyLine([[tender.target_lat, tender.target_lng], [photo_lat, photo_lng]], color=pin_color, dash_array="5, 5").add_to(m)
st_folium(m, width=900, height=360)
