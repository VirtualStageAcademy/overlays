from typing import Any, Optional
from functools import wraps
import logging

def handle_error(error_type: Optional[type] = Exception) -> Any:
    """
    Decorator to handle errors in functions
    
    Args:
        error_type: Type of error to catch (defaults to Exception)
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except error_type as e:
                logging.error(f"Error in {func.__name__}: {str(e)}")
                # Re-raise the error after logging
                raise
        return wrapper
    return decorator 