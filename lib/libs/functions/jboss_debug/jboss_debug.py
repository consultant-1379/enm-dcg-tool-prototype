import copy
import os
import signal
import socket

from libs.functions.collate_attach_files.collate_attach_files import CollateAttachFiles
from libs.functions.collect_files.collect_files import CollectFiles
from libs.functions.collect_files.tools.vm.vm_files import VMFiles
from libs.functions.commands.commands import Commands
from libs.functions.commands.tools.vm.vm_commands import VMCommands
from libs.functions.disable_debug.disable_debug import DisableDebug
from libs.functions.enable_debug.enable_debug import EnableDebug
from libs.functions.enable_jboss_commands.enable_jboss_command import JBossCommandController
from libs.functions.function_superclass import FunctionSuperclass
from libs.functions.jboss_debug.tools.vms_jboss_debug_controller import VMsJBossDebugController
from libs.functions.wait.wait import Wait
from libs.logging.logger import Logger
from libs.utilities.data_structures.dictionary import Dictionary
from libs.utilities.data_structures.type_check import TypeCheck
from libs.utilities.system.output import Output
from libs.utilities.system.print_text import Print
from libs.utilities.system.terminal import Terminal
from libs.utilities.system.timing import Timing
from libs.utilities.vms.global_search import GlobalSearch
from libs.utilities.vms.return_servers import ReturnServers
from libs.variables import variables
from libs.variables.configuration import Configuration
from libs.variables.keys import AppKeys


class JBOSSDebug(FunctionSuperclass):
    """description of class"""

    @staticmethod
    def func_name():
        return "JBOSS"

    def __init__(self, function, app, config_stack):
        if not FunctionSuperclass.check_name_equal(function[AppKeys.func_name], JBOSSDebug.func_name()):
            Terminal.exception("This function was wrongly passed in JBOSS")
        time = Dictionary.get_value(function, AppKeys.debug_time, None)
        JBoss_log_path = Dictionary.get_value(function, AppKeys.log_file_paths)
        self.stamp = Timing.strftime()
        self.function = function
        self.app = app
        self.config_stack = config_stack
        # set up the function list
        self.func_list = list()
        self.log_dir = Dictionary.get_value(function, AppKeys.func_log_dir)
        self.Loggers = self._get_loggers()
        Configuration.JBoss_loggers = self.Loggers
        Configuration.JBoss_plug_in_output_dir = self.log_dir
        Configuration.JBoss_time_out = time
        Configuration.JBoss_log_path = JBoss_log_path

        # if timeout = 0 jboss_debug = false then don't run
        self.commands_before()
        if Configuration.jboss_debug:
            # if user has set debug_time to 0 in yaml file then don't run
            if time != 0:
                if self._user_input(time) is True:
                    #################################################################################
                    # Collect TPC_dumps
                    self.filetime = self.stamp
                    cmd_func = copy.deepcopy(function)
                    if Configuration.debug_time is None:
                        time = Dictionary.get_value(function, AppKeys.debug_time,
                                                    default=variables.default_debug_time)
                        if int(time) > int(Configuration.JBoss_maximum_time):
                            time = Configuration.JBoss_maximum_time
                    else:
                        if int(Configuration.jboss_debug) > int(Configuration.JBoss_maximum_time):
                            time = Configuration.JBoss_maximum_time
                        else:
                            time = Configuration.debug_time
                    cmd_func[AppKeys.func_log_dir] = self.log_dir
                    JBossCommandController(cmd_func, time, self.filetime)
                    #################################################################################
                    # Enable loggers
                    enable_func = copy.deepcopy(function)
                    Dictionary.remove_key(enable_func, AppKeys.debug_time)
                    enable_func[AppKeys.func_name] = EnableDebug.func_name()
                    self.func_list.append(EnableDebug(enable_func, app, config_stack))
                    enable_func[AppKeys.func_log_dir] = self.log_dir
                    #################################################################################
                    # Wait for the user to reproduce issues, when it is waiting
                    if Configuration.Jboss_EOCM is not True:
                        wait_func = copy.deepcopy(function)
                        wait_func[AppKeys.func_name] = Wait.func_name()
                        Dictionary.remove_key(wait_func, AppKeys.log_file_paths)
                        wait_func[AppKeys.message] = 'Reproduce issues for "%s"' % app.get_config_name()

                        for each_vm in wait_func[AppKeys.JBoss_servers]:
                            Dictionary.remove_key(each_vm, AppKeys.loggers)
                            Dictionary.remove_key(each_vm, AppKeys.level_value)

                        self.func_list.append(Wait(wait_func, app, config_stack))
                        wait_func[AppKeys.func_log_dir] = self.log_dir
                    #################################################################################
                    # Disable loggers
                    disable_func = copy.deepcopy(function)
                    Dictionary.remove_key(disable_func, AppKeys.debug_time)
                    disable_func[AppKeys.func_name] = DisableDebug.func_name()
                    self.func_list.append(DisableDebug(disable_func, app, config_stack, self.filetime, time))
                    disable_func[AppKeys.func_log_dir] = self.log_dir
                    #################################################################################
                    # create a Commands function that it execute the task of "create a break_loop file" on each VM

                    # get the server list
                    jboss_server_list = Dictionary.get_value(function, AppKeys.JBoss_servers, type=list,
                                                             file_path=app.get_file_path())
                    command_func = ReturnServers.return_vms(
                        jboss_server_list)
                    # convert the server list to a dictionary including VM instances and VM names
                    Dictionary.set_value(command_func, AppKeys.func_name,
                                         Commands.func_name())  # this is a commands function
                    Dictionary.set_value(command_func, AppKeys.server_type, VMCommands.server_type())  # execute on VMs

                    command_func[AppKeys.func_log_dir] = self.log_dir
        else:
            Output.yellow('JBoss Loggers will not be enabled because timeout is set to 0\n')
            self._collect_jboss_files()

    def run(self):
        # check for Ctrl-c press
        signal.signal(signal.SIGINT, self._ctrlC_handler)
        # check for Ctrl-Z press
        signal.signal(signal.SIGTSTP, self._ctrlC_handler)

        for each_func in self.func_list:
            each_func.run()

            # allow 2 seconds for the logger level to be updated
            Timing.sleep(2)

        # To reset all settings to the default:
        Terminal.system("stty sane")

    def _user_input(self, time):
        if self.check_instance_is_localhost() is True:
            Configuration.Jboss_EOCM = True

        if Configuration.yes_to_all is True:
            return True
        else:
            if Configuration.debug_time is not None:
                new_time = Configuration.debug_time
            else:
                new_time = time
            if int(Configuration.plugin_count) > 1:
                # check for Ctrl-c press
                signal.signal(signal.SIGINT, self._ctrlC_handler)
                # check for Ctrl-Z press
                signal.signal(signal.SIGTSTP, self._ctrlC_handler)
            else:
                # check for Ctrl-c press
                signal.signal(signal.SIGINT, self._ctrlC_handler_user_input)
                # check for Ctrl-Z press
                signal.signal(signal.SIGTSTP, self._ctrlC_handler_user_input)
            yes = ['Yes']
            no = ['No']
            if time == 1 or '1' or Configuration.jboss_debug == 1 or '1':
                plural = 'second'
            else:
                plural = 'seconds'
            JBoss = Dictionary.get_value(self.function, AppKeys.JBoss_servers)
            vm_list = []
            level = []
            for each in JBoss:
                instances = Dictionary.get_value(each, AppKeys.instances)
                vm_list.append(instances)
                log_level = Dictionary.get_value(each, AppKeys.loggers)
                level.append(log_level)
            if Configuration.Jboss_EOCM is True:
                Output.yellow('\nThe following JBOSS loggers will be Enabled for %s %s.' % (new_time, plural))
                for each in level[0]:
                    Output.white(each)
                Output.yellow("\nOn the following VM service group:")
                Output.white(socket.gethostname())
                Print.yellow("\n[NOTE] - Enable the logs only if the problem can be reproduced")
                Print.yellow("\n[NOTE] - Enabling the DEBUG log will cause extensive logging for JBoss.")
                Print.yellow("\nDo you want to enable the above loggers for the VM listed")
                Configuration.jboss_is_running = True
            else:
                Print.yellow('\nThe following JBOSS loggers will be Enabled for %s %s.' % (new_time, plural))
                Logger.info('The following JBOSS loggers will be Enabled for %s %s.' % (new_time, plural))
                for each in level[0]:
                    Print.white(each)
                    Logger.info(each)
                Print.yellow("\nOn the following VM instance's or service-groups:")
                Logger.info("On the following VM instance's or service-groups:")
                Print.white(vm_list[0])
                Logger.info(vm_list[0])
                Print.yellow("\n[NOTE] - Enable the logs only if the problem can be reproduced")
                Print.yellow("\n[NOTE] - Enabling the DEBUG log will cause extensive logging for JBoss.")
                Print.yellow("\nDo you want to enable the above loggers for each VM instance/service-group listed")
                Configuration.jboss_is_running = True
            while True:
                Print.yellow("Answer [Yes] to confirm or [No]:")
                ans = Terminal.input('')
                Logger.info(ans)
                if ans in yes:
                    Configuration.plugin_count = int(Configuration.plugin_count) + 1
                    Configuration.JBoss_ans_true = True
                    return True
                elif ans in no:
                    Configuration.jboss_debug = False
                    Output.yellow('JBoss Loggers will not be enabled')
                    self._collect_jboss_files()
                    self.commands_after()
                    return False
                else:
                    Output.red('Invalid input')

    def _ctrlC_handler(self, sig, frame):
        if Configuration.jboss_debug is True and Configuration.JBoss_ans_true is True and Configuration.Jboss_EOCM is not True:
            debug = VMsJBossDebugController(self.function[AppKeys.JBoss_servers])
            Output.yellow('\nDisabling JBOSS debugging loggers, please wait...')
            successful_vms = debug.disable_debug()
            if len(successful_vms) == 0:
                Output.yellow("No JBoss loggers from VM instances have been disabled.")
            elif len(successful_vms) == 1:
                Output.green("JBoss loggers from the VM instance %s has been disabled" % (successful_vms[0]))
            else:
                Output.green("The JBoss loggers from the following VM instances have been disabled")

                for each_vm in successful_vms:
                    Output.white("%s\t" % each_vm, new_line=False)
            func_name = dict()
            func_name[AppKeys.func_name] = CollateAttachFiles.func_name()
            func_type = self.app
            stack = self.config_stack
            Terminal.system('touch /tmp/.CtrlC')
            CollateAttachFiles(func_name, func_type, stack, True).run()
            if len(Configuration.failed_Jboss_diabled_list) == 0:
                Terminal.system('sudo rm %s/log/.lastRun/.lastRunRecord' % Configuration.default_path)
            Terminal.rm('/tmp/Log_tool_running')
            Terminal.exit(0)
        elif Configuration.Jboss_EOCM is True:
            # Disable loggers
            disable_func = copy.deepcopy(self.function)
            Dictionary.remove_key(disable_func, AppKeys.debug_time)
            disable_func[AppKeys.func_name] = DisableDebug.func_name()
            self.func_list.append(DisableDebug(disable_func, self.app, self.config_stack, self.filetime, '20'))
            disable_func[AppKeys.func_log_dir] = self.log_dir
        else:
            func_name = dict()
            func_name[AppKeys.func_name] = CollateAttachFiles.func_name()
            func_type = self.app
            stack = self.config_stack
            Terminal.system('touch /tmp/.CtrlC')
            Terminal.rm('/tmp/Log_tool_running')
            CollateAttachFiles(func_name, func_type, stack, True).run()
            Terminal.exit(0)

    def _ctrlC_handler_user_input(self, sig, frame):
        Terminal.system('touch /tmp/.CtrlC')
        Terminal.rm('/tmp/Log_tool_running')
        Terminal.exit(0)

    def _get_loggers(self):
        JBoss = (self.function[AppKeys.JBoss_servers])
        Loggers = Dictionary.get_value(JBoss[0], AppKeys.loggers)
        return Loggers

    def _collect_jboss_files(self):
        #################################################################################
        # Collect files from the VMs
        Configuration.jboss_debug = True
        collect_func = copy.deepcopy(self.function)
        Dictionary.remove_key(collect_func, AppKeys.debug_time)
        collect_func[AppKeys.func_name] = CollectFiles.func_name()
        collect_func[AppKeys.server_type] = VMFiles.server_type()
        collect_func[AppKeys.files] = Dictionary.get_value(collect_func, AppKeys.log_file_paths,
                                                           default=variables.JBoss_logs)
        #######################################
        if type(collect_func[AppKeys.files]) is str:
            collect_func[AppKeys.files] = [collect_func[AppKeys.files]]

        func_instances = list()
        jboss_servers = Dictionary.get_value(collect_func, AppKeys.JBoss_servers, type=list)
        for each in jboss_servers:
            instances = Dictionary.get_value(each, AppKeys.instances)
            if type(instances) == str:
                instances = [instances]
            TypeCheck.list(instances)
            func_instances += instances

        collect_func[AppKeys.instances] = func_instances
        Dictionary.remove_key(collect_func, AppKeys.log_file_paths)
        Dictionary.remove_key(collect_func, AppKeys.debug_time)
        Dictionary.remove_key(collect_func, AppKeys.JBoss_servers)
        self.func_list.append(CollectFiles(collect_func, self.app, self.config_stack))

    def commands_before(self):
        if os.path.exists(Configuration.storing_logs_dir + '.LCSMetadata/') is not True:
            Terminal.mkdir(Configuration.storing_logs_dir + '.LCSMetadata/')
        Terminal.copy(Configuration.default_path + '/lib/libs/scripts/jboss_pre_cmd.bsh',
                      Configuration.storing_logs_dir + '.LCSMetadata/')
        if os.stat(Configuration.default_path + '/lib/libs/scripts/.bf_vm_command_list').st_size is not 0:
            Terminal.copy(Configuration.default_path + '/lib/libs/scripts/.bf_vm_command_list',
                          Configuration.storing_logs_dir + '.LCSMetadata/')
            path_to_script = Configuration.storing_logs_dir + '.LCSMetadata/jboss_pre_cmd.bsh'
            path_to_file = Configuration.storing_logs_dir +'.LCSMetadata/.bf_vm_command_list'
            jboss_servers = Dictionary.get_value(self.function, AppKeys.JBoss_servers)
            instances = Dictionary.get_value(jboss_servers[0], AppKeys.instances)
            self.vms = GlobalSearch(instances).get_correct_list()
            for each in self.vms:
                if os.path.exists(Configuration.storing_logs_dir + 'JBOSS/%s_cmd/' % each) is not True:
                    Terminal.mkdir(Configuration.storing_logs_dir + 'JBOSS/%s_cmd/' % each)
                output_file = Configuration.storing_logs_dir + 'JBOSS/%s_cmd/before_jboss_vm_commands.out' % each
                result = Terminal.system('ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null 2>/dev/null -i %s %s@%s 2>/dev/null "sudo bash %s %s %s &"' % (Configuration.vm_private_key, Configuration.vm_user_name, each, path_to_script, path_to_file, output_file))
                if result == 0:
                    Logger.info("commands running on VM's before jboss is enabled")
                else:
                    Logger.warning("commands not running on VM's before jboss is enabled")
        else:
            Logger.info('.bf_vm_command_list file is empty, commands will not be run before Jboss')

    def commands_after(self):
        if os.path.exists(Configuration.storing_logs_dir + '.LCSMetadata/') is not True:
            Terminal.mkdir(Configuration.storing_logs_dir + '.LCSMetadata/')
            Terminal.copy(Configuration.default_path + '/lib/libs/scripts/jboss_pre_cmd.bsh',
                      Configuration.storing_logs_dir + '.LCSMetadata/')
        if os.stat(Configuration.default_path + '/lib/libs/scripts/.af_vm_command_list').st_size is not 0:
            Terminal.copy(Configuration.default_path + '/lib/libs/scripts/.af_vm_command_list',
                          Configuration.storing_logs_dir + '.LCSMetadata/')
            path_to_script = Configuration.storing_logs_dir + '.LCSMetadata/jboss_pre_cmd.bsh'
            path_to_file = Configuration.storing_logs_dir +'.LCSMetadata/.af_vm_command_list'
            jboss_servers = Dictionary.get_value(self.function, AppKeys.JBoss_servers)
            instances = Dictionary.get_value(jboss_servers[0], AppKeys.instances)
            self.vms = GlobalSearch(instances).get_correct_list()
            for each in self.vms:
                if os.path.exists(Configuration.storing_logs_dir + 'JBOSS/%s_cmd/' % each) is not True:
                    Terminal.mkdir(Configuration.storing_logs_dir + 'JBOSS/%s_cmd/' % each)
                output_file = Configuration.storing_logs_dir + 'JBOSS/%s_cmd/after_jboss_vm_commands.out' % each
                result = Terminal.system('ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null 2>/dev/null -i %s %s@%s 2>/dev/null "sudo bash %s %s %s &"' % (Configuration.vm_private_key, Configuration.vm_user_name, each, path_to_script, path_to_file, output_file))
                if result == 0:
                    Logger.info("commands running on VM's after jboss is enabled")
                else:
                    Logger.warning("commands not running on VM's after jboss is enabled")
        else:
            Logger.info('.af_vm_command_list file is empty, commands will not be run after Jboss')

    def check_instance_is_localhost(self):
        Jboss_servers = Dictionary.get_value(self.function, AppKeys.JBoss_servers)
        instance = Dictionary.get_value(Jboss_servers[0], AppKeys.instances)
        if 'localhost' in instance:
            return True
        return False