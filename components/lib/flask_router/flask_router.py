from contextlib import contextmanager
from typing import Any, Callable

from flask import (
    Blueprint,
    Flask,
)
from flask.globals import app_ctx

from components.lib.basic_routes.app_route import AppRoute
from components.lib.basic_routes.ui_view import UiView
from components.lib.database_manager import DatabaseManager
from components.lib.router import Router

from .flask_test_client import FlaskRouterTester
from .flask_view_adapter import FlaskViewAdapter

Teardown = Callable[[Flask], None]


class FlaskRouter(Router):
    def __init__(
        self,
        name: str,
        *,
        views: list[UiView] = None,
        routes: list[AppRoute[UiView]] = None,
        DB_URI: str | None = None,
    ) -> None:
        self.app = self.create_app(name)
        self.db_manager = None
        self._teardown_appcontext_registered = False
        self._teardown_appcontext: dict[str, Teardown] = {}
        self.app.test_client_class = FlaskRouterTester

        if DB_URI:
            self._configure_db(DB_URI)

        if views:
            for view in views:
                self.register_view(view)

        if routes:
            for route in routes:
                self.register_route(route)

        self._register_teardown_appcontext_callback_with_app()

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

    def register_view(self, view: UiView, main: Blueprint = None):
        adapter = self._create_adapter(view)
        view_func = adapter.build_view_function()
        (main or self.app).add_url_rule(view.endpoint, view.name, view_func=view_func)

    def register_route(self, route: AppRoute[UiView], main: Blueprint = None):
        bp = self._configure_route(route)
        (main or self.app).register_blueprint(bp)

    def register_teardown_appcontext(self, key: str, teardown: Teardown):
        self._teardown_appcontext[key] = teardown

    def tester(self):
        return self.app.test_client()

    def _configure_db(self, DB_URI: str):
        if not self.db_manager:
            self.db_manager = DatabaseManager(DB_URI)
            self._configure_db_session_with_flask(self.db_manager)
            self._connect_db_session_with_app()

    def _configure_route(self, route: AppRoute[UiView]) -> Blueprint:
        bp = self._create_blueprint(route)

        for view in route.views:
            self.register_view(view, bp)

        for nested_route in route.routes:
            self.register_route(nested_route, bp)

        return bp

    def _register_teardown_appcontext_callback_with_app(self):
        if not self._teardown_appcontext_registered:
            teardown_callback = self._create_teardown_appcontext_callback()
            self.app.teardown_appcontext(teardown_callback)
            self._teardown_appcontext_registered = True

    @classmethod
    def _configure_db_session_with_flask(cls, db_manager: DatabaseManager):
        def get_flask_app_ctx() -> int:
            return id(app_ctx._get_current_object())

        db_manager.configure_session_factory(get_flask_app_ctx)

    def _connect_db_session_with_app(self):
        self.app.session = self.db_manager.SessionFactory

        def remove_session(app: Flask):
            app.session.remove()

        self.register_teardown_appcontext("remove_session", remove_session)

    def _create_teardown_appcontext_callback(self):
        def _teardown_appcontext(*args, **kwargs):
            for teardown in self._teardown_appcontext.values():
                teardown(self.app)

        return _teardown_appcontext

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
