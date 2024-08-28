import select
import sys
import time
from time import time

from libs.utilities.system.output import Output
from libs.utilities.system.print_text import Print
from libs.utilities.system.timing import Timing
from libs.variables.configuration import Configuration


class WaitTime():
    def __init__(self, time, message):

        if Configuration.debug_time != None:
            # if the user passes the timeout argument in the command line
            self.time = Configuration.debug_time
        else:
            # use the debug time stated in the YAML file
            self.time = time
        self.message = message

        self.log_dir = Configuration.storing_logs_dir
        # print trigger for startYAML
        self.print_trigger = True
        if Configuration.manual_startYamlFile is True:
            self.print_trigger = False

    def run(self):
        # if the time is equal to 0, skip the function
        if (self.time != 0):
            self._sleep()

            # if the user asks for extend debug time
            # if (self._extend()):
            #     # double the debug time
            #     self._sleep()

    def _sleep(self):
        """
        Set time and wait for reproducing issues in remote virtual machines
        :return:
        """

        start_time = time()
        end_time = start_time + self.time
        while True:
            Timing.sleep(0.1)
            now = time()

            percents = (now - start_time) / (self.time)

            time_left = self.time * (1 - percents)
            seconds = int(time_left % 60)
            minutes = int((time_left - seconds) / 60)
            text = '%s, time left ' % (self.message)

            # Display minutes
            if (minutes > 0):
                if (minutes == 1):
                    text += "%s minute and " % (minutes)
                else:
                    text += "%s minutes and " % (minutes)

            # Display seconds
            if (seconds == 1):
                text += '%s second.' % (seconds)
            else:
                text += '%s seconds.' % (seconds)

            Print.clean_line()
            Print.white(text, new_line=False, trigger=self.print_trigger)

            if (now >= end_time):
                Print.clean_line()
                break

        Print.white()

    def _extend(self):
        total_time = 60
        yes = ["Yes"]
        no = ["No"]

        start_time = time()
        end_time = start_time + total_time

        while True:
            now = time()
            if (now > end_time):
                return False

            percents = (now - start_time) / (total_time)

            time_left = total_time * (1 - percents)
            seconds = int(time_left)
            text = 'Do you want more time to reproduce the issue? Answer [Yes] or [No] in %s seconds: ' % (seconds)
            Print.clean_line()
            Print.yellow(text, new_line=False)

            i, o, e = select.select([sys.stdin], [], [], 60)
            if (i):
                answer = sys.stdin.readline().strip()
                if (answer in yes):
                    return True
                elif (answer in no):
                    Output.green('Issue reproduction finished',print_trigger=self.print_trigger)
                    return False
                else:
                    Output.red("Invalid response: '%s'" % (answer),print_trigger=self.print_trigger)
