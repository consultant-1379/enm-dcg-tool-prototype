from libs.functions.jboss_debug.tools.debug_logs_superclass import DebugLogsSuperclass
from libs.functions.jboss_debug.tools.vm_name_controller import VMNameController


class VMsJBossDebugController(DebugLogsSuperclass):
    def __init__(self, vm_name_list, debug_name='default debug name', debug_time=300):
        """

        :param debug_name: the name of this use case
        :param debug_time: The time for debugging in second
        :param vm_name_list: a list of dictionaries containing the logger info
        """

        DebugLogsSuperclass.__init__(self, debug_name, debug_time)

        self.vm_name_list = vm_name_list

        self.vm_name_controller_list = list()
        for vm_name in self.vm_name_list:
            vm_name_controller = VMNameController(vm_name)
            self.vm_name_controller_list.append(vm_name_controller)

    def enable_debug(self):
        successful_vms = list()
        for vm_name_controller in self.vm_name_controller_list:
            successful_vms += vm_name_controller.enable_debug()
        return successful_vms

    def disable_debug(self):
        successful_vms = list()
        for vm_name_controller in self.vm_name_controller_list:
            successful_vms += vm_name_controller.disable_debug()
        return successful_vms
