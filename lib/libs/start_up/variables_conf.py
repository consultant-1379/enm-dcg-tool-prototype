from libs.start_up.silent_setup import SilentSetup
from libs.variables.configuration import Configuration
from libs.utilities.system.file_paths import FilePaths
from libs.utilities.file.file_reader import FileReader
from libs.utilities.system.output import Output
from libs.utilities.system.terminal import Terminal
from libs.utilities.system.timing import Timing
import yaml

class VariableConf():

    def __init__(self):
        if not self.check_conf():
            if SilentSetup() == False:
                Terminal.exception("Error. cannot find conf file at path "
                                   + Configuration.configuration_dir
                                   + ". Please run --setup ")
        try:
            original_conf = FileReader(Configuration.default_path + '/etc/.origin_lcs.conf').get()
            conf = FileReader(Configuration.lcs_conf_path).get()
            if Configuration.EOCM is not True:
                if len(conf) != len(original_conf):
                    import sys
                    Output.red(
                        'There is a new parameter that is needed in the conf file, Run --setup to add this parameter to use this tool')
                    sys.exit(0)
                else:
                    for each_key in conf.keys():
                        value = conf.get(each_key)
                        if (type(value) == unicode):
                            value = value.encode('ascii')
                            import base64
                            value = base64.urlsafe_b64decode(value)
                            value = value.decode('ascii')
                            value = str(value)

                        setattr(Configuration, each_key, value)

                    Configuration.storing_logs_dir = '%s%s/' % (Configuration.report_output_dir, Timing.strftime())
            else:
                for each_key in conf.keys():
                    value = conf.get(each_key)
                    if (type(value) == unicode):
                        value = value.encode('ascii')
                        import base64
                        value = base64.urlsafe_b64decode(value)
                        value = value.decode('ascii')
                        value = str(value)

                    setattr(Configuration, each_key, value)

                Configuration.storing_logs_dir = '%s%s/' % (Configuration.report_output_dir, Timing.strftime())

        except yaml.scanner.ScannerError:
            if FilePaths.path_exists(Configuration.lcs_conf_path):
                Terminal.rm(Configuration.lcs_conf_path)
                Output.red("File Deleted")
            Terminal.exception("This is not a conf file. Run --setup to create new file.")


    def check_conf(self):
        if not FilePaths.path_exists(Configuration.lcs_conf_path):
            return False
        else:
            return True