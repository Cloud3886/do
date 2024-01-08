from typing import Callable, Generic, TypeVar

T = TypeVar("T")
Teardown = Callable[[T], None]


class TeardownRecorder(Generic[T]):
    def __init__(self) -> None:
        self._initialized = False
        self._teardowns: dict[str, Teardown] = {}

    def record_teardown(self, key: str, teardown: Teardown):
        self._teardowns[key] = teardown

    def init(self, *, registrar: Callable[[Callable[..., None]], None], arg: T):
        if not self._initialized:
            teardown_callback = self._create_teardown_callback(arg)
            registrar(teardown_callback)
            self._initialized = True

    def _create_teardown_callback(self, arg: T):
        def _teardown_callback(*args, **kwargs):
            for teardown in self._teardowns.values():
                teardown(arg)

        return _teardown_callback
