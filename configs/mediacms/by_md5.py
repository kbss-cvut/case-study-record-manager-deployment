import os
from django.http import HttpResponse, Http404
from django.conf import settings


BY_MD5_PREFIX = '/by-md5/'


class ByMd5Middleware:
    """Resolve `/by-md5/<md5>` to the original media file via X-Accel-Redirect.

    Mirrors ProtectedMediaMiddleware: Django performs auth and the DB lookup
    by Media.md5sum, then hands the byte serving to nginx through
    `/protected-media/` (the internal alias defined in nginx.conf).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path.startswith(BY_MD5_PREFIX):
            return self.get_response(request)

        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())

        md5 = request.path[len(BY_MD5_PREFIX):].strip('/')
        if not md5:
            raise Http404()

        from files.models import Media
        media = Media.objects.filter(md5sum=md5).first()
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
