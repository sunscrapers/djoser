from django.conf.urls import url
from django.contrib.auth import get_user_model
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns

from djoser import views
from djoser.conf import settings


class CustomRouter(DefaultRouter):
    """
    Router class that disables the PUT method.
    """

    def get_urls(self):
        """
        Use the registered viewsets to generate a list of URL patterns.
        """
        ret = []

        for prefix, viewset, basename in self.registry:
            lookup = self.get_lookup_regex(viewset)
            routes = self.get_routes(viewset)

            for route in routes:

                # Only actions which actually exist on the viewset will be bound
                mapping = self.get_method_map(viewset, route.mapping)
                if not mapping:
                    continue

                # Build the url pattern
                regex = route.url.format(
                    prefix=prefix,
                    lookup=lookup,
                    trailing_slash=self.trailing_slash
                )

                # If there is no prefix, the first part of the url is probably
                #   controlled by project's urls.py and the router is in an app,
                #   so a slash in the beginning will (A) cause Django to give
                #   warnings and (B) generate URLS that will require using '//'.
                if not prefix and regex[:2] == '^/':
                    regex = '^' + regex[2:]

                initkwargs = route.initkwargs.copy()
                initkwargs.update({
                    'basename': basename,
                    'detail': route.detail,
                })

                name = route.name.format(basename=basename)

                # checking allowed urls from djoser configuration
                if name not in list(settings.ALLOW_URLS.keys()):
                    continue
                # checking allowed methods from djoser configuration
                copy_mapping = mapping.copy()
                allowed_methods = settings.ALLOW_URLS[name]
                for method in copy_mapping.keys():
                    if method not in allowed_methods:
                        del mapping[method]

                view = viewset.as_view(mapping, **initkwargs)
                ret.append(url(regex, view, name=name))

        if self.include_root_view:
            view = self.get_api_root_view(api_urls=ret)
            root_url = url(r'^$', view, name=self.root_view_name)
            ret.append(root_url)

        if self.include_format_suffixes:
            ret = format_suffix_patterns(ret)

        return ret


router = CustomRouter()
router.register("users", views.UserViewSet)

User = get_user_model()

urlpatterns = router.urls
