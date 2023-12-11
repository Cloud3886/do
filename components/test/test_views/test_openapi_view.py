from components.lib.views.openapi_view import OpenapiView
from components.test.test_views.test_ui_view import UiViewTester


# ------------------------------------------------------------------------------
# Testers
# ------------------------------------------------------------------------------
class OpenapiViewTester(UiViewTester):
    def __init__(self, view: OpenapiView) -> None:
        self.view = view


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

        def get(self):
            return "testing"

    view = ParamOpenapiView("")
    OpenapiViewTester(view).test()
