from flask import Flask, render_template, request, redirect
import operators
import datetime
import dbmake
import utils


app = Flask(__name__)
man = operators.Manager()
disp = operators.Dispatcher()


print man.planes_stat


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
        "can_buy_plane": man.can_buy_plane
    }
    print(man.transactions)
    return render_template('index.html', **context)


@app.route('/flight', methods=['POST'])
def flight():
    if request.method == 'POST':
        data = request.values
        disp.flight(all_passengers=int(data["passengers"]), all_cargo=float(data["cargo"]))
    return redirect("/")


@app.route("/reset")
def reset():
    man.reset(confirm="y")
    return redirect("/")


@app.route("/sell_<plane_id>")
def sell(plane_id):
    man.sell_plane(plane_id=plane_id)
    return redirect("/")


@app.route("/buy_<plane_id>")
def buy(plane_id):
    man.buy_plane(plane_id=plane_id)
    return redirect("/")


@app.route("/credit", methods=["POST"])
def credit():
    if request.method == "POST":
        money = float(request.values["credit"])
        man.credit(money)
    return redirect("/")

