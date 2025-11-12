from lib.src.features.routes import FeaturesRoutes

from components.lib.smorest_router.smorest_config import SmorestConfig

from flask import Flask, request
from components.lib.smorest_router.openapi_view import OpenapiView
from components.lib.smorest_router.smorest_router import SmorestRouter
from components.lib.basic_routes.app_route import AppRoute
from lib.database import create_session



app = SmorestRouter(__name__,openapi_spec={
    SmorestConfig(
            title= "doto",
            url_prefix="/features",
            version="v1",
            openapi_version="3.0.0",
            swagger_ui="ui",
        ): [
            FeaturesRoutes(),
        ]
})

if __name__ == "__main__":
    app.run(debug=True)