import ntpath
import os
import re
import time
import subprocess

from libs.executors.menu_executor.dynamic_menu import DynamicMenu
from libs.functions.collate_attach_files.ftp_file import FtpFiles
from libs.functions.function_superclass import FunctionSuperclass
from libs.health_check.check_nr_of_files import CheckNrOfFiles
from libs.health_check.mounts import Mounts
from libs.logging.logger import Logger
from libs.utilities.data_structures.dictionary import Dictionary
from libs.utilities.system.file_paths import FilePaths
from libs.utilities.system.output import Output
from libs.utilities.system.terminal import Terminal
from libs.utilities.system.timing import Timing
from libs.variables.keys import AppKeys
from libs.variables.configuration import Configuration


class CollateAttachFiles(FunctionSuperclass):
    report_file_prefix = 'lcs_report_'

    def __init__(self, function, app, config_stack, ctrl_c=False):
        """
                This class follows the document: ENM Data Collection Guidelines

        1.3. Collate and Attach Files
            Context Description
                Use the following steps to wrap up and attach the required files to the Customer Support Request.
            Prerequisites
                Access to the Management Server
                Access to the Service Cluster Nodes
                Access to EMP (Cloud)
            Expected Result
                A set of relevant log files to attach to the Customer Support Request.
        :param function:
        :param app: an object of the class ConfigItem
        :param config_stack: A stack of objects of the class ConfigItem
        """

        if (not FunctionSuperclass.check_name_equal(function[AppKeys.func_name], CollateAttachFiles.func_name())):
            Terminal.exception("This function was wrongly passed in CollateAttachFiles")
        try:
            # get the YAML file name
            self.debug_function_name = config_stack.second_peek().get_config_name()
        except:
            self.debug_function_name = "Unknown Use Case"
        self.ctrl_c = ctrl_c
        self.config_stack = config_stack
        self.size = self.config_stack.size()

        # example of file name is lcs_report_alarm_api_20190128-553472.tar.gz
        if Configuration.Jboss_log_not_collected is True:
            self.report_gz_file_name = "INCOMPLETE___%s%s%s_%s.tar.gz" % (Configuration.report_output_dir, CollateAttachFiles.report_file_prefix, re.sub(" ", "_", self.debug_function_name), str(Configuration.storing_logs_dir).rsplit("/", 2)[1])
        else:
            self.report_gz_file_name = "%s%s%s_%s.tar.gz" % (Configuration.report_output_dir, CollateAttachFiles.report_file_prefix, re.sub(" ", "_", self.debug_function_name), str(Configuration.storing_logs_dir).rsplit("/", 2)[1])

        self.log_dir = Dictionary.get_value(function, AppKeys.func_log_dir, default=Configuration.storing_logs_dir)
        self.metadata = Configuration.storing_logs_dir + ".LCSMetadata"
        self.ver = self.version()
        self.ver = self.ver.rstrip()

    @staticmethod
    def func_name():
        return "Collate and Attach Files"

    def run(self):
        Output.yellow('Archiving and Compressing files, please wait...')
        # 1. Execute the /opt/ericsson/enminst/bin/enm_version.sh and store the output in the log file directory to ensure it gets included in the report.tar file.

        # If the directory /enm/enm_error/ doesn't exist create it using the following command
        Terminal.mkdir(self.log_dir, True)

        if (Configuration.cloud_server):
            enm_version = Configuration.cloud_server_enm_version
        else:
            enm_version = Configuration.physical_server_enm_version
            # run sed script
            sed_cmd = "bash " + Configuration.scripts_file_path + "/cp_sed_file.bsh "+"\""+str(self.log_dir).split("end")[0] + "\""
            Terminal.system(sed_cmd)

        # To store the output in /enm/enm_error run the following command
        Terminal.system("%s > %s 2>/dev/null" % (enm_version, FilePaths.join_path(self.log_dir, "enm_ver.out")))

        # Add the tool logs to the final report
        Terminal.cp(FilePaths.join_path(Configuration.log_file_location, "debug.log"), self.metadata)

        # 2. To tar and zip up the report for attachment to the Customer Support Request use the following command:
        Terminal.tar_gzip(Configuration.storing_logs_dir, self.report_gz_file_name)

        # end of programme until now
        Configuration.end_time = time.strftime('%H%M%S')
        time.sleep(10)
        # duration
        duration = int(Configuration.end_time) - int(Configuration.start_time)

        # get compressed file size
        file = Terminal.filesize(self.report_gz_file_name)
        size = float(file) /1000


        run_command = subprocess.Popen('''logger -p local2.info -t DDCDATA[%s] %s { '"Duration"':%s,'"LogFileSizeKB"':%s,'"YmlFileName"':%s.yml,'"OutputFileName"':%s,'"Version"':%s }''' %(Configuration.tag_name,Configuration.tag_name,str(duration),int(round(size,1)),self.debug_function_name,self.report_gz_file_name, self.ver),shell=True)
        run_command.wait()

        run_command = subprocess.Popen('''logger -p local2.info -t DDCDATA[%s] MR.EXECUTION {'"MR"':'"105 65-0334/56103"'}''' % (Configuration.tag_name), shell=True)
        #logger - p local2.info - t DDCDATA[LogCollectionService:] MR.EXECUTION {"MR": "105 65-0334/56103"}
        run_command.wait()

        # 3. Write a reproduction scenario (step by step how to reproduce the problem) to include in the Customer Support Request.

        # 4. To clean up the directory use the following command
        Terminal.rm(Configuration.storing_logs_dir, superuser=True)
        Output.green('%s debug logs Collected.' % self.debug_function_name)

        # To upload file to ftp server
        if Configuration.Automatic_upload == True:
            if Configuration.ftp_url != 'None' or None and Configuration.ftp_username != 'None' or None and Configuration.ftp_password != None:
                if FtpFiles(self.report_gz_file_name).run() == True:
                    Output.green('\n%s has been successfully uploaded to ftp server ' % os.path.basename(self.report_gz_file_name))
                    Output.green('\nCopy/Paste the following text into JIRA/CSR, if required...\n')
                    Output.green('###############################################################')
                    Output.green('Hostname: %s' % Terminal.hostname())
                    Output.green('Date/Time: %s' % Timing.strftime())
                    Output.green('LCS version: %s' % self.version())
                    if Configuration.DDP_URL is not None:
                        Output.green('DDP URL: %s' % Configuration.DDP_URL)
                    if Configuration.ticket_number is True and Configuration.ticket_number is not None:
                        Output.green('Ticket Number: %s' % Configuration.ticket_dir[0])
                        Output.green('FTP URL: [ ftp://%s/lcs_reports/%s/%s/%s ]' % (Configuration.ftp_url, Terminal.hostname(), Configuration.ticket_dir[0], os.path.basename(self.report_gz_file_name)))
                        Output.green('\nThe follwoing command can be used to download the logs from FTP server to local machine for analysis purpose.')
                        Output.green('# wget ftp://%s/lcs_reports/%s/%s/%s' % (Configuration.ftp_url, Terminal.hostname(), Configuration.ticket_dir[0], os.path.basename(self.report_gz_file_name)))
                        Output.green('# tar xvfz %s\n' % os.path.basename(self.report_gz_file_name))
                        Output.green('###############################################################')
                    else:
                        Output.green('FTP URL: [ ftp://%s/lcs_reports/%s/%s ]' % (Configuration.ftp_url, Terminal.hostname(), os.path.basename(self.report_gz_file_name)))
                        Output.green('\nThe follwoing command can be used to download the logs from FTP server to local machine for analysis purpose.')
                        Output.green('# wget ftp://%s/lcs_reports/%s/%s' % (Configuration.ftp_url, Terminal.hostname(), os.path.basename(self.report_gz_file_name)))
                        Output.green('# tar xvfz <PATH_OF_LCS_REPORT>')
                        Output.green('###############################################################')

                    if Configuration.Delete_file_after_upload is True:
                        if Configuration.ticket_number is True and Configuration.ticket_number is not None:
                            Terminal.system('sudo rm -R %s --force' % (FilePaths.join_path(Configuration.storing_logs_dir, self.report_gz_file_name)))
                            Terminal.system('sudo rm -R %s/%s --force' % (Configuration.storing_logs_dir, Configuration.ticket_dir[0]))
                        else:
                            Terminal.system('sudo rm -R %s --force' % (FilePaths.join_path(Configuration.storing_logs_dir, self.report_gz_file_name)))
                    else:
                        self.output_file()
                else:
                    self.output_file()
            else:
                Logger.warning('No url found to upload Log report')
                self.output_file()
        else:
            self.output_file()


        if Configuration.report_output_dir == "/ericsson/enm/dumps/lcs/" and Configuration.report_mount_umount and Configuration.cloud_server:
            Mounts.umount_dumps()
        #
        # if Configuration.cloud_server is True:
        #     Mounts.umount_gp()

        Terminal.rm('/tmp/Log_tool_running')
        # checks if the second item in the stack exists, and if does check if its type is menu
        for each in range(self.size, -1, -1):
            if self.ctrl_c is True:
                CheckNrOfFiles()
                break
        if type(Configuration.dynamic_menu_path) == list:
            menu_path = Configuration.dynamic_menu_path[0]
        else:
            menu_path = Configuration.dynamic_menu_path
        Configuration.plugin_count = 0
        if menu_path is not None:
            CheckNrOfFiles()
            if os.path.exists('/tmp/.CtrlC') is False:
                Terminal.any_input()
                Configuration.jboss_debug = True
                Configuration.JBoss_ans_true = False
                DynamicMenu(Configuration.menu_next_list)

        # if (parameter.check_dir):
        #     if not (FilePaths.isdir(input)):
        #         if FilePaths.isdir(str(input.rsplit("/",2)[0])):
        #             pass
        #         else:
        #             Output.yellow("Path does not exist %s: Please create this path before you continue" % str(input.rsplit("/",2)[0]), setup=True)
        #             return False
        #         path = str(input.rsplit("/", 2)[0])
        #         if self.check_global_path(path) is False:
        #             return False
        #         else:
        #             Terminal.system("sudo mkdir -p " + input + ">> /dev/null")
        #             return True
        #
        #     if not (input[-1] == '/'):
        #         return False
        # if os.path.exists('/opt/ericsson/lcs/etc/.upgrade_conf') == True:
        #     Terminal.rm('/opt/ericsson/lcs/etc/.upgrade_conf')
        # return True

    def output_file(self):
        Output.green('\n%s' % self.report_gz_file_name)
        Output.green('\nCopy/Paste the following text into JIRA/CSR, if required...\n')
        Output.green('###############################################################')
        Output.green('Hostname: %s' % Terminal.hostname())
        Output.green('Date/Time: %s' % Timing.strftime())
        Output.green('LCS version: %s' % self.version())
        if Configuration.DDP_URL is not None:
            Output.green('DDP URL: %s' % Configuration.DDP_URL)
        if Configuration.ticket_number is True and Configuration.ticket_number is not None:
            Output.green('Ticket Number: %s' % Configuration.ticket_dir[0])
        Output.green('Log file: %s' % self.report_gz_file_name)
        Output.green('\nThe following command can be used to un-tar the log file for analysis purpose')
        Output.green('# tar xvfz <PATH_OF_LCS_REPORT>')
        Output.green('###############################################################\n')

    @staticmethod
    def version():
        version_check_cmd = "rpm -qi lcs | egrep \"^Version \" | awk -F ':' '{print $2}' | awk '{print $1}'"
        version_check = subprocess.Popen(version_check_cmd, shell=True, stdout=subprocess.PIPE).stdout
        return version_check.read()

