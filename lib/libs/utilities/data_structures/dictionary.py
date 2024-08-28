from libs.utilities.data_structures.type_check import TypeCheck
from libs.utilities.system.output import Output
from libs.utilities.system.terminal import Terminal


class Dictionary(object):
    @staticmethod
    def set_value(dictionary, key, value):
        TypeCheck.dict(dictionary)
        TypeCheck.str(key)
        dictionary[key] = value
        return True

    @staticmethod
    def get_value(dictionary, key, default=Exception(), file_path=None, type=None, add_default=False):

        # Argument check
        if not (TypeCheck.dict(dictionary) & TypeCheck.str(key)):
            Terminal.exception("The argument's type is not correct")

        try:
            value = dictionary[key]
            if (type != None):
                TypeCheck.type(type, value, key, file_path)
        except KeyError:
            if (isinstance(default, Exception)):

                # If default value is not set
                Output.red("The dictionary:")
                Output.white(dictionary)
                Output.red("was supposed to have the key: '%s'" % key)
                if (file_path == None):
                    raise KeyError(
                        "Cannot locate the YAML file which contains this key error. Check the previous output for the wrong type.")
                else:
                    Terminal.exception("This error occurred in the YAML file '%s'" % (file_path))
            else:
                # If default value is set
                value = default
                if (add_default):
                    Dictionary.set_value(dictionary, key, value)

        return value

    @staticmethod
    def remove_key(dictionary, key):
        try:
            del dictionary[key]
        except KeyError:
            pass
        return dictionary
