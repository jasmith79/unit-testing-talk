"""Contains the well-written example"""


# This file represents the better version of some_fun
import math

from functools import partial


class Logger:
    def log(self, msg):
        pass


logger = Logger()


def is_valid(n):
    return isinstance(n, (int, float)) and n > 0 and n != math.inf


def times_five(n):
    return n * 5


def not_quite_some_fun(logger, validator, xform, n):
    if validator(n):
        return xform(n)
    else:
        logger.log("Invalid input")


some_fun = partial(not_quite_some_fun, logger, is_valid, times_five)
