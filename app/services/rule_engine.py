import re

from app.utils.logger import get_logger

logger = get_logger(__name__)

# Define validation rules with more precise patterns
RULES = {
    "unlimited_liability": {
        "patterns": [
            "unlimited liability",
            "subject to unlimited liability",
            "unlimited damages",
            "no limitation of liability",
            "no cap on liability"
        ],
        "negative_patterns": [],  # Patterns that negate the rule (if present, ignore)
        "name": "Unlimited Liability",
        "severity": "high"
    },
    "missing_duration": {
        "patterns": [
            "indefinitely",
            "in perpetuity",
            "forever",
            "no time limit",
            "without limitation",
            "indefinite term"
        ],
        "negative_patterns": [
            "for a period of",
            "for the term of",
            "years",
            "months",
            "until"
        ],  # If these follow, duration IS specified
        "name": "Missing Duration",
        "severity": "high"
    },
    "exclusive_jurisdiction": {
        "patterns": [
            "exclusive jurisdiction",
            "sole jurisdiction",
            "exclusive venue",
            "sole and exclusive jurisdiction"
        ],
        "negative_patterns": [],
        "name": "Exclusive Jurisdiction",
        "severity": "medium"
    },
    "broad_confidentiality": {
        "patterns": [
            "confidential information includes all",
            "all information is confidential",
            "any and all information",
            "broadly includes",
            "all technical and business information"
        ],
        "negative_patterns": ["excludes", "does not include", "except"],  # If these are present, scope is limited
        "name": "Broad Confidentiality Scope",
        "severity": "medium"
    },
    "unilateral_obligation": {
        "patterns": [
            "only the receiving party shall",
            "solely the receiving party",
            "only one party is obligated",
            "one-way obligation"
        ],
        "negative_patterns": [],
        "name": "Unilateral Obligations",
        "severity": "medium"
    },
    "ip_assignment": {
        "patterns": [
            "hereby automatically assigns",
            "assigns, transfers, and conveys",
            "all right, title, and interest in any intellectual property",
            "ownership of all derivative works shall vest"
        ],
        "negative_patterns": [],
        "name": "IP Assignment",
        "severity": "high"
    },
    "unilateral_indemnity": {
        "patterns": [
            "receiving party agrees to indemnify",
            "receiving party shall indemnify",
            "receiving party agrees to indemnify, defend, and hold harmless"
        ],
        "negative_patterns": ["each party shall indemnify", "both parties shall indemnify", "mutual indemnification"],
        "name": "Unilateral Indemnity",
        "severity": "high"
    },
    "zero_liability_cap": {
        "patterns": ["liability shall be strictly capped at $0", "liability is capped at $0"],
        "regex_patterns": [r"(?:aggregate\s+)?liability.{0,100}(?:capped|limited).{0,30}(?:\$\s*0(?:\.0+)?|zero)"],
        "negative_patterns": [],
        "name": "Zero Liability Cap",
        "severity": "high"
    },
    "punitive_liquidated_damages": {
        "patterns": ["liquidated damages of minimum", "liquidated damages of at least", "minimum liquidated damages"],
        "negative_patterns": [],
        "name": "Punitive Liquidated Damages",
        "severity": "high"
    },
    "non_compete_restriction": {
        "patterns": [
            "non-compete",
            "prohibited from engaging, directly or indirectly",
            "competitive business operations",
            "competitive business activities"
        ],
        "negative_patterns": [],
        "name": "Non-Compete Restriction",
        "severity": "high"
    },
    "unmarked_confidential_information": {
        "patterns": ["marked or unmarked", "whether or not marked confidential"],
        "negative_patterns": [],
        "name": "Unmarked Confidential Information",
        "severity": "medium"
    }
}


def validate_clause(clause):
    """
    Validate clause against known risk patterns.
    
    Uses positive patterns for detection and negative patterns to avoid false positives.
    
    Args:
        clause: Text of the clause to validate
        
    Returns:
        list: Names of matched rules
    """
    clause_lower = clause.lower()
    matched_rules = []
    
    for rule_id, rule in RULES.items():
        # Check literal and regex patterns. Regex supports small variations
        # such as "$0" versus "$0.00" in an asymmetric liability cap.
        pattern_matched = any(pattern in clause_lower for pattern in rule["patterns"])
        if not pattern_matched:
            pattern_matched = any(
                re.search(pattern, clause_lower, flags=re.DOTALL)
                for pattern in rule.get("regex_patterns", [])
            )
        
        if not pattern_matched:
            continue
        
        # If pattern matched, check for negative patterns that would negate the match (precision mechanism)
        negated = False
        if "negative_patterns" in rule:
            for neg_pattern in rule["negative_patterns"]:
                if neg_pattern in clause_lower:
                    negated = True
                    logger.debug(f"Rule {rule['name']} negated by pattern: {neg_pattern}")
                    break
        
        if not negated:
            matched_rules.append(rule["name"])
            logger.debug(f"Rule matched: {rule['name']}")
    
    if matched_rules:
        logger.info(f"Validation found {len(matched_rules)} matched rules: {matched_rules}")
    else:
        logger.debug("No validation rules matched")
    
    return matched_rules
