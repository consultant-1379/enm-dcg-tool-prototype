from libs.utilities.system.output import Output
from libs.utilities.system.terminal import Terminal


class TypeCheck():
    @staticmethod
    def str(object, object_name='', source_file_name=None, output_error=True):
        return TypeCheck.type(str, object, object_name, source_file_name,output_error)

    @staticmethod
    def dict(object, object_name='', source_file_name=None, output_error=True):
        return TypeCheck.type(dict, object, object_name, source_file_name,output_error)

    @staticmethod
    def list(object, object_name='', source_file_name=None, output_error=True):
        return TypeCheck.type(list, object, object_name, source_file_name,output_error)

    @staticmethod
    def type(type, object, object_name='', source_file_name=None, output_error=True):
        if not (isinstance(object, type)):
            if (output_error):
                Output.red("The object '%s'" % object_name)
                Output.white(object)
                Output.red("should be in type %s" % type)
                if (source_file_name != None):
                    Output.yellow("Please check the file %s for this error" % source_file_name)
                else:
                    Terminal.exception("Cannot locate the file where this error occurred. Check the previous output for the wrong type.")
                Terminal.exception('configuration file error')
            return False
        return True
