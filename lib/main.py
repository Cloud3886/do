from typing import Optional

from components.lib.smorest_router.smorest_config import SmorestConfig
from components.lib.smorest_router.smorest_router import SmorestRouter
from components.lib.storage_manager.storage_manager import StorageManager
from lib.src.features.routes import FeaturesRoutes


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
            ]
        },
        storage=storage,
    )


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
