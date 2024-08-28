from libs.functions.commands.tools.vm.vm_instance_controller import VMInstanceController
from libs.utilities.system.output import Output
from libs.utilities.vms.instace_insert import InstanceInsert
from libs.variables.configuration import Configuration


class VMNameController():
    def __init__(self, server):
        """

        :param server: Dictionary the the vm command function
        """
        self.vm_name = InstanceInsert(server)
        correct_list = self.vm_name.correct_list()
        self.controllers = list()
        for each in correct_list:
            self.controllers.append(VMInstanceController(each, server))
        # print trigger for startYAML
        self.print_trigger = True
        if Configuration.manual_startYamlFile is True:
            self.print_trigger = False

    def run(self):
        incorrect_list = self.vm_name.incorrect_list()
        correct_list = self.vm_name.correct_list_vms()

        Output.green("\nExecuting commands on VM's: ", print_trigger=self.print_trigger)
        for each in self.controllers:
            each.run()

        if (len(incorrect_list) != 0):
            Output.red("\nThe following VMs don't exist for Command Execution", print_trigger=self.print_trigger)
            incorrect_list = str(incorrect_list)
            incorrect_list = incorrect_list.translate(None, "[']")
            Output.white(incorrect_list + "\n", print_trigger=self.print_trigger)

        if len(correct_list) != 0:
            Output.green("\nSuccessful: The following VMs exist for Command Execution", print_trigger=self.print_trigger)
            correct_list = str(correct_list)
            correct_list = correct_list.translate(None, "[']")
            Output.white(correct_list + "\n", print_trigger=self.print_trigger)
