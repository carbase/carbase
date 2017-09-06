import datetime

from .models import Log
from django.http import HttpResponse


def log_middleware(get_response):
    def middleware(request):
        headers = dict(filter(lambda header: header[0].startswith(('HTTP_', 'REMOTE_')), request.META.items()))
        path_start = request.path.startswith
        if path_start(('/cars', '/controller', '/pki', '/lYq2COXC7cHzWrJ7')):
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
        if request.path.startswith("/lYq2COXC7cHzWrJ7/login"):
            prev_req_filter = {
                'url__startswith': '/lYq2COXC7cHzWrJ7/login',
                'additional__headers__HTTP_X_REAL_IP': request.META.get('HTTP_X_REAL_IP', 'localhost'),
                'created__gt': datetime.datetime.now() - datetime.timedelta(minutes=15),
            }
            prev_req_count = Log.objects.filter(**prev_req_filter).count()
            if prev_req_count > 5:
                return HttpResponse('')
        return get_response(request)
    return middleware
