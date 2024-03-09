import pytest

from components.lib.storage_manager import DatabaseManager
from components.test._components._testers import ClassTester


class TestDatabaseManager(ClassTester):
    @pytest.fixture
    def db(self) -> DatabaseManager:
        db = DatabaseManager("sqlite:///")
        return db

    def test_debug_log(self):
        import logging

        DatabaseManager("sqlite:///", debug=True)
        assert logging.getLogger("sqlalchemy.engine").level == logging.INFO

    def test_model_base(self, db: DatabaseManager):
        assert db.Base

    def test_model_base_metadata(self, db: DatabaseManager):
        assert db.metadata
        assert db.metadata == db.Base.metadata

    def test_engine_access(self, db: DatabaseManager):
        assert db.engine

    def test_session_factory(self, db: DatabaseManager):
        assert not db.session

        db.configure_session()

        assert db.session
