from libs.executors.tools.menu_item import MenuItem
from libs.utilities.data_structures.dictionary import Dictionary
from libs.utilities.file.absolute_path import AbsoluttePath
from libs.variables.keys import MenuKeys


class MenuItemParser(object):
    @staticmethod
    def parser(dictioray, currect_file_path, leave_item=False):
        item_name = Dictionary(dictioray, MenuKeys.item_name)
        if (leave_item):
            menu_item = MenuItem(item_name, leave_item)
        else:
            config_file = AbsoluttePath.AbsoluttePath(currect_file_path)
            menu_item = MenuItem(item_name, leave_item, config_file)
        return menu_item
