import pytest


@pytest.fixture
def test_user(db):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user_kwargs = {
        User.USERNAME_FIELD: 'test',
        'email': 'test@localhost',
        'password': 'testing123'
    }
    return User.objects.create_user(**user_kwargs)


@pytest.fixture
def test_inactive_user(db):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user_kwargs = {
        User.USERNAME_FIELD: 'test',
        'email': 'test@localhost',
        'password': 'testing123',
        'is_active': False,
    }
    return User.objects.create_user(**user_kwargs)
