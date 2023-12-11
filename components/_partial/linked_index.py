from components.lib.views.ui_view import UiView


class LinkedIndex(UiView):
    name: str = "index"
    endpoint: str = "/"

    def __init__(self, links: list[str]) -> None:
        self.links = links
        if not (self._class_args or self._class_kwargs):
            self.store_args(links)
        super().__init__()

    def get(self):
        return self.render_template("index.html", links=self.links)
