import pytest
import sqlalchemy.util as sql_tools
from flask import Flask, request
from flask.testing import FlaskClient

from components.lib.basic_routes.ui_view import UiView
from components.lib.database_manager import DatabaseManager
from components.lib.flask_router.flask_router import FlaskRouter
from components.lib.router import Router
from components.test._components._testers import ClassTester
from components.test.test_basic_routes.test_app_route import AppRouteTester
from components.test.test_basic_routes.test_ui_view import UiViewTester

create_view = UiViewTester.create_view
create_route = AppRouteTester.create_route


class TestFlaskRouter(ClassTester):
    @pytest.fixture
    def router(self) -> FlaskRouter:
        router = FlaskRouter(__name__)
        return router

    def test_router_interface(self, router):
        assert isinstance(router, Router)

    def test_router(self):
        router = FlaskRouter("test_router")
        assert isinstance(router.app, Flask)
        assert router.app.import_name == "test_router"

    def test_router_with_database(self):
        router = FlaskRouter("test_router", DB_URI="sqlite:///")
        router.register_view(create_view("/"))
        assert isinstance(router.db_manager, DatabaseManager)
        assert isinstance(router.app.session.registry, sql_tools.ScopedRegistry)

        router.app.test_client().get("/")

        router.app.test_client().get("/")

    # def test_run(self, router: FlaskRouter):
    #     router.register_view(create_view("/"))

    #     url = "http://127.0.0.1:5000/"
    #     with Server(router.run):
    #         res = requests.get(url)
    #         assert res.status_code == 200

    def test_router_registered_teardown_appcontext(self, router: FlaskRouter):
        assert len(router.app.teardown_appcontext_funcs) >= 1

    def test_router_tester(self, router: FlaskRouter):
        assert not router.app.testing

        with router.tester() as tester:
            assert isinstance(tester, FlaskClient)
            assert router.app.testing
            tester.get("/?vodka=42")
            assert request.args["vodka"] == "42"

        assert not router.app.testing

    def test_view_at_index(self, router: FlaskRouter):
        router.register_view(create_view("/"))
        res = router.app.test_client().get("/")
        assert res.status_code == 200

    def test_view_at_test(self, router: FlaskRouter):
        router.register_view(create_view("/test"))
        res = router.app.test_client().get("/test")
        assert res.status_code == 200

    def test_view_data_retention(self, router: FlaskRouter):
        class SomeView(UiView):
            name = "some"
            endpoint = "/"
            reloads = False

            def __init__(self) -> None:
                self.count = 0

            def get(self):
                self.count += 1
                return str(self.count)

        router.register_view(SomeView())

        res = router.app.test_client().get("/")
        assert int(res.data) == 1

        res = router.app.test_client().get("/")
        assert int(res.data) == 2

    def test_view_data_reload(self, router: FlaskRouter):
        class SomeView(UiView):
            name = "some"
            endpoint = "/"

            def __init__(self) -> None:
                self.count = 0

            def get(self):
                self.count += 1
                return str(self.count)

        router.register_view(SomeView())

        res = router.app.test_client().get("/")
        assert int(res.data) == 1

        res = router.app.test_client().get("/")
        assert int(res.data) == 1

    def test_view_data_reload_with_view_arg(self, router: FlaskRouter):
        class SomeView(UiView):
            name = "some"
            endpoint = "/"

            def __init__(self, count: int) -> None:
                self.count = count
                self.store_args(count)

            def get(self):
                self.count += 1
                return str(self.count)

        UiViewTester(SomeView(99)).test()

        router.register_view(SomeView(8))

        res = router.app.test_client().get("/")
        assert int(res.data) == 9

        res = router.app.test_client().get("/")
        assert int(res.data) == 9

    def test_view_multiple(self, router: FlaskRouter):
        router.register_view(create_view("/"))
        router.register_view(create_view("/test"))

        res = router.app.test_client().get("/")
        assert res.status_code == 200

        res = router.app.test_client().get("/test")
        assert res.status_code == 200

    def test_view_response(self, router: FlaskRouter):
        router.register_view(create_view("/"))
        router.register_view(create_view("/test", data="more testing"))

        res = router.app.test_client().get("/")
        assert res.status_code == 200
        assert res.data == b"testing"

        res = router.app.test_client().get("/test")
        assert res.status_code == 200
        assert res.data == b"more testing"

    def test_view_with_params(self, router: FlaskRouter):
        class SomeView(UiView):
            name = "test"
            endpoint = "/<string:some>"

            def get(self, some):
                return some

        router.register_view(SomeView())

        res = router.app.test_client().get("/testing")
        assert res.status_code == 200
        assert res.data == b"testing"

    def test_view_with_post(self, router: FlaskRouter):
        class SomeView(UiView):
            name = "test"
            endpoint = "/"

            def post(self):
                return "Success"

        router.register_view(SomeView())

        res = router.app.test_client().post("/")
        assert res.status_code == 200
        assert res.data == b"Success"

        res = router.app.test_client().get("/")
        assert res.status_code == 405

    def test_view_with_multiple_methods(self, router: FlaskRouter):
        class SomeView(UiView):
            name = "test"
            endpoint = "/"

            def post(self):
                return "Success"

            def get(self):
                return "No Data"

        router.register_view(SomeView())

        res = router.app.test_client().post("/")
        assert res.status_code == 200
        assert res.data == b"Success"

        res = router.app.test_client().get("/")
        assert res.status_code == 200
        assert res.data == b"No Data"

    def test_route_registration(self, router: FlaskRouter):
        route0 = create_route([])
        route1 = create_route([create_view("/")])
        route2 = create_route([create_view("/test", data="test")])
        route3 = create_route([create_view("/test1"), create_view("/test2")])
        route4 = create_route(
            [create_view("/")],
            routes=[
                create_route([create_view("/", data="more test")], prefix="/nest2")
            ],
            prefix="/nest",
        )
        route5 = create_route(
            [create_view("/"), create_view("/test")], prefix="/nested"
        )

        router.register_route(route0)
        router.register_route(route1)
        router.register_route(route2)
        router.register_route(route3)
        router.register_route(route4)
        router.register_route(route5)

        assert router.app.test_client().get("/").data == b"testing"
        assert router.app.test_client().get("/test").data == b"test"
        assert router.app.test_client().get("/test1").data == b"testing"
        assert router.app.test_client().get("/test2").data == b"testing"
        assert router.app.test_client().get("/nest/").data == b"testing"
        assert router.app.test_client().get("/nest/nest2/").data == b"more test"
        assert router.app.test_client().get("/nested/").data == b"testing"
        assert router.app.test_client().get("/nested/test").data == b"testing"

    def test_route_with_multi_methods(self, router: FlaskRouter):
        class SomeView(UiView):
            name = "test"
            endpoint = "/"

            def post(self):
                return "Success"

            def get(self):
                return "No Data"

        router.register_route(create_route([SomeView()]))

        res = router.app.test_client().post("/")
        assert res.status_code == 200
        assert res.data == b"Success"

        res = router.app.test_client().get("/")
        assert res.status_code == 200
        assert res.data == b"No Data"

    def test_router_initialization(self):
        view1 = create_view("/")
        view2 = create_view("/test")
        route1 = create_route([create_view("/")], prefix="/one")

        router = FlaskRouter(__name__, views=[view1, view2], routes=[route1])

        assert router.app.test_client().get("/").status_code == 200
        assert router.app.test_client().get("/test").status_code == 200
        assert router.app.test_client().get("/one/").status_code == 200

    def test_view_helpers(self, router: FlaskRouter):
        class SomeView(UiView):
            name = "test"
            endpoint = "/"

            def post(self):
                return self.serialize("Success")

            def get(self):
                return self.serialize("No Data")

        router.register_view(SomeView())

        assert router.app.test_client().post("/").json == "Success"
        assert router.app.test_client().get("/").json == "No Data"
