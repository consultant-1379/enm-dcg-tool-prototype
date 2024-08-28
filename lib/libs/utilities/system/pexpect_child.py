import pexpect

from libs.logging.logger import Logger
from libs.logging.verbose import Verbose
from libs.variables.configuration import Configuration


class PexpectChild():

    def __init__(self, init_command):
        Verbose.white("pexpect.spawn(command) " + init_command)
        self.child = pexpect.spawn(init_command)

    def expect(self, pattern, timeout=-1):
        Verbose.white("expecting response: " + str(pattern))
        result = self.child.expect(pattern, timeout)
        Verbose.white("Index of the pattern matched: %d" % (result))
        return result

    def sendline(self, string, echo=True):
        if (echo == True):
            Verbose.white("sending the string: ")
            if string != Configuration.peer_server_root_password and string != Configuration.peer_server_password \
                    and string != Configuration.cli_password:
                Verbose.white("\t%s" % string)
            else:
                Verbose.white("\t################")
        return self.child.sendline(string)

    def close(self):
        return self.child.close()
    def before(self):
        return self.child.before
    def after(self):
        return self.child.after