from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker


class DatabaseManager:
    def __init__(self, DB_URI: str) -> None:
        self._set_base_model()

        self.engine = self._engine(DB_URI)
        self.session = None

    def configure_session(self, scope_func=None):
        SessionScoped = self._scoped_session_factory(self.engine, scope_func)
        self.session = SessionScoped
        self.Base.query = self.session.query_property()

    def _set_base_model(self):
        self.Base = declarative_base()
        self.metadata = self.Base.metadata

    @classmethod
    def _engine(cls, DB_URI: str) -> Engine:
        return create_engine(DB_URI)

    @classmethod
    def _session_factory(cls, engine: Engine):
        return sessionmaker(engine, autoflush=False, autocommit=False)

    @classmethod
    def _scoped_session_factory(cls, engine: Engine, scope_func):
        return scoped_session(cls._session_factory(engine), scope_func)
