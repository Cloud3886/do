import pytest
from components.lib.database_manager import DatabaseManager
from components.test._components._testers import ClassTester


class TestDatabaseManager(ClassTester):
    @pytest.fixture
    def db(self) -> DatabaseManager:
        db = DatabaseManager("sqlite:///")
        return db

    def test_model_base(self, db: DatabaseManager):
        assert db.Base

    def test_model_base_metadata(self, db: DatabaseManager):
        assert db.metadata

    def test_engine_access(self, db: DatabaseManager):
        assert db.engine

    def test_session(self, db: DatabaseManager):
        session = db.create_session()
        assert session
