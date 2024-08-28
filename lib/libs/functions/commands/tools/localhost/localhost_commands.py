import socket
import subprocess

from libs.functions.commands.tools.commands_superclass import CommandsSuperclass
from libs.logging.verbose import Verbose
from libs.utilities.data_structures.dictionary import Dictionary
from libs.utilities.system.file_paths import FilePaths
from libs.utilities.system.output import Output
from libs.utilities.system.terminal import Terminal
from libs.utilities.system.timing import Timing
from libs.variables.configuration import Configuration
from libs.variables.keys import AppKeys
import time


class LocalhostCommands(CommandsSuperclass):
    def __init__(self, function):
        if Dictionary.get_value(function, AppKeys.server_type) != LocalhostCommands.server_type():
            Terminal.exception('In the "Commands" function, the server type is %s, while %s is expected' % (
                Dictionary.get_value(function, AppKeys.server_type), LocalhostCommands.server_type()))
        if Configuration.EOCM is True:
            self.log_dir = FilePaths.join_path(Dictionary.get_value(function, AppKeys.func_log_dir),
                                               socket.gethostname())
        else:
            if Configuration.EOCM is True:
                self.log_dir = FilePaths.join_path(Dictionary.get_value(function, AppKeys.func_log_dir),
                                                   socket.gethostname())
            else:
                self.log_dir = FilePaths.join_path(Dictionary.get_value(function, AppKeys.func_log_dir),
                                                   LocalhostCommands.server_type())

        self.commands = Dictionary.get_value(function, AppKeys.commands)

        self.sudo = Dictionary.get_value(function, AppKeys.sudo, True, type=bool)
        self.exec_script_path = None

        # print trigger for startYAML
        self.print_trigger = True
        if Configuration.manual_startYamlFile is True or Configuration.manual_endYamlFile is True:
            self.print_trigger = False

    @staticmethod
    def server_type():
        return 'localhost'

    def run(self):
        if FilePaths.isdir(self.log_dir) is False:
            Terminal.mkdir(self.log_dir, True)
            if Configuration.EOCM is True:
                Output.yellow('Executing the following commands on %s' % socket.gethostname(),
                              print_trigger=self.print_trigger)
                Output.white(self.commands, print_trigger=self.print_trigger)
            else:
                Output.yellow('Executing the following commands on %s' % self.server_type(),
                              print_trigger=self.print_trigger)
                Output.white(self.commands, print_trigger=self.print_trigger)
        for each in self.commands:
            basename = str(Terminal.popen_read("basename $(echo \"%s\" | awk '{print $1}')" % each)).strip()
            output_file_path = (self.log_dir + "/" + basename + "_output_" + Timing.strftime() + ".txt")
            with open(output_file_path, 'w') as f:
                f.write("#Hostname: %s\n" % (Terminal.hostname()))
                f.write("#Datetime: %s\n" % (Timing.strftime()))
                f.write("#Command executed: %s\n" % each)
                # Execute the command and the output
                f.write('#Output of command:\n')
                f.write("##########################################################\n")
                f.close()
                start = time.time()
                cmd = (each+" >> %s 2>&1" % output_file_path)
                pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
                streamdata = pipe.communicate()[0]
                pipe.stdout.close()
                output = pipe.returncode
                end = time.time()
                time_lapse = (end - start)
                Terminal.system('echo "#Execution Time: %s\n" >> %s' % (time_lapse, output_file_path))
                Terminal.system('echo "##########################################################\n" >> %s'
                                % output_file_path)
                if output == 0:
                    Terminal.system('echo "#Command finished [SUCCESS:%s]\n" >> %s' % (output, output_file_path))
                elif output == 124:
                    Output.red("The following command [%s] timed out. exit code = [%s]"
                               % (each, output), print_trigger=self.print_trigger)
                    Terminal.system('echo "#Command finished [TIMEOUT:%s]\n" >> %s' % (output, output_file_path))
                else:
                    Terminal.system('echo "#Command finished [FAILED:%s]\n" >> %s' % (output, output_file_path))
                    if Configuration.EOCM is True:
                        Output.red("The following command [%s]. failed execution on %s" % (each, socket.gethostname()),
                                   print_trigger=self.print_trigger)
                    else:
                        Output.red("The following command [%s]. failed execution on localhost"
                                   % each, print_trigger=self.print_trigger)
            Verbose.green('The command output file %s has been generated.' % output_file_path)
