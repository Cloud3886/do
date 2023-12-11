import sys
from typing import Self, Generic, TypeVar
from components.lib.views.api_view import ApiView

T = TypeVar("T", bound=ApiView)


class AppRoute(Generic[T]):
    name: str = None
    prefix: str | None = None

    views: list[T] = []
    routes: list[Self] = []
    template_path: str | None = None
    subdomain: str | None = None

    description: str = None

    def __init__(self) -> None:
        self._root = sys.modules[self.__module__].__name__
