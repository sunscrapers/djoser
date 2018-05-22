Adjustment
==========

If you need to customize any serializer behaviour you can use
the ``DJOSER['SERIALIZERS']`` setting to use your own serializer classes in the built-in views.
Or if you need to completely change the default djoser behaviour,
you can always override djoser views with your own custom ones.

Define custom ``urls`` instead of reusing ``djoser.urls``:

.. code-block:: python

    urlpatterns = patterns('',
        (...),
        url(r'^users/create/$', views.CustomRegistrationView.as_view()),
    )

Define custom view/serializer (inherit from one of ``djoser`` class) and override necessary method/field:

.. code-block:: python

    class CustomUserCreateView(djoser.views.UserCreateView):

        def perform_create(self, *args, **kwargs):
            super(UserCreateView, self).perform_update(serializer)
            your_custom_actions()

You could check ``djoser`` API in source code:

* `djoser.views <https://github.com/sunscrapers/djoser/blob/master/djoser/views.py>`_
* `djoser.serializers <https://github.com/sunscrapers/djoser/blob/master/djoser/serializers.py>`_
