import os
from libs.utilities.system.print_text import Print
from libs.variables.configuration import Configuration


class CheckRoot:

    def __init__(self):
        if Configuration.EOCM is not True:
            # check if user has root access
            if not self.check_root():
                Print.red("Must have root access or be run with sudo")
                os._exit(1)

    def check_root(self):
        if os.getuid() != 0:
            return False
        else:
            return True
