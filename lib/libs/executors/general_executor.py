from libs.executors.app_executor.app_executor import AppExecutor
from libs.executors.menu_executor.menu_executor import MenuExecutor
from libs.utilities.data_structures.dictionary import Dictionary
from libs.utilities.data_structures.type_check import TypeCheck
from libs.utilities.system.terminal import Terminal
from libs.variables.keys import BasicKeys


class GeneralExecutor(object):
    def __init__(self, config, menu_stack):
        """
        Execute the current configuration files (e.g. YAML file)
        :param config: The configuration item which is being executed
        :param menu_stack: The order of all configuration files which will be executed
        """
        super(GeneralExecutor, self).__init__()

        # Initialise the variables
        self.config = config
        self.menu_stack = menu_stack

        next_config = menu_stack.second_peek()

        # Find out the next configuration file type
        if (next_config == None):
            next_config_type = None
        else:
            next_config_type = next_config.get_config_type()

        Dictionary.set_value(self.config.get_data(), BasicKeys.next_config_type, next_config_type)

        # Set up the list of all available executors
        self.executors = list()
        self.executors.append(AppExecutor)
        self.executors.append(MenuExecutor)

    def run(self):
        config_type = self.config.get_config_type()

        # find the executor which matches the configuration file (i.e. YAML file)
        target = GeneralExecutor.find_executor(self.executors, config_type, None)
        if (target == None):
            Terminal.exception("The config_type: '%s' in the file %s is not defined" % (config_type, self.menu_stack))

        executor = target(self.config, self.menu_stack)
        return executor.run()

    @staticmethod
    def find_executor(executors, config_type, default_executor=None):
        TypeCheck.str(config_type)
        TypeCheck.list(executors)

        target = default_executor
        for executor in executors:
            if (config_type == executor.config_type()):
                target = executor
                break

        return target
