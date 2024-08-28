from libs.utilities.data_structures.dictionary import Dictionary
from libs.utilities.system.file_paths import FilePaths
from libs.utilities.system.output import Output
from libs.utilities.system.terminal import Terminal
from libs.variables.configuration import Configuration
from libs.variables.keys import AppKeys


class VMInstanceController():
    def __init__(self, server, timeout, function):
        # self.script = script
        self.timeout = timeout
        self.vm_instance = Dictionary.get_value(server, AppKeys.instance)
        self.log_dir = Dictionary.get_value(function, AppKeys.func_log_dir)
        self.log_dir = FilePaths.join_path(self.log_dir, self.vm_instance)
        # print trigger for startYAML
        self.print_trigger = True
        if Configuration.manual_startYamlFile is True:
            self.print_trigger = False

    def run(self):
        result = Terminal.system('ping -c 1 %s >/dev/null' % self.vm_instance)
        if result == 0:
            Terminal.mkdir(self.log_dir, superuser=True)
        else:
            Output.red("%s not accessible"%self.vm_instance,print_trigger=self.print_trigger)


    def bash(self,vm,script, output, timeout=None,*args):
        command = "bash %s" % (script)
        command = " ".join([command] + list(args))
        if (timeout != None):
            command = ("timeout %d " % timeout) + command

        # direct the output and error messages to the output file
        command += " &>> %s" % output

        # run the command in another process
        command += " &"
        Terminal.system('ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i %s %s@%s 2>/dev/null "%s" > /dev/null 2>&1' %(Configuration.vm_private_key,Configuration.vm_user_name,vm,command))