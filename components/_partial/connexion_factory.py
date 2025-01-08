import connexion
from connexion.options import SwaggerUIOptions

from .connexion_class_resolver import ConnexionClassResolver
from .connexion_route import ConnexionRoute


class ConnexionFactory:
    def create_app(self, name: str, spec_dir: str = "./") -> connexion.FlaskApp:
        app = connexion.App(name, specification_dir=spec_dir)
        return app

    def register_route(
        self,
        main: connexion.AbstractApp,
        route: ConnexionRoute,
        route_prefix: str | None = None,
        name_prefix: str | None = None,
    ) -> None:
        name = ".".join(filter(None, (name_prefix, route.name)))
        prefix = "".join(filter(None, (route_prefix, route.prefix)))
        swagger_options = SwaggerUIOptions(
            swagger_ui=route.show_ui,
            swagger_ui_path=route.ui_path,
        )

        resolver = (
            ConnexionClassResolver(route.resolver_path) if route.resolver_path else None
        )

        main.add_api(
            route.spec_path,
            name=name,
            swagger_ui_options=swagger_options,
            base_path=prefix,
            resolver=resolver,
        )

    def configure(
        self,
        name: str,
        routes: list[ConnexionRoute],
        spec_dir: str = "./",
    ) -> connexion.FlaskApp:
        app = self.create_app(name, spec_dir)
        for route in routes:
            self.register_route(app, route)
        return app
