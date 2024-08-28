from libs.utilities.system.print_text import Print
from libs.variables.configuration import Configuration


class Verbose():

    @staticmethod
    def white(message, new_line=True):
        if (Configuration.verbose):
            Print.white(message, new_line)

    @staticmethod
    def red(message, new_line=True):
        if (Configuration.verbose):
            Print.red(message, new_line)

    @staticmethod
    def green(message, new_line=True):
        if (Configuration.verbose):
            Print.green(message, new_line)

    @staticmethod
    def yellow(message, new_line=True):
        if (Configuration.verbose):
            Print.yellow(message, new_line)
