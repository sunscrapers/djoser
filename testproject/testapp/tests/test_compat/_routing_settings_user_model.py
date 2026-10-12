"""
Settings for the subprocess in test_url_routing that swaps the user model.

AUTH_USER_MODEL can only be chosen before Django starts, so the test runs a fresh
interpreter with this module and ROUTING_AUTH_USER_MODEL in its environment.
"""

import os

from testproject.settings import *  # noqa: F401,F403

AUTH_USER_MODEL = os.environ["ROUTING_AUTH_USER_MODEL"]
ROOT_URLCONF = "testapp.tests.test_compat._routing_urls_documented"
