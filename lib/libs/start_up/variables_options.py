import sys

from libs.logging.logger import Logger
from libs.start_up.get_version import GetVersion
from libs.utilities.system.terminal import Terminal
from libs.variables.configuration import Configuration
from libs.variables import variables
import argparse


class VariableOption():

    def __init__(self):

        parser = argparse.ArgumentParser(description=variables.tool_description)

        main_group = parser.add_argument_group()

        main_group.add_argument("-v", "--version", action="store_true", default=False,
                                help="display version information")
        main_group.add_argument("-s", "--setup", action="store_true", default=False,
                                help="sets up the tool")
        main_group.add_argument("-m", "--manual_action", type=VariableOption.str2bool, default=True,
                                help="set True to execute manual actions or set False to skip manual actions from the YAML file (default value is True)")
        main_group.add_argument("--execute", default=Configuration.start_up_file,type=str,nargs='+',
                                help="execute specific YAML file")
        main_group.add_argument("--menu",default=Configuration.dynamic_menu_path,type=str,nargs='+'
                                ,help="execute a dynamic menu")
        main_group.add_argument("--verbose", action="store_true", default=False,
                                help="explanation of commands executed")
        main_group.add_argument("-t", "--timeout", type=int, help="time set to reproduce issues in seconds."
                                "if set to 0 it will collect logs without changing Jboss loggers")
        main_group.add_argument("--DDC", type=VariableOption.str2bool, default=False,
                                help="set True to execute DDC data collection or set False to skip it (default value is True)")
        main_group.add_argument("--ticket", default=Configuration.ticket_dir, type=str, nargs='+'
                                , help='csv"Number" or torf"Number" to create a directory in lcs or on ftp server')
        main_group.add_argument("--yes", type=VariableOption.str2bool, default=False,
                                help="")
        main_group.add_argument("--use_tool", type=VariableOption.str2bool, default=False,
                                help="")


        self._logger_of_args(sys.argv)
        if '--execute' in sys.argv[2:] or '--menu' in sys.argv[2:]:
            newList = sys.argv[2:]
            try:
                newList.remove("--exec_dir")
            except:
                pass
            try:
                newList.remove("--menu_dir")
            except:
                pass
        else:
            newList = sys.argv[2:]


        args = parser.parse_args(newList)

        for each in newList:
            if (each == "--setup" or each == "-s") and (len(sys.argv[2:]) > 1):
                parser.error("argument -s/--setup: not allowed with other arguments")
            elif (each == "--version" or each == "-v") and (len(sys.argv[2:]) > 1):
                parser.error("argument -v/--version: not allowed with other arguments")
            elif (each == "--execute" and each == "--menu"):
                parser.error("argument -m/--menu: not allowed with --execute ")

        Configuration.manual_actions = args.manual_action
        Configuration.start_up_file = args.execute
        Configuration.verbose = args.verbose
        Configuration.debug_time = args.timeout
        Configuration.DDC_collection = args.DDC
        Configuration.dynamic_menu_path = args.menu
        Configuration.ticket_dir = args.ticket
        Configuration.yes_to_all = args.yes
        Configuration.use_tool_while_instance_running = args.use_tool

        if (args.execute):
            Configuration.execute_multiple_files = True
            from libs.start_up_message.start_up_msg import StartUpMsg
            if args.version or Configuration.dynamic_menu_path != None:
                pass
            else:
                StartUpMsg.message()

        if (args.timeout == 0):
            Configuration.jboss_debug = False

        elif (args.timeout is None):
            pass

        elif (args.timeout < 0):
            parser.error("argument -t/--timeout: cannot be < 0")

        if (args.version):
            GetVersion()
            sys.exit()

        if (args.setup):
            from libs.setup.setup import Setup
            Setup.setup()
            Terminal.exit()

        if (args.menu):
            Configuration.page_num = 1
            Configuration.dynamic_menu = True
            Configuration.length = Configuration.dynamic_menu_path

        if (args.ticket):
            Configuration.ticket_number = True

    @staticmethod
    def str2bool(v):
        if v.lower() in ('yes', 'true', 't', 'y', '1', 'on'):
            return True
        elif v.lower() in ('no', 'false', 'f', 'n', '0', 'off'):
            return False
        else:
            raise argparse.ArgumentTypeError('Boolean value expected.')

    def _logger_of_args(self,args):
        str_args = str(args[2:]).replace('[','').replace(']','').replace(',','').replace("'","")
        Logger.info('Tool has been run with these arguments ' + str_args)
