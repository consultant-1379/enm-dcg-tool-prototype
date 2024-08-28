import os
import re
import sre_constants
import subprocess
import time

from libs.functions.collate_attach_files.ftp_file import FtpFiles
from libs.functions.commands.tools.peer_server.peer_server_controller import PeerServerController
from libs.functions.enm_cli.enm_cli_commands import EnmCliCommands
from libs.health_check.mounts import Mounts
from libs.logging.logger import Logger
from libs.utilities.data_structures.dictionary import Dictionary
from libs.utilities.file.file_reader import FileReader
from libs.utilities.system.file_paths import FilePaths
from libs.utilities.system.output import Output
from libs.utilities.system.print_text import Print
from libs.utilities.system.terminal import Terminal
from libs.utilities.system.timing import Timing
from libs.utilities.vms.global_search import GlobalSearch
from libs.variables.configuration import Configuration
from libs.variables.keys import AppKeys


class NetworkNodeMenu:

    def __init__(self, path):
        self.path = path
        self.file_path = path+"/"+Configuration.network_element_filename
        self.cli_output_file = Configuration.network_element_output
        self.list_of_lines = []
        self.stamp = "NetworkElement"
        self.list_of_lists = []
        self.check_something()
        self.output_path = "lcs/temp/network_output.txt"
        self.node_Type = "NodeType"
        self.nodeID = "NodeID"
        self.files_to_collect_list = []

    def check_something(self):
        if Configuration.netlog_collection_timeout <= 0:
            def_value = False
            Print.yellow("Netlog timeout cannot be negative or 0\nPlease Enter another value")
            while def_value is False:
                value = Terminal.input()
                try:
                    value = int(value)
                    if value > 0:
                        def_value = True
                    else:
                        Print.red("Netlog Value must be an integer > 0")
                except ValueError:
                    Print.red("Netlog Value must be an integer")

        if FilePaths.is_file(self.file_path):
            data = FileReader(self.file_path).get()
            data = Dictionary.get_value(data, AppKeys.functions)
            data = data[0]
            name = str(Dictionary.get_value(data, AppKeys.func_name)).lstrip().rstrip().replace(" ", "_")
            plugin = FilePaths.join_path(Configuration.storing_logs_dir, name)
            Dictionary.set_value(data, AppKeys.func_log_dir, plugin)
            Print.yellow("Please Wait. Retrieving Node List")
            if EnmCliCommands(data, app=False, config_stack=False, network=True).run() is False:
                Output.red("Network CLI Failed")
            else:
                # example_location = "/tmp/correct_output.txt"
                example_location = Configuration.network_element_output
                with open(example_location) as f:
                    if f.read().__contains__("0 instance(s)"):
                        Output.red("No nodes found")
                    else:
                        Output.green("Network CLI Succeeded")
                        with open(example_location) as f:
                            self.list_of_lines = f.read().splitlines(False)
                        while "" in self.list_of_lines:
                            self.list_of_lines.remove("")
                        # Terminal.rm(Configuration.network_element_output)
                        node_type_cmd = "cat %s | awk '{print $2}' | sort | uniq | grep -v neType | " \
                                        "grep -v instance | grep -v UserName | sort" % example_location
                        pipe = subprocess.Popen(node_type_cmd, shell=True, stdout=subprocess.PIPE).stdout
                        cmd_output = pipe.read().splitlines()
                        pipe.close()
                        while "" in cmd_output:
                            cmd_output.remove("")
                        if len(cmd_output) > 0:
                            self.list_of_lists.append(cmd_output)
                            if self.menu(self.list_of_lists, 1) is True:
                                return True
                            else:
                                return False
                        else:
                            Print.yellow("CLI Command Found no nodes on this server")

    def print_menu(self, input_list, page):
        if page == 3:
            alpha_list = input_list[page - 1]
        else:
            alpha_list = sorted(input_list[page - 1])
        col = Terminal.console_width()
        extension = self.remove_extension(alpha_list)
        menu_list = self.numberlist(extension)
        length_of_list = len(menu_list)
        if length_of_list != 0:
            os.system('clear')
            Print.green('#' * col)
            if page == 1:
                Print.yellow("Network Element Type Menu".center(col, ' '))
            elif page == 2:
                Print.yellow("Supported logs for [%s]".center(col, ' ') % self.node_Type)
            else:
                path = os.path.basename(self.path)
                Print.yellow((path + ' Menu').replace('_', ' ').upper().center(col, ' '))
            Print.green('#' * col)
            Print.blue('0. Back')
            print(menu_list)
            print ''
            Print.green('#' * col)
        return menu_list

    def menu(self, input_list, page):
        menu_list = self.print_menu(input_list, page)
        val = True
        if menu_list is False:
            Output.red('No Network Element Types could be found')
            return False
        while val is True:
            try:
                if loop is True:
                    menu_list = self.print_menu(input_list, page)
            except:
                pass
            Print.yellow("Enter Choice")
            num_input = Terminal.input('')
            if num_input == "":
                Print.red("value cannot be none")
                continue
            if num_input == '0':
                if page == 1:
                    Logger.info('User Pressed 0 to return to Dynamic Menu')
                    val = False
                else:
                    current_list = input_list[page - 1]
                    self.list_of_lists.remove(current_list)
                    page = page - 1
                    menu_list = self.print_menu(input_list, page)
            elif num_input in menu_list and num_input != '':
                try:
                    item = int(num_input) - 1
                    if page == 3:
                        alpha_list = input_list[page - 1]
                    else:
                        alpha_list = sorted(input_list[page - 1])
                    loop = False
                    nr_of_type = 0
                    for each in self.list_of_lines:
                        if str(each).endswith(alpha_list[item]):
                            nr_of_type = nr_of_type+1
                    while loop is False:
                        if page == 1:
                            self.node_Type = alpha_list[item]
                            correct_list = []
                            if nr_of_type <= 20:
                                for each in self.list_of_lines:
                                    if str(each).strip().endswith(str(alpha_list[item])):
                                        correct_list.append(str(each).rstrip(str(alpha_list[item])).strip())
                                self.list_of_lists.append(correct_list)
                                page = page + 1
                                menu_list = self.print_menu(input_list, page)
                                break
                            else:
                                Print.green("Node Type [%s], Total Nodes found [%s]" % (alpha_list[item], str(nr_of_type)))
                                Print.yellow('Please Enter exact NodeID or Wildcard Pattern, Type \"BACK\" for previous manu.')
                                keyword = Terminal.input('')
                                if keyword == "":
                                    Print.red('NodeID cannot be null.\n')
                                elif keyword == "BACK":
                                    loop = True
                                elif keyword.__contains__("?") or keyword.__contains__("*"):
                                    if self.process_wildcard_input(keyword) is False:
                                        Print.yellow("Incorrect Wildcard Syntax Try Again")
                                    else:
                                        Print.yellow("Detected Wildcard Input")
                                        tag = self.process_wildcard_input(keyword)
                                        for each in self.list_of_lines:
                                            if len(tag.findall(str(each))):
                                                if str(each).endswith(str(alpha_list[item])):
                                                    correct_list.append(str(each).rstrip(str(alpha_list[item])).strip())
                                        if len(correct_list) == 0:
                                            try:
                                                Print.red("No NodeID's matched with Wildcard for Node Type %s" % str(alpha_list[item]))
                                            except:
                                                Print.red("No NodeID's matched with Wildcard for Node Type %s" % keyword)
                                        elif len(correct_list) <= 20:
                                            self.list_of_lists.append(correct_list)
                                            page = page + 1
                                            menu_list = self.print_menu(input_list, page)
                                            break
                                        elif len(correct_list) > 20:
                                            Print.red("More than 20 Node ID Found (%s). Enter ID with Higher Accuracy" % len(correct_list))
                                else:
                                    for each in self.list_of_lines:
                                        if str(each).rstrip(str(alpha_list[item])).strip() == keyword:
                                            if str(each).endswith(str(alpha_list[item])):
                                                correct_list.append(str(each).rstrip(str(alpha_list[item])).strip())
                                    if len(correct_list) == 0:
                                        try:
                                            Print.red("No NodeID's matched for Node Type %s" % str(alpha_list[item]))
                                        except:
                                            Print.red("No NodeID's matched for Node Type %s" % keyword)

                                    elif len(correct_list) <= 1:
                                        self.list_of_lists.append(correct_list)
                                        page = page + 1
                                        menu_list = self.print_menu(input_list, page)
                                        break
                                    elif len(correct_list) > 1:
                                        Print.red("More than 1 Node ID Found (%s). Enter ID with Higher Accuracy or use Wildcard" % len(correct_list))
                        elif page == 2:
                            self.files_to_collect_list = []
                            self.nodeID = alpha_list[item]
                            nodeID = alpha_list[item]
                            cmd_list = ["netlog describe %s" % alpha_list[item]]
                            test_file_path = self.exec_cli_get_output(cmd_list)
                            with open(test_file_path) as f:
                                string = f.read()
                                f.close()
                            if string.__contains__("Supported log types"):
                                self.files_to_collect_list.append(test_file_path)
                                string = string.split("Supported log types: [")[1]
                                string = string.split("]")[0]
                                string = string.strip()
                                if string.__contains__(","):
                                    string = string.split(",")
                                else:
                                    string = [string.strip()]

                                while "" in string:
                                    string.remove("")

                                if len(string) == 0:
                                    Output.red("No logs can be ")
                                for each in string:
                                    change = each.strip()
                                    index = string.index(each)
                                    string[index] = change
                                string.append("ALL LOGS")
                                Print.white("Chose ONE of the options above")
                                self.list_of_lists.append(string)
                                page = page + 1
                                menu_list = self.print_menu(input_list, page)
                            else:
                                current_list = input_list[page - 1]
                                self.list_of_lists.remove(current_list)
                                page = page - 1
                                menu_list = self.print_menu(input_list, page)
                                Output.red("ENM does not support log collection for this node type [%s]" % self.node_Type)
                            break
                        elif page == 3:
                            list_of_paths = []
                            if alpha_list[item] != "ALL LOGS":
                                cmd_list = ["netlog upload %s %s" % (nodeID, alpha_list[item])]
                                check_command = "netlog status %s %s" % (nodeID, alpha_list[item])
                                message = "Uploading [%s] for [%s] \nPlease wait" % (alpha_list[item],self.nodeID)
                                list_of_logs = len([alpha_list[item]])
                                test_file_path = self.exec_cli_get_output(cmd_list, check_status=check_command, log_types=list_of_logs, message=message)
                            else:
                                cmd_list = ["netlog upload %s" % nodeID]
                                check_command = "netlog status %s" % nodeID
                                list_of_logs = len(alpha_list) - 1
                                message = "Uploading [ALL LOGS] for [%s] \nPlease wait" % self.nodeID
                                test_file_path = self.exec_cli_get_output(cmd_list, check_status=check_command, log_types=list_of_logs, message=message)
                            with open(test_file_path) as f:
                                string = f.read().splitlines(False)
                                f.close()
                            if string[-1] == "All logs ready for download":
                                self.files_to_collect_list.append(test_file_path)
                                Output.green("Requested Logs Ready For Download")
                            elif string[-1].__contains__("Timeout occurred"):
                                Output.yellow("Logs were not ready for upload by Timeout") ###### finished here ####
                            if string[-1] == "Some logs ready for download":
                                self.files_to_collect_list.append(test_file_path)
                                Output.green("Only logs which were successfully set up for upload will be downloaded")
                            var = "-%s-" % nodeID
                            for each in string:
                                if str(each).__contains__(var) and str(each).__contains__(".zip"):
                                    striped = each.split(",", 1)[0].strip()
                                    list_of_paths.append(striped)
                            if len(list_of_paths) == 0:
                                Output.yellow("No Files to Download")
                            else:
                                self.connect_collect(list_of_paths)
                                self.metadata()
                                return True
                            self.metadata()
                            return False
                        elif page > 3:
                            break
                except:
                    Print.red('Invalid input')
            else:
                Print.red('Invalid input')

    def connect_collect(self, list_of_files):
        list_of_vms = GlobalSearch("msnetlog").get_correct_list()
        if len(list_of_vms) == 0:
            Output.red("No [msnetlog] VM's available for file collection")
        else:
            netlog_dir = Configuration.storing_logs_dir+"Network_Element"
            if FilePaths.isdir(netlog_dir) is False:
                Terminal.mkdir(netlog_dir)
            collected = 0
            vm = list_of_vms[0]
            list_to_collect = []
            Logger.info("Collecting Files from [%s]" % vm)
            for each in list_of_files:
                find_path_command = "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null 2>/dev/null" \
                                    " -i %s %s@%s \"sudo find /ericsson/netlog/ -name %s\""\
                                    % (Configuration.vm_private_key, Configuration.vm_user_name, vm, each)

                pipe = subprocess.Popen(find_path_command, shell=True, stdout=subprocess.PIPE).stdout
                check_status = pipe.read()
                pipe.close()
                if check_status.strip() != "":
                    list_to_collect.append(check_status.strip())
            for each_file in list_to_collect:
                each_path = FilePaths.absolute_path(os.path.join(each_file,FilePaths.pardir()))
                out_dir = netlog_dir+each_path
                if FilePaths.isdir(out_dir) is False:
                    Terminal.mkdir(out_dir)
                cp_command = "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null 2>/dev/null" \
                             " -i %s %s@%s \"sudo /bin/cp -a -p --force %s %s\""\
                             % (Configuration.vm_private_key, Configuration.vm_user_name, vm, each_file, out_dir)
                pipe = subprocess.Popen(cp_command, shell=True, stdout=subprocess.PIPE)
                streamdata = pipe.communicate()[0]
                pipe.stdout.close()
                response = pipe.returncode
                if response == 0:
                    collected = collected + 1
            if collected == 0:
                Output.red("No Files Collected Successfully")
            elif collected == len(list_to_collect):
                Logger.debug("All Files Collected Successfully")
            else:
                Output.yellow("Some Files Collected Successfully")

    def metadata(self):
        if FilePaths.isdir(Configuration.storing_logs_dir+"/.LCSMetadata") is False:
            Terminal.mkdir(Configuration.storing_logs_dir+"/.LCSMetadata")
        from os import listdir
        from os.path import isfile, join
        onlyfiles = [f for f in listdir(Configuration.tmp_directory) if isfile(join(Configuration.tmp_directory, f))]
        for each in onlyfiles:
            if os.path.basename(each).startswith("network_cli_output"):
                full_path = Configuration.tmp_directory + "/%s" % each
                Terminal.mv(full_path, Configuration.storing_logs_dir+"/.LCSMetadata/")
        self.collect_files()

    def collect_files(self):
        debug_function_name = "NetworkElement_%s_%s" % (self.node_Type,self.nodeID)
        report_file_prefix = 'lcs_report_'
        report_gz_file_name = "%s%s%s_%s.tar.gz" % (Configuration.report_output_dir, report_file_prefix, re.sub(" ", "_", debug_function_name), str(Configuration.storing_logs_dir).rsplit("/", 2)[1])
        metadata = Configuration.storing_logs_dir + ".LCSMetadata"
        log_dir = Configuration.storing_logs_dir
        Output.yellow('Archiving and Compressing files, please wait...')
        # 1. Execute the /opt/ericsson/enminst/bin/enm_version.sh and store the output in the log file directory to ensure it gets included in the report.tar file.

        # If the directory /enm/enm_error/ doesn't exist create it using the following command
        Terminal.mkdir(log_dir, True)

        if (Configuration.cloud_server):
            enm_version = Configuration.cloud_server_enm_version
        else:
            enm_version = Configuration.physical_server_enm_version
            # run sed script
            sed_cmd = "bash " + Configuration.scripts_file_path + "/cp_sed_file.bsh " + "\"" + \
                      str(log_dir).split("end")[0] + "\""
            Terminal.system(sed_cmd)

        # To store the output in /enm/enm_error run the following command
        Terminal.system("%s > %s 2>/dev/null" % (enm_version, FilePaths.join_path(log_dir, "enm_ver.out")))

        # Add the tool logs to the final report
        log_file_location = Configuration.default_path + "/log/debug.log"
        if FilePaths.is_file(log_file_location):
            Terminal.cp(log_file_location, metadata)

        # 2. To tar and zip up the report for attachment to the Customer Support Request use the following command:
        Terminal.tar_gzip(Configuration.storing_logs_dir, report_gz_file_name)

        # end of programme until now
        Configuration.end_time = time.strftime('%H%M%S')
        # duration
        duration = int(Configuration.end_time) - int(Configuration.start_time)

        # get compressed file size
        file = Terminal.filesize(report_gz_file_name)
        size = float(file) / 1000

        run_command = subprocess.Popen(
            'logger -p local2.info -t DDCDATA['"%s"'] {"Duration":'"%s"',"LogFileSize":'"%s"',"YML_FILE_NAME":'"%s"',"OutputFileName":'"%s"'}' % (
            Configuration.tag_name, str(duration), float(round(size, 1)), debug_function_name,
            report_gz_file_name), shell=True)
        run_command.wait()
        # 3. Write a reproduction scenario (step by step how to reproduce the problem) to include in the Customer Support Request.

        # 4. To clean up the directory use the following command
        Terminal.rm(Configuration.storing_logs_dir, superuser=True)
        Output.green('%s debug logs Collected.' % debug_function_name)

        # To upload file to ftp server
        if Configuration.Automatic_upload == True:
            if Configuration.ftp_url != 'None' or None and Configuration.ftp_username != 'None' or None and Configuration.ftp_password != None:
                if FtpFiles(report_gz_file_name).run() == True:
                    Output.green('\n%s has been successfully uploaded to ftp server ' % os.path.basename(
                        report_gz_file_name))
                    Output.green('\nCopy/Paste the following text into JIRA/CSR, if required...\n')
                    Output.green('###############################################################')
                    Output.green('Hostname: %s' % Terminal.hostname())
                    Output.green('Date/Time: %s' % Timing.strftime())
                    Output.green('LCS version: %s' % self.version())
                    if Configuration.DDP_URL is not None:
                        Output.green('DDP URL: %s' % Configuration.DDP_URL)
                    if Configuration.ticket_number is True and Configuration.ticket_number is not None:
                        Output.green('Ticket Number: %s' % Configuration.ticket_dir[0])
                        Output.green('FTP URL: [ ftp://%s/lcs_reports/%s/%s/%s ]' % (
                        Configuration.ftp_url, Terminal.hostname(), Configuration.ticket_dir[0],
                        os.path.basename(report_gz_file_name)))
                        Output.green(
                            '\nThe follwoing command can be used to download the logs from FTP server to local machine for analysis purpose.')
                        Output.green('# wget ftp://%s/lcs_reports/%s/%s/%s' % (
                        Configuration.ftp_url, Terminal.hostname(), Configuration.ticket_dir[0],
                        os.path.basename(report_gz_file_name)))
                        Output.green('# tar xvfz %s\n' % os.path.basename(report_gz_file_name))
                        Output.green('###############################################################')
                    else:
                        Output.green('FTP URL: [ ftp://%s/lcs_reports/%s/%s ]' % (
                        Configuration.ftp_url, Terminal.hostname(), os.path.basename(report_gz_file_name)))
                        Output.green(
                            '\nThe follwoing command can be used to download the logs from FTP server to local machine for analysis purpose.')
                        Output.green('# wget ftp://%s/lcs_reports/%s/%s' % (
                        Configuration.ftp_url, Terminal.hostname(), os.path.basename(report_gz_file_name)))
                        Output.green('# tar xvfz <PATH_OF_LCS_REPORT>')
                        Output.green('###############################################################')

                    if Configuration.Delete_file_after_upload is True:
                        if Configuration.ticket_number is True and Configuration.ticket_number is not None:
                            Terminal.system('sudo rm -rf %s' % (
                                FilePaths.join_path(Configuration.storing_logs_dir, report_gz_file_name)))
                            Terminal.system(
                                'sudo rm -rf %s/%s' % (Configuration.storing_logs_dir, Configuration.ticket_dir[0]))
                        else:
                            Terminal.system('sudo rm -rf %s' % (
                                FilePaths.join_path(Configuration.storing_logs_dir, report_gz_file_name)))
                    else:
                        self.output_file(report_gz_file_name)
                else:
                    self.output_file(report_gz_file_name)
            else:
                Logger.warning('No url found to upload Log report')
                self.output_file(report_gz_file_name)
        else:
            self.output_file(report_gz_file_name)

        if Configuration.report_output_dir == "/ericsson/enm/dumps/lcs/" and Configuration.report_mount_umount and Configuration.cloud_server:
            Mounts.umount_dumps()

    def output_file(self, report_gz_file_name):
        Output.green('\n%s' % report_gz_file_name)
        Output.green('\nCopy/Paste the following text into JIRA/CSR, if required...\n')
        Output.green('###############################################################')
        Output.green('Hostname: %s' % Terminal.hostname())
        Output.green('Date/Time: %s' % Timing.strftime())
        Output.green('LCS version: %s' % self.version())
        if Configuration.DDP_URL is not None:
            Output.green('DDP URL: %s' % Configuration.DDP_URL)
        if Configuration.ticket_number is True and Configuration.ticket_number is not None:
            Output.green('Ticket Number: %s' % Configuration.ticket_dir[0])
        Output.green('Log file: %s' % report_gz_file_name)
        Output.green('\nThe following command can be used to un-tar the log file for analysis purpose')
        Output.green('# tar xvfz <PATH_OF_LCS_REPORT>')
        Output.green('###############################################################\n')

    @staticmethod
    def version():
        version_check_cmd = "rpm -qi lcs | egrep \"^Version \" | awk -F ':' '{print $2}' | awk '{print $1}'"
        version_check = subprocess.Popen(version_check_cmd, shell=True, stdout=subprocess.PIPE).stdout
        return version_check.read()

    @staticmethod
    def process_wildcard_input(keyword):
        keyword = keyword.replace("*", ".*").replace("?", ".")
        try:
            rex = re.compile(keyword)
            return rex
        except sre_constants.error:
            return False

    @staticmethod
    def further_process(left, word, right):
        pass

    def exec_cli_get_output(self, list_of_commands, check_status=None, log_types=None,message=False):
        list_of_commands = list_of_commands
        check_status = check_status
        timeout = Configuration.netlog_collection_timeout
        time_stamp = Timing.strftime()
        Terminal.chmod(644, Configuration.scripts_file_path+"/network_cli_script.py")
        output_file_path = Configuration.directory_to_check_disk_usage + "/lcs"
        output_file = os.path.join(output_file_path, "network_cli_output_%s.txt" % time_stamp)
        Terminal.touch(output_file)
        Terminal.chmod(777, output_file)
        network_script_path = Configuration.scripts_file_path+"/network_cli_script.py"
        Terminal.copy(network_script_path, Configuration.directory_to_check_disk_usage)

        string_to_execute = "python '"+Configuration.directory_to_check_disk_usage + "/network_cli_script.py'"
        new_list_of_commands = list()
        # adding enm commands as arguments to string
        if check_status is None:
            string_to_execute += (" '%s' '%s' " % (str(check_status), str(timeout)))
        else:
            string_to_execute += (" '%s' '%s' '%s'" % (str(check_status), str(timeout), str(log_types)))
        for each in list_of_commands:
            new_string = " '" + each + "'"
            string_to_execute += new_string
            new_list_of_commands.append(new_string)
        string_to_execute += " >> " + output_file + " 2>&1"
        import pexpect
        try:
            if message is not False:
                Output.white(message)
            PeerServerController().cli_pexpect_run(string_to_execute, output_file)
        except pexpect.EOF and pexpect.TIMEOUT:
            Print.red("Error Occured with ENM CLI commands execution")
            Configuration.enm_cli_check = False
            return False
        Configuration.enm_cli_check = False
        final_file = Configuration.tmp_directory + "/network_cli_output_%s.txt" % time_stamp
        Terminal.mv(output_file, final_file)
        return final_file

    @staticmethod
    def remove_extension(yaml_list):
        no_extension = []
        for each in yaml_list:
            if each.endswith('.yml'):
                no_extension.append(each.replace('.yml', ''))
            else:
                no_extension.append(each)
        return no_extension

    @staticmethod
    def numberlist(lists):
        new = ('\n'.join(['. '.join((str(name).zfill(1), num)) for name, num in enumerate(lists, 1)]))
        return new
