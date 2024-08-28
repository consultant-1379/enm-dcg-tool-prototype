from libs.functions.commands.tools.peer_server.peer_server_controller import PeerServerController
from libs.functions.commands.tools.peer_server.command_controller import CommandController
from libs.utilities.data_structures.dictionary import Dictionary
from libs.utilities.system.file_paths import FilePaths
from libs.utilities.system.output import Output
from libs.utilities.system.terminal import Terminal
from libs.utilities.system.timing import Timing
from libs.variables.configuration import Configuration
from libs.variables.keys import AppKeys


class LoginPeerServer():
    def __init__(self, function, username, login_password, root_password):
        self.commands = Dictionary.get_value(function, AppKeys.commands)

        # set up variables
        self.peer_server = Dictionary.get_value(function, AppKeys.instance)
        self.username = username
        self.login_password = login_password
        self.root_password = root_password
        self.log_dir = Dictionary.get_value(function, AppKeys.func_log_dir)
        self.exec_script_path = None
        self.argument_list = None
        self.user = None

        # print trigger for startYAML
        self.print_trigger = True
        if Configuration.manual_startYamlFile is True:
            self.print_trigger = False

        if "cp_exec_command" in function:
            self.exec_script_path = Dictionary.get_value(function, "cp_exec_command")
        if "argument_list" in function:
            self.argument_list = Dictionary.get_value(function, "argument_list")
        if "user" in function:
            self.user = Dictionary.get_value(function, "user")

    def run(self):
        # scp script if exists in yaml file
        if self.exec_script_path is None:
            pass
        else:
            self.add_run_script_command()
            PeerServerController.scp_file(self.username, self.root_password, self.peer_server,
                                          self.exec_script_path, "/var/tmp/")
        # execute the commands
        script_dir = FilePaths.join_path(self.log_dir, self.peer_server)
        for command in self.commands:
            # Log in the peer_server with root user
            child = self.login()

            if child is None:
                Output.red("Cannot execute commands in the peer_server. See the previous output.",print_trigger=self.print_trigger)
                return False

            if FilePaths.isdir(script_dir) is False:
                Terminal.mkdir(script_dir)

            basename = str(Terminal.popen_read("basename $(echo \"%s\" | awk '{print $1}')" % command)).strip()
            script_path = (script_dir + "/" + basename + "_output_" + Timing.strftime() + ".txt")
            Terminal.system('sudo touch ' + script_path)

            command_script = "%s/peer_server_command_%s" % (Configuration.storing_logs_dir + ".LCSMetadata",
                                                            str(Timing.strftime()))
            Terminal.touch(command_script)

            commands = 'time ' + command
            command_controller = CommandController(child, command_script, script_path, self.peer_server)

            file = open(command_script, "w")
            file.write("echo \"#Peer_server: %s\"\n" % self.peer_server)
            file.write("echo \"#Datetime: $(date)\"\n")
            file.write("echo \"#Command executed: %s\"\n" % commands)
            file.write("echo \"#Output of command:\"\n")
            file.write("echo \"#####################################\"\n")
            file.write("%s\n" % commands)
            file.write('''ret=$?\n''')
            file.write("echo \"#####################################\"\n")
            file.write("if [[ ${ret} -eq 0 ]]; then\n")
            file.write("echo \"#Command finished [SUCCESS:${ret}]\"\n")
            file.write("elif [[ ${ret} -eq 124 ]]; then\n")
            file.write("echo \"#Command finished [TIMEOUT:${ret}]\"\n")
            file.write("else\n")
            file.write("echo \"#Command finished [FAILED:${ret}]\"\n")
            file.write("fi\n")
            file.write("/bin/rm \"$0\"\n")
            file.write("exit ${ret}\n")
            file.close()
            execution = command_controller.run()
            execution = str(execution).strip()
            if execution == "False":
                Output.red("Unexpected issue occurred, Host not responding with command [%s]." % command,print_trigger=self.print_trigger)
            elif execution == "124":
                Output.red("The following command [%s] timed out. exit code = [%s]" % (command, execution),print_trigger=self.print_trigger)
            elif execution != "0":
                Output.red("The following command [%s]. failed execution on Peer Server [%s]" % (command, self.peer_server),print_trigger=self.print_trigger)
            # logout the peer_server
            child.close()

    def login(self):
        """
        :return: child of pexpect if connect is successful. Otherwise, None
        """
        if PeerServerController.ping_server(self.peer_server) is False:
            return None
        else:
            child = PeerServerController.connect_peer_server(self.username, self.peer_server)

            if not PeerServerController.login_peer_server(self.login_password, child):
                Output.red("Incorrect password(s) to connect to the peer server [%s]" % (self.peer_server), print_trigger=self.print_trigger)
                return None

            if not PeerServerController.use_root(self.root_password, child):
                Output.red("Incorrect root password", print_trigger=self.print_trigger)
                return None

            return child

    def add_run_script_command(self):
        import os
        path_of_file = "/var/tmp/" + os.path.basename(self.exec_script_path)
        if type(self.argument_list) is list:
            str_of_arguments = ""
            if len(self.argument_list) == 0:
                pass
            else:
                for each in self.argument_list:
                    str_of_arguments += "\"" + str(each) + "\" "
        else:
            str_of_arguments = self.argument_list
        if str_of_arguments is None or str_of_arguments is "":
            bash_script_command ="chmod 755 %s;%s;rm -f %s" % (str(path_of_file), str(path_of_file), str(path_of_file))
        else:
            bash_script_command ="chmod 755 %s;%s %s;rm -f %s" % (str(path_of_file), str(path_of_file), str_of_arguments, str(path_of_file))
        self.commands = self.commands + [bash_script_command]

