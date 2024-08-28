from libs.utilities.system.output import Output
from libs.utilities.system.file_paths import FilePaths
from libs.utilities.system.terminal import Terminal


class FileType(object):
    @staticmethod
    def extension():
        pass

    @staticmethod
    def load(file):
        pass

    @staticmethod
    def check(file, ext):
        if (ext != FilePaths.get_extension(file.name)):
            Output.red("File name: %s\nExtension expected: %s" % (file.name, ext))

            Terminal.exception("The file extension does not match this file type.")

    @staticmethod
    def file_type():
        return ''
