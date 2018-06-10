# -*- coding: utf-8 -*-
""" QUERY MODULE """
import sqlite3


class DB(object):

    @classmethod
    def query(cls, db_file, query):
        conn = sqlite3.connect(db_file)
        cur = conn.cursor()
        print(query)
        cur.execute(query)
        conn.commit()
        conn.close()

    @classmethod
    def queries(cls, db_file, queries):
        conn = sqlite3.connect(db_file)
        cur = conn.cursor()
        for query in queries:
            print(query)
            cur.execute(query)
        conn.commit()
        conn.close()
