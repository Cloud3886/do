import logging

import pytest
import sqlalchemy.util as sql_tools
from flask import Flask, abort, request
from flask.testing import FlaskClient
from werkzeug import Response
from werkzeug.exceptions import HTTPException

from components.lib.basic_routes.app_route import AppRoute
from components.lib.basic_routes.ui_view import UiView
from components.lib.flask_router.flask_router import FlaskRouter
from components.lib.storage_manager import DatabaseManager
from components.lib.storage_manager.storage_manager import StorageManager
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

    def test_router_app(self):
        router = FlaskRouter("test_router")
        assert isinstance(router.app, Flask)
        assert router.app.import_name == "test_router"

    def test_router_logging(
        self,
        router: FlaskRouter,
        caplog: pytest.LogCaptureFixture,
    ):
        router.logger.setLevel(logging.INFO)
        router.logger.info("Hello Logs")
        assert "Hello Logs" in caplog.text

    def test_router_with_database(self):
        db = DatabaseManager("sqlite:///")
        storage = StorageManager(db=db)
        router = FlaskRouter("test_router", views=[create_view("/")], storage=storage)
        assert router.storage.db
        assert isinstance(router.app.session.registry, sql_tools.ScopedRegistry)  # type: ignore

        router.tester().get("/")
        router.tester().get("/")

    def test_database_registration(self, router: FlaskRouter):
        db = DatabaseManager("sqlite:///")
        storage = StorageManager(db=db)
        router.register_view(create_view("/"))
        router.register_storage(storage)

        assert router.storage.db
        assert router.app.session  # type: ignore
        assert isinstance(router.app.session.registry, sql_tools.ScopedRegistry)  # type: ignore

        router.tester().get("/")
        router.tester().get("/")

    def test_router_configuration(self):
        class Config:
            SQLALCHEMY_DATABASE_URI = "sqlite:///"
            SECRET_KEY = "secretly secret"

        config = Config()
        router = FlaskRouter("test_router", config=config)
        assert router.app.config.get("SECRET_KEY") == "secretly secret"
        assert router.config == config

    # def test_run(self, router: FlaskRouter):
    #     router.register_view(create_view("/"))

    #     url = "http://127.0.0.1:5000/"
    #     with Server(router.run):
    #         res = requests.get(url)
    #         assert res.status_code == 200

    def test_router_error_handlers_configuration(self):
        def error_handler1(error: Exception) -> Response:
            return Response("error", 0)

        def error_handler2(error: HTTPException) -> Response:
            return Response("http error", error.code)

        router = FlaskRouter(
            "test_router",
            error_handlers={Exception: error_handler1, HTTPException: error_handler2},
        )

        class TView(UiView):
            name = "test"
            endpoint = "/"

            def get(self):
                None["error"]  # type: ignore

        router.register_view(TView())
        res = router.tester().get("/")
        assert res.text == "error"
        assert res.status_code == 0

        res = router.tester().get("/error")
        assert res.text == "http error"
        assert res.status_code == 404

    def test_router_error_handler_registration(self, router: FlaskRouter):
        from werkzeug import Response

        def error_handler(error: Exception) -> Response:
            return Response("error test", 0)

        router.register_error_handler(Exception, error_handler)

        class TView(UiView):
            name = "test"
            endpoint = "/"

            def get(self):
                None["error"]  # type: ignore

        router.register_view(TView())
        res = router.tester().get("/")
        assert res.text == "error test"
        assert res.status_code == 0

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
        res = router.tester().get("/")
        assert res.status_code == 200

    def test_api_view_at_index(self, router: FlaskRouter):
        router.register_view(UiViewTester.create_view("/"))
        res = router.tester().get("/")
        assert res.status_code == 200

    def test_view_at_test(self, router: FlaskRouter):
        router.register_view(create_view("/test"))
        res = router.tester().get("/test")
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

        res = router.tester().get("/")
        assert int(res.data) == 1

        res = router.tester().get("/")
        assert int(res.data) == 2

    def test_view_router_access(self, router: FlaskRouter):
        router.secret = "Key of Heaven"  # type: ignore

        class SomeView(UiView):
            name = "some"
            endpoint = "/"
            reloads = True

            def get(self):
                return self.router.secret  # type: ignore

        router.register_view(SomeView())

        res = router.tester().get("/")
        assert res.data == b"Key of Heaven"

    def test_view_init_state(self):
        db = DatabaseManager("sqlite:///")
        storage = StorageManager(db=db)
        db.hidden_secret = "In Memory DB"  # type: ignore

        class SomeView(UiView):
            name = "some"
            endpoint = "/"
            reloads = True

            def init_state(self):
                self.router.storage.db.hidden_secret = "Memory DB"  # type: ignore

            def get(self):
                return self.router.storage.db.hidden_secret  # type: ignore

        router = FlaskRouter("testing", views=[SomeView()], storage=storage)

        res = router.tester().get("/")
        assert res.data == b"Memory DB"

    def test_view_data_reload(self, router: FlaskRouter):
        class SomeView(UiView):
            name = "some"
            endpoint = "/"
            reloads = True

            def __init__(self) -> None:
                super().__init__()
                self.count = 0

            def get(self):
                self.count += 1
                return str(self.count)

        router.register_view(SomeView())

        res = router.tester().get("/")
        assert int(res.data) == 1

        res = router.tester().get("/")
        assert int(res.data) == 1

    def test_view_data_reload_with_view_arg(self, router: FlaskRouter):
        class SomeView(UiView):
            name = "some"
            endpoint = "/"

            def __init__(self, count: int) -> None:
                super().__init__()
                self.count = count
                self.store_args(count)

            def get(self):
                self.count += 1
                return str(self.count)

        UiViewTester(SomeView(99)).test()

        router.register_view(SomeView(8))

        res = router.tester().get("/")
        assert int(res.data) == 9

        res = router.tester().get("/")
        assert int(res.data) == 9

    def test_view_multiple(self, router: FlaskRouter):
        router.register_view(create_view("/"))
        router.register_view(create_view("/test"))

        res = router.tester().get("/")
        assert res.status_code == 200

        res = router.tester().get("/test")
        assert res.status_code == 200

    def test_view_response(self, router: FlaskRouter):
        router.register_view(create_view("/"))
        router.register_view(create_view("/test", data="more testing"))

        res = router.tester().get("/")
        assert res.status_code == 200
        assert res.data == b"testing"

        res = router.tester().get("/test")
        assert res.status_code == 200
        assert res.data == b"more testing"

    def test_view_with_params(self, router: FlaskRouter):
        class SomeView(UiView):
            name = "test"
            endpoint = "/<string:some>"

            def get(self, some):
                return some

        router.register_view(SomeView())

        res = router.tester().get("/testing")
        assert res.status_code == 200
        assert res.data == b"testing"

    def test_view_with_post(self, router: FlaskRouter):
        class SomeView(UiView):
            name = "test"
            endpoint = "/"

            def post(self):
                return "Success"

        router.register_view(SomeView())

        res = router.tester().post("/")
        assert res.status_code == 200
        assert res.data == b"Success"

        res = router.tester().get("/")
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

        res = router.tester().post("/")
        assert res.status_code == 200
        assert res.data == b"Success"

        res = router.tester().get("/")
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

        assert router.tester().get("/").data == b"testing"
        assert router.tester().get("/test").data == b"test"
        assert router.tester().get("/test1").data == b"testing"
        assert router.tester().get("/test2").data == b"testing"
        assert router.tester().get("/nest/").data == b"testing"
        assert router.tester().get("/nest/nest2/").data == b"more test"
        assert router.tester().get("/nested/").data == b"testing"
        assert router.tester().get("/nested/test").data == b"testing"

    def test_route_error_handler(self, router: FlaskRouter):
        def error_handler1(error: Exception) -> Response:
            return Response("error", 0)

        def error_handler2(error: HTTPException) -> Response:
            return Response("http error", error.code)

        class TView(UiView):
            name = "test"
            endpoint = "/"

            def get(self):
                None["error"]  # type: ignore

            def post(self):
                abort(403)

        class TRoute(AppRoute[UiView]):
            name = "test"
            error_handlers = {Exception: error_handler1, HTTPException: error_handler2}

            def configure(self):
                super().configure()
                self.views = [TView()]

        router.register_route(TRoute())
        res = router.tester().get("/")
        assert res.text == "error"
        assert res.status_code == 0

        res = router.tester().post("/", json={})
        assert res.text == "http error"
        assert res.status_code == 403

    def test_route_with_multi_methods(self, router: FlaskRouter):
        class SomeView(UiView):
            name = "test"
            endpoint = "/"

            def post(self):
                return "Success"

            def get(self):
                return "No Data"

        router.register_route(create_route([SomeView()]))

        res = router.tester().post("/")
        assert res.status_code == 200
        assert res.data == b"Success"

        res = router.tester().get("/")
        assert res.status_code == 200
        assert res.data == b"No Data"

    def test_router_initialization(self):
        view1 = create_view("/")
        view2 = create_view("/test")
        route1 = create_route([create_view("/")], prefix="/one")

        router = FlaskRouter(__name__, views=[view1, view2], routes=[route1])

        assert router.tester().get("/").status_code == 200
        assert router.tester().get("/test").status_code == 200
        assert router.tester().get("/one/").status_code == 200

    def test_view_helpers(self, router: FlaskRouter):
        class SomeView(UiView):
            name = "test"
            endpoint = "/"

            def post(self):
                return self.serialize("Success")

            def get(self):
                return self.serialize("No Data")

        router.register_view(SomeView())

        assert router.tester().post("/").json == "Success"
        assert router.tester().get("/").json == "No Data"
