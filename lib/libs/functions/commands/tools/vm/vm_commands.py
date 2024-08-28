from libs.functions.commands.tools.commands_superclass import CommandsSuperclass
from libs.utilities.data_structures.dictionary import Dictionary
from libs.utilities.system.terminal import Terminal
from libs.variables.keys import AppKeys
from libs.functions.commands.tools.vm.vm_name_controller import VMNameController


class VMCommands(CommandsSuperclass):
    def __init__(self, function):
        if (Dictionary.get_value(function, AppKeys.server_type) != VMCommands.server_type()):
            Terminal.exception('In the "Commands" function, the server type is %s, while %s is expected' % (
                Dictionary.get_value(function, AppKeys.server_type), VMCommands.server_type()))

        self.controller = VMNameController(function)

    @staticmethod
    def server_type():
        return 'vm'

    def run(self):
        self.controller.run()
