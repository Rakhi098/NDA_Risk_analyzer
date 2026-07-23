# NDA Risk Analyzer

A lightweight NDA review tool that extracts text from uploaded documents, splits it into clauses, runs rule-based checks and optional local LLM analysis, and returns a structured risk report.

## Features

- Supports PDF, DOCX, TXT, MD, and CSV uploads.
- Extracts text locally using PyMuPDF and Tesseract OCR when needed.
- Splits documents into clauses and evaluates them for risk.
- Returns a JSON response with overall risk and per-clause findings.

## Project structure

```text
NDA_Solution/
├── app/
│   ├── api/
│   │   └── upload.py
│   ├── services/
│   │   ├── clause_splitter.py
│   │   ├── evaluation.py
│   │   ├── llm_engine.py
│   │   ├── parser.py
│   │   ├── recommendations.py
│   │   ├── risk_scorer.py
│   │   └── rule_engine.py
│   ├── ui/
│   │   ├── streamlit_app.py
│   │   └── testing_report.py
│   └── utils/
│       └── logger.py
├── config.py
├── main.py
├── requirements.txt
├── sample_docs/
├── tests/
└── logs/
```

## Requirements

- Python 3.8+
- Ollama for local LLM inference
- Tesseract OCR for scanned PDFs
- pip

## Setup

```bash
cd NDA_Solution
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

If needed, start Ollama and pull a model:

```bash
ollama serve
ollama pull gemma:2b
```

## Run the app

### API

```bash
uvicorn main:app --reload --port 8000
```

### Streamlit UI

```bash
streamlit run app/ui/streamlit_app.py
```

## API endpoints

- GET /health
- POST /upload

## Run tests

```bash
pytest tests/ -v
```

## Notes

- The FastAPI entrypoint is main.py.
- The upload workflow is handled in app/api/upload.py.
- The main flow runs locally and does not require cloud services.
