from django.shortcuts import redirect
from django.conf import settings

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        login_url = settings.LOGIN_URL
        if not request.user.is_authenticated and not request.path.startswith(login_url):
            return redirect(login_url)

        return self.get_response(request)
