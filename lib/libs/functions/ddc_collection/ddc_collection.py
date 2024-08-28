from libs.functions.collate_attach_files.collate_attach_files import CollateAttachFiles
from libs.functions.ddc_collection.tools.ddc_file_path import DDCFilePath
from libs.functions.ddc_collection.tools.ddc_maketar import DDCMaketar
from libs.functions.ddc_collection.tools.move_old_DDC_files import MoveOldDDCFiles
from libs.functions.function_superclass import FunctionSuperclass
from libs.utilities.data_structures.dictionary import Dictionary
from libs.utilities.system.output import Output
from libs.utilities.system.terminal import Terminal
from libs.variables.configuration import Configuration
from libs.variables.keys import AppKeys
import signal

class DDCCollection(FunctionSuperclass):

    def __init__(self, function, app, config_stack):
        """
        This class collects DDC file, following the document "Manually Triggering & Uploading DDC" at 
        https://confluence-nam.lmera.ericsson.se/pages/viewpage.action?pageId=192425560

        :param function:
        :param app: an object of the class ConfigItem
        :param config_stack:
        """
        self.app = app
        self.menu_stack = config_stack
        if (not FunctionSuperclass.check_name_equal(function[AppKeys.func_name], DDCCollection.func_name())):
            Terminal.exception("This function was wrongly passed in DDCFile")

        # From step 3, the DDC file is at the following directory
        #  /var/ericsson/ddc_data/<LMS hostname>_TOR
        self.ddc_file_dir = '%s%s_TOR/' % (Configuration.DDC_output_dir, Terminal.hostname())
        # print trigger for startYAML
        self.print_trigger = True
        if Configuration.manual_startYamlFile is True:
            self.print_trigger = False

    @staticmethod
    def func_name():
        return "DDC Collection"

    def run(self):
        """
        On production servers DDC files are created every 4 hours starting from midnight. The resulting DDC_Data_<ddmmyy>.tar.gz file is then stored in the folder /var/ericsson/ddc_data/<LMS hostname>_TOR. This file can be uploaded (manually or automatically) to the relevant DDP server for processing.
        The file /var/ericsson/ddc_data/config/ddp.txt must contain the FTP username for the site with no spaces, carriage returns or line feeds.
        :return:
        """
        if Configuration.DDC_collection == True:
            # check for Ctrl-c press
            signal.signal(signal.SIGINT, self._ctrlC_handler)
            # check for Ctrl-Z press
            signal.signal(signal.SIGTSTP, self._ctrlC_handler)

            Output.yellow("Collecting DDC data file. It may take a long time. Please wait...",print_trigger=self.print_trigger)

            # move old DDC data link files before doing the collection
            MoveOldDDCFiles.move(self.ddc_file_dir)

            # Step 1: On the MS check that the file  /var/ericsson/ddc_data/config/ddp.txt has the FTP username of the DDP account
            pass

            # Step 2: As root execute "/opt/ericsson/ERICddc/bin/ddc MAKETAR" on the MS
            if (not DDCMaketar.execute()):
                # if the command has NOT been executed successfully
                return self.fail('The command "%s"cannot be executed.' % (DDCMaketar.ddc_maketar_command))

            # Step 3 - 5: wait until the ddc file is generated and get the file path
            ddc_data_file = DDCFilePath.get_ddc_file_path(self.ddc_file_dir)

            # if file cannot be collected
            if (ddc_data_file == None):
                return self.fail('Cannot find DDC data file within %s minutes.\n' % (Configuration.DDC_time_out))

            # Step 6: Cut the file to the log storing directory
            Terminal.mkdir(Configuration.storing_logs_dir, superuser=True)
            Terminal.cp(ddc_data_file, Configuration.storing_logs_dir, superuser=True)
            Output.green('DDC data file collected.',print_trigger=self.print_trigger)

    def fail(self, reason='Unknown'):
        Output.yellow('DDC data file cannot be collected. Reason:',print_trigger=self.print_trigger)
        Output.white(reason,print_trigger=self.print_trigger)

    def _ctrlC_handler(self,sig,frame):
        func_name = dict()
        func_name[AppKeys.func_name] = CollateAttachFiles.func_name()
        func_type = self.app
        stack = self.menu_stack
        CollateAttachFiles(func_name, func_type, stack).run()
        Terminal.rm('/tmp/Log_tool_running')
        Terminal.exit()