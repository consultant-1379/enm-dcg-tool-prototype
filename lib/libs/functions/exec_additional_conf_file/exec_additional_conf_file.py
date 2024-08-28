from libs.config_item import ConfigItem
from libs.functions.function_superclass import FunctionSuperclass
from libs.utilities.data_structures.dictionary import Dictionary
from libs.utilities.system.file_paths import FilePaths
from libs.utilities.system.output import Output
from libs.utilities.system.terminal import Terminal
from libs.variables.keys import AppKeys, BasicKeys
from libs.variables.configuration import Configuration
import os


class ExecAdditionalConfFile(FunctionSuperclass):
    def __init__(self, function, app, config_stack):
        if (not FunctionSuperclass.check_name_equal(function[AppKeys.func_name], ExecAdditionalConfFile.func_name())):
            Terminal.exception("This function was wrongly passed in ProcessConfig")

        self.config_stack = config_stack
        self.function = function
        self.app = app
        # print trigger for startYAML
        self.print_trigger = True
        if Configuration.manual_startYamlFile is True:
            self.print_trigger = False

    def run(self):
        run_list = []
        file_path = self.function[AppKeys.additional_config_file_path]
        if type(file_path) is list:
            path = file_path[0]
        else:
            path = file_path

        if not '.implicit_plugins' in str(path).split('/'):
            Output.yellow('\nExecuting additional yaml file %s' % path,print_trigger=self.print_trigger)
            if os.path.exists(path):
                if len(run_list) > 0:
                    if path not in run_list:
                        function_index = 0
                        funcs = self.app.get_data()[AppKeys.functions]
                        while (funcs[function_index] != self.function):
                            function_index += 1

                        # function_index is now equal to the index of the current function

                        # point to the next function
                        function_index += 1
                        self.config_stack.peek().set_marker(function_index)

                        current_path = self.app.get_file_path()
                        default_storing_log = self.function[AppKeys.func_log_dir]
                        storing_log = Dictionary.get_value(self.function, AppKeys.storing_log, default=None)
                        if (storing_log == None):
                            storing_log = default_storing_log
                        else:
                            # find out the parent directory of the storing log and join it with the

                            default_storing_log = os.path.abspath(os.path.join(default_storing_log, os.pardir))
                            storing_log = FilePaths.join_path(default_storing_log, storing_log)

                        config_item = ConfigItem(self.absolute_path(current_path, path), implicit_plugins=False,
                                                 storing_log=storing_log)
                        run_list.append(path)
                        self.config_stack.push(config_item)
                        self.config_stack.push(object)

                        return False
                else:
                    function_index = 0
                    funcs = self.app.get_data()[AppKeys.functions]
                    while (funcs[function_index] != self.function):
                        function_index += 1

                    # function_index is now equal to the index of the current function

                    # point to the next function
                    function_index += 1
                    self.config_stack.peek().set_marker(function_index)

                    current_path = self.app.get_file_path()
                    default_storing_log = self.function[AppKeys.func_log_dir]
                    storing_log = Dictionary.get_value(self.function, AppKeys.storing_log, default=None)
                    if (storing_log == None):
                        storing_log = default_storing_log
                    else:
                        # find out the parent directory of the storing log and join it with the

                        default_storing_log = os.path.abspath(os.path.join(default_storing_log, os.pardir))
                        storing_log = FilePaths.join_path(default_storing_log, storing_log)

                    config_item = ConfigItem(self.absolute_path(current_path, path), implicit_plugins=False,
                                             storing_log=storing_log)

                    self.config_stack.push(config_item)
                    self.config_stack.push(object)

                    return False
            Output.red("The file %s can't be found\n" % path,print_trigger=self.print_trigger)
        else:
            function_index = 0
            funcs = self.app.get_data()[AppKeys.functions]
            while (funcs[function_index] != self.function):
                function_index += 1

            # function_index is now equal to the index of the current function

            # point to the next function
            function_index += 1
            self.config_stack.peek().set_marker(function_index)

            current_path = self.app.get_file_path()
            default_storing_log = self.function[AppKeys.func_log_dir]
            storing_log = Dictionary.get_value(self.function, AppKeys.storing_log, default=None)
            if (storing_log == None):
                storing_log = default_storing_log
            else:
                # find out the parent directory of the storing log and join it with the

                default_storing_log = os.path.abspath(os.path.join(default_storing_log, os.pardir))
                storing_log = FilePaths.join_path(default_storing_log, storing_log)

            config_item = ConfigItem(self.absolute_path(current_path, path), implicit_plugins=False,
                                     storing_log=storing_log)

            self.config_stack.push(config_item)
            self.config_stack.push(object)

            return False

    @staticmethod
    def func_name():
        return "Execute Additional Config File"


    def absolute_path(self, current_path, relative_path):

        absolute_path = FilePaths.get_directory(current_path) + "/" + relative_path
        pos = absolute_path.find('//')

        is_absolute_path = False
        while (not pos == -1):
            is_absolute_path = True

            absolute_path = absolute_path[pos + 2:]
            pos = absolute_path.find('//')

        if (is_absolute_path):
            if '.implicit_plugins' in absolute_path.split('/'):
                absolute_path = Configuration.config_files_dir + absolute_path
            else:
                absolute_path = '/' + absolute_path

        if os.path.exists(absolute_path) is False:
            Output.red('you have to provide a path of yaml file you want to execute',print_trigger=self.print_trigger)
            Configuration.skip_additional_config_file = True
        return absolute_path