import glob
import os

from libs.utilities.system.terminal import Terminal
from libs.utilities.system.timing import Timing


class MoveOldDDCFiles():
    @staticmethod
    def move(ddc_file_directory):
        # get all file paths under the directory
        files = glob.glob('%sDDC_Data_%s*.tar.gz' % (ddc_file_directory, Timing.short_date()))

        for file in files:
            if (os.path.islink(file)):

                # move all DDC link files to /tmp, but the DDC data file will be left
                Terminal.mv(file, '/tmp', True)
