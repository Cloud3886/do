from dataclasses import dataclass, field
from enum import Enum, StrEnum
from typing import Protocol, runtime_checkable


class OpenapiSecurityScheme(Enum):
    pass


class OpenapiSecurityType(OpenapiSecurityScheme, StrEnum):
    apikey = "apiKey"
    http = "http"
    oauth = "oauth2"
    open_id = "openIdConnect"


class OpenapiSecurityLocation(OpenapiSecurityScheme, StrEnum):
    query = "query"
    header = "header"
    cookie = "cookie"


@dataclass(frozen=True)
class SmorestConfig:
    title: str
    version: str
    openapi_version: str
    name: str = ""
    url_prefix: str = "/"
    security_scheme: list["SmorestSecurityScheme"] = field(
        default_factory=lambda: [], hash=False
    )
    swagger_ui: str | None = None
    redoc_ui: str | None = None
    rapidoc_ui: str | None = None
    swagger_ui_url: str | None = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    redoc_ui_url: str | None = (
        "https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"
    )
    rapidoc_ui_url: str | None = "https://unpkg.com/rapidoc/dist/rapidoc-min.js"


@runtime_checkable
class SmorestSecurityScheme(Protocol):
    id: str
    description: str | None
    type: OpenapiSecurityType
    universally_enabled: bool

    def to_dict(self):
        json = self.__dict__.copy()
        if json.get("location"):
            json["in"] = json["location"]
            del json["location"]
        return json


@dataclass(frozen=True)
class SmorestApiKeySecurityScheme(SmorestSecurityScheme):
    id: str
    description: str | None = None
    name: str = "api_key"
    location: OpenapiSecurityLocation = OpenapiSecurityLocation.header
    universally_enabled: bool = False
    type: OpenapiSecurityType = field(init=False, default=OpenapiSecurityType.apikey)


@dataclass(frozen=True)
class SmorestHttpSecurityScheme(SmorestSecurityScheme):
    id: str
    scheme: str
    description: str | None = None
    universally_enabled: bool = False
    type: OpenapiSecurityType = field(init=False, default=OpenapiSecurityType.http)


@dataclass(frozen=True)
class SmorestBearerSecurityScheme(SmorestHttpSecurityScheme):
    id: str
    description: str | None = None
    bearerFormat: str = "JWT"
    universally_enabled: bool = False
    scheme: str = field(init=False, default="bearer")
