import os

import pytest
from ninja.testing import TestAsyncClient

from apps.api.app import api


def pytest_generate_tests(metafunc):
    os.environ['NINJA_SKIP_REGISTRY'] = 'yes'


@pytest.fixture
def api_client():
    api.urls_namespace = 'test'
    return TestAsyncClient(api)
