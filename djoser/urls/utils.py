from typing import Dict, Type, Callable, Any, List, Optional

from django.contrib.auth import get_user_model
from django.http import HttpRequest, HttpResponseBase
from django.urls import URLPattern, re_path
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView


def user_url_name(suffix: str) -> str:
    """
    The name 2.x's router gave a user URL, e.g. "user-me".

    The router named the routes after the user model class, so a project whose model is
    CustomUser reverses "customuser-me".
    """
    return f"{get_user_model()._meta.object_name.lower()}-{suffix}"


def schema_patterns(regex: str, dispatcher: Callable) -> List[URLPattern]:
    """
    URL patterns that show a dispatcher's views to schema generators.

    The generators of DRF, drf-spectacular and drf-yasg describe each URL pattern whose
    callback is a DRF view, so they skip a dispatcher, which hands each method to a
    different view. These patterns repeat the dispatcher's path once per view. Placed
    after the dispatcher's pattern, they are never reached when resolving a request.
    """
    view_classes = dict.fromkeys(dispatcher.method_view_map.values())
    return [re_path(regex, view_class.as_view()) for view_class in view_classes]


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

    allowed_methods = list(method_view_map.keys())
    if "GET" in method_view_map and "HEAD" not in method_view_map:
        allowed_methods.append("HEAD")
    if "OPTIONS" not in method_view_map:
        allowed_methods.append("OPTIONS")
    allow_header = ", ".join(allowed_methods)
    # Given to the fallback view so DRF answers 405 for every method that is not
    # mapped here, even one the fallback view class itself implements.
    fallback_method_names = [method.lower() for method in allowed_methods]
    fallback_view_class = next(iter(method_view_map.values()), APIView)

    def dispatcher(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseBase:
        method = request.method
        view_class = method_view_map.get(method)
        if view_class is None and method == "HEAD":
            # Django serves HEAD with the GET handler.
            view_class = method_view_map.get("GET")
        if view_class is not None:
            return view_class.as_view()(request, *args, **kwargs)

        # OPTIONS, or a method no view is mapped to. 2.x routed every method through
        # one DRF view, so authentication ran first and the client got DRF's own
        # 401, JSON 405 or OPTIONS metadata. Hand the request to a mapped view with
        # its method list narrowed to what this path accepts to get the same result.
        view = fallback_view_class.as_view(http_method_names=fallback_method_names)
        response = view(request, *args, **kwargs)
        # DRF derives Allow from the handlers of that one view; advertise the path.
        response["Allow"] = allow_header
        return response

    # CsrfViewMiddleware decides exemption by inspecting the callable the URL resolver
    # returns, which is this dispatcher rather than the wrapped view. Without this,
    # the csrf_exempt that APIView.as_view() applies never reaches the middleware and
    # CSRF is enforced on every djoser endpoint routed through a dispatcher.
    dispatcher = csrf_exempt(dispatcher)

    # Store allowed methods as attribute for URL test introspection
    setattr(dispatcher, "_allowed_methods", list(method_view_map.keys()))
    # Read by schema_patterns().
    dispatcher.method_view_map = method_view_map
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
