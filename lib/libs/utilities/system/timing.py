import time

from libs.logging.verbose import Verbose
from datetime import timedelta


class Timing():
    def __init__(self, seconds=0, minutes=0, hours=0, days=0):
        delta = timedelta(days=days, seconds=seconds, minutes=minutes, hours=hours)
        self.seconds = delta.seconds
        self.minutes = self.seconds / 60
        self.hours = self.minutes / 60
        self.days = delta.days

    @staticmethod
    def debug_info(message):
        """
        Do not call this method outside of this class
        :param message:
        :return:
        """
        Verbose.white(message)

    @staticmethod
    def sleep(seconds):
        """
        Pause the program for a specific time
        :param seconds: sleeping time
        :return:
        """
        if (seconds > 5):
            Timing.debug_info("Sleeping for %s" % seconds)
        return time.sleep(seconds)

    @staticmethod
    def strftime():
        """

        :return: Current time in  "%Y%m%d-%H%M%S" format
        """
        time.sleep(1)
        return time.strftime("%Y%m%d-%H%M%S")

    @staticmethod
    def time():
        """

        :return: Current time in seconds
        """
        return time.time()

    @staticmethod
    def short_date():
        """

        :return: Current time in  "%d%m%y" format
        """
        return time.strftime('%d%m%y')
