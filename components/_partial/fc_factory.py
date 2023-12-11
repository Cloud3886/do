from _lib._components.dependencies.connexion_dependency import (
    ConnexionDependency as _CD,
)
from _lib._components.dependencies.flask_dependency import FlaskDependency as _FD

from _lib._components.factory.app_factory import AppFactory
from _lib._components.routes.app_route import AppRoute
from _lib._components.routes.connexion_route import ConnexionRoute
from _lib._components.web_app.fc_app import FCApp


from .flask_factory import FlaskFactory
from .connexion_factory import ConnexionFactory


class FCFactoryDependency(_CD, _FD):
    FCApp = FCApp
    FlaskFactory = FlaskFactory
    ConnexionFactory = ConnexionFactory


_FCFD = FCFactoryDependency


class FCFactory(AppFactory):
    def __init__(self, *, _deps: FCFactoryDependency = _FCFD()) -> None:
        self._deps = _deps

    def create_app(self, name: str, spec_dir: str = "./") -> FCApp:
        app = self._deps.connexion.FlaskApp(name, specification_dir=spec_dir)
        fs_app = self._deps.FCApp(app)
        return fs_app

    def configure_route(
        self,
        main: _CD.connexion.FlaskApp,
        route: AppRoute,
        route_prefix: str | None = None,
        name_prefix: str | None = None,
    ) -> _FD.Blueprint:
        name = ".".join(filter(None, (name_prefix, route.name)))
        prefix = "".join(filter(None, (route_prefix, route.prefix)))
        bp = self._deps.FlaskFactory().create_blueprint(route)

        for view in route.views:
            self._deps.FlaskFactory().register_view(bp, view=view)

        for nested_route in route.routes:
            if isinstance(nested_route, AppRoute):
                sub = self.configure_route(
                    main,
                    nested_route,
                    route_prefix=prefix,
                    name_prefix=name,
                )
                bp.register_blueprint(sub)
            else:
                self._deps.ConnexionFactory().register_route(
                    main,
                    nested_route,
                    route_prefix=prefix,
                    name_prefix=name,
                )

        return bp

    def register_route(
        self,
        main: _CD.connexion.FlaskApp,
        route: AppRoute | ConnexionRoute,
        route_prefix: str | None = None,
        name_prefix: str | None = None,
    ) -> None:
        if name_prefix:
            route.name = f"{name_prefix}.{route.name}"
        if isinstance(route, AppRoute):
            bp = self.configure_route(main, route)
            main.app.register_blueprint(bp, url_prefix=route_prefix)
        else:
            self._deps.ConnexionFactory().register_route(main, route, route_prefix)

    def configure(
        self,
        name: str,
        routes: list[AppRoute | ConnexionRoute],
        spec_dir: str = "./",
    ) -> FCApp:
        app = self.create_app(name, spec_dir)
        for route in routes:
            self.register_route(app.app, route)
        return app
