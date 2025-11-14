from components.lib.smorest_router.openapi_view import OpenapiView
from lib.src.features.todo.controller.todo_controller import TodoController


class TodoView(OpenapiView):
    name = "TodoView"
    endpoint = "/todo"
    
    def init_state(self):
        self.ctrl = TodoController()
    
    def get(self):
        return self.serialize(self.ctrl.get_todo())
    
    def post(self):
        # Respond with Redis PING as string, and optionally with todos as JSON
        ping_result = self.router.storage.redis.execute_command("PING")
        return {"redis": str(ping_result), "todos": self.serialize(self.ctrl.get_todo())}