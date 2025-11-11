from components.lib.basic_routes.ui_view import UiView
from components.lib.flask_router.flask_router import FlaskRouter
from components.test.test_basic_routes.test_api_view import ApiViewTester
from components.utils.extensions import hash_gen


# ------------------------------------------------------------------------------
# Testers
# ------------------------------------------------------------------------------
class UiViewTester(ApiViewTester):
    def __init__(self, view: UiView) -> None:
        self.view = view

    def test_serialize(self):
        self.view.serialize("data")

    def test_render_template(self):
        self.view.render_template("template")

    def test_view_building(self):
        router = FlaskRouter("test")

        def serialize(data):
            return "serialized"

        def render(template: str, **kwargs):
            return "rendered"

        self.view._build(router, serialize, render)
        assert self.view.render_template("test") == "rendered"
        assert self.view.serialize("test") == "serialized"
        assert self.view.router == router
        assert self.view._ready

        del self.view._serialize
        del self.view._render_template
        del self.view.router
        del self.view._ready

    @staticmethod
    def create_view(endpoint: str, data="testing", name: str | None = None) -> UiView:
        path = endpoint
        view_name = name

        class TView(UiView):
            name = view_name or hash_gen()
            endpoint = path

            def get(self):
                return data

        return TView()


# ------------------------------------------------------------------------------
# Test Cases
# ------------------------------------------------------------------------------
def test_ui_view():
    class ParamUiView(UiView):
        name = "test"
        endpoint = "/test"

        def __init__(self, something) -> None:
            super().__init__()
            self.store_args(something)

    view = ParamUiView("")
    UiViewTester(view).test()


def test_view_helpers():
    view = UiViewTester.create_view("/")

    assert view.serialize
    assert view.render_template
