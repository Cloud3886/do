from contextlib import contextmanager
from typing import Any, Callable

import flask.typing as ft
from flask import (
    Blueprint,
    Flask,
    current_app,
    jsonify,
    render_template,
)
from flask.globals import app_ctx
from flask.views import MethodView

from components.lib.basic_routes.app_route import AppRoute
from components.lib.basic_routes.ui_view import UiView
from components.lib.database_manager.database_manager import DatabaseManager


class FlaskViewAdapter:
    def __init__(self, view: UiView) -> None:
        self.view = view

    def build_view_class(self) -> type[MethodView]:
        view_class = self._create_adapted_view_class()
        view_class.initialize(self.view)
        return view_class

    def build_view_function(self) -> ft.RouteCallable:
        return self.build_view_class().as_view(self.view.name)

    def _create_adapted_view_class(self) -> type[MethodView]:
        class AdaptedView(MethodView):
            __name__ = self.view.name
            init_every_request = self.view.reloads
            view = self.view
            adapter = self

            def reinitialize(self):
                re_view = self.view.__class__(
                    *self.view._class_args, **self.view._class_kwargs
                )
                self.initialize(re_view)

            @classmethod
            def initialize(cls, view: UiView):
                cls.adapter._build_internal_view(view)
                cls.adapter.view = view
                cls.view = view
                cls._configure_methods()

            @classmethod
            def _configure_methods(cls):
                methods = cls.view._view_methods()
                for call in methods:
                    setattr(cls, call, methods[call])
                cls.methods = set(map(lambda o: o.upper(), methods.keys()))

            @classmethod
            def as_view(
                cls,
                name: str,
                *class_args,
                **class_kwargs,
            ) -> ft.RouteCallable:
                self = cls()
                if cls.init_every_request:

                    def view(**kwargs: Any) -> ft.ResponseReturnValue:
                        self.reinitialize()
                        return current_app.ensure_sync(self.dispatch_request)(**kwargs)

                else:

                    def view(**kwargs: Any) -> ft.ResponseReturnValue:
                        return current_app.ensure_sync(self.dispatch_request)(**kwargs)

                # if cls.decorators:
                #     view.__name__ = name
                #     view.__module__ = cls.__module__
                #     for decorator in cls.decorators:
                #         view = decorator(view)

                view.internal_view = cls.view
                view.internal_adapter = cls.adapter
                view.view_class = cls
                view.__name__ = name
                view.__doc__ = cls.__doc__
                view.__module__ = cls.__module__
                view.methods = cls.methods
                view.provide_automatic_options = cls.provide_automatic_options
                return view

        return AdaptedView

    @staticmethod
    def _build_internal_view(view: UiView):
        view._build(serialize=jsonify, render_template=render_template)


Teardown = Callable[[Flask], None]


class FlaskRouter:
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

    @contextmanager
    def tester(self):
        self.app.testing = True
        with self.app.test_client() as tester:
            yield tester
        self.app.testing = False

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

        db_manager.configure_scoped_session(get_flask_app_ctx)

    def _connect_db_session_with_app(self):
        self.app.session = self.db_manager.SessionScoped

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
