from typing import Any, Callable, Concatenate
from .api_view import ApiView


class UiView(ApiView):
    def serialize(self, data):
        pass

    def render_template(self, template: str, **params) -> str:
        pass

    def _build(
        self,
        serialize: Callable[[Any], Any] = serialize,
        render_template: Callable[Concatenate[str, ...], str] = render_template,
        *args,
        **kwargs,
    ):
        self.serialize = serialize
        self.render_template = render_template
        self._ready = True
