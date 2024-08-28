import sys

from libs.functions.function_superclass import FunctionSuperclass
from libs.functions.jboss_debug.jboss_debug import JBOSSDebug
from libs.utilities.data_structures.dictionary import Dictionary
from libs.utilities.system.print_text import Print
from libs.utilities.system.terminal import Terminal
from libs.variables.configuration import Configuration
from libs.variables.keys import AppKeys


class AnyName():

    def __init__(self,func):
        self.func = func

    def run(self):
        if Configuration.vm_name == False:
            Print.yellow('Enter the vm instance(s) you want to execute this yaml file on ')
            Print.yellow('Enter instances: ')
            vm_input = Terminal.input('')
            Configuration.vm_list = vm_input.split(',')
            if (FunctionSuperclass.check_name_equal(self.func[AppKeys.func_name], JBOSSDebug.func_name())):
                JBoss = Dictionary.get_value(self.func,AppKeys.JBoss_servers)
                for item in JBoss:
                    Dictionary.set_value(item, AppKeys.instances, Configuration.vm_list)
                    Configuration.vm_name = True
                    return self.func
            else:
                Dictionary.set_value(self.func, AppKeys.instances, Configuration.vm_list)
                Configuration.vm_name = True
                return self.func
        else:
            if (FunctionSuperclass.check_name_equal(self.func[AppKeys.func_name], JBOSSDebug.func_name())):
                JBoss = Dictionary.get_value(self.func,AppKeys.JBoss_servers)
                for item in JBoss:
                    Dictionary.set_value(item, AppKeys.instances, Configuration.vm_list)
                    return self.func
            else:
                Dictionary.set_value(self.func, AppKeys.instances,  Configuration.vm_list)
                return self.func


    @staticmethod
    def VM_name():
        return "['vms=GET_V1A_CMD']"

    @staticmethod
    def checkfile(func):
        if (FunctionSuperclass.check_name_equal(func[AppKeys.func_name], JBOSSDebug.func_name())):
                JBoss = Dictionary.get_value(func, AppKeys.JBoss_servers)
                for each in JBoss:
                    if AppKeys.instances in each:
                        name = Dictionary.get_value(each, AppKeys.instances)
                        if str(name) == AnyName.VM_name():
                            return True
                    return False
        else:
            if AppKeys.instances in func:
                name = Dictionary.get_value(func, AppKeys.instances)
                if str(name) == AnyName.VM_name():
                    return True
            return False

