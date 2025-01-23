from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return {
        "abcd": "abeds"
    }

def foo():
    return "LOL"
app.route("/abc")(foo)