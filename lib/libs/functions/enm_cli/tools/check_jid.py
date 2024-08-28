from libs.utilities.data_structures.dictionary import Dictionary
from libs.utilities.system.output import Output
from libs.variables.configuration import Configuration
from libs.variables.keys import AppKeys


class CheckJID:

    def __init__(self, function):
        self.function = function
        self.var = None
        # print trigger for startYAML
        self.print_trigger = True
        if Configuration.manual_startYamlFile is True:
            self.print_trigger = False
        cli_cmd = Dictionary.get_value(self.function, AppKeys.enm_commands)[0]
        if str(cli_cmd).startswith("JID"):
            if str(cli_cmd).split("=", 1)[0] != "JID":
                Output.yellow("Yaml File variable not initialized correctly",print_trigger=self.print_trigger)
            else:
                Configuration.JID_present = True
                refactored_cmd = [str(cli_cmd).split("=", 1)[1]]
                Dictionary.set_value(self.function, AppKeys.enm_commands, refactored_cmd)
        else:
            Configuration.JID_present = False

    def return_function(self):
        return self.function
        # Idea for multiple JID Variables

        # def __init__(self, function):
        #     self.function = function
        #     self.var = None
        #     cli_cmd = Dictionary.get_value(self.function, AppKeys.enm_commands)[0]
        #     if str(cli_cmd).startswith("JID"):
        #         self.var = str(cli_cmd).split("=", 1)[0]
        #         if self.var.__contains__("_"):
        #             index = self.var.split("_", 1)[1]
        #             try:
        #                 index = int(index)
        #                 Configuration.JID_list.insert(index, self.var)
        #             except ValueError:
        #                 Logger.warning("JID index is not a integer")
        #         else:
        #             Configuration.JID_list.append(self.var)
        #         Configuration.JID_present = True
        #     else:
        #         pass
