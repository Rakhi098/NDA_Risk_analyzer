import json
from pathlib import Path

from app.services.rule_engine import RULES, validate_clause


RISK_RANK = {
    "no-risk": 0,
    "medium": 1,
    "high": 2,
}

DEFAULT_EVAL_DATASET = Path("tests/fixtures/nda_eval_cases.json")

RISK_REASON_KEYWORDS = {
    "Unlimited Liability": ["unlimited liability", "unlimited damages", "no limitation of liability", "no cap on liability"],
    "Missing Duration": ["indefinitely", "in perpetuity", "forever", "no time limit", "indefinite"],
    "Exclusive Jurisdiction": ["exclusive jurisdiction", "sole jurisdiction", "exclusive venue"],
    "Broad Confidentiality Scope": ["all information", "any and all information", "broad confidentiality", "broadly includes"],
    "Unilateral Obligations": ["only the receiving party", "solely the receiving party", "one-way obligation"],
    "IP Assignment": ["automatically assigns", "assigns, transfers, and conveys", "all right, title, and interest"],
    "Unilateral Indemnity": ["receiving party agrees to indemnify", "receiving party shall indemnify"],
    "Zero Liability Cap": ["capped at $0", "capped at $0.00", "liability is capped at zero"],
    "Punitive Liquidated Damages": ["liquidated damages of minimum", "liquidated damages of at least"],
    "Non-Compete Restriction": ["non-compete", "prohibited from engaging, directly or indirectly", "competitive business operations"],
    "Unmarked Confidential Information": ["marked or unmarked", "whether or not marked confidential"],
}


def load_eval_cases(path=DEFAULT_EVAL_DATASET):
    dataset_path = Path(path)
    with dataset_path.open("r", encoding="utf-8-sig") as file:
        cases = json.load(file)

    if not isinstance(cases, list):
        raise ValueError("Evaluation dataset must be a JSON list of cases")

    return cases


def infer_rule_risk(matched_rules):
    if not matched_rules:
        return "no-risk"

    severities = []
    for rule_config in RULES.values():
        if rule_config["name"] in matched_rules:
            severities.append(rule_config.get("severity", "medium"))

    if "high" in severities:
        return "high"
    return "medium"


def find_hallucination_flags(clause, reason, matched_rules):
    clause_lower = clause.lower()
    reason_lower = (reason or "").lower()
    flags = []

    for rule_name, keywords in RISK_REASON_KEYWORDS.items():
        reason_mentions_risk = any(keyword in reason_lower for keyword in keywords)
        clause_contains_evidence = any(keyword in clause_lower for keyword in keywords)
        rule_supported = rule_name in matched_rules

        if reason_mentions_risk and not clause_contains_evidence and not rule_supported:
            flags.append(rule_name)

    return flags


def analyze_case(case, use_llm=False):
    clause = case["text"]
    expected_risk = case["expected_risk"].lower()
    expected_rules = case.get("expected_rules", [])
    matched_rules = validate_clause(clause)
    predicted_risk = infer_rule_risk(matched_rules)
    reason = "Rule-based evaluation"
    llm_risk = None
    llm_reason = None

    if use_llm:
        from app.services.llm_engine import analyze_clause

        llm_analysis = analyze_clause(clause)
        llm_risk = llm_analysis.get("risk", "no-risk").lower()
        llm_reason = llm_analysis.get("reason", "")

        predicted_risk = llm_risk
        reason = llm_reason

        if matched_rules and RISK_RANK[infer_rule_risk(matched_rules)] > RISK_RANK[predicted_risk]:
            predicted_risk = infer_rule_risk(matched_rules)
            reason = f"{llm_reason} | Upgraded by matched rule"

    hallucination_flags = find_hallucination_flags(clause, reason, matched_rules)

    return {
        "id": case.get("id", ""),
        "title": case.get("title", ""),
        "text": clause,
        "expected_risk": expected_risk,
        "predicted_risk": predicted_risk,
        "expected_rules": expected_rules,
        "matched_rules": matched_rules,
        "reason": reason,
        "llm_risk": llm_risk,
        "llm_reason": llm_reason,
        "correct": predicted_risk == expected_risk,
        "false_positive": RISK_RANK[predicted_risk] > RISK_RANK[expected_risk],
        "false_negative": RISK_RANK[predicted_risk] < RISK_RANK[expected_risk],
        "hallucination_flags": hallucination_flags,
    }


def calculate_metrics(results):
    total = len(results)
    correct = sum(1 for result in results if result["correct"])
    false_positives = sum(1 for result in results if result["false_positive"])
    false_negatives = sum(1 for result in results if result["false_negative"])
    hallucinations = sum(1 for result in results if result["hallucination_flags"])

    high_expected = [result for result in results if result["expected_risk"] == "high"]
    high_detected = [
        result
        for result in high_expected
        if RISK_RANK[result["predicted_risk"]] >= RISK_RANK["high"]
    ]

    risky_expected = [result for result in results if result["expected_risk"] != "no-risk"]
    risky_detected = [
        result
        for result in risky_expected
        if result["predicted_risk"] != "no-risk"
    ]

    predicted_risky = [result for result in results if result["predicted_risk"] != "no-risk"]
    true_predicted_risky = [
        result
        for result in predicted_risky
        if result["expected_risk"] != "no-risk"
    ]

    return {
        "total_cases": total,
        "accuracy": round((correct / total) * 100, 2) if total else 0,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "hallucination_flags": hallucinations,
        "high_risk_recall": round((len(high_detected) / len(high_expected)) * 100, 2) if high_expected else 0,
        "risky_recall": round((len(risky_detected) / len(risky_expected)) * 100, 2) if risky_expected else 0,
        "risky_precision": round((len(true_predicted_risky) / len(predicted_risky)) * 100, 2) if predicted_risky else 0,
    }


def run_evaluation(cases, use_llm=False):
    results = [analyze_case(case, use_llm=use_llm) for case in cases]
    return {
        "metrics": calculate_metrics(results),
        "results": results,
    }

