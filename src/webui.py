import flask


app = flask.Flask(__name__)
# flask.url_for('static', filename='css/dashboard.css')


@app.route("/")
def hello_world():
    # return 'Hello, World!'
    return flask.render_template('index.html', context={"a": 5, "b": 2})
