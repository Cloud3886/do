from typing import Any, Generic, TypeVar

R = TypeVar("R")


http_methods = frozenset(
    ["get", "post", "head", "options", "delete", "put", "trace", "patch"]
)


class ApiView(Generic[R]):
    name: str
    endpoint: str
    reloads: bool = True

    def __init__(self) -> None:
        self._class_args: tuple = tuple()
        self._class_kwargs: dict = {}

    def store_args(self, *args, **kwargs) -> None:
        if self._class_args or self._class_kwargs:
            print("Store args called twice")
            print(f"Previous args: {self._class_args, self._class_kwargs}")
            print(f"New args: {args,kwargs}")

        self._class_args = args
        self._class_kwargs = kwargs

    def _build(self, router: R, *args, **kwargs):
        self.router = router
        self._ready = True
        self.init_state()

    def init_state(self):
        pass

    def _view_methods(self) -> dict[str, Any]:
        methods = {}
        for call in http_methods:
            if hasattr(self, call):
                methods[call] = getattr(self, call)
        return methods
