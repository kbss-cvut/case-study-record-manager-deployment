import os
from django.http import HttpResponse, Http404
from django.conf import settings

class ProtectedMediaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path.startswith('/media/'):
            return self.get_response(request)
        protected = getattr(settings, 'PROTECTED_MEDIA_ENABLED', True)
        if protected and not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())

        path = request.path[len('/media/'):]
        file_path = os.path.join(settings.MEDIA_ROOT, path)

        if not os.path.exists(file_path):
            raise Http404()

        response = HttpResponse()
        response['X-Accel-Redirect'] = f'/protected-media/{path}'
        response['Content-Type'] = ''
        return response

        return self.get_response(request)