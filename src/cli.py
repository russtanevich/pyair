import operators
import argparse
import sqlite3
from utils import date_filter
from dbquery import DB


def check_mode():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dispatcher", help="run in DISPATCHER MODE", action="store_true")
    parser.add_argument("-m", "--manager", help="run in MANAGER MODE", action="store_true")
    args = parser.parse_args()
    if args.manager and args.dispatcher:
        raise ValueError("SPECIFY only ONE MODE: -d or -m")
    if not (args.manager or args.dispatcher):
        raise ValueError("SPECIFY -d or -m MODE")
    return args


def draw_table(query):
    response = DB.query_mod(query)
    print "|".join(
        (
            "{:>16}".format(str(col)) for col in response["header"])
    )
    for row in response["data"]:
        print "|".join(("{:>16}".format(str(row[col])) for col in response["header"]))



def manager_mode():
    man = operators.Manager()
    while True:
        choices = {
            "1": "planes",
            "2": "planes_stat",
            "3": "buy_plane"
        }
        # print(choices)
        choice = raw_input("MANAGER MODE >> ")

        draw_table("SELECT id, TIME(date_time) FROM flights")



def dispatcher_mode():
    disp = operators.Dispatcher()
    while True:
        print("DISPATCHER MODE")
        raw_input("D")


if __name__ == "__main__":

    mode = check_mode()

    if mode.manager:
        manager_mode()
    elif mode.dispatcher:
        dispatcher_mode()

