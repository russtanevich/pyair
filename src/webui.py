"""Flask web UI for PyAir."""
import os
from flask import Flask, flash, redirect, render_template, request, url_for

if __package__:
    from . import operators, utils
else:
    import operators
    import utils


app = Flask(__name__)
app.secret_key = os.environ.get("PYAIR_SECRET_KEY", "pyair-dev-secret")
man = operators.Manager()
disp = operators.Dispatcher()


@app.route("/")
def home_page():
    context = {
        "own_planes": man.planes,
        "market_planes": man.market_planes,
        "balance": man.balance,
        "manager_name": man.name,
        "planes_stat": man.planes_stat,
        "transactions": man.transactions,
        "notifications": man.notifications,
        "dispatcher_name": disp.name,
        "flights": disp.flights,
        "date_filter": utils.date_filter,
        "can_buy_plane": man.can_buy_plane,
    }
    return render_template("index.html", **context)


@app.route("/flight", methods=["POST"])
def flight():
    try:
        passengers = int(request.form["passengers"])
        cargo = float(request.form["cargo"])
        disp.flight(all_passengers=passengers, all_cargo=cargo)
    except (KeyError, ValueError) as exc:
        flash(f"Flight error: {exc}", "danger")
    return redirect(url_for("home_page"))


@app.route("/reset", methods=["GET", "POST"])
def reset():
    man.reset(confirm="y")
    flash("System has been reset.", "success")
    return redirect(url_for("home_page"))


@app.route("/sell_<int:plane_id>")
def sell(plane_id):
    try:
        man.sell_plane(plane_id=plane_id)
    except ValueError as exc:
        flash(str(exc), "danger")
    return redirect(url_for("home_page"))


@app.route("/buy_<int:plane_id>")
def buy(plane_id):
    try:
        man.buy_plane(plane_id=plane_id)
    except ValueError as exc:
        flash(str(exc), "danger")
    return redirect(url_for("home_page"))


@app.route("/credit", methods=["POST"])
def credit():
    try:
        money = float(request.form["credit"])
        man.credit(money)
    except (KeyError, ValueError) as exc:
        flash(f"Credit error: {exc}", "danger")
    return redirect(url_for("home_page"))


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG", "").lower() in ("1", "true"))
