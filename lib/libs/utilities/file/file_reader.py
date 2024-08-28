import sys

from libs.logging.logger import Logger
from libs.utilities.file.conf_reader import ConfReader
from libs.utilities.file.json_reader import JsonReader
from libs.utilities.file.yaml_reader import YamlReader
from libs.utilities.system.print_text import Print
from libs.utilities.system.terminal import Terminal
from libs.variables.keys import BasicKeys
from libs.utilities.system.file_paths import FilePaths


class FileReader(object):
    def __init__(self, file_path, second_peek=None):
        super(FileReader, self).__init__()

        self.file_types = list()
        self.file_types.append(YamlReader)
        self.file_types.append(JsonReader)
        self.file_types.append(ConfReader)

        self.file_path = file_path
        self.second_peek = second_peek


    def get(self):
        if (type(self.file_path) == type(dict())):
            return self.file_path

        reader = None
        for each in self.file_types:
            extension = FilePaths.get_extension(self.file_path)
            if (each.extension() == extension):
                reader = each
                break

        if (reader == None):
            Terminal.exception("Cannot recognize the file type of the file: %s" % (self.file_path))

        if FilePaths.path_exists(self.file_path):
            with open(self.file_path, "r") as f:
                data = reader.load(f)
            try:
                # Add the value telling where the data comes from
                data[BasicKeys.current_file_path] = self.file_path

                # Add the value telling the type of the file
                data[BasicKeys.file_type] = reader.file_type()
            except:
                Print.red('The file you tried to execute is not the correct syntax to run with the LCS Tool')
                Logger.error('The yaml file the user ran was incorrect, it was missing [config_name: or config_type] in yaml file')
                sys.exit(0)


            return data
        else:
            Terminal.exception("File path invalid: %s" % (self.file_path))