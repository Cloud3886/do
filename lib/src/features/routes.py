from flask import config
from components.lib.basic_routes.app_route import AppRoute
from lib.src.features.todo.todo_routes import TodoRoute


class FeaturesRoutes(AppRoute):
    name = "FeaturesRoutes"
    
    def configure(self):
        super().configure()
        self.routes = [TodoRoute()]