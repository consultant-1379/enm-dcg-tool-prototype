import os
import socket

from libs.functions.jboss_debug.tools.logger_level_controller import LoggerLevelController as Log
from libs.logging.logger import Logger
from libs.logging.verbose import Verbose
from libs.utilities.data_structures.dictionary import Dictionary
from libs.utilities.system.file_paths import FilePaths
from libs.utilities.system.output import Output
from libs.utilities.system.terminal import Terminal
from libs.utilities.vms.global_search import GlobalSearch
from libs.variables.configuration import Configuration
from libs.variables.keys import AppKeys


class VMInstanceController(object):

    def _get_level_value(self):
        """
        the level value should be either DEBUG or TRACE
        :return:
        """
        if AppKeys.level_value in self.vm_node:
            log_level = Dictionary.get_value(self.vm_node, AppKeys.level_value)
        else:
            log_level = 'DEBUG'

        if type(log_level) is list:
            value = log_level[0]
        else:
            value = log_level

        return value

    def __init__(self, vm_node):
        self.vm_node = vm_node
        self.level_value = self._get_level_value()

    def get_vn_instance_name(self):
        return self.vm_node[AppKeys.instance]

    def enable_debug(self):
        """
        :return: True is loggers are enabled
        """
        if Configuration.Jboss_EOCM is True:
            Log(self.vm_node, self.level_value).enable_debug()
        else:
            result = Terminal.system('ping -c 1 %s >/dev/null' % self.get_vn_instance_name())
            if result == 0:
                Terminal.system('ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i %s %s@%s 2>/dev/null "touch /tmp/.lcs_debug_enabled" > /dev/null 2>&1' % (Configuration.vm_private_key, Configuration.vm_user_name, self.get_vn_instance_name()))
                instance = Dictionary.get_value(self.vm_node, AppKeys.instance)
                Log(instance, self.level_value).enable_debug()
                Verbose.white('')
                return True
            else:
                Verbose.red(
                    "Could not enable debug logs from the VM %s, due to VM not accessible" % self.get_vn_instance_name())
                Output.red(
                    "Could not enable debug logs from the VM %s, due to VM not accessible" % self.get_vn_instance_name())
                return False

    def disable_debug(self):
        if Configuration.Jboss_EOCM is True:
            Output.yellow('\n\nDisabling JBOSS debugging loggers, please wait...')
            Log(self.vm_node, self.level_value).disable_debug()
        else:
            instance = Dictionary.get_value(self.vm_node, AppKeys.instance)
            if Log(instance, self.level_value).disable_debug() == True:
                Verbose.white('')
                Terminal.system('ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i %s %s@%s 2>/dev/null "sudo rm /tmp/.lcs_debug_enabled" > /dev/null 2>&1' % (
                Configuration.vm_private_key, Configuration.vm_user_name, self.get_vn_instance_name()))
                return True
            return False

    @staticmethod
    def run_jboss_commands(time, commands, tar_path, vm, stamp):
        more_than_one = VMInstanceController.check_for_more_than_one_command(commands)
        host = socket.gethostname()
        Configuration.jboss_command_stamp = stamp
        if Configuration.Jboss_EOCM is True:
            for command in more_than_one:
                name_file = os.path.basename(command)
                file_split = name_file.split(' ')
                name_of_file = file_split[0]
                file_path = tar_path + '/' + host + '/jboss_commands_' + name_of_file + '_' + stamp
                Terminal.mkdir('%s/%s' % (tar_path, socket.gethostname()))
                Terminal.touch(file_path)
                Terminal.system('sudo chmod 777 %s' % file_path)
                result = Terminal.system(
                    'echo "<<<<<<<<<<<<<<< command run: %s [$(date)] >>>>>>>>>>>>>>>" > %s ' % (command, file_path))
                Terminal.system("sudo timeout %s %s >> %s 2>&1 &" % (time, command, file_path))
                if result == 0:
                    Logger.info('jboss commands directory made')
                    return True
                else:
                    Logger.info('jboss commands directory not made')
                    return False
        else:
            vms = GlobalSearch(vm).get_correct_list()
            for vm in vms:
                result = Terminal.system('ping -c 1 %s >/dev/null' % vm)
                if result == 0:
                    for command in more_than_one:
                        name_file = os.path.basename(command)
                        file_split = name_file.split(' ')
                        name_of_file = file_split[0]
                        file_path = tar_path + '/' + vm + '/jboss_commands_' + name_of_file + '_' + stamp
                        Terminal.mkdir('%s/%s' % (tar_path, vm))
                        Terminal.touch(file_path)
                        Terminal.system('sudo chmod 777 %s' % file_path)
                        result = Terminal.system('echo "<<<<<<<<<<<<<<< command run: %s [$(date)] >>>>>>>>>>>>>>>" > %s ' % (command, file_path))
                        Terminal.system('ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i %s %s@%s 2>/dev/null "sudo timeout %s %s >> %s 2>&1 &"' % (Configuration.vm_private_key, Configuration.vm_user_name, vm, time, command,  file_path))
                        if result == 0:
                            Logger.info('jboss commands directory made')
                        else:
                            Logger.info('jboss commands directory not made')
                else:
                    Output.red("Can not run Jboss commmand on %s." % vm)
                    Verbose.red("Can not run Jboss commmand on %s." % vm)
                    return False
            return True

    @staticmethod
    def jboss_command_file(tar_path, vm, cmd):
        # name_file = os.path.basename(cmd)
        # file_split = name_file.split(' ')
        # file_name = file_split[0]
        # if Configuration.TCP_collection is True:
        #     vms = GlobalSearch(vm).get_correct_list()
        #     for each in vms:
        #         Terminal.tarfile(FilePaths.join_path(tar_path, each + '/%s_' + Configuration.jboss_command_stamp) % file_name)
        pass

    @staticmethod
    def check_for_more_than_one_command(commands):
        new = []
        new_command = commands.split(',')
        for each in new_command:
            new.append(each)
        return new