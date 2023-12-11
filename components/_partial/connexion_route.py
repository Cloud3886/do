class ConnexionRoute:
    name: str = None
    prefix: str | None = None
    ui_path: str = "/docs"
    show_ui: bool = False
    spec_path: str = "openapi.yaml"
    resolver_path: str | None = None
