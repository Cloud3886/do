from components.lib.smorest_router import OpenapiView
from components.test.test_basic_routes.test_ui_view import UiViewTester
from components.utils.extensions import hash_gen


# ------------------------------------------------------------------------------
# Testers
# ------------------------------------------------------------------------------
class OpenapiViewTester(UiViewTester):
    def __init__(self, view: OpenapiView) -> None:
        self.view = view

    @staticmethod
    def create_view(
        endpoint: str,
        data="testing",
        name: str | None = None,
    ) -> OpenapiView:
        path = endpoint
        view_name = name

        class TView(OpenapiView):
            name = view_name or hash_gen()
            endpoint = path

            def get(self):
                return data

        return TView()


# ------------------------------------------------------------------------------
# Test Cases
# ------------------------------------------------------------------------------
def test_openapi_view():
    class ParamOpenapiView(OpenapiView):
        name = "test"
        endpoint = "/test"

        def __init__(self, something) -> None:
            super().__init__()
            self.store_args(something)

    view = ParamOpenapiView("")
    OpenapiViewTester(view).test()


def test_openapi_add_viewdoc():
    view = OpenapiViewTester.create_view("/")
    assert view.get() == view._add_viewdoc("test")(view.get)()  # type: ignore
