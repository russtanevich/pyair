# -*- coding: utf-8 -*-
""" MAIN MODULE """
from dbquery import DB
import settings


class Manager(object):

    def __init__(self):
        self.airline_id = settings.AIR_LINES
        query = "SELECT * FROM staff WHERE airline_id={} LIMIT 1;".format(settings.AIR_LINES)
        data = DB.query(query=query)[0]
        self.name = data[2]

    def buy_plane(self, plane_id):
        query = "SELECT balance FROM airlines WHERE id={}".format(self.airline_id)
        data = DB.query(query=query)[0]
        print data[0]

    def sell_plane(self, plane_id):
        query = "SELECT balance FROM airlines WHERE id={}".format(self.airline_id)
        curr_balance = DB.query(query=query)[0][0]
        query = "SELECT price FROM planes WHERE id=(SELECT plane_id FROM airlines_planes WHERE id ={})".format(plane_id)
        price = DB.query(query=query)[0][0]
        DB.query("UPDATE airlines SET balance={} WHERE id={}".format(curr_balance+price, self.airline_id))
