from flask_smorest import Api, Blueprint

from components.lib.basic_routes.app_route import AppRoute
from components.lib.basic_routes.ui_view import UiView
from components.lib.flask_router import FlaskRouter

from .openapi_view import OpenapiView
from .smorest_config import SmorestConfig
from .smorest_view_adapter import SmorestViewAdapter


class SmorestRouter(FlaskRouter):
    def __init__(
        self,
        name: str,
        *,
        views: list[UiView] = None,
        routes: list[AppRoute[UiView]] = None,
        openapi_spec: dict[SmorestConfig, list[AppRoute[OpenapiView]]] = None,
        DB_URI: str | None = None,
    ) -> None:
        super().__init__(name, views=views, routes=routes, DB_URI=DB_URI)
        self.apis: dict[Api, SmorestConfig] = {}
        if openapi_spec:
            for config, routes in openapi_spec.items():
                self.add_api(config, routes)

    def register_view(self, view: UiView, main: Blueprint = None):
        adapter = self._create_adapter(view, main)
        view_func = (
            adapter.build_view_class() if main else adapter.build_view_function()
        )
        (main or self.app).add_url_rule(view.endpoint, view.name, view_func=view_func)

    def _create_adapter(
        self,
        view: UiView,
        blueprint: Blueprint = None,
    ) -> SmorestViewAdapter:
        return SmorestViewAdapter(view, blueprint)

    def _create_blueprint(self, route: AppRoute) -> Blueprint:
        bp = Blueprint(
            name=route.name,
            import_name=route._root,
            url_prefix=route.prefix,
            template_folder=route.template_path,
            subdomain=route.subdomain,
        )
        return bp

    def register_route_with_api(self, api: Api, route: AppRoute[OpenapiView]) -> None:
        config = self.apis[api]

        config_has_prefix = (
            config.OPENAPI_URL_PREFIX and config.OPENAPI_URL_PREFIX != "/"
        )
        if config_has_prefix:
            route.prefix = config.OPENAPI_URL_PREFIX + (route.prefix or "")

        bp = self._configure_route(route)
        api.register_blueprint(bp)

    def add_api(self, config: SmorestConfig, routes: list[AppRoute[OpenapiView]] = []):
        self._register_openapi_config_with_app(config)
        api = self._create_openapi(config)
        self._record_openapi(api, config)

        for route in routes:
            self.register_route_with_api(api, route)

        return api

    def _register_openapi_config_with_app(self, config: SmorestConfig):
        name_prefix = (config.name.upper() + "_") if config.name else ""
        self.app.config[name_prefix + "OPENAPI_URL_PREFIX"] = (
            config.OPENAPI_URL_PREFIX or "/"
        )
        self.app.config[name_prefix + "OPENAPI_REDOC_PATH"] = config.OPENAPI_REDOC_PATH
        self.app.config[name_prefix + "OPENAPI_REDOC_URL"] = config.OPENAPI_REDOC_URL
        self.app.config[
            name_prefix + "OPENAPI_SWAGGER_UI_PATH"
        ] = config.OPENAPI_SWAGGER_UI_PATH
        self.app.config[
            name_prefix + "OPENAPI_SWAGGER_UI_URL"
        ] = config.OPENAPI_SWAGGER_UI_URL
        self.app.config[
            name_prefix + "OPENAPI_RAPIDOC_PATH"
        ] = config.OPENAPI_RAPIDOC_PATH
        self.app.config[
            name_prefix + "OPENAPI_RAPIDOC_URL"
        ] = config.OPENAPI_RAPIDOC_URL

    def _record_openapi(self, api: Api, config: SmorestConfig):
        self.apis[api] = config
        if config.name:
            setattr(self, f"api_{config.name.lower()}", api)
        else:
            self.api = api

    def _create_openapi(self, config: SmorestConfig):
        api = Api(
            self.app,
            config_prefix=config.name.upper(),
            spec_kwargs={
                "title": config.API_TITLE,
                "version": config.API_VERSION,
                "openapi_version": config.OPENAPI_VERSION,
            },
        )
        return api
