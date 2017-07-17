from functools import wraps

from django.http import HttpResponseForbidden
from django.template import loader


def login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if (request.session.get('user_serialNumber') or request.user.is_authenticated):
            return view_func(request, *args, **kwargs)
        else:
            template = loader.get_template('403.html')
            return HttpResponseForbidden(template.render(request=request))
    return _wrapped_view
