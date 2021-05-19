"""
his file illustrates the bad version of some_fun.
I've included the dependencies but the implementations
are dummied out.
""" 

class Logger:
    def log(self, msg):
        pass


logger = Logger()


def is_valid(x):
    pass


def some_fun(x):
    if is_valid(x):
        return x * 5
    else:
        logger.log("Invalid input to x")
