from libs.functions.function_superclass import FunctionSuperclass
from libs.utilities.data_structures.dictionary import Dictionary
from libs.utilities.system.output import Output
from libs.variables.configuration import Configuration
from libs.variables.keys import AppKeys, BasicKeys
from libs.utilities.system.terminal import Terminal


class UnknownFunction(FunctionSuperclass):
    def __init__(self, function, app, config_stack):
        """
        If there is a function defined in the configuration file. and the function name is not defined, the function will be past to this class
        :param function:
        :param app:
        :param config_stack:
        """
        self.function = function
        self.path = Dictionary.get_value(app, BasicKeys.current_file_path, type=str)
        self.file_type = Dictionary.get_value(app, BasicKeys.file_type, type=str)
        # print trigger for startYAML
        self.print_trigger = True
        if Configuration.manual_startYamlFile is True:
            self.print_trigger = False

    def run(self):
        Output.red('The %s file at ' % (self.file_type), new_line=False,print_trigger=self.print_trigger)
        Output.white(self.path, new_line=False,print_trigger=self.print_trigger)
        Output.red(' contains the value "%s" of the key "%s" which is undefined.' % (
            self.function[AppKeys.func_name], AppKeys.func_name),print_trigger=self.print_trigger)
        Output.red('Re-configure this file.',print_trigger=self.print_trigger)
        Terminal.any_input()
        return False
