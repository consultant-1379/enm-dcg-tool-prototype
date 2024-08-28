
from libs.functions.jboss_debug.tools.vm_instance_controller import VMInstanceController
from libs.utilities.data_structures.dictionary import Dictionary
from libs.utilities.data_structures.type_check import TypeCheck
from libs.utilities.system.output import Output
from libs.utilities.system.print_text import Print
from libs.variables.configuration import Configuration
from libs.variables.keys import AppKeys


class JBossCommandController:

    def __init__(self, func, time, stamp):
        self.stamp = stamp
        self.tcpvm = (func[AppKeys.JBoss_servers])
        self.path = Dictionary.get_value(func, AppKeys.func_log_dir)
        self.time = time
        self.tcp = (func[AppKeys.jboss_commands])
        self.bool = Dictionary.get_value(self.tcp[0], AppKeys.run_command)
        self.cmd = Dictionary.get_value(self.tcp[1], AppKeys.command_options)
        # print trigger for startYAML
        self.print_trigger = True
        if Configuration.manual_startYamlFile is True:
            self.print_trigger = False
        func_instances = list()
        for each in self.tcpvm:
            instances = Dictionary.get_value(each, AppKeys.instances)
            if Configuration.Jboss_EOCM is True:
                if 'localhost' in instances:
                    self.vm = 'localhost'
            else:
                if type(instances) is str:
                    instances = [instances]
                TypeCheck.list(instances)
                func_instances += instances
                self.vm = func_instances
        if Configuration.tcptaring is False:
            if self.bool is True:
                Configuration.TCP_collection = True
                self.run_tcp_dump()
            else:
                return
        elif Configuration.tcptaring is True and self.bool is True:
            self.taring_up()

    def run_tcp_dump(self):
        Output.yellow('\nRunning the following commands specified in the JBOSS plugin',print_trigger=self.print_trigger)
        Print.white(self.cmd, trigger=self.print_trigger)
        if type(self.cmd) is list:
            commands = str(self.cmd).replace('[', '').replace(']', '').replace("'", '')
        else:
            commands = self.cmd
        if VMInstanceController.run_jboss_commands(self.time, commands, self.path, self.vm, self.stamp) is True:
            return
        else:
            Output.red('commands were not run during Jboss enable', print_trigger=self.print_trigger)
            return

    def taring_up(self):
        VMInstanceController.jboss_command_file(self.path, self.vm, self.cmd)
        Configuration.taring = False
