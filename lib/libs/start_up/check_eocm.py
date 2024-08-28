import os

from libs.start_up.check_user_eocm import CheckUserEocm
from libs.utilities.system.file_paths import FilePaths
from libs.utilities.system.terminal import Terminal
from libs.variables.configuration import Configuration


class CheckEocm:

    def __init__(self):
        if os.path.exists('/ericsson/tor/data/global.properties') is False:
            Configuration.EOCM = True
            self.run_path()
            lcs_conf_path = Configuration.default_path + '/etc/'
            os.system('sudo chown %s:%s %s' % (CheckUserEocm.user(), CheckUserEocm.group_id(), lcs_conf_path))
            if os.path.exists(Configuration.default_path + '/etc/lcs.conf') is False:
                with open(lcs_conf_path + 'lcs.conf', 'w') as f:
                    f.write('# LCS configuration file\n')
                    f.write('\n# The shared directory to put all the lcs log files. This directory is shared between the MS server and the cluster server.')
                    f.write('\nreport_output_dir: /tmp/lcs/\n')
                    f.write('\n# If the usage in percent(%) of the file system is greater this limit, the tool cannot be run until the user cleans up the file system.')
                    f.write('\nfile_system_max_usage: 90\n')
                    f.write('\n# The username for EOCM.')
                    f.write('\nusername: osadm\n')
                    f.write('\n# Max number of old report copies allowed')
                    f.write('\nmax_number_of_reports: 10\n')
                    f.write('\n# Max time allocated for peer server commands to execute before timeout occurs(in seconds)')
                    f.write('\npeer_server_command_timeout: 1800\n')
                    f.write("\n# Maximum time in seconds for JBoss to reproduce the issue before disabling the loggers")
                    f.write('\nJBoss_maximum_time: 3600\n')
                    f.write('\n# Max File size limit(MB)')
                    f.write('\nmax_file_size: 500\n')
                    f.write('\n# This variable specifies if the logs are automatically uploaded in FTP #(True/False) NOTE: [DO NOT EDIT THIS PARAMETER. TO CHANGE THIS PARAMETER RUN --SETUP]')
                    f.write('\nAutomatic_upload: True\n')
                    f.write('\n# This variable specifies if the user wants to delete the logs in report_output_dir after it is automatically uploaded to FTP server (True/False)')
                    f.write('\nDelete_file_after_upload: True\n')
                    f.write('\n# This variable specifies if the user wants to enable automatic cleanup of the report_output_dir directory (True/False)')
                    f.write('\nAuto_clean: False\n')
                    f.write('\n# This variable specifies the number of days before files are removed from the report_output_dir')
                    f.write('\nDuration: 31\n')
                    f.write('\n# This is the link for the DDP data')
                    f.write('\nDDP_URL: \n')
                    f.write('\n# ftp_upload_url')
                    f.write('\nftp_url: ftp.athtem.eei.ericsson.se\n')
                    f.write('\n# ftp_url_username')
                    f.write('\nftp_username: anonymous\n')
                    f.write('\n# ftp_url_password')
                    f.write('\nftp_password: anonymous\n')

    def run_path(self):
        Configuration.default_path = FilePaths.absolute_path(os.path.join(Configuration.default_main_file,
                                                                          FilePaths.pardir(), FilePaths.pardir()))