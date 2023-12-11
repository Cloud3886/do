from typing import TypeVar


from components.test._components._testers import InstanceTester
from components.lib.basic_routes.api_view import ApiView
from components.lib.basic_routes.app_route import AppRoute

from components.utils.extensions import hash_gen

T = TypeVar("T", bound=ApiView)


class AppRouteTester(InstanceTester):
    def __init__(self, route: AppRoute) -> None:
        self.route = route
        super().__init__()

    def test_has_name(self):
        assert self.route.name

    def test_not_improper_prefix(self):
        if self.route.prefix:
            assert self.route.prefix.startswith("/")

    def has_route_test(self, prefix: str = None):
        for route in self.route.routes:
            if route.prefix == prefix:
                return True

        return False

    def has_view_test(self, prefix: str = None) -> bool:
        for view in self.route.views:
            if view.endpoint == prefix:
                return True

        return False

    @classmethod
    def parse_route(cls, route: AppRoute) -> list[str]:
        route_map: list[str] = []

        direct_views = route.views
        route_map.extend(map(lambda x: (route.prefix or "") + x.endpoint, direct_views))

        for nested_route in route.routes:
            nested_map = cls.parse_route(nested_route)
            route_map.extend(map(lambda x: (route.prefix or "") + x, nested_map))

        return route_map

    @classmethod
    def parse_multiple_routes(cls, routes: list[AppRoute]) -> list[str]:
        route_map: list[str] = []
        for route in routes:
            route_map.extend(cls.parse_route(route))

        return list(filter(None, route_map))

    @staticmethod
    def create_route(
        views: list[T],
        routes: list[AppRoute[T]] = [],
        prefix: str = None,
        name: str = None,
    ) -> AppRoute:
        route_name = name
        path = prefix
        urls = views
        nested_routes = routes

        class TRoute(AppRoute[T]):
            name = route_name or hash_gen()
            prefix = path

            views = urls
            routes = nested_routes

        return TRoute()
