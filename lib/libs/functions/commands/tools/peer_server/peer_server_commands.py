import copy

from libs.functions.commands.tools.peer_server.login_peer_server import LoginPeerServer
from libs.functions.commands.tools.commands_superclass import CommandsSuperclass
from libs.utilities.data_structures.dictionary import Dictionary
from libs.utilities.server_result import ServerResult
from libs.utilities.system.output import Output
from libs.utilities.system.terminal import Terminal
from libs.variables.configuration import Configuration
from libs.variables.keys import AppKeys


class PeerServerCommands(CommandsSuperclass):
    def __init__(self, function):
        """
        NB: Variable naming convention in this package: blade = peer server
        :param function:
        """
        if (Dictionary.get_value(function, AppKeys.server_type) != PeerServerCommands.server_type()):
            Terminal.exception('In the "Commands" function, the server type is %s, while %s is expected' % (
                Dictionary.get_value(function, AppKeys.server_type), PeerServerCommands.server_type()))
        self.function = function
        # print trigger for startYAML
        self.print_trigger = True
        if Configuration.manual_startYamlFile is True:
            self.print_trigger = False


    @staticmethod
    def server_type():
        return 'peer servers'

    def run(self):
        if Configuration.cloud_server is False:
            results_to_print = ServerResult()
            # Command can only run on physical servers
            if (Configuration.cloud_server):
                Output.yellow("The following function can only run on physical server, so it has been skipped.", print_trigger=self.print_trigger)
                Output.white(self.function, print_trigger=self.print_trigger)

            server_list = Dictionary.get_value(self.function, AppKeys.instances)

            # if the server list is a string, convert the value into a list of strings (only one string in this list)
            if (type(server_list) == str):
                server_list = [server_list]

            server_list = self.set_instaces(server_list)
            if len(server_list) != 0:
                Output.yellow("Executing commands in the following Peer Server: ", print_trigger=self.print_trigger)
                Output.white(str(server_list), print_trigger=self.print_trigger)
            for each_server in server_list:
                each_server_dictionary = copy.deepcopy(self.function)
                Dictionary.set_value(each_server_dictionary, AppKeys.instance, each_server)

                controller = LoginPeerServer(each_server_dictionary, Configuration.peer_server_username,
                                             Configuration.peer_server_password,
                                             Configuration.peer_server_root_password)
                # controller.run()
                if controller.run() == False:
                    results_to_print.add_down_server(each_server)
                else:
                    results_to_print.add_successful_server(each_server)

            results_to_print.print_result("Commands", "peer server")
        else:
            Output.yellow('Skipping Peer Server Commands Plugin on Cloud Server', print_trigger=self.print_trigger)

    @staticmethod
    def _get_clusters(cluster_name):
            if (cluster_name == 'all_clusters'):

                clusters = Terminal.popen_read(
                    "for clus in $(litp show -p /deployments/enm/clusters/ 2> /dev/null | egrep \"[ ]+/\" | awk -F '/' '{print $NF}'); do for subclus in $(litp show -p /deployments/enm/clusters/${clus}/nodes | egrep \"[ ]+/\" | awk -F '/' '{print $NF}'); do echo $subclus; done; done")
            else:
                clusters = Terminal.popen_read(
                    "for subclus in $(litp show -p /deployments/enm/clusters/%s/nodes 2> /dev/null | egrep \"[ ]+/\" | awk -F '/' '{print $NF}'); do echo $subclus; done" % (
                        cluster_name))
            clusters = clusters.split('\n')[:-1]
            return clusters

    @staticmethod
    def set_instaces(list_of_instaces):
        for instance in list_of_instaces:
            if instance == 'svc_cluster':
                list_of_instaces.remove(instance)
                list_of_instaces += PeerServerCommands._get_clusters('svc_cluster')

            elif instance == 'db_cluster':
                list_of_instaces.remove(instance)
                list_of_instaces += PeerServerCommands._get_clusters('db_cluster')

            elif instance == 'scp_cluster':
                list_of_instaces.remove(instance)
                list_of_instaces += PeerServerCommands._get_clusters('scp_cluster')
            elif instance == 'all_clusters':
                list_of_instaces.remove(instance)
                list_of_instaces += PeerServerCommands._get_clusters(instance)

        return list_of_instaces
