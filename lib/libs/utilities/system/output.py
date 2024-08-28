from libs.logging.logger import Logger
from libs.utilities.system.print_text import Print


class Output(object):
    """
    The methods in this class log the message to the program log file,
    and print the message to the terminal
    """

    @staticmethod
    def red(text="", new_line=True, setup=False, trigger=True, print_trigger=True):
        """
        Logs to file in black and prints to Terminal in red
        :param text: String variable to log/print (default = "")
        :param new_line: if true will add /n to end of line
        :param setup: this is an Object of type logger if included which describes which log file to use
        :return:
        """
        if setup is False:
            Logger.error(text, trigger=trigger)
            Print.red(text, new_line, trigger=print_trigger)
        else:
            Logger.error(text, setup=setup, trigger=trigger)
            Print.red(text, new_line, trigger=print_trigger)

    @staticmethod
    def white(text="", new_line=True, setup=False, trigger=True, print_trigger=True):
        if setup is False:
            Logger.info(text, trigger=trigger)
            Print.white(text, new_line, trigger=print_trigger)
        else:
            Logger.info(text, setup=setup, trigger=trigger)
            Print.white(text, new_line, trigger=print_trigger)

    @staticmethod
    def green(text="", new_line=True, setup=False, trigger=True, print_trigger=True):
        if setup is False:
            Logger.info(text, trigger=trigger)
            Print.green(text, new_line, trigger=print_trigger)
        else:
            Logger.info(text, setup=setup, trigger=trigger)
            Print.green(text, new_line, trigger=print_trigger)

    @staticmethod
    def yellow(text="", new_line=True, setup=False, trigger=True, print_trigger=True):
        if setup is False:
            Logger.info(text, trigger=trigger)
            Print.yellow(text, new_line, trigger=print_trigger)
        else:
            Logger.info(text, setup=setup, trigger=trigger)
            Print.yellow(text, new_line, trigger=print_trigger)

    @staticmethod
    def blue(text="", new_line=True, setup=False, trigger=True, print_trigger=True):
        if setup is False:
            Logger.info(text, trigger=trigger)
            Print.blue(text, new_line, trigger=print_trigger)
        else:
            Logger.info(text, setup=setup, trigger=trigger)
            Print.blue(text, new_line, trigger=print_trigger)
