from libs.functions.commands.tools.peer_server.peer_server_controller import PeerServerController
from libs.utilities.system.output import Output
from libs.utilities.system.terminal import Terminal


class PeerServer():
    def __init__(self, peer_server, username, login_password, root_password):

        self._peer_server = peer_server
        self._username = username
        self._login_password = login_password
        self._root_password = root_password
        self._child = None

    def get_name(self):
        return self._peer_server

    def connect(self):
        """
        :return: True if connect is successful. Otherwise, False
        """

        if PeerServerController.ping_server(self._peer_server) is False:
            return False
        self._child = PeerServerController.connect_peer_server(self._username, self._peer_server)

        if (self._child == None):
            return False

        if not PeerServerController.login_peer_server(self._login_password, self._child):
            Output.red("Incorrect password(s) to connect to the peer server [%s]" % (self._peer_server))
            return False

        if not PeerServerController.use_root(self._root_password, self._child):
            Output.red("Incorrect root password")
            return False

        return True

    def execute(self, command):
        if (self._child == None):
            Terminal.exception("The connection should be established before executing commands on a peer server")
        self._child.sendline(command)

        # wait until the command is finished
        self._child.expect('root.*#')

    def execute_and_return(self, command):
        if (self._child == None):
            Terminal.exception("The connection should be established before executing commands on a peer server")
        self._child.sendline(command)

        # wait until the command is finished
        self._child.expect('root.*#')
        return self._child.before()

    def cp(self, source, destination):
        """
        copy a file or directory from source to destination
        :param source:
        :param destination:
        :return:
        """
        import os
        filename = os.path.basename(source).strip()
        self.execute('/bin/cp -a -p --force %s %s' % (source, destination))
        out_file_dir = destination+"/"+filename
        if str(out_file_dir).endswith(".gz") is False:
            Terminal.system("gzip %s --force" % out_file_dir)
        # Terminal.cp(source, destination)

    def close(self):
        if (self._child == None):
            return
        # close the child
        self._child.close()
