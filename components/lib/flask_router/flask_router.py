from typing import Any

from flask import (
    Blueprint,
    Flask,
)
from flask.globals import app_ctx

from components.lib.basic_routes.app_route import AppRoute
from components.lib.basic_routes.ui_view import UiView
from components.lib.database_manager import DatabaseManager

from .flask_test_client import FlaskRouterTester
from .flask_view_adapter import FlaskViewAdapter
from .teardown_recorder import Teardown, TeardownRecorder


class FlaskRouter:
    def __init__(
        self,
        name: str,
        *,
        views: list[UiView] | None = None,
        routes: list[AppRoute[UiView]] | None = None,
        config: object | None = None,
        db: DatabaseManager | None = None,
    ) -> None:
        self._initialize_app(name)
        self._initialize_fields()
        self._initialize_configuration(config)
        self._initialize_views(views)
        self._initialize_routes(routes)
        self._initialize_db(db)
        self._initialize_teardowns()

    @staticmethod
    def create_app(name: str):
        return Flask(name)

    def run(
        self,
        host: str | None = None,
        port: int | None = None,
        debug: bool | None = None,
        load_dotenv: bool = True,
        **options: Any,
    ):
        self.app.run(host, port, debug, load_dotenv, **options)

    def tester(self):
        return self.app.test_client()

    def register_view(self, view: UiView, main: Blueprint = None):
        adapter = self._create_adapter(view)
        view_func = adapter.build_view_function()
        (main or self.app).add_url_rule(view.endpoint, view.name, view_func=view_func)

    def register_route(self, route: AppRoute[UiView], main: Blueprint = None):
        bp = self._configure_route(route)
        (main or self.app).register_blueprint(bp)

    def register_db(self, db: DatabaseManager) -> bool:
        if not hasattr(self, "db"):
            self.db = db
            self._configure_db_session_with_flask(db)
            self._connect_db_session_with_app(db)
            return True
        else:
            return False

    def register_teardown_appcontext(self, key: str, teardown: Teardown):
        self._teardown_appcontext.record_teardown(key, teardown)

    def _initialize_app(self, name: str):
        self.app = self.create_app(name)

    def _initialize_fields(self):
        self.app.test_client_class = FlaskRouterTester
        self._teardown_appcontext = TeardownRecorder()

    def _initialize_configuration(self, config: object | None):
        if config:
            self.app.config.from_object(config)

    def _initialize_views(self, views: list[UiView] | None):
        if views:
            for view in views:
                self.register_view(view)

    def _initialize_routes(self, routes: list[AppRoute[UiView]] | None):
        if routes:
            for route in routes:
                self.register_route(route)

    def _initialize_db(self, db: DatabaseManager | None):
        if db:
            self.register_db(db)

    def _initialize_teardowns(self):
        self._teardown_appcontext.init(
            registrar=self.app.teardown_appcontext,
            arg=self.app,
        )

    def _configure_route(self, route: AppRoute[UiView]) -> Blueprint:
        bp = self._create_blueprint(route)

        for view in route.views:
            self.register_view(view, bp)

        for nested_route in route.routes:
            self.register_route(nested_route, bp)

        return bp

    @classmethod
    def _configure_db_session_with_flask(cls, db_manager: DatabaseManager):
        def get_flask_app_ctx() -> int:
            return id(app_ctx._get_current_object())

        db_manager.configure_session(get_flask_app_ctx)

    def _connect_db_session_with_app(self, db_manager: DatabaseManager):
        self.app.session = db_manager.session

        def remove_session(app: Flask):
            app.session.remove()

        self.register_teardown_appcontext("remove_session", remove_session)

    def _create_adapter(self, view: UiView) -> FlaskViewAdapter:
        return FlaskViewAdapter(view)

    def _create_blueprint(self, route: AppRoute) -> Blueprint:
        return Blueprint(
            name=route.name,
            import_name=route._root,
            url_prefix=route.prefix,
            template_folder=route.template_path,
            subdomain=route.subdomain,
        )
