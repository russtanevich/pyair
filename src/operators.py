# -*- coding: utf-8 -*-
""" MAIN MODULE """
from dbquery import DB
import settings
import time
from abc import ABCMeta


class Operator(object):
    """Operator class"""

    __metaclass__ = ABCMeta

    airline_id = settings.AIR_LINES
    PASSENGER_PAYMENT = settings.PASSENGER_PAYMENT
    CARGO_TON_PAYMENT = settings.CARGO_TON_PAYMENT

    UPDATE_BALANCE_QUERY = "UPDATE airlines SET balance={balance} WHERE id={id}"
    BALANCE_QUERY = "SELECT balance FROM airlines WHERE id={id}"
    CAPACITY_PASSENGERS_QUERY = """
        SELECT SUM(passengers)
        FROM airlines_planes AS ap LEFT JOIN planes AS p
        ON ap.plane_id=p.id
        WHERE ap.airline_id={id}"""
    CAPACITY_CARGO_QUERY = """
        SELECT SUM(cargo)
        FROM airlines_planes AS ap LEFT JOIN planes AS p
        ON ap.plane_id=p.id
        WHERE ap.airline_id={id}"""
    COMMON_PLANE_PRICE_QUERY = "SELECT price FROM planes WHERE id={id}"
    OWN_PLANE_PRICE_QUERY = """
        SELECT price FROM planes
        WHERE id=(SELECT plane_id FROM airlines_planes WHERE id ={id})"""
    DELETE_PLANE_QUERY = "DELETE FROM airlines_planes WHERE id={id}"
    ADD_PLANE_QUERY = "INSERT INTO airlines_planes (airline_id, plane_id) values ({airline_id},{plane_id})"
    OWN_PLANES_QUERY = "SELECT * FROM airlines_planes AS ap LEFT JOIN planes AS p ON ap.plane_id=p.id WHERE ap.airline_id={id}"
    OWN_COUNT_PLANES_QUERY = "SELECT COUNT(*) FROM airlines_planes WHERE airline_id={id}"
    COMMON_PLANES_QUERY = "SELECT * FROM planes"
    COMMON_AVAILABLE_PLANES_QUERY = "SELECT * FROM planes AS p WHERE p.price < (SELECT balance FROM airlines AS a WHERE a.id={id})"
    GET_MANAGER_QUERY = "SELECT name FROM staff WHERE position='manager' AND airline_id={id} LIMIT 1;"
    GET_DISPATCHER_QUERY = "SELECT name FROM staff WHERE position='dispatcher' AND airline_id={id} LIMIT 1;"
    OWN_DISP_PLANES_QUERY = """
        SELECT ap.id, p.passengers, p.cargo
        FROM airlines_planes AS ap LEFT JOIN planes AS p
        WHERE ap.plane_id=p.id AND ap.airline_id={id}"""
    ADD_FLIGHT_QUERY = "INSERT INTO flights (plane_id, date_time, passengers, cargo) values ({plane_id}, {date_time}, {passengers}, {cargo})"
    ADD_NOTIFICATION = "INSERT INTO notifications (airline_id, text, date_time) values ({airline_id}, {text}, {date_time})"

    @property
    def balance(self):
        return DB.query(self.BALANCE_QUERY.format(id=self.airline_id))[0][0]

    @property
    def passengers_capacity(self):
        return DB.query(self.CAPACITY_PASSENGERS_QUERY.format(id=self.airline_id))[0][0]

    @property
    def cargo_capacity(self):
        return DB.query(self.CAPACITY_CARGO_QUERY.format(id=self.airline_id))[0][0]

    def _get_money(self, payment):
        new_balance = self.balance + payment
        DB.query(self.UPDATE_BALANCE_QUERY.format(balance=new_balance, id=self.airline_id))


class Manager(Operator):
    """Manager class"""
    def __init__(self):
        self.name = DB.query(self.GET_MANAGER_QUERY.format(id=settings.AIR_LINES))[0][0]
        self._notifications = []

    @property
    def notifications(self):
        return self._notifications

    def clear_notifications(self):
        self._notifications = []

    @property
    def planes(self):
        return DB.query(self.OWN_PLANES_QUERY.format(id=self.airline_id))

    @property
    def common_planes(self):
        return DB.query(self.COMMON_PLANES_QUERY)

    @property
    def common_available_planes(self):
        return DB.query(self.COMMON_AVAILABLE_PLANES_QUERY.format(id=self.airline_id))

    @property
    def count_planes(self):
        return DB.query(self.OWN_COUNT_PLANES_QUERY.format(id=self.airline_id))[0][0]

    def price_common_plane(self, plane_id):
        return DB.query(self.COMMON_PLANE_PRICE_QUERY.format(id=plane_id))[0][0]

    def price_own_plane(self, plane_id):
        return DB.query(self.OWN_PLANE_PRICE_QUERY.format(id=plane_id))[0][0]

    def can_buy_plane(self, plane_id):
        return self.balance > self.price_common_plane(plane_id)

    def _del_plane(self, plane_id):
        DB.query(self.DELETE_PLANE_QUERY.format(id=plane_id))

    def _add_plane(self, plane_id):
        DB.query(self.ADD_PLANE_QUERY.format(airline_id=self.airline_id, plane_id=plane_id))

    def _pay_money(self, payment):
        new_balance = self.balance - payment
        DB.query(self.UPDATE_BALANCE_QUERY.format(balance=new_balance, id=self.airline_id))

    def buy_plane(self, plane_id):
        if self.can_buy_plane(plane_id):
            price = self.price_common_plane(plane_id)
            self._pay_money(price)
            self._add_plane(plane_id)
        else:
            raise ValueError("No money - no honey")

    def sell_plane(self, plane_id):
        price = self.price_own_plane(plane_id)
        self._del_plane(plane_id)
        self._get_money(price)


class Dispatcher(Operator):
    """Dispatcher class"""
    def __init__(self):
        self.airline_id = settings.AIR_LINES
        self.name = DB.query(self.GET_DISPATCHER_QUERY.format(id=settings.AIR_LINES))[0][0]

    def _add_flight(self, plane_id, date_time, passengers, cargo):
        DB.query(self.ADD_FLIGHT_QUERY.format(plane_id=plane_id, date_time=date_time, passengers=passengers, cargo=cargo))

    def flight(self, all_passengers, all_cargo):
        left_passengers = all_passengers
        left_cargo = all_cargo
        planes = DB.query(self.OWN_DISP_PLANES_QUERY.format(id=self.airline_id))
        for plane in planes:
            plane_id, passengers, cargo = plane
            placed_passengers = passengers if passengers <= left_passengers else left_passengers
            placed_cargo = cargo if cargo <= left_cargo else left_cargo
            self._add_flight(plane_id=plane_id, date_time=time.time(), passengers=placed_passengers, cargo=placed_cargo)
            payment = self.PASSENGER_PAYMENT * placed_passengers + self.CARGO_TON_PAYMENT * placed_cargo
            self._get_money(payment)
            left_passengers -= placed_passengers
            left_cargo -= placed_cargo
            if left_passengers <= 0 and left_cargo <= 0:
                break
        if left_passengers or left_cargo:
            notification = "LEFT: {} passengers and {} ton cargo".format(left_passengers, left_cargo)
            self.push_notification(notification)

    def push_notification(self, notification):
        DB.query(self.ADD_NOTIFICATION.format(airline_id=self.airline_id, date_time=time.time(), text=notification))
