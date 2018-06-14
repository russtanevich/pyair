"""Utils module"""
import datetime


def date_filter(seconds):
    return datetime.datetime.fromtimestamp(seconds).strftime("%Y-%m-%d  %I:%M")


