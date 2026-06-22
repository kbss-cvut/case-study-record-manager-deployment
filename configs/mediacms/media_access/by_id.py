import os
from django.http import HttpResponse, Http404
from django.conf import settings


BY_ID_PREFIX = '/by-id/'


class ByIdMiddleware:
    """Resolve `/by-id/<friendly_token>` to the original media file via X-Accel-Redirect.

    Mirrors ProtectedMediaMiddleware: Django performs auth and the DB lookup
    by Media.friendly_token, then hands the byte serving to nginx through
    `/protected-media/` (the internal alias defined in nginx.conf).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path.startswith(BY_ID_PREFIX):
            return self.get_response(request)

        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())

        friendly_token = request.path[len(BY_ID_PREFIX):].strip('/')
        if not friendly_token:
            raise Http404()

        from files.models import Media
        media = Media.objects.filter(friendly_token=friendly_token).first()
        if not media or not media.media_file:
            raise Http404()

        try:
            rel_path = os.path.relpath(media.media_file.path, settings.MEDIA_ROOT)
        except ValueError:
            raise Http404()

        response = HttpResponse()
        response['X-Accel-Redirect'] = f'/protected-media/{rel_path}'
        response['Content-Type'] = ''
        return response
