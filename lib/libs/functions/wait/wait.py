from libs.functions.function_superclass import FunctionSuperclass
from libs.functions.wait.tools.vm_name_controller import VMNameController
from libs.functions.wait.tools.wait_reproducing_issues import WaitTime
from libs.utilities.data_structures.dictionary import Dictionary
from libs.utilities.system.file_paths import FilePaths
from libs.utilities.system.terminal import Terminal
from libs.variables import variables
from libs.variables.configuration import Configuration
from libs.variables.keys import AppKeys


class Wait(FunctionSuperclass):
    def __init__(self, function, app, config_stack):
        if (not FunctionSuperclass.check_name_equal(function[AppKeys.func_name], Wait.func_name())):
            Terminal.exception("This function was wrongly passed to Wait")

        debug_time = Dictionary.get_value(function, AppKeys.debug_time, default=variables.default_debug_time)
        self.wait_function = WaitTime(debug_time, function[AppKeys.message])

        if Configuration.debug_time != None:
            # if the user passes the timeout argument in the command line
            timeout = Configuration.debug_time
        else:
            # use the debug time stated in the YAML file
            timeout = debug_time

        # if the user decides the extend the log time
        timeout *= 2

        # we ask the user if they want to extend the log time, which will take one minute
        timeout += 60

        # another 2 minutes to allow for disabling the loggers
        timeout += 120

        self.controllers = list()
        for each_vm in Dictionary.get_value(function, AppKeys.JBoss_servers):
            controller = VMNameController(each_vm, timeout, function)
            self.controllers.append(controller)

    def run(self):
        # run the script in each vm respectively
        for each in self.controllers:
            each.run()

        # run the wait function
        self.wait_function.run()

    @staticmethod
    def func_name():
        return 'wait'
