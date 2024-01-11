import marshmallow as ma
import pytest
import sqlalchemy.util as sql_tools
from flask import Flask
from flask_smorest import Api

from components.lib.database_manager import DatabaseManager
from components.lib.smorest_router import (
    OpenapiView,
    SmorestRouter,
)
from components.test.test_basic_routes.test_app_route import AppRouteTester
from components.test.test_flask_router.test_flask_router import (
    TestFlaskRouter as FlaskRouterTester,
)
from components.utils.extensions import prettify

from .test_openapi_view import OpenapiViewTester
from .test_smorest_config import SmorestConfigTester

create_view = OpenapiViewTester.create_view
create_route = AppRouteTester.create_route


class TestSmorestRouter(FlaskRouterTester):
    @pytest.fixture
    def router(self) -> SmorestRouter:
        router = SmorestRouter(__name__)
        return router

    def test_router_app(self):
        router = SmorestRouter("test")
        assert isinstance(router.app, Flask)
        assert router.app.import_name == "test"

    def test_router_with_database(self):
        db = DatabaseManager("sqlite:///")
        router = SmorestRouter("test_router", views=[create_view("/")], db=db)
        assert router.db
        assert isinstance(router.app.session.registry, sql_tools.ScopedRegistry)  # type: ignore

        router.tester().get("/")
        router.tester().get("/")

    def test_view_init_state(self):
        db = DatabaseManager("sqlite:///")
        db.hidden_secret = "In Memory DB"  # type: ignore

        class SomeView(OpenapiView):
            name = "some"
            endpoint = "/"
            reloads = True

            def init_state(self):
                self.router.db.hidden_secret = "Memory DB"  # type: ignore

            def get(self):
                return self.router.db.hidden_secret  # type: ignore

        router = SmorestRouter("testing", views=[SomeView()], db=db)

        res = router.tester().get("/")
        assert res.data == b"Memory DB"

    def test_router_initialization(self):
        view1 = create_view("/")
        view2 = create_view("/test")
        route1 = create_route([create_view("/")], prefix="/one")

        router = SmorestRouter(__name__, views=[view1, view2], routes=[route1])

        assert router.tester().get("/").status_code == 200
        assert router.tester().get("/test").status_code == 200
        assert router.tester().get("/one/").status_code == 200

    def test_view_helpers(self, router: SmorestRouter):
        class SomeView(OpenapiView):
            name = "test"
            endpoint = "/"

            def post(self):
                return self.serialize("Success")

            def get(self):
                return self.serialize("No Data")

        router.register_view(SomeView())

        assert router.tester().post("/").json == "Success"
        assert router.tester().get("/").json == "No Data"

    def test_router_add_api(self, router: SmorestRouter):
        config = SmorestConfigTester.create_smorest_config()
        api = router.add_api(config)
        assert isinstance(api, Api)

    def test_router_add_api_with_spec(self, router: SmorestRouter):
        config = SmorestConfigTester.create_smorest_config()
        assert router.apis == {}
        api = router.add_api(config, [create_route([create_view("/")])])
        assert api in router.apis
        assert config == router.apis[api]
        assert router.tester().get("/").status_code == 200

    def test_router_multiple_apis(self, router: SmorestRouter):
        api1 = router.add_api(
            SmorestConfigTester.create_smorest_config("v1", ui="/ui"),
            [
                create_route([create_view("/")]),
                create_route([create_view("/")], prefix="/v1"),
            ],
        )
        api2 = router.add_api(
            SmorestConfigTester.create_smorest_config(ui="/ui"),
            [create_route([create_view("/")])],
        )
        api3 = router.add_api(
            SmorestConfigTester.create_smorest_config("v2", ui="/ui"),
            [create_route([create_view("/")])],
        )

        assert api1 in router.apis
        assert api2 in router.apis
        assert api3 in router.apis

        assert router.tester().get("/v1/").status_code == 200
        assert router.tester().get("/v1/v1/").status_code == 200
        assert router.tester().get("/v1/ui").status_code == 200

        assert router.tester().get("/").status_code == 200
        assert router.tester().get("/ui").status_code == 200

        assert router.tester().get("/v2/").status_code == 200
        assert router.tester().get("/v2/ui").status_code == 200

    def test_api_direct_access(self, router: SmorestRouter):
        api1 = router.add_api(SmorestConfigTester.create_smorest_config("v1"), [])
        api2 = router.add_api(SmorestConfigTester.create_smorest_config(), [])
        api3 = router.add_api(SmorestConfigTester.create_smorest_config("v2_long"), [])

        assert api2 == router.api
        assert api1 == router.api_v1  # type: ignore
        assert api3 == router.api_v2_long  # type: ignore

    def test_router_params(self):
        router = SmorestRouter(
            "test",
            views=[create_view("/")],
            routes=[create_route([create_view("/")], prefix="/flask")],
            openapi_spec={
                SmorestConfigTester.create_smorest_config("v1", ui="/ui"): [
                    create_route([create_view("/")])
                ],
                SmorestConfigTester.create_smorest_config("v2", ui="/ui"): [
                    create_route([create_view("/")]),
                    create_route([create_view("/")], prefix="/more"),
                ],
            },
        )

        assert router.tester().get("/").status_code == 200
        assert router.tester().get("/flask/").status_code == 200
        assert router.tester().get("/v1/").status_code == 200
        assert router.tester().get("/v1/ui").status_code == 200
        assert router.tester().get("/v2/").status_code == 200
        assert router.tester().get("/v2/more/").status_code == 200
        assert router.tester().get("/v2/ui").status_code == 200

    def test_register_route_with_api(self, router: SmorestRouter):
        api = router.add_api(SmorestConfigTester.create_smorest_config())
        router.register_route_with_api(api, create_route([create_view("/")]))
        router.register_route_with_api(
            api, create_route([create_view("/")], prefix="/nest")
        )

        assert router.tester().get("/").status_code == 200
        assert router.tester().get("/nest/").status_code == 200

    def test_generate_openapi_json(self, router: SmorestRouter):
        api = router.add_api(
            SmorestConfigTester.create_smorest_config(ui="/ui"),
            [create_route([create_view("/")])],
        )

        openapi_json = router.generate_openapi_json(api)
        print(prettify(openapi_json))

        assert "get" in openapi_json["paths"]["/"]

    def test_view_decorators(self, router: SmorestRouter):
        class One(ma.Schema):
            id = ma.fields.Int(dump_only=True)
            name = ma.fields.String()

        class Two(ma.Schema):
            name = ma.fields.String()

        class SomeView(OpenapiView):
            name = "test"
            endpoint = "/"

            @OpenapiView.arguments(One)
            @OpenapiView.arguments(Two, location="query")
            @OpenapiView.response(200, One)
            def get(self, *args):
                """Get Testing"""
                return "testing"

            @OpenapiView.arguments(One)
            @OpenapiView.arguments(Two)
            @OpenapiView.alt_response(202, schema=Two)
            @OpenapiView.response(201, One)
            def post(self, *args):
                """Post Testing"""
                return "testing"

        api = router.add_api(
            SmorestConfigTester.create_smorest_config(), [create_route([SomeView()])]
        )

        openapi_json = router.generate_openapi_json(api)
        print(prettify(openapi_json))

        # Test Arguments
        assert "One" in openapi_json["components"]["schemas"]
        assert "Two" in openapi_json["components"]["schemas"]

        # Test Alt Response
        assert "202" in openapi_json["paths"]["/"]["post"]["responses"]

        # Test Response
        assert "200" in openapi_json["paths"]["/"]["get"]["responses"]
        assert "201" in openapi_json["paths"]["/"]["post"]["responses"]

        assert openapi_json["paths"]["/"]["get"]["summary"] == "Get Testing"
        assert openapi_json["paths"]["/"]["post"]["summary"] == "Post Testing"
