from libs.utilities.system.file_paths import FilePaths
from libs.utilities.system.print_text import Print
from libs.variables.configuration import Configuration
import os


class StartUpMsg():

    @staticmethod
    def message():

        file_path = 'startup_msg'

        filePresent = FilePaths.path_exists(FilePaths.join_path(Configuration.configuration_dir, file_path))
        if (filePresent == True):
            try:
                with open(FilePaths.join_path(Configuration.configuration_dir, file_path), 'r') as fileRead:
                    data = fileRead.read()
                    Print.red(data)
                if os.path.exists(Configuration.default_path + '/etc/.upgrade_conf') == True:
                    with open(Configuration.default_path + '/etc/.upgrade_conf', 'r') as f:
                        data = f.read()
                        Print.yellow(data)
            except:
                pass
