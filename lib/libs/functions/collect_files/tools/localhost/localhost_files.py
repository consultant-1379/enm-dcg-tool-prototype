import os
import socket
import subprocess

from libs.functions.collect_files.tools.collect_files_superclass import CollectFilesSuperclass
from libs.functions.collect_files.tools.global_exclusion import GlobalExclusion
from libs.functions.function_superclass import FunctionSuperclass
from libs.logging.logger import Logger
from libs.utilities.data_structures.dictionary import Dictionary
from libs.utilities.system.file_paths import FilePaths
from libs.utilities.system.output import Output
from libs.utilities.system.print_text import Print
from libs.utilities.system.terminal import Terminal
from libs.variables.configuration import Configuration
from libs.variables.keys import AppKeys


class LocalhostFiles(CollectFilesSuperclass):

    def __init__(self, function):
        func = Dictionary.get_value(function, AppKeys.server_type)
        if (not FunctionSuperclass.check_name_equal(func,LocalhostFiles.server_type())):
            Terminal.exception("This function was wrongly passed in LocalhostFiles")

        # collect local host files
        if Configuration.EOCM is True:
            self.log_dir = FilePaths.join_path(Dictionary.get_value(function, AppKeys.func_log_dir)
                                               , socket.gethostname())
        else:
            self.log_dir = FilePaths.join_path(Dictionary.get_value(function, AppKeys.func_log_dir)
                                           , LocalhostFiles.server_type())
        self.files = Dictionary.get_value(function, AppKeys.files)
        if type(self.files) is str:
            self.files = [self.files]
        self.limit = str(Configuration.max_file_size)

        # print trigger for startYAML
        self.print_trigger = True
        if Configuration.manual_startYamlFile is True:
            self.print_trigger = False

    @staticmethod
    def server_type():
        return 'localhost'

    def run(self):
        if Configuration.EOCM is True:
            Output.yellow("Collecting files on the %s" % socket.gethostname(),  print_trigger=self.print_trigger)
        else:
            Output.yellow("Collecting files on the localhost", print_trigger=self.print_trigger)
        not_exists_files = []; large_files = []; more_dir = []; successful_files = []
        for each in self.files:
            command_to_exec = "for file in $(find " + each + " -type f -exec du -h --block-size=M \"{}\" + |" \
                              "perl -pi -e 's|([0-9]+)[A-Z]+.(/.+)|$1%$2|g'); do size=$(echo $file |" \
                              "awk -F '%' '{print $1}'); name=$(echo $file | awk -F '%' '{print $2}');" \
                              "if [[ $size -le "+self.limit+" ]]; then echo $file; else echo \"TOO LARGE $file\"; fi; done"
            if FilePaths.isdir(each):
                files_to_collect = []
                pipe = subprocess.Popen(command_to_exec, shell=True, stdout=subprocess.PIPE).stdout
                reply = pipe.read()
                if reply.__contains__("TOO LARGE"):
                    more_dir.append(each)
                out_list = reply.splitlines(False)
                for line in out_list:
                    file_name = line.split("%", 1)[1]
                    if line.__contains__("TOO LARGE"):
                        large_files.append(file_name)
                    else:
                        files_to_collect.append(file_name)
                files_to_collect = GlobalExclusion(files_to_collect).get_output_list()
                for each_file in files_to_collect:
                    each = self.check_for_extension(each_file, self.print_trigger)
                    refined_path = os.path.abspath(os.path.join(str(each), os.pardir))
                    addon_dir = self.log_dir + refined_path
                    Terminal.mkdir(addon_dir, True)
                    Terminal.cp(each, FilePaths.join_path(Configuration.storing_logs_dir, addon_dir))
                    successful_files.append(each)

            elif FilePaths.is_file(each):
                pipe = subprocess.Popen(command_to_exec, shell=True, stdout=subprocess.PIPE).stdout
                reply = pipe.read()
                if reply.__contains__("TOO LARGE") is True:
                    large_files.append(each)
                    continue
                else:
                    correct_output = GlobalExclusion(each).get_output_list()
                    if len(correct_output) != 0:
                        for each_file in correct_output:
                            each = self.check_for_extension(each_file, self.print_trigger)
                            refined_path = os.path.abspath(os.path.join(str(each), os.pardir))
                            addon_dir = self.log_dir + refined_path
                            Terminal.mkdir(addon_dir, True)
                            Terminal.cp(each, FilePaths.join_path(Configuration.storing_logs_dir, addon_dir))
                            successful_files.append(each)
            else:
                not_exists_files.append(each)
                continue
        if len(large_files) != 0:
            Output.yellow("\nCannot Collect all files as some Exceed size Limit [%sMB]:" % str(Configuration.max_file_size), print_trigger=self.print_trigger)
            Logger.info("Files Too Large(Not Collected)" + str(large_files))
        if len(not_exists_files) != 0:
            Output.yellow("\n\nCould not locate the following Files/Directory's [%s]" % not_exists_files, print_trigger=self.print_trigger)
            Logger.info("Files Not Found" + str(not_exists_files))
        if Configuration.EOCM is True:
            Output.green('File Collection succeed on %s\n\n' % socket.gethostname(), print_trigger=self.print_trigger)
        else:
            Output.green('File Collection succeed on localhost\n\n', print_trigger=self.print_trigger)

    @staticmethod
    def check_for_extension(file_path, print_trigger):
        if str(file_path).find("||") != -1:
            new_argument = str(file_path).split("||")[1]
            new_string = str(file_path).split("||")[0]
            if new_argument == "LATEST":
                command_to_exec = "ls -lart " + new_string + " | awk '{print $NF}' | tail -1"
                pipe = subprocess.Popen(command_to_exec, shell=True, stdout=subprocess.PIPE).stdout
                new_path = pipe.read()
                pipe.close()
                if new_path is not None:
                    new_path = new_path.strip()
                    return new_path
            else:
                Print.yellow("\nfile has prefix (||) but NOT extension", trigger=print_trigger)
                Print.yellow("File will not be tarred\n", trigger=print_trigger)
                return file_path
        else:
            return file_path
