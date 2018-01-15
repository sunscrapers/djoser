class ValidationError(BaseException):
    def __init__(self, errors):
        self.errors = errors
