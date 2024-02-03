from copy import deepcopy
from functools import wraps
from typing import TYPE_CHECKING, Any, TypeVar

from flask_smorest import Blueprint

from components.lib.basic_routes.ui_view import UiView
from components.lib.flask_router import FlaskViewAdapter
from components.utils.deepset import deepset

if TYPE_CHECKING:
    from components.lib.smorest_router.smorest_router import SmorestRouter


S = TypeVar("S", bound="SmorestRouter")


class SmorestViewAdapter(FlaskViewAdapter[S]):
    def __init__(
        self,
        router: S,
        view: UiView[S],
        blueprint: Blueprint | None,
    ) -> None:
        super().__init__(router, view)
        self.blueprint = blueprint
        self._init_docs()

    def _init_docs(self):
        methods = self.view._view_methods()
        for call, call_method in methods.items():
            self._init_docs_for_call_method(call, call_method)

    def _init_docs_for_call_method(self, call: str, call_method):
        call_viewdoc: dict[str, Any] = getattr(call_method, "_viewdoc", None)  # type: ignore
        blueprint = self.blueprint

        if call_viewdoc and blueprint:
            call_method = self._add_calldocs(call_viewdoc, call_method, blueprint)

        setattr(self.view, call, call_method)

    def _add_calldocs(
        self,
        viewdoc: dict[str, Any],
        call_method,
        blueprint: Blueprint,
    ):
        arg = (viewdoc, blueprint)
        call_method = self._add_apidoc("response", *arg, call_method)
        call_method = self._add_apidoc("alt_response", *arg, call_method)
        call_method = self._add_apidoc("arguments", *arg, call_method)
        call_method = self._add_custom_doc(call_method, viewdoc)
        return call_method

    @staticmethod
    def _add_apidoc(
        decoration: str,
        viewdoc: dict[str, Any],
        blueprint: Blueprint,
        call_method,
    ):
        docs: list[dict] | None = viewdoc.get(decoration)
        if docs:
            for doc in docs:
                call_method = getattr(blueprint, decoration)(**doc)(call_method)

        return call_method

    @staticmethod
    def _add_custom_doc(call_method, viewdoc: dict[str, Any]):
        custom_docs: list[dict[str, Any]] | None = viewdoc.get("custom")

        @wraps(call_method)
        def wrapped(*args, **kwargs):
            return call_method(*args, **kwargs)

        call_method = wrapped  # type: ignore
        if custom_docs:
            for doc in custom_docs:
                apidoc = deepcopy(getattr(call_method, "_apidoc", {}))
                apidoc = deepset(apidoc, doc)
                setattr(call_method, "_apidoc", apidoc)
        return call_method
