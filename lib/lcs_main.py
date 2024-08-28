from libs.config_executor import ConfigExecutor
from libs.executors.menu_executor.dynamic_menu import DynamicMenu
from libs.health_check.JBoss_error_checker import JbossError
from libs.lcs_error import LCSError
from libs.start_up.start_up import StartUp
from libs.utilities.system.print_text import Print
from libs.utilities.system.terminal import Terminal
from libs.variables.configuration import Configuration
from libs.logging.logger import Logger
import time

def main():

    if Configuration.EOCM is True:
        Terminal.mkdir(Configuration.report_output_dir)

    #start time of program
    Configuration.start_time = time.strftime('%H%M%S')

    if Configuration.menu_run_file is None:
        # set up and health checks
        StartUp()

        if Configuration.start_up_file is None:
            if Configuration.dynamic_menu_path[0] == Configuration.default_path + '/etc/':
                Logger.info('The user is running the tool through menu with default path %s'
                            % Configuration.dynamic_menu_path)
            else:
                Logger.info('The user is running the tool through menu using %s directory'
                            % Configuration.dynamic_menu_path)
            DynamicMenu(Configuration.dynamic_menu_path)
            start_up_file = Configuration.menu_run_file
        else:
            if os.path.isdir(Configuration.start_up_file[0]) is True:
                Logger.info('The user is executing multiple yaml files from this path %s '
                            % Configuration.start_up_file)
            else:
                Logger.info('The user is executing %s ' % Configuration.start_up_file)
            start_up_file = Configuration.start_up_file
    else:
        start_up_file = Configuration.menu_run_file

    # check for ticket number
    if Configuration.ticket_number is True:
        Configuration.report_output_dir = Configuration.report_output_dir + Configuration.ticket_dir[0] + '/'
        Terminal.mkdir(Configuration.report_output_dir)

    # run the tool
    program = ConfigExecutor(start_up_file)
    program.run()

if __name__ == '__main__':
# if an error that can't be seen occurs comment out the exception it occurred in
    import os
    Configuration.default_main_file = os.path.realpath(__file__)
    try:
        main()
    except KeyboardInterrupt:
        JbossError()
        Logger.exception("Keyboard Error Occurred")
    except LCSError:
        JbossError()
        Logger.exception("LCS Error Occurred")
    except SystemExit:
        JbossError()
        Logger.info("SystemExit")
    # except:
    #     JbossError()
    #     Print.red("Unknown Error Caused Crash")
    #     Logger.exception("Unknown Error Occurred")
