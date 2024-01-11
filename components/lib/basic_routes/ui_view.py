from typing import Any, Callable, Concatenate, Self

from components.lib.router.router import Router

from .api_view import ApiView


class UiView(ApiView):
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
        router: Router,
        serialize: Callable[..., Any] | None = None,
        render_template: Callable[Concatenate[str, ...], str] | None = None,
        *args,
        **kwargs,
    ):
        self._serialize = serialize
        self._render_template = render_template
        super()._build(router, *args, **kwargs)
