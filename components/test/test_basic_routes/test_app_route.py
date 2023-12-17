from typing import TypeVar

from components.lib.basic_routes.api_view import ApiView
from components.lib.basic_routes.app_route import AppRoute
from components.test._components._testers import InstanceTester
from components.test.test_basic_routes.test_api_view import ApiViewTester
from components.utils.extensions import hash_gen

T = TypeVar("T", bound=ApiView)


# ------------------------------------------------------------------------------
# Testers
# ------------------------------------------------------------------------------
class AppRouteTester(InstanceTester):
    def __init__(self, route: AppRoute) -> None:
        self.route = route
        super().__init__()

    def test_has_name(self):
        assert self.route.name

    def test_not_improper_prefix(self):
        if self.route.prefix:
            assert self.route.prefix.startswith("/")

    def has_route(self, prefix: str = None):
        for nested_routes in self.route.routes:
            if nested_routes.prefix == prefix:
                return True

        return False

    def has_view(self, prefix: str = None) -> bool:
        for view in self.route.views:
            if view.endpoint == prefix:
                return True

        return False

    def has_endpoint(self, endpoint: str) -> bool:
        return endpoint in self.parse_route(self.route)

    @classmethod
    def parse_route(cls, route: AppRoute) -> list[str]:
        route_map: list[str] = []

        direct_views = route.views
        route_map.extend(map(lambda x: (route.prefix or "") + x.endpoint, direct_views))

        for nested_route in route.routes:
            nested_map = cls.parse_route(nested_route)
            route_map.extend(map(lambda x: (route.prefix or "") + x, nested_map))

        return route_map

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


# ------------------------------------------------------------------------------
# Test Cases
# ------------------------------------------------------------------------------
def test_app_route():
    route = AppRouteTester.create_route([ApiViewTester.create_view("/one")])
    route2 = AppRouteTester.create_route(
        [ApiViewTester.create_view("/")], routes=[route], prefix="/nest"
    )

    test1 = AppRouteTester(route)
    test1.test()
    assert test1.has_view("/one")
    assert test1.has_endpoint("/one")
    assert not test1.has_view("/no")
    assert not test1.has_route()

    test2 = AppRouteTester(route2)
    test2.test()
    assert test2.has_view("/")
    assert test2.has_route()
    assert test2.has_endpoint("/nest/")
    assert test2.has_endpoint("/nest/one")
