from libs.utilities.system.terminal import Terminal


class ExecutorSuperclass(object):
    def __init__(self):
        pass

    @staticmethod
    def config_type():
        Terminal.exception("This method must be implemented")

    def run(self):
        pass
