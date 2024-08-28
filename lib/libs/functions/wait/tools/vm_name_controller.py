from libs.functions.wait.tools.vm_instance_controller import VMInstanceController
from libs.utilities.vms.instace_insert import InstanceInsert


class VMNameController():
    def __init__(self, server, timeout, function):

        l = InstanceInsert(server).correct_list()
        self.controllers = list()
        for each in l:
            self.controllers.append(VMInstanceController(each, timeout, function))
    def run(self):
        for each in self.controllers:
            each.run()
