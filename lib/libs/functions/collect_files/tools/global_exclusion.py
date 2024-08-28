from libs.logging.logger import Logger
from libs.variables.configuration import Configuration
import os


class GlobalExclusion():

    def __init__(self, check_list):
        if type(check_list) is str:
            check_list = [check_list]
        self.check_list = check_list
        self.file_list = Configuration.exclude_file_paths
        self.ext_list = Configuration.exclude_file_extensions
        if type(self.file_list) is list and len(self.file_list) != 0:
            self._process_files()
        if type(self.ext_list) is list and len(self.ext_list) != 0:
            self._process_extensions()

    def _process_extensions(self):
        no_collect = []
        for each_ext in self.ext_list:
            if str(each_ext).startswith(".") is False:
                each_ext = "." + each_ext
            for each_file in self.check_list:
                if each_file.endswith(each_ext) is True:
                    no_collect.append(each_file)
        yes_collect = [files_to_collect for files_to_collect in self.check_list if files_to_collect not in no_collect]
        if len(no_collect) != 0:
            Logger.info("Files Not collected as a result of Extension Rule: " + str(no_collect))
        self.check_list = yes_collect

    def _process_files(self):
        no_collect = []
        for each_file in self.file_list:
            if str(each_file).__contains__("/"):
                if each_file in self.check_list:
                    self.check_list.remove(each_file)
            else:
                for each_type in self.check_list:
                    if os.path.basename(each_type) == each_file:
                        no_collect.append(each_type)
                        self.check_list.remove(each_type)
        if len(no_collect) != 0:
            Logger.info("Files Not collected as a result of File Exclusion Rule: " + str(no_collect))
            
    def get_output_list(self):
        return self.check_list
