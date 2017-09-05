from .models import Log


def log_middleware(get_response):
    def middleware(request):
        headers = dict(filter(lambda header: header[0].startswith(('HTTP_', 'REMOTE_')), request.META.items()))
        path_start = request.path.startswith
        if (path_start('/cars') or path_start('/controller') or path_start('/pki')):
            try:
                Log.objects.create(
                    url=request.path,
                    session=dict(request.session.items()),
                    body=request.body,
                    user=request.user,
                    additional={'headers': headers},
                )
            except UnicodeDecodeError:
                Log.objects.create(
                    url=request.path,
                    session=dict(request.session.items()),
                    body='UnicodeDecodeError',
                    user=request.user,
                    additional={'headers': headers},
                )
        response = get_response(request)
        return response
    return middleware


def anti_brut_middleware(get_response):
    def middleware(request):
        return get_response(request)
    return middleware
