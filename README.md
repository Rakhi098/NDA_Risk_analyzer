# NDA Risk Analyzer

A production-style AI-Assisted NDA Risk Analyzer using FastAPI, local lightweight LLMs via Ollama, PyMuPDF, and hybrid AI + validation-rule architecture.

## Features

- 📄 **PDF Upload & Extraction**: Upload NDA PDFs and automatically extract text using PyMuPDF
- 🤖 **AI-Assisted Analysis**: Leverages Gemma 2B model via Ollama for intelligent clause analysis
- ✅ **Deterministic Validation**: Rule-based validation layer supports and enhances AI analysis
- 📊 **Risk Scoring**: Comprehensive risk assessment with confidence metrics
- 🔒 **Offline Processing**: Fully offline - no cloud dependencies, all processing local
- 📈 **Structured Output**: Clean JSON API responses with detailed clause analysis
- 🎨 **Interactive UI**: Streamlit frontend for user-friendly document analysis
- 🔍 **Color-Coded Results**: Visual risk indicators (High=Red, Medium=Orange, Low=Green)

## Architecture

```
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
Validation Rules (Supporting)
    ↓
Risk Scoring & Aggregation
    ↓
Structured Risk Report
```

## Tech Stack

| Component     | Technology          |
|---------------|-------------------|
| Backend API   | FastAPI           |
| PDF Parsing   | PyMuPDF (fitz)    |
| AI Model      | Gemma 2B via Ollama|
| LLM Framework | LangChain Ollama  |
| Language      | Python 3.8+       |
| UI            | Streamlit         |
| Local LLM     | Ollama            |
| Logging       | Python logging    |

## Prerequisites

### Required
- Python 3.8+
- Ollama (for local LLM inference)
- pip/conda for package management

### System Requirements
- Minimum 4GB RAM
- ~2GB disk space for model download
- Modern CPU with AVX support (for Ollama)

## Installation

### 1. Clone and Setup Environment

```bash
# Navigate to project directory
cd NDA_Solution

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 2. Install Ollama

Download and install Ollama from https://ollama.ai

```bash
# Start Ollama service
ollama serve

# In another terminal, pull Gemma model
ollama pull gemma:2b
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Update `.env` file with your settings:
```bash
# LLM Configuration
LLM_MODEL=gemma:2b
LLM_BASE_URL=http://localhost:11434

# API Configuration  
API_HOST=0.0.0.0
API_PORT=8000
```

## Usage

### Run API Server

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

API will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### Run Streamlit UI

```bash
# In another terminal
streamlit run app/ui/streamlit_app.py
```

UI will open at `http://localhost:8501`

### API Endpoints

#### Health Check
```bash
GET /health
```

Response:
```json
{"status": "ok"}
```

#### Upload and Analyze NDA
```bash
POST /upload
Content-Type: multipart/form-data

File: nda_document.pdf
```

Response:
```json
{
  "overall_risk": "High",
  "total_risky_clauses": 2,
  "analysis": [
    {
      "clause": "The Receiving Party shall be subject to unlimited liability...",
      "risk": "high",
      "reason": "Unlimited liability exposure",
      "matched_rules": ["Unlimited Liability"]
    }
  ]
}
```

## Project Structure

```
NDA_Solution/
├── app/
│   ├── api/
│   │   └── upload.py              # Upload endpoint
│   ├── services/
│   │   ├── parser.py              # PDF text extraction
│   │   ├── clause_splitter.py     # Clause segmentation
│   │   ├── llm_engine.py          # AI analysis via Ollama
│   │   ├── rule_engine.py         # Validation rules
│   │   └── risk_scorer.py         # Risk aggregation & scoring
│   ├── utils/
│   │   └── logger.py              # Structured logging
│   ├── ui/
│   │   └── streamlit_app.py       # Streamlit frontend
│   └── main.py                    # FastAPI application
├── sample_docs/                   # Sample NDA documents
├── logs/                          # Log files (auto-generated)
├── .env                           # Configuration file
├── requirements.txt               # Python dependencies
├── README.md                      # This file
└── COPILOT_CONTEXT.md            # Project context
```

## Configuration

### Environment Variables (.env)

```env
# API Configuration
API_HOST=0.0.0.0                  # API server host
API_PORT=8000                     # API server port
API_RELOAD=true                   # Auto-reload in development
API_WORKERS=1                     # Number of workers

# LLM Configuration
LLM_MODEL=gemma:2b               # Model name
LLM_TEMPERATURE=0                 # LLM temperature (0 for deterministic)
LLM_BASE_URL=http://localhost:11434  # Ollama endpoint

# Clause Processing
MAX_CLAUSES=20                    # Max clauses to analyze
MIN_CLAUSE_LENGTH=50              # Min clause length
MAX_CLAUSE_LENGTH=2000            # Max clause length

# Logging
LOG_LEVEL=INFO                    # Logging level
LOG_DIR=logs                      # Logs directory

# Environment
ENVIRONMENT=development           # development/production
DEBUG=true                        # Enable debug mode
```

## Risk Assessment Rules

### AI Analysis Risks
- **High Risk**: Unlimited liability, indefinite obligations, broad confidentiality scope
- **Medium Risk**: Concerning but potentially negotiable clauses
- **No Risk**: Standard, balanced, commonly acceptable clauses

### Validation Rules
Supported patterns:
- Unlimited Liability
- Missing Duration
- Exclusive Jurisdiction
- Broad Confidentiality
- Unilateral Obligations

### Risk Scoring Logic
```
Any HIGH risk clause → Overall HIGH
Else any MEDIUM risk clause → Overall MEDIUM
Else → Overall LOW
```

## API Response Format

### Successful Analysis
```json
{
  "overall_risk": "High",
  "total_risky_clauses": 2,
  "analysis": [
    {
      "clause": "Clause text here...",
      "risk": "high",
      "reason": "Risk explanation",
      "matched_rules": ["Rule 1", "Rule 2"]
    }
  ]
}
```

### Error Response
```json
{
  "detail": "Error description"
}
```

## Logging

Logs are automatically generated in the `logs/` directory with:
- **File**: Daily log files with rotation
- **Console**: Real-time logging output
- **Format**: Timestamp, module name, log level, message
- **Retention**: 5 backup files kept per module

Example log entry:
```
2024-05-26 10:30:45 - app.api.upload - INFO - Document parsed successfully
```

## Error Handling

The application implements graceful error handling:

| Error Scenario | Response |
|---|---|
| Invalid PDF | 400 - Only PDF files are accepted |
| Empty file | 400 - Empty file uploaded |
| No clauses found | 400 - No clauses found in document |
| LLM failure | Continues with rule validation only |
| Connection error | 500 - Internal server error |

## Performance Considerations

- **Gemma 2B Model**: ~1-2 seconds per clause on modern CPU
- **Memory**: ~4GB RAM minimum, 8GB+ recommended
- **Processing**: Sequential clause analysis (can be parallelized)
- **Caching**: No caching implemented (future enhancement)

## Security Considerations

- **No external APIs**: All processing local
- **No cloud uploads**: Documents never leave your system
- **Structured logging**: Sensitive data not logged
- **CORS enabled**: API accessible from frontend

## Production Deployment

### Docker (Recommended)
```bash
# Build Docker image
docker build -t nda-analyzer .

# Run container
docker run -p 8000:8000 -p 11434:11434 nda-analyzer
```

### Systemd Service
```bash
sudo cp systemd/nda-analyzer.service /etc/systemd/system/
sudo systemctl enable nda-analyzer
sudo systemctl start nda-analyzer
```

## Development

### Running Tests
```bash
pytest tests/ -v
```

### Linting & Formatting
```bash
black app/
pylint app/
```

### Type Checking
```bash
mypy app/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Future Enhancements

- [ ] Vector database (FAISS) for clause similarity
- [ ] Multi-model support (LLaMA, Mistral)
- [ ] Parallel clause processing
- [ ] Response caching
- [ ] Advanced UI with clause comparison
- [ ] Batch PDF processing
- [ ] Custom rule creation UI
- [ ] PDF markup and annotations
- [ ] Export to PDF reports

## Troubleshooting

### Ollama Connection Issues
```bash
# Check if Ollama is running
curl http://localhost:11434

# Restart Ollama
ollama serve
```

### Memory Issues
- Reduce MAX_CLAUSES in .env
- Use a smaller model (e.g., tinyllama)
- Increase system RAM or reduce MAX_CLAUSE_LENGTH

### Slow Processing
- GPU acceleration not yet implemented
- Process documents in batches
- Use smaller model version

## License

This project is provided as-is for educational and research purposes.

## Support

For issues or questions:
1. Check logs in `logs/` directory
2. Review COPILOT_CONTEXT.md for architecture details
3. Enable DEBUG=true in .env for verbose logging

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Ollama Documentation](https://github.com/ollama/ollama)
- [LangChain Documentation](https://python.langchain.com/)
- [PyMuPDF Documentation](https://pymupdf.readthedocs.io/)
- [Streamlit Documentation](https://docs.streamlit.io/)
