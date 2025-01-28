from lib.main import app
from . import controller 
from lib.database import create_session
from lib.models import *
from sqlalchemy import select

@app.route("/")
def getAtHome():
    return controller.getHome()

@app.route("/add")
def add():
    with create_session() as session:
        todo = Todo(
            name = "Tester",
            text = "Demo testing"
        )
        session.add_all([todo])
        session.commit()
        return "Success"

@app.route("/view")
def view():
    with create_session() as session:
        stmt = select(Todo)
        data = []
        for todo in session.scalars(stmt):
            data.append(todo.id)

        return data

    