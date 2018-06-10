# -*- coding: utf-8 -*-
""" QUERY MODULE """
import sqlite3
import settings


class DB(object):

    db_file = settings.DB_FILE

    @classmethod
    def query(cls, query):
        conn = sqlite3.connect(cls.db_file)
        cur = conn.cursor()
        print(query)
        result = cur.execute(query).fetchall()
        conn.commit()
        conn.close()
        return result

    @classmethod
    def queries(cls, queries):
        conn = sqlite3.connect(cls.db_file)
        cur = conn.cursor()
        for query in queries:
            print(query)
            cur.execute(query)
        conn.commit()
        conn.close()
