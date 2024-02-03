from types import TracebackType
from typing import Optional

from flask.testing import FlaskClient


class FlaskRouterTester(FlaskClient):
    def __enter__(self) -> FlaskClient:
        self.application.testing = True
        return super().__enter__()

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_value: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        self.application.testing = False
        return super().__exit__(exc_type, exc_value, tb)
