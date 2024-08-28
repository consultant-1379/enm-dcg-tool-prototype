from libs.executors.tools.menu_controller import MenuController
from libs.utilities.data_structures.type_check import TypeCheck
from libs.utilities.system.output import Output
from libs.utilities.system.terminal import Terminal
from libs.variables.variables import exit, go_back

class SingleOptionMenu(MenuController):

    def __init__(self, menu,menu_stack):
        """

        :param menu: an object of class Menu
        """

        if (menu.redisplay):
            if menu_stack.size() == 1:
                super(SingleOptionMenu, self).__init__(menu, [exit])
            else:
                super(SingleOptionMenu, self).__init__(menu, [go_back])
        else:
            super(SingleOptionMenu, self).__init__(menu)

    @staticmethod
    def menu_type():
        return 'Single Option'

    def get_options(self):

        # print the menu
        self.print_menu()
        while (True):
            try:
                input = Terminal.input()
                choice_list = self.get_option_list(input)
                if (len(choice_list) != 1):
                    raise ValueError()
                break

            except(IndexError):
                Output.red("Out of range. Please try again: ",new_line=False)
            except(ValueError):
                Output.red("You can only select one item.")
        TypeCheck.list(choice_list)
        return choice_list
