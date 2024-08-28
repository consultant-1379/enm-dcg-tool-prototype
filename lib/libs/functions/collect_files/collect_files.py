from libs.functions.collect_files.tools.localhost.localhost_files import LocalhostFiles
from libs.functions.collect_files.tools.peer_server.peer_server_files import PeerServerFiles
from libs.functions.collect_files.tools.vm.vm_files import VMFiles
from libs.functions.function_superclass import FunctionSuperclass
from libs.utilities.data_structures.dictionary import Dictionary
from libs.utilities.system.terminal import Terminal
from libs.variables.configuration import Configuration
from libs.variables.keys import AppKeys


class CollectFiles(FunctionSuperclass):

    @staticmethod
    def func_name():
        return "Files"

    def __init__(self, function, app, config_stack):
        if (not FunctionSuperclass.check_name_equal(function[AppKeys.func_name], CollectFiles.func_name())):
            Terminal.exception("This function was wrongly passed in Files")

        # If the YAML file does not specify the server_type, consider it as VM by default
        self.type = Dictionary.get_value(function, AppKeys.server_type, default=VMFiles.server_type(), type=str,
                                         add_default=True).lower()

        # Set of the function list which contains 3 types
        self.collect_files_type = list()
        self.collect_files_type.append(LocalhostFiles)
        self.collect_files_type.append(PeerServerFiles)
        self.collect_files_type.append(VMFiles)

        self.function = function
        self.app = app

    def run(self):
        Configuration.plugin_count = int(Configuration.plugin_count) + 1
        target = None
        for each in self.collect_files_type:
            if (each.server_type() == self.type):
                target = each
                break

        if (target == None):
            Terminal.exception(
                '"server_type: %s "\nis not defined. Please check the %s file at %s' % (
                    self.type, self.app.get_file_type(), self.app.get_file_path()))
        else:
            target(self.function).run()
