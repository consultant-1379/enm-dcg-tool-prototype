import base64
import os
import signal
import socket
import subprocess
import sys
import tty
from ftplib import FTP
import termios
import readline
import time


class EncryptFile:

    def __init__(self):
        f = open('/opt/ericsson/lcs/etc/.silent_setup_url', 'r')
        self.url_in_file = f.readlines()
        self.cloud = None
        self.cli_username = ''
        self.cli_password = ''
        self.cli_role = ''
        self.ftp_url = ''
        self.ftp_user = ''
        self.ftp_pass = ''
        self.main_menu()

    def main_menu(self):
        # check for Ctrl-c press
        signal.signal(signal.SIGINT, self._dynamic_menu_ctrlc_handler)
        # check for Ctrl-Z press
        signal.signal(signal.SIGTSTP, self._dynamic_menu_ctrlc_handler)
        if self.hostname() == 'cloud-ms-1':
            print('Detected this tool is running on vAPP, Because all vAPP LMS names are the same,\nsilent setup is not supported in this environment')
            sys.exit(0)

        if self.check_for_cloud() is True:
            self.cloud = True
            self.cloud_file_setup()
        else:
            self.cloud = False
            self.physical_file_setup()

    def cloud_file_setup(self):
        self.vm_private_key()
        print('\nENM username')
        self.cli_username = raw_input('')
        if self.cli_username is not '':
            self.enm_cli()
        self.ddp_url()
        self.output_dir()
        self.ftp_parameters()
        self.file_name()
        self.write_to_file_cloud()
        print '\nFile successfully created\n'
        self.ftp_upload()

    def generic_cloud_file_setup(self):
        self.cloud = True
        self.vm_private_key()
        print('\nENM username')
        self.cli_username = raw_input('')
        if self.cli_username is not '':
            self.enm_cli()
        self.ddp_url()
        self.output_dir()
        self.ftp_parameters()
        self.file_name()
        self.write_to_file_cloud()
        print '\nFile successfully created\n'
        self.ftp_upload()

    def physical_file_setup(self):
        self.vm_private_key()
        print('\nENM username')
        self.cli_username = raw_input('')
        if self.cli_username is not '':
            self.enm_cli()
        self.user_pass()
        self.ddp_url()
        self.output_dir()
        self.ftp_parameters()
        self.file_name()
        self.write_to_file_physical()
        print '\nFile successfully created\n'
        self.ftp_upload()

    def generic_physical_file_setup(self):
        self.cloud = False
        self.vm_private_key()
        print('\nENM username')
        self.cli_username = raw_input('')
        if self.cli_username is not '':
            self.enm_cli()
        self.user_pass()
        self.ddp_url()
        self.output_dir()
        self.ftp_parameters()
        self.file_name()
        self.write_to_file_physical()
        print '\nFile successfully created\n'
        self.ftp_upload()

    def vm_private_key(self):
        default = '/root/.ssh/vm_private_key'
        while True:
            print('\nEnter VM Private key default [%s]' % default)
            self.vm_key = raw_input('')
            if self.vm_key is not '':
                if os.path.exists(self.vm_key) is True:
                    break
                else:
                    print ('This is not a vm private key')
            else:
                print('Accepting Default')
                self.vm_key = default
                break

    def enm_cli(self):
        print('\nENM user password: ')
        self.cli_password = self.print_to_asterisks()
        if self.cli_password is not '':
            print('\nRole: ')
            self.cli_role = raw_input('')
            if self.cli_role is '':
                self.cli_role = 'OPERATOR'

    def ddp_url(self):
        print('\nDDP URL: ')
        self.ddp_url = raw_input('')

    def user_pass(self):
        print("\nEnter physical Peer Server's username for SSH [litp-admin]:")
        self.server_username = raw_input('')
        if self.server_username is '':
            self.server_username = 'litp-admin'
        while True:
            print("\nEnter physical Peer server's password for SSH")
            self.ssh_pass = self.print_to_asterisks()
            if self.ssh_pass is not '':
                break
            else:
                print('ERROR. This is a mandatory parameter, you must enter ssh password\n')
        while True:
            print("\nEnter Root Password for Peer Server ")
            self.root_pass = self.print_to_asterisks()
            if self.root_pass is not '':
                break
            else:
                print('ERROR. This is a mandatory parameter, you must enter root password\n')

    def output_dir(self):
        default = '/ericsson/enm/dumps'
        while True:
            print("\nEnter the shared path for the directory to store the output data."
                  "\n[Note]: this path must be available on all VMs."
                  "\nEnter Output Directory for logs default [%s]" % default)
            self.directory = raw_input('')
            if self.directory is '':
                print 'Accepting default'
                self.directory = default
                break
            else:
                # check for directory
                if os.path.exists(self.directory):
                    break
                else:
                    print 'The path %s does not exist' % self.directory

    def ftp_parameters(self):
        yes = ['Yes', 'Y']
        no = ['No', 'N']
        default = 'ftp.athtem.eei.ericsson.se'
        while True:
            print('\nDo you want this tool to automatically upload trouble reports to FTP server')
            print('[Yes] to confirm or [No] to cancel:')
            ans = raw_input('')
            if ans in yes:
                while True:
                    print('\nEnter URL for FTP server for Automatic upload default [%s]' % default)
                    self.ftp_url = raw_input('')
                    if self.ftp_url is '':
                        print('Accepting default')
                        self.ftp_url = default
                    if self.check_ftp_url(self.ftp_url) is True:
                        break
                    else:
                        print('%s is not a url' % self.ftp_url)
                default_user = 'anonymous'
                while True:
                    print('\nEnter Username for FTP server default [%s]' % default_user)
                    self.ftp_user = raw_input('')
                    if self.ftp_user is'':
                        self.ftp_user = default_user
                        print 'Accepting default'
                    break
                default_pass = 'anonymous'
                while True:
                    print('\nEnter Password for FTP server default [%s]' % default_pass)
                    self.ftp_pass = self.print_to_asterisks()
                    if self.ftp_pass is '':
                        print 'Accepting default'
                        self.ftp_pass = default_pass
                    break
                break
            elif ans in no:
                break
            else:
                print('Invalid Entry')

    def file_name(self):
        if self.cloud is True:
            self.setup_file = '/tmp/%s_lcs_silent_setup_cloud' % self.hostname()
        else:
            self.setup_file = '/tmp/%s_lcs_silent_setup_physical' % self.hostname()

        os.system('touch %s' % self.setup_file)

    def write_to_file_physical(self):
        f = open(self.setup_file, 'w')
        f.write('COMMON_VM_KEY=> %s' % self.encrypt(self.vm_key))
        f.write('\nCOMMON_CLI_USERNAME=> %s' % self.cli_username)
        f.write('\nCOMMON_CLI_PASSWD=> %s' % self.encrypt(self.cli_password))
        f.write('\nCOMMON_CLI_ROLE=> %s' % self.cli_role)
        f.write('\nPHYCIAL_SSH_USER=> %s' % self.server_username)
        f.write('\nPHYCIAL_SSH_PASSWD=> %s' % self.encrypt(self.ssh_pass))
        f.write('\nPHYCIAL_ROOT_PASSED=> %s' % self.encrypt(self.root_pass))
        f.write('\nDDP_URL=> %s' % self.ddp_url)
        f.write('\nCOMMON_OUTPUT_DIR=> %s' % self.directory)
        f.write('\nFTP_URL=> %s' % self.ftp_url)
        f.write('\nFTP_USERNAME=> %s' % self.ftp_user)
        f.write('\nFTP_PASSWORD=> %s\n' % self.encrypt(self.ftp_pass))

    def write_to_file_cloud(self):
        f = open(self.setup_file, 'w')
        f.write('COMMON_VM_KEY=>%s' % self.encrypt(self.vm_key))
        f.write('\nCOMMON_CLI_USERNAME=> %s' % self.cli_username)
        f.write('\nCOMMON_CLI_PASSWD=> %s' % self.encrypt(self.cli_password))
        f.write('\nCOMMON_CLI_ROLE=> %s' % self.cli_role)
        f.write('\nDDP_URL=> %s' % self.ddp_url)
        f.write('\nCOMMON_OUTPUT_DIR=> %s' % self.directory)
        f.write('\nFTP_URL=> %s' % self.ftp_url)
        f.write('\nFTP_USERNAME=> %s' % self.ftp_user)
        f.write('\nFTP_PASSWORD=> %s\n' % self.encrypt(self.ftp_pass))

    def ftp_upload(self):
        url_list = self.url_in_file[0].split('/')
        url = url_list[2]
        ftp_folder = url_list[3]
        ftp = FTP()
        try:
            # check if connection established
            ftp.connect(str(url))
            ftp.login('anonymous', 'anonymous')
        except:
            print 'ERROR. could not access ftp server. Upload file manually'
            print 'File location is /tmp/%s' % self.setup_file
            sys.exit(0)
        try:
            resp = ftp.sendcmd('MLST %s' % ftp_folder)
        except:
            print 'ERROR. could not upload the file to the ftp server. Upload file manually'
            print 'File location is /tmp/%s' % self.setup_file
            sys.exit(0)
        # check if lcs_report directory exists
        if 'type=dir;' in resp:
            ftp.cwd(ftp_folder)
            setup_file = open(self.setup_file, 'rb')
            try:
                ftp.storbinary('STOR ' + os.path.basename(self.setup_file), setup_file)
                ftp.quit()
            except:
                print('%s already exists on ftp server' % os.path.basename(self.setup_file))
                Yes = ['Yes', 'Y']
                No = ['No', 'N']
                while True:
                    ans = raw_input('Would you like to overwrite this file? Answer Yes or No: ')
                    if ans in Yes:
                        ftp.delete(os.path.basename(self.setup_file))
                        time.sleep(2)
                        ftp.storbinary('STOR ' + os.path.basename(self.setup_file), setup_file)
                        ftp.quit()
                        break
                    elif ans in No:
                        os.system('rm -rf %s' % self.setup_file)
                        self.main_menu()
                        break
                    else:
                        print 'Invalid Entry'

            print '\nFile upload successful\n'
            os.system('rm -rf %s' % self.setup_file)
            sys.exit(0)
        else:
            ftp.mkd(ftp_folder)
            ftp.cwd(ftp_folder)
            setup_file = open(self.setup_file, 'rb')
            try:
                ftp.storbinary('STOR ' + os.path.basename(self.setup_file), setup_file)
                ftp.quit()
            except:
                print('%s already exists on ftp server' % self.setup_file)
                Yes = ['Yes', 'Y']
                No = ['No', 'N']
                while True:
                    ans = raw_input('Would you like to overwrite this file? Answer Yes or No: ')
                    if ans in Yes:
                        ftp.delete(os.path.basename(self.setup_file))
                        time.sleep(2)
                        ftp.storbinary('STOR ' + os.path.basename(self.setup_file), setup_file)
                        ftp.quit()
                        break
                    elif ans in No:
                        os.system('rm -rf %s' % self.setup_file)
                        self.main_menu()
                        break
                    else:
                        print 'Invalid Entry'
                os.system('rm -rf %s' % self.setup_file)
                self.main_menu()
            print '\nFile upload successful\n'
            os.system('rm -rf %s' % self.setup_file)
            sys.exit(0)

    @staticmethod
    def check_ftp_url(url):
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

    @staticmethod
    def numberlist(menu):
        new = ('\n'.join(['. '.join((str(name).zfill(1), num)) for name, num in enumerate(menu, 1)]))
        return new

    def print_to_asterisks(self):
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
                sys.exit(0)
            else:
                key += ch
                sys.stdout.write('*')
        print
        return key

    @staticmethod
    def hostname():
        return socket.gethostname()

    @staticmethod
    def pass_to_asterisks():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    @staticmethod
    def check_for_cloud():
        if os.path.exists('/usr/bin/litp') is True:
            return False
        else:
            return True

    @staticmethod
    def encrypt(plain_text):
        binary_str = plain_text.encode('ascii')
        b64_encoded = base64.urlsafe_b64encode(binary_str)
        encrypted = str(b64_encoded.decode('ascii'))
        return encrypted

    @staticmethod
    def _dynamic_menu_ctrlc_handler(sig, frame):
        sys.exit(0)


EncryptFile()
