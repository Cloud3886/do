import sys
from typing import Generic, TypeVar

from components.lib.basic_routes.api_view import ApiView

T = TypeVar("T", bound=ApiView, covariant=True)


class AppRoute(Generic[T]):
    name: str
    prefix: str | None = None
    template_path: str | None = None
    subdomain: str | None = None

    description: str | None = None

    def __init__(self) -> None:
        self._root = sys.modules[self.__module__].__name__
        self.configure()

    def configure(self):
        self.views: list[T] = []
        self.routes: list[AppRoute] = []
