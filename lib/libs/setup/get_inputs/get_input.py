import signal
import subprocess
import sys, tty, termios
import os

from libs.lcs_error import LCSError
from libs.logging.logger import Logger
from libs.utilities.data_structures.encryption import Encryption
from libs.utilities.system.file_paths import FilePaths
from libs.utilities.system.output import Output
from libs.utilities.system.pexpect_child import PexpectChild
from libs.utilities.system.terminal import Terminal
from libs.utilities.vms.global_search import GlobalSearch
from libs.variables.configuration import Configuration
import pexpect


class GetInput():

    def __init__(self, parameter):
        self.parameter = parameter

    def get(self):
        parameter = self.parameter
        # construct the prompting message
        prompt_message = parameter.prompt
        if (parameter.default != None):
            prompt_message += ' [%s]: ' % (parameter.default)
        stamp = None
        if parameter.name == 'report_output_dir':
            stamp = "lcs/"

        if parameter.name == 'peer_server_username' or parameter.name == 'report_output_dir':
            Configuration.cli_blank = False

        if Configuration.cli_blank == True or Configuration.ftp_no_upload == True:
            pass
        else:
            Output.white(prompt_message, setup=True)

        # get the input
        displaying = (parameter.displaying_name + ": ")

        while True:
            # check for Ctrl-c press
            signal.signal(signal.SIGINT, self._dynamic_menu_ctrlC_handler)
            # check for Ctrl-Z press
            signal.signal(signal.SIGTSTP, self._dynamic_menu_ctrlC_handler)
            if Configuration.ftp_no_upload == True:
                break
            if (parameter.confidential and parameter.name != 'vm_private_key' and parameter.name != 'cli_username'):
                if os.path.isfile('.silent_setup_true') == False:
                    if Configuration.cli_blank == True:
                        input = ''
                    else:
                        key = ""
                        sys.stdout.write('Password: ')
                        while True:
                            ch = self.pass_to_asterisks()
                            num = len(key) + 1
                            if ch == '\r':
                                break
                            elif ch == '\x08' or ch == '\x7f':
                                new_num = num - 1
                                key = key[:-1]
                                if new_num > 0:
                                    sys.stdout.write('\b \b')
                            elif ch == '\x03':
                                Terminal.exit(0)
                            else:
                                key += ch
                                sys.stdout.write('*')
                        input = key
                        print
                else:
                        input = Terminal.noecho_input(displaying)
            else:
                if Configuration.cli_blank == True:
                    input = ''
                else:
                    input = Terminal.input(displaying,setup=True)

            # if no input for cli username name, skip password and role
            if os.path.exists('.silent_setup_true') == False:
                if parameter.name == 'cli_username':
                    if input == '':
                        Configuration.cli_blank = True
                        Configuration.enm_cli_dont_display = True
                    else:
                        Configuration.enm_username_check = input
                if parameter.name == 'cli_password':
                    if input == '':
                        Configuration.cli_blank = True
                        Configuration.enm_cli_dont_display = True
                    else:
                        if self.check_enm_cli_details(input) is False:
                            Configuration.enm_cli_pass_usr_wrong = True

            if parameter.name == 'cli_password' and input == '\r':
                Configuration.enm_cli_pass_usr_wrong = True
            # check if empty and dont print
            if (input == ''):
                input = parameter.default
                if input != None:
                    if Configuration.cli_blank == True:
                        pass
                    else:
                        Output.green("Accepting Default", setup=True)

            if parameter.name == 'DDP_URL' and input != '':
                if self.check_for_ddp_url(input) is not True:
                    Configuration.DDP_URL_WRONG = True

            if parameter.name == 'ftp_url':
                if self._check_ftp_url(input) is False:
                    Configuration.url_check = False

            if parameter.name == "report_output_dir":
                input = FilePaths.join_path(input, stamp)

            if (GetInput.check_input_validity(self, input, parameter)) and Configuration.url_check == None and Configuration.enm_cli_pass_usr_wrong is not True and Configuration.DDP_URL_WRONG is not True:
                # process of valid input
                if (parameter.confidential):
                    input = Encryption.encrypt(input)
                parameter.input = input
                if parameter.name == 'vm_private_key':
                    Configuration.temp_key = input
                break
            elif Configuration.enm_cli_pass_usr_wrong is True:
                Output.yellow(
                    "Password provided for ENM user [%s] not correct, Enter the password again." % Configuration.enm_username_check,
                    setup=True)
                Configuration.enm_cli_pass_usr_wrong = False

            elif Configuration.DDP_URL_WRONG is True:
                Output.yellow("Please provide a DDP URL.", setup=True)
                Configuration.DDP_URL_WRONG = False
            else:
                if Configuration.report_output_dir_response is False and Configuration.enm_cli_pass_usr_wrong is False:
                    if stamp is not None:
                        if str(input).endswith(stamp):
                            count = str(input).count(stamp)
                            input = str(input).split(stamp, count)[0]
                    Output.yellow("Invalid input '%s'. Please provide a valid value." % input, setup=True)
                    Configuration.url_check = None
                elif Configuration.url_check is False and Configuration.enm_cli_pass_usr_wrong is False:
                    Output.yellow("URL '%s' does not exist. Please provide a valid a URL." % input, setup=True)
                    Configuration.url_check = None
                else:
                    Output.yellow("Please provide a different value.", setup=True)
        print ''
        return parameter

    def check_input_validity(self, input, parameter):
        # 1. the input cannot be an empty string
        if (input == None):
            return False

        # 2. check if file path exists
        if (parameter.check_file):
            if not (FilePaths.is_file(input)):
                return False

        # 3. Check if the directory exists
        if (parameter.check_dir):
            if not (FilePaths.isdir(input)):
                if FilePaths.isdir(str(input.rsplit("/", 2)[0])):
                    pass
                else:
                    Output.yellow("Path does not exist %s: Please create this path before you continue" % str(
                        input.rsplit("/", 2)[0]), setup=True)
                    return False
            if Configuration.cloud_server is True:
                if input == "/ericsson/enm/dumps/lcs/" and Configuration.report_mount_umount:
                    # Mount Check and Assertion
                    check_mount = "mount | grep hcdumps"
                    pipe = subprocess.Popen(check_mount, shell=True, stdout=subprocess.PIPE).stdout
                    check_out = pipe.read()
                    pipe.close()
                    if check_out is None or check_out == "":
                        if FilePaths.isdir("/ericsson/enm/dumps/") is False:
                            Terminal.system("sudo mkdir -p /ericsson/enm/dumps/")
                        Terminal.system("sudo mount nfshcdumps:/ericsson/hcdumps /ericsson/enm/dumps/")
                        pipe2 = subprocess.Popen(check_mount, shell=True, stdout=subprocess.PIPE).stdout
                        check_out2 = pipe2.read()
                        pipe.close()
                        if check_out2 is None or check_out2 == "":
                            raise LCSError('\nError, Could not Mount dumps file System')
                    if FilePaths.isdir("/ericsson/enm/dumps/lcs") is False:
                        Terminal.system("sudo mkdir -p /ericsson/enm/dumps/lcs")
                    unmount_cmd = "sudo umount /ericsson/enm/dumps"
                    pipe = subprocess.Popen(unmount_cmd, shell=True, stdout=subprocess.PIPE).stdout
                    unmount_out = pipe.read()
                    pipe.close()
                    if unmount_out == "" or unmount_out is None:
                        pass
                    else:
                        Output.red("Un-mounting operation of dumps directory issues occurred", setup=True)
                    if self.upload_check() == True:
                        return True
                    else:
                        Configuration.ftp_no_upload = True
                else:
                    path = str(input.rsplit("/", 2)[0])
                    if self.check_global_path(path) is False:
                        return False
                    else:
                        Terminal.system("sudo mkdir -p " + input + ">> /dev/null")
                        if self.upload_check() == True:
                            return True
                        else:
                            Configuration.ftp_no_upload = True
            else:
                path = str(input.rsplit("/", 2)[0])
                if self.check_global_path(path) is False:
                    return False
                else:
                    Terminal.system("sudo mkdir -p " + input + ">> /dev/null")
                    if self.upload_check() == True:
                        return True
                    else:
                        Configuration.ftp_no_upload = True

            if not (input[-1] == '/'):
                return False
        if os.path.exists('/opt/ericsson/lcs/etc/.upgrade_conf') == True:
            Terminal.rm('/opt/ericsson/lcs/etc/.upgrade_conf')
        if parameter.name != "report_output_dir" or parameter.name != "vm_private_key" or parameter.name != "cli_role":
            if input.__contains__(" "):
                Output.yellow("This variable cannot contain spaces please try again")
                return False
        return True

    @staticmethod
    def check_global_path(path):
        check_dir = os.path.realpath(__file__)
        path_to_check_file = os.path.abspath(os.path.join(check_dir, os.pardir, os.pardir, os.pardir, os.pardir, os.pardir))
        path_to_check_file = (path_to_check_file + "/etc/.random_srv")
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
                        " -i " + Encryption.decrypt(Configuration.temp_key) + " cloud-user@" + str(each_instance) + \
                        " 2> /dev/null [ -f \"" + str(check_file_path) + "\" ]" \
                        " && echo \"FileExist\" || echo \"NotExist\" > /dev/null 2>&1"
            pipe = subprocess.Popen(check_cmd, shell=True, stdout=subprocess.PIPE).stdout
            check_status = pipe.read()
            pipe.close()
            check_status = check_status.splitlines()
            for each in check_status:
                if each.__contains__("FileExist"):
                    count = count + 1
        Terminal.rm(check_file_path)
        if count < total / 2:
            Output.white("\n[Note] This path does not seem to be globally available")
            return False

    def pass_to_asterisks(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    def _check_ftp_url(self, url):
        if os.path.exists('.silent_setup_true') == True:
            pass
        else:
            try:
                if 'http' or 'ftp' in url:
                    temp = url.split('/')
                    result = os.system('ping -c 1 ' + str(temp[2]) + ' > /dev/null 2>&1')
                    if result == 0:
                        return True
                    else:
                        return False
            except:
                result = os.system('ping -c 1 ' + str(url) + ' > /dev/null 2>&1')
                if result == 0:
                    return True
                else:
                    return False

    def upload_check(self):
        yes = ['Yes', 'Y']
        no = ['No', 'N']
        Output.white('\nDo you want this tool to automatically upload trouble reports to FTP server', setup=True)
        while True:
            Output.yellow('[Yes] to confirm or [No] to cancel: ', setup=True)
            choice = Terminal.input('')
            if choice in yes:
                Configuration.upload_choice = True
                return True
            elif choice in no:
                Configuration.upload_choice = False
                return False
            else:
                Output.red('Invaild input', setup=True)

    @staticmethod
    def check_for_ddp_url(input):
        if input.__contains__('http://') or input.__contains__('https://'):
            return True
        return False

    @staticmethod
    def check_enm_cli_details(input):
        list_of_scripting_vms = GlobalSearch("scripting").get_correct_list()
        for each in list_of_scripting_vms:
            try:
                child = PexpectChild("ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null %s@%s"
                                     % (Configuration.enm_username_check, each))
                child.expect("%s@%s's password:" % (Configuration.enm_username_check, each), timeout=5)
                child.sendline(input)
                expected = "Last login:.*"
                exception = "Permission denied.*"
                result = child.expect([expected, exception], timeout=5)
                if result == 0:
                    return True
                elif result == 1:
                    child.close()
                    return False

            except pexpect.EOF and pexpect.TIMEOUT:
                return False

    def _dynamic_menu_ctrlC_handler(self, sig, frame):
        Logger.error('Control C used to exit setup before setup was complete')
        Terminal.exit(0)
