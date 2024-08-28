from libs.utilities.data_structures.dictionary import Dictionary
from libs.variables.configuration import Configuration


class RefactorYaml:

    def __init__(self, function):
        self.function = function
        self.getJID()
        for each in self.function:
            for key,value in each.items():
                if type(value) is list:
                    for each_item in value:
                        each_item = self.replace(each_item)
                        Dictionary.set_value(each, key, each_item)
                elif type(value) is str:
                    value = self.replace(value)
                    Dictionary.set_value(each, key, value)

    def getJID(self):
        if Configuration.JID_path is not None:
            file_to_read = Configuration.JID_path
            with open(file_to_read, 'r') as f:
                lines = f.read().splitlines()
                last_line = lines[-1]
                id = str(last_line).split("ID")[1]
                id = id.strip()
                Configuration.JID_ID = id

    def replace(self, string):
        if str(string).__contains__("$$JID$$"):
            replaced = str(string).replace("$$JID$$", Configuration.JID_ID)
            return replaced
        else:
            return string

    def method(self):
        del self.function[1]
        return self.function