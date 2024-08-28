from libs.functions.function_superclass import FunctionSuperclass
from libs.utilities.system.terminal import Terminal


class CollectFilesSuperclass(FunctionSuperclass):

    @staticmethod
    def server_type():
        """
        override this method
        :return: provide the server type
        """
        Terminal.exception("This function must be overridden")
