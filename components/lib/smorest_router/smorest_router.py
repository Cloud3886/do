from typing import Any, Callable

from flask_smorest import Api, Blueprint

from components.lib.basic_routes.app_route import AppRoute
from components.lib.basic_routes.ui_view import UiView
from components.lib.database_manager.database_manager import DatabaseManager
from components.lib.flask_router import FlaskRouter

from .openapi_view import OpenapiView
from .smorest_config import SmorestConfig
from .smorest_view_adapter import SmorestViewAdapter


class SmorestRouter(FlaskRouter):
    def __init__(
        self,
        name: str,
        *,
        views: list[UiView] | None = None,
        routes: list[AppRoute[UiView]] | None = None,
        openapi_spec: dict[SmorestConfig, list[AppRoute[OpenapiView]]] | None = None,
        config: object | None = None,
        db: DatabaseManager | None = None,
        error_handlers: dict[type[Exception], Callable[[Any], Any]] = {},
    ) -> None:
        self._initialize_app(name)
        self._initialize_fields()
        self._initialize_configuration(config)
        self._initialize_db(db)
        self._initialize_views(views)
        self._initialize_routes(routes)
        self._initialize_openapi_specs(openapi_spec)
        self._initialize_error_handlers(error_handlers)
        self._initialize_teardowns()

    def register_view(self, view: UiView, main: Blueprint | None = None):
        adapter = self._create_adapter(view, main)

        if main:
            view_func = adapter.build_view_class()
            main.add_url_rule(view.endpoint, view.name, view_func=view_func)
        else:
            view_func = adapter.build_view_function()
            self.app.add_url_rule(view.endpoint, view.name, view_func=view_func)

    def register_route_with_api(self, api: Api, route: AppRoute[OpenapiView]) -> None:
        config = self.apis[api]
        self._prepend_config_prefix_to_route(config, route)
        bp = self._configure_route(route)
        api.register_blueprint(bp)

    def add_api(self, config: SmorestConfig, routes: list[AppRoute[OpenapiView]] = []):
        self._register_openapi_config_with_app(config)
        api = self._create_openapi(config)
        self._store_openapi(api, config)

        for route in routes:
            self.register_route_with_api(api, route)

        return api

    def generate_openapi_json(self, api: Api) -> dict:
        return api.spec.to_dict()  # type: ignore

    def _initialize_fields(self):
        super()._initialize_fields()
        self.apis: dict[Api, SmorestConfig] = {}

    def _initialize_openapi_specs(
        self, openapi_spec: dict[SmorestConfig, list[AppRoute[OpenapiView]]] | None
    ):
        if openapi_spec:
            for config, routes in openapi_spec.items():
                self.add_api(config, routes)

    def _prepend_config_prefix_to_route(
        self,
        config: SmorestConfig,
        route: AppRoute[OpenapiView],
    ):
        config_has_prefix = (
            config.OPENAPI_URL_PREFIX and config.OPENAPI_URL_PREFIX != "/"
        )
        if config_has_prefix:
            route.prefix = config.OPENAPI_URL_PREFIX + (route.prefix or "")

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

    def _store_openapi(self, api: Api, config: SmorestConfig):
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

    def _create_adapter(
        self,
        view: UiView,
        blueprint: Blueprint | None = None,
    ) -> SmorestViewAdapter:
        return SmorestViewAdapter(self, view, blueprint)

    def _create_blueprint(self, route: AppRoute) -> Blueprint:
        bp = Blueprint(
            name=route.name,
            import_name=route._root,
            url_prefix=route.prefix,
            template_folder=route.template_path,
            subdomain=route.subdomain,
        )
        return bp
