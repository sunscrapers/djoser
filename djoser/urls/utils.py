from typing import Dict, Type, Callable, Any, Optional
from django.http import (
    HttpRequest,
    HttpResponseNotAllowed,
    HttpResponseBase,
)
from rest_framework.views import APIView


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
