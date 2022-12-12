from flask import Flask

app = Flask(__name__)


@app.post('/')
def test():
    return "OK"


app.run(host="0.0.0.0")