from typing import TYPE_CHECKING, Any, Callable, Concatenate, TypeVar

from .api_view import ApiView

if TYPE_CHECKING:
    from components.lib.flask_router.flask_router import FlaskRouter

T = TypeVar("T", bound="FlaskRouter")


class UiView(ApiView[T]):
    def serialize(self, data):
        serializer = getattr(self, "_serialize", None)
        if serializer:
            return serializer(data)

    def render_template(self, template: str, **params):
        renderer = getattr(self, "_render_template", None)
        if renderer:
            return renderer(template, **params)

    def _build(
        self,
        router: T,
        serialize: Callable[..., Any] | None = None,
        render_template: Callable[Concatenate[str, ...], str] | None = None,
        *args,
        **kwargs,
    ):
        self._serialize = serialize
        self._render_template = render_template
        super()._build(router, *args, **kwargs)
