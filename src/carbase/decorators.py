from functools import wraps

from django.http import HttpResponseForbidden


def login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if (request.session.get('user_serialNumber') or request.user.is_authenticated):
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()
    return _wrapped_view
