import json

from libs.utilities.file.file_type import FileType


class JsonReader(FileType):

    @staticmethod
    def load(file):
        FileType.check(file, JsonReader.extension())

        return json.load(file)

    @staticmethod
    def extension():
        return ".json"

    @staticmethod
    def file_type():
        return 'JSON'