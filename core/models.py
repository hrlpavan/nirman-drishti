"""
Nirman-Drishti Data Models
Pydantic schemas for tenders, contractor claims, and forensic audit results.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
import hashlib
import json
from datetime import datetime


class TenderItem(BaseModel):
    item_code: str
    description: str
    unit: str
    tendered_qty: float
    approved_rate_inr: float
    total_tendered_amount_inr: float


class ProjectTender(BaseModel):
    tender_id: str
    project_name: str
    department: str
    scheme: str  # e.g., "PMGSY", "MPLADS", "Jal Jeevan Mission", "Smart City"
    sanctioned_budget_inr: float
    contractor_name: str
    target_lat: float
    target_lng: float
    geo_fence_radius_meters: float = 500.0
    sanction_date: str
    scheduled_completion_date: str
    boq_items: List[TenderItem]


class ClaimItem(BaseModel):
    item_code: str
    description: str
    claimed_qty: float
    claimed_unit_rate_inr: float
    total_claimed_amount_inr: float


class ContractorClaim(BaseModel):
    claim_id: str
    tender_id: str
    milestone_name: str
    claimed_completion_pct: float
    claimed_amount_inr: float
    claim_date: str
    photo_lat: Optional[float] = None
    photo_lng: Optional[float] = None
    photo_timestamp: Optional[str] = None
    photo_filename: Optional[str] = None
    measurement_book_ref: str
    claimed_items: List[ClaimItem]


class Discrepancy(BaseModel):
    category: str  # "VISION_MISMATCH", "GEO_TAMPERING", "RATE_INFLATION", "QUANTITY_OVERCLAIM"
    severity: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    description: str
    financial_impact_inr: float = 0.0


class ForensicAuditResult(BaseModel):
    audit_id: str
    tender_id: str
    claim_id: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    risk_score: float  # 0.0 (clean) to 100.0 (high fraud risk)
    verdict: str  # "APPROVED", "FLAGGED_FOR_VIGILANCE", "REJECTED"
    geospatial_verified: bool
    distance_from_site_meters: float
    vision_stage_detected: str
    vision_observations: List[str]
    discrepancies: List[Discrepancy]
    total_flagged_amount_inr: float
    recommended_disbursement_inr: float
    recommendation_summary: str
    audit_hash: Optional[str] = None

    def compute_tamper_hash(self) -> str:
        """Cryptographic tamper-evident hash for DPI/DigiLocker audit chain."""
        payload = {
            "audit_id": self.audit_id,
            "tender_id": self.tender_id,
            "claim_id": self.claim_id,
            "risk_score": self.risk_score,
            "verdict": self.verdict,
            "total_flagged": self.total_flagged_amount_inr,
            "timestamp": self.timestamp,
        }
        raw = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()
