import logging
import os
import sys

from libs.utilities.system.file_paths import FilePaths
from libs.variables.configuration import Configuration

class Logger(object):
    _static_logger = None
    _setup_logger = None

    def __init__(self, name='logger', level=logging.DEBUG):
        setup_enabled = False
        for each in sys.argv:
            if '--setup' in each or '-s' in each:
                setup_enabled = True
        if setup_enabled is True:
            setup_logger = logging.getLogger("setup-logger")
            setup_logger.setLevel(level)
            formatter = logging.Formatter(Configuration.tag_name + '%(asctime)s:%(levelname)s:%(msg)s', )
            fh = self._logfile(setup=True)
            fh.setFormatter(formatter)
            setup_logger.addHandler(fh)
            Logger._setup_logger = setup_logger

        logger = logging.getLogger(name)
        logger.setLevel(level)
        formatter = logging.Formatter(Configuration.tag_name + '%(asctime)s:%(levelname)s:%(msg)s', )
        fh = self._logfile()
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        Logger._static_logger = logger
        #Configuration.full_command_line = " ".join(["python"] + sys.argv)
        #Logger.info("User ran the command along with the extensions. " + Configuration.full_command_line)

    # for detailed debugging during normal execution
    @staticmethod
    def debug(msg, setup=False, trigger=True):
        if str(Configuration.vm_private_key) in msg:
            msg = msg.replace(str(Configuration.vm_private_key), '**************')
        if trigger is True:
            if setup is False:
                Logger._static_logger.debug(msg)
            else:
                Logger._setup_logger.debug(msg)

    # less detailed output during normal execution
    @staticmethod
    def info(msg, setup=False, trigger=True):
        if str(Configuration.vm_private_key) in msg:
            msg = msg.replace(str(Configuration.vm_private_key), '**************')
        if trigger is True:
            if setup is False:
                Logger._static_logger.info(msg)
            elif setup == True:
                Logger._setup_logger.info(msg)

    # for things that should'nt happen not due to the user
    @staticmethod
    def warning(msg, setup=False, trigger=True):
        if str(Configuration.vm_private_key) in msg:
            msg = msg.replace(str(Configuration.vm_private_key), '**************')
        if trigger is True:
            if setup is False:
                Logger._static_logger.warning(msg)
            else:
                Logger._setup_logger.warning(msg)

    # Error, but doesnt prevent programme from running
    @staticmethod
    def error(msg, setup=False, trigger=True):
        if str(Configuration.vm_private_key) in msg:
            msg = msg.replace(str(Configuration.vm_private_key), '**************')
        if trigger is True:
            if setup is False:
                Logger._static_logger.error(msg)
            else:
                Logger._setup_logger.error(msg)

    # errors that crash the programme
    @staticmethod
    def critical(msg, setup=False, trigger=True):
        if str(Configuration.vm_private_key) in msg:
            msg = msg.replace(str(Configuration.vm_private_key), '**************')
        if trigger is True:
            if setup is False:
                Logger._static_logger.critical(msg)
            else:
                Logger._setup_logger.critical(msg)

    # logger exception
    @staticmethod
    def exception(msg, setup=False, trigger=True):
        if str(Configuration.vm_private_key) in msg:
            msg = msg.replace(str(Configuration.vm_private_key), '**************')
        if trigger is True:
            if setup is False:
                Logger._static_logger.exception(msg)
            else:
                Logger._setup_logger.exception(msg)

    def _logfile(self, setup=False):
        if setup is False:
            file = 'debug.log'
            self._logFileRotation(file)
        else:
            file = "setup.log"
            self._logFileRotation(file, setup=True)
        fh = logging.FileHandler(FilePaths.join_path(Configuration.log_file_location, file))
        return fh

    def _logFileRotation(self, file, setup=False):
        if setup is False:
            backup = 'backup_debug.log'
        else:
            backup = 'backup_setup.log'
        self._logFileDirSize(backup)
        exists = os.path.exists(FilePaths.join_path(Configuration.log_file_location, file))
        if exists is True:
            from libs.utilities.system.terminal import Terminal
            Terminal.system('sudo /bin/mv %s %s' % (FilePaths.join_path(Configuration.log_file_location, file), FilePaths.join_path(Configuration.log_file_location, backup)))

    def _logFileDirSize(self, backupfile):
        path = Configuration.log_file_location
        file_list = os.listdir(path)
        for each in file_list:
            if os.path.isfile(each) is False:
                file_list.remove(each)

        if backupfile.endswith('debug.log'):
            debug_logs = sum(1 for each in file_list if 'debug.log' in each)
            if debug_logs > 2:
                os.remove(FilePaths.join_path(Configuration.log_file_location, backupfile))
        elif backupfile.endswith('setup.log'):
            setup_logs = sum(1 for each in file_list if 'setup.log' in each)
            if setup_logs > 2:
                os.remove(FilePaths.join_path(Configuration.log_file_location, backupfile))
