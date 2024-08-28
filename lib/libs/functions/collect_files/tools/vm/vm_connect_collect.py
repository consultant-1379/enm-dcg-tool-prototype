import os
import subprocess

from libs.functions.collect_files.tools.global_exclusion import GlobalExclusion
from libs.logging.logger import Logger
from libs.logging.verbose import Verbose
from libs.utilities.data_structures.dictionary import Dictionary
from libs.utilities.data_structures.type_check import TypeCheck
from libs.utilities.system.output import Output
from libs.utilities.system.print_text import Print
from libs.utilities.system.terminal import Terminal
from libs.variables.configuration import Configuration
from libs.variables.keys import AppKeys


class VMConnectCollect:

    def __init__(self, dictionary, function):
        """

        :param dictionary: individual instance dictionary
        :param function: first original dictionary
        """
        self.instance_name = dictionary[AppKeys.instance]
        files = dictionary[AppKeys.files]
        self.files = files
        if type(self.files) is str:
            self.files = [self.files]
        for each in self.files:
            if str(each).__contains__("server.log"):
                if self.check_for_files() is True and Configuration.jboss_is_running is True:
                    if str(each).__contains__("||"):
                        before = str(each).split("||")[0]
                        after = str(each).split("||")[1]
                        each = before+".*"+"||"+after
                    else:
                        each = each + ".*"
        self.log_dir = Dictionary.get_value(function, AppKeys.func_log_dir)
        self.limit = str(Configuration.max_file_size)
        self.size_script_name = "collect_files_size_limit_check.bsh"
        self.size_limit_script = Configuration.scripts_file_path + "/%s" % self.size_script_name
        self.type_script_name = "file_type_check.bsh"
        self.type_script_path = Configuration.scripts_file_path + "/%s" % self.type_script_name

        # print trigger for startYAML
        self.print_trigger = True
        if Configuration.manual_startYamlFile is True:
            self.print_trigger = False

    def check_for_extension(self, file_path):
        if str(file_path).find("||") != -1:
            new_argument = str(file_path).split("||")[1]
            new_string = str(file_path).split("||")[0]
            if new_argument == "LATEST":
                command_to_exec = "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i "+Configuration.vm_private_key+" cloud-user@"+self.instance_name+" ls -lart "+new_string+\
                                  " | awk '{print $NF}' | tail -1 > /dev/null 2>&1"
                try:
                    pipe = subprocess.Popen(command_to_exec, shell=True, stdout=subprocess.PIPE).stdout
                    new_path = pipe.read()
                    pipe.close()
                    if new_path is not None:
                        new_path = new_path.strip()
                        return new_path
                except:
                    pass
            else:
                Print.yellow("\nfile has prefix (||) but NOT extension")
                Print.yellow("File will not be tarred\n")
                return file_path
        else:
            return file_path

    def run(self):
        not_exists_files = []; large_files = []; more_dir = []; successful_files = []
        Verbose.green('Collecting files from hostname = %s' % self.instance_name)
        TypeCheck.list(self.files, AppKeys.log_file_paths)
        for each_file_or_dir in self.files:

            file_type_cmd = "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i %s %s@%s 2>/dev/null \" sudo bash /tmp/%s '%s'\"" % \
                            (Configuration.vm_private_key,Configuration.vm_user_name, self.instance_name, self.type_script_name, each_file_or_dir)
            scp_size_command = "scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null > /dev/null 2>&1 -i %s %s %s@%s:/tmp/ " \
                               % (Configuration.vm_private_key, self.size_limit_script,
                                  Configuration.vm_user_name, self.instance_name)
            scp_type_command = "scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null > /dev/null 2>&1 -i %s %s %s@%s:/tmp/ " \
                               % (Configuration.vm_private_key, self.type_script_path,
                                  Configuration.vm_user_name, self.instance_name)
            file_size_cmd = "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i %s %s@%s 2>/dev/null \" sudo bash /tmp/%s '%s' '%s'\"" \
                            % (Configuration.vm_private_key, Configuration.vm_user_name,
                               self.instance_name, self.size_script_name, each_file_or_dir, Configuration.max_file_size)
            Terminal.system(scp_type_command)
            pipe = subprocess.Popen(file_type_cmd, shell=True, stdout=subprocess.PIPE).stdout
            type_cmd = pipe.read().splitlines()
            pipe.close()
            type_stdout = type_cmd
            if type_stdout[0].__contains__("type-directory"):
                files_to_collect = []
                Terminal.system(scp_size_command)
                pipe2 = subprocess.Popen(file_size_cmd, shell=True, stdout=subprocess.PIPE).stdout
                size_cmd = pipe2.read().splitlines()
                pipe2.close()
                size_stdout = size_cmd
                if len(size_stdout) == 0:
                    not_exists_files.append(each_file_or_dir)
                elif any("TOO LARGE" in substring for substring in size_stdout) is True:
                    more_dir.append(each_file_or_dir)
                for each_file in size_stdout:
                    file_name = each_file.split("%", 1)[1]
                    if str(each_file).__contains__("TOO LARGE"):
                        large_files.append(file_name)
                    else:
                        files_to_collect.append(file_name.strip())
                files_to_collect = GlobalExclusion(files_to_collect).get_output_list()
                for file in files_to_collect:
                    each = file.strip()
                    refined_path = os.path.abspath(os.path.join(str(each), os.pardir))
                    addon_dir = self.log_dir + "/" + self.instance_name + refined_path
                    Terminal.system("sudo mkdir -p %s" % (addon_dir))
                    out_file = os.path.basename(file).strip()

                    cp_cmd = 'ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i %s %s@%s 2>/dev/null \"sudo cp -a -p --force %s %s > /dev/null 2>&1\"' % (Configuration.vm_private_key,
                              Configuration.vm_user_name, self.instance_name, each, addon_dir)
                    exit_status = Terminal.system(cp_cmd)

                    if exit_status == 0:
                        out_file_dir = addon_dir + "/" + out_file
                        check_compression = subprocess.Popen("file %s" % (str(out_file_dir)), shell=True, stdout=subprocess.PIPE).stdout
                        response = check_compression.read().splitlines()
                        check_compression.close()
                        if str(response).__contains__("compressed data") is False:
                            Terminal.system("sudo gzip %s --force" % out_file_dir)
                    successful_files.append(each)

            elif type_stdout[0].__contains__("type-file"):
                Terminal.system(scp_size_command)
                pipe5 = subprocess.Popen(file_size_cmd, shell=True, stdout=subprocess.PIPE).stdout
                size_cmd2 = pipe5.read().splitlines()
                pipe5.close()
                size_stdout2 = size_cmd2
                if str(size_stdout2[0]).__contains__("TOO LARGE"):
                    large_files.append(size_stdout2[0].split("%")[1])
                    continue
                else:
                    correct_output = GlobalExclusion(each_file_or_dir).get_output_list()
                    if len(correct_output) != 0:
                        for each_file in correct_output:
                            each = self.check_for_extension(each_file)
                            refined_path = os.path.abspath(os.path.join(str(each), os.pardir))
                            addon_dir = self.log_dir + "/" + self.instance_name + refined_path
                            out_file = os.path.basename(each_file).strip()
                            Terminal.system("sudo mkdir -p %s" % (addon_dir))

                            cp_cmd = 'ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i %s %s@%s 2>/dev/null \"sudo cp -a -p --force %s %s > /dev/null 2>&1\" > /dev/null 2>&1' % (Configuration.vm_private_key,
                                      Configuration.vm_user_name, self.instance_name, each, addon_dir)
                            exit_status = Terminal.system(cp_cmd)
                            if exit_status == 0:
                                out_file_dir = addon_dir + "/" + out_file
                                check_compression = subprocess.Popen("file %s" % (str(out_file_dir)), shell=True,
                                                                     stdout=subprocess.PIPE).stdout
                                response = check_compression.read().splitlines()
                                check_compression.close()
                                for each in response:
                                    path = each.split(":")[0]
                                    if str(each).__contains__("compressed data") is False:
                                        Terminal.system("sudo gzip %s --force" % path)
                                successful_files.append(each)
            elif type_stdout[0].__contains__("type-neither"):
                not_exists_files.append(each_file_or_dir)

        if len(large_files) != 0:
            Output.yellow("\nCannot Collect all files as some Exceed size Limit [%sMB]:" % (
                str(Configuration.max_file_size)), print_trigger=self.print_trigger)
            Logger.info("Files Too Large(Not Collected)" + str(large_files))
        if len(not_exists_files) != 0:
            Output.yellow("\nCould not locate the following Files/Directory's %s on VM [%s]:" % (not_exists_files,self.instance_name), print_trigger=self.print_trigger)
            Logger.info("Files Not Found" + str(not_exists_files))

        if len(not_exists_files) == len(self.files):
            return False
        else:
            return True

    def check_for_files(self):
        result = os.system('ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i %s %s@%s 2>/dev/null "find /ericsson/3pp/jboss/standalone/log/server.log.1" > /dev/null 2>&1' % (
                Configuration.vm_private_key, Configuration.vm_user_name, self.instance_name))
        if result == 0:
            return True
        return False
