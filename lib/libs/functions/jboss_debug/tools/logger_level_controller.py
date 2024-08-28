import socket
import subprocess
import time

from libs.logging.logger import Logger
from libs.logging.verbose import Verbose
from libs.start_up.check_user_eocm import CheckUserEocm
from libs.utilities.system.output import Output
from libs.utilities.system.terminal import Terminal
from libs.variables.configuration import Configuration
import os


class LoggerLevelController:

    def __init__(self, vm, level_value):
        """
        :param client: The client for enabling debug
        :param logger_name: The name of logger
        :param subsystem:
        """
        if Configuration.time_stamp_jboss == None:
            Configuration.time_stamp_jboss = time.strftime('%Y%m%d%H%M%S')
        if Configuration.debug_time != None:
            self.added_time = int(Configuration.debug_time) + 1
        else:
            self.added_time = int(Configuration.JBoss_time_out) + 1
        self.JBoss_log_path = Configuration.JBoss_log_path[0]
        if 'localhost' in vm:
            self.vm = socket.gethostname()
        else:
            self.vm = vm
        self.level_value = level_value
        self.logger = Configuration.JBoss_loggers
        self.subsystem = "logging"
        self.length_of_loggers = len(Configuration.JBoss_loggers)
        self.stamp = self.vm + '_' + Configuration.time_stamp_jboss
        self.stamp = self.vm + '_' + Configuration.time_stamp_jboss
        self.directory = Configuration.storing_logs_dir + '.LCSMetadata/' + self.stamp
        self.enable_file = self.directory + '/Lcs_Loggers_enable.bsh'
        self.disable_file = self.directory + '/Lcs_Loggers_disable.bsh'
        self.jboss_plug_timeout = Configuration.jboss_plug_timeout

    def enable_debug(self):
        refined_path = os.path.abspath(os.path.join(str(self.JBoss_log_path), os.pardir))
        if Configuration.Jboss_EOCM is True:
            Terminal.sub('mkdir -p ' + Configuration.storing_logs_dir + '.LCSMetadata/' + self.stamp)
            medadata_dir = Configuration.storing_logs_dir + '.LCSMetadata/' + self.stamp
            Terminal.sub('sudo chown -R %s:%s %s/../..' % (CheckUserEocm.user(), CheckUserEocm.group_id(), medadata_dir))


            Terminal.sub('''mkdir -p "%s/%s%s/"''' % (Configuration.JBoss_plug_in_output_dir, socket.gethostname(), refined_path))
            Terminal.sub('sudo chmod 777 %s/%s%s/' % (Configuration.JBoss_plug_in_output_dir, socket.gethostname(), refined_path))
        else:
            Terminal.sub('sudo mkdir -p ' + Configuration.storing_logs_dir + '.LCSMetadata/' + self.stamp)
            Terminal.sub('''sudo mkdir -p "%s/%s%s/"''' % (Configuration.JBoss_plug_in_output_dir, self.vm, refined_path))
            Terminal.sub('sudo chmod 777 %s/%s%s/' % (Configuration.JBoss_plug_in_output_dir, self.vm, refined_path))
        if (self._create_jboss_control_file("change-log-level(level=%s)" % self.level_value) == False):
            self._create_jboss_control_file("add(level=%s)" % self.level_value)

    def disable_debug(self):
        if Configuration.Jboss_EOCM is True:
            self._execute_disable_debug()
        else:
            if self._execute_disable_debug() == True:
                return True
            return False

    def _create_jboss_control_file(self, command):
        with open(self.enable_file, 'w') as f:
            f.write('#!/bin/bash\n')
            if Configuration.EOCM is True:
                f.write('chown -R %s:%s %s/..\n' % (CheckUserEocm.user(), CheckUserEocm.group_id(), Configuration.storing_logs_dir))
            f.write('ERROR_IN_LOGGER=NOERR\n')
            f.write('''JBOSS_CLI="/ericsson/3pp/jboss/bin/jboss-cli.sh"\n''')
            f.write('if [[ ! -f /ericsson/tor/data/global.properties ]]; then\n')
            f.write('. /root/.bashrc\n')
            f.write('''JBOSS_DIR=$(alias | grep jboss | awk '{print $NF}' | awk -F "'" '{print $1}')\n''')
            f.write('if [[ -f ${JBOSS_DIR}/bin/jboss-cli.sh ]]; then\n')
            f.write('JBOSS_CLI="${JBOSS_DIR}/bin/jboss-cli.sh"\n')
            f.write('ARGS="--controller=localhost:12500"\n')
            f.write('else\n')
            f.write('echo "${JBOSS_DIR}/bin/jboss-cli.sh, not found. Exiting..."\n')
            f.write('exit 1\n')
            f.write('fi\n')
            f.write('fi\n')
            f.write('rm -f /tmp/Loggers_failed /tmp/Loggers_added\n')
            f.write('touch /tmp/.lcs_debug_enabled > /dev/null 2>&1\n')
            f.write('\necho $(date) JBOSS enable START [timeout=%s]' % (self.added_time - 1))
            refined_path = os.path.abspath(os.path.join(str(self.JBoss_log_path), os.pardir))
            if Configuration.EOCM is True:
                f.write('''\n[[ ! -d %s/%s%s/ ]] && mkdir -p "%s/%s%s/"'''
                        % (Configuration.JBoss_plug_in_output_dir, self.vm, refined_path,
                           Configuration.JBoss_plug_in_output_dir, self.vm, refined_path))
                f.write('\nchmod 777 %s/%s%s/' % (Configuration.JBoss_plug_in_output_dir, self.vm, refined_path))
            else:
                f.write('''\n[[ ! -d %s/%s%s/ ]] && sudo mkdir -p "%s/%s%s/"'''
                        % (Configuration.JBoss_plug_in_output_dir, self.vm, refined_path,
                           Configuration.JBoss_plug_in_output_dir, self.vm, refined_path))
                f.write('\nsudo chmod 777 %s/%s%s/' % (Configuration.JBoss_plug_in_output_dir, self.vm, refined_path))
            f.write('\necho "<<<<<<<<<<<<<<< JBOSS LOG [%s] START [$(date)] >>>>>>>>>>>>>>>" >> %s/%s%s.debug_out '
                    % (self.level_value, Configuration.JBoss_plug_in_output_dir, self.vm, self.JBoss_log_path))
            f.write('\ntimeout %s tail -f %s >> %s/%s%s.debug_out &'
                    % (self.added_time, self.JBoss_log_path, Configuration.JBoss_plug_in_output_dir,
                       self.vm, self.JBoss_log_path))
            for loggers in self.logger:
                f.write('\necho $(date) Enabling logger [%s], log level [%s]' % (loggers, self.level_value))
                f.write('\n${JBOSS_CLI} -c ${ARGS}<<EOF\n')
                f.write('/subsystem=%s/logger=%s:%s\nEOF\n' % (self.subsystem, loggers, command))
                f.write('ret=$?\n')
                f.write('if [[ $ret -eq 0 ]]; then\n')
                f.write('echo \" $(date) [logger=%s, level=%s] Enabled successfully.\";\n'
                        % (loggers, self.level_value))
                f.write('else')
                f.write('\necho $(date) Adding logger [%s], log level [%s]' % (loggers, self.level_value))
                f.write('\n${JBOSS_CLI} -c ${ARGS}<<EOF\n')
                f.write('/subsystem=%s/logger=%s:add(level=%s)\nEOF\n' % (self.subsystem, loggers, self.level_value))
                f.write('ret=$?\n')
                f.write('if [[ $ret -eq 0 ]]; then\n')
                f.write('echo \"$(date) [logger=%s, level=%s] Added successfully.\";\n' % (loggers, self.level_value))
                f.write('echo %s >> /tmp/Loggers_added\n' % loggers)
                f.write('else\n')
                f.write('echo \"$(date) Error in adding [logger=%s, level=%s] jboss logging.\";\n'
                       % (loggers, self.level_value))
                f.write('echo %s >> /tmp/Loggers_failed\n' % (loggers))
                f.write('ERROR_IN_LOGGER=ERR\n')
                f.write('fi\n')
                f.write('fi\n')
            f.write('NUM_OF_LOGGER_ERR=0\n')
            f.write('if [[ -f /tmp/Loggers_failed ]]; then\n')
            f.write('''NUM_OF_LOGGER_ERR=$(wc -l /tmp/Loggers_failed | awk '{print $1}')\n''')
            f.write('fi\n')
            f.write('if [[ ${NUM_OF_LOGGER_ERR} -eq %s ]]; then\n' %(self.length_of_loggers))
            f.write('echo "$(date) ERROR in enabling all [%s] loggers. Stoping tail process.";\n'
                    % (self.length_of_loggers))
            f.write('PID=0\n')
            f.write('''PID=$(ps -ef | grep timeout | grep tail | awk '{print $2}')\n''')
            f.write('if [[ $PID -gt 10 ]]; then\n')
            f.write("kill 2> /dev/null -9 ${PID}\n")
            f.write('fi\n')
            f.write('\nexit $ret\n')
            f.write('fi\n')
            f.write('''if [[ "$ERROR_IN_LOGGER" == "ERR" ]]; then\n''')
            f.write('''for logger in $(cat /tmp/Loggers_failed); do logger_list="${logger_list}${logger},"; done\n''')
            f.write('echo \"$(date) Some JBOSS logger [${logger_list}] not enabled successfully.\";\n')
            f.write('fi\n')
            f.write('sleep %s\n' %(self.added_time))
            f.write('echo $(date) Calling disable script.\n')
            f.write('bash %s &\n' % self.disable_file)
            f.write('''echo $(date) [$?]\n''')
            f.write('sleep 1\n')
            f.write("kill 2> /dev/null -9 $(ps -ef | grep timeout | grep tail | awk '{print $2}')\n")
            f.write('''\necho "<<<<<<<<<<<<<<< JBOSS LOG END [$(date)] >>>>>>>>>>>>>>>" >> %s/%s%s.debug_out '''
                    % (Configuration.JBoss_plug_in_output_dir, self.vm, self.JBoss_log_path))
            f.write('\necho $(date) JBOSS enable END')
            f.write('\nsleep 1')
            f.write('\nexit $ret\n')
        with open(self.disable_file, 'w') as f:
            f.write('#!/bin/bash\n')
            f.write('''JBOSS_CLI="/ericsson/3pp/jboss/bin/jboss-cli.sh"\n''')
            f.write('if [[ ! -f /ericsson/tor/data/global.properties ]]; then\n')
            f.write('. /root/.bashrc\n')
            f.write('''JBOSS_DIR=$(alias | grep jboss | awk '{print $NF}' | awk -F "'" '{print $1}')\n''')
            f.write('if [[ -f ${JBOSS_DIR}/bin/jboss-cli.sh ]]; then\n')
            f.write('JBOSS_CLI="${JBOSS_DIR}/bin/jboss-cli.sh"\n')
            f.write('ARGS="--controller=localhost:12500"\n')
            f.write('else\n')
            f.write('echo "${JBOSS_DIR}/bin/jboss-cli.sh, not found. Exiting..."\n')
            f.write('exit 1\n')
            f.write('fi\n')
            f.write('fi\n')
            for loggers in self.logger:
                self.disable_level = self.check_log_level(loggers)
                Logger.info('Changing log level of logger %s on %s from %s to %s' % (loggers, self.vm, self.disable_level, self.level_value))
                f.write('if [[ -f /tmp/Loggers_added ]]; then\n')
                f.write('grep %s /tmp/Loggers_added > /dev/null 2>&1\n' % loggers)
                f.write('if [[ $? -eq 0 ]]; then\n')
                f.write('\necho $(date) Removing logger [%s]\n' % loggers)
                f.write('\n${JBOSS_CLI} -c ${ARGS}<<EOF\n/subsystem=%s/logger=%s:remove()\nEOF\n'
                        % (self.subsystem, loggers))
                f.write('ret=$?\n')
                f.write('if [[ $ret -eq 0 ]]; then echo \"Removed successfully.\"; else  echo \"$(date) Error in removing jboss logger.\"; fi')
                f.write('\nelse\n')
                f.write('\necho $(date) Disabling logger [%s]' % loggers)
                f.write('\n${JBOSS_CLI} -c ${ARGS}<<EOF\n/subsystem=%s/logger=%s:change-log-level(level=%s)\nEOF\n' % (self.subsystem, loggers, self.disable_level))
                f.write('ret=$?\n')
                f.write('if [[ $ret -eq 0 ]]; then echo \"Removed successfully.\"; else echo \"$(date) Error in removing jboss logger.\"; fi')
                f.write('\nfi\n')
                f.write('else')
                f.write('\necho $(date) Disabling logger [%s]' % loggers)
                f.write('\n${JBOSS_CLI} -c ${ARGS}<<EOF\n/subsystem=%s/logger=%s:change-log-level(level=%s)\nEOF\n' % (self.subsystem, loggers, self.disable_level))
                f.write('ret=$?\n')
                f.write('if [[ $ret -eq 0 ]]; then echo \"Removed successfully.\"; else echo \"$(date) Error in removing jboss logger.\"; fi')
                f.write('\nfi\n')
            f.write('exit $ret\n')

        self._execute_enable_debug()

    def _execute_enable_debug(self):
        """
        enable the debugging logger
        :param command:No
        :return:
        """
        if Configuration.Jboss_EOCM is True:
            result = self.process('sudo /bin/rm -f /tmp/logger_enable.out > /dev/null 2>&1; sudo bash %s > /tmp/logger_enable.out &' % self.enable_file)
            if result is True:
                Output.green('JBOSS loggers successfully enabled\n')
            else:
                Output.red('Could not enable jboss loggers on %s' % socket.gethostname())
        else:
            Verbose.yellow("Connecting to: hostname = %s\tusername = %s" % (self.vm, Configuration.vm_user_name))
            result = self.process('ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null 2>/dev/null -i %s %s@%s 2>/dev/null "bash %s > /tmp/logger_enable.out &"' % (Configuration.vm_private_key, Configuration.vm_user_name, self.vm, self.enable_file))
            if result is True:
                return True
            else:
                Output.red('Could not access %s' % self.vm)
                return False

    def _execute_disable_debug(self):
        """
        disable the debugging logger
        :param command:No
        :return:
        """
        if Configuration.Jboss_EOCM is True:
            result = self.process('sudo /bin/rm -f /tmp/logger_disable.out > /dev/null 2>&1; sudo bash %s > /tmp/logger_disable.out &' % self.disable_file)
            if result is True:
                Output.green('JBOSS loggers successfully disabled\n')
                Terminal.copy('/tmp/logger_*.out', self.directory)
            else:
                Output.red('Could not disable JBOSS loggers on %s' % socket.gethostname())
        else:
            # remove /tmp/.lcs_debug_enabled
            Verbose.yellow("Connecting to: hostname = %s\tusername = %s" % (self.vm, Configuration.vm_user_name))
            result = self.process('ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i %s %s@%s 2>/dev/null "sudo bash %s > /tmp/logger_disable.out 2>&1 &" > /dev/null' % (Configuration.vm_private_key, Configuration.vm_user_name, self.vm, self.disable_file))
            if result is True:
                Terminal.sub('ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null 2>/dev/null -i %s %s@%s 2>/dev/null "rm -rf /tmp/Loggers_failed /tmp/Loggers_added" > /dev/null 2>&1' % (Configuration.vm_private_key, Configuration.vm_user_name, self.vm))
                Terminal.sub('scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i %s %s@%s:/tmp/logger_*.out %s.LCSMetadata/%s* >/dev/null 2>&1' % (Configuration.vm_private_key, Configuration.vm_user_name, self.vm, Configuration.storing_logs_dir, self.vm))

                if os.path.exists(Configuration.JBoss_plug_in_output_dir + '/' + self.vm) is False:
                    Output.red('\nCould not collect partial log from %s\n' % self.vm)
                    Configuration.Jboss_log_not_collected = True
                return True
            else:
                Terminal.sub('scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i %s %s@%s:/tmp/logger_*.out %s >/dev/null 2>&1' % (Configuration.vm_private_key, Configuration.vm_user_name, self.vm, self.directory))
                Configuration.failed_Jboss_diabled_list = self.vm
                return False

    def check_log_level(self,logger):
        name = ['FINEST', 'FINER', 'TRACE', 'DEBUG', 'FINE', 'CONFIG', 'INFO', 'WARN', 'ERROR', 'SEVERE', 'FATAL', 'OFF']
        if Configuration.Jboss_EOCM is True:
            JBoss_path = os.environ.get('JBOSS_HOME')
            Terminal.system('sudo %s/bin/jboss-cli.sh -c --controller=localhost:12500 /subsystem=logging/logger=%s:read-attribute\(name=level\) > /tmp/check_loggercheck' % (JBoss_path, logger))
            with open('/tmp/check_loggercheck', 'r') as f:
                data = f.read()
                string = data.split('\n')[2].split('=>')
                level = string[1].replace('"', '').strip()
            Terminal.rm('/tmp/check_loggercheck')
            if level in name:
                return level
            else:
                return 'INFO'
        else:
            Terminal.system('ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i %s %s@%s 2>/dev/null "/ericsson/3pp/jboss/bin/jboss-cli.sh -c /subsystem=logging/logger=%s:read-attribute\(name=level\)" > /tmp/check_loggercheck' % (Configuration.vm_private_key, Configuration.vm_user_name, self.vm, logger))
            with open('/tmp/check_loggercheck', 'r') as f:
                data = f.read()
                string = data.split('\n')[2].split('=>')
                level = string[1].replace('"', '').strip()
            Terminal.rm('/tmp/check_loggercheck')
            if level in name:
                return level
            else:
                return 'INFO'

    @staticmethod
    def process(cmd):
        run_command = subprocess.Popen(cmd, shell=True)
        run_command.wait()
        (stdout, stderr) = run_command.communicate()
        if run_command.returncode != 0:
            return False
        return True
