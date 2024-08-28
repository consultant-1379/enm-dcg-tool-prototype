import os
import re
import time
import subprocess

from libs.executors.menu_executor.network_node_menu import NetworkNodeMenu
from libs.functions.collate_attach_files.ftp_file import FtpFiles
from libs.health_check.mounts import Mounts
from libs.logging.logger import Logger
from libs.utilities.system.file_paths import FilePaths
from libs.utilities.system.output import Output
from libs.utilities.system.print_text import Print
from libs.utilities.system.terminal import Terminal
from libs.utilities.system.timing import Timing
from libs.variables.configuration import Configuration


class NetSim:

    def __init__(self):
        self.col = Terminal.console_width()
        self.line_number = 20
        line_list = self.get_list()
        self.menu_display(line_list)

    def menu_display(self, line_list):
        new_list = ('\n'.join(['. '.join((str(name).zfill(1), num)) for name, num in enumerate(line_list, 1)]))
        menu_lists = new_list.split('\n')
        if len(menu_lists) % len(line_list) != 0:
            menu_lists.append(" ")

        l1 = menu_lists[0:self.line_number]
        l2 = menu_lists[self.line_number:self.line_number * 2]
        l3 = menu_lists[self.line_number * 2: self.line_number * 3]
        os.system('clear')
        Print.green('#' * self.col)
        if len(self.original_list) > 60 and Configuration.netsim_page_num == 1:
            Print.yellow(('Netsim Menu page 1/2').center(self.col))
        elif Configuration.netsim_page_num == 2:
            Print.yellow(('Netsim Menu page 2/2').center(self.col))
        else:
            Print.yellow(('Netsim Menu').center(self.col))
        Print.green('#' * self.col)
        if len(menu_lists) < 10:
            Print.blue('0. Back')
            for key in zip(l1):
                print '%-32s ' % key
        elif len(menu_lists) < 20:
            Print.blue('0. Back')
            for key, value in zip(l1, l2):
                print '%-32s %-32s' % (key, value)
        elif len(menu_lists) > 20:
            if Configuration.netsim_page_num is 1 and len(self.original_list) > 60:
                Print.blue('0. Back', new_line=False), Print.blue('\t\t\t\t\t\t\t  61. Next Page')

            for key, value, pair in zip(l1, l2, l3):
                print '%-32s %-32s %-32s' % (key, value, pair)

        print ''
        Print.green('#' * self.col)
        while True:
            Print.yellow('Password less SSH access MUST be configure to login to netsim(s). ')
            Print.yellow('Enter choice: ')
            ans = Terminal.input('')
            if ans.isdigit():
                if ans == '0':
                    if Configuration.netsim_page_num is 1:
                        Logger.info('User Pressed 0 to return to Dynamic Menu')
                        from libs.executors.menu_executor.dynamic_menu import DynamicMenu
                        DynamicMenu(Configuration.default_path + '/etc')
                    else:
                        Configuration.netsim_page_num = Configuration.netsim_page_num - 1
                        NetSim()
                elif ans == '61' or int(ans) == 61 and Configuration.netsim_page_num == 1:
                    Configuration.netsim_page_num = 2
                    NetSim()
                elif ans is '' or type(int(ans)) is str:
                    print ('invalid entry')
                else:
                    ans = int(ans)
                    if type(ans) is int:
                        try:
                            if self.ping_netsim(line_list[int(ans) - 1]) is True:
                                break
                            else:
                                Print.red('Netsim node not accessible')
                        except:
                            Print.red('invalid entry')
                    else:
                        Print.red('invalid entry')
            else:
                Print.red('invalid entry')

    def get_list(self):
        line_list = []
        with open('/var/ericsson/ddc_data/config/server.txt', 'r') as f:
            for line in f:
                if 'WORKLOAD' not in str(line):
                    new = line.split('=')
                    line_list.append(new[0].strip())
            try:
                line_list.remove('')
            except:
                pass
        self.original_list = line_list
        if len(line_list) > 60:
            if Configuration.netsim_page_num is 2:
                try:
                    line_list.remove('')
                except:
                    pass
                return line_list[60:]
            else:
                try:
                    line_list.remove('')
                except:
                    pass
                return line_list[:60]
        else:
            try:
                line_list.remove('')
            except:
                pass
            return line_list

    def ping_netsim(self, netsim_name):
        result = Terminal.system('ping -c 1 %s >/dev/null 2>&1' % netsim_name)
        if result == 0:
            self.run_command(netsim_name)
        else:
            return False

    def run_command(self, netsim_name):
        command = '/netsim/inst/logtool'
        Output.yellow('Collecting Netsims on %s' % netsim_name)
        Configuration.netsim_stamp = Timing.strftime()
        directory = Configuration.report_output_dir + Configuration.netsim_stamp
        Terminal.mkdir(directory + '/netsim_%s/' % netsim_name)
        output_file = Configuration.report_output_dir + Configuration.netsim_stamp + '/netsim_%s/%s_output' \
                      % (netsim_name, netsim_name)
        Terminal.system('ssh -X netsim@%s "%s" > %s' % (netsim_name, command, output_file))
        Output.green('collection of netsim complete')
        self.collect_files(directory, netsim_name)

    def collect_files(self, Output_dir, node_type):
        debug_function_name = "Netsims_%s" % node_type
        report_file_prefix = 'lcs_report_'
        report_gz_file_name = "%s%s%s_%s.tar.gz" % (
        Configuration.report_output_dir, report_file_prefix, re.sub(" ", "_", debug_function_name),
        str(Output_dir).rsplit("/", 2)[1])
        metadata = Output_dir + "/.LCSMetadata/"
        Terminal.mkdir(metadata)
        log_dir = metadata
        Output.yellow('\nArchiving and Compressing files, please wait...')
        # 1. Execute the /opt/ericsson/enminst/bin/enm_version.sh and store the output in the log file
        # directory to ensure it gets included in the report.tar file.

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
        Terminal.tar_gzip(Output_dir, report_gz_file_name)

        # end of programme until now
        Configuration.end_time = time.strftime('%H%M%S')
        # duration
        duration = int(Configuration.end_time) - int(Configuration.start_time)

        # get compressed file size
        file = Terminal.filesize(report_gz_file_name)
        size = float(file) / 1000

        run_command = subprocess.Popen('logger -p local2.info -t DDCDATA['"%s"'] {"Duration":'"%s"','
                                       '"LogFileSize":'"%s"',"YML_FILE_NAME":'"%s"',"OutputFileName":'"%s"'}' % (
                Configuration.tag_name, str(duration), float(round(size, 1)), debug_function_name,
                report_gz_file_name), shell=True)
        run_command.wait()
        # 3. Write a reproduction scenario (step by step how to reproduce the problem) to include in the Customer Support Request.

        # 4. To clean up the directory use the following command
        Terminal.rm(Configuration.storing_logs_dir, superuser=True)
        Output.green('%s debug logs Collected.' % debug_function_name)

        # To upload file to ftp server
        if Configuration.Automatic_upload is True:
            if Configuration.ftp_url != 'None' or None and Configuration.ftp_username != 'None' \
                    or None and Configuration.ftp_password is not None:
                if FtpFiles(report_gz_file_name).run() is True:
                    Output.green('\n%s has been successfully uploaded to ftp server ' % os.path.basename(
                        report_gz_file_name))
                    Output.green('\nCopy/Paste the following text into JIRA/CSR, if required...\n')
                    Output.green('###############################################################')
                    Output.green('Hostname: %s' % Terminal.hostname())
                    Output.green('Date/Time: %s' % Timing.strftime())
                    Output.green('LCS version: %s' % NetworkNodeMenu.version())
                    if Configuration.DDP_URL is not None:
                        Output.green('DDP URL: %s' % Configuration.DDP_URL)
                    if Configuration.ticket_number is True and Configuration.ticket_number is not None:
                        Output.green('Ticket Number: %s' % Configuration.ticket_dir[0])
                        Output.green('FTP URL: [ ftp://%s/lcs_reports/%s/%s/%s ]' % (
                            Configuration.ftp_url, Terminal.hostname(), Configuration.ticket_dir[0],
                            os.path.basename(report_gz_file_name)))
                        Output.green(
                            '\nThe follwoing command can be used to download the logs from FTP '
                            'server to local machine for analysis purpose.')
                        Output.green('# wget ftp://%s/lcs_reports/%s/%s/%s' % (
                            Configuration.ftp_url, Terminal.hostname(), Configuration.ticket_dir[0],
                            os.path.basename(report_gz_file_name)))
                        Output.green('# tar xvfz %s\n' % os.path.basename(report_gz_file_name))
                        Output.green('###############################################################')
                    else:
                        Output.green('FTP URL: [ ftp://%s/lcs_reports/%s/%s ]' % (
                            Configuration.ftp_url, Terminal.hostname(), os.path.basename(report_gz_file_name)))
                        Output.green(
                            '\nThe follwoing command can be used to download the logs '
                            'from FTP server to local machine for analysis purpose.')
                        Output.green('# wget ftp://%s/lcs_reports/%s/%s' % (
                            Configuration.ftp_url, Terminal.hostname(), os.path.basename(report_gz_file_name)))
                        Output.green('# tar xvfz <PATH_OF_LCS_REPORT>')
                        Output.green('###############################################################')

                    if Configuration.Delete_file_after_upload is True:
                        if Configuration.ticket_number is True and Configuration.ticket_number is not None:
                            Terminal.system('sudo rm -R %s --force' % (
                                FilePaths.join_path(Configuration.storing_logs_dir, report_gz_file_name)))
                            Terminal.system(
                                'sudo rm -R %s/%s --force' % (Configuration.storing_logs_dir, Configuration.ticket_dir[0]))
                        else:
                            Terminal.system('sudo rm -R %s --force' % (
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

        if Configuration.report_output_dir == "/ericsson/enm/dumps/lcs/" and Configuration.report_mount_umount \
                and Configuration.cloud_server:
            Mounts.umount_dumps()
        Terminal.any_input()
        NetSim()

    @staticmethod
    def output_file(report_gz_file_name):
        Output.green('\n%s' % report_gz_file_name)
        Output.green('\nCopy/Paste the following text into JIRA/CSR, if required...\n')
        Output.green('###############################################################')
        Output.green('Hostname: %s' % Terminal.hostname())
        Output.green('Date/Time: %s' % Timing.strftime())
        Output.green('LCS version: %s' % NetworkNodeMenu.version())
        if Configuration.DDP_URL is not None:
            Output.green('DDP URL: %s' % Configuration.DDP_URL)
        if Configuration.ticket_number is True and Configuration.ticket_number is not None:
            Output.green('Ticket Number: %s' % Configuration.ticket_dir[0])
        Output.green('Log file: %s' % report_gz_file_name)
        Output.green('\nThe following command can be used to un-tar the log file for analysis purpose')
        Output.green('# tar xvfz <PATH_OF_LCS_REPORT>')
        Output.green('###############################################################\n')
