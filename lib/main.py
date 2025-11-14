from typing import Optional

from redis import Redis

from components.lib.smorest_router.smorest_config import SmorestConfig
from components.lib.smorest_router.smorest_router import SmorestRouter
from components.lib.storage_manager.database_manager import DatabaseManager
from components.lib.storage_manager.storage_manager import StorageManager
from lib.src.features.routes import FeaturesRoutes
from lib.src.test_api import TestRoute

# Use the WSL2 IP address for Redis
WSL_REDIS_IP = "172.22.165.186"  # Replace with your actual WSL2 IP if different


def create_app(storage: Optional[StorageManager] = None):

    return SmorestRouter(
        __name__,
        openapi_spec={
            SmorestConfig(
                title="doto",
                url_prefix="/features",
                version="v1",
                openapi_version="3.0.0",
                swagger_ui="ui",
            ): [
                FeaturesRoutes(),
            ],
            SmorestConfig(
                title="test",
                name="test",
                url_prefix="/test",
                version="v1",
                openapi_version="3.0.0",
                swagger_ui="ui",
            ): [
                TestRoute(),
            ]
        },
        storage=storage,
    )


if __name__ == "__main__":
    db = DatabaseManager(DB_URI="postgresql://postgres:123@localhost:5432/dodb")
    redis = Redis(
        host=WSL_REDIS_IP,
        port=6379,
    )
    storage =  StorageManager(db=db, redis=redis)
    app = create_app(storage=storage)
    app.run(debug=True)
