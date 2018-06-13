# -*- coding: utf-8 -*-
""" SET DATABASE MODULE """
from settings import TABLES, FILLINGS, STATE
from dbquery import DB


def delete_tables():
    queries = ("DELETE FROM {}".format(key) for key in TABLES)
    DB.queries(queries)


def main():
    build_tables(tables=TABLES)
    fill_tables(fillings=FILLINGS)
    fill_tables(fillings=STATE)


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


def build_tables(tables):
    """build database function"""
    queries = tables.values()
    DB.queries(queries=queries)


def fill_tables(fillings):
    """FILL database tables"""
    queries = _gen_fill_queries(fillings)
    DB.queries(queries=queries)


if __name__ == "__main__":
    main()



