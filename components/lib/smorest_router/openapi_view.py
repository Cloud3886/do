from copy import deepcopy
from functools import wraps
from typing import TYPE_CHECKING, Any, TypeVar, cast

from components.lib.basic_routes.ui_view import UiView
from components.lib.smorest_router.smorest_config import SmorestSecurityScheme

if TYPE_CHECKING:
    from components.lib.smorest_router.smorest_router import SmorestRouter

T = TypeVar("T", bound="SmorestRouter")


class OpenapiView(UiView[T]):
    @classmethod
    def arguments(
        cls,
        schema,
        *,
        location="json",
        content_type=None,
        required=True,
        description=None,
        example=None,
        examples=None,
        **kwargs,
    ):
        return cls._add_viewdoc(
            "arguments",
            schema=schema,
            location=location,
            content_type=content_type,
            required=required,
            description=description,
            example=example,
            examples=examples,
            **kwargs,
        )

    @classmethod
    def response(
        cls,
        status_code,
        schema=None,
        *,
        content_type=None,
        description=None,
        example=None,
        examples=None,
        headers=None,
    ):
        return cls._add_viewdoc(
            "response",
            status_code=status_code,
            schema=schema,
            content_type=content_type,
            description=description,
            example=example,
            examples=examples,
            headers=headers,
        )

    @classmethod
    def alt_response(
        cls,
        status_code,
        response=None,
        *,
        schema=None,
        content_type=None,
        description=None,
        example=None,
        examples=None,
        headers=None,
        success=False,
    ):
        return cls._add_viewdoc(
            "alt_response",
            status_code=status_code,
            response=response,
            schema=schema,
            content_type=content_type,
            description=description,
            example=example,
            examples=examples,
            headers=headers,
            success=success,
        )

    @classmethod
    def security_scheme(cls, scheme: SmorestSecurityScheme | str):
        scheme_id = cast(str | None, getattr(scheme, "id", None)) or scheme
        return cls.custom_doc(manual_doc={"security": [{scheme_id: []}]})

    # @staticmethod
    # def paginate():
    #     pass

    # @staticmethod
    # def etag():
    #     pass

    @classmethod
    def custom_doc(cls, **kwargs):
        return cls._add_viewdoc("custom", **kwargs)

    @classmethod
    def _add_viewdoc(cls, decoration: str, **kwargs):
        def decorator(method):
            @wraps(method)
            def wrapped(*args, **kwargs):
                return method(*args, **kwargs)

            wrapped._viewdoc = deepcopy(getattr(wrapped, "_viewdoc", {}))  # type: ignore
            docs: list = wrapped._viewdoc.setdefault(decoration, [])  # type: ignore
            docs.append(kwargs)

            return wrapped

        return decorator
