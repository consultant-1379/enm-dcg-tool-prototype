import os

from libs.config_item import ConfigItem
from libs.executors.app_executor.multiple_yaml_files import MultipleFiles
from libs.executors.general_executor import GeneralExecutor
from libs.instance_check import InstanceCheck
from libs.logging.logger import Logger
from libs.logging.verbose import Verbose
from libs.utilities.data_structures.stack import Stack
from libs.utilities.system.terminal import Terminal
from libs.variables.configuration import Configuration



class ConfigExecutor(object):
    def __init__(self, config_dir):
        super(ConfigExecutor, self).__init__()
        InstanceCheck(config_dir)
        self.menu_stack = Stack()
        if os.path.isdir(config_dir[0]) and Configuration.execute_multiple_files is True:
            MultipleFiles(config_dir)
            self.write_pid_to_file()
            for each in Configuration.start_up_file:
                Logger.info('Executing %s' % each)
                first_item = ConfigItem(each)
                self.menu_stack.push(first_item)
        else:
            if type(config_dir) == list:
                first_item = ConfigItem(config_dir[0])
                self.write_pid_to_file()
                self.menu_stack.push(first_item)
            else:
                first_item = ConfigItem(config_dir)
                self.write_pid_to_file()
                self.menu_stack.push(first_item)

    def run(self):
        while (not self.menu_stack.isEmpty()):
            Verbose.green("Menu stack status:\n" + str(self.menu_stack))
            item = self.menu_stack.peek()
            # Execute the data and get another config file
            executor = GeneralExecutor(item, self.menu_stack)
            executor.run()

    def write_pid_to_file(self):
        if Configuration.use_tool_while_instance_running == False:
            Terminal.touch('/tmp/Log_tool_running')
            with open('/tmp/Log_tool_running', 'w') as f:
                f.write(str(os.getpid()))
