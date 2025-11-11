from types import TracebackType

from flask.testing import FlaskClient


class FlaskRouterTester(FlaskClient):
    def __enter__(self) -> FlaskClient:
        self.application.testing = True
        return super().__enter__()

    def __exit__(
        self,
        exc_type: type | None,
        exc_value: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.application.testing = False
        return super().__exit__(exc_type, exc_value, tb)
