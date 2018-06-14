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
    def query_mod(cls, query):
        conn = sqlite3.connect(cls.db_file)
        cur = conn.cursor()
        print(query)
        response = cur.execute(query)
        header = tuple(arr[0] for arr in response.description)
        data = response.fetchall()
        conn.commit()
        conn.close()
        return {"header": header,
                "data": tuple({ key: val for key, val in zip(header, row)} for row in data )}

    @classmethod
    def queries(cls, queries):
        conn = sqlite3.connect(cls.db_file)
        cur = conn.cursor()
        for query in queries:
            print(query)
            cur.execute(query)
        conn.commit()
        conn.close()
