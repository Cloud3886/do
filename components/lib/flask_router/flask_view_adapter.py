from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Generic, Protocol, TypeVar

import flask.typing as ft
from flask import (
    current_app,
    jsonify,
    render_template,
)
from flask.views import MethodView

from components.lib.basic_routes.ui_view import UiView

if TYPE_CHECKING:
    from components.lib.flask_router.flask_router import FlaskRouter


F = TypeVar("F", bound="FlaskRouter")


class AdaptedViewType(Protocol):
    @classmethod
    @abstractmethod
    def initialize(cls, view: UiView):
        pass

    @classmethod
    @abstractmethod
    def _configure_methods(cls):
        pass

    @classmethod
    @abstractmethod
    def as_view(
        cls,
        name: str,
        *class_args,
        **class_kwargs,
    ) -> ft.RouteCallable:
        pass


class FlaskViewAdapter(Generic[F]):
    def __init__(self, router: F, view: UiView[F]) -> None:
        self.view = view
        self.router = router

    def build_view_class(self) -> type[AdaptedViewType]:
        view_class = self._create_adapted_view_class()
        view_class.initialize(self.view)
        return view_class

    def build_view_function(self) -> ft.RouteCallable:
        return self.build_view_class().as_view(self.view.name)

    def _create_adapted_view_class(self) -> type[AdaptedViewType]:
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
            def initialize(cls, view: UiView[F]):
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

    def _build_internal_view(self, view: UiView[F]):
        view._build(
            router=self.router,
            serialize=jsonify,
            render_template=render_template,
        )
