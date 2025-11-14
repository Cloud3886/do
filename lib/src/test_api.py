from components.lib.basic_routes.app_route import AppRoute
from components.lib.smorest_router.openapi_view import OpenapiView


class TestView(OpenapiView):
    name = "TestView"
    endpoint = "/"
    
    
    def get(self):
        return self.serialize({"message": "Test API is working!"})
    
class RedisTestView(OpenapiView):
    name = "RedisTestView"
    endpoint = "/redis"
    
    
    def get(self):
        # Respond with Redis PING as string, and optionally with todos as JSON
        ping_result = self.router.storage.redis.execute_command("PING")
        return {"redis": str(ping_result)}

class TestRoute(AppRoute):
    name = "TestRoute"
    
    def configure(self):
        super().configure()
        self.views = [TestView(), RedisTestView()]