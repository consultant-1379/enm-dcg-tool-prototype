from libs.functions.commands.tools.peer_server.peer_server_controller import PeerServerController
from libs.functions.enm_cli.enm_cli_checks import ENMCliChecks
from libs.functions.enm_cli.tools.enm_cli_commands_superclass import EnmCliCommandsSuperclass
from libs.functions.function_superclass import FunctionSuperclass
from libs.logging.logger import Logger
from libs.utilities.data_structures.dictionary import Dictionary
from libs.utilities.system.file_paths import FilePaths
from libs.utilities.system.output import Output
from libs.utilities.system.pexpect_child import PexpectChild
from libs.utilities.system.print_text import Print
from libs.utilities.system.terminal import Terminal
from libs.utilities.system.timing import Timing
from libs.variables.configuration import Configuration
from libs.variables.keys import AppKeys
import os


class EnmCliCommands(EnmCliCommandsSuperclass):

    @staticmethod
    def func_name():
        return "ENMCLI"

    def __init__(self, function, app, config_stack, network=False):
        if (not FunctionSuperclass.check_name_equal(function[AppKeys.func_name], EnmCliCommands.func_name())):
            Terminal.exception("This function was wrongly passed in Enm Cli Commands")
        self.app = app
        self.network = network
        self.config_stack = config_stack
        self.function = function
        self.list_of_commands = Dictionary.get_value(function,AppKeys.enm_commands)
        self.check_status = None
        self.timeout = None
        # print trigger for startYAML
        self.print_trigger = True
        if Configuration.manual_startYamlFile is True:
            self.print_trigger = False
        # check for timeout in yaml file
        if AppKeys.check_status in function:
            if type(Dictionary.get_value(function, AppKeys.check_status)) is str:
                self.check_status = Dictionary.get_value(function, AppKeys.check_status)
            elif type(Dictionary.get_value(function, AppKeys.check_status)) is list:
                self.check_status = Dictionary.get_value(function, AppKeys.check_status)[0]
        # check for status in yaml file
        if AppKeys.timeout in function:
            self.timeout = int(Dictionary.get_value(function, AppKeys.timeout))

        if type(self.list_of_commands) is str:
            self.list_of_commands = [self.list_of_commands]

        self.log_dir = Dictionary.get_value(function, AppKeys.func_log_dir)
        self.time_stamp = Timing.strftime()

    def run(self):
        Configuration.plugin_count = int(Configuration.plugin_count) + 1
        checks = ENMCliChecks(self.function)
        checks.full_check()
        checks.full_check(2)
        if Configuration.enm_cli_check is False:
            if self.network is False:
                Output.red("Skipping cli plugin\n", print_trigger=self.print_trigger)
            pass
        elif Configuration.enm_cli_check is True:
            Terminal.chmod(644, FilePaths.join_path(os.path.dirname(os.path.realpath(__file__)), "tools/enm_cli_script.py"))
            if self.network is False:
                Output.green("Executing ENM commands on: [%s]\n" % Configuration.cli_correct_vm, print_trigger=self.print_trigger)
            # step 1 cp script over to shared directory
            Terminal.copy(FilePaths.join_path(os.path.dirname(os.path.realpath(__file__)), "tools/enm_cli_script.py"),
                          Configuration.directory_to_check_disk_usage)
            # path of output text file
            output_path = os.path.join(self.log_dir, "enm_cli_output_%s.txt" % self.time_stamp)
            if self.app is None and self.config_stack is None:
                Configuration.JID_path = output_path
            # generating command to execute with ssh as string
            string_to_execute = ""
            string_to_execute += "python '/ericsson/enm/dumps/enm_cli_script.py'"
            new_list_of_commands = list()
            # adding enm commands as arguments to string
            string_to_execute += (" '%s' '%s' '%s' '%s' '%s' " % (Configuration.executing_username,
            Configuration.executing_role, str(self.check_status), str(self.timeout), str(Configuration.JID_present)))
            for each in self.list_of_commands:
                new_string = " '" + each + "'"
                string_to_execute += new_string
                new_list_of_commands.append(new_string)
            string_to_execute += " >> " + output_path + " 2>&1"
            # creating text output file and giving permissions for alteration before collection
            Terminal.mkdir(self.log_dir)
            Terminal.touch(output_path)
            Terminal.chmod(777, output_path)
            # connecting to client scripting vm and executing command previously created on script
            import pexpect
            try:
                PeerServerController().cli_pexpect_run(string_to_execute, output_path)
            except pexpect.EOF and pexpect.TIMEOUT:
                Print.red("Error Occured with ENM CLI commands execution", trigger=self.print_trigger)
                Configuration.enm_cli_check = False
            Configuration.enm_cli_check = False
            if self.network is True:
                Terminal.copy(output_path, Configuration.network_element_output)



