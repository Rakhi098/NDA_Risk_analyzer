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


def test_rules_detect_broad_scope_and_one_sided_duties_in_scanned_nda_text():
    """OCR text from a mutual NDA must not be reported as having no risks."""
    broad_scope = (
        '"Confidential Information" shall include all information or material that has '
        "or could have commercial value or other utility in the business."
    )
    one_sided_duty = (
        "Receiving Party shall hold and maintain the Confidential Information in strictest "
        "confidence for the sole and exclusive benefit of the Disclosing Party."
    )

    assert validate_clause(broad_scope) == ["Broad Confidentiality Scope"]
    assert validate_clause(one_sided_duty) == ["Unilateral Obligations"]
