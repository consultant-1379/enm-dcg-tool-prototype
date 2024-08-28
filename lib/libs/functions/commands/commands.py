from libs.functions.commands.tools.peer_server.peer_server_commands import PeerServerCommands
from libs.functions.commands.tools.localhost.localhost_commands import LocalhostCommands
from libs.functions.commands.tools.vm.vm_commands import VMCommands
from libs.functions.function_superclass import FunctionSuperclass
from libs.utilities.data_structures.dictionary import Dictionary
from libs.utilities.system.terminal import Terminal
from libs.variables.configuration import Configuration
from libs.variables.keys import AppKeys


class Commands(FunctionSuperclass):

    @staticmethod
    def func_name():
        return "Commands"

    def __init__(self, function, app, config_stack):
        if (not FunctionSuperclass.check_name_equal(function[AppKeys.func_name], Commands.func_name())):
            Terminal.exception("This function was wrongly passed in Commands")
        self.function = function
        self.app = app
        # Set up all command types
        self.command_types = list()
        self.command_types.append(VMCommands)
        self.command_types.append(LocalhostCommands)
        self.command_types.append(PeerServerCommands)

        self.type = Dictionary.get_value(function, AppKeys.server_type, VMCommands.server_type(), type=str,
                                         add_default=True)
        self.type = self.type.lower()

    def run(self):
        target = None

        Configuration.plugin_count = int(Configuration.plugin_count) + 1
        for each in self.command_types:
            if (each.server_type() == self.type):
                target = each
                break

        if (target == None):
            Terminal.exception(
                'server_type: %s is not defined. Please check the file at %s' % (self.type, self.app.get_file_path()))
        else:
            target(self.function).run()
