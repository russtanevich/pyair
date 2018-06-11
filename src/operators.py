# -*- coding: utf-8 -*-
""" MAIN MODULE """
from dbquery import DB
import settings


class Manager(object):

    COMMON_PLANE_PRICE_QUERY = "SELECT price FROM planes WHERE id={id}"
    BALANCE_QUERY = "SELECT balance FROM airlines WHERE id={id}"
    OWN_PLANE_PRICE_QUERY = "SELECT price FROM planes WHERE id=(SELECT plane_id FROM airlines_planes WHERE id ={id})"
    DELETE_PLANE_QUERY = "DELETE FROM airlines_planes WHERE id={id}"
    ADD_PLANE_QUERY = "INSERT INTO airlines_planes (airline_id, plane_id) values ({airline_id},{plane_id})"
    UPDATE_BALANCE_QUERY = "UPDATE airlines SET balance={balance} WHERE id={id}"
    OWN_PLANES_QUERY = "SELECT * FROM airlines_planes AS ap LEFT JOIN planes AS p WHERE ap.plane_id=p.id AND ap.airline_id={id}"
    OWN_COUNT_PLANES_QUERY = "SELECT COUNT(*) FROM airlines_planes WHERE airline_id={id}"
    COMMON_PLANES_QUERY = "SELECT * FROM planes"
    COMMON_AVAILABLE_PLANES_QUERY = "SELECT * FROM planes AS p WHERE p.price < (SELECT balance FROM airlines AS a WHERE a.id={id})"
    GET_MANAGER_QUERY = "SELECT name FROM staff WHERE airline_id={id} LIMIT 1;"

    def __init__(self):
        self.airline_id = settings.AIR_LINES
        self.name = DB.query(self.GET_MANAGER_QUERY.format(id=settings.AIR_LINES))[0][0]

    @property
    def balance(self):
        return DB.query(self.BALANCE_QUERY.format(id=self.airline_id))[0][0]

    def price_common_plane(self, plane_id):
        return DB.query(self.COMMON_PLANE_PRICE_QUERY.format(id=plane_id))[0][0]

    def price_own_plane(self, plane_id):
        return DB.query(self.OWN_PLANE_PRICE_QUERY.format(id=plane_id))[0][0]

    def can_buy_plane(self, plane_id):
        return self.balance > self.price_common_plane(plane_id)

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

    def _del_plane(self, plane_id):
        DB.query(self.DELETE_PLANE_QUERY.format(id=plane_id))

    def _add_plane(self, plane_id):
        DB.query(self.ADD_PLANE_QUERY.format(airline_id=self.airline_id, plane_id=plane_id))

    def _pay_money(self, payment):
        new_balance = self.balance - payment
        DB.query(self.UPDATE_BALANCE_QUERY.format(balance=new_balance, id=self.airline_id))

    def _get_money(self, payment):
        new_balance = self.balance + payment
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
