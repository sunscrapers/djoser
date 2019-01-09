from rest_framework import serializers

from djoser import exceptions


def default_view_pipeline_adapter(request, steps):
    try:
        result = Pipeline(request, steps).run()
    except exceptions.ValidationError as e:
        raise serializers.ValidationError(e.errors)

    return result.get('response_data')


class Pipeline(object):
    def __init__(self, request, steps):
        self._request = request
        self._steps = steps

    def run(self):
        context = {'request': self._request}
        for step_func in self._steps:
            step_context = step_func(**context) or {}
            context.update(step_context)

        return context
