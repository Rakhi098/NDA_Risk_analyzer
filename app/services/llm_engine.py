from langchain_ollama import ChatOllama
import json
import os
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Initialize LLM
try:
    llm = ChatOllama(
        model=os.getenv("LLM_MODEL", "gemma:2b"),
        temperature=float(os.getenv("LLM_TEMPERATURE", 0)),
        base_url=os.getenv("LLM_BASE_URL", "http://localhost:11434")
    )
    logger.info(f"LLM initialized: {os.getenv('LLM_MODEL', 'gemma:2b')}")
except Exception as e:
    logger.error(f"Failed to initialize LLM: {str(e)}")
    llm = None


def analyze_clause(clause):
    """
    Analyze a legal clause for risks using AI model.
    
    Args:
        clause: Text of the clause to analyze
        
    Returns:
        dict: Risk assessment with 'risk' and 'reason' keys
    """
    if llm is None:
        logger.warning("LLM not available, returning no-risk")
        return {"risk": "no-risk", "reason": "LLM unavailable"}
    
    # Truncate clause to avoid token limits on lightweight models
    short_clause = clause[:600]
    
    prompt = f"""TASK: Analyze this legal clause for risks. ONLY report risks FOUND IN THE TEXT.

CRITICAL RULE: DO NOT HALLUCINATE. If the clause doesn't mention a risk, DO NOT REPORT IT.

RISK TYPES (only report if explicitly in text):
- HIGH: unlimited or one-sided liability, indefinite term, overly broad scope, exclusive jurisdiction,
  automatic IP assignment, unilateral indemnity, punitive liquidated damages, or a non-compete restriction
- MEDIUM: concerning terms but potentially negotiable
- NO-RISK: standard, normal, balanced

WHAT IS NOT RISKY (even if mentioned):
- Requiring return/destruction of materials = PROTECTIVE, not risky
- Listing exclusions = LIMITING scope, not risky
- Standard IP clauses = not risky unless unfair
- Injunctive relief alone = MEDIUM at most, not HIGH

EXAMPLES:
Text: "shall promptly return or destroy all materials"
Analysis: NO-RISK, reason: "Requires return/destruction of materials - protective clause"

Text: "subject to unlimited liability for any damages"
Analysis: HIGH, reason: "Subject to unlimited liability for breach damages"

Text: "The Receiving Party must maintain confidentiality"
Analysis: NO-RISK, reason: "Standard confidentiality obligation"

ANALYZE THIS CLAUSE - return JSON only:
{short_clause}

Format: {{"risk":"high|medium|no-risk","reason":"specific risk found in this clause"}}"""
    
    try:
        response = llm.invoke(prompt)
        content = response.content.strip()
        
        # Try to extract JSON from response
        # Handle case where model returns extra text
        if '{' in content:
            json_start = content.index('{')
            json_end = content.rindex('}') + 1
            json_str = content[json_start:json_end]
        else:
            json_str = content
        
        result = json.loads(json_str)
        
        # Validate risk level
        risk = result.get("risk", "no-risk").lower()
        if risk not in ["no-risk", "medium", "high"]:
            risk = "no-risk"
        
        logger.debug(f"Clause analyzed: {risk} risk")
        
        return {
            "risk": risk,
            "reason": result.get("reason", "")
        }
        
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse JSON response: {str(e)}")
        return {"risk": "no-risk", "reason": "analysis parsing failed"}
    except Exception as e:
        logger.error(f"Clause analysis failed: {str(e)}", exc_info=True)
        return {"risk": "no-risk", "reason": "analysis failed"}
