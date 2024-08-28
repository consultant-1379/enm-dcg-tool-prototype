import glob
import os
import sys

import yaml

from libs.logging.logger import Logger
from libs.utilities.system.output import Output
from libs.utilities.system.print_text import Print
from libs.utilities.system.terminal import Terminal
from libs.variables.configuration import Configuration


class MultipleFiles:

    def __init__(self, directory):
        self.path = directory[0]
        self.files = self.chech_for_yaml_files()
        if self.check_for_ftp_upload() is True:
            self.check_if_want_to_execute()
            path_of_files = self.get_full_path()
            Configuration.start_up_file = path_of_files
        else:
            self.exit_function()

    def chech_for_yaml_files(self):
        new = list()
        files_only = glob.glob(self.path + '/*.yml*')
        yamlfile = self.extract_filename(files_only)
        new.append(yamlfile)
        files = []
        for each in new[0]:
            try:
                config = yaml.load(open(self.path + '/' + str(each) + '.yml'))
                if config['config_type'] == 'app':
                    files.append(each)
            except:
                pass
        return files

    def get_full_path(self):
        dir_list = []
        for each in self.files:
            dir_list.append(self.path + '/' + each + '.yml')
        return dir_list

    def check_if_want_to_execute(self):
        if Configuration.yes_to_all is True:
            Logger.info('The directory you have provided has %s Yaml user cases and will '
                        'be executed one after another' % len(self.files))
        else:
            Output.yellow('The directory you have provided has %s Yaml user cases and will'
                          ' be executed one after another' % len(self.files))
            while True:
                Print.yellow('Are you sure to want to proceed? Answer [Yes] or [No]:')
                ans = Terminal.input('')
                if ans == 'Yes':
                    break
                elif ans == 'No':
                    sys.exit(0)
                else:
                    Output.red('Invaild Entry')

    @staticmethod
    def extract_filename(paths):
        newlist = list()
        for each in paths:
            yaml_files = os.path.splitext(each)[0]
            file_name = os.path.basename(yaml_files)
            newlist.append(file_name)
        return newlist

    @staticmethod
    def check_for_ftp_upload():
        if Configuration.Automatic_upload is True:
            if Configuration.ftp_url is not 'None' or None and Configuration.ftp_username is not 'None' \
                    or None and Configuration.ftp_password is not None:
                return True
            else:
                return False
        else:
            return False

    @staticmethod
    def exit_function():
        Output.red('ftp upload must be configured to run multiple Yaml user case files')
        Output.red('please run /opt/ericsson/lcs/bin/log_collection.bsh --setup to rectify this')
        sys.exit(0)
