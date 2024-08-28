from libs.utilities.data_structures.string import String
from libs.utilities.system.output import Output
from libs.variables.configuration import Configuration


class ServerResult():
    def __init__(self):
        self._not_exist = list()
        self._successful = list()
        self._unsuccessful = list()
        self._down = list()
        self.print_trigger = True
        if Configuration.manual_startYamlFile is True:
            self.print_trigger = False

    def add_not_exist_server(self, not_exist):
        self._not_exist.append(not_exist)

    def add_successful_server(self, successful):
        self._successful.append(successful)

    def add_down_server(self, down_server):
        self._down.append(down_server)

    def add_unsuccessful_server(self, unsuccessful):
        self._unsuccessful.append(unsuccessful)

    def get_unsuccessful(self):
        return self._unsuccessful

    def get_successful(self):
        return self._successful

    def get_not_exist(self):
        return self._not_exist

    def get_down_server(self):
        return self._down

    def __iadd__(self, other):
        if (type(other) == ServerResult):
            self._not_exist += other._not_exist
            self._successful += other._successful
            self._down += other._down
            return self
        else:
            raise Exception("The iadd argument must be in type of ServerResult")

    def print_result(self, operation, server_type):
        """
        Print out the operation result(s)
        :param operation: operation name e.g. enable JBoss loggers
        :param server_type: VM/localhost/peer server
        :return:
        """
        flag = False
        ############################################################
        # print successful message
        if len(self._successful) != 0:
            text = ("%s completed on the %s" % (operation, server_type))

            # consider the plural case
            if len(self._successful) > 1:
                text += 's'
            Output.green(text,print_trigger=self.print_trigger)
            flag = True
        ############################################################
        # print unsuccessful message
        if len(self._unsuccessful) != 0:
            text = ("%s failed on the %s" % (operation, server_type))

            # consider the plural case
            if len(self._unsuccessful) > 1:
                text += 's'
            text += " %s. Error: Issue during operation" % (String.join(self._unsuccessful))
            Output.red(text,print_trigger=self.print_trigger)
            flag = True
        ############################################################
        # print successful message for not existing servers

        if len(self._not_exist) != 0:
            text = ("%s failed on the %s" % (operation, server_type))

            # consider the plural case
            if len(self._not_exist) > 1:
                text += 's'
            text += " %s. Error: server not present" % (String.join(self._not_exist))
            Output.red(text,print_trigger=self.print_trigger)
            flag = True

        ############################################################
        # print fail message for down servers
        if len(self._down) != 0:
            text = ("%s failed on the %s" % (operation, server_type))

            # consider the plural case
            if len(self._down) > 1:
                text += 's'
            text += " %s. Error: server no response" % (String.join(self._down))
            Output.red(text,print_trigger=self.print_trigger)
            flag = True
        ############################################################
        if (flag == False):
            Output.yellow("Failed to connect to peer server(s).",print_trigger=self.print_trigger)
        Output.white("",print_trigger=self.print_trigger)