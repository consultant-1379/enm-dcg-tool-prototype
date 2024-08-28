import os
import sys
import time
import subprocess

from libs.lcs_error import LCSError
from libs.logging.logger import Logger
from libs.logging.verbose import Verbose
from libs.start_up.check_user_eocm import CheckUserEocm
from libs.utilities.system.output import Output
from libs.variables.configuration import Configuration


class Terminal():

    ##################################################################################
    # get information from the terminal
    @staticmethod
    def pwd():
        return Terminal.popen_read('pwd')[:-1]

    @staticmethod
    def hostname():
        return Terminal.popen_read('hostname')[:-1]

    @staticmethod
    def username():
        return Terminal.popen_read('whoami')[:-1]

    ##################################################################################

    # get inputs
    @staticmethod
    def noecho_input(message=''):
        from getpass import getpass
        return getpass(message)

    @staticmethod
    def get_input():
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    @staticmethod
    def input(message='',setup=False):
        import readline
        msg = raw_input(message)
        Logger.info(msg, setup=setup)
        return msg

    @staticmethod
    def any_input():
        import readline
        Output.yellow("Press ANY key to continue...")
        while True:
            if Terminal.get_input() is None:
                time.sleep(0.1)
            else:
                return False

    ##################################################################################

    # execute common commands
    @staticmethod
    def tar_gzip(file_path, target_gzip_path=None):
        if (file_path[-1] != '/'):
            file_path += '/'

        if (target_gzip_path == None):
            target_gzip_path = file_path[:-1] + ".tar.gz"

        # save the current working directory
        cwd = os.getcwd()

        # Switch to the parent directory of the target path
        Terminal.chdir(file_path + "..")
        log_dir_folder_name = (file_path.split("/"))[-2]

        command = "tar -czf %s %s 2> /dev/null" % (target_gzip_path, log_dir_folder_name)
        try:
            Terminal.sub(command)
        except:
            Logger.error("Python code error, Could not Compress file")
            raise LCSError('\nError, Could not Compress file')

        # Change the working directory to the original one
        return Terminal.chdir(cwd)

    @staticmethod
    def tarfile(file_path):
        command = "gzip %s" %(file_path)
        try:
            Terminal.sub(command)
        except:
            Logger.error("Python code error, Could not Compress file")
            raise LCSError('\nError, Could not Compress file')

    @staticmethod
    def mkdir(directory, superuser=False):
        """
        If the directory exists, does nothing
        If not, make this directory in the host which is running this script
        :param directory: The directory to be made
        :param superuser: True/False
        :return:
        """
        if Configuration.EOCM is True:
            return Terminal.system('if [[ ! -d %s ]]; then sudo mkdir -p %s; else echo test > /dev/null 2>&1; fi; sudo chown -R %s:%s %s > /dev/null 2>&1 ' % (directory, directory, CheckUserEocm.user(), CheckUserEocm.group_id(), directory), superuser)
        else:
            return Terminal.system('[[ ! -d %s ]] && mkdir -p %s || { echo test > /dev/null 2>&1; }' % (directory, directory), superuser)

    @staticmethod
    def cp(file_path, destination, superuser=False):
        # return Terminal.system('cp -a -p --force %s %s' % (file_path, destination), superuser)
        if os.path.isdir(file_path):
            if (file_path[-1] != '/'):
                file_path += '/'
        # just get name of file
        file_name = (file_path.split("/"))[-1]
        # get parent directory
        log_dir_folder_name = os.path.abspath(os.path.join(str(file_path), os.pardir))
        # final file you wish to generate
        final_file = destination + '/' + file_name
        cp_cmd = "sudo /bin/cp -a -p --force %s %s" % (file_path,destination)
        gzip_cmd = "sudo gzip %s --force" % final_file
        # command = "tar -czf %s %s/%s 2> /dev/null" % (final_file,log_dir_folder_name,file_name)
        try:
            Terminal.sub(cp_cmd)
            if str(final_file).endswith(".gz") is False:
                Terminal.sub(gzip_cmd)
        except:
            Logger.error("Python code error, Could not Compress file")
            raise LCSError('\nError, Could not Compress file')

    @staticmethod
    def filesize(file):
        statinfo = os.stat(file)
        return statinfo.st_size

    @staticmethod
    def copy(file_path, destination, superuser=False, setup=False):
        if Configuration.EOCM is True:
            return Terminal.system('sudo /bin/cp -a -p --force %s %s' % (file_path, destination), superuser, setup=setup)
        else:
            return Terminal.system('/bin/cp -a -p --force %s %s' % (file_path, destination), superuser, setup=setup)

    @staticmethod
    def mv(file_path, destination, superuser=False, setup=False):
        return Terminal.system('mv --force %s %s' % (file_path, destination), superuser, setup=setup)

    @staticmethod
    def system(command, superuser=False, setup=False):
        if (superuser):
            command = "sudo sh -c '" + command + "'"
        result = os.system(command)
        if result != 0:
            Logger.error('%s not executed'%command)
        return result

    @staticmethod
    def rm(path, superuser=False, setup=False):
        Terminal.system('rm -rf %s' % path, superuser, setup=setup)

    @staticmethod
    def chdir(path):
        Terminal._debug_info(path, "os.chdir(path)")
        return os.chdir(path)

    @staticmethod
    def _debug_info(command, method_name=None, setup=False):
        if method_name is None:
            Verbose.white("\t%s" % command)
        else:
            Verbose.white("Using %s to execute the command:\n\t%s" % (method_name, command))

    @staticmethod
    def clear():
        return Terminal.system("clear")

    @staticmethod
    def chmod(mode_code, file_path,setup=False):
        try:
            mode_code = int(mode_code)
        except:
            Terminal.exception("Mode code must be an integer.")

        return Terminal.system("chmod %03d '%s'" % (mode_code, file_path),setup=setup)

    @staticmethod
    def exception(message=''):
        # To reset all settings to the default:
        Terminal.system("stty sane")
        message = message + "\nError caused Exit."
        # Output information and raise LCS exception
        # Verbose.red(message)
        # Output.red("Error caused Exit.")
        raise LCSError(message)

    @staticmethod
    def exit(status=0, message=''):
        # To reset all settings to the default:
        Terminal.system("stty sane")
        # Output information
        if (status == 0):
            Output.white(message)
            Output.green("Exiting Log Collection Service")
        else:
            Output.white(message)
            Output.white("Exiting")
        # Exit the program
        try:
            Terminal._debug_info("status = %s" % status, "sys.exception(status)")
            return sys.exit(status)
        except SystemExit:
            Terminal._debug_info("status = %s" % status, "os._exit(status)")
            return sys.exit(status)

    @staticmethod
    def popen_read(command, mode='r', superuser=False):
        if (superuser):
            command = "sudo sh -c '" + command + "'"

        #Terminal._debug_info("command = %s, mode = %s" % (command, mode), "os.popen(command, mode, bufsize)")
        return os.popen(command, mode).read()

    @staticmethod
    def console_width():
        rows, columns = os.popen('stty size', 'r').read().split()
        return int(columns)

    @staticmethod
    def touch(file_path, superuser=False):
        """
        Create a file on the local machine
        :param file_path: the file path
        :return:
        """
        return Terminal.system("touch %s" % (file_path), superuser)

    @staticmethod
    def sub(command):
        # command = "sudo sh -c '" + command + "'"
        Terminal._debug_info(command)
        run_command = subprocess.Popen(command, shell=True)
        run_command.wait()
        # check linux error
        (stdout, stderr) = run_command.communicate()
        if run_command.returncode != 0:
            # raise LCSError('\nError, Could not Compress file, Linux command not correct')
            Logger.error('\nLinux Error, Could not Compress file')
            return run_command
        else:
            return run_command

    @staticmethod
    def check_file_running():
        if Configuration.use_tool_while_instance_running == False:
            if os.path.exists('/tmp/Log_tool_running'):
                if Configuration.execute_multiple_files == True:
                     Output.red('Another instance of log collection is already running. Please try again later.')
                     sys.exit(0)
                else:
                    Output.red('Another instance of log collection Service is already running. Please try again later.')
                    sys.exit(0)
