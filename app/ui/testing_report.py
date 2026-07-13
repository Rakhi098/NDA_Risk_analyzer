import json
from datetime import datetime

import streamlit as st

from app.services.evaluation import DEFAULT_EVAL_DATASET, load_eval_cases, run_evaluation


st.set_page_config(
    page_title="NDA Testing Report",
    page_icon="TEST",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("NDA Analyzer Testing Report")
st.markdown("Accuracy, false-positive, false-negative, and hallucination checks for the current analyzer logic.")

with st.sidebar:
    st.header("Evaluation Setup")
    st.caption(f"Default dataset: {DEFAULT_EVAL_DATASET}")

    uploaded_dataset = st.file_uploader(
        "Use custom JSON dataset",
        type="json",
        help="Upload a JSON list with text, expected_risk, and optional expected_rules.",
    )

    use_llm = st.checkbox(
        "Include local LLM analysis",
        value=False,
        help="Runs Ollama/Gemma locally. Slower, but closer to full app behavior.",
    )

    st.divider()
    st.markdown(
        """
        **Risk labels**
        - `high`
        - `medium`
        - `no-risk`
        """
    )


def get_cases():
    if uploaded_dataset is None:
        return load_eval_cases()

    return json.loads(uploaded_dataset.getvalue().decode("utf-8"))


try:
    cases = get_cases()
except Exception as exc:
    st.error(f"Could not load evaluation dataset: {exc}")
    st.stop()

st.info(f"Loaded {len(cases)} evaluation cases. Report generated at {datetime.now().strftime('%H:%M:%S')}.")

if st.button("Run Evaluation", type="primary", use_container_width=True):
    with st.spinner("Running evaluation..."):
        try:
            report = run_evaluation(cases, use_llm=use_llm)
        except Exception as exc:
            st.error(f"Evaluation failed: {exc}")
            st.stop()

    metrics = report["metrics"]
    results = report["results"]

    st.subheader("Scorecard")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Accuracy", f"{metrics['accuracy']}%")
    col2.metric("High-Risk Recall", f"{metrics['high_risk_recall']}%")
    col3.metric("Risky Precision", f"{metrics['risky_precision']}%")
    col4.metric("Risky Recall", f"{metrics['risky_recall']}%")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Cases", metrics["total_cases"])
    col2.metric("False Positives", metrics["false_positives"])
    col3.metric("False Negatives", metrics["false_negatives"])
    col4.metric("Hallucination Flags", metrics["hallucination_flags"])

    st.divider()
    st.subheader("Case Results")

    summary_rows = [
        {
            "ID": result["id"],
            "Title": result["title"],
            "Expected": result["expected_risk"],
            "Predicted": result["predicted_risk"],
            "Correct": result["correct"],
            "False Positive": result["false_positive"],
            "False Negative": result["false_negative"],
            "Hallucination Flags": ", ".join(result["hallucination_flags"]),
        }
        for result in results
    ]
    st.dataframe(summary_rows, use_container_width=True, hide_index=True)

    misses = [result for result in results if not result["correct"]]
    hallucinations = [result for result in results if result["hallucination_flags"]]

    left, right = st.columns(2)
    with left:
        st.subheader("Misses")
        if not misses:
            st.success("No incorrect predictions in this run.")
        for result in misses:
            with st.expander(f"{result['id']} - {result['title']}"):
                st.write(f"Expected: `{result['expected_risk']}`")
                st.write(f"Predicted: `{result['predicted_risk']}`")
                st.write(f"Matched rules: {', '.join(result['matched_rules']) or 'None'}")
                st.write(result["text"])

    with right:
        st.subheader("Hallucination Checks")
        if not hallucinations:
            st.success("No hallucination flags in this run.")
        for result in hallucinations:
            with st.expander(f"{result['id']} - {result['title']}"):
                st.write(f"Flags: {', '.join(result['hallucination_flags'])}")
                st.write(f"Reason: {result['reason']}")
                st.write(result["text"])

    st.divider()
    st.subheader("Full JSON Report")
    st.download_button(
        "Download Report JSON",
        data=json.dumps(report, indent=2),
        file_name="nda_testing_report.json",
        mime="application/json",
        use_container_width=True,
    )
    st.json(report)
else:
    st.subheader("Dataset Preview")
    preview_rows = [
        {
            "ID": case.get("id", ""),
            "Title": case.get("title", ""),
            "Expected Risk": case.get("expected_risk", ""),
            "Expected Rules": ", ".join(case.get("expected_rules", [])),
        }
        for case in cases
    ]
    st.dataframe(preview_rows, use_container_width=True, hide_index=True)
