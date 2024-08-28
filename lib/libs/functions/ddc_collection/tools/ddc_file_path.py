import glob
import os

from libs.logging.verbose import Verbose
from libs.utilities.system.file_paths import FilePaths
from libs.utilities.system.timing import Timing
from libs.variables.configuration import Configuration


class DDCFilePath():

    @staticmethod
    def get_ddc_file_path(ddc_file_directory):
        delta = Timing(minutes=Configuration.DDC_time_out)
        end_time = Timing.time() + delta.seconds

        # The DDC data file path
        ddc_file = None

        # The symbolic link file which points to the ddc data file
        link_file = None

        Verbose.yellow('Waiting for the symbolic link file to be generated which points to the DDC data file.')

        while (Timing.time() < end_time):
            Timing.sleep(2)

            link_file = DDCFilePath.find_soft_link_file(ddc_file_directory)

            if (link_file == False):
                # There are more than one link file found
                Verbose.red('More than one symbolic link file found.\n')
                return None

            elif (link_file != None):
                # only one link file found, proceed to next step
                break

        if (link_file == None):
            # if the link file is still not found, cannot find the ddc data file
            Verbose.red('Symbolic link file not found.\n')
            return None

        Verbose.green('Symbolic link file found.\n')
        Verbose.yellow('Waiting for the DDC data file to be generated.')
        while (Timing.time() < end_time):
            Timing.sleep(2)

            ddc_file = DDCFilePath.get_file_with_link(link_file)
            if (ddc_file != None):
                # Once the ddc data file is found, proceed to next step
                break

            if (ddc_file == None):
                Verbose.red('DDC data file not found.')
        return ddc_file

    @staticmethod
    def get_file_with_link(ddc_file_link):

        ddc_file = os.path.realpath(ddc_file_link)
        if (FilePaths.is_file(ddc_file)):
            return ddc_file
        else:
            return None

    @staticmethod
    def find_soft_link_file(ddc_file_directory):

        # get all file paths under the directory
        files = glob.glob('%sDDC_Data_%s*.tar.gz' % (ddc_file_directory, Timing.short_date()))

        link_file = None

        # in all files starting with "DDC_Data_" and ending with ".tar.gz"
        for file in files:

            # if it is a symbolic link file
            if (os.path.islink(file)):

                # if it is the first symbolic file
                if (link_file == None):

                    # store this file
                    link_file = file

                # if it is not the first symbolic file, we cannot decide if it is the file we want. we cannot collect ddc data
                else:
                    return False
        return link_file
