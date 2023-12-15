from flask.views import MethodView
from flask_smorest import Api, Blueprint

from components.lib.basic_routes.app_route import AppRoute
from components.lib.basic_routes.ui_view import UiView
from components.lib.flask_router.flask_router import (
    FlaskRouter,
    FlaskViewAdapter,
)
from components.lib.smorest_router.openapi_view import OpenapiView
from components.utils.extensions import prettify


class SmorestConfig:
    def __init__(
        self,
        title: str,
        version: str,
        openapi_version: str,
        name: str = "",
        url_prefix: str = "/",
        swagger_ui: str | None = None,
        redoc_ui: str | None = None,
        rapidoc_ui: str | None = None,
        swagger_ui_url: str | None = None,
        redoc_ui_url: str | None = None,
        rapidoc_ui_url: str | None = None,
    ) -> None:
        self.name = name
        self.API_TITLE = title
        self.API_VERSION = version
        self.OPENAPI_VERSION = openapi_version
        self.OPENAPI_URL_PREFIX = url_prefix

        self.OPENAPI_SWAGGER_UI_PATH = swagger_ui
        self.OPENAPI_REDOC_PATH = redoc_ui
        self.OPENAPI_RAPIDOC_PATH = rapidoc_ui

        self.OPENAPI_SWAGGER_UI_URL = (
            swagger_ui_url or "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
        )
        self.OPENAPI_REDOC_URL = (
            redoc_ui_url
            or "https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"
        )
        self.OPENAPI_RAPIDOC_URL = (
            rapidoc_ui_url or "https://unpkg.com/rapidoc/dist/rapidoc-min.js"
        )


class SmorestViewAdapter(FlaskViewAdapter):
    def __init__(self, view: UiView, blueprint: Blueprint = None) -> None:
        self.blueprint = blueprint
        super().__init__(view)
        self._init_docs()

    def _init_docs(self):
        methods = self.view._view_methods()
        for call, call_method in methods.items():
            self._init_docs_for_call_method(call, call_method)

    def _init_docs_for_call_method(self, call: str, call_method):
        call_viewdoc: dict = getattr(call_method, "_viewdoc", None)
        blueprint = self.blueprint

        if call_viewdoc and blueprint:
            call_method = self._add_calldocs(call_viewdoc, call_method, blueprint)

        setattr(self.view, call, call_method)

    def _add_calldocs(self, viewdoc: dict, call_method, blueprint: Blueprint):
        arg = (viewdoc, blueprint)
        call_method = self._add_apidoc("response", *arg, call_method)
        call_method = self._add_apidoc("alt_response", *arg, call_method)
        call_method = self._add_apidoc("arguments", *arg, call_method)
        return call_method

    @staticmethod
    def _add_apidoc(decoration: str, viewdoc: dict, blueprint: Blueprint, call_method):
        docs: list[dict] = viewdoc.get(decoration)
        if docs:
            for doc in docs:
                call_method = getattr(blueprint, decoration)(**doc)(call_method)

        return call_method


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
