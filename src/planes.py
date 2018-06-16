from dbquery import DB
import settings


class Plane(object):
    """Plane DB abstraction class"""

    ADD_FLIGHT_QUERY = "INSERT INTO flights (plane_id, date_time, passengers, cargo) " \
                       "values ({plane_id}, {date_time}, {passengers}, {cargo})"
    MARKET_PLANE_PRICE_QUERY = "SELECT price " \
                               "FROM planes " \
                               "WHERE id={plane_id}"
    OWN_PLANE_PRICE_QUERY = "SELECT price FROM planes " \
                            "WHERE id=(SELECT plane_id FROM airlines_planes WHERE id ={id})"
    FLIGHTS_QUERY = "SELECT f.id AS id, f.plane_id AS plane_id, p.name AS plane_name, f.passengers AS passengers, f.cargo AS cargo, f.date_time AS date_time " \
                    "FROM flights f, planes p, airlines_planes ap " \
                    "WHERE f.plane_id=ap.id AND ap.plane_id=p.id AND ap.airline_id={airline_id} " \
                    "ORDER BY date_time DESC LIMIT 16"
    OWN_PLANES_QUERY = "SELECT ap.id, p.name, pt.name AS type, p.price, p.passengers, p.cargo, " \
                       "(SELECT COUNT(*) FROM flights f WHERE f.plane_id=ap.id) AS flights " \
                       "FROM airlines_planes ap, planes p, plane_types pt " \
                       "WHERE ap.plane_id=p.id AND pt.id = p.plane_type_id AND ap.airline_id={airline_id}"
    OWN_PLANES_TYPE_QUERY = OWN_PLANES_QUERY + " AND pt.name='{pt_name}'"
    OWN_PLANES_STAT_QUERY = "SELECT pt.name AS plane_type, COUNT(*) AS planes, SUM(p.passengers) AS passengers, SUM(p.cargo) AS cargo, " \
                            "SUM((SELECT COUNT(*) FROM flights f WHERE f.plane_id=ap.id)) AS flights, SUM(p.price) AS price " \
                            "FROM planes p, airlines_planes ap, plane_types pt " \
                            "WHERE ap.plane_id=p.id AND pt.id=p.plane_type_id AND ap.airline_id={airline_id} " \
                            "GROUP BY p.plane_type_id " \
                            "ORDER BY p.plane_type_id"
    MARKET_PLANES_QUERY = "SELECT p.id, p.name, pt.name AS type, price, passengers, cargo " \
                          "FROM planes p, plane_types pt " \
                          "WHERE pt.id=p.plane_type_id"
    MARKET_AVAILABLE_PLANES_QUERY = "SELECT * FROM planes AS p " \
                                    "WHERE p.price < (SELECT balance FROM airlines AS a WHERE a.id={airline_id})"

    @classmethod
    def flight(cls, plane_id, date_time, passengers, cargo):
        DB.query(cls.ADD_FLIGHT_QUERY.format(plane_id=plane_id, date_time=date_time, passengers=passengers, cargo=cargo))
        settings.logger.info("FLIGHT by plane #{}: passengers: {}, cargo: {} tons".format(plane_id, passengers, cargo))

    @classmethod
    def price_market_plane(cls, plane_id):
        settings.logger.info("INQUIRE market price of the plane #{}".format(plane_id))
        return DB.query(cls.MARKET_PLANE_PRICE_QUERY.format(plane_id=plane_id))[0][0]

    @classmethod
    def price_own_plane(cls, plane_id):
        settings.logger.info("Get price of own plane #{}".format(plane_id))
        return DB.query(cls.OWN_PLANE_PRICE_QUERY.format(id=plane_id))[0][0]

    @classmethod
    def flights(cls, airline_id):
        settings.logger.info("SHOW FLIGHTS")
        return DB.query_mod(cls.FLIGHTS_QUERY.format(airline_id=airline_id))

    @classmethod
    def planes(cls, airline_id):
        settings.logger.info("SHOW COMPANY'S PLANES")
        return DB.query_mod(cls.OWN_PLANES_QUERY.format(airline_id=airline_id))

    @classmethod
    def passenger_planes(cls, airline_id):
        settings.logger.info("SHOW COMPANY'S PASSENGER PLANES")
        return DB.query_mod(cls.OWN_PLANES_TYPE_QUERY.format(airline_id=airline_id, pt_name="passenger"))

    @classmethod
    def cargo_planes(cls, airline_id):
        settings.logger.info("SHOW COMPANY'S CARGO PLANES")
        return DB.query_mod(cls.OWN_PLANES_TYPE_QUERY.format(airline_id=airline_id, pt_name="cargo"))

    @classmethod
    def market_planes(cls):
        settings.logger.info("SHOW PLANES IN MARKET")
        return DB.query_mod(cls.MARKET_PLANES_QUERY)

    @classmethod
    def planes_stat(cls, airline_id):
        settings.logger.info("SHOW STATISTICS BY PLANE TYPES")
        return DB.query_mod(cls.OWN_PLANES_STAT_QUERY.format(airline_id=airline_id))

    @classmethod
    def market_available_planes(cls, airline_id):
        settings.logger.info("SHOW AVAILABLE (FOR COST) PLANES")
        return DB.query_mod(cls.MARKET_AVAILABLE_PLANES_QUERY.format(airline_id=airline_id))
