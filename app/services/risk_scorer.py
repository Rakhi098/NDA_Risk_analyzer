"""
Risk scoring module for NDA analysis.
Aggregates AI analysis and rule validation into final risk scores.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Thresholds for confidence-based risk interpretation
HIGH_CONFIDENCE_THRESHOLD = 0.7
MEDIUM_CONFIDENCE_THRESHOLD = 0.4
OVERALL_HIGH_PERCENT_THRESHOLD = 0.10
OVERALL_MEDIUM_PERCENT_THRESHOLD = 0.25

RISK_ORDER = {
    "no-risk": 0,
    "medium": 1,
    "high": 2
}


def normalize_risk_label(risk_label: str, confidence: float) -> str:
    """
    Normalize an AI risk label using confidence thresholds.
    """
    risk = risk_label.lower()
    if confidence is None:
        return risk
    if confidence < MEDIUM_CONFIDENCE_THRESHOLD:
        if risk == "high":
            return "medium"
        if risk == "medium":
            return "no-risk"
    return risk


def calculate_overall_risk(analysis_results: List[Dict[str, Any]], total_clauses: Optional[int] = None) -> str:
    """
    Calculate overall risk based on clause analysis results.

    Rules:
    - If any clause is HIGH → overall HIGH
    - Else if any clause is MEDIUM → overall MEDIUM
    - Else LOW
    - Optional percentage fallback to enforce high/medium thresholds
    """
    if not analysis_results:
        return "Low"

    high_count = sum(1 for r in analysis_results if r.get("risk", "no-risk").lower() == "high")
    medium_count = sum(1 for r in analysis_results if r.get("risk", "no-risk").lower() == "medium")

    if high_count > 0:
        logger.info("Overall risk assessed as HIGH due to at least one high-risk clause")
        return "High"

    if total_clauses and total_clauses > 0:
        high_ratio = high_count / total_clauses
        medium_ratio = medium_count / total_clauses
        if high_ratio >= OVERALL_HIGH_PERCENT_THRESHOLD:
            logger.info("Overall risk assessed as HIGH due to high-risk clause percentage threshold")
            return "High"
        if medium_ratio >= OVERALL_MEDIUM_PERCENT_THRESHOLD:
            logger.info("Overall risk assessed as MEDIUM due to medium-risk clause percentage threshold")
            return "Medium"

    if medium_count > 0:
        logger.info("Overall risk assessed as MEDIUM due to at least one medium-risk clause")
        return "Medium"

    logger.info("Overall risk assessed as LOW")
    return "Low"


def filter_risky_clauses(analysis_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filter out low-risk clauses from analysis results.
    """
    risky = [r for r in analysis_results if r.get("risk", "no-risk").lower() != "no-risk"]
    logger.info(f"Filtered {len(risky)} risky clauses out of {len(analysis_results)} total")
    return risky


def format_risk_response(analysis_results: List[Dict[str, Any]], total_clauses: Optional[int] = None) -> Dict[str, Any]:
    """
    Format the final risk analysis response.
    """
    risky_clauses = filter_risky_clauses(analysis_results)
    overall_risk = calculate_overall_risk(risky_clauses, total_clauses)
    high_count = sum(1 for r in risky_clauses if r.get("risk", "no-risk").lower() == "high")
    medium_count = sum(1 for r in risky_clauses if r.get("risk", "no-risk").lower() == "medium")

    response = {
        "overall_risk": overall_risk,
        "total_risky_clauses": len(risky_clauses),
        "total_clauses": total_clauses if total_clauses is not None else len(analysis_results),
        "high_risk_clause_percentage": round((high_count / total_clauses) * 100, 2) if total_clauses else 0,
        "medium_risk_clause_percentage": round((medium_count / total_clauses) * 100, 2) if total_clauses else 0,
        "high_risk_threshold_pct": int(OVERALL_HIGH_PERCENT_THRESHOLD * 100),
        "medium_risk_threshold_pct": int(OVERALL_MEDIUM_PERCENT_THRESHOLD * 100),
        "analysis": risky_clauses
    }

    logger.info(f"Risk response formatted: {overall_risk} risk with {len(risky_clauses)} risky clauses")
    return response


def assess_risk_confidence(clause_analysis: Dict[str, Any], matched_rules: List[str], risk_label: Optional[str] = None) -> Dict[str, Any]:
    """
    Assess confidence level based on AI analysis and rule matches.
    """
    risk_level = (risk_label or clause_analysis.get("risk", "no-risk")).lower()
    confidence = clause_analysis.get("confidence", 0.7)

    try:
        confidence = float(confidence)
    except (TypeError, ValueError):
        confidence = 0.7

    if matched_rules and len(matched_rules) > 0:
        confidence = min(0.95, confidence + 0.05 * len(matched_rules))

    adjusted_risk = normalize_risk_label(risk_level, confidence)

    return {
        "risk": adjusted_risk,
        "reason": clause_analysis.get("reason", ""),
        "matched_rules": matched_rules,
        "confidence": round(confidence, 2)
    }
