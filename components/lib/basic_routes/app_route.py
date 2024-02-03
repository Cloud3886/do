import sys
from typing import Any, Callable, Generic, Optional, TypeVar

from components.lib.basic_routes.api_view import ApiView

T = TypeVar("T", bound=ApiView, covariant=True)


class AppRoute(Generic[T]):
    name: str
    prefix: Optional[str] = None
    template_path: Optional[str] = None
    subdomain: Optional[str] = None

    description: Optional[str] = None
    error_handlers: dict[type[Exception], Callable[[Any], Any]] = {}

    def __init__(self) -> None:
        self._root = sys.modules[self.__module__].__name__
        self.configure()

    def configure(self):
        self.views: list[T] = []
        self.routes: list[AppRoute] = []
