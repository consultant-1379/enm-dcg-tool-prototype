import subprocess

from libs.logging.verbose import Verbose
from libs.utilities.data_structures.dictionary import Dictionary
from libs.utilities.system.file_paths import FilePaths
from libs.utilities.system.output import Output
from libs.utilities.system.print_text import Print
from libs.utilities.system.terminal import Terminal
from libs.utilities.system.timing import Timing
from libs.variables.configuration import Configuration
from libs.variables.keys import AppKeys


class VMInstanceController():

    def __init__(self, vm_instance, function):
        self.instance_name = Dictionary.get_value(vm_instance, AppKeys.instance)

        self.log_dir = FilePaths.join_path(Dictionary.get_value(function, AppKeys.func_log_dir), self.instance_name)

        self.commands = Dictionary.get_value(vm_instance, AppKeys.commands)

        self.sudo = Dictionary.get_value(vm_instance, AppKeys.sudo, True, type=bool)
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
            scp_command = "scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i > /dev/null 2>&1" + Configuration.vm_private_key + " " + self.exec_script_path + " " + \
                          Configuration.vm_user_name + "@" + self.instance_name + ":/var/tmp/ >> /dev/null"
            self.add_run_script_command()
            Terminal.system(scp_command)
        result = Terminal.system('ping -c 1 %s >/dev/null'%self.instance_name)
        if result == 0:
            if FilePaths.isdir(self.log_dir) is False:
                Terminal.mkdir(self.log_dir, True)
            for command in self.commands:
                basename = str(Terminal.popen_read("basename $(echo \"%s\" | awk '{print $1}')" % command)).strip()
                output_file_path = (self.log_dir + "/" + basename + "_output_" + Timing.strftime() + ".txt")
                Terminal.system('sudo touch ' + output_file_path)

                Terminal.system('touch %s' % output_file_path)
                Terminal.system('echo "Hostname: %s\nDatetime: %s\nCommand executed: %s\nOutput of command:" >> %s'%( self.instance_name,Timing().strftime(),command,output_file_path))
                Terminal.system('echo "##########################################################\n" >> %s' % output_file_path)
                example = ('sudo ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i  %s %s@%s  " sudo time %s" >> %s 2>/dev/null 2>&1' % (Configuration.vm_private_key,Configuration.vm_user_name,self.instance_name,command,output_file_path))
                pipe = subprocess.Popen(example, shell=True, stdout=subprocess.PIPE)
                streamdata = pipe.communicate()[0]
                pipe.stdout.close()
                cmd = pipe.returncode
                Terminal.system('echo "##########################################################\n" >> %s' % output_file_path)
                if cmd == 0:
                    Terminal.system('echo "#Command finished [SUCCESS:%s]\n" >> %s' % (cmd, output_file_path))
                elif cmd == 124:
                    Terminal.system('echo "#Command finished [TIMEOUT:%s]\n" >> %s' % (cmd, output_file_path))
                    Output.red("The following command [%s] timed out. exit code = [%s]" % (command, cmd), print_trigger=self.print_trigger)
                else:
                    Terminal.system('echo "#Command finished [FAILED:%s]\n" >> %s' % (cmd, output_file_path))
                    Print.red("The following command [%s]. failed execution on vm [%s]" % (command, self.instance_name),trigger=self.print_trigger)
                Verbose.green('The command output file %s has been generated.' % output_file_path)
        else:
            Output.red("Could not connect to the vm %s." % self.instance_name, print_trigger=self.print_trigger)


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
            bash_script_command ="chmod 755 %s;%s;rm -f %s" % (str(path_of_file),str(path_of_file),str(path_of_file))
        else:
            bash_script_command ="chmod 755 %s;%s %s;rm -f %s" % (str(path_of_file),str(path_of_file),str_of_arguments,str(path_of_file))
        self.commands = self.commands + [bash_script_command]