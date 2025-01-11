from typing import Any, Dict


class ErrorHandler:
    """Centralized error handling"""
    @staticmethod
    def oauth_error(message: str) -> Dict[str, Any]:
        """Return formatted OAuth error response"""
        return {
            'status': 'error',
            'message': message
        }

    @staticmethod
    def ws_error(message: str) -> Dict[str, Any]:
        """Return formatted WebSocket error response"""
        return {
            'status': 'error',
            'message': message
        } 