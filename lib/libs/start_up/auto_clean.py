from libs.logging.logger import Logger
from libs.utilities.system.terminal import Terminal
from libs.variables.configuration import Configuration
from datetime import datetime
import os
import time

class AutoClean():

    def __init__(self):

        if Configuration.Auto_clean == True:
            Logger.info('Running clean up on output_directory')
            self.duration = int(Configuration.Duration)
            self.output_dir = Configuration.report_output_dir
            self.date_to_check = self._todays_date()
            files = self._get_files_in_directory()
            self.delete_list = self._check_date_on_files(files)
            self.delete_files()

    def _todays_date(self):
        date = datetime.now()
        new_date = str(date).split('.')
        pattern = '%Y-%m-%d %H:%M:%S'
        epoch = int(time.mktime(time.strptime(new_date[0], pattern)))
        return epoch

    def _get_files_in_directory(self):
        tarfiles = []
        for r, d, f in os.walk(self.output_dir):
            for file in f:
                if "lcs_report" in file:
                    tarfiles.append(file)
        return tarfiles

    def _check_date_on_files(self,files):
        delete_files = []
        for each in files:
            new = each.replace('.tar.gz','').split('_')
            date_on_file = str(new[4]).replace('-',' ')
            pattern = '%Y%m%d %H%M%S'
            file_epoch = int(time.mktime(time.strptime(date_on_file, pattern)))
            difference = self.date_to_check - file_epoch
            epoch_duration = 86400 * int(self.duration)
            if int(difference) > epoch_duration:
                delete_files.append(each)
        return delete_files

    def delete_files(self):
        if len(self.delete_list) > 0:
            for each in self.delete_list:
                dir_path = self._find_path(each)
                Logger.info('removing %s because it is gone past the date specified in conf file '%each)
                Terminal.system('rm -rf %s%s'%(dir_path,each))

    def _find_path(self,file):
        dir = self.output_dir
        for root, dirs, files in os.walk(self.output_dir):
            for name in files:
                if name == str(file):
                    dir = root + '/'
        return dir