class BasePipeline(object):
    steps = None

    def __init__(self, request, steps=None):
        self._request = request
        if steps is not None:
            self.steps = steps

    def run(self):
        assert self.steps is not None, (
            'Pipeline `steps` have not been specified. '
            'They are required to run the pipeline.'
        )

        context = {'request': self._request}
        for step_func in self.steps:
            step_context = step_func(self._request, context) or {}
            context.update(step_context)

        return context
