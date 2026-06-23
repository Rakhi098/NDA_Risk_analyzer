# NDA Risk Analyzer — End-to-End GitHub Copilot Development Guide

## Project Overview

Build a production-style AI-Assisted NDA Risk Analyzer using FastAPI, local lightweight LLMs via Ollama, PyMuPDF, and hybrid AI + validation-rule architecture.

The system should:

* Accept NDA PDF uploads
* Extract text from PDFs
* Split documents into meaningful legal clauses
* Perform AI-assisted risk analysis on each clause
* Validate identified risks using deterministic rule validation
* Return structured JSON output
* Show only risky clauses
* Generate overall contract risk score
* Work fully offline using local lightweight LLMs via Ollama
* Follow clean architecture and modular backend design

---

# Final Architecture

## Architecture Principle

AI is the primary clause analyzer.
Rules act as supporting validation and explainability layer.

Flow:

```text
PDF Upload
   ↓
FastAPI Endpoint
   ↓
PyMuPDF Text Extraction
   ↓
Clause Segmentation
   ↓
AI Clause Analysis (Primary)
   ↓
Validation Rules
   ↓
Confidence Enhancement
   ↓
Structured Risk Report
```

---

# Tech Stack

| Component        | Technology          |
| ---------------- | ------------------- |
| Backend API      | FastAPI             |
| PDF Parsing      | PyMuPDF             |
| AI Model         | Gemma 2B via Ollama |
| LLM Framework    | LangChain Ollama    |
| Language         | Python              |
| API Docs         | Swagger/OpenAPI     |
| Local Inference  | Ollama              |
| Future UI        | Streamlit           |
| Future Vector DB | FAISS               |

---

# Folder Structure

````text
nda_risk_analyzer/
│
├── app/
│   ├── api/
│   │   └── upload.py
│   │
│   ├── services/
│   │   ├── parser.py
│   │   ├── clause_splitter.py
│   │   ├── llm_engine.py
│   │   ├── rule_engine.py
│   │   └── risk_scorer.py
│   │
│   ├── utils/
│   │   └── logger.py
│   │
│   └── main.py
│
├── ui/
│   └── streamlit_app.py
│
├── sample_docs/
├── requirements.txt
├── README.md
└── .env
```text
nda_risk_analyzer/
│
├── app/
│   ├── api/
│   │   └── upload.py
│   │
│   ├── services/
│   │   ├── parser.py
│   │   ├── clause_splitter.py
│   │   ├── llm_engine.py
│   │   ├── rule_engine.py
│   │   └── risk_scorer.py
│   │
│   ├── utils/
│   │   └── logger.py
│   │
│   └── main.py
│
├── sample_docs/
├── requirements.txt
├── README.md
└── .env
````

---

# Functional Requirements

## PDF Upload

* Upload NDA PDF via FastAPI endpoint
* Validate file type
* Handle invalid uploads gracefully
* Return structured errors

---

## Text Extraction

Use PyMuPDF.

Requirements:

* Extract text page-by-page
* Preserve clause readability
* Remove excessive whitespace
* Ignore page numbers and headers when possible

---

## Clause Segmentation

Split NDA into meaningful legal clauses.

Examples:

* Confidentiality Obligations
* Term and Survival
* Liability and Indemnification
* Governing Law

Use:

* regex-based segmentation
* fallback paragraph splitting

Clause segmentation should support:

```text
1. Heading Style
2. Multi-line Clauses
3. Legal Formatting
```

---

# AI-Assisted Clause Analysis

## AI Responsibilities

AI must:

* Identify risky clauses
* Determine severity
* Generate short explanation
* Return structured JSON only

Allowed risks:

```text
no-risk
medium
high
```

---

## AI Prompting Requirements

Prompts must:

* be short
* optimized for local lightweight models
* request JSON-only output
* avoid hallucination
* clearly define standard clauses

Example guidance:

```text
Standard confidentiality clauses are usually not risky.
Only identify serious contractual risks.
```

---

## AI JSON Format

```json
{
  "risk": "high",
  "reason": "Unlimited liability exposure"
}
```

---

# Validation Rule Layer

Rules DO NOT replace AI.

Rules only:

* validate known risks
* improve confidence
* improve explainability
* support hybrid architecture

---

## Supported Rule Patterns

Examples:

* unlimited liability
* indefinite duration
* exclusive jurisdiction
* broad confidentiality
* missing exclusions
* unilateral obligations

---

## Rule Output

```json
{
  "matched_rules": [
    "Unlimited Liability",
    "Missing Duration"
  ]
}
```

---

# Risk Scoring

Rules:

```text
Any HIGH → overall HIGH
Else any MEDIUM → overall MEDIUM
Else LOW
```

---

# Streamlit UI Layer

## UI Architecture

```text
Streamlit UI
     ↓
FastAPI Backend
     ↓
AI Analysis + Validation Rules
```

---

## Streamlit Responsibilities

The Streamlit frontend should:

* Upload NDA PDFs
* Send files to FastAPI backend
* Display overall contract risk
* Display risky clauses only
* Show color-coded severity levels
* Show matched validation rules
* Show AI explanations
* Display mitigation recommendations
* Support expandable clause sections

---

## UI Color Coding

| Risk    | Color  |
| ------- | ------ |
| High    | Red    |
| Medium  | Orange |
| No Risk | Green  |

---

## Recommended Streamlit Components

Use:

* st.file_uploader
* st.expander
* st.markdown
* st.container
* st.columns
* st.warning
* st.error
* st.success
* st.metric

---

## UI Design Goal

The UI should remain:

* lightweight
* clean
* readable
* presentation-friendly
* suitable for dissertation demonstration

---

# Final API Response

```json
{
  "overall_risk": "High",
  "total_risky_clauses": 2,
  "analysis": [
    {
      "clause": "The Receiving Party shall be subject to unlimited liability...",
      "risk": "high",
      "reason": "Unlimited liability exposure",
      "matched_rules": [
        "Unlimited Liability"
      ]
    }
  ]
}
```

---

# Non-Functional Requirements

## Performance

* Support lightweight local inference
* Handle low-RAM environments
* Limit clause size for local models
* Avoid sending full documents to LLM

---

## Reliability

Implement graceful degradation.

If LLM fails:

* system should not crash
* validation rules should still work
* structured error logging required

---

## Privacy

* Fully offline processing
* No cloud APIs
* No external document sharing

---

## Logging

Add structured logging:

* upload events
* parsing failures
* AI failures
* JSON parsing errors
* latency metrics

---

# Error Handling Requirements

Handle:

* invalid PDFs
* empty PDFs
* LLM unavailable
* invalid AI JSON
* timeout failures
* malformed clauses

Return proper HTTP status codes.

---

# Production-Level Coding Requirements

Code must:

* follow modular architecture
* use async FastAPI endpoints
* include type hints
* include logging
* separate services cleanly
* avoid hardcoded values
* use reusable utility functions
* use environment variables
* maintain readable structure

---

# Future Enhancements

Design code keeping future extensibility in mind.

Potential future additions:

* Streamlit dashboard
* clause highlighting UI
* RAG using FAISS
* persistent database
* contract comparison
* export reports
* multi-document support
* cloud deployment

---

# Important Architectural Constraints

DO NOT:

* make rules primary analyzer
* hardcode all risks
* depend fully on keyword matching
* send full documents to AI
* trust AI blindly without validation

Architecture must remain:

```text
AI = Primary Analyzer
Rules = Validation Support Layer
```

---

# Final Goal

Build a clean, modular, production-style AI-assisted NDA risk analysis backend suitable for:

* dissertation demonstration
* resume project
* architecture discussion
* future extensibility
* offline local AI inference

The implementation should prioritize:

* explainability
* modularity
* maintainability
* realistic hybrid AI architecture
* clean API design
