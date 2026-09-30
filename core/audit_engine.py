"""
Nirman-Drishti Audit Engine
Master orchestrator unifying vision, geospatial, and financial rate auditing.
"""

import uuid
from typing import Optional
from .models import (
    ProjectTender,
    ContractorClaim,
    ForensicAuditResult,
    Discrepancy,
)
from .vision_auditor import audit_vision_and_geospatial
from .boq_auditor import audit_boq_and_rates


class NirmanAuditEngine:
    """
    Forensic audit orchestrator for public infrastructure claims.
    """

    @staticmethod
    def audit_claim(
        tender: ProjectTender,
        claim: ContractorClaim,
        image_path: Optional[str] = None
    ) -> ForensicAuditResult:
        audit_id = f"AUD-{uuid.uuid4().hex[:8].upper()}"

        # 1. Vision & Geospatial Audit
        geo_verified, distance, stage_detected, observations, vision_discrepancies = (
            audit_vision_and_geospatial(tender, claim, image_path)
        )

        # 2. BOQ & State Schedule of Rates Audit
        boq_discrepancies, boq_flagged_amount = audit_boq_and_rates(tender, claim)

        # Combine discrepancies
        all_discrepancies = vision_discrepancies + boq_discrepancies

        # 3. Compute Risk Score (0 to 100)
        risk_score = 0.0
        critical_count = sum(1 for d in all_discrepancies if d.severity == "CRITICAL")
        high_count = sum(1 for d in all_discrepancies if d.severity == "HIGH")

        if not geo_verified:
            risk_score += 45.0
        for d in all_discrepancies:
            if d.category == "VISION_MISMATCH":
                risk_score += 35.0
            elif d.category == "RATE_INFLATION":
                risk_score += 15.0
            elif d.category == "QUANTITY_OVERCLAIM":
                risk_score += 25.0

        risk_score = min(100.0, max(0.0, risk_score))

        # 4. Determine Verdict
        if critical_count > 0 or risk_score >= 65.0:
            verdict = "REJECTED"
        elif high_count > 0 or risk_score >= 25.0:
            verdict = "FLAGGED_FOR_VIGILANCE"
        else:
            verdict = "APPROVED"

        # 5. Financial Reconciliation
        total_flagged_inr = sum(d.financial_impact_inr for d in all_discrepancies)
        # Cap flagged amount to claimed amount
        total_flagged_inr = min(claim.claimed_amount_inr, total_flagged_inr)
        recommended_disbursement = max(0.0, claim.claimed_amount_inr - total_flagged_inr)

        # 6. Recommendation Summary
        if verdict == "APPROVED":
            summary = (
                f"VERIFIED SAFE: Site visual evidence matches claimed milestone ({claim.milestone_name}). "
                f"Coordinates verified within {distance:.1f}m of sanctioned tender site. "
                f"All billed rates strictly adhere to approved State Schedule of Rates (SoR). "
                f"Recommended for automated treasury disbursement of ₹{recommended_disbursement:,.2f}."
            )
        elif verdict == "FLAGGED_FOR_VIGILANCE":
            summary = (
                f"VIGILANCE HOLD: Detected {len(all_discrepancies)} non-conformances totaling "
                f"₹{total_flagged_inr:,.2f} in questioned costs. "
                f"Physical inspection recommended by Executive Engineer before disbursement. "
                f"Withheld disbursement: ₹{total_flagged_inr:,.2f}."
            )
        else:
            summary = (
                f"CRITICAL FRAUD ALERT: Claim rejected due to {critical_count} critical violations. "
                f"Flagged for immediate Vigilance Directorate & District Collector enquiry. "
                f"All fund releases halted. Potential savings to exchequer: ₹{total_flagged_inr:,.2f}."
            )

        result = ForensicAuditResult(
            audit_id=audit_id,
            tender_id=tender.tender_id,
            claim_id=claim.claim_id,
            risk_score=round(risk_score, 1),
            verdict=verdict,
            geospatial_verified=geo_verified,
            distance_from_site_meters=round(distance, 1),
            vision_stage_detected=stage_detected,
            vision_observations=observations,
            discrepancies=all_discrepancies,
            total_flagged_amount_inr=round(total_flagged_inr, 2),
            recommended_disbursement_inr=round(recommended_disbursement, 2),
            recommendation_summary=summary,
        )
        result.audit_hash = result.compute_tamper_hash()
        return result
