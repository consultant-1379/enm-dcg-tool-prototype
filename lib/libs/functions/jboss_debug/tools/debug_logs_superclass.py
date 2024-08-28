from abc import ABCMeta, abstractmethod


class DebugLogsSuperclass(object):
    __metaclass__ = ABCMeta

    def __init__(self, debug_name, debug_time):
        """
        All debug logs controllers must implement this class and the methods in this class
        :param debug_name: The name of this debug function
        """
        self.debug_time = debug_time
        self.debug_name = debug_name

    def get_debug_time(self):
        """
        Do not override this method
        :return: The time of this debugging
        """
        return self.debug_time

    def get_debug_name(self):
        """
        Do not override this method
        :return: The name of this debugging
        """
        return self.debug_name

    @abstractmethod
    def enable_debug(self):
        """
        To enable the debug logs
        :return:
        """
        pass

    @abstractmethod
    def disable_debug(self):
        """
        To disaable the debug logs
        :return:
        """
        pass
