from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)


class LoginRequiredMiddleware:
    """
    Middleware to require login for all pages except login, logout, and admin.
    """
    
    # URLs that don't require authentication
    EXEMPT_URLS = [
        settings.LOGIN_URL,
        '/admin/',
        '/static/',
        '/media/',
        '/favicon.ico',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip middleware for exempt URLs
        if any(request.path.startswith(url) for url in self.EXEMPT_URLS):
            return self.get_response(request)
        
        # Check if user is authenticated
        if not request.user.is_authenticated:
            logger.warning(f'Unauthenticated access attempt to: {request.path}')
            return redirect(settings.LOGIN_URL + f'?next={request.path}')
        
        # Check if user is active (optional additional security)
        if not request.user.is_active:
            logger.warning(f'Inactive user access attempt: {request.user.username}')
            return redirect(settings.LOGIN_URL)
        
        return self.get_response(request)
