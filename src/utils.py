"""Utils module"""
import datetime
import prettytable


def date_filter(seconds):
    """DATE FILTER FOR JINJA TEMPLATE"""
    return datetime.datetime.fromtimestamp(seconds).strftime("%Y-%m-%d  %H:%M")


def draw_choices(choices):
    """DRAW CHOICES FOR CLI"""
    return "\n{}\n".format("\n".join("{}\t- {}".format(num, row[0]) for num, row in enumerate(choices["data"])))


def draw_table(response):
    """DRAW TABLE OF RESULT CLI QUERY. USING PRETTY TABLE MODULE"""
    table = prettytable.PrettyTable(response["header"])
    for row in response["data"]:
        table.add_row(tuple(str(row[col]) for col in response["header"]))
    return table


# def draw_table(response):
#     """ALTERNATIVE DRAW TABLE"""
#     header = "|".join(("{:>16}".format(str(col)) for col in response["header"]))
#     body = "\n".join("|".join(("{:>16}".format(str(row[col])) for col in response["header"])) for row in response["data"])
#     return "\n{}\n".format("\n".join((header, body)))


def sort_result(executor, choices, num):
    """SORT RESULT"""
    additional_action = choices["data"][num][2]
    action = choices["data"][num][1]

    if not additional_action:
        response = draw_table(executor.__getattribute__(action))
    elif additional_action == "new_flight":
        new_flight(executor, action)
        response = "DONE!"
    else:
        if additional_action["show"]:
            print(draw_table(executor.__getattribute__(additional_action["show"])))
        arg = raw_input("{}:\n ?>> ".format(additional_action["description"]))
        if arg in "Nn":
            response = "CANCELED"
        else:
            executor.__getattribute__(action)(arg)
            response = "DONE!"
    return response


def new_flight(executor, method):
    passengers = raw_input("How many people do want to fly?\n?>> ")
    cargo = raw_input("How much cargo is needed to take?\n?>> ")
    executor.__getattribute__(method)(all_passengers=int(passengers), all_cargo=float(cargo))
