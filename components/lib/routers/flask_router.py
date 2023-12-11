from typing import Any, Callable

import flask.typing as ft
from flask import (
    Blueprint,
    Flask,
    jsonify,
    render_template,
    current_app,
)
from flask.globals import app_ctx
from flask.views import MethodView
from components.lib.database_manager import DatabaseManager

from components.lib.views.ui_view import UiView
from components.lib.app_route import AppRoute
from components.utils.extensions import prettify


class FlaskViewAdapter:
    def __init__(self, view: UiView) -> None:
        self.view = view

    def build_view_class(self) -> type[MethodView]:
        class AdaptedView(MethodView):
            __name__ = self.view.name
            init_every_request = self.view.reloads
            view = self.view
            adapter = self

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
                        self.adapter.reinitialize(self, self.view)
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

        self.initialize(AdaptedView, self.view)
        return AdaptedView

    def build_view_function(self) -> ft.RouteCallable:
        return self.build_view_class().as_view(self.view.name)

    @classmethod
    def reinitialize(cls, self, view: UiView):
        re_view = view.__class__(*view._class_args, **view._class_kwargs)
        cls.initialize(self, re_view)

    @classmethod
    def initialize(cls, self, view: UiView):
        cls._build_internal_view(view)
        self.view = view
        methods = self.view._view_methods()
        for call in methods:
            setattr(self, call, methods[call])
        self.methods = set(map(lambda o: o.upper(), methods.keys()))

    @classmethod
    def _build_internal_view(cls, view: UiView):
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
        self._teardown_appcontext: list[Teardown] = []

        if DB_URI:
            self._configure_db(DB_URI)

        if views:
            for view in views:
                self.register_view(view)

        if routes:
            for route in routes:
                self.register_route(route)

        self._register_teardown_appcontext_with_flask()

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

    def register_teardown_appcontext(self, teardown: Teardown):
        self._teardown_appcontext.append(teardown)
        return teardown

    def _configure_db(self, DB_URI: str):
        if self.db_manager:
            return

        self.db_manager = DatabaseManager(DB_URI)

        def get_app_ctx() -> int:
            return id(app_ctx._get_current_object())

        self.app.session = self.db_manager.configure_scoped_session(get_app_ctx)

        @self.register_teardown_appcontext
        def remove_session(app: Flask):
            app.session.remove()

    def _register_teardown_appcontext_with_flask(self):
        if self._teardown_appcontext_registered:
            return

        @self.app.teardown_appcontext
        def _teardown_appcontext(*args, **kwargs):
            for teardown in self._teardown_appcontext:
                teardown(self.app)

        self._teardown_appcontext_registered = True

    def _configure_route(self, route: AppRoute[UiView]) -> Blueprint:
        bp = self._create_blueprint(route)

        for view in route.views:
            self.register_view(view, bp)

        for route in route.routes:
            self.register_route(route, bp)

        return bp

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
