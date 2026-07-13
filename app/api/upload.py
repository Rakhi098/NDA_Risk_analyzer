from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.parser import is_supported_document, parse_document
from app.services.clause_splitter import split_clauses
from app.services.llm_engine import analyze_clause
from app.services.rule_engine import validate_clause, RULES
from app.services.risk_scorer import format_risk_response, assess_risk_confidence
from app.services.recommendations import format_enhanced_response
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload and analyze an NDA document in PDF, text, or DOCX form."""
    logger.info(f"Received upload request for file: {file.filename}")
    
    try:
        # Read before validating: browsers may send application/octet-stream.
        content = await file.read()
        if not content:
            logger.warning("Empty file uploaded")
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        logger.info(f"File size: {len(content)} bytes")

        if not is_supported_document(content, file.filename, file.content_type):
            logger.warning(f"Unsupported file type: {file.content_type}, {file.filename}")
            raise HTTPException(
                status_code=400,
                detail="Supported formats: PDF, DOCX, TXT, MD, and CSV",
            )
        
        try:
            text = parse_document(content, file.filename, file.content_type)
            logger.info(f"Document parsed successfully, extracted {len(text)} characters")
        except Exception as e:
            logger.error(f"Document parsing failed: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Failed to extract document text: {str(e)}")
        
        if not text or len(text.strip()) == 0:
            logger.warning("Document contains no extractable text")
            raise HTTPException(status_code=400, detail="Document contains no extractable text")
        
        # Split clauses
        try:
            clauses = split_clauses(text)
            logger.info(f"Document split into {len(clauses)} clauses")
        except Exception as e:
            logger.error(f"Clause splitting failed: {str(e)}")
            raise HTTPException(status_code=500, detail="Error processing document clauses")
        
        if not clauses:
            logger.warning("No clauses found in document")
            raise HTTPException(status_code=400, detail="No clauses found in document")
        
        results = []
        for idx, clause in enumerate(clauses, 1):
            try:
                logger.debug(f"Analyzing clause {idx}/{len(clauses)}")
                # Check deterministic rules before calling the LLM. This makes explicit
                # risks reliable even when the lightweight local model misses them or
                # returns malformed JSON, and avoids an unnecessary LLM call.
                matched_rules = validate_clause(clause)
                if matched_rules:
                    rule_severities = [
                        rule_config.get("severity", "medium")
                        for rule_config in RULES.values()
                        if rule_config["name"] in matched_rules
                    ]
                    risk = "high" if "high" in rule_severities else "medium"
                    reason = f"Pattern matched: {', '.join(matched_rules)}"
                    analysis = {"risk": risk, "reason": reason}
                    logger.info(f"Clause {idx}: rules detected {matched_rules}")
                else:
                    analysis = analyze_clause(clause)
                    risk = analysis.get("risk", "no-risk")
                    reason = analysis.get("reason", "")
                
                # Skip only if both LLM and rules found no risk
                if risk == "no-risk" and not matched_rules:
                    logger.debug(f"Clause {idx}: No risk detected by LLM or rules")
                    continue
                
                # HALLUCINATION FILTER: If LLM says "unlimited liability" but clause doesn't mention it, 
                # and no rule matched it, downgrade risk or skip
                if "unlimited liability" in reason.lower() and "Unlimited Liability" not in matched_rules:
                    if risk == "high":
                        # Check if clause actually mentions liability terms
                        if "unlimited" not in clause.lower() and "liability" not in clause.lower():
                            logger.warning(f"Clause {idx}: Hallucinated 'unlimited liability' - skipping")
                            continue
                        # If it mentions liability but no rule matched, classify as medium
                        if risk == "high":
                            risk = "medium"
                            reason = "Clause contains liability-related terms but pattern not matched by rules"
                
                # If no matched rules and LLM flagged as high, be more conservative
                if risk == "high" and not matched_rules:
                    logger.debug(f"Clause {idx}: HIGH risk but no rules matched - downgrading to MEDIUM")
                    risk = "medium"

                risk_assessment = assess_risk_confidence(analysis, matched_rules, risk)
                risk = risk_assessment["risk"]
                
                result = {
                    "clause": clause,
                    "risk": risk,
                    "reason": reason,
                    "matched_rules": matched_rules,
                    "confidence": risk_assessment["confidence"]
                }
                results.append(result)
                logger.info(f"Clause {idx}: {risk.upper()} risk detected")
                
            except Exception as e:
                logger.error(f"Clause {idx} analysis failed: {str(e)}", exc_info=True)
                continue
        
        # Format final response with enhanced details (risk scores, recommendations)
        response = format_enhanced_response(results, total_clauses=len(clauses))
        logger.info(f"Analysis complete: {response['overall_risk']} risk, {response['total_risky_clauses']} risky clauses")
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in upload endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
