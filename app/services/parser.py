import fitz
from app.utils.logger import get_logger

logger = get_logger(__name__)


def parse_document(content):
    """
    Extract text from PDF document using PyMuPDF.
    
    Args:
        content: PDF file content (bytes)
        
    Returns:
        str: Extracted text from all pages
        
    Raises:
        Exception: If PDF parsing fails
    """
    try:
        doc = fitz.open(stream=content, filetype="pdf")
        text = ""
        
        logger.info(f"PDF document opened with {doc.page_count} pages")
        
        for page_num, page in enumerate(doc, 1):
            try:
                page_text = page.get_text()
                text += page_text
                logger.debug(f"Extracted {len(page_text)} characters from page {page_num}")
            except Exception as e:
                logger.warning(f"Failed to extract text from page {page_num}: {str(e)}")
                continue
        
        doc.close()
        logger.info(f"Total extracted text: {len(text)} characters")
        
        return text
        
    except Exception as e:
        logger.error(f"PDF parsing failed: {str(e)}", exc_info=True)
        raise