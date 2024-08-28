import os

from libs.utilities.system.terminal import Terminal
from libs.variables.configuration import Configuration
from libs.utilities.system.file_paths import FilePaths
from libs.variables import variables

class ReadPaths():

    def __init__(self):
        """
        Set up the file paths in configuration.py
        :return:
        """
        Configuration.default_path = FilePaths.absolute_path(os.path.join(Configuration.default_main_file,
                                                             FilePaths.pardir(), FilePaths.pardir()))
        Configuration.configuration_dir = FilePaths.join_path(Configuration.default_path,
                                                              variables.config_dir)
        Configuration.lcs_conf_path = FilePaths.join_path(Configuration.configuration_dir,
                                                          variables.lcs_conf_file_name)
        Configuration.database_file = FilePaths.join_path(Configuration.configuration_dir,
                                                          "LCS.db")
        Configuration.old_database_file = FilePaths.join_path(Configuration.configuration_dir,
                                                          ".LCS.db.old")
        Configuration.setup_detail_file = FilePaths.join_path(Configuration.default_path,
                                                              "lib/libs/setup/setup_parameters.yml")
        Configuration.config_files_dir = FilePaths.join_path(Configuration.default_path,
                                                             "etc/ENM/")
        Configuration.scripts_file_path = Configuration.default_path + "/lib/libs/scripts"

        Configuration.tmp_directory = Configuration.default_path + "/lib/libs/utilities/tmp"

        Configuration.network_element_output = Configuration.tmp_directory + "/enm_cli_network_output.txt"

        # default YAML file to be executed (e.g. the LCS main menu)

        ReadPaths.make_log_dir()

        Configuration.log_file_location = FilePaths.join_path(Configuration.default_path, "log/")
    @staticmethod
    def make_log_dir():
        if not FilePaths.isdir(Configuration.default_path + "/log/"):
            Terminal.mkdir(Configuration.default_path + "/log/")