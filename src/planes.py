"""PLANE DB MODULE"""
if __package__:
    from . import settings
    from .dbquery import DB
else:
    import settings
    from dbquery import DB


class Plane:
    """Plane DB abstraction class."""

    ADD_FLIGHT_QUERY = (
        "INSERT INTO flights (plane_id, date_time, passengers, cargo) "
        "VALUES (?, ?, ?, ?)"
    )
    MARKET_PLANE_PRICE_QUERY = "SELECT price FROM planes WHERE id = ?"
    OWN_PLANE_PRICE_QUERY = (
        "SELECT price FROM planes "
        "WHERE id = (SELECT plane_id FROM airlines_planes WHERE id = ?)"
    )
    FLIGHTS_QUERY = (
        "SELECT f.id AS id, f.plane_id AS plane_id, p.name AS plane_name, "
        "f.passengers AS passengers, f.cargo AS cargo, f.date_time AS date_time "
        "FROM flights f, planes p, airlines_planes ap "
        "WHERE f.plane_id = ap.id AND ap.plane_id = p.id AND ap.airline_id = ? "
        "ORDER BY date_time DESC LIMIT 16"
    )
    OWN_PLANES_QUERY = (
        "SELECT ap.id, p.name, pt.name AS type, p.price, p.passengers, p.cargo, "
        "(SELECT COUNT(*) FROM flights f WHERE f.plane_id = ap.id) AS flights "
        "FROM airlines_planes ap, planes p, plane_types pt "
        "WHERE ap.plane_id = p.id AND pt.id = p.plane_type_id AND ap.airline_id = ?"
    )
    OWN_PLANES_TYPE_QUERY = OWN_PLANES_QUERY + " AND pt.name = ?"
    OWN_PLANES_STAT_QUERY = (
        "SELECT pt.name AS plane_type, COUNT(*) AS planes, "
        "SUM(p.passengers) AS passengers, SUM(p.cargo) AS cargo, "
        "SUM((SELECT COUNT(*) FROM flights f WHERE f.plane_id = ap.id)) AS flights, "
        "SUM(p.price) AS price "
        "FROM planes p, airlines_planes ap, plane_types pt "
        "WHERE ap.plane_id = p.id AND pt.id = p.plane_type_id AND ap.airline_id = ? "
        "GROUP BY p.plane_type_id "
        "ORDER BY p.plane_type_id"
    )
    MARKET_PLANES_QUERY = (
        "SELECT p.id, p.name, pt.name AS type, price, passengers, cargo "
        "FROM planes p, plane_types pt "
        "WHERE pt.id = p.plane_type_id"
    )
    MARKET_AVAILABLE_PLANES_QUERY = (
        "SELECT p.id, p.name, pt.name AS type, p.price, p.passengers, p.cargo "
        "FROM planes p, plane_types pt "
        "WHERE pt.id = p.plane_type_id "
        "AND p.price <= (SELECT balance FROM airlines AS a WHERE a.id = ?)"
    )

    @classmethod
    def flight(cls, plane_id, date_time, passengers, cargo):
        DB.query(
            cls.ADD_FLIGHT_QUERY,
            (int(plane_id), date_time, int(passengers), float(cargo)),
        )
        settings.logger.info(
            "FLIGHT by plane #%s: passengers: %s, cargo: %s tons",
            plane_id,
            passengers,
            cargo,
        )

    @classmethod
    def price_market_plane(cls, plane_id):
        settings.logger.info("INQUIRE market price of the plane #%s", plane_id)
        rows = DB.query(cls.MARKET_PLANE_PRICE_QUERY, (int(plane_id),))
        if not rows:
            raise ValueError(f"Market plane #{plane_id} not found")
        return rows[0][0]

    @classmethod
    def price_own_plane(cls, plane_id):
        settings.logger.info("Get price of own plane #%s", plane_id)
        rows = DB.query(cls.OWN_PLANE_PRICE_QUERY, (int(plane_id),))
        if not rows:
            raise ValueError(f"Owned plane #{plane_id} not found")
        return rows[0][0]

    @classmethod
    def flights(cls, airline_id):
        settings.logger.info("SHOW FLIGHTS")
        return DB.query_mod(cls.FLIGHTS_QUERY, (int(airline_id),))

    @classmethod
    def planes(cls, airline_id):
        settings.logger.info("SHOW COMPANY'S PLANES")
        return DB.query_mod(cls.OWN_PLANES_QUERY, (int(airline_id),))

    @classmethod
    def passenger_planes(cls, airline_id):
        settings.logger.info("SHOW COMPANY'S PASSENGER PLANES")
        return DB.query_mod(cls.OWN_PLANES_TYPE_QUERY, (int(airline_id), "passenger"))

    @classmethod
    def cargo_planes(cls, airline_id):
        settings.logger.info("SHOW COMPANY'S CARGO PLANES")
        return DB.query_mod(cls.OWN_PLANES_TYPE_QUERY, (int(airline_id), "cargo"))

    @classmethod
    def market_planes(cls):
        settings.logger.info("SHOW PLANES IN MARKET")
        return DB.query_mod(cls.MARKET_PLANES_QUERY)

    @classmethod
    def planes_stat(cls, airline_id):
        settings.logger.info("SHOW STATISTICS BY PLANE TYPES")
        return DB.query_mod(cls.OWN_PLANES_STAT_QUERY, (int(airline_id),))

    @classmethod
    def market_available_planes(cls, airline_id):
        settings.logger.info("SHOW AVAILABLE (FOR COST) PLANES")
        return DB.query_mod(cls.MARKET_AVAILABLE_PLANES_QUERY, (int(airline_id),))
