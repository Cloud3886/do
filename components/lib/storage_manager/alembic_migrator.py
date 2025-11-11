import importlib
import os
import pkgutil
from types import ModuleType
from typing import Callable

from alembic.migration import MigrationContext
from alembic.operations import Operations

from components.lib.storage_manager import DatabaseManager


class AlembicMigrator:
    def __init__(self, db: DatabaseManager, migration_versions: ModuleType) -> None:
        self.db = db
        self.migration_versions = migration_versions
        self.op = self._create_operations_object()

    def _create_operations_object(self) -> Operations:
        engine = self.db.engine
        mc = MigrationContext.configure(engine.connect())
        op = Operations(mc)
        return op

    def _configure_script(self, script: ModuleType, op: Operations):
        setattr(script, "op", op)

    def run_command(self, command: Callable[[ModuleType], None]):
        scripts = self.get_scripts()
        for script in scripts:
            self._configure_script(script, self.op)
            command(script)

    def upgrade_head(self):
        self.run_command(self._upgrade_head_command)

    @staticmethod
    def _upgrade_head_command(script: ModuleType):
        script.upgrade()

    def get_scripts(self) -> list[ModuleType]:
        scp_dir = self.migration_versions
        pkgpath = os.path.dirname(scp_dir.__file__)  # type: ignore
        scripts = [
            importlib.import_module(scp_dir.__name__ + "." + name)
            for _, name, _ in pkgutil.iter_modules([pkgpath])
            if not name.startswith("_")
        ]
        scripts.reverse()
        return scripts
