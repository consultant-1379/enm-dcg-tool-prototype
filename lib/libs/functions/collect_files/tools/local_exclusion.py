from libs.logging.logger import Logger
from libs.utilities.data_structures.dictionary import Dictionary
from libs.utilities.file.file_reader import FileReader
from libs.utilities.system.file_paths import FilePaths
from libs.utilities.vms.global_search import GlobalSearch
from libs.variables.configuration import Configuration
import os


# may be used later however will not operate right now. vm and local should work however peer is not complete
class LocalExclusion():

    def __init__(self, check_list, collection_type, instance=False):
        if type(check_list) is str:
            check_list = [check_list]
        self.instance = instance
        self.check_list = check_list
        self._vm = "vm"; self._peer = "peer"; self._localhost = "localhost"
        self.file_dir = FilePaths.join_path(Configuration.configuration_dir, "local_excluded_files.yml")
        if FilePaths.is_file(self.file_dir):
            self.local_dictionary = FileReader(self.file_dir).get()
            self.local_dictionary = Dictionary.get_value(self.local_dictionary, "Local_Exclusion")
            for each in self.local_dictionary:
                if each == "local_files":
                    self.files = Dictionary.get_value(self.local_dictionary, "local_files")
                elif each == "local_extensions":
                    self.extensions = Dictionary.get_value(self.local_dictionary, "local_extensions")
            if collection_type == self._localhost:
                self.localhost_files()
                self.localhost_extension()
            elif collection_type == self._vm:
                self.vm_files()
                self.vm_extension()
            elif collection_type == self._peer:
                pass
                # self.peer_files()
                # self.peer_extensions()
        else:
            Logger.info("No Local Exception File")

    def _files_processing(self, file_list):
        for each_file in file_list:
            if str(each_file).__contains__("/"):
                if each_file in self.check_list:
                    self.check_list.remove(each_file)
            else:
                for each_type in self.check_list:
                    if os.path.basename(each_type) == each_file:
                        self.check_list.remove(each_type)

    def _extension_processing(self, extension_list):
        no_collect = []
        for each_ext in extension_list:
            if str(each_ext).startswith(".") is False:
                each_ext = "." + each_ext
            for each_file in self.check_list:
                each_file = each_file
                if each_file.endswith(each_ext) is True:
                    no_collect.append(each_file)
        yes_collect = [files_to_collect for files_to_collect in self.check_list if files_to_collect not in no_collect]
        self.check_list = yes_collect

    def localhost_files(self):
        for each_file in self.files:
            if self._localhost in each_file.keys():
                self.local_files = Dictionary.get_value(each_file, self._localhost)
        if type(self.local_files) is str:
            self.local_files = [self.local_files]
        self._files_processing(self.local_files)

    def localhost_extension(self):
        for each_ext in self.extensions:
            if self._localhost in each_ext.keys():
                self.local_extension = Dictionary.get_value(each_ext, self._localhost)
        if type(self.local_extension) is str:
            self.local_extension = [self.local_extension]
        self._extension_processing(self.local_extension)

    def vm_files(self):
        for each_server in self.files:
            if self._vm in each_server.keys():
                instances = Dictionary.get_value(each_server, self._vm)
                for each_service in instances:
                    vm_instances = GlobalSearch(each_service.keys()[0]).get_correct_list()
                    if self.instance in vm_instances:
                        vm_files = Dictionary.get_value(each_service, each_service.keys()[0])
                        if type(vm_files) is str:
                            vm_files = [vm_files]
                        self._files_processing(vm_files)

    def vm_extension(self):
        for each_server in self.extensions:
            if self._vm in each_server.keys():
                instances = Dictionary.get_value(each_server, self._vm)
                for each_service in instances:
                    vm_instances = GlobalSearch(each_service.keys()[0]).get_correct_list()
                    if self.instance in vm_instances:
                        vm_extensions = Dictionary.get_value(each_service, each_service.keys()[0])
                        if type(vm_extensions) is str:
                            vm_extensions = [vm_extensions]
                        self._extension_processing(vm_extensions)

    def peer_files(self):
        pass

    def peer_extension(self):
        pass

    def get_output_list(self):
        return self.check_list
