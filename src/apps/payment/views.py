from django.views.decorators.csrf import csrf_exempt

from .helpers import http_code
from .api import set_callback


@csrf_exempt
def callback(request):

    invoke = set_callback(request)

    if invoke == 0:
        return http_code('OK', 200)

    return http_code('Not Approved', 200)