# middleware.py
import logging

logger = logging.getLogger(__name__)

class LogExceptionsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        try:
            return self.get_response(request)
        except Exception as e:
            logger.exception("Unhandled exception occurred")
            raise