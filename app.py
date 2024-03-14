from werkzeug.middleware.proxy_fix import ProxyFix
import identity
import identity.web
from flask import Flask, redirect, render_template, request, session, url_for
from flask_session import Session

import app_config

app = Flask(__name__)
app.config.from_object(app_config)
Session(app)

app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

auth = identity.web.Auth(
    session=session,
    authority=app.config.get("AUTHORITY"),
    client_id=app.config["CLIENT_ID"],
    client_credential=app.config["CLIENT_SECRET"],
)


@app.route("/login")
def login():
    return render_template("login.html", version=identity.__version__, **auth.log_in(
        scopes=app_config.SCOPE,
        redirect_uri=url_for("auth_response", _external=True),
    ))


@app.route(app_config.REDIRECT_PATH)
def auth_response():
    auth.complete_log_in(request.args)

    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    return redirect(auth.log_out(url_for("index", _external=True)))


@app.route("/")
def index():
    if not auth.get_user():
        return redirect(url_for("login"))
    return render_template('index.html', user=auth.get_user(), version=identity.__version__)

if __name__ == "__main__":
    app.run(host='localhost')
    
