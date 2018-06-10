# -*- coding: utf-8 -*-
""" MAIN MODULE """
import sqlite


class Manager(object):

    def buy_plane(self, plane_id):
        conn = sqlite3.connect(db_file)
        cur = conn.cursor()
        for table in tables:
            query = tables[table]
            print(query)
            cur.execute(query)
        conn.commit()
        conn.close()
