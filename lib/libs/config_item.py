from libs.lcs_error import LCSError
from libs.utilities.file.file_reader import FileReader
from libs.utilities.system.file_paths import FilePaths
from libs.variables.configuration import Configuration
from libs.variables.keys import BasicKeys


class ConfigItem():
    def __init__(self, file_path=None, dictionary=None, implicit_plugins=True, storing_log=None):
        """
        Construct the ConfgItem EITHER by file path of a dictionary
        :param file_path:  the path of the configuration file
        :param dictionary: the dictionary of the configuration file
        :param implicit_plugins: If it is True, we need to add implicit plug-ins
        """
        if (storing_log == None):
            self._storing_log = Configuration.storing_logs_dir
        else:
            self._storing_log = storing_log

        if (file_path == None and dictionary == None):
            raise LCSError('Both dictionary and file path are None')
        if (file_path != None and dictionary != None):
            raise LCSError('Both dictionary and file path are not None')
        if (file_path == None):
            self._file_path = None
            self._data = dictionary
            self._file_type = None
        else:
            file_path = FilePaths.real_path(file_path)
            self._file_path = file_path
            self._data = FileReader(file_path).get()
            self._file_type = self._data[BasicKeys.file_type]

        self._app_marker = 0
        self._config_type = self._data[BasicKeys.config_type]
        self._config_name = self._data[BasicKeys.config_name]
        self._implicit_plugins = implicit_plugins

    def get_storing_log_dir(self):
        return self._storing_log

    def get_implicit_plugins(self):
        return self._implicit_plugins

    def set_implicit_plugins(self, implicit_plugins):
        self._implicit_plugins = implicit_plugins

    def get_config_name(self):
        return self._config_name

    def get_file_path(self):
        return self._file_path

    def get_data(self):
        return self._data

    def get_marker(self):
        return self._app_marker

    def set_marker(self, marker):
        self._app_marker = marker

    def get_file_type(self):
        if (self._file_type == None):
            raise LCSError("File path does not exist")
        return self._file_type

    def get_config_type(self):
        return self._config_type
