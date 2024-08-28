

class MenuItem(object):

    def __init__(self, item,  config_file=None):
        self.item_namme = item
        self.config_file = config_file

    def get_item_path(self):
        return self.config_file

    def get_item_name(self):
        return self.item_namme
