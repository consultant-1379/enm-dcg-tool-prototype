from libs.utilities.system.file_paths import FilePaths
from libs.variables.configuration import Configuration


class AbsoluttePath():
    @staticmethod
    def AbsoluttePath(currect_path, relative_path):
        """
        todo: this method should be moved to somewhere else
        todo: change the name of this method
        :param currect_path: The current file path (menu or app yaml file)
        :param relative_path: The path of the next yaml file needed to be processed
        :return:
        """
        if (relative_path == Configuration.previous_menu or relative_path == Configuration.current_menu):
            return relative_path

        if (relative_path[0] == "/"):
            # if the path starts with a forward slash, concatenate it with the default YAML file directory
            absolute_path = FilePaths.join_path(Configuration.config_files_dir, relative_path[1:])
        else:
            # if the path does not start with a forward slash, concatenate it with the current file directory
            file_directory = FilePaths.get_directory(currect_path)
            absolute_path = FilePaths.join_path(file_directory, relative_path)
        return absolute_path
