from functools import wraps
from logging import getLogger

from django.shortcuts import redirect
from django.conf import settings


from dwapi.datawiz import DW


def dw_auth_required(sign_in_url=None):
    """
    A decorator that restricts access to specified pages if user is not dw authorized.

    As authorization url DW_AUTH_URL setting can be used if it is provided else default is used.
    if any troubles then redirects to authorization page.

    :param sign_in_url: is used in redirect call when is not None and nothing else where provided.
    :return: decorated view.
    """
    def wrapper(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            dw = getattr(request, 'dw', None)
            if dw and isinstance(dw, DW):
                try:
                    return view_func(request, *args, **kwargs)
                except TypeError as error:
                    getLogger('django.dw_client').error(error, error.args)
            return redirect(getattr(settings, 'DW_CLIENT_SIGN_IN_URL', sign_in_url or 'dw-client:auth:sign:in'))
        return _wrapped_view
    return wrapper
