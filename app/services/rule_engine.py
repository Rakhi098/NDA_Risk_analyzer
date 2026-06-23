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
        "negative_patterns": ["for a period of", "for", "years", "months", "until"],  # If these follow, duration IS specified
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
        # Check if any positive pattern matches
        pattern_matched = False
        for pattern in rule["patterns"]:
            if pattern in clause_lower:
                pattern_matched = True
                break
        
        if not pattern_matched:
            continue
        
        # If pattern matched, check for negative patterns that would negate the match
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