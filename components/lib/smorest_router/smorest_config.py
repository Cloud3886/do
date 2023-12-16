class SmorestConfig:
    def __init__(
        self,
        title: str,
        version: str,
        openapi_version: str,
        name: str = "",
        url_prefix: str = "/",
        swagger_ui: str | None = None,
        redoc_ui: str | None = None,
        rapidoc_ui: str | None = None,
        swagger_ui_url: str | None = None,
        redoc_ui_url: str | None = None,
        rapidoc_ui_url: str | None = None,
    ) -> None:
        self.name = name
        self.API_TITLE = title
        self.API_VERSION = version
        self.OPENAPI_VERSION = openapi_version
        self.OPENAPI_URL_PREFIX = url_prefix

        self.OPENAPI_SWAGGER_UI_PATH = swagger_ui
        self.OPENAPI_REDOC_PATH = redoc_ui
        self.OPENAPI_RAPIDOC_PATH = rapidoc_ui

        self.OPENAPI_SWAGGER_UI_URL = (
            swagger_ui_url or "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
        )
        self.OPENAPI_REDOC_URL = (
            redoc_ui_url
            or "https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"
        )
        self.OPENAPI_RAPIDOC_URL = (
            rapidoc_ui_url or "https://unpkg.com/rapidoc/dist/rapidoc-min.js"
        )
