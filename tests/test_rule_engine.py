import json
from pathlib import Path

from app.services.rule_engine import validate_clause


FIXTURES = Path(__file__).parent / "fixtures" / "nda_eval_cases.json"


def test_rules_detect_all_expected_risks_in_evaluation_fixture():
    """Known high/medium-risk clauses must not depend on the local LLM."""
    cases = json.loads(FIXTURES.read_text(encoding="utf-8-sig"))

    for case in cases:
        assert validate_clause(case["text"]) == case["expected_rules"], case["id"]


def test_missing_duration_is_detected_when_no_time_limit_is_explicit():
    clause = (
        "The confidentiality obligations shall continue for the duration of the business relationship, "
        "and there is no time limit."
    )

    assert validate_clause(clause) == ["Missing Duration"]
