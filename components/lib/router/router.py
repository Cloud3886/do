from abc import abstractmethod
from typing import Any, Protocol

from flask import Flask

from components.lib.database_manager.database_manager import DatabaseManager


class Router(Protocol):
    def __init__(self) -> None:
        super().__init__()
        self.app: Flask
        self.db: DatabaseManager
