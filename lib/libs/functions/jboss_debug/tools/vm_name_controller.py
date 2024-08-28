from libs.functions.jboss_debug.tools.vm_instance_controller import VMInstanceController
from libs.utilities.system.output import Output
from libs.utilities.vms.instace_insert import InstanceInsert


class VMNameController():
    def __init__(self, server):

        self.vm_instances = InstanceInsert(server)
        correct_list = self.vm_instances.correct_list()
        self.controllers = list()

        for each_instance in correct_list:
            self.controllers.append(VMInstanceController(each_instance))

    def enable_debug(self):
        incorrect_list = self.vm_instances.incorrect_list()
        if len(incorrect_list) != 0:
            Output.red("\nThe following VMs don't exist for Jboss")
            incorrect_list = str(incorrect_list)
            incorrect_list = incorrect_list.translate(None, "[']")
            Output.white(incorrect_list + "\n")

        successful_vms = list()
        for each_vm_instance_controller in self.controllers:
            if (each_vm_instance_controller.enable_debug() == True):
                #
                successful_vms.append(each_vm_instance_controller.get_vn_instance_name())
            else:
                # the VM is not reachable
                each_vm_instance_controller.get_vn_instance_name()

        return successful_vms

    def disable_debug(self):
        successful_vms = list()
        for each_vm_instance_controller in self.controllers:
            if (each_vm_instance_controller.disable_debug() == True):
                successful_vms.append(each_vm_instance_controller.get_vn_instance_name())
        return successful_vms
