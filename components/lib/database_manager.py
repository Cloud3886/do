from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session


class DatabaseManager:
    def __init__(self, DB_URI: str) -> None:
        self.Base = declarative_base()
        self.metadata = self.Base.metadata

        self.engine = self._engine(DB_URI)
        self.SessionScoped = None

    # def create_local_session(self):
    #     session = self.SessionLocal()
    #     return session

    def create_session(self):
        if not self.SessionScoped:
            self.configure_scoped_session()

        session = self.SessionScoped()
        return session

    def configure_scoped_session(self, scope_func=None):
        SessionScoped = self._scoped_session_factory(self.engine, scope_func)
        self.SessionScoped = SessionScoped
        self.Base.query = self.SessionScoped.query_property()
        return SessionScoped

    @staticmethod
    def _engine(DB_URI: str) -> Engine:
        engine = create_engine(DB_URI, connect_args={"check_same_thread": False})
        return engine

    @staticmethod
    def _session_factory(engine: Engine):
        SessionLocal = sessionmaker(engine, autoflush=False, autocommit=False)
        return SessionLocal

    @staticmethod
    def _scoped_session_factory(engine: Engine, scope_func):
        SessionLocal = sessionmaker(engine, autoflush=False, autocommit=False)
        SessionScoped = scoped_session(SessionLocal, scopefunc=scope_func)
        return SessionScoped
