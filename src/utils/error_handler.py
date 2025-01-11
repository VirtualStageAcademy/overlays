import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

def handle_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Handle errors consistently across the application
    
    Args:
        error: The exception that was raised
        context: Optional dictionary with additional context about the error
        
    Returns:
        Dict with error details formatted for response
    """
    error_type = type(error).__name__
    error_message = str(error)
    
    # Log the error with context
    logger.error(f"Error: {error_type} - {error_message}")
    if context:
        logger.error(f"Context: {context}")
        
    # Return formatted error response
    return {
        'error': error_type,
        'message': error_message,
        'context': context or {}
    } 