# -*- coding: utf-8 -*-
""" SET DATABASE MODULE """
import sqlite3
from tables import tables, fillings, state
from dbquery.query import DB


def _gen_fill_queries(fillings):
    for table in fillings:
        for raw in fillings[table]:
            pairs = raw.items()
            keys = tuple(pair[0] for pair in pairs)
            values = tuple(pair[1] for pair in pairs)
            query = "INSERT INTO {table} {keys} values {values}".format(
                table=table, keys=str(keys), values=str(values)
            )
            yield query


def build_tables(db_file, tables):
    """build database function"""
    queries = tables.values()
    DB.queries(db_file=db_file, queries=queries)


def fill_tables(db_file, fillings):
    """FILL database tables"""
    queries = _gen_fill_queries(fillings)
    DB.queries(db_file=db_file, queries=queries)


if __name__ == "__main__":

    DB_FILE = "airbase.db"

    build_tables(db_file=DB_FILE, tables=tables)
    fill_tables(db_file=DB_FILE, fillings=fillings)
    fill_tables(db_file=DB_FILE, fillings=state)




