# -*- coding: utf-8 -*-
""" MAIN MODULE """
from dbquery import DB
import dbmake
import settings
import time
from abc import ABCMeta


class Operator(object):
    """Operator class"""

    __metaclass__ = ABCMeta

    airline_id = settings.AIR_LINES
    PASSENGER_PAYMENT = settings.PASSENGER_PAYMENT
    CARGO_TON_PAYMENT = settings.CARGO_TON_PAYMENT

    ADD_FLIGHT_QUERY = "INSERT INTO flights (plane_id, date_time, passengers, cargo) " \
                       "values ({plane_id}, {date_time}, {passengers}, {cargo})"

    ADD_NOTIFICATION = "INSERT INTO notifications (airline_id, text, date_time) " \
                       "values ({airline_id}, '{text}', {date_time})"

    ADD_PLANE_QUERY = "INSERT INTO airlines_planes (airline_id, plane_id) " \
                      "values ({airline_id},{plane_id})"

    ADD_TRANSACTION = "INSERT INTO transactions (value, description, date_time, airline_id) " \
                      "values({value}, '{description}', {date_time}, {airline_id})"

    AIRLINE_STAT_QUERY = "SELECT a.id, a.balance, SUM(p.passengers) AS passengers, SUM(p.cargo) AS cargo, " \
                         "SUM((SELECT COUNT(*) FROM flights f WHERE f.plane_id=ap.id)) AS flights, SUM(p.price) AS price " \
                         "FROM planes p, airlines_planes ap, plane_types pt, airlines a " \
                         "WHERE ap.plane_id=p.id AND pt.id=p.plane_type_id AND ap.airline_id={airline_id} AND a.id = ap.airline_id " \
                         "GROUP BY a.id"

    BALANCE_QUERY = "SELECT balance " \
                    "FROM airlines " \
                    "WHERE id={id}"

    MARKET_PLANE_PRICE_QUERY = "SELECT price " \
                               "FROM planes " \
                               "WHERE id={plane_id}"

    MARKET_PLANES_QUERY = "SELECT p.id, p.name, pt.name AS type, price, passengers, cargo " \
                          "FROM planes p, plane_types pt " \
                          "WHERE pt.id=p.plane_type_id"

    MARKET_AVAILABLE_PLANES_QUERY = "SELECT * FROM planes AS p " \
                                    "WHERE p.price < (SELECT balance FROM airlines AS a WHERE a.id={airline_id})"

    DELETE_PLANE_QUERY = "DELETE " \
                         "FROM airlines_planes " \
                         "WHERE id={id}"

    FLIGHTS_QUERY = "SELECT f.id AS id, f.plane_id AS plane_id, p.name AS plane_name, f.passengers AS passengers, f.cargo AS cargo, f.date_time AS date_time " \
                    "FROM flights f, planes p, airlines_planes ap " \
                    "WHERE f.plane_id=ap.id AND ap.plane_id=p.id AND ap.airline_id={airline_id} " \
                    "ORDER BY date_time DESC LIMIT 16"

    GET_MANAGER_QUERY = "SELECT name " \
                        "FROM staff " \
                        "WHERE position='manager' AND airline_id={id} " \
                        "LIMIT 1;"

    GET_DISPATCHER_QUERY = "SELECT name " \
                           "FROM staff " \
                           "WHERE position='dispatcher' AND airline_id={id} " \
                           "LIMIT 1;"

    NOTIFICATIONS_QUERY = "SELECT id, text, date_time " \
                          "FROM notifications " \
                          "WHERE airline_id={airline_id} " \
                          "ORDER BY date_time DESC LIMIT 5"

    OWN_PLANE_PRICE_QUERY = "SELECT price FROM planes " \
                            "WHERE id=(SELECT plane_id FROM airlines_planes WHERE id ={id})"

    OWN_PLANES_QUERY = "SELECT ap.id, p.name, pt.name AS type, p.price, p.passengers, p.cargo, " \
                       "(SELECT COUNT(*) FROM flights f WHERE f.plane_id=ap.id) AS flights " \
                       "FROM airlines_planes ap, planes p, plane_types pt " \
                       "WHERE ap.plane_id=p.id AND pt.id = p.plane_type_id AND ap.airline_id={airline_id}"

    OWN_PLANES_TYPE_QUERY = OWN_PLANES_QUERY + " AND pt.name='{pt_name}'"

    OWN_PLANES_STAT_QUERY = "SELECT pt.name AS plane_type, COUNT(*) AS planes, SUM(p.passengers) AS passengers, SUM(p.cargo) AS cargo, " \
                            "SUM((SELECT COUNT(*) FROM flights f WHERE f.plane_id=ap.id)) AS flights, SUM(p.price) AS price " \
                            "FROM planes p, airlines_planes ap, plane_types pt " \
                            "WHERE ap.plane_id=p.id AND pt.id=p.plane_type_id AND ap.airline_id={airline_id} " \
                            "GROUP BY p.plane_type_id " \
                            "ORDER BY p.plane_type_id"

    TRANSACTIONS_QUERY = "SELECT id, value, description, date_time " \
                         "FROM transactions " \
                         "WHERE airline_id={airline_id} " \
                         "ORDER BY date_time DESC LIMIT 5"

    UPDATE_BALANCE_QUERY = "UPDATE airlines " \
                           "SET balance={balance} " \
                           "WHERE id={airline_id}"

    @property
    def balance(self):
        return DB.query(self.BALANCE_QUERY.format(id=self.airline_id))[0][0]

    @property
    def flights(self):
        return DB.query_mod(self.FLIGHTS_QUERY.format(airline_id=self.airline_id))

    @property
    def planes(self):
        return DB.query_mod(self.OWN_PLANES_QUERY.format(airline_id=self.airline_id))

    @property
    def passenger_planes(self):
        return DB.query_mod(self.OWN_PLANES_TYPE_QUERY.format(airline_id=self.airline_id, pt_name="passenger"))

    @property
    def cargo_planes(self):
        return DB.query_mod(self.OWN_PLANES_TYPE_QUERY.format(airline_id=self.airline_id, pt_name="cargo"))

    @property
    def market_planes(self):
        return DB.query_mod(self.MARKET_PLANES_QUERY)

    @property
    def planes_stat(self):
        return DB.query_mod(self.OWN_PLANES_STAT_QUERY.format(airline_id=self.airline_id))

    def _get_money(self, payment, description=""):
        new_balance = self.balance + payment
        DB.query(self.UPDATE_BALANCE_QUERY.format(balance=new_balance, airline_id=self.airline_id))
        DB.query(self.ADD_TRANSACTION.format(value=payment, description=description, date_time=time.time(), airline_id=self.airline_id))


class Manager(Operator):
    """Manager class"""
    def __init__(self):
        self.name = DB.query(self.GET_MANAGER_QUERY.format(id=settings.AIR_LINES))[0][0]

    def credit(self, money):
        money = float(money)
        self._get_money(money, "GET Credit")

    @property
    def airline_stat(self):
        return DB.query_mod(self.AIRLINE_STAT_QUERY.format(airline_id=self.airline_id))

    @property
    def transactions(self):
        return DB.query_mod(self.TRANSACTIONS_QUERY.format(airline_id=self.airline_id))

    @property
    def notifications(self):
        return DB.query_mod(self.NOTIFICATIONS_QUERY.format(airline_id=self.airline_id))

    @property
    def market_available_planes(self):
        return DB.query_mod(self.MARKET_AVAILABLE_PLANES_QUERY.format(airline_id=self.airline_id))

    def price_market_plane(self, plane_id):
        return DB.query(self.MARKET_PLANE_PRICE_QUERY.format(plane_id=plane_id))[0][0]

    def price_own_plane(self, plane_id):
        return DB.query(self.OWN_PLANE_PRICE_QUERY.format(id=plane_id))[0][0]

    def can_buy_plane(self, plane_id):
        return self.balance >= self.price_market_plane(plane_id)

    def _del_plane(self, plane_id):
        DB.query(self.DELETE_PLANE_QUERY.format(id=plane_id))

    def _add_plane(self, plane_id):
        DB.query(self.ADD_PLANE_QUERY.format(airline_id=self.airline_id, plane_id=plane_id))

    def _pay_money(self, payment, description=""):
        new_balance = self.balance - payment
        DB.query(self.UPDATE_BALANCE_QUERY.format(balance=new_balance, airline_id=self.airline_id))
        DB.query(self.ADD_TRANSACTION.format(value=-payment, description=description, date_time=time.time(), airline_id=self.airline_id))

    def buy_plane(self, plane_id):
        if self.can_buy_plane(plane_id):
            price = self.price_market_plane(plane_id)
            self._pay_money(price, "purchase plane # {}".format(plane_id))
            self._add_plane(plane_id)
        else:
            raise ValueError("No money - no honey")

    def sell_plane(self, plane_id):
        price = self.price_own_plane(plane_id)
        self._del_plane(plane_id)
        self._get_money(price, "sold plane # {}".format(plane_id))

    @classmethod
    def reset(cls, confirm="Y"):
        if confirm.lower() == "y":
            dbmake.delete_tables()
            dbmake.main()
        else:
            print("RESET WAS CANCELED")


class Dispatcher(Operator):
    """Dispatcher class"""
    def __init__(self):
        self.airline_id = settings.AIR_LINES
        self.name = DB.query(self.GET_DISPATCHER_QUERY.format(id=settings.AIR_LINES))[0][0]

    def _add_flight(self, plane_id, date_time, passengers, cargo):
        DB.query(self.ADD_FLIGHT_QUERY.format(plane_id=plane_id, date_time=date_time, passengers=passengers, cargo=cargo))
        payment = self.PASSENGER_PAYMENT * passengers + self.CARGO_TON_PAYMENT * cargo
        self._get_money(payment, "flight of plane # {}".format(plane_id))

    def flight(self, all_passengers, all_cargo):
        left_passengers = all_passengers
        left_cargo = all_cargo
        for plane in self.passenger_planes["data"]:
            if left_passengers <= 0:
                break
            plane_id, passengers = plane["id"], plane["passengers"]
            placed_passengers = passengers if passengers <= left_passengers else left_passengers
            self._add_flight(plane_id=plane_id, date_time=time.time(), passengers=placed_passengers, cargo=0)
            left_passengers -= placed_passengers
        for plane in self.cargo_planes["data"]:
            if left_cargo <= 0:
                break
            plane_id, cargo = plane["id"], plane["cargo"]
            placed_cargo = cargo if cargo <= left_cargo else left_cargo
            self._add_flight(plane_id=plane_id, date_time=time.time(), passengers=0, cargo=placed_cargo)
            left_cargo -= placed_cargo

        if left_passengers or left_cargo:
            notification = "NOT FLOUGHT: {} passengers and {} tons cargo".format(left_passengers, left_cargo)
        else:
            free_seats = self.planes_stat["data"][0]["passengers"] - all_passengers
            free_cargo = self.planes_stat["data"][1]["cargo"] - all_cargo
            notification = "FREE: {} seats and {} tons cargo".format(free_seats, free_cargo)
        self.push_notification(notification)

    def push_notification(self, notification):
        DB.query(self.ADD_NOTIFICATION.format(airline_id=self.airline_id, date_time=time.time(), text=notification))
