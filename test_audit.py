"""
Nirman-Drishti Self-Check / Assertion Suite
Single runnable check verifying end-to-end forensic auditing logic.
"""

import json
import os
from core.models import ProjectTender, ContractorClaim
from core.audit_engine import NirmanAuditEngine
from core.cert_generator import generate_pdf_certificate


def run_checks():
    print("--- Running Nirman-Drishti Forensic Audit Self-Check ---")

    # 1. Load benchmark datasets
    with open("data/tenders.json") as f:
        tenders_raw = json.load(f)
    with open("data/claims.json") as f:
        claims_raw = json.load(f)

    tenders = {t["tender_id"]: ProjectTender(**t) for t in tenders_raw}
    claims = [ContractorClaim(**c) for c in claims_raw]

    assert len(tenders) == 3, f"Expected 3 tenders, got {len(tenders)}"
    assert len(claims) == 3, f"Expected 3 claims, got {len(claims)}"

    # 2. Test Claim 1: PMGSY Road (Should be REJECTED / High Fraud Alert)
    claim1 = claims[0]
    tender1 = tenders[claim1.tender_id]
    img1_path = os.path.join("data/sample_images", claim1.photo_filename)
    res1 = NirmanAuditEngine.audit_claim(tender1, claim1, img1_path)

    print(f"\n[Case 1] {tender1.tender_id} Claim: {claim1.claim_id}")
    print(f"  Verdict: {res1.verdict} | Risk Score: {res1.risk_score}/100")
    print(f"  Flagged Amount: ₹{res1.total_flagged_amount_inr:,.2f}")
    print(f"  Discrepancies found: {len(res1.discrepancies)}")

    assert res1.verdict == "REJECTED", f"Expected REJECTED, got {res1.verdict}"
    assert res1.risk_score >= 65.0, f"Expected risk >= 65, got {res1.risk_score}"
    assert not res1.geospatial_verified, "Expected geofence violation"
    categories = {d.category for d in res1.discrepancies}
    assert "GEO_TAMPERING" in categories, "Expected GEO_TAMPERING category"
    assert "RATE_INFLATION" in categories, "Expected RATE_INFLATION category"
    assert "QUANTITY_OVERCLAIM" in categories, "Expected QUANTITY_OVERCLAIM category"

    # 3. Test Case 2: JJM Solar Pump (Should be APPROVED / Safe)
    claim2 = claims[1]
    tender2 = tenders[claim2.tender_id]
    img2_path = os.path.join("data/sample_images", claim2.photo_filename)
    res2 = NirmanAuditEngine.audit_claim(tender2, claim2, img2_path)

    print(f"\n[Case 2] {tender2.tender_id} Claim: {claim2.claim_id}")
    print(f"  Verdict: {res2.verdict} | Risk Score: {res2.risk_score}/100")
    print(f"  Recommended Release: ₹{res2.recommended_disbursement_inr:,.2f}")

    assert res2.verdict == "APPROVED", f"Expected APPROVED, got {res2.verdict}"
    assert res2.risk_score < 25.0, f"Expected risk < 25, got {res2.risk_score}"
    assert res2.geospatial_verified, "Expected valid geofence"
    assert res2.total_flagged_amount_inr == 0.0, "Expected zero flagged overcharge"
    assert res2.recommended_disbursement_inr == claim2.claimed_amount_inr

    # 4. Test Case 3: MPLADS Building (Should be FLAGGED_FOR_VIGILANCE)
    claim3 = claims[2]
    tender3 = tenders[claim3.tender_id]
    img3_path = os.path.join("data/sample_images", claim3.photo_filename)
    res3 = NirmanAuditEngine.audit_claim(tender3, claim3, img3_path)

    print(f"\n[Case 3] {tender3.tender_id} Claim: {claim3.claim_id}")
    print(f"  Verdict: {res3.verdict} | Risk Score: {res3.risk_score}/100")
    print(f"  Flagged Rate Overcharge: ₹{res3.total_flagged_amount_inr:,.2f}")

    assert res3.verdict == "FLAGGED_FOR_VIGILANCE", f"Expected FLAGGED, got {res3.verdict}"
    assert res3.total_flagged_amount_inr > 0.0, "Expected flagged rate inflation"

    # 5. Test Cryptographic Hash
    for res in (res1, res2, res3):
        assert len(res.audit_hash) == 64, "Expected valid SHA256 audit hash"

    # 6. Test PDF Certificate Generation
    cert_path = generate_pdf_certificate(tender1, claim1, res1)
    assert os.path.exists(cert_path), f"Certificate file {cert_path} was not created"
    assert os.path.getsize(cert_path) > 500, "Certificate file is unexpectedly small"
    print(f"\n[Certificate Check] Generated PDF: {cert_path} ({os.path.getsize(cert_path)} bytes)")

    print("\n>>> ALL CHECKS PASSED SUCCESSFULLY (100% Correctness) <<<")


if __name__ == "__main__":
    run_checks()
