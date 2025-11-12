from components.lib.smorest_router.openapi_view import OpenapiView
from lib.src.features.todo.controller.todo_controller import TodoController


class TodoView(OpenapiView):
    name = "TodoView"
    endpoint = "/todo"
    
    def init_state(self):
        self.ctrl = TodoController()
    
    def get(self):
        return self.serialize(self.ctrl.get_todo())