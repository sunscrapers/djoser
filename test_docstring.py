def test_function():
    """
    This is a very long docstring that exceeds 88 characters and should be wrapped by
    the docformatter pre-commit hook.
    """
    pass


class TestClass:
    """
    Another very long docstring that exceeds the 88 character limit and should be
    formatted properly by docformatter when we commit.
    """

    def method(self):
        """
        Short docstring.
        """
        pass
