"""
Risk recommendation engine for NDA clauses.
Provides categories, risk scores, and mitigation strategies.
"""

from app.services.risk_scorer import (
    OVERALL_HIGH_PERCENT_THRESHOLD,
    OVERALL_MEDIUM_PERCENT_THRESHOLD,
    calculate_overall_risk,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Risk categories based on matched rules and content
RISK_CATEGORIES = {
    "Duration + Liability": {
        "keywords": ["indefinitely", "unlimited liability"],
        "severity": "critical",
        "recommendations": [
            "Request a specific confidentiality duration limit (e.g., 3-5 years)",
            "Negotiate a liability cap based on actual damages",
            "Add sunset provisions for survival clauses",
            "Define scope of 'damages' narrowly"
        ]
    },
    "Scope Overly Broad": {
        "keywords": ["all information", "broad confidentiality", "any and all"],
        "severity": "high",
        "recommendations": [
            "Define confidential information more precisely",
            "List specific types of information covered",
            "Add clear public domain and exclusion language",
            "Limit to information disclosed in writing"
        ]
    },
    "Exclusive Jurisdiction": {
        "keywords": ["exclusive jurisdiction", "sole jurisdiction"],
        "severity": "high",
        "recommendations": [
            "Negotiate for mutual jurisdiction (both parties' domicile)",
            "Request dispute resolution through arbitration",
            "Add a choice of law provision favorable to both parties",
            "Consider neutral jurisdiction for disputes"
        ]
    },
    "Unlimited Liability": {
        "keywords": ["unlimited liability", "unlimited damages"],
        "severity": "critical",
        "recommendations": [
            "Cap liability to direct damages only",
            "Exclude consequential and indirect damages",
            "Set a monetary liability limit",
            "Add liability sunset or survival limit"
        ]
    },
    "Unilateral Obligations": {
        "keywords": ["only the receiving party", "solely"],
        "severity": "medium",
        "recommendations": [
            "Make obligations mutual for both parties",
            "Clarify that both parties have equal responsibilities",
            "Request reciprocal confidentiality duties",
            "Balance rights and obligations"
        ]
    }
}


def categorize_risk(matched_rules, clause_text):
    """
    Categorize risk based on matched rules and clause content.
    
    Args:
        matched_rules: List of matched validation rules
        clause_text: Text of the clause
        
    Returns:
        str: Risk category name
    """
    clause_lower = clause_text.lower()
    
    # Check for Duration + Liability combination
    if "Missing Duration" in matched_rules and any(kw in clause_lower for kw in ["liability", "damages"]):
        return "Duration + Liability"
    
    # Check individual categories
    for category, rules in RISK_CATEGORIES.items():
        for rule in matched_rules:
            if rule in ["Broad Confidentiality Scope", "Missing Duration", "Unlimited Liability", "Exclusive Jurisdiction", "Unilateral Obligations"]:
                if "Broad Confidentiality" in rule:
                    return "Scope Overly Broad"
                elif "Missing Duration" in rule:
                    return "Duration + Liability" if "liability" in clause_lower else "Duration + Liability"
                elif "Unlimited Liability" in rule:
                    return "Unlimited Liability"
                elif "Exclusive Jurisdiction" in rule:
                    return "Exclusive Jurisdiction"
                elif "Unilateral" in rule:
                    return "Unilateral Obligations"
    
    return None


def calculate_risk_score(risk_level, matched_rules, category):
    """
    Calculate a risk score (0-100) based on risk level and matched rules.
    
    Args:
        risk_level: 'high', 'medium', or 'no-risk'
        matched_rules: List of matched validation rules
        category: Risk category
        
    Returns:
        int: Risk score 0-100
    """
    score = 0
    
    # Base score from risk level
    if risk_level == "high":
        score = 75
    elif risk_level == "medium":
        score = 50
    else:
        score = 10
    
    # Boost for multiple matched rules
    score += min(len(matched_rules) * 5, 15)
    
    # Boost for critical categories
    if category and RISK_CATEGORIES.get(category, {}).get("severity") == "critical":
        score = min(score + 10, 100)
    
    logger.debug(f"Risk score calculated: {score} (risk={risk_level}, rules={len(matched_rules)}, category={category})")
    return min(score, 100)


def get_mitigation_recommendations(category, matched_rules):
    """
    Get mitigation recommendations for a risk category.
    
    Args:
        category: Risk category name
        matched_rules: List of matched rules
        
    Returns:
        list: Mitigation recommendations
    """
    if not category or category not in RISK_CATEGORIES:
        return ["Review clause with legal counsel", "Negotiate terms with disclosing party"]
    
    recommendations = RISK_CATEGORIES[category]["recommendations"]
    logger.debug(f"Retrieved {len(recommendations)} recommendations for category: {category}")
    return recommendations


def format_enhanced_response(analysis_results, total_clauses=None):
    """
    Format analysis results with risk scores, categories, and recommendations.

    Args:
        analysis_results: List of clause analysis results
        total_clauses: Optional total number of clauses in the document

    Returns:
        dict: Enhanced response with scores and recommendations
    """
    enhanced_analysis = []
    
    for result in analysis_results:
        category = categorize_risk(result.get("matched_rules", []), result.get("clause", ""))
        risk_score = calculate_risk_score(
            result.get("risk", "no-risk"),
            result.get("matched_rules", []),
            category
        )
        recommendations = get_mitigation_recommendations(
            category,
            result.get("matched_rules", [])
        )
        
        enhanced_analysis.append({
            "clause": result["clause"],
            "risk": result["risk"],
            "reason": result["reason"],
            "matched_rules": result.get("matched_rules", []),
            "category": category or "Other",
            "risk_score": risk_score,
            "recommendations": recommendations[:2]
        })
    
    total_clauses = total_clauses or len(analysis_results)
    high_count = sum(1 for r in enhanced_analysis if r["risk"] == "high")
    medium_count = sum(1 for r in enhanced_analysis if r["risk"] == "medium")
    high_pct = round((high_count / total_clauses) * 100, 2) if total_clauses else 0
    medium_pct = round((medium_count / total_clauses) * 100, 2) if total_clauses else 0

    overall_risk = calculate_overall_risk(enhanced_analysis, total_clauses)

    return {
        "overall_risk": overall_risk,
        "total_risky_clauses": len(enhanced_analysis),
        "total_clauses": total_clauses,
        "high_risk_clause_percentage": high_pct,
        "medium_risk_clause_percentage": medium_pct,
        "high_risk_threshold_pct": int(OVERALL_HIGH_PERCENT_THRESHOLD * 100),
        "medium_risk_threshold_pct": int(OVERALL_MEDIUM_PERCENT_THRESHOLD * 100),
        "analysis": enhanced_analysis
    }
