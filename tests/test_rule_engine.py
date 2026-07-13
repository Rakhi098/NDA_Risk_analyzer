import json
from pathlib import Path

from app.services.rule_engine import validate_clause


FIXTURES = Path(__file__).parent / "fixtures" / "nda_eval_cases.json"


def test_rules_detect_all_expected_risks_in_evaluation_fixture():
    """Known high/medium-risk clauses must not depend on the local LLM."""
    cases = json.loads(FIXTURES.read_text(encoding="utf-8-sig"))

    for case in cases:
        assert validate_clause(case["text"]) == case["expected_rules"], case["id"]
