from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.parser import parse_document
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
    """Upload and analyze an NDA PDF document"""
    logger.info(f"Received upload request for file: {file.filename}")
    
    try:
        # Validate file type
        if file.content_type not in ["application/pdf", "application/x-pdf"]:
            logger.warning(f"Invalid file type: {file.content_type}")
            raise HTTPException(status_code=400, detail="Only PDF files are accepted")
        
        # Read and parse document
        content = await file.read()
        if not content:
            logger.warning("Empty file uploaded")
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        logger.info(f"File size: {len(content)} bytes")
        
        try:
            text = parse_document(content)
            logger.info(f"Document parsed successfully, extracted {len(text)} characters")
        except Exception as e:
            logger.error(f"PDF parsing failed: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Failed to parse PDF: {str(e)}")
        
        if not text or len(text.strip()) == 0:
            logger.warning("PDF contains no extractable text")
            raise HTTPException(status_code=400, detail="PDF contains no extractable text")
        
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
                analysis = analyze_clause(clause)
                risk = analysis.get("risk", "no-risk")
                reason = analysis.get("reason", "")

                # Always check rule validation (don't skip for "no-risk" clauses)
                matched_rules = validate_clause(clause)
                
                # If rules matched, upgrade risk level based on rule severity
                if matched_rules:
                    if risk == "no-risk":
                        # Check the severity of matched rules by looking up their names in RULES
                        rule_severities = []
                        for rule_id, rule_config in RULES.items():
                            if rule_config["name"] in matched_rules:
                                rule_severities.append(rule_config.get("severity", "medium"))
                        
                        if "high" in rule_severities:
                            risk = "high"
                            reason = f"Pattern matched: {', '.join(matched_rules)}"
                        else:
                            risk = "medium"
                            reason = f"Pattern matched: {', '.join(matched_rules)}"
                        logger.info(f"Clause {idx}: LLM missed risk, but rules detected: {matched_rules}")
                    else:
                        # If LLM detected risk, confirm it matches rules
                        for rule_id, rule_config in RULES.items():
                            if rule_config["name"] in matched_rules:
                                rule_severity = rule_config.get("severity", "medium")
                                # Upgrade to high if any matched rule is high
                                if rule_severity == "high":
                                    risk = "high"
                                    break
                
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