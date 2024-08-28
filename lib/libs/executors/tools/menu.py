from libs.executors.menu_executor.single_option_menu import SingleOptionMenu
from libs.utilities.data_structures.dictionary import Dictionary
from libs.variables.keys import BasicKeys, MenuKeys, JBossMenuKeys


class Menu(object):

    def __init__(self, menu):
        self.menu_file_path = Dictionary.get_value(menu, BasicKeys.current_file_path, default=None, type=str)

        config_name = Dictionary.get_value(menu, BasicKeys.config_name, file_path=self.menu_file_path)

        self.menu_type = Dictionary.get_value(menu, MenuKeys.menu_type, SingleOptionMenu.menu_type(), type=str)

        self.title = Dictionary.get_value(menu, MenuKeys.title, config_name, type=str)

        self.redisplay = Dictionary.get_value(menu, MenuKeys.redisplay, True, type=bool)

        self.options = Dictionary.get_value(menu, MenuKeys.options, list(), type=list)

        self.options_type = Dictionary.get_value(menu, JBossMenuKeys.options_type, None, type=str)

    def get_title(self):
        return self.title

    def get_options(self):
        return self.options

    def get_menu_type(self):
        return self.menu_type

    def is_redisplay(self):
        return self.redisplay
