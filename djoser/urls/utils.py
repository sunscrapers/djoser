from typing import Dict, Type, Callable, Any, Optional
from django.http import (
    HttpRequest,
    HttpResponseNotAllowed,
    HttpResponsePermanentRedirect,
)
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

try:
    from django.http import HttpResponseBase
except ImportError:
    # Django < 4.1
    from django.http.response import HttpResponseBase
from rest_framework.views import APIView


class HttpResponsePermanentRedirectPreserveMethod(HttpResponsePermanentRedirect):
    """
    308 Permanent Redirect.

    Unlike a 301, clients must repeat the request with the original method and body,
    which is what makes this usable in front of POST-only endpoints.
    """

    status_code = 308


class AppendSlashRedirectView(View):
    """
    Redirects a slash-less URL to its canonical slash-terminated form.

    djoser 2.x matched these endpoints with an optional trailing slash. Switching to
    path() made the slash mandatory, so callers using the slash-less form got a 404.
    """

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any):
        target = f"{request.path}/"
        query_string = request.META.get("QUERY_STRING")
        if query_string:
            target = f"{target}?{query_string}"
        return HttpResponsePermanentRedirectPreserveMethod(target)


def create_dispatcher(
    method_view_map: Dict[str, Type[APIView]],
) -> Callable[[HttpRequest, Any, Any], HttpResponseBase]:
    """
    Creates a dispatcher function that routes requests to different views based on HTTP
    method.

    Args:
        method_view_map: Dict mapping HTTP methods to view classes
                        e.g., {"GET": ListView, "POST": CreateView}

    Returns:
        A dispatcher function that can be used directly in URL patterns
    """

    def dispatcher(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseBase:
        method = request.method
        if method in method_view_map:
            view_class = method_view_map[method]
            return view_class.as_view()(request, *args, **kwargs)
        else:
            allowed_methods = list(method_view_map.keys())
            return HttpResponseNotAllowed(allowed_methods)

    # CsrfViewMiddleware decides exemption by inspecting the callable the URL resolver
    # returns, which is this dispatcher rather than the wrapped view. Without this,
    # the csrf_exempt that APIView.as_view() applies never reaches the middleware and
    # CSRF is enforced on every djoser endpoint routed through a dispatcher.
    dispatcher = csrf_exempt(dispatcher)

    # Store allowed methods as attribute for URL test introspection
    setattr(dispatcher, "_allowed_methods", list(method_view_map.keys()))
    return dispatcher


def create_configurable_dispatcher(
    method_config_map: Dict[str, str],
) -> Optional[Callable[[HttpRequest, Any, Any], HttpResponseBase]]:
    """
    Creates a dispatcher function using configurable view paths from djoser settings.

    Args:
        method_config_map: Dict mapping HTTP methods to view configuration keys
                          e.g., {"GET": "user_me_get", "PUT": "user_me_put"}

    Returns:
        A dispatcher function, or None if no views are configured
    """
    from djoser.conf import settings

    method_view_map = {}

    for method, config_key in method_config_map.items():
        if config_key is not None:
            view_class = getattr(settings.VIEWS, config_key, None)
            if view_class is not None:
                method_view_map[method] = view_class

    if not method_view_map:
        return None

    return create_dispatcher(method_view_map)
