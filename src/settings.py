# -*- coding: utf-8 -*-
""" SETTINGS MODULE """
import random

DB_FILE = "airbase.db"
AIR_LINES = 1
PASSENGER_PAYMENT = 500
CARGO_TON_PAYMENT = 1000

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


# ######### DATABASE FILINGS ##################
FILLINGS = {
  "plane_types": [
    {
      "id": 1,
      "name": "passenger"
    },
    {
      "id": 2,
      "name": "cargo"
    }
  ],
  "planes": [
    {
      "id": 1,
      "name": "Airbus A330-300",
      "price": "240000000",
      "plane_type_id": 1,
      "passengers": 350,
      "cargo": 0
    },
    {
      "id": 2,
      "name": "Airbus A380-800",
      "price": "390000000",
      "plane_type_id": 1,
      "passengers": 525,
      "cargo": 0
    },
    {
      "id": 3,
      "name": "Boeing 737-900ER",
      "price": "100000000",
      "plane_type_id": 1,
      "passengers": 200,
      "cargo": 0
    },
    {
      "id": 4,
      "name": "Boeing 747-400",
      "price": "250000000",
      "plane_type_id": 1,
      "passengers": 416,
      "cargo": 0
    },
    {
      "id": 5,
      "name": "Airbus A330-200F",
      "price": "220000000",
      "plane_type_id": 2,
      "passengers": 0,
      "cargo": 70.0
    },
    {
      "id": 6,
      "name": "Boeing 747-8F",
      "price": "380000000",
      "plane_type_id": 2,
      "passengers": 0,
      "cargo": 134.2
    }
  ],
  "airlines": [
    {
      "id": 1,
      "name": "PyAir",
      "balance": 0.0
    }
  ],
  "staff": [
    {
      "airline_id": 1,
      "name": "John",
      "position": "manager"
    },
    {
      "airline_id": 1,
      "name": "Mark",
      "position": "dispatcher"
    }
  ]
}
#############################################


# ######## GENERATE STATE ###################
STATE = {
  "airlines_planes": list(
    {"airline_id": 1, "plane_id": random.randint(1, 6)} for _ in xrange(20)
  )
}
##############################################
