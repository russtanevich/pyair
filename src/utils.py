"""Utils module"""
import datetime
import prettytable


def date_filter(seconds):
    """DATE FILTER FOR JINJA TEMPLATE"""
    if seconds is None:
        return ""
    return datetime.datetime.fromtimestamp(float(seconds)).strftime(
        "%Y-%m-%d  %H:%M"
    )


def draw_choices(choices):
    """DRAW CHOICES FOR CLI"""
    lines = "\n".join(
        f"{num}\t- {row[0]}" for num, row in enumerate(choices["data"])
    )
    return f"\n{lines}\n"


def draw_table(response):
    """DRAW TABLE OF RESULT CLI QUERY. USING PRETTY TABLE MODULE"""
    header = list(response["header"])
    if not header:
        return ""
    table = prettytable.PrettyTable(header)
    for row in response["data"]:
        table.add_row([str(row[col]) for col in header])
    return table


def sort_result(executor, choices, num):
    """SORT RESULT"""
    additional_action = choices["data"][num][2]
    action = choices["data"][num][1]

    if not additional_action:
        response = draw_table(getattr(executor, action))
    elif additional_action == "new_flight":
        new_flight(executor, action)
        response = "DONE!"
    else:
        if additional_action["show"]:
            print(draw_table(getattr(executor, additional_action["show"])))
        arg = input(f"{additional_action['description']}:\n ?>> ")
        if arg.strip().lower() == "n":
            response = "CANCELED"
        else:
            getattr(executor, action)(arg)
            response = "DONE!"
    return response


def new_flight(executor, method):
    """Prompt for flight parameters and execute flight."""
    passengers = input("How many people do want to fly?\n?>> ")
    cargo = input("How much cargo is needed to take?\n?>> ")
    getattr(executor, method)(
        all_passengers=int(passengers), all_cargo=float(cargo)
    )
