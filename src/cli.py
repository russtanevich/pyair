import operators
import argparse
import settings
from utils import draw_choices, sort_result


def check_mode():
    """CHECK COMMAND LINE ARGUMENTS"""
    parser = argparse.ArgumentParser(description="FLIGHT MANAGEMENT APPLICATION")
    parser.add_argument("-d", "--dispatcher", help="run in DISPATCHER MODE", action="store_true")
    parser.add_argument("-m", "--manager", help="run in MANAGER MODE", action="store_true")
    args = parser.parse_args()
    if not (args.manager or args.dispatcher):
        parser.print_help()
        exit(1)
    return args


def common_cycle(executor, mode_name, settings_cli):
    """COMMON CYCLE FOR MANAGERS AND DISPATCHERS"""
    while True:
        choices = settings_cli
        print(draw_choices(choices=choices))
        choice = raw_input("{} >> ".format(mode_name))
        solve = sort_result(executor=executor, choices=choices, num=int(choice))
        print solve


def manager_mode():
    """MANAGER MODE"""
    manager = operators.Manager()
    common_cycle(executor=manager, mode_name="MANAGER", settings_cli=settings.MANAGER_CLI)


def dispatcher_mode():
    """DISPATCHER MODE"""
    disp = operators.Dispatcher()
    common_cycle(executor=disp, mode_name="DISPATCHER", settings_cli=settings.DISPATCHER_CLI)


if __name__ == "__main__":
    mode = check_mode()
    if mode.manager:
        manager_mode()
    elif mode.dispatcher:
        dispatcher_mode()

