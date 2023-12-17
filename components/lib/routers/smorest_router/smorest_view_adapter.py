from flask_smorest import Blueprint

from components.lib.basic_routes.ui_view import UiView
from components.lib.routers.flask_router import FlaskViewAdapter


class SmorestViewAdapter(FlaskViewAdapter):
    def __init__(self, view: UiView, blueprint: Blueprint = None) -> None:
        self.blueprint = blueprint
        super().__init__(view)
        self._init_docs()

    def _init_docs(self):
        methods = self.view._view_methods()
        for call, call_method in methods.items():
            self._init_docs_for_call_method(call, call_method)

    def _init_docs_for_call_method(self, call: str, call_method):
        call_viewdoc: dict = getattr(call_method, "_viewdoc", None)
        blueprint = self.blueprint

        if call_viewdoc and blueprint:
            call_method = self._add_calldocs(call_viewdoc, call_method, blueprint)

        setattr(self.view, call, call_method)

    def _add_calldocs(self, viewdoc: dict, call_method, blueprint: Blueprint):
        arg = (viewdoc, blueprint)
        call_method = self._add_apidoc("response", *arg, call_method)
        call_method = self._add_apidoc("alt_response", *arg, call_method)
        call_method = self._add_apidoc("arguments", *arg, call_method)
        return call_method

    @staticmethod
    def _add_apidoc(decoration: str, viewdoc: dict, blueprint: Blueprint, call_method):
        docs: list[dict] = viewdoc.get(decoration)
        if docs:
            for doc in docs:
                call_method = getattr(blueprint, decoration)(**doc)(call_method)

        return call_method
