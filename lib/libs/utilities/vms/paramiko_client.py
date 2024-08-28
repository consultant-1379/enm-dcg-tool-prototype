import socket
import pexpect
from libs.utilities.system.pexpect_child import PexpectChild
import time
from libs.logging.logger import Logger
from libs.logging.verbose import Verbose
from libs.utilities.system.file_paths import FilePaths
from libs.utilities.system.output import Output
from libs.variables.configuration import Configuration


class ParamikoClient():
    """
    This class follows the document: ENM Data Collection Guidelines

    1.1.1. Connect to a Virtual Machine on an ENM deployment on the Cloud
        Context Description
            To connect to the virtual machine (VM) linked to the deployment, it is necessary to determine what environment you are working on and
            follow the task relevant to your environment.
        Prerequisites
            A command window is open and you have super user privileges.
            You have access to the cloud-user private key file for authentication, contact your Openstack administrator
        Expected Result
            You are connected via SSH to the VM. If the result is not as expected, contact local Ericsson support.
    """

    def __init__(self, vm_instance, using_sudo=False, port_number=None, user_name=None, password=None):
        """

        :param vm_instance: The vm instance name (e.g. svc-3-cmserv) or the IP address (e.g. 10.247.246.61)
        :param using_sudo: If use root user privilege when executing commands
        :param port_number: default port number to connect to VMs is 22
        :param user_name: default value is 'cloud-user'
        """

        # Set up for connection
        self.vm_instance = vm_instance

        self.port_number = port_number
        if (self.port_number == None):
            self.port_number = Configuration.vm_port_number

        self.user_name = user_name
        if (self.user_name == None):
            self.user_name = Configuration.vm_user_name

        self.password = password
        if (self.password == None):
            self.password = Configuration.vm_password

        self._key_filename = Configuration.vm_private_key

        # SSH object
        self.ssh_client = None

        # Configured variables
        self.using_sudo = using_sudo
        self.stdin = None
        self.stdout = None
        self.stderr = None
        self.out_lines = None
        self.err_lines = None
        self.hostname = None
        self.command = None

    def set_using_sudo(self, sudo):
        """
        set if you want to use sudo
        :param sudo: True/False
        :return:
        """
        self.using_sudo = sudo

    def connect(self):
        Verbose.yellow("Connecting to: hostname = %s\tusername = %s" % (self.vm_instance,self.user_name))
        try:
            child = PexpectChild('sudo ssh  -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i %s %s@%s > /dev/null 2>&1' % (Configuration.vm_private_key, self.user_name,self.vm_instance))
            expected = "Last login:"
            exception = "Permission denied"
            exception1 = "Warning: Identity file /root/.ssh/vm_private_ke not accessible:"
            result = child.expect([expected, exception,exception1])
            if (result == 0):
                # logged in the peer server successfully
                Verbose.green("Logged into %s"%self.vm_instance)
                return True
            elif result == 2:
                # todo if permission denied pass a password
                pass
            else:
                return False
        except socket.error as e:
            Output.red('"socket.error" occurred when connecting to VM %s.\nstrerror = "%s"\n' % (self.vm_instance, e.strerror))
            return False
        except (IOError, pexpect.ExceptionPexpect):
            Output.red('Invalid vm_private_key "%s"' % (self._key_filename))
        return True

    def close(self):
        Verbose.green("Closing session: %s" % (self.vm_instance))
        child = PexpectChild('exit')
        child.expect('logout')

    @staticmethod
    def get_hostname():
        host = PexpectChild('hostname')
        hostname = host.before
        if isinstance(hostname, bytes):
            hostname = hostname.decode('utf-8').strip()
        return hostname

    @staticmethod
    def get_username():
        return Configuration.vm_user_name

    def _raw_execute(self, command):
        # print out the command before executing
        Logger.info("Host = %s\tusername = %s, executing the command:" % (self.get_hostname(), self.get_username()))
        Verbose.white("\t%s " % command)
        start = time.time()
        # Execute the command
        child = PexpectChild(command)
        end = time.time()
        total = start - end
        Logger.info("Execution Time: %s" %total)

        # Get the output
        self.out_lines = child.before
        self.err_lines = child.before
        print self.out_lines

    def execute(self, command, superuser=None):
        if (superuser == None):
            if (self.using_sudo):
                command = "sudo sh -c '" + command + "'"
        else:
            if (superuser):
                command = "sudo sh -c '" + command + "'"

        self.command = command

        try:
            self._raw_execute(command)
        except pexpect.ExceptionPexpect as e:
            # Exception occurs if the session overflew
            Verbose.yellow('Failed to execute the command, because the current session of the following vm overflew')
            Verbose.green('\tvm = %s\tclient = %s' % (self.vm_instance, self.ssh_client.get_transport().getpeername()))
            Verbose.yellow('We are trying to close and reconnect it to execute the command.')

            # So we disconnect and reconnect the client for executing the command again
            self.close()
            self.connect()
            self._raw_execute(command)

    def get_stdin(self):
        return self.stdin

    def get_stdout(self):
        """

        :return: a list of strings including the output messages
        """
        return self.out_lines

    def get_stderr(self):
        """

        :return:  a list of strings including the error messages
        """
        return self.err_lines

    def get_command(self):
        """

        :return: the command you just executed last time
        """
        return self.command

    def mkdir(self, directory, superuser=None):
        """
        If the directory exists, does nothing
        If not, make this directory in the virtual machine
        :param directory: The directory to be made
        :param superuser: True/False
        :return:
        """
        self.execute('[[ ! -d %s ]] && mkdir -p %s' % (directory, directory), superuser == superuser)

    def mv(self, source, destination, superuser=None):
        self.execute('mv -f %s %s' % (source, destination), superuser)

    def cp(self, source, destination, superuser=None):

        filename = (source.split("/"))[-1]

        final_file = FilePaths.join_path(destination,filename + '.tar.gz')

        command = "tar -czf " + final_file + ' ' + source
        self.execute(command)

    def rm(self, path, superuser=None):
        self.execute('rm -rf %s' % (path), superuser)

    def tar_gzip(self, file_path, target_gzip_path=None):
        """
        Tar and zip a directory
        :param file_path: the directory to tar and zip
        :param target_gzip_path: the name of the .tar.gz file
        :return:
        """
        if (file_path[-1] != '/'):
            file_path += '/'

        if (target_gzip_path == None):
            target_gzip_path = file_path[:-1] + ".tar.gz"

        # Switch to the parent directory of the target path
        chdir_command = "cd %s" % (file_path + "..")

        log_dir_folder_name = (file_path.split("/"))[-2]
        tar_zip_command = "tar -czf %s %s" % (target_gzip_path, log_dir_folder_name)
        self.execute(";".join([chdir_command, tar_zip_command]), superuser=True)

        return target_gzip_path

    def bash(self, script, output, timeout=None, superuser=None, *args):
        """
        Execute a bash script on the VM
        :param script: the path of the script
        :param timeout: the timeout value for the execution
        :return:
        """

        command = "bash %s" % (script)

        command = " ".join([command] + list(args))

        if (timeout != None):
            command = ("timeout %d " % timeout) + command

        # direct the output and error messages to the output file
        command += " &>> %s" % output

        # run the command in another process
        command += " &"
        self.execute(command, superuser)