from libs.logging.verbose import Verbose
from libs.utilities.system.file_paths import FilePaths
from libs.variables.configuration import Configuration
from libs.utilities.system.output import Output
from libs.utilities.system.terminal import Terminal
import datetime
import os
import glob
import shutil
import time

class CleanUpOutputDir:

    def __init__(self):
        if not self.Clean_output_dir():
            #Terminal.exception()
            pass

    def Clean_output_dir(self):
        """
        If there is any other file other than .tar/gzdd
        :return:
        """
        # checks if data dump path exists
        if FilePaths.path_exists(Configuration.report_output_dir):
            file_list = glob.glob1(Configuration.report_output_dir, "202*")
            now = time.time()
            for filename in file_list:
                dir_path = os.path.join(Configuration.report_output_dir, filename)
                if os.stat(dir_path).st_mtime < now - 1 * 3600:
                    if os.path.isdir(dir_path):
                        try:
                            shutil.rmtree(dir_path)
                        except OSError as e:
                            pass
            return True
        # if the data dump path does not exist
        else:
            Verbose.yellow("Warning the Data dump path does not exist")
            return True
