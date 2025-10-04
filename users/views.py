from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
import logging

logger = logging.getLogger(__name__)


class CustomLoginView(LoginView):
    """Custom login view with enhanced functionality"""
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        """Redirect to dashboard after successful login"""
        return reverse_lazy('home')
    
    def form_valid(self, form):
        """Log successful login attempts"""
        response = super().form_valid(form)
        logger.info(f'User {self.request.user.username} logged in successfully')
        messages.success(self.request, f'Welcome back, {self.request.user.username}!')
        return response
    
    def form_invalid(self, form):
        """Log failed login attempts"""
        username = form.cleaned_data.get('username', 'unknown')
        logger.warning(f'Failed login attempt for username: {username}')
        messages.error(self.request, 'Invalid username or password.')
        return super().form_invalid(form)


class CustomLogoutView(LogoutView):
    """Custom logout view with logging"""
    next_page = reverse_lazy('users:login')
    
    def dispatch(self, request, *args, **kwargs):
        """Log logout events"""
        if request.user.is_authenticated:
            logger.info(f'User {request.user.username} logged out')
            messages.info(request, 'You have been logged out successfully.')
        return super().dispatch(request, *args, **kwargs)


@login_required
def user_profile(request):
    """Display user profile information"""
    return render(request, 'users/profile.html', {
        'user': request.user
    })
