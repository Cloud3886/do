from test._utils.setup_test import SetupTests

import pytest


@pytest.fixture(scope="session")
def setup_tests() -> SetupTests:
    return SetupTests()
