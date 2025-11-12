from components.lib.basic_routes.app_route import AppRoute


class TodoRoute(AppRoute):
    name = "TodoRoute"

    def configure(self):
        super().configure()
        from lib.src.features.todo.view.todo import TodoView

        self.views = [TodoView()]