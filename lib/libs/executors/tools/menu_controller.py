from libs.executors.tools.str_number_list import NumStrToList
from libs.utilities.data_structures.dictionary import Dictionary
from libs.utilities.data_structures.type_check import TypeCheck
from libs.utilities.system.output import Output
from libs.utilities.system.terminal import Terminal
from libs.variables.keys import MenuKeys, JBossMenuKeys
from libs.start_up_message.start_up_msg import StartUpMsg

class MenuController(object):
    @staticmethod
    def menu_type():
        Terminal.exception("This method must be implemented.")

    start_index = 0

    def __init__(self, menu, pre_options=list(), post_options=list(), option_type=None):
        TypeCheck.list(pre_options)
        TypeCheck.list(post_options)
        if (option_type == None):
            self.item_prefix = ''
        else:
            self.item_prefix = option_type + ': '

        self.menu = menu
        self.pre_options = pre_options
        self.post_options = post_options
        if (len(pre_options) > 0):
            MenuController.start_index = 0
        else:
            MenuController.start_index = 1

    def get_option_list(self, input):
        TypeCheck.str(input, "input")

        def parse_numbers(range):

            converter = NumStrToList(input, range)
            # TODO: incase the user selects more than one option including 0. Go Back

            if (converter.is_legal()):
                return converter.convert()
            else:
                return False

        # the range that can be chosen from
        all_options = self.pre_options + self.menu.options + self.post_options
        available_range = range(MenuController.start_index, MenuController.start_index + len(all_options))

        # get correct choice list
        choice_list = parse_numbers(available_range)
        if (choice_list == False):
            raise IndexError("out of range")

        # get the dictionary options that are selected
        selected_options = list()
        for each in choice_list:
            selected_options.append(all_options[each - MenuController.start_index])

        # Reverse the list
        return selected_options[::-1]

    def print_menu(self):
        """

        :return: range of available options
        """
        columns = Terminal.console_width()
        separator = columns * "*"

        def print_title():
            Output.white(separator)
            Output.white()

            Output.yellow((" %s " % self.menu.title).center(columns, ' '))
            Output.white()
            Output.white(separator)

        def print_options(option_list, index, item_prefix=''):
            """

            :param option_list: each option is a dictionary
            :param index: starting index
            :return: Ending index + 1
            """
            for each in option_list:
                TypeCheck.dict(each)

                # print index
                text = str(index) + ". "
                if (index < 10):
                    text += " "

                # print prefix
                text += item_prefix
                # print item name
                item_name = Dictionary.get_value(each, MenuKeys.item_name, type=str, file_path=self.menu.menu_file_path)

                text += item_name

                # Decide item's color
                selected = Dictionary.get_value(each, JBossMenuKeys.selected, False, type=bool)

                if (selected):
                    Output.green(text)
                else:
                    Output.white(text)

                index += 1
            return index

        Terminal.clear()
        StartUpMsg.message()
        print_title()
        Output.white()

        index = MenuController.start_index

        index = print_options(self.pre_options, index)
        index = print_options(self.menu.options, index, self.item_prefix)
        index = print_options(self.post_options, index)

        Output.white(separator)
        Output.yellow("Enter your choice [%d-%d]: " % (MenuController.start_index, index - 1))

        return range(MenuController.start_index, index)
