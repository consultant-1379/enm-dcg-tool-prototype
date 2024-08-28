import yaml

from libs.utilities.file.file_type import FileType


class ConfReader(FileType):

    @staticmethod
    def load(file):
        FileType.check(file, ConfReader.extension())
        return yaml.load(file)

    @staticmethod
    def extension():
        return ".conf"

    @staticmethod
    def file_type():
        return 'CONF'