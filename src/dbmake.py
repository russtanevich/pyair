"""SET DATABASE MODULE"""
if __package__:
    from . import settings
    from .dbquery import DB
    from .settings import FILLINGS, TABLES
else:
    import settings
    from dbquery import DB
    from settings import FILLINGS, TABLES


def delete_tables():
    """Delete all rows from configured tables."""
    queries = (f"DELETE FROM {key}" for key in TABLES)
    DB.queries(queries)
    settings.logger.info("CLEAR ALL TABLES")


def main():
    """Create database tables and populate initial data."""
    build_tables(tables=TABLES)
    fill_tables(fillings=FILLINGS)
    fill_tables(fillings=settings.generate_state())


def ensure_initialized():
    """Initialize tables and seed data if the database is empty."""
    existing = {
        row[0]
        for row in DB.query(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
    }
    if not set(TABLES).issubset(existing):
        main()
        return
    airlines_count = DB.query("SELECT COUNT(*) FROM airlines")[0][0]
    if airlines_count == 0:
        fill_tables(fillings=FILLINGS)
        fill_tables(fillings=settings.generate_state())


def _gen_fill_queries(fillings):
    for table, rows in fillings.items():
        if table not in TABLES:
            raise ValueError(f"Unknown table: {table}")
        for row in rows:
            keys = tuple(row.keys())
            values = tuple(row.values())
            cols = ", ".join(keys)
            placeholders = ", ".join("?" for _ in keys)
            sql = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"
            yield sql, values


def build_tables(tables):
    """Build database tables."""
    DB.queries(tables.values())
    settings.logger.info("BUILT %d TABLES", len(tables))


def fill_tables(fillings):
    """Fill database tables with initial rows."""
    DB.queries(_gen_fill_queries(fillings))
    settings.logger.info("FILLED tables")


if __name__ == "__main__":
    main()
