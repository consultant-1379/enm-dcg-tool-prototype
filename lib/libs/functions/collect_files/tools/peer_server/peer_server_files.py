import os
import subprocess
import pexpect

from libs.functions.collect_files.tools.collect_files_superclass import CollectFilesSuperclass
from libs.functions.collect_files.tools.global_exclusion import GlobalExclusion
from libs.functions.commands.tools.peer_server.peer_server_controller import PeerServerController
from libs.logging.logger import Logger
from libs.utilities.data_structures.dictionary import Dictionary
from libs.utilities.peer_servers.peer_server import PeerServer
from libs.utilities.system.file_paths import FilePaths
from libs.utilities.system.output import Output
from libs.utilities.system.print_text import Print
from libs.utilities.system.terminal import Terminal
from libs.variables.configuration import Configuration
from libs.variables.keys import AppKeys


class PeerServerFiles(CollectFilesSuperclass):
    def __init__(self, function):
        if (not CollectFilesSuperclass.check_name_equal(function[AppKeys.server_type], PeerServerFiles.server_type())):
            Terminal.exception("This function was wrongly passed in PeerServerFiles")

        self.instances = Dictionary.get_value(function, AppKeys.instances)
        if (type(self.instances) == str):
            self.instances = [self.instances]

        self.files = Dictionary.get_value(function, AppKeys.files)
        if type(self.files) is str:
            self.files = [self.files]
        self.log_dir = Dictionary.get_value(function, AppKeys.func_log_dir)
        self.username = Configuration.peer_server_username
        self.password = Configuration.peer_server_root_password
        self.limit = str(Configuration.max_file_size)
        self.type_script_name = "file_type_check.bsh"
        self.type_script_path = Configuration.scripts_file_path + "/%s" % self.type_script_name
        self.size_script_name = "collect_files_size_limit_check.bsh"
        self.size_limit_script = Configuration.scripts_file_path + "/%s" % self.size_script_name

        # print trigger for startYAML
        self.print_trigger = True
        if Configuration.manual_startYamlFile is True:
            self.print_trigger = False

    @staticmethod
    def server_type():
        return 'peer servers'

    @staticmethod
    def file_type_check(cmd, server):
        output = str(server.execute_and_return(cmd)).splitlines(False)
        for each in output:
            if each == "type-file" or each == "type-directory" or each == "type-neither":
                return each
            else:
                continue

    @staticmethod
    def file_size_check(cmd, server):
        output = str(server.execute_and_return(cmd)).splitlines(False)
        output.pop(-1)
        return output

    def run(self):
        if Configuration.cloud_server is False:
            peer_server_success = []; peer_server_fail = []
            # find out all instances
            for instance in self.instances:
                if instance == 'svc_cluster':
                    self.instances.remove(instance)
                    self.instances += PeerServerFiles._get_clusters('svc_cluster')

                elif instance == 'db_cluster':
                    self.instances.remove(instance)
                    self.instances += PeerServerFiles._get_clusters('db_cluster')

                elif instance == 'scp_cluster':
                    self.instances.remove(instance)
                    self.instances += PeerServerFiles._get_clusters('scp_cluster')
                elif instance == 'all_clusters':
                    self.instances.remove(instance)
                    self.instances += PeerServerFiles._get_clusters(instance)

            if len(self.instances) != 0:
                Output.yellow("Collecting the following files:", print_trigger=self.print_trigger)
                Output.white('%s' % str(self.files), new_line=False, print_trigger=self.print_trigger)
                Logger.info("On Peer Servers: %s" % str(self.instances))
                Print.yellow("\nOn Peer Servers:", trigger=self.print_trigger)
                Print.white("%s" % str(self.instances), trigger=self.print_trigger)
            for peer_server in self.instances:
                not_exists_files = [];large_files = [];more_dir = [];successful_files = []
                server = PeerServer(peer_server, Configuration.peer_server_username, Configuration.peer_server_password,
                                    Configuration.peer_server_root_password)
                log_dir = FilePaths.join_path(self.log_dir, peer_server)
                addon_dir = log_dir
                Terminal.mkdir(addon_dir, True)
                Print.white("\nChecking connection on [%s]" % peer_server, trigger=self.print_trigger)
                if server.connect():
                    list_of_files_not_collected = []
                    for file in self.files:
                        self.type_script_name = "file_type_check.bsh"
                        self.type_script_path = Configuration.scripts_file_path + "/%s" % self.type_script_name
                        self.size_script_name = "collect_files_size_limit_check.bsh"
                        self.size_limit_script = Configuration.scripts_file_path + "/%s" % self.size_script_name
                        # copy files over
                        Terminal.copy(self.type_script_path, Configuration.storing_logs_dir+".LCSMetadata")
                        Terminal.copy(self.size_limit_script, Configuration.storing_logs_dir+".LCSMetadata")

                        type_location = Configuration.storing_logs_dir + ".LCSMetadata/" + self.type_script_name
                        size_location = Configuration.storing_logs_dir + ".LCSMetadata/" + self.size_script_name
                        # commands to execute checks
                        file_type_cmd = "bash %s %s" % (type_location, file)
                        command_to_exec = "bash %s %s %s" % (size_location, file, Configuration.max_file_size)
                        # Find file type
                        file_type = self.file_type_check(file_type_cmd, server)
                        if file_type == "type-directory" or file_type == "directory":
                            files_to_collect = []
                            # find info of files/directory
                            list_of_stuff = self.file_size_check(command_to_exec,server)
                            file_info_list = []
                            for each in list_of_stuff:
                                if "%" in each:
                                    file_info_list.append(each)
                            if any("TOO LARGE" in substring for substring in file_info_list) is True:
                                more_dir.append(file)
                            for each_file in file_info_list:
                                file_name = each_file.split("%", 1)[1]
                                if str(each_file).__contains__("TOO LARGE"):
                                    large_files.append(file_name)
                                else:
                                    files_to_collect.append(file_name)
                            files_to_collect = GlobalExclusion(files_to_collect).get_output_list()
                            for each_correct_file in files_to_collect:
                                refined_path = os.path.abspath(os.path.join(str(each_correct_file), os.pardir))
                                file_dir = addon_dir + refined_path
                                Terminal.system("sudo mkdir -p %s" % file_dir)
                                server.cp(each_correct_file, file_dir)
                                location = "%s/%s.gz" % (file_dir, os.path.basename(each_correct_file))
                                if FilePaths.is_file(location):
                                    successful_files.append(each_correct_file)
                                else:
                                    list_of_files_not_collected.append(each_correct_file)

                        elif file_type == "type-file" or file_type == "file":
                            # find info of files/directory
                            list_of_stuff = self.file_size_check(command_to_exec,server)
                            file_info_list = []
                            for each in list_of_stuff:
                                if "%" in each:
                                    file_info_list.append(each)
                            if file_info_list[0].__contains__("TOO LARGE"):
                                large_files.append(file)
                            else:
                                correct_output = GlobalExclusion(file).get_output_list()
                                if len(correct_output) != 0:
                                    for each_file in correct_output:
                                        refined_path = os.path.abspath(os.path.join(str(each_file), os.pardir))
                                        file_dir = addon_dir + refined_path
                                        Terminal.system("sudo mkdir -p %s" % file_dir)
                                        server.cp(file, file_dir)
                                        location = "%s/%s.gz" % (file_dir, os.path.basename(file))
                                        if FilePaths.is_file(location):
                                            successful_files.append(file)
                                        else:
                                            list_of_files_not_collected.append(file)
                        elif file_type == "type-neither" or file_type == "neither":
                            not_exists_files.append(file)
                        Terminal.rm(type_location)
                        Terminal.rm(size_location)
                    server.close()
                    if len(not_exists_files) == len(self.files):
                        peer_server_fail.append(peer_server)
                    else:
                        peer_server_success.append(peer_server)
                    if len(list_of_files_not_collected) == 0:
                        Output.green("\nAll Files Collected Successfully on [%s]" % peer_server)
                else:
                    peer_server_fail.append(peer_server)
                if len(large_files) != 0:
                    Output.yellow("\nUnable to collect All files on [%s]. Size Limit Exceed [%sMB]:" % (peer_server, str(Configuration.max_file_size)), print_trigger=self.print_trigger)
                    Logger.info("Files Too Large(Not Collected)" + str(large_files))
                if len(not_exists_files) != 0:
                    not_exists_files = list(dict.fromkeys(not_exists_files))
                    not_exists_files = str(not_exists_files).strip().strip("[]").replace("'", "")
                    Output.yellow("Unable to collect the following Files's:", print_trigger=self.print_trigger)
                    Output.white("[%s]" % not_exists_files, print_trigger=self.print_trigger,new_line=False)
                    Output.yellow("\nOn Peer Server:", new_line=False, print_trigger=self.print_trigger)
                    Output.white("[%s]" % str(peer_server), print_trigger=self.print_trigger)
                    Logger.info("Files Not Found" + str(not_exists_files))

            if len(peer_server_success) != 0:
                Output.green("\nSuccessfully collected Files from the following peer servers: ", print_trigger=self.print_trigger)
                Output.white(peer_server_success, print_trigger=self.print_trigger)
            if len(peer_server_fail) != 0:
                Output.red("\nUnable to collect Files from the following peer servers: ", print_trigger=self.print_trigger)
                Output.white(peer_server_fail, print_trigger=self.print_trigger)
        else:
            Output.yellow('Skipping Peer Server Collect Files Plugin', print_trigger=self.print_trigger)

    def login(self, peer_server):
        """
        :return: child of pexpect if connect is successful. Otherwise, None
        """
        if PeerServerController.ping_server(peer_server) is False:
            return None
        else:
            child = PeerServerController.connect_peer_server(self.username, peer_server)

            if not PeerServerController.login_peer_server(self.password, child):
                Output.red("Incorrect password(s) to connect to the peer server [%s]" % (peer_server), print_trigger=self.print_trigger)
                return None

            if not PeerServerController.use_root(self.password, child):
                Output.red("Incorrect root password :)", print_trigger=self.print_trigger)
                return None

            return child

    def check_for_extension(self, file_path,instance):
        if str(file_path).find("||") != -1:
            new_argument = str(file_path).split("||")[1]
            new_string = str(file_path).split("||")[0]
            if new_argument == "LATEST":
                command_to_exec = "ssh -i " + Configuration.vm_private_key + " cloud-user@" + instance + " ls -lart " + new_string + " | awk '{print $NF}' | tail -1 > /dev/null 2>&1"
                pipe = subprocess.Popen(command_to_exec, shell=True, stdout=subprocess.PIPE).stdout
                new_path = pipe.read()
                pipe.close()
                if new_path is not None:
                    new_path = new_path.strip()
                    return new_path
            else:
                Print.yellow("\nfile has prefix (||) but NOT extension", trigger=self.print_trigger)
                Print.yellow("File will not be tarred\n", trigger=self.print_trigger)
                return file_path
        else:
            return file_path

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
