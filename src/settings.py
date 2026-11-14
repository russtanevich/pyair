"""SETTINGS MODULE"""
from pathlib import Path
import logging
import random
import sys


# ######## APPLICATION SETTINGS #########
BASE_DIR = Path(__file__).resolve().parent
DB_FILE = str(BASE_DIR / "airbase.db")
LOGS_DIR = BASE_DIR / "logs"
AIR_LINES = 1
PASSENGER_PAYMENT = 500
CARGO_TON_PAYMENT = 1000
#########################################


# ########## LOGS #######################
def make_logger(logfile, log_name, screen=False):
    """LOGGER FACTORY"""
    log_path = Path(logfile)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name=log_name)
    if logger.handlers:
        return logger

    formatter = logging.Formatter("%(asctime)s - %(message)s")
    if screen:
        screen_handler = logging.StreamHandler(sys.stdout)
        screen_handler.setLevel(logging.INFO)
        screen_handler.setFormatter(formatter)
        logger.addHandler(screen_handler)

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)
    return logger


db_logger = make_logger(logfile=LOGS_DIR / "db.log", log_name="DB")
logger = make_logger(logfile=LOGS_DIR / "log.log", log_name="OPERATIONS")
########################################


# ######### CREATE TABLES ###############
TABLES = {
    "plane_types": """
    CREATE TABLE IF NOT EXISTS plane_types (
        id INTEGER PRIMARY KEY,
        name TEXT
    );""",
    "planes": """
    CREATE TABLE IF NOT EXISTS planes (
        id INTEGER PRIMARY KEY,
        plane_type_id INTEGER NOT NULL,
        name TEXT,
        price FLOAT,
        passengers INTEGER,
        cargo FLOAT,
        FOREIGN KEY(plane_type_id) REFERENCES plane_types(id)
    );""",
    "airlines": """
    CREATE TABLE IF NOT EXISTS airlines (
        id INTEGER PRIMARY KEY,
        name TEXT,
        balance FLOAT
    );""",
    "airlines_planes": """
    CREATE TABLE IF NOT EXISTS airlines_planes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        airline_id INTEGER,
        plane_id INTEGER,
        FOREIGN KEY(airline_id) REFERENCES airlines(id),
        FOREIGN KEY(plane_id) REFERENCES planes(id)
    );""",
    "flights": """
    CREATE TABLE IF NOT EXISTS flights (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plane_id INTEGER,
        date_time INTEGER,
        passengers INTEGER,
        cargo FLOAT,
        FOREIGN KEY(plane_id) REFERENCES planes(id)
    );""",
    "staff": """
    CREATE TABLE IF NOT EXISTS staff (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        airline_id INTEGER,
        name TEXT,
        position TEXT,
        FOREIGN KEY(airline_id) REFERENCES airlines(id)
    );""",
    "notifications": """
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        airline_id INTEGER,
        text TEXT,
        date_time INTEGER,
        FOREIGN KEY(airline_id) REFERENCES airlines(id)
    );""",
    "transactions": """
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        value INTEGER,
        description TEXT,
        date_time INTEGER,
        airline_id INTEGER,
        FOREIGN KEY(airline_id) REFERENCES airlines(id)
    );""",
}
###############################################


# ######### DATABASE FILLINGS #################
FILLINGS = {
    "plane_types": [
        {"id": 1, "name": "passenger"},
        {"id": 2, "name": "cargo"},
    ],
    "planes": [
        {
            "id": 1,
            "name": "Airbus A330-300",
            "price": 240000000.0,
            "plane_type_id": 1,
            "passengers": 350,
            "cargo": 0.0,
        },
        {
            "id": 2,
            "name": "Airbus A380-800",
            "price": 390000000.0,
            "plane_type_id": 1,
            "passengers": 525,
            "cargo": 0.0,
        },
        {
            "id": 3,
            "name": "Boeing 737-900ER",
            "price": 100000000.0,
            "plane_type_id": 1,
            "passengers": 200,
            "cargo": 0.0,
        },
        {
            "id": 4,
            "name": "Boeing 747-400",
            "price": 250000000.0,
            "plane_type_id": 1,
            "passengers": 416,
            "cargo": 0.0,
        },
        {
            "id": 5,
            "name": "Airbus A330-200F",
            "price": 220000000.0,
            "plane_type_id": 2,
            "passengers": 0,
            "cargo": 70.0,
        },
        {
            "id": 6,
            "name": "Boeing 747-8F",
            "price": 380000000.0,
            "plane_type_id": 2,
            "passengers": 0,
            "cargo": 134.2,
        },
    ],
    "airlines": [
        {"id": 1, "name": "PyAir", "balance": 0.0},
    ],
    "staff": [
        {"airline_id": 1, "name": "John", "position": "manager"},
        {"airline_id": 1, "name": "Mark", "position": "dispatcher"},
    ],
}
#############################################


# ######## GENERATE STATE ###################
def generate_state():
    """Generate initial random fleet state for the airline."""
    return {
        "airlines_planes": [
            {"airline_id": 1, "plane_id": random.randint(1, 6)} for _ in range(20)
        ]
    }


STATE = generate_state()
##############################################


# ######### MANAGER COMMAND LINE INTERFACE ###
MANAGER_CLI = {
    "header": ("description", "method", "action"),
    "data": (
        ("Airline STATISTICS", "airline_stat", None),
        ("Airplanes PARK", "planes", None),
        ("Airline planes STATISTICS", "planes_stat", None),
        ("Show latest FLIGHTS", "flights", None),
        ("Latest TRANSACTIONS", "transactions", None),
        ("Latest NOTIFICATIONS from dispatcher", "notifications", None),
        ("MARKET planes", "market_planes", None),
        (
            "BUY plane",
            "buy_plane",
            {
                "description": (
                    "What plane would you like to buy? "
                    "There is showing only available for purchase planes.\n"
                    "Input <N>/<n> if want to cancel."
                ),
                "show": "market_available_planes",
            },
        ),
        (
            "SELL_PLANE",
            "sell_plane",
            {
                "description": (
                    "What plane would you like to sell?\n"
                    "Input <N>/<n> if want to cancel."
                ),
                "show": "planes",
            },
        ),
        (
            "Get CREDIT",
            "credit",
            {
                "description": (
                    "How much money do want to get?\n"
                    "Input <N>/<n> if want to cancel."
                ),
                "show": None,
            },
        ),
        (
            "RESET",
            "reset",
            {
                "description": (
                    "Do you really want to reset?\n"
                    "Input <Y>/<y> to confirm."
                ),
                "show": None,
            },
        ),
    ),
}
##############################################


# ###### DISPATCHER COMMAND LINE INTERFACE ###
DISPATCHER_CLI = {
    "header": ("description", "method", "action"),
    "data": (
        ("Show latest FLIGHTS", "flights", None),
        ("New FLIGHT", "flight", "new_flight"),
    ),
}
##############################################
