import os
import time
import yaml

from libs.executors.menu_executor.dynamic_menu import DynamicMenu
from libs.utilities.data_structures.dictionary import Dictionary
from libs.utilities.system.file_paths import FilePaths
from libs.utilities.system.output import Output
from libs.utilities.system.terminal import Terminal
from libs.variables.configuration import Configuration
from libs.variables.keys import AppKeys


class InstanceCheck:

    def __init__(self, yaml_file):
        self.time = time.strftime('%Y%m%d%H%M')
        self.path = self.path = Configuration.default_path + '/log/.lastRun/'
        if os.path.exists(self.path) is True:
            if type(yaml_file) is list:
                self.file = yaml_file[0]
            else:
                self.file = yaml_file
            if len(self.check_for_files()) > 0:
                self.func = self.read_file()
                if AppKeys.JBoss_servers in self.func:
                    self.function = Dictionary.get_value(self.func, AppKeys.functions)
                    self.jboss = Dictionary.get_value(self.function[0], AppKeys.JBoss_servers)
                    self.instances = Dictionary.get_value(self.jboss[0], AppKeys.instances)
                    self.check()

    def check(self):
        for each in self.check_for_files():
            with open(self.path + each) as f:
                instance = f.readline().strip()
            if self.check_both_lists(instance.split(','), self.instances) is True:
                time_list = each.split('_')
                time = int(time_list[1]) - int(self.time)

                Output.red('Another JBoss plugin is currently enabled on the same vm your are trying to enable.')
                Output.red('Wait %s minutes until it is complete or run another user case' % time)
                if Configuration.dynamic_menu is True:
                    Terminal.any_input()
                    DynamicMenu(Configuration.menu_next_list)
                    break
                else:
                    Terminal.exit()

    def read_file(self):
        with open(self.file, 'r') as stream:
            try:
                yaml_func = (yaml.safe_load(stream))
                return yaml_func
            except:
                Output.red("Yaml file %s can't be read" % self.file)

    def check_for_files(self):
        run_files_list = []
        time_to_check = int(self.time) - 1
        files_list = os.listdir(self.path)
        for each in files_list:
            if int(each.split('_')[1]) > time_to_check:
                run_files_list.append(each)
        return run_files_list

    @staticmethod
    def check_both_lists(list_from_file, list_from_yaml):
        print list_from_file
        print list_from_yaml
        check = any(item in list_from_file for item in list_from_yaml)
        if check is True:
            return True
        return False

    @staticmethod
    def get_default_path():
        Configuration.default_path = FilePaths.absolute_path(os.path.join(Configuration.default_main_file,
                                                                          FilePaths.pardir(), FilePaths.pardir()))
