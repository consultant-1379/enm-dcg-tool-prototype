import sys
import time

from libs.functions.enable_jboss_commands.enable_jboss_command import JBossCommandController
from libs.functions.function_superclass import FunctionSuperclass
from libs.functions.jboss_debug.tools.vm_instance_controller import VMInstanceController
from libs.functions.jboss_debug.tools.vms_jboss_debug_controller import VMsJBossDebugController
from libs.utilities.data_structures.dictionary import Dictionary
from libs.utilities.system.output import Output
from libs.utilities.system.terminal import Terminal
from libs.variables.configuration import Configuration
from libs.variables.keys import AppKeys


class DisableDebug(FunctionSuperclass):
    """description of class"""

    @staticmethod
    def func_name():
        return "Disable Debug"

    def __init__(self, function, app, config_stack, stamp, yaml_time):
        self.time = None
        self.stamp = stamp
        self.function = function
        if (not FunctionSuperclass.check_name_equal(function[AppKeys.func_name], DisableDebug.func_name())):
            Output.yellow("The function name is %s, which %s is expected." % (
                function[AppKeys.func_name], DisableDebug.func_name()))
            Terminal.exception("This function was wrongly passed in DisableDebug")
        if Configuration.Jboss_EOCM is True:
            file_name = app.get_config_name()
            jboss_servers = Dictionary.get_value(self.function, AppKeys.JBoss_servers)
            instance = Dictionary.get_value(jboss_servers[0], AppKeys.instances)
            if Configuration.debug_time is None:
                if type(yaml_time) is list:
                    time_left = int(yaml_time[0])
                else:
                    time_left = int(yaml_time)
            else:
                time_left = Configuration.debug_time
            for num in xrange(int(time_left), 0, -1):
                sys.stdout.write('\rReproduce issues for "' + file_name +'", time left ' + str(num) + ' seconds')
                sys.stdout.flush()
                time.sleep(1)
            VMInstanceController(instance).disable_debug()

        else:
            self.debug = VMsJBossDebugController(function[AppKeys.JBoss_servers])
            # print trigger for startYAML
            self.print_trigger = True
            if Configuration.manual_startYamlFile is True:
                self.print_trigger = False

    def run(self):
        Configuration.tcptaring = True
        if Configuration.Jboss_EOCM is not True:
            JBossCommandController(self.function, self.time, self.stamp)
            Output.yellow('Disabling JBOSS debugging loggers, please wait...',print_trigger=self.print_trigger)
            successful_vms = self.debug.disable_debug()
            if (len(successful_vms) == 0):
                Output.yellow("No JBoss loggers from VM instances have been disabled.",print_trigger=self.print_trigger)
            elif (len(successful_vms) == 1):
                Output.green("JBoss loggers from the VM instance %s has been disabled" % (successful_vms[0]), print_trigger=self.print_trigger)
            else:
                Output.green("The JBoss loggers from the VM instances have been disabled",print_trigger=self.print_trigger)
            # two line breaks
            if len(Configuration.failed_Jboss_diabled_list) == 0:
                Terminal.system('sudo rm %s/log/.lastRun/lastRunRecord_%s' % (
                Configuration.default_path, Configuration.last_run_file_time))
                Output.white()