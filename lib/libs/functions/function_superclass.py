from libs.utilities.system.terminal import Terminal


class FunctionSuperclass(object):
    def run(self):
        Terminal.exception("This function must be overridden")

    @staticmethod
    def func_name():
        pass

    @staticmethod
    def check_name_equal(a, b):
        try:

            # ignore all spaces
            a = a.replace(' ', '').lower()
            b = b.replace(' ', '').lower()
        except AttributeError:
            pass
        return a == b
