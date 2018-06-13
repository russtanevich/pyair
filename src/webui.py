from flask import Flask, render_template, request, redirect
import operators
import datetime
import dbmake


app = Flask(__name__)
man = operators.Manager()
disp = operators.Dispatcher()


@app.route("/")
def home_page():
    context = {
        "own_planes": man.planes,
        "market_planes": man.market_planes,
        "balance": man.balance,
        "manager_name": man.name,

        "count_passenger_planes": man.count_passenger_planes,
        "passengers_capacity": man.passengers_capacity,
        "passenger_flights": man.passenger_flights,

        "count_cargo_planes": man.count_cargo_planes,
        "cargo_capacity": man.cargo_capacity,
        "cargo_flights": man.cargo_flights,

        "notifications": man.notifications,

        "dispatcher_name": disp.name,
        "flights": disp.flights,
        "strftime": datetime.datetime.utcfromtimestamp
    }
    return render_template('index.html', **context)


@app.route('/flight', methods=['POST'])
def flight():
    if request.method == 'POST':
        data = request.values
        disp.flight(all_passengers=int(data["passengers"]), all_cargo=float(data["cargo"]))
    return redirect("/")


@app.route("/reset")
def reset():
    dbmake.delete_tables()
    dbmake.main()
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
        credit = float(request.values["credit"])
        man._get_money(credit)
    return redirect("/")

