import pytest


@pytest.fixture
def user():
    from testapp.tests.common import create_user

    return create_user()
