from abc import abstractmethod
from typing import Any, Protocol, runtime_checkable

from components.lib.basic_routes.api_view import ApiView
from components.lib.basic_routes.app_route import AppRoute


@runtime_checkable
class Router(Protocol):
    def __init__(
        self,
        name: str,
        *,
        views: list[ApiView] = None,
        routes: list[AppRoute[ApiView]] = None,
        DB_URI: str | None = None,
    ) -> None:
        pass

    @staticmethod
    @abstractmethod
    def create_app(name: str):
        pass

    def run(
        self,
        host: str | None = None,
        port: int | None = None,
        debug: bool | None = None,
        load_dotenv: bool = True,
        **options: Any,
    ):
        pass

    def register_view(self, view: ApiView):
        pass

    def register_route(self, route: AppRoute[ApiView]):
        pass

    def tester(self):
        pass
