# -*- coding: utf-8 -*-
""" MAIN MODULE """
from FINAL_TASK.src.dbquery import DB


class Manager(object):

    def __init__(self, staff_id):
        self.staff_id = staff_id
        query = "SELECT * FROM staff WHERE id={} LIMIT 1;".format(staff_id)
        data = DB.query("air")


    def buy_plane(self, plane_id):
        balance = DB.query()
