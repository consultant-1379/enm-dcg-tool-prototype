import os


class FilePaths:

    @staticmethod
    def join_path(head, tail):
        """
        Joins two paths
        :param head: Path where programme exists
        :param tail: File/directory path
        :return: Full Path
        """
        return os.path.join(head, tail)

    @staticmethod
    def get_extension(file_path):
        """
        Finds file type
        :param file_path: Path to file
        :return: Extension of file
        """
        name, extension = os.path.splitext(file_path)
        return extension

    @staticmethod
    def get_directory(file_path):
        """
        Finds directory
        :param file_path: a file path or a directory
        :return: The directory of a file or the parent directory a directory
        """
        return os.path.dirname(file_path)

    @staticmethod
    def isdir(directory):
        """
        Checks if path is a directory
        :param directory: Path to check
        :return: True/False
        """
        return os.path.isdir(directory)

    @staticmethod
    def path_exists(directory):
        """
        Checks if directory/file exists
        :param directory: Path to directory
        :return: True/False
        """
        return os.path.exists(directory)

    @staticmethod
    def is_file(file_path):
        """
        Checks if it is a file
        :param file_path: Path of file
        :return: True/False
        """
        return os.path.isfile(file_path)

    @staticmethod
    def pardir():
        return os.pardir

    @staticmethod
    def absolute_path(file_path):
        return os.path.abspath(file_path)

    @staticmethod
    def real_path(file_path):
        return os.path.realpath(file_path)