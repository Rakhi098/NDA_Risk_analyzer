import re
import os
from app.utils.logger import get_logger

logger = get_logger(__name__)


def split_clauses(text):
    """
    Split NDA text into meaningful legal clauses.
    
    Uses regex-based pattern matching for numbered clauses with fallback
    to paragraph splitting.
    
    Args:
        text: Full NDA text
        
    Returns:
        list: List of clause strings
    """
    max_clauses = int(os.getenv("MAX_CLAUSES", 20))
    min_clause_length = int(os.getenv("MIN_CLAUSE_LENGTH", 50))
    max_clause_length = int(os.getenv("MAX_CLAUSE_LENGTH", 2000))
    
    # Pattern for numbered clauses (e.g., "1. Confidentiality")
    pattern = r'\d+\.\s+[A-Za-z\s]+'
    matches = list(re.finditer(pattern, text))
    
    logger.debug(f"Found {len(matches)} potential clause markers")
    
    clauses = []
    
    if matches:
        # Use regex-based segmentation
        for i in range(len(matches)):
            start = matches[i].start()
            
            if i + 1 < len(matches):
                end = matches[i + 1].start()
            else:
                end = len(text)
            
            clause = text[start:end].strip()
            
            # Filter by length
            if min_clause_length <= len(clause) <= max_clause_length:
                clauses.append(clause)
                logger.debug(f"Added clause: {len(clause)} characters")
    
    if not clauses:
        # Fallback: split by paragraphs
        logger.info("No numbered clauses found, falling back to paragraph splitting")
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        clauses = [p for p in paragraphs if min_clause_length <= len(p) <= max_clause_length]
    
    # Limit to max clauses
    if len(clauses) > max_clauses:
        logger.warning(f"Limiting clauses from {len(clauses)} to {max_clauses}")
        clauses = clauses[:max_clauses]
    
    logger.info(f"Extracted {len(clauses)} clauses for analysis")
    return clauses