import pexpect

from libs.variables.configuration import Configuration


class CommandController():
    def run(self):
        try:
            self.child.sendline('bash %s >> %s' % (self.command_script, self.output_file) + " 2>&1 ")
            # wait until the command is finished
            self.child.expect(['root.*#'], timeout=Configuration.peer_server_command_timeout)
            self.child.sendline("echo $?")
            self.child.expect(['root.*#'])
            exitcode = self.child.before().splitlines()[1]
            return exitcode.strip()
        except pexpect.TIMEOUT:
            return False

    def __init__(self, child, command_script, output_file, peer_server):
        self.child = child
        self.command_script = command_script
        self.output_file = output_file
        self.peer_server = peer_server