from .models import Log


def log_middleware(get_response):
    def middleware(request):
        path_start = request.path.startswith
        if (path_start('/cars') or path_start('/controller') or path_start('/pki')):
            try:
                Log.objects.create(
                    url=request.path,
                    session=dict(request.session.items()),
                    body=request.body,
                    user=request.user,
                    additional={}
                )
            except UnicodeDecodeError:
                Log.objects.create(
                    url=request.path,
                    session=dict(request.session.items()),
                    body='UnicodeDecodeError',
                    user=request.user,
                    additional={}
                )
        response = get_response(request)
        return response
    return middleware
