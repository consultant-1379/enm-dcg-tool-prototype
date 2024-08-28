import base64
import os
import sys
import subprocess
import time
import pexpect
import socket
from libs.health_check.mounts import Mounts
from libs.logging.logger import Logger
from libs.start_up.cloud_server import CloudServer
from libs.utilities.system.file_paths import FilePaths
from libs.utilities.system.output import Output
from libs.utilities.system.terminal import Terminal
from libs.utilities.vms.global_search import GlobalSearch
from libs.variables.configuration import Configuration


class SilentSetup:

    def __init__(self):
        CloudServer()
        if socket.gethostname() == 'cloud-ms-1':
            Output.yellow('Detecting that the LCS Tool is being executed for the first time')
            Output.red('silent setup is not supported on vAPP, please perform the manual setup ')
            sys.exit(0)
        else:
            if os.path.isfile(Configuration.default_path + '/etc/.silent_setup_url'):
                Output.yellow('Detecting that the LCS Tool is being executed for the first time')
                Output.yellow('Performing silent setup, Please Wait!')
                f = open(Configuration.default_path + '/etc/.silent_setup_url', 'r')
                url = f.readlines()
                self.get_file(url[0])

    def get_data(self, data, silent_file):
        if Configuration.cloud_server is False:
            Terminal.rm(silent_file)
            val_list = []
            for line in data:
                if line != '':
                    new = (line.split('=>', 1)[1])
                    val_list.append(new.replace(' ', ''))

            vm_private = self.decrypt(val_list[0])
            if val_list[1] is None:
                enm_cli_username = '\n'
            else:
                enm_cli_username = val_list[1]

            if val_list[2] is None:
                enm_cli_password = '\n'
            else:
                enm_cli_password = self.decrypt(val_list[2])
            if val_list[3] is None:
                enm_cli_role = '\n'
            else:
                enm_cli_role = val_list[3]
            if val_list[4] is None:
                ssh_username = '\n'
            else:
                ssh_username = val_list[4]
            ssh_password = self.decrypt(val_list[5])
            ssh_root_password = self.decrypt(val_list[6])
            ddp_url =  val_list[7]
            if val_list[8] is None:
                output_directory = '\n'
            else:
                output_directory = val_list[8]
            if val_list[9] == '':
                ftp_url = 'None'
                ftp_answer = 'No'
            else:
                ftp_url = val_list[9]
                ftp_answer = 'Yes'
            if val_list[10] == '':
                ftp_user = 'None'
            else:
                ftp_user = val_list[10]
            if val_list[11] == '':
                ftp_pass = 'None'
            else:
                ftp_pass = self.decrypt(val_list[11])
            answer = 'Yes'

            if self.check_dir_path_is_global(output_directory, vm_private) is False:
                Output.red("The Output Directory path provided in %s does not seem to be globally available to VM's"
                           % silent_file)
                self.setup_statement()
                sys.exit(0)
            else:
                SilentSetup.run_setup(vm_private, enm_cli_username, enm_cli_password, enm_cli_role, ssh_username, ssh_password, ssh_root_password, ddp_url, output_directory, answer, ftp_url, ftp_user, ftp_pass, ftp_answer)
        else:
            Terminal.rm(silent_file)
            val_list = []
            for line in data:
                if line != '':
                    new = (line.split('=>', 1)[1])
                    val_list.append(new.replace(' ', ''))

            vm_private = self.decrypt(val_list[0])
            if val_list[1] is None:
                enm_cli_username = '\n'
            else:
                enm_cli_username = val_list[1]
            if val_list[2] is None:
                enm_cli_password = '\n'
            else:
                enm_cli_password = self.decrypt(val_list[2])
            if val_list[3] is None:
                enm_cli_role = '\n'
            else:
                enm_cli_role = val_list[3]
            ddp_url = val_list[4]
            if val_list[5] is None:
                output_directory = '\n'
            else:
                output_directory = val_list[5]
            answer = 'Yes'
            if self.check_dir_path_is_global(output_directory, vm_private) is False:
                Output.yellow(output_directory)
                Output.red("The Output Directory path provided in %s does not seem to be globally available to VM's"
                           % silent_file)
                self.setup_statement()
                sys.exit(0)
            else:
                if val_list[6] == '':
                    ftp_url = 'None'
                    ftp_answer = 'No'
                else:
                    ftp_url = val_list[6]
                    ftp_answer = 'Yes'
                if val_list[7] == '':
                    ftp_user = 'None'
                else:
                    ftp_user = val_list[7]
                if val_list[8] == '':
                    ftp_pass = 'None'
                else:
                    ftp_pass = self.decrypt(val_list[8])
                SilentSetup.run_setup_cloud(vm_private, enm_cli_username, enm_cli_password, enm_cli_role,
                                            ddp_url, output_directory, answer, ftp_url, ftp_user, ftp_pass, ftp_answer)
    def get_file(self, link):
        if self.check_url(link):
            if Configuration.cloud_server is False:
                os.popen("sudo wget 'ftp://anonymous:anonymous@" + self.get_ip(link) + self.check_for_hostname()
                         + "_lcs_silent_setup_physical' >/dev/null 2>&1 ")
                silent_file = self.check_for_hostname() + '_lcs_silent_setup_physical'
                if os.path.isfile(silent_file):
                    if os.path.getsize(silent_file) > 0:
                        Logger.info('Performing silent setup with %s' % silent_file)
                        Output.yellow('Performing silent setup with %s' % silent_file)
                        self.read_file(silent_file)
                    else:
                        Terminal.rm(silent_file)
                        Logger.info(self.check_for_hostname() + '_lcs_silent_setup_physical seems to be empty')
                        Logger.info('Trying silent setup with generic_answer_lcs_silent_setup_physical')
                        os.popen("sudo wget 'ftp://anonymous:anonymous@" + self.get_ip(
                            link) + "/generic_answer_lcs_silent_setup_physical'  >/dev/null 2>&1")
                        silent_file = 'generic_answer_lcs_silent_setup_physical'
                        if os.path.isfile(silent_file) is True:
                            if os.path.getsize(silent_file) > 0:
                                Logger.info('Performing silent setup with %s' % silent_file)
                                Output.yellow('Performing silent setup with %s' % silent_file)
                                self.read_file(silent_file)
                            else:
                                Terminal.rm(silent_file)
                                Output.red(silent_file + ' seems to be empty')
                                self.setup_statement()
                                sys.exit(0)
                        else:
                            Logger.info(
                                'Cannot find %s, make sure at least one of these files exist and have correct '
                                'name to complete silent setup' % silent_file)
                            self.setup_statement()
                            Terminal.rm(silent_file)
                            sys.exit(0)
                else:
                    Logger.info('Cannot find ' + self.check_for_hostname() +
                               '_lcs_silent_setup_physical , trying generic_answer_lcs_silent_setup_physical')
                    os.popen("sudo wget 'ftp://anonymous:anonymous@" + self.get_ip(link)
                             + "/generic_answer_lcs_silent_setup_physical' >/dev/null 2>&1")
                    silent_file = 'generic_answer_lcs_silent_setup_physical'
                    if os.path.isfile(silent_file) is True:
                        if os.path.getsize(silent_file) > 0:
                            Logger.info('Performing silent setup with %s' % silent_file)
                            Output.yellow('Performing silent setup with %s' % silent_file)
                            self.read_file(silent_file)
                        else:
                            Terminal.rm(silent_file)
                            Output.red(silent_file + ' seems to be empty')
                            self.setup_statement()
                            sys.exit(0)
                    else:
                        Logger.info('Cannot find %s, make sure at least one of these files exist and have correct name to complete silent setup' % silent_file)
                        self.setup_statement()
                        Terminal.rm(silent_file)
                        sys.exit(0)
            else:
                # cloud
                os.popen("sudo wget 'ftp://anonymous:anonymous@" + self.get_ip(link) + "/" + self.check_for_hostname()
                         + "_lcs_silent_setup_cloud' >/dev/null 2>&1")
                silent_file = self.check_for_hostname() + '_lcs_silent_setup_cloud'
                if os.path.isfile(silent_file):
                    if os.path.getsize(silent_file) > 0:
                        Logger.info('Performing silent setup with %s' % silent_file)
                        Output.yellow('Performing silent setup with %s' % silent_file)
                        self.read_file(silent_file)
                    else:
                        Output.red(silent_file + ' seems to be empty')
                        Terminal.rm(silent_file)
                        Logger.info('Trying generic_answer_lcs_silent_setup_cloud')
                        os.popen("sudo wget 'ftp://anonymous:anonymous@" + self.get_ip(link)
                                 + "/generic_answer_lcs_silent_setup_cloud' >/dev/null 2>&1")
                        silent_file = 'generic_answer_lcs_silent_setup_cloud'
                        if os.path.isfile(silent_file):
                            if os.path.getsize(silent_file) > 0:
                                Logger.info('Performing silent setup with %s' % silent_file)
                                Output.yellow('Performing silent setup with %s' % silent_file)
                                self.read_file(silent_file)
                            else:
                                Logger.info(silent_file + ' seems to be empty')
                                self.setup_statement()
                                sys.exit(0)
                        else:
                            Logger.info(
                                'Cannot find %s, make sure at least one of these files exist and have correct name '
                                'to complete silent setup' % silent_file)
                            self.setup_statement()
                            Terminal.rm(silent_file)
                            sys.exit(0)
                else:
                    Logger.info('Cannot find ' + self.check_for_hostname()
                               + '_lcs_silent_setup_cloud, trying generic_answer_lcs_silent_setup_cloud')
                    os.popen("sudo wget 'ftp://anonymous:anonymous@" + self.get_ip(link)
                             + "/generic_answer_lcs_silent_setup_cloud'  >/dev/null 2>&1")
                    silent_file = 'generic_answer_lcs_silent_setup_cloud'
                    if os.path.isfile(silent_file) is True:
                        if os.path.getsize(silent_file) > 0:
                            Logger.info('Performing silent setup with %s' % silent_file)
                            Output.yellow('Performing silent setup with %s' % silent_file)
                            self.read_file(silent_file)
                        else:
                            Terminal.rm(silent_file)
                            Output.red(silent_file + ' seems to be empty')
                            self.setup_statement()
                            sys.exit(0)
                    else:
                        Logger.info('Cannot find %s, make sure at least one of these files exist and have correct name '
                                   'to complete silent setup' % silent_file)
                        self.setup_statement()
                        Terminal.rm(silent_file)
                        sys.exit(0)
        else:
            Output.red('%s in ' + Configuration.default_path + '/etc/.silent_setup is incorrect' % link)
            self.setup_statement()
            sys.exit(0)

    def read_file(self, setup_file):
        changed = setup_file.split('\n')
        if os.path.isfile(str(changed[0])) is True:
            f = open(changed[0], 'r')
            data = f.read().splitlines(False)
            if self.check_files(data) is True:
                self.get_data(data, changed[0])
            else:
                Output.red('Silent setup File format is incorrect or details provided are incorrect')
                self.setup_statement()
                Terminal.rm(changed[0])
                sys.exit()
        Terminal.rm(changed[0])

    @staticmethod
    def run_setup(vm_private, enm_cli_username, enm_cli_password, enm_cli_role, ssh_username, ssh_password,
                  ssh_root_password, ddp_url, output_directory, answer, ftp_url, ftp_user, ftp_pass, ftp_answer):
        try:
            if ftp_answer == 'Yes':
                Terminal.system('sudo touch .silent_setup_true')
                child = pexpect.spawn('sudo python ' + Configuration.default_path
                                      + '/bin/log_collection_service.py --setup')
                child.expect('VM Private Key:')
                child.sendline(vm_private)
                child.expect('Username:')
                child.sendline(enm_cli_username)
                child.expect('Password:')
                child.sendline(enm_cli_password)
                child.expect('Role:')
                child.sendline(enm_cli_role)
                child.expect('Username:')
                child.sendline(ssh_username)
                child.expect('Password:')
                child.sendline(ssh_password)
                child.expect('Root Password:')
                child.sendline(ssh_root_password)
                child.expect('DDP URL:')
                child.sendline(ddp_url)
                child.expect('Output Directory for Logs:')
                child.sendline(output_directory)
                time.sleep(5)
                child.expect = "[Yes}.*"
                child.sendline(ftp_answer)
                child.expect = 'FTP URL:'
                child.sendline(ftp_url)
                child.expect = 'FTP username:'
                child.sendline(ftp_user)
                child.expect = 'Password:'
                child.sendline(ftp_pass)
                child.expect = "You have just provided the following information,Are you sure.*"
                child.sendline(answer)
                child.expect = "Exiting Log Collection Service"
                Output.green('Silent setup complete')
                child.close()
                Terminal.system('sudo rm .silent_setup_true')
                return True
            else:
                Terminal.system('sudo touch .silent_setup_true')
                child = pexpect.spawn('sudo python ' + Configuration.default_path
                                      + '/bin/log_collection_service.py --setup')
                child.expect('VM Private Key:')
                child.sendline(vm_private)
                child.expect('Username:')
                child.sendline(enm_cli_username)
                child.expect('Password:')
                child.sendline(enm_cli_password)
                child.expect('Role:')
                child.sendline(enm_cli_role)
                child.expect('Username:')
                child.sendline(ssh_username)
                child.expect('Password:')
                child.sendline(ssh_password)
                child.expect('Root Password:')
                child.sendline(ssh_root_password)
                child.expect('DDP URL:')
                child.sendline(ddp_url)
                child.expect('Output Directory for Logs:')
                child.sendline(output_directory)
                time.sleep(5)
                child.expect = "[Yes}.*"
                child.sendline(ftp_answer)
                child.expect = "You have just provided the following information,Are you sure.*"
                child.sendline(answer)
                child.expect = "Exiting Log Collection Service"
                Output.green('Silent setup complete')
                child.close()
                Terminal.system('sudo rm .silent_setup_true')
                return True
        except:
            Output.red("ERROR in silent setup")
            Logger.error("Silent setup Failed")

    @staticmethod
    def run_setup_cloud(vm_private, enm_cli_username, enm_cli_password, enm_cli_role, ddp_url, output_directory,
                        answer, ftp_url, ftp_user, ftp_pass, ftp_answer):
        try:
            if ftp_answer == 'Yes':
                Terminal.system('sudo touch .silent_setup_true')
                child = pexpect.spawn('sudo python ' + Configuration.default_path
                                      + '/bin/log_collection_service.py --setup')
                child.sendline(ftp_answer)
                child.expect('VM Private Key:')
                child.sendline(vm_private)
                child.expect('Username:')
                child.sendline(enm_cli_username)
                child.expect('Password:')
                child.sendline(enm_cli_password)
                child.expect('Role:')
                child.sendline(enm_cli_role)
                child.expect('DDP URL:')
                child.sendline(ddp_url)
                child.expect('Output Directory for Logs:')
                child.sendline(output_directory)
                time.sleep(5)
                child.expect = "[Yes}.*"
                child.sendline(ftp_answer)
                child.expect = 'FTP URL:'
                child.sendline(ftp_url)
                child.expect = 'FTP username:'
                child.sendline(ftp_user)
                child.expect = 'Password:'
                child.sendline(ftp_pass)
                child.expect = "You have just provided the following information,Are you sure.*"
                child.sendline(answer)
                child.expect = "Finished the LCS setup."
                Output.green('Silent setup complete')
                child.close()
                Terminal.system('sudo rm .silent_setup_true')
                return True
            else:
                Terminal.system('sudo touch .silent_setup_true')
                child = pexpect.spawn('sudo python ' + Configuration.default_path
                                      + '/bin/log_collection_service.py --setup')
                child.sendline(ftp_answer)
                child.expect('VM Private Key:')
                child.sendline(vm_private)
                child.expect('Username:')
                child.sendline(enm_cli_username)
                child.expect('Password:')
                child.sendline(enm_cli_password)
                child.expect('Role:')
                child.sendline(enm_cli_role)
                child.expect('DDP URL:')
                child.sendline(ddp_url)
                child.expect('Output Directory for Logs:')
                child.sendline(output_directory)
                time.sleep(5)
                child.expect = "[Yes}.*"
                child.sendline(ftp_answer)
                child.expect = "You have just provided the following information,Are you sure.*"
                child.sendline(answer)
                child.expect = "Finished the LCS setup."
                Output.green('Silent setup complete')
                child.close()
                Terminal.system('sudo rm .silent_setup_true')
                return True
        except:
            Output.red("ERROR in silent setup")
            Logger.error("Silent setup Failed")

    @staticmethod
    def check_for_hostname():
        return socket.gethostname()

    @staticmethod
    def get_ip(url):
        url = url.replace('http://', '').replace('ftp://', '').strip()
        return url

    @staticmethod
    def setup_statement():
        Output.red('Configuration for silent setup not found, please perform the manual setup')

    @staticmethod
    def check_url(url):
        link = url.split('/')
        result = Terminal.system('ping -c 1 ' + link[2] + ' >/dev/null 2>&1')
        if result == 0:
            return True
        return False

    def check_files(self, setup_file):
        if Configuration.cloud_server is False:
            items = ['COMMON_VM_KEY', 'COMMON_CLI_USERNAME', 'COMMON_CLI_PASSWD', 'COMMON_CLI_ROLE',
                     'PHYCIAL_SSH_USER', 'PHYCIAL_SSH_PASSWD', 'PHYCIAL_ROOT_PASSED', 'DDP_URL', 'COMMON_OUTPUT_DIR', 'FTP_URL=', 'FTP_USERNAME=', 'FTP_PASSWORD=']
            me = []
            for each in setup_file:
                me.append(each.split('=>'))
            if os.path.isfile(self.decrypt(me[0][1].replace(' ', ''))) is True and len(me[5][1].replace(' ', '')) > 0 and len(me[6][1].replace(' ', '')) > 0:
                for each in me:
                    for item in items:
                        if item == each[0]:
                          return True
            return False
        else:
            items = ['COMMON_VM_KEY', 'COMMON_CLI_USERNAME', 'COMMON_CLI_PASSWD',
                     'COMMON_CLI_ROLE', 'DDP_URL', 'COMMON_OUTPUT_DIR', 'FTP_URL=', 'FTP_USERNAME=', 'FTP_PASSWORD=']
            me = []
            for each in setup_file:
                me.append(each.split('=>'))
            if os.path.isfile(self.decrypt(me[0][1].replace(' ', ''))):
                for each in me:
                    for item in items:
                        if item == each[0]:
                            return True

    @staticmethod
    def check_dir_path_is_global(path, temp_key):
        CloudServer()
        Configuration.default_path = FilePaths.absolute_path(os.path.join(Configuration.default_main_file,
                                                                          FilePaths.pardir(), FilePaths.pardir()))
        if Configuration.cloud_server and Configuration.report_mount_umount:
            Mounts.mount_dumps()
        path_to_check_file = (Configuration.default_path + "/etc/.random_srv")
        if FilePaths.is_file(path_to_check_file) is False:
            Terminal.system("touch %s" % path_to_check_file)
            Terminal.system("printf 'impexpserv\nsaid\nitservices\nsecserv\nfmserv' >> %s" % path_to_check_file)
        f = open(path_to_check_file, "r")
        services = f.read().splitlines()
        instances = GlobalSearch(services).get_correct_list()
        check_file_path = FilePaths.join_path(path, ".check_globle_dir")
        if FilePaths.is_file(check_file_path):
            Terminal.rm(check_file_path)
        Terminal.touch(check_file_path)
        total = len(instances)
        count = 0
        for each_instance in instances:
            check_cmd = "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" \
                        " -i " + temp_key + " cloud-user@" + str(each_instance) + \
                        " 2> /dev/null [ -f \"" + str(check_file_path) + "\" ]" \
                                                                         " && echo \"FileExist\" || echo \"NotExist\""
            pipe = subprocess.Popen(check_cmd, shell=True, stdout=subprocess.PIPE).stdout
            check_status = pipe.read()
            pipe.close()
            check_status = check_status.splitlines()
            for each in check_status:
                if each.__contains__("FileExist"):
                    count = count + 1
        Terminal.rm(check_file_path)
        if count < total / 2:
            return False
        if Configuration.cloud_server and Configuration.report_mount_umount:
            Mounts.umount_dumps()

    @staticmethod
    def decrypt(encrypted):
        return base64.b64decode(str(encrypted))
