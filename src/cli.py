import operators
import argparse
import sqlite3


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

        conn = sqlite3.connect("airbase.db")
        cur = conn.cursor()
        query = "SELECT * FROM flights;"
        response = cur.execute(query)
        header = tuple(arr[0] for arr in response.description)
        result = response.fetchall()
        result.insert(0, header)
        conn.commit()
        conn.close()
        for row in result:
            print "|".join("{:>16}".format(str(_)) for _ in row)


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

