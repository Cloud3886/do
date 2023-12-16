from typing import Any

http_methods = frozenset(
    ["get", "post", "head", "options", "delete", "put", "trace", "patch"]
)


class ApiView:
    name: str = None
    endpoint: str = None
    reloads: bool = True
    _class_args: list = []
    _class_kwargs: dict = {}

    def store_args(self, *args, **kwargs) -> None:
        if self._class_args or self._class_kwargs:
            print("Store args called twice")
            print(f"Previous args: {self._class_args, self._class_kwargs}")
            print(f"New args: {args,kwargs}")

        self._class_args = args
        self._class_kwargs = kwargs

    def _build(self, *args, **kwargs):
        self._ready = True

    def _view_methods(self) -> dict[str, Any]:
        methods = {}
        for call in http_methods:
            if hasattr(self, call):
                methods[call] = getattr(self, call)
        return methods
