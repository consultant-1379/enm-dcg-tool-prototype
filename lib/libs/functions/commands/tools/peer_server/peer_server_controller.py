import os

from libs.logging.logger import Logger
from libs.logging.verbose import Verbose
from libs.utilities.system.pexpect_child import PexpectChild
from libs.utilities.system.terminal import Terminal
from libs.variables.configuration import Configuration


class PeerServerController():

    @staticmethod
    def ping_server(server):
        """
        :param server:
        :return:
        """
        reply = Terminal.system("ping -c 1 " + server + " > /dev/null 2>&1")
        if reply == 0:
            return True
        else:
            return False

    @staticmethod
    def scp_file(username, root_password, peer_server, path_of_file, path_of_destination):
        import pexpect
        cmd = 'scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null > /dev/null 2>&1 '+path_of_file+'' \
              ' '+username+'@'+peer_server+':'+path_of_destination
        child = PexpectChild(cmd)
        name_of_file = (os.path.basename(path_of_file))
        expected = ".*%s@%s's password:.*" % (username, peer_server)
        question = "yes/no.*"
        exception = "ssh: Could not resolve hostname.*"
        result = child.expect([expected, question, exception, name_of_file])
        if result == 0:
            child.sendline(root_password)
            check = child.expect([name_of_file,pexpect.TIMEOUT],5)
            if check == 1:
                Verbose.red("Peer Server Password and/or Username incorrect for File SCP")
        elif result == 1:
            child.sendline("yes")
        child.close()

    @staticmethod
    def connect_peer_server(username, peer_server):
        child = PexpectChild('ssh %s@%s' % (username, peer_server))

        expected = ".*%s@%s's password:.*" % (username, peer_server)
        expected2 = ".*%s@.*" % (username)
        question = "yes/no.*"
        exception = "ssh: Could not resolve hostname.*"
        result = child.expect([expected, question, exception, expected2])
        if (result == 0):
            # connection was successful
            Verbose.green("Connected to the peer server %s." % (peer_server))
            return child
        elif (result == 1):
            # first time connection
            child.sendline("yes")
            return child
        elif (result == 3):
            # connection was successful
            Verbose.green("Connected to the peer server %s." % (peer_server))
            return child
        else:
            return None

    @staticmethod
    def login_peer_server(password, child):
        import pexpect
        try:
            child.sendline(password, False)
            expected = "Last login:"
            expected2 = ".*litp-admin@.*"
            exception = "Permission denied"
            result = child.expect([expected, exception, expected2])
            if result == 0 or result == 2:
                # logged in the peer server successfully
                Verbose.green("Logged in the peer server")
                return True
            else:
                return False
        except pexpect.EOF and pexpect.TIMEOUT:
            return False

    @staticmethod
    def cli_pexpect_run(string_to_execute, output_path):
        finish = False
        made_time = os.path.getmtime(output_path)
        child = PexpectChild("ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null %s@%s \"%s\"" % (
            Configuration.executing_username, Configuration.cli_correct_vm, string_to_execute))
        child.expect("%s@%s's password:" % (Configuration.executing_username, Configuration.cli_correct_vm),
                     timeout=5)
        child.sendline(Configuration.executing_password)
        expected = "Last login:.*"
        expected2 = ".*"
        exception = "root@.*"
        result = child.expect([expected, exception, expected2], timeout=5)
        if result == 0:
            # infinite loop until the output file gets written to
            while finish is False:
                check_time = os.path.getmtime(output_path)
                if made_time != check_time:
                    finish = True
                    break
            Logger.info("ENM CLI commands Successful")
        elif result == 1:
            Logger.warning("Issue encountered connecting to scripting vm to execute cli commands")
        elif result == 2:
            # infinite loop until the output file gets written to
            while finish is False:
                check_time = os.path.getmtime(output_path)
                if made_time != check_time:
                    finish = True
                    break
            Logger.info("ENM CLI commands Successful 2")
        child.close()

    @staticmethod
    def use_root(password, child):
        import pexpect
        try:
            child.sendline('su -')
            child.expect("Password:")
            child.sendline(password, False)

            expected = "root.*"
            exception = "su: incorrect password"
            result = child.expect([expected, exception])
            if (result == 0):
                # using Root
                Verbose.green("Using root to execute the following commands")
                return True
            else:
                return False
        except pexpect.EOF and pexpect.TIMEOUT:
            return False
