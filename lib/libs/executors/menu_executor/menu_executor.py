import signal

from libs.config_item import ConfigItem
from libs.executors.executor_superclass import ExecutorSuperclass
from libs.executors.menu_executor.single_option_menu import SingleOptionMenu
from libs.executors.tools.menu import Menu
from libs.utilities.data_structures.dictionary import Dictionary
from libs.utilities.file.absolute_path import AbsoluttePath
from libs.utilities.system.terminal import Terminal
from libs.variables.configuration import Configuration
from libs.variables.keys import BasicKeys, MenuKeys


class MenuExecutor(ExecutorSuperclass):

    def __init__(self, menu, menu_stack):
        menu = menu.get_data()
        super(MenuExecutor, self).__init__()
        if (menu[BasicKeys.config_type] != MenuExecutor.config_type()):
            Terminal.exception("This config was wrongly passed in MenuExecutor")
        self.menu_stack = menu_stack
        self.menu = Menu(menu)

        self.available_types = list()
        self.available_types.append(SingleOptionMenu)

    def run(self):

        # check for Ctrl-c press
        signal.signal(signal.SIGINT, self._ctrlC_handler)
        # check for Ctrl-Z press
        signal.signal(signal.SIGTSTP, self._ctrlC_handler)

        for each_type in self.available_types:
            if (each_type.menu_type() == self.menu.get_menu_type()):
                target = each_type
                break
        else:
            Terminal.exception("Incorrect menu type: %s. This error occurred in the file %s" % (
            self.menu.get_menu_type(), self.menu.menu_file_path))

        menu = target(self.menu,self.menu_stack)
        options = menu.get_options()

        if (not self.menu.is_redisplay()):
            self.menu_stack.pop()

        for option in options:
            additional_config_file_path = Dictionary.get_value(option, MenuKeys.config_file)
            if (additional_config_file_path == Configuration.previous_menu):
                self.menu_stack.pop()
            else:

                path = AbsoluttePath.AbsoluttePath(self.menu.menu_file_path, additional_config_file_path)

                config_item = ConfigItem(path)
                self.menu_stack.push(config_item)

    @staticmethod
    def config_type():
        return "menu"

    def _ctrlC_handler(self, sig, frame):
        import sys
        sys.exit()