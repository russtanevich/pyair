# -*- coding: utf-8 -*-
""" MAIN MODULE """
from dbquery import DB
import dbmake
import settings
import time
from abc import ABCMeta
from planes import Plane


class Operator(object):
    """Operator class"""

    __metaclass__ = ABCMeta

    airline_id = settings.AIR_LINES
    PASSENGER_PAYMENT = settings.PASSENGER_PAYMENT
    CARGO_TON_PAYMENT = settings.CARGO_TON_PAYMENT

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
    DELETE_PLANE_QUERY = "DELETE " \
                         "FROM airlines_planes " \
                         "WHERE id={id}"
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
    TRANSACTIONS_QUERY = "SELECT id, value, description, date_time " \
                         "FROM transactions " \
                         "WHERE airline_id={airline_id} " \
                         "ORDER BY date_time DESC LIMIT 5"
    UPDATE_BALANCE_QUERY = "UPDATE airlines " \
                           "SET balance={balance} " \
                           "WHERE id={airline_id}"

    @property
    def balance(self):
        settings.logger.info("SHOW COMPANY'S BALANCE")
        return DB.query(self.BALANCE_QUERY.format(id=self.airline_id))[0][0]

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

    def _get_money(self, payment, description=""):
        new_balance = self.balance + payment
        DB.query(self.UPDATE_BALANCE_QUERY.format(balance=new_balance, airline_id=self.airline_id))
        DB.query(self.ADD_TRANSACTION.format(value=payment, description=description, date_time=time.time(), airline_id=self.airline_id))


class Manager(Operator):
    """Manager class"""
    def __init__(self):
        self.name = DB.query(self.GET_MANAGER_QUERY.format(id=settings.AIR_LINES))[0][0]

    @property
    def airline_stat(self):
        settings.logger.info("SHOW COMPANY'S STATISTICS")
        return DB.query_mod(self.AIRLINE_STAT_QUERY.format(airline_id=self.airline_id))

    @property
    def transactions(self):
        settings.logger.info("SHOW TRANSACTIONS")
        return DB.query_mod(self.TRANSACTIONS_QUERY.format(airline_id=self.airline_id))

    @property
    def notifications(self):
        settings.logger.info("SHOW notifications")
        return DB.query_mod(self.NOTIFICATIONS_QUERY.format(airline_id=self.airline_id))

    @property
    def market_available_planes(self):
        return Plane.market_available_planes(airline_id=self.airline_id)

    def credit(self, money):
        self._get_money(float(money), "GET Credit")

    def can_buy_plane(self, plane_id):
        settings.logger.info("Request for allowing to buy plane #{}".format(plane_id))
        return self.balance >= Plane.price_market_plane(plane_id)

    def _del_plane(self, plane_id):
        DB.query(self.DELETE_PLANE_QUERY.format(id=plane_id))

    def _add_plane(self, plane_id):
        DB.query(self.ADD_PLANE_QUERY.format(airline_id=self.airline_id, plane_id=plane_id))

    def _pay_money(self, payment, description=""):
        new_balance = self.balance - payment
        DB.query(self.UPDATE_BALANCE_QUERY.format(balance=new_balance, airline_id=self.airline_id))
        DB.query(self.ADD_TRANSACTION.format(value=-payment, description=description, date_time=time.time(), airline_id=self.airline_id))
        settings.logger.info("{}: ${}".format(description, payment))

    def buy_plane(self, plane_id):
        if self.can_buy_plane(plane_id):
            price = Plane.price_market_plane(plane_id)
            self._pay_money(price, "purchase plane # {}".format(plane_id))
            self._add_plane(plane_id)
        else:
            raise ValueError("No money - no honey")

    def sell_plane(self, plane_id):
        price = Plane.price_own_plane(plane_id)
        self._del_plane(plane_id)
        self._get_money(price, "sold plane # {}".format(plane_id))

    @classmethod
    def reset(cls, confirm="Y"):
        if confirm.lower() == "y":
            dbmake.delete_tables()
            dbmake.main()
            settings.logger.info("RESET SYSTEM")
        else:
            settings.logger.info("RESET WAS CANCELED")


class Dispatcher(Operator):
    """Dispatcher class"""
    def __init__(self):
        self.airline_id = settings.AIR_LINES
        self.name = DB.query(self.GET_DISPATCHER_QUERY.format(id=settings.AIR_LINES))[0][0]

    def _add_flight(self, plane_id, date_time, passengers, cargo):
        Plane.flight(plane_id=plane_id, date_time=date_time, passengers=passengers, cargo=cargo)
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
        self._create_notifications(left_passengers, left_cargo, all_passengers, all_cargo)

    def _create_notifications(self, left_passengers, left_cargo, all_passengers, all_cargo):
        notifications = []
        if left_passengers:
            notifications.append("NOT SERVED: {} passengers".format(left_passengers))
        else:
            free_seats = self.planes_stat["data"][0]["passengers"] - all_passengers
            if free_seats > 0:
                notifications.append("NOT USED: {} passenger seats".format(free_seats))
        if left_cargo:
            notifications.append("NOT SERVED: {} tons cargo".format(left_cargo))
        else:
            free_cargo = self.planes_stat["data"][1]["cargo"] - all_cargo
            if free_cargo > 0:
                notifications.append("NOT USED: {} cargo tons".format(free_cargo))
        for notification in notifications:
            self.push_notification(notification)

    def push_notification(self, notification):
        DB.query(self.ADD_NOTIFICATION.format(airline_id=self.airline_id, date_time=time.time(), text=notification))
        settings.logger.info("PUSH NOTIFICATION:  <{}>".format(notification))
