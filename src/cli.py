"""CLI entry point for PyAir."""
import argparse
import sys

if __package__:
    from . import operators, settings
    from .utils import draw_choices, sort_result
else:
    import operators
    import settings
    from utils import draw_choices, sort_result


def check_mode(argv=None):
    """CHECK COMMAND LINE ARGUMENTS"""
    parser = argparse.ArgumentParser(
        description="FLIGHT MANAGEMENT APPLICATION"
    )
    parser.add_argument(
        "-d", "--dispatcher", help="run in DISPATCHER MODE", action="store_true"
    )
    parser.add_argument(
        "-m", "--manager", help="run in MANAGER MODE", action="store_true"
    )
    args = parser.parse_args(argv)
    if not (args.manager or args.dispatcher):
        parser.print_help()
        sys.exit(1)
    return args


def manager_mode():
    """MANAGER MODE"""
    manager = operators.Manager()
    common_cycle(
        executor=manager, mode_name="MANAGER", settings_cli=settings.MANAGER_CLI
    )


def dispatcher_mode():
    """DISPATCHER MODE"""
    disp = operators.Dispatcher()
    common_cycle(
        executor=disp,
        mode_name="DISPATCHER",
        settings_cli=settings.DISPATCHER_CLI,
    )


def validate_choice(choice, choices):
    """CHECK CHOICE FOR VALIDATION. SKIP UNVALIDATED INPUT"""
    try:
        idx = int(choice)
    except (TypeError, ValueError):
        return False
    return 0 <= idx < len(choices["data"])


def common_cycle(executor, mode_name, settings_cli):
    """COMMON CYCLE FOR MANAGERS AND DISPATCHERS"""
    choices = settings_cli
    while True:
        print(draw_choices(choices=choices))
        try:
            choice = input(f"{mode_name} >> ")
        except (KeyboardInterrupt, EOFError):
            print("\nBye!")
            break
        if validate_choice(choice=choice, choices=choices):
            try:
                print(
                    sort_result(
                        executor=executor, choices=choices, num=int(choice)
                    )
                )
            except (ValueError, KeyError) as exc:
                print(f"Error: {exc}")
            except (KeyboardInterrupt, EOFError):
                print("\nCanceled.")


if __name__ == "__main__":
    mode = check_mode()
    if mode.manager:
        manager_mode()
    elif mode.dispatcher:
        dispatcher_mode()
