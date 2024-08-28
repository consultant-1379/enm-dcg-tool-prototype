import os
import getpass
from libs.utilities.system.print_text import Print
from libs.variables.configuration import Configuration


class CheckUserEocm:

    def __init__(self):
        if Configuration.EOCM is True:
            # check if user has root access
            if not self.check_user():
                Print.red("Must run the tool as %s user" % Configuration.username)
                os._exit(1)

    def check_user(self):
        username = getpass.getuser()
        if str(username) == str(Configuration.username):
            return True
        else:
            return False

    @staticmethod
    def user():
        return getpass.getuser()

    @staticmethod
    def group_id():
        return os.getegid()