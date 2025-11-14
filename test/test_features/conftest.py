from typing import Any, Generator
from test._utils.domain_tester import DomainTester
from test._utils.setup_test import SetupTests

import pytest
from redis import Redis

from components.lib.smorest_router.smorest_router import SmorestRouter
from components.lib.storage_manager import DatabaseManager, StorageManager
from lib.main import WSL_REDIS_IP, create_app


@pytest.fixture
def router(request: pytest.FixtureRequest, setup_tests: SetupTests) -> Generator[SmorestRouter, Any, Any]:
    db_path = setup_tests.setup_db(request.node.name)
    redis = Redis(host=WSL_REDIS_IP, port=6379)
    db = DatabaseManager(f"sqlite:///{db_path}", True)
    storage = StorageManager(db=db, redis=redis, debug=True)
    router = create_app(storage=storage)
    yield router
    # setup_tests.cleanup_redis(redis_port)


@pytest.fixture
def app(router: SmorestRouter) -> DomainTester:
    tester = DomainTester(router, router.storage)
    return tester
