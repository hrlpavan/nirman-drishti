"""
Nirman-Drishti BOQ & Invoice Auditor
Cross-checks contractor claim items against State Schedule of Rates (SoR) and Tender BOQ.
"""

from typing import List, Tuple
from .models import ProjectTender, ContractorClaim, Discrepancy


def audit_boq_and_rates(
    tender: ProjectTender,
    claim: ContractorClaim
) -> Tuple[List[Discrepancy], float]:
    """
    Audits contractor claimed line items against approved tender BOQ.
    Returns:
        (discrepancies, total_flagged_amount_inr)
    """
    discrepancies: List[Discrepancy] = []
    total_flagged_amount = 0.0

    # Build tender lookup map
    tender_map = {item.item_code: item for item in tender.boq_items}

    for item in claim.claimed_items:
        # Check 1: Phantom item (item not in tender)
        if item.item_code not in tender_map:
            overcharge = item.total_claimed_amount_inr
            discrepancies.append(
                Discrepancy(
                    category="QUANTITY_OVERCLAIM",
                    severity="CRITICAL",
                    description=(
                        f"Unsanctioned / Phantom Item '{item.item_code}' ({item.description}). "
                        f"Not present in approved tender BOQ."
                    ),
                    financial_impact_inr=overcharge,
                )
            )
            total_flagged_amount += overcharge
            continue

        tender_item = tender_map[item.item_code]

        # Check 2: Rate Inflation (Claimed rate > Approved SoR rate)
        if item.claimed_unit_rate_inr > tender_item.approved_rate_inr:
            rate_delta = item.claimed_unit_rate_inr - tender_item.approved_rate_inr
            rate_overcharge = round(rate_delta * item.claimed_qty, 2)
            discrepancies.append(
                Discrepancy(
                    category="RATE_INFLATION",
                    severity="HIGH",
                    description=(
                        f"Rate Inflation for '{item.description}' ({item.item_code}): "
                        f"Billed at ₹{item.claimed_unit_rate_inr:,.2f}/{tender_item.unit} vs. "
                        f"Approved SoR rate ₹{tender_item.approved_rate_inr:,.2f}/{tender_item.unit} "
                        f"(Excess of ₹{rate_delta:,.2f}/{tender_item.unit})."
                    ),
                    financial_impact_inr=rate_overcharge,
                )
            )
            total_flagged_amount += rate_overcharge

        # Check 3: Quantity Overclaim (Claimed qty > Tendered qty)
        if item.claimed_qty > tender_item.tendered_qty:
            excess_qty = item.claimed_qty - tender_item.tendered_qty
            qty_overcharge = round(excess_qty * tender_item.approved_rate_inr, 2)
            discrepancies.append(
                Discrepancy(
                    category="QUANTITY_OVERCLAIM",
                    severity="CRITICAL",
                    description=(
                        f"Quantity Overclaim for '{item.description}': "
                        f"Claimed {item.claimed_qty:,.2f} {tender_item.unit} exceeds "
                        f"sanctioned ceiling {tender_item.tendered_qty:,.2f} {tender_item.unit} "
                        f"by {excess_qty:,.2f} {tender_item.unit}."
                    ),
                    financial_impact_inr=qty_overcharge,
                )
            )
            total_flagged_amount += qty_overcharge

    return discrepancies, total_flagged_amount
