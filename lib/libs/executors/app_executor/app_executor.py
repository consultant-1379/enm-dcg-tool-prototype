import os

from libs.executors.executor_superclass import ExecutorSuperclass
from libs.functions.collate_attach_files.collate_attach_files import CollateAttachFiles
from libs.functions.collect_files.collect_files import CollectFiles
from libs.functions.cp_old_image.cp_old_image import CpOldImage
from libs.functions.ddc_collection.ddc_collection import DDCCollection
from libs.functions.disable_debug.disable_debug import DisableDebug
from libs.functions.enable_debug.enable_debug import EnableDebug
from libs.functions.enm_cli.enm_cli_commands import EnmCliCommands
from libs.functions.enm_cli.tools.check_jid import CheckJID
from libs.functions.enm_cli.tools.refactor_yaml import RefactorYaml
from libs.functions.jboss_debug.jboss_debug import JBOSSDebug
from libs.functions.manual_actions.manual_actions import ManualActions
from libs.functions.exec_additional_conf_file.exec_additional_conf_file import ExecAdditionalConfFile
from libs.functions.unknown_function.unknown_function import UnknownFunction
from libs.functions.commands.commands import Commands
from libs.functions.wait.wait import Wait
from libs.logging.verbose import Verbose
from libs.utilities.data_structures.dictionary import Dictionary
from libs.utilities.file.any_name import AnyName
from libs.utilities.system.file_paths import FilePaths
from libs.utilities.system.terminal import Terminal
from libs.variables.keys import AppKeys, BasicKeys
from libs.variables.configuration import Configuration
import signal


class AppExecutor(ExecutorSuperclass):
    def __init__(self, app_config_item, menu_stack):
        """

        :param app_config_item: An object of the class ConfigItem
        :param menu_stack:
        """
        if self.check_for_eocm is True:
            Configuration.EOCM = True

        Configuration.manual_startYamlFile = False
        yaml_list = []
        yaml_list.append(str(menu_stack).split('/'))
        if Configuration.EOCM is True:
            if 'endEocmYamlFile.yml\n' in yaml_list[0]:
                Configuration.manual_endYamlFile = True
            if 'startEocmYamlFile.yml\n' in yaml_list[0]:
                Configuration.manual_startYamlFile = True
        else:
            if 'endYamlFile.yml\n' in yaml_list[0]:
                Configuration.manual_endYamlFile = True
            if 'startYamlFile.yml\n' in yaml_list[0]:
                Configuration.manual_startYamlFile = True

        app = app_config_item.get_data()
        if (app[BasicKeys.config_type] != AppExecutor.config_type()):
            Terminal.exception("This config was wrongly passed in AppExecutor")
        current_yaml_file = os.path.basename(menu_stack.peek().get_file_path())
        # todo add later [or current_yaml_file == "endYamlFile.yml"]
        if current_yaml_file == "startYamlFile.yml":
            Configuration.log_trigger = False
        else:
            Configuration.log_trigger = True
        Verbose.green("Executing LCS user case: %s\n" % (menu_stack.peek().get_file_path()))
        super(AppExecutor, self).__init__()
        if app_config_item.get_implicit_plugins():
            # implicit plugins are needed to be added
            print "\nPlease Wait..."

            if Configuration.EOCM is True:
                startYamlFile = dict()
                Dictionary.set_value(startYamlFile, AppKeys.func_name, ExecAdditionalConfFile.func_name())
                Dictionary.set_value(startYamlFile, AppKeys.additional_config_file_path,
                                     "/.implicit_plugins/startEocmYamlFile.yml")
                Dictionary.set_value(startYamlFile, AppKeys.storing_log, ".LCSMetadata/startEocmYamlFile")

                endYamlFile = dict()
                Dictionary.set_value(endYamlFile, AppKeys.func_name, ExecAdditionalConfFile.func_name())
                Dictionary.set_value(endYamlFile, AppKeys.additional_config_file_path,
                                     "/.implicit_plugins/endEocmYamlFile.yml")
                Dictionary.set_value(endYamlFile, AppKeys.storing_log, ".LCSMetadata/endEocmYamlFile")
            else:
                startYamlFile = dict()
                Dictionary.set_value(startYamlFile, AppKeys.func_name, ExecAdditionalConfFile.func_name())
                Dictionary.set_value(startYamlFile, AppKeys.additional_config_file_path, "/.implicit_plugins/startYamlFile.yml")
                Dictionary.set_value(startYamlFile, AppKeys.storing_log, ".LCSMetadata/startYamlFile")

                endYamlFile = dict()
                Dictionary.set_value(endYamlFile, AppKeys.func_name, ExecAdditionalConfFile.func_name())
                Dictionary.set_value(endYamlFile, AppKeys.additional_config_file_path,
                                     "/.implicit_plugins/endYamlFile.yml")
                Dictionary.set_value(endYamlFile, AppKeys.storing_log, ".LCSMetadata/endYamlFile")


            original_functions = Dictionary.get_value(app, AppKeys.functions)
            original_functions.insert(0, startYamlFile)
            original_functions.insert(len(original_functions), endYamlFile)
            if Dictionary.get_value(original_functions[1], AppKeys.func_name) == EnmCliCommands.func_name():
                original_functions[1] = CheckJID(original_functions[1]).return_function()
            if Configuration.JID_present is True:
                name = str(Dictionary.get_value(original_functions[1], AppKeys.func_name)).lstrip().rstrip().replace(" ", "_")
                plugin = FilePaths.join_path(Configuration.storing_logs_dir, name)
                original_functions[1][AppKeys.func_log_dir] = plugin
                EnmCliCommands(function=original_functions[1], app=None, config_stack=None).run()
                if Configuration.JID_path is not None:
                    original_functions = RefactorYaml(original_functions).method()

            app_config_item.set_implicit_plugins(False)

        self.app = app_config_item
        self.marker = app_config_item.get_marker()

        self.menu_stack = menu_stack

        function_list = list()

        function_list.append(CollateAttachFiles)
        function_list.append(CollectFiles)
        function_list.append(DisableDebug)
        function_list.append(EnableDebug)
        function_list.append(JBOSSDebug)
        function_list.append(Commands)
        function_list.append(ManualActions)
        function_list.append(ExecAdditionalConfFile)
        function_list.append(Wait)
        function_list.append(DDCCollection)
        function_list.append(EnmCliCommands)
        function_list.append(CpOldImage)

        self.functions = dict()
        for each in function_list:
            self.functions[each.func_name()] = each

    def run(self):
        # check for Ctrl-c press
        signal.signal(signal.SIGINT, self._ctrlC_handler)
        # check for Ctrl-Z press
        signal.signal(signal.SIGTSTP, self._ctrlC_handler)

        # Store the configuration file to report
        if (self.app.get_file_path() != None):
            Terminal.mkdir((Configuration.storing_logs_dir+"/.LCSMetadata"), superuser=True)
            Terminal.cp(self.app.get_file_path(), (Configuration.storing_logs_dir+"/.LCSMetadata"), True)

        func_list = self.app.get_data()[AppKeys.functions][self.marker:]

        for each in func_list:
            # checking for command line instances
            if AnyName.checkfile(each) == True:
                newfunc = AnyName(each).run()
            else:
                newfunc = each
            name = str(Dictionary.get_value(each, AppKeys.func_name)).lstrip().rstrip().replace(" ", "_")
            plugin = FilePaths.join_path(self.app.get_storing_log_dir(), name)
            each[AppKeys.func_log_dir] = plugin
            target = Dictionary.get_value(self.functions, each[AppKeys.func_name], UnknownFunction)
            func = target(newfunc, self.app, self.menu_stack)
            if (func.run() == False):
                break

        self.menu_stack.pop()
        Configuration.vm_name = False

    @staticmethod
    def config_type():
        return "app"

    def _ctrlC_handler(self, sig, frame):
        func_name = dict()
        func_name[AppKeys.func_name] = CollateAttachFiles.func_name()
        func_type = self.app
        stack = self.menu_stack
        CollateAttachFiles(func_name, func_type, stack).run()
        Terminal.rm('/tmp/Log_tool_running')
        Terminal.exit()

    def check_for_eocm(self):
        result = os.system('grep cloud-user /etc/passwd')
        if result is 0:
            return True
        return False
