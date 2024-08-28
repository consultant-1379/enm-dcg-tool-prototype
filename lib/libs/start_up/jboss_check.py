import os
import time

from libs.logging.logger import Logger
from libs.utilities.data_structures.database import Database
from libs.utilities.data_structures.encryption import Encryption
from libs.utilities.system.file_paths import FilePaths
from libs.utilities.system.output import Output
from libs.utilities.system.terminal import Terminal
from libs.utilities.vms.global_search import GlobalSearch
from libs.variables.configuration import Configuration


class JBossCheck:

    def __init__(self):
        self.stamp = time.strftime('%Y%m%d%H%M')
        self.path = Configuration.default_path + '/log/.lastRun/'
        if os.path.exists(self.path) is True:
            disable_list = self.check_for_old_files(self.path, self.stamp)
            self.out_lines = None
            self.get_default_path()
            for each in disable_list:
                path = self.path + each
                print path
                if self._exists(path) is True and os.path.exists('/tmp/Log_tool_running') is False:
                    self._get_vm_key()
                    with open(path, 'r') as f:
                        instances = f.readline()
                        loggers = f.readline()
                        self.vms = GlobalSearch(instances.replace('[', '').replace(']', '').replace('"', '').strip())\
                            .get_correct_list()
                        self.loggers = self. _get_loggers(loggers)
                        self.subsystem = "logging"
                        self.count = 0
                        self.vm_list = self.check_file_vms()
                        if len(self.vm_list) > 0:
                            if self.disable_logers() is True:
                                Terminal.rm(self.path, superuser=True)
                                Output.green('logger for %s are disabled' % self.vm_list)
                                Logger.warning('Loggers for %s had to be disabled on start-up' % self.vm_list)
                            else:
                                Output.red('logger could not be disabled for %s' % self.vm_list)
                                Logger.error('loggers could not be disabled on start-up for %s' % self.vm_list)
                        else:
                            Terminal.rm(path)
                            Logger.warning(path + ' file exists on startup but all loggers were disabled')

    def check_file_vms(self):
        vm_list = []
        file_name = '/tmp/.lcs_debug_enabled'
        command = 'test -f ' + file_name
        for vm in self.vms:
            print vm
            result = Terminal.system('ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null '
                                     '-i %s %s@%s 2>/dev/null "%s" > /dev/null'
                                     % (Configuration.vm_private_key, Configuration.vm_user_name, vm, command))
            if result == 0:
                vm_list.append(vm)
                # file exists on vm, debug needs to disabled
                with open('/tmp/lcs_start_up_disable_JBoss_loggers.bsh', 'w') as f:
                    f.write('#!/bin/bash\n')
                    for loggers in self.loggers:
                        f.write('\n/ericsson/3pp/jboss/bin/jboss-cli.sh -c '
                                '<<EOF\n/subsystem=%s/logger=%s:change-log-level(level=INFO)\nEOF\n'
                                % (self.subsystem, loggers))
                        f.write('ret=$?\n')
                    f.write('exit $ret\n')
                    Terminal.system("scp -o StrictHostKeyChecking=no -o "
                                    "UserKnownHostsFile=/dev/null > /dev/null 2>&1 -i %s "
                                    "/tmp/lcs_start_up_disable_JBoss_loggers.bsh %s@%s:/tmp/ >/dev/null "
                                    % (Configuration.vm_private_key, Configuration.vm_user_name, vm))
                    Terminal.system('sudo rm -rf /tmp/lcs_start_up_disable_JBoss_loggers.bsh')
        return vm_list

    def disable_logers(self):
        try:
            for vm in self.vm_list:
                Terminal.system('ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i %s %s@%s '
                                '2>/dev/null "bash /tmp/lcs_start_up_disable_JBoss_loggers.bsh" >/dev/null'
                                % (Configuration.vm_private_key, Configuration.vm_user_name, vm))
                result = Terminal.system('echo $? >/dev/null')
                if result == 0:
                    Terminal.system('ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i %s %s@%s '
                                    '2>/dev/null "rm -rf /tmp/lcs_start_up_disable_JBoss_loggers.bsh '
                                    '/tmp/.lcs_debug_enabled" >/dev/null'
                                    % (Configuration.vm_private_key, Configuration.vm_user_name, vm))
                    self.count = self.count + 1
                if self.count == len(self.vm_list):
                    return True
        except:
            Logger.error("Could not run lcs_start_up_disable_JBoss_loggers.bsh script on %s" % self.vm_list)
            return False

    @staticmethod
    def check_for_old_files(path, time_now):
        disable_files_list = []
        time_to_check = int(time_now) - 60
        files_list = os.listdir(path)
        for each in files_list:
            if int(each.split('_')[1]) < time_to_check:
                #print 'hello'
                disable_files_list.append(each)

        return disable_files_list

    @staticmethod
    def _exists(path):
        return os.path.exists(path)

    @staticmethod
    def _get_vm_key():
        if os.stat(Configuration.database_file).st_size is not 0:
            db = Database(Configuration.database_file)
            result = db.select('*', Configuration.database_table)
            key = []
            value = []
            for record in result:
                key.append(record[0])
                value.append(record[1])
            if 'vm_private_key' in key:
                vm_key = value[0]
                private = Encryption.decrypt(vm_key)
                Configuration.vm_private_key = private

    @staticmethod
    def _get_loggers(logger_str):
        loggers = logger_str.split(' ')
        return loggers

    @staticmethod
    def get_default_path():
        Configuration.default_path = FilePaths.absolute_path(os.path.join(Configuration.default_main_file,
                                                                          FilePaths.pardir(), FilePaths.pardir()))