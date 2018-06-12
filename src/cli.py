import operators
import argparse


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
    while True:
        print("MANAGER MODE")
        raw_input()


def dispatcher_mode():
    while True:
        print("DISPATCHER MODE")
        raw_input()


if __name__ == "__main__":

    mode = check_mode()

    if mode.manager:
        manager_mode()
    elif mode.dispatcher:
        dispatcher_mode()

#
# man = operators.Manager()
# disp = operators.Dispatcher(manager=man)
#
#
# disp.flight(5000, 400)
#
# print man.notifications
