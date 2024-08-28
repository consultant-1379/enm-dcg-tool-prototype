from libs.health_check.check_root import CheckRoot
from libs.health_check.check_disk_usage import CheckDiskUsage
from libs.health_check.check_nr_of_files import CheckNrOfFiles
from libs.health_check.clean_up_output_dir import CleanUpOutputDir
from libs.health_check.mounts import Mounts
from libs.start_up.auto_clean import AutoClean
from libs.start_up.check_eocm import CheckEocm
from libs.start_up.check_user_eocm import CheckUserEocm
from libs.start_up.construct_paths import ReadPaths
from libs.start_up.jboss_check import JBossCheck
from libs.start_up.pid_check import PidCheck
from libs.start_up.variables_db import VariableDb
from libs.start_up.variables_options import VariableOption
from libs.start_up.variables_conf import VariableConf
from libs.start_up.cloud_server import CloudServer
from libs.logging.logger import Logger

class StartUp:

    def __init__(self):

        # check eocm
        CheckEocm()

        # checks if user has root access
        CheckRoot()

        # set's up the paths
        ReadPaths()

        # calls logger
        Logger()

        # Set's up variables
        VariableOption()

        # checks for configuration file and that values have been input
        VariableConf()

        # check eocm username
        CheckUserEocm()

        # checks if is cloud server
        CloudServer()

        # check job id of file if it exists
        #PidCheck()

        # Checks disk space
        CheckDiskUsage()

        # Checks File limit
        CheckNrOfFiles()

        # Clean output dir
        CleanUpOutputDir()

        # checks for database file and file format is .db, also checks contents are in database format
        VariableDb()

        # if cloud server mount required directories
        Mounts()

        # checks if debug level was changed back
        JBossCheck()

        # cleans all files in the output_logs_dir that are past a date set in the conf file
        AutoClean()