from libs.functions.commands.tools.peer_server.peer_server_controller import PeerServerController
from libs.functions.cp_old_image.tools.cp_old_image_superclass import CpOldImageSuperclass
from libs.functions.function_superclass import FunctionSuperclass
from libs.utilities.data_structures.dictionary import Dictionary
from libs.utilities.server_result import ServerResult
from libs.utilities.system.file_paths import FilePaths
from libs.utilities.system.output import Output
from libs.utilities.system.print_text import Print
from libs.utilities.system.terminal import Terminal
from libs.variables.configuration import Configuration
from libs.variables.keys import AppKeys


class CpOldImage(CpOldImageSuperclass):

    @staticmethod
    def func_name():
        return "Cp From Old Image"

    def __init__(self, function, app, config_stack):
        if (not FunctionSuperclass.check_name_equal(function[AppKeys.func_name], CpOldImage.func_name())):
            Terminal.exception("This function was wrongly passed in CP From Old Image")
        self.instances = Dictionary.get_value(function, AppKeys.instances)
        if type(self.instances) is str:
            self.list_of_commands = [self.list_of_commands]
        self.path_for_collection = Dictionary.get_value(function, AppKeys.log_path)
        self.log_dir = Dictionary.get_value(function, AppKeys.func_log_dir)
        self.instances = self.set_instaces(self.instances)
        self.instances = self.remove_duplicates(self.instances)
        self.vms = ""
        self.image_age = "1"
        self.files_to_copy = ""
        # print trigger for startYAML
        self.print_trigger = True
        if Configuration.manual_startYamlFile is True:
            self.print_trigger = False

        if AppKeys.log_path in function:
            self.files_to_copy = Dictionary.get_value(function, AppKeys.log_path)
            self.files_to_copy = str(self.files_to_copy).strip("[]").replace("'", "").replace(" ", "")
        if AppKeys.vm_list in function:
            self.vms = Dictionary.get_value(function, AppKeys.vm_list)
            self.vms = str(self.vms).strip("[]").replace("'", "").replace(" ", "")
        if AppKeys.image_age in function:
            self.image_age = str(Dictionary.get_value(function, AppKeys.image_age))

    def run(self):
        Configuration.plugin_count = int(Configuration.plugin_count) + 1
        if Configuration.cloud_server is False:
            if FilePaths.isdir(self.log_dir) is False:
                Terminal.mkdir(self.log_dir)
            path_of_cp_image_file_log = "%s.LCSMetadata/Cp_From_Old_Image" % Configuration.storing_logs_dir
            if FilePaths.isdir(path_of_cp_image_file_log) is False:
                Terminal.mkdir(path_of_cp_image_file_log)
            result_to_print = ServerResult()
            path_of_script = FilePaths.join_path(Configuration.default_path, "lib/libs/scripts/cp_from_old_image.bsh")
            path_of_output = "/var/tmp/"

            Output.yellow("Collecting old image files on the peer servers",print_trigger=self.print_trigger)

            for each in self.instances:
                log_out_file = "%s/%s.out" % (path_of_cp_image_file_log, each)
                arg_list = "-o" + "\"" + self.log_dir + "\"" + " " + "-i" + "\"" + self.vms + "\"" + " " + "-a" + "\"" + self.image_age + "\"" + " " + "-f" + "\"" + self.files_to_copy + "\"" + " " + "-m" + "\"" + path_of_cp_image_file_log + "\""
                cmd = "bash " + path_of_output + "cp_from_old_image.bsh " + arg_list + " > " + log_out_file + " 2>&1"
                if PeerServerController.ping_server(each) is False:
                    result_to_print.add_down_server(each)
                else:
                    # scp file to svc
                    PeerServerController.scp_file(Configuration.peer_server_username,Configuration.peer_server_root_password,each,path_of_script,path_of_output)
                    # connect and execute script with root
                    cmd_child = self.login(each, Configuration.peer_server_username, Configuration.peer_server_root_password,self.print_trigger)
                    if cmd_child is not None:
                        import pexpect
                        Print.yellow("\nChecking [%s] for any old image to collect the logs." % each,trigger=self.print_trigger)
                        try:
                            cmd_child.sendline(cmd, 60)
                            expected = "root.*"
                            exception = "copy-out:.*"
                            cmd_child.expect([expected, exception], 60)
                            cmd_child.close()
                            result_to_print.add_successful_server(each)
                            Print.white("[%s]\n" % each,trigger=self.print_trigger)
                            with open(log_out_file) as f:
                                content = f.read().splitlines(False)
                            for line in content:
                                Print.white(line,trigger=self.print_trigger,new_line=False)
                        except pexpect.EOF and pexpect.TIMEOUT:
                            Output.red("Unexpected issue occurred, Host not responding with commands.",print_trigger=self.print_trigger)
                            result_to_print.add_unsuccessful_server(each)

            result_to_print.print_result("Cp From Old Image", "peer server")

        else:
            Output.yellow('Skipping Copy From old Image plugin on Cloud Server, not applicable for vENM',print_trigger=self.print_trigger)

    @staticmethod
    def login(peer_server,username,password,print_trigger):
        """
        :return: child of pexpect if connect is successful. Otherwise, None
        """
        if PeerServerController.ping_server(peer_server) is False:
            return None
        else:
            child = PeerServerController.connect_peer_server(username, peer_server)

            if not PeerServerController.login_peer_server(password, child):
                Output.red("Incorrect password(s) to connect to the peer server [%s]" % (peer_server),print_trigger=print_trigger)
                return None

            if not PeerServerController.use_root(password, child):
                Output.red("Incorrect root password",print_trigger=print_trigger)
                return None

            return child

    @staticmethod
    def remove_duplicates(list):

        unique = []
        for elem in list:
            if elem not in unique:
                unique.append(elem)

            # Return the list of unique elements
        return unique

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
                list_of_instaces += CpOldImage._get_clusters('svc_cluster')

            elif instance == 'db_cluster':
                list_of_instaces.remove(instance)
                list_of_instaces += CpOldImage._get_clusters('db_cluster')

            elif instance == 'scp_cluster':
                list_of_instaces.remove(instance)
                list_of_instaces += CpOldImage._get_clusters('scp_cluster')
            elif instance == 'all_clusters':
                list_of_instaces.remove(instance)
                list_of_instaces += CpOldImage._get_clusters(instance)

        return list_of_instaces
