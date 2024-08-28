from libs.logging.verbose import Verbose
from libs.utilities.system.file_paths import FilePaths
from libs.variables.configuration import Configuration
from libs.utilities.system.output import Output
from libs.utilities.system.terminal import Terminal
import datetime
import os
import glob


class CheckNrOfFiles:

    def __init__(self):
        if not self.check_nr_of_files():
            #Terminal.exception()
            pass

    def check_nr_of_files(self):
        """
        If there are too many files in the dump, the tool cannot be run
        :return:
        """
        # checks if data dump path exists
        if FilePaths.path_exists(Configuration.report_output_dir):

            # year = datetime.datetime.now().year
            # clean_cmd = "sudo rm -rf "+Configuration.report_output_dir+str(year)+"*"+" 2> /dev/null"
            # Terminal.system(clean_cmd)

            # if data dump path does exist only count files that start with the prefix and end with .tar.gz
            # THis is the old way which is not working to get the number of files in output_dir
            #number_of_files = sum([len(files) for r, d, files in os.walk(Configuration.report_output_dir)])
            number_of_files = len(glob.glob1(Configuration.report_output_dir, "lcs_report_*.tar.gz"))

            if number_of_files >= Configuration.max_number_of_reports:
                Output.red('ERROR.', new_line=False), Output.yellow("More reports present (" + str(number_of_files)
                                                                    + ") in " + Configuration.report_output_dir + " than expected ("
                                                                    + str(Configuration.max_number_of_reports)
                                                                    + ").\nRemove old/unwanted reports from " + Configuration.report_output_dir + " and re-run the tool")
                Terminal.exit()
            else:
                return True
        # if the data dump path does not exist
        else:
            Verbose.yellow("Warning the Data dump path does not exist")
            return True