from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from lib.models import Base

engine = create_engine("sqlite:///db.db", echo=True)
Base.metadata.create_all(engine)
def create_session():
    return Session(engine)

