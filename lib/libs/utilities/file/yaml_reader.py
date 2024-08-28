import yaml

from libs.utilities.file.file_type import FileType


class YamlReader(FileType):

    @staticmethod
    def load(file):
        FileType.check(file, YamlReader.extension())

        return yaml.load(file)

    @staticmethod
    def extension():
        return ".yml"

    @staticmethod
    def file_type():
        return 'YAML'
