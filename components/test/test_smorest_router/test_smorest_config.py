from components.lib.smorest_router import SmorestConfig
from components.test._components._testers import InstanceTester


# ------------------------------------------------------------------------------
# Testers
# ------------------------------------------------------------------------------
class SmorestConfigTester(InstanceTester):
    def __init__(self, config: SmorestConfig) -> None:
        self.config = config

    def test_has_title(self):
        assert self.config.title

    def test_has_version(self):
        assert self.config.version

    def test_has_openapi_version(self):
        assert self.config.openapi_version

    def test_has_prefix(self):
        assert self.config.url_prefix
        assert self.config.url_prefix.startswith("/")

    @staticmethod
    def create_smorest_config(
        name: str | None = None,
        ui: str | None = None,
    ) -> SmorestConfig:
        return SmorestConfig(
            title=name or "api",
            version="v1",
            openapi_version="3.0.0",
            name=name or "",
            url_prefix="/" + (name or ""),
            swagger_ui=ui,
        )


# ------------------------------------------------------------------------------
# Test Cases
# ------------------------------------------------------------------------------
def test_smorest_config():
    config = SmorestConfigTester.create_smorest_config()
    SmorestConfigTester(config).test()
