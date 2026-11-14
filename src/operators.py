"""MAIN MODULE"""
from abc import ABC
import math
import time

if __package__:
    from . import dbmake, settings
    from .dbquery import DB
    from .planes import Plane
else:
    import dbmake
    import settings
    from dbquery import DB
    from planes import Plane


class Operator(ABC):
    """Base operator class for airline roles."""

    airline_id = settings.AIR_LINES
    PASSENGER_PAYMENT = settings.PASSENGER_PAYMENT
    CARGO_TON_PAYMENT = settings.CARGO_TON_PAYMENT

    ADD_NOTIFICATION = (
        "INSERT INTO notifications (airline_id, text, date_time) "
        "VALUES (?, ?, ?)"
    )
    ADD_PLANE_QUERY = (
        "INSERT INTO airlines_planes (airline_id, plane_id) "
        "VALUES (?, ?)"
    )
    ADD_TRANSACTION = (
        "INSERT INTO transactions (value, description, date_time, airline_id) "
        "VALUES (?, ?, ?, ?)"
    )
    AIRLINE_STAT_QUERY = (
        "SELECT a.id, a.balance, SUM(p.passengers) AS passengers, "
        "SUM(p.cargo) AS cargo, "
        "SUM((SELECT COUNT(*) FROM flights f WHERE f.plane_id = ap.id)) AS flights, "
        "SUM(p.price) AS price "
        "FROM planes p, airlines_planes ap, plane_types pt, airlines a "
        "WHERE ap.plane_id = p.id AND pt.id = p.plane_type_id "
        "AND ap.airline_id = ? AND a.id = ap.airline_id "
        "GROUP BY a.id"
    )
    BALANCE_QUERY = "SELECT balance FROM airlines WHERE id = ?"
    DELETE_PLANE_QUERY = "DELETE FROM airlines_planes WHERE id = ?"
    GET_STAFF_QUERY = (
        "SELECT name FROM staff WHERE position = ? AND airline_id = ? LIMIT 1"
    )
    NOTIFICATIONS_QUERY = (
        "SELECT id, text, date_time FROM notifications "
        "WHERE airline_id = ? ORDER BY date_time DESC LIMIT 5"
    )
    TRANSACTIONS_QUERY = (
        "SELECT id, value, description, date_time FROM transactions "
        "WHERE airline_id = ? ORDER BY date_time DESC LIMIT 5"
    )
    UPDATE_BALANCE_QUERY = "UPDATE airlines SET balance = ? WHERE id = ?"

    def __init__(self):
        dbmake.ensure_initialized()

    @property
    def balance(self):
        settings.logger.info("SHOW COMPANY'S BALANCE")
        rows = DB.query(self.BALANCE_QUERY, (self.airline_id,))
        if not rows:
            raise ValueError(f"Airline #{self.airline_id} not found")
        return rows[0][0]

    @property
    def flights(self):
        return Plane.flights(airline_id=self.airline_id)

    @property
    def planes(self):
        return Plane.planes(airline_id=self.airline_id)

    @property
    def passenger_planes(self):
        return Plane.passenger_planes(airline_id=self.airline_id)

    @property
    def cargo_planes(self):
        return Plane.cargo_planes(airline_id=self.airline_id)

    @property
    def market_planes(self):
        return Plane.market_planes()

    @property
    def planes_stat(self):
        return Plane.planes_stat(airline_id=self.airline_id)

    def _record_balance_change(self, delta, description=""):
        new_balance = self.balance + delta
        now = time.time()
        DB.queries(
            [
                (self.UPDATE_BALANCE_QUERY, (new_balance, self.airline_id)),
                (
                    self.ADD_TRANSACTION,
                    (delta, description, now, self.airline_id),
                ),
            ]
        )

    def _get_money(self, payment, description=""):
        self._record_balance_change(payment, description)


class Manager(Operator):
    """Manager class."""

    def __init__(self):
        super().__init__()
        rows = DB.query(self.GET_STAFF_QUERY, ("manager", self.airline_id))
        self.name = rows[0][0] if rows else "Manager"

    @property
    def airline_stat(self):
        settings.logger.info("SHOW COMPANY'S STATISTICS")
        return DB.query_mod(self.AIRLINE_STAT_QUERY, (self.airline_id,))

    @property
    def transactions(self):
        settings.logger.info("SHOW TRANSACTIONS")
        return DB.query_mod(self.TRANSACTIONS_QUERY, (self.airline_id,))

    @property
    def notifications(self):
        settings.logger.info("SHOW notifications")
        return DB.query_mod(self.NOTIFICATIONS_QUERY, (self.airline_id,))

    @property
    def market_available_planes(self):
        return Plane.market_available_planes(airline_id=self.airline_id)

    def credit(self, money):
        amount = float(money)
        if not math.isfinite(amount) or amount <= 0:
            raise ValueError("Credit amount must be a positive number")
        self._get_money(amount, "GET Credit")

    def can_buy_plane(self, plane_id):
        settings.logger.info("Request for allowing to buy plane #%s", plane_id)
        return self.balance >= Plane.price_market_plane(plane_id)

    def _del_plane(self, plane_id):
        DB.query(self.DELETE_PLANE_QUERY, (int(plane_id),))

    def _add_plane(self, plane_id):
        DB.query(self.ADD_PLANE_QUERY, (self.airline_id, int(plane_id)))

    def _pay_money(self, payment, description=""):
        self._record_balance_change(-payment, description)
        settings.logger.info("%s: $%s", description, payment)

    def buy_plane(self, plane_id):
        plane_id = int(plane_id)
        if self.can_buy_plane(plane_id):
            price = Plane.price_market_plane(plane_id)
            self._pay_money(price, f"purchase plane # {plane_id}")
            self._add_plane(plane_id)
        else:
            raise ValueError("No money - no honey")

    def sell_plane(self, plane_id):
        plane_id = int(plane_id)
        price = Plane.price_own_plane(plane_id)
        self._del_plane(plane_id)
        self._get_money(price, f"sold plane # {plane_id}")

    @classmethod
    def reset(cls, confirm="Y"):
        if str(confirm).strip().lower() == "y":
            dbmake.delete_tables()
            dbmake.main()
            settings.logger.info("RESET SYSTEM")
        else:
            settings.logger.info("RESET WAS CANCELED")


class Dispatcher(Operator):
    """Dispatcher class."""

    def __init__(self):
        super().__init__()
        rows = DB.query(self.GET_STAFF_QUERY, ("dispatcher", self.airline_id))
        self.name = rows[0][0] if rows else "Dispatcher"

    def _add_flight(self, plane_id, date_time, passengers, cargo):
        Plane.flight(
            plane_id=plane_id,
            date_time=date_time,
            passengers=passengers,
            cargo=cargo,
        )
        payment = (
            self.PASSENGER_PAYMENT * passengers + self.CARGO_TON_PAYMENT * cargo
        )
        self._get_money(payment, f"flight of plane # {plane_id}")

    def _dispatch_planes(self, planes, capacity_key, remaining, is_cargo=False):
        for plane in planes:
            if remaining <= 0:
                break
            placed = min(plane[capacity_key], remaining)
            self._add_flight(
                plane_id=plane["id"],
                date_time=time.time(),
                passengers=0 if is_cargo else placed,
                cargo=placed if is_cargo else 0,
            )
            remaining -= placed
        return remaining

    def flight(self, all_passengers, all_cargo):
        all_passengers = int(all_passengers)
        all_cargo = float(all_cargo)
        if all_passengers < 0 or all_cargo < 0 or not math.isfinite(all_cargo):
            raise ValueError("Passengers and cargo must be non-negative")

        left_passengers = self._dispatch_planes(
            self.passenger_planes["data"], "passengers", all_passengers
        )
        left_cargo = self._dispatch_planes(
            self.cargo_planes["data"], "cargo", all_cargo, is_cargo=True
        )

        self._create_notifications(
            left_passengers, left_cargo, all_passengers, all_cargo
        )

    def _create_notifications(
        self, left_passengers, left_cargo, all_passengers, all_cargo
    ):
        notifications = []
        stats_by_type = {
            row["plane_type"]: row for row in self.planes_stat["data"]
        }

        if left_passengers:
            notifications.append(f"NOT SERVED: {left_passengers} passengers")
        else:
            total_seats = stats_by_type.get("passenger", {}).get("passengers") or 0
            free_seats = total_seats - all_passengers
            if free_seats > 0:
                notifications.append(f"NOT USED: {free_seats} passenger seats")

        if left_cargo:
            notifications.append(f"NOT SERVED: {left_cargo} tons cargo")
        else:
            total_cargo = stats_by_type.get("cargo", {}).get("cargo") or 0
            free_cargo = total_cargo - all_cargo
            if free_cargo > 0:
                notifications.append(f"NOT USED: {free_cargo} cargo tons")

        for notification in notifications:
            self.push_notification(notification)

    def push_notification(self, notification):
        DB.query(
            self.ADD_NOTIFICATION,
            (self.airline_id, notification, time.time()),
        )
        settings.logger.info("PUSH NOTIFICATION: <%s>", notification)
