import os
import time

from libs.functions.function_superclass import FunctionSuperclass
from libs.functions.jboss_debug.tools.vm_instance_controller import VMInstanceController
from libs.functions.jboss_debug.tools.vms_jboss_debug_controller import VMsJBossDebugController
from libs.utilities.data_structures.dictionary import Dictionary
from libs.utilities.system.output import Output
from libs.utilities.system.terminal import Terminal
from libs.variables.configuration import Configuration
from libs.variables.keys import AppKeys


class EnableDebug(FunctionSuperclass):
    """description of class"""

    @staticmethod
    def func_name():
        return "Enable Debug"

    def __init__(self, function, app, config_stack):
        if (not FunctionSuperclass.check_name_equal(function[AppKeys.func_name], EnableDebug.func_name())):
            Terminal.exception(
                "This function was wrongly passed in CollateAttachFiles")  # todo fix the bug   a wrong string
        self.function = function
        if Configuration.Jboss_EOCM is True:
            Output.yellow('Enabling JBOSS debugging loggers, please wait...')
            Jboss_servers = Dictionary.get_value(self.function, AppKeys.JBoss_servers)
            instance = Dictionary.get_value(Jboss_servers[0], AppKeys.instances)
            VMInstanceController(instance).enable_debug()
        else:
            self.enable_debug = VMsJBossDebugController(function[AppKeys.JBoss_servers])
            # print trigger for startYAML
            self.print_trigger = True
            if Configuration.manual_startYamlFile is True:
                self.print_trigger = False

    def run(self):
        if Configuration.Jboss_EOCM is not True:
            Output.yellow('Enabling JBOSS debugging loggers, please wait...', print_trigger=self.print_trigger)
            self.recordFile()
            # the number of vm instances which have been successfully enabled
            successful_vms = self.enable_debug.enable_debug()

            if (len(successful_vms) == 0):
                Output.yellow("No JBoss loggers from VM instances have been enabled.", print_trigger=self.print_trigger)
            elif (len(successful_vms) == 1):
                Output.green("JBoss loggers from the VM instance %s has been enabled" % (successful_vms[0]),print_trigger=self.print_trigger)
            else:
                Output.green("The JBoss loggers from the following VM instances have been enabled", print_trigger=self.print_trigger)
                successful_vms = str(successful_vms)
                successful_vms = successful_vms.translate(None, "[']")
                Output.white(successful_vms, print_trigger=self.print_trigger)

            # two line breaks
            Output.white(print_trigger=self.print_trigger)

    def recordFile(self):
        logger = Configuration.JBoss_loggers
        list_dictionary = (self.function[AppKeys.JBoss_servers])
        str_of_list = "["
        for vms in list_dictionary:
             instances = Dictionary.get_value(vms, AppKeys.instances)
             self.vm = instances

        if type(self.vm) is str:
            self.vm = [self.vm]

        if type(self.vm) is list:
            for each in self.vm:
                str_of_list += ("\"" + str(each) + "\"")
                if (self.vm.index(each) != (len(self.vm) - 1)):
                    str_of_list += ","
        str_of_list += "]"
        run_time = Configuration.JBoss_time_out / 60
        timestamp = int(time.strftime('%Y%m%d%H%M')) + int(run_time)
        Configuration.last_run_file_time = timestamp
        if os.path.exists(Configuration.default_path + '/log/.lastRun') is False:
            Terminal.mkdir(Configuration.default_path + '/log/.lastRun')
        with open(Configuration.default_path + '/log/.lastRun/lastRunRecord_' + str(timestamp), 'w') as f:
            f.write(str_of_list + ',')
            for each in logger:
                f.write(each + ',')
                f.write('')
