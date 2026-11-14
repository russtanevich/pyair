"""QUERY MODULE"""
import sqlite3

if __package__:
    from . import settings
else:
    import settings


class DB:
    """SQLite database helper."""

    db_file = settings.DB_FILE

    @classmethod
    def _log_query(cls, query, params=()):
        if params:
            settings.db_logger.info("%s | params=%s", query, params)
        else:
            settings.db_logger.info(query)

    @classmethod
    def query(cls, query, params=()):
        """Execute a single SQL query and return fetched rows."""
        conn = sqlite3.connect(cls.db_file)
        try:
            with conn:
                cur = conn.cursor()
                cls._log_query(query, params)
                return cur.execute(query, params).fetchall()
        finally:
            conn.close()

    @classmethod
    def query_mod(cls, query, params=()):
        """Execute a SQL query and return header tuple and dict rows."""
        conn = sqlite3.connect(cls.db_file)
        try:
            with conn:
                cur = conn.cursor()
                cls._log_query(query, params)
                response = cur.execute(query, params)
                header = (
                    tuple(col[0] for col in response.description)
                    if response.description
                    else ()
                )
                data = response.fetchall()
                return {
                    "header": header,
                    "data": tuple(
                        dict(zip(header, row)) for row in data
                    ),
                }
        finally:
            conn.close()

    @classmethod
    def queries(cls, queries):
        """Execute a sequence of SQL statements or (sql, params) pairs."""
        conn = sqlite3.connect(cls.db_file)
        try:
            with conn:
                cur = conn.cursor()
                for item in queries:
                    if isinstance(item, tuple):
                        sql, params = item
                    else:
                        sql, params = item, ()
                    cls._log_query(sql, params)
                    cur.execute(sql, params)
        finally:
            conn.close()
